# plan.md — water_mitigation_billing (M=2), round 1

## Draws (scripts/draw_counts.py)
- task 0: prerequisite_problems=2, factor_counts=[6,4,6]
- task 1: prerequisite_problems=1, factor_counts=[6,6]

## Charter reading (frozen base, water)
- Customer-owned writes the base gives water: work authorization (no numeric field), Early Equipment Removal
  Release (no numeric field), customer payments (amount = customer's choice; base prices only the self-pay
  deposit gate). Only a payment can carry a scored computed amount, and only two payments are not "the balance":
  the drying deposit (authorized stage) and the insured's share of an insurance job (billing stage).
- Charge lines are rate x quantity; 4-6 load-bearing factors only exist where the quantity is assembled from
  several recorded scope inputs (Xactimate-style line quantities keyed on IICRC category/class).
- BLUEPRINT-KNOWN candidate: the water charter has no priced customer act besides the flat self-pay deposit;
  routed around by (a) a drying-estimate deposit (overwrite of the flat deposit sentence) and (b) the insured's
  share payment on an insurance job.

## Design thesis
### Task 0 (self-pay rental, Gray Water - Standard Loss, authorized today, tear-out done today)
Surface goal: landlord wants to pay what is needed so the crew can set drying equipment today (pays by debit).
- root  water_ext_drying_deposit (owner=user payment, 6 factors): drying-estimate deposit + charges posted to date
  - payments posted; IICRC class air-mover plan, dehumidifier type, drying days, air scrubber, regulated reserve,
  credit standing (other company mold job past due: cross-difficulty (claimed sibling), multi-source).
- prereq water_ext_tearout_debris (agent, 6 factors): debris haul-off line for the tear-out date
  (value_input -> charges_posted of the deposit).
- prereq water_ext_tearout_antimicrobial (agent, 4 factors): antimicrobial line for surfaces exposed by tear-out
  (value_input -> charges_posted of the deposit).
Edges: deposit <- debris (state form, value_input); deposit <- antimicrobial (state form, value_input);
debris and antimicrobial commute (separate lines, no shared quantity).

### Task 1 (Direction to Pay insured homeowner, water job drying_complete, claim at estimate_submitted)
Surface goal: homeowner wants to pay "her part" (what insurance will not pay) of the water job today, by ACH.
- prereq water_ext_final_hepa_vacuum (agent, 6 factors): final HEPA vacuuming line on the drying complete date
  (value_input -> HEPA square feet read by the share).
- root  water_ext_insured_share (owner=user, 6 factors): finance charges plus non-covered amounts (code work under the
  claim's ordinance or law limit, emergency premium by dispatch timing, IICRC air-mover and LGR caps, HEPA beyond the
  stripped floor, contents rooms beyond the category block), billed only where the claims arrangement bills declined lines.
Edge: share <- HEPA (state form, value_input).

## Problem-tree cards: see worklog.md (kept per task).
