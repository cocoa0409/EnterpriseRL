# worklog — summit_miles_status_and_upgrades (category loyalty, M=2)

2026-09-24 START erl-task-instantiate. Blueprint read (blueprint.yaml, products/loyalty.yaml, db_schema.json, share_tools.py).

## Step 0 draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=3, factor_counts=[4,5,6,5]
- task 1: prerequisite_problems=3, factor_counts=[4,5,5,6]

## Tool names (uuid8 minted one per tool, frozen)
- post_retro_credit_03268362 (agent)            task 0
- post_segment_qualifying_dollars_d0ee7d28 (agent) task 0
- record_tier_requalification_84e40849 (agent)  task 0
- reinstate_expired_miles_d28241c8 (user)       task 0 root
- post_choice_bonus_miles_029b6e8c (agent)      task 1
- post_miles_upgrade_charge_7f00044a (agent)    task 1
- issue_choice_upgrade_certificates_458899d3 (agent) task 1
- buy_miles_4af9ade8 (user)                     task 1 root

## Space budget (Principle C)
Feeders of a fee root (tier / activity / qualifying dollars) are retro credit, segment qualifying dollars and
tier requalification: task 0 claims all three as the chain under the reinstatement fee.
Feeders of a balance root (bonus credit +, miles-upgrade charge -) plus the certificate issue owed on a
choice selection are left for task 1 under the top-up purchase. Neither task can take the other's feeders
without leaving the other with fewer than the drawn 3 prerequisite problems.

## Constraints noted
- award redemptions of saver/standard trigger ticket:ticket_book, loyalty_close triggers companion revoke,
  choice selections of companion_certificate / club_membership trigger other categories: no tool writes them.
- every empty foreign key is seeded as null (an empty string is a dangling FK for replay_tasks).

## Task 0 (Kellerman, reinstatement fee root) — closed
- Tree: retro credit -> segment qualifying dollars -> tier requalification -> reinstatement fee (+ fee -> retro). All 4 edges value_input, state form.
- Gold values (harness on handling-time worlds): retro 13711 mi; qualifying dollars 2931.75; tier Summit Silver (count 4574 vs 4500); fee 108.00.
- Per-task gates (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (closure 44/44), SOLVABILITY OK, COMPUTE OK (20 factors, 12 cross, hist 18, branches 84), GROUNDING OK, SCOPE OK.
- Revisions: club factor in the QD policy replaced by a card factor; prerequisite sentences rephrased on the flown segment (vacuous-at-opening fix); helper function inlined in task_tools.py.
- Scratch work lives in scratchpad/summit_d3 (shared scratchpad root has sibling agents' files).

## Task 1 (Ibarra, top-up purchase root) — closed
- Tree (fan-out): purchase <- bonus credit (value_input), <- miles-upgrade charge (value_input), <- certificate issue (state_gate). All state form.
- Gold: bonus 29500 mi (year 2025); upgrade charge 25000 mi + co-pay 12.00; 13 certificates (year 2024, expiry 2027-10-06); purchase 20000 mi for 440.00.
- All six orders of the three prerequisites give identical values and terminal hash (order_uniqueness).
- Revisions: ledger re-planned to never go negative; clearance-timing factor now reads the upgraded segment's coupon; distance read via MAX for the history floor.

## Final difficulty-wide gates (traceability deferred until the KB is published)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (0: 44/44, 1: 107/107) / SOLVABILITY OK / COMPUTE OK
(branches mean 77.00, steps mean 21.00, history max 20, branches max 84) / GROUNDING OK / CACHE-DIFF INFO / SCOPE OK.

## Manual values checks
- Prerequisite sentences: 7 edges, 4 affirmative ("only after") and 3 negated ("not ... until"); each names a
  record-visible state written by exactly one policy of this difficulty; no tool, id or code token.
- Cross-task obligations: task-1 policies owe nothing in task 0's world (no selection, no clearance); task-0 policies
  owe nothing in task 1's world (all tickets name the membership, all segments carry QD, tier count 4951 < Platinum held).
- Known design risk for the audits: several factors are Crestline program rules introduced in this charter's params
  (returning-member, lounge, card, tenure, pass and ancillary credits); each is declared through `overwrite` where it
  replaces a base clause and each is load-bearing on its world.

## Round 2 rework (audit audits/policy_task/summit_miles_status_and_upgrades, round 1)
- F-1 / T0-1 / T1-1: six rate ladders labelled method now change the operation per tier (scale vs flat add/subtract vs
  first-band substitution): returning_member_qualifying_treatment, tenure_treatment, prompt_request_treatment,
  late_posting_treatment, distance_treatment, repeat_buyer_treatment. Tiers taken on both worlds unchanged.
- F-2 / T1-2: upgrade_cabin_reduction (unreachable fall-through) replaced by departure_cabin_reduction
  (trip departs within close_trip_days 21 AND requested cabin), fall-through reachable.
- F-3 / T1-3: departure_cabin_reduction is multi-source over two records (trip ticket departure + waitlist request cabin).
- O-3 docstring wording; O-4 club/pass factors no longer claim cross_difficulty; task-1 persona O-A/O-B wording.
- Gold values, factor_sensitivity and baseline_result figures unchanged on both tasks (harness re-run).
- Gates (full, no --task): EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK
  (xfac 10 and 9, branches mean 77.50) / GROUNDING OK / CACHE-DIFF INFO / SCOPE OK. Traceability still deferred.

## Round 3 rework (audit revision_2)
- F-4 / T0-2: returning_member_qualifying_treatment (near = max(x1.5, share+500) vs far share+250), tenure_treatment
  (long = max(x1.1, qd+250) vs mid qd+200), prompt_request_treatment (<=30 days flat 50 vs 75% of band vs band) now
  monotone over their whole domain (sweep: no violation); tiers taken and all task-0 figures unchanged.
- O-8: compute_basis entry for miles_short. O-9: very-long co-pay surcharge capped at the shared co-pay.
- F-1, F-2, F-3, O-3, O-4 and task-1 O-A/O-B stay closed; task 1 figures unchanged.
- Gates (full): EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (branches mean 79.00) /
  GROUNDING OK / CACHE-DIFF INFO / SCOPE OK. Traceability deferred.

## Round 4 (merge-acceptance: customer id collision)
- Root cause: the first task-0 builder run used the shared, generically named scratchpad t0_ids.json and reused its
  `cust` key (a sibling's customer id). All 44 task-0 seeded ids passed through that shared file, so all were re-minted
  (map kept in my scratch folder summit_d3/r4/t0_id_map.json); task-1 ids were minted only in the private folder and
  collide with nothing in the shared scratchpad.
- Customer fbbf57f4-be2a-4a40-8585-56f2ebb54ddf -> 2a60b6a4-4f49-4ef5-b099-4a315aba4948; membership, activity, tickets,
  coupon, bag charge, companion, club, pass rows re-minted likewise; FKs, GT arguments, tracing and proof fields rebuilt.
- No value moved: 13711 / 2931.75 / Summit Silver / 108.00; all sensitivities, baselines and skips identical.
- Gates (full): all OK as in round 3; traceability deferred.

## Round 5 (render-layer source miss: SLM-1, SLM-2; SLM-3 is frozen base, logged by the coordinator)
- SLM-1: reinstatement fee, retro-segment QD, miles-upgrade charge and top-up purchase. baseline.rule now defines every
  quantity a ladder is written on (band fee / fee to pay; share qualifying dollars / qualifying share percent; shared
  co-pay / co-pay to charge; tier / net price per thousand). Each factor sentence and ladder value/method states the
  amount it acts on and when it applies; factor-naming assembly sentences replaced by factor-silent ones.
- SLM-2: QD overwrite retargeted to loyalty_retro_credit_claims' "earns exactly what the flight would have earned"
  clause (retro scope; flight-earning QD clause back in force for ordinary coupons); top-up replaced_by now also prices
  a purchase covering no waitlisted upgrade at the base price.
- compute, params and ladder conditions byte-identical (scratch verifier); every value, sensitivity, baseline and skip
  unchanged. Gates (full) all OK; traceability deferred.
