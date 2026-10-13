# Worklog — delivery_and_installation_appointments (M=2)

## Step 0 — difficulty pre-check (2026-10-05)
- Read: references/{product_extended.yaml,task_tools.py,task.json}; blueprint.yaml; products/delivery.yaml; db_schema.json; share_tools.py.
- Category `delivery`; holding delivery_holdings; event table delivery_charges; intake delivery_claims.
- Draws (`draw_counts.py --tasks 2`):
  - task 0: prerequisite_problems=2, factor_counts=[4, 6, 4]
  - task 1: prerequisite_problems=1, factor_counts=[5, 5]
- Structural constraints found while reading the gates/base:
  - compute returns numbers only; no date construction -> every scored write is a numeric fee entry (delivery_service_charged).
  - subject delivery_charge_credited inherits six gates from three base policies (late credit, cancellation notice, approved damage claim) that no single credit satisfies -> no credit policies.
  - subject delivery_scheduled needs delivery_holdings evidence for a row that does not exist yet -> no booking policy.
  - holding updates (move/rebook/cancel) carry no numeric parameter -> not usable as a computed problem.
  - customer-chosen quantities (flights, items) are invisible to compute -> every root quantity must be record-derived.
  - replay closure: every seeded row must be read by some gold read; empty FK strings dangle -> omit empty FK fields.
- Claim plan (5 extended policies, pairwise disjoint):
  - task 0 (TV Delivery & Wall-Mount world): root wall mounting added after booking (owner=user) <- owed extended-distance charge (agent, value_input) ; root <- owed reschedule fee (agent, state_gate) ; reschedule fee <- extended-distance charge (value_input).
  - task 1 (Appliance Delivery & Installation world): root haul-away of the replaced appliances (owner=user) <- owed installation parts kit (agent, value_input).
- Identifier band: phones 6145550300-6145550399, member numbers 100300000000-100399999999.

## Task 0 — wall mounting added after booking (TV world)
- Draw: prerequisite_problems=2, factor_counts=[4,6,4] -> distance settlement 4, reschedule settlement 4, wall-mount addition 6.
- Policies appended to delivery.extended.yaml: delivery_ext_distance_settlement, delivery_ext_reschedule_settlement, delivery_ext_wall_mount_addition.
- Tools (uuid8 drawn one per tool): post_extended_distance_charge_120a0e6d (agent), post_reschedule_fee_c618067c (agent), authorize_wall_mounting_3e376943 (user). check_task_tools -> TASK TOOL CONTRACT OK.
- Seed written by _t0_seed.py (uuid4 ids): Club Plus member opened 2012-09-20; delivered purchase 2026-09-14 (75 in. + 65 in. TVs, $2,249.98, Northgate Visa); other purchases 2026-07-11 (43 in. TV + HDMI), 2026-05-30 (patio set + chairs, one chair returned), 2025-09-28 (laptop, outside 12 months); TV appointment 64 mi, radius 40, reschedule_count 2 (free 1), stairs entries 2+1 flights, haul-away entries 2+1 old TVs, no extended-distance entry, no reschedule fee entry.
- Verification (_verify.py, real tools, topological order distance -> reschedule -> mounting):
  - distance 26.25 (baseline 36.00; factor baselines: free miles 45.00, mile rate 31.50, 12-month scaling 35.00, return leg 13.12)
  - reschedule 30.00 (baseline 50.00; hold 26.25, route 22.50, Visa multiplier 40.00, courtesy 60.00)
  - mounting 247.41 (baseline 398.00; multi-TV 282.75, TV spend 261.62, tender 268.73, late 197.93, member tier 323.53, multi-service 304.50)
  - skip distance -> reschedule 22.50, mounting 266.44 (both value_input edges bear weight); skip reschedule -> mounting unchanged 247.41, terminal state lacks the reschedule fee row (state_gate edge).
- Task 0 assets written by staged scripts (_t0_persona.py, _t0_eval.py, _t0_comp.py, _t0_solv.py, _t0_rat1.py, _t0_rat2.py).
- Per-task gates task 0 (all --task 0): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (13 acts, closure 19/19); SOLVABILITY OK; COMPUTE OK (3 comps, 14 factors, 9 xfac, hist 8, brch 54); GROUNDING OK; CACHE-DIFF INFO (none); SCOPE OK. Traceability deferred (KB not rendered).
- Manual value gates task 0: recorded in design_rationale ("MANUAL VALUE GATES"). Task 0 closed.

## Task 1 — haul-away of replaced appliances (appliance world)
- Snapshot: occupied by task 0 = distance settlement, reschedule settlement, wall-mount addition + their 3 tools. Task 1 claims installation parts kit settlement (agent, state_due) + replacement haul-away (user, on_request). Nothing left for later tasks (M=2), every policy covered.
- Draw: prerequisite_problems=1, factor_counts=[5,5].
- Policies appended: delivery_ext_install_kit_settlement (5 factors), delivery_ext_replacement_haul_away (5 factors). Tools: post_installation_kit_charge_19cc3b17 (agent), authorize_haul_away_734a64e4 (user); TASK TOOL CONTRACT OK (5 tools).
- Design change during authoring: first draft of the contractor kit price used active business add-on cards; dropped because each add-on card issuance triggers addon_card_fee ledger rows in membership_transactions that would have to be seeded and read for no decision -> replaced by Business tier AND twelve-month major-appliance units.
- Seed (_t1_seed.py): Business Plus landlord opened 2009-09-28 (auto-renew on Northgate Visa); delivered purchase 2026-09-24 washer + electric dryer $1,799.98 (Northgate Visa); 2026-03-11 refrigerator; 2025-09-20 two dishwashers (outside 12 months); Appliance Delivery & Installation appointment 2026-10-08 08:00-12:00, 37 mi, one kit entry (units 1, $20.24 = the kit rule's price at booking with no kit standing).
- Verification: kit 18.56 (baseline 39.99; contractor 22.61, stock 20.24, tenure 21.26, scaling 24.74, tender 20.62); haul-away 40.80 (baseline 25.00; included 20.40, fee 52.80, planning 48.00, late 27.20, renewal 51.00); skip kit -> haul-away 20.40.
- Task 1 assets written by staged scripts (_t1_persona.py, _t1_eval.py, _t1_comp.py, _t1_rat.py). Per-task gates (--task 1): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (11 acts, closure 11/11); SOLVABILITY OK; COMPUTE OK (2 comps, 10 factors, 7 xfac, hist 3, brch 36); GROUNDING OK; SCOPE OK. Manual value gates recorded in its design_rationale. Task 1 closed.

## Final difficulty-wide run (no --task)
- check_extended: EXTENDED OK (5 policies, 5 tools, 2 tasks, coverage complete, scopes disjoint)
- check_task_tools: TASK TOOL CONTRACT OK (5 tools)
- replay_tasks: REPLAY OK (0.json 13 acts closure 19/19; 1.json 11 acts closure 11/11)
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK (suite means branches 45.00, steps 12.00; history_rows_max 8; branches_max 54)
- check_grounding: GROUNDING OK
- check_cache_diff: CACHE-DIFF INFO (no cache trap designed)
- check_cross_fire: SCOPE OK
- check_traceability: TRACEABILITY NOT OK — expected: the only uncopied values are the five hidden tool names, whose source is the published KB (docs/ not rendered yet). Re-run after erl-kb-doc-render.
- Coverage: task 0 = distance settlement, reschedule settlement, wall-mount addition; task 1 = install kit settlement, replacement haul-away. Every extended policy fires in exactly one task's computations.
- Temporary authoring scripts (_t0_*.py, _t1_*.py, _verify.py, id/plan json) deleted after closing.

## Rework round 2 (audits/policy_task/delivery_and_installation_appointments: _difficulty.md, 0.md, 1.md)
- F-1: reschedule settlement overwrite now supersedes the whole base sentence "A reschedule is free only when ... otherwise reschedule_fee_usd is charged ..."; its replacement keeps the notice rule for moves as they are made and adjudicates recorded moves by count (no request date is kept; a recorded move within the free reschedules without a fee entry stands as free).
- F-2: distance free miles replaced by a per-mile Plus reduction ($0.30 / $0.20 / 0); the reduced per-mile fee never falls below $0.60, so an appointment beyond the radius always owes a positive charge and its entry always exists (base "zero component not entered" no longer conflicts; tool "always positive" holds).
- F-3: distance per-mile tiers changed to $0.90 / $1.10, distinct from every service level's per-mile fee ($1.25, $1.50).
- F-4 / T0-1 / T1-1: scalar "method" factors removed or relabelled. distance: twelve_month_mileage_schedule (capped / graduated / flat) is the method; return-leg multiplier removed (also O-6, O-7); tenure discount (parameter) added. reschedule: storage_by_hold_span (daily accrual / flat / none) is the method; Visa multiplier -> northgate_visa_discount (parameter); courtesy replaced by crew_reslot_surcharge (parameter, stair-carry flights) so task 0 still reconciles 8 ledger rows. wall mount: late multiplier -> late_mounting_surcharge (parameter); member-tier pct 20 -> 15 (no half-cent figures). kit: installed_appliance_scaling -> kit_place_schedule (kits priced by place). haul-away: late multiplier -> late_removal_surcharge (parameter); planning reduction -> recycler_trip_schedule (consolidated / graduated / itemized).
- T0-2: 169 -> 168 whole months everywhere. T0-3 / O-1: all gold, sensitivity and baseline figures re-derived; raw products checked, none on an exact half cent.
- O-2: "At booking ..." clause declared superseded on reschedule, wall mount, kit and haul-away. O-4: reschedule edge condition no longer carries the units clause. O-T0-a/b, O-T1-a/d: rationale wording corrected.
- Gold now: task 0 distance 13.77, reschedule 73.65, mounting 266.44; task 1 kit 18.56, haul-away 36.00 (task-1 booking kit seed 20.24 -> 26.99 to follow the place schedule). Objects, order, owners, units unchanged.
- Final gate block: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (history_rows_max 8, branches_max 54); GROUNDING OK; CACHE-DIFF INFO; SCOPE OK; TRACEABILITY NOT OK (only the five hidden tool names, KB not rendered yet).
- Temporary scripts of this round deleted.
