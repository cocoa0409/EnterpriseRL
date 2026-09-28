# Difficulty worklog — ticket_changes_refunds_and_disruptions (M=2)

Each task's `design_rationale` holds its full dossier (draw, cards, factor sensitivities, verification run, revisions).
This file records the difficulty-level ledger only.

## Draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems 2, factor_counts [4, 4, 5]
- task 1: prerequisite_problems 3, factor_counts [6, 4, 5, 5]

## Claims (pairwise disjoint; together they cover all 7 extended policies)
| task | policy | target tool | owner | factors | gold value |
|---|---|---|---|---|---|
| 0 | ticket_ext_same_day_change_fee | post_same_day_change_fee_61b8e8ae | agent | 4 | 17.55 |
| 0 | ticket_ext_seat_charge_correction | refund_seat_charge_excess_9145fc3e | agent | 4 | 61.30 |
| 0 (root) | ticket_ext_first_upgrade_charge | purchase_first_upgrade_fa17fda8 | user | 5 | 69.19 |
| 1 | ticket_ext_change_fee_posting | post_change_fee_ac050962 | agent | 5 | 58.32 |
| 1 | ticket_ext_bag_sequence_charge | post_bag_sequence_charge_b2992c63 | agent | 4 | 61.13 |
| 1 | ticket_ext_bag_weight_charge | post_bag_weight_charge_02a99017 | agent | 5 | 66.88 |
| 1 (root) | ticket_ext_premium_economy_upgrade_charge | purchase_premium_economy_upgrade_2477ee45 | user | 6 | 36.89 |

## Trees
- task 0: First upgrade <- same-day change fee (value_input, state form, negated sentence), <- seat charge correction (value_input, state form, affirmative sentence). The two prerequisites commute (swapped replay: identical hash).
- task 1: Premium Economy upgrade <- change fee, <- bag sequence charge, <- bag weight charge (all value_input, state form; affirmative, negated and "before ... must" sentences). All 6 orders of the prerequisites replay to one hash and the same upgrade charge.

## Cross-difficulty and multi-source
- task 0 reads the loyalty product (Summit tier parameters, status, flight accruals over 12 months); the same-day fee rule also reads the business product for an agreement the ticket names (none on task 0's ticket).
- task 1 reads the business product (agreement status, tier waiver, spend vs threshold, eligible brands and channels, the tier discount for the itinerary class, points balance, flown-spend postings in 6 months); the bag sequence rule also reads the loyalty product for a credited membership's allowance (none on task 1's ticket).

## Design decisions recorded at difficulty level
- Compensation, involuntary refunds and voucher choices were not claimed: their base gates bind a disruption reference as a caller statement, which a persona cannot state without an internal id.
- Exchanges with fare collections were not claimed as problems: no record carries the new itinerary's fare, so no compute could reproduce it.
- Every write tool writes only ticket tables and no event whose trigger reaches another category (no residual-to-credit, credit conversion, goodwill voucher or goodwill miles).
- On the personal ticket of task 0, the change-fee corporate gate is evidenced by the traveller's employer agreement, which the ticket does not name (a trap: no corporate waiver applies).

## Rework round 2 (audit: audits/policy_task/ticket_changes_refunds_and_disruptions/)
Closed item by item (details in each task's design_rationale, section REWORK ROUND 2):
- F1 — every prerequisite sentence now has exactly the scope of the rule that resolves it: P3 waits on the latest same-day confirmed exchange only when it owes a fee; P7 waits on the latest standard exchange only when it owes a fee, on every weight-entry bag of the upgraded segment, and on the heaviest bag charged by count only when it owes a weight charge. P1 now prices same-day changes on every ticket (an active agreement whose tier waives change fees gives a zero rate) and says a zero-fee exchange owes none; P4 targets the latest standard exchange and says the same; P5 now covers member tickets (the member allowance competes in the free allowance); P6 says a zero charge is not owed.
- F2 — P3 sentence, condition and P2 rule all name the latest seat charge of the segment.
- F3 — O1: P5's check-in channel is a segment property read from bag charges paid at the airport or online, rule and compute alike; O2: P4 rule targets the latest standard exchange, as compute reads; O3: P3's seat standing reads the latest seat charge less refunds against that charge.
- F4 — P3's month-window and P4's notice multiplier are removed; the method factors are P3's fare-part convention of the trip spend and P4's banding-fare convention (fare collected less taxes on an agreement ticket / fare still unflown / fare collected).
- F5 — P5's whole-ticket and charged-only counts are removed (the place in the count is the base per-direction count; the method factor is P5's banding-fare convention); P6's count-place rate is replaced by a graduated weight excess rate.
- O4 — P7 trip charges count the segment's and the itinerary-level (no-segment) change, bag and upgrade charges, rule and compute alike. O5 — the base "for a fixed fee" sentence is declared in P3's and P7's overwrites. O6 — the third-bag and oversize clauses are declared in P5's and P6's overwrites. O7 — P3 names the travel manager as buyer on a company-held ticket. O9 — P3's trip spend counts only seat charges, same-day fees and seat refunds; P7's trip charges only change, bag and upgrade charges; no undeclared cross-policy coupling remains.
- Task observations — task 0 persona: seats picked online in the days after booking; task 1 ticket paid by company credit card; P7 corporate rate reads the tier discount for the itinerary class; P7 credit tier 2 is an agreement under review; order_uniqueness reason rewritten.
- Scored values: task 0 unchanged (17.55, 61.30, 69.19); task 1 now 58.32, 61.13 (second bag, position 2), 66.88, 36.89.

## Final gate run (difficulty-wide, after rework round 2)
EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
Traceability is deferred until the knowledge base is published.
