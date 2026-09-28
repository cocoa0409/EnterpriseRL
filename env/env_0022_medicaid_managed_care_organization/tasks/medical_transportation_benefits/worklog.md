# worklog — medical_transportation_benefits (category ride), M=2

## Step 0 — difficulty pre-check
- Read references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/ride.yaml, db_schema.json, share_tools.py.
- Identity preamble: find_customers -> verify_member_identity (K=2 credentials; name not a credential).
- Identifier band: phone 4025540000-4025540999, medicaid_id PR40000000-PR49999999, ssn_last4 4000-4999.
- DSL limits that shape every design: history primitives are scoped to the holding with equality filters and
  whole-month windows only; "the claimed trip" is reached with LATEST over the booked legs ordered by
  appointment_date (the claimed trip is the latest of its kind in each world); the current / previous benefit year
  is derived as MONTHS('2000-01-01', NOW)//12 + 2000; compute can only read records, never a caller statement,
  so every reimbursement amount is an allowance computed from records (no receipt amounts).
- Numeric write slots in ride: ride_ledger (allotment load / debit / expire trips; approved mileage,
  lodging_meals, late_pickup_alternative amount; paid amount). Six problems chosen:
  B lodging & meals allowance, A trip mileage, K trip settlement payout (Mileage member, task 0);
  E previous-year expiry, D new-year allotment load, C alternative-ride allowance (Door-to-Door member, task 1).
- Draws (scripts/draw_counts.py --tasks 2):
  {"task": 0, "prerequisite_problems": 2, "problems": 3, "factor_counts": [4, 6, 4]}
  {"task": 1, "prerequisite_problems": 2, "problems": 3, "factor_counts": [5, 4, 6]}
- Headroom: task 0 claims {B, A, K} (Mileage-level reimbursement chain); task 1 keeps the value-added allotment
  ledger (year-end expiry, new-year load) and the late-pickup alternative ride, all untouched by task 0.

## Task 0 — design thesis
Surface goal: a Mileage Reimbursement member who drove to a two-week radiation course 218 miles away asks to have
her trip money put on her prepaid card. Root = K (trip settlement payout, owner=user, on_request).
Hidden chain: K waits on the trip's approved mileage entry (A, state_due); A waits on the trip's lodging and meals
entry (B, state_due). Order B -> A -> K. Edges: A->B value_input (local stay trips), K->A value_input (settlement
sums the mileage entry). Factor counts: B=6, A=4, K=4.

## Task 1 — design thesis
Surface goal: a Door-to-Door Assist member whose return pickup from a value-added pharmacy trip in January was
late asks to be paid back for the cab home. Root = C (alternative-ride allowance, owner=user self-service claim).
Hidden chain: C waits on the new benefit year's allotment load (D, state_due); D waits on the previous year's
expiry entry (E, state_due). Order E -> D -> C. Edges: C->D value_input (enhanced value-added share reads the
load), D->E state_gate. Factor counts: C=6, D=5, E=4.
- Step 2 (task 0): tools approve_stay_lodging_meals_3bb3a021 (agent), approve_trip_mileage_f67ba186 (agent), collect_trip_settlement_816cec94 (user) written; check_task_tools -> TASK TOOL CONTRACT OK. Policies ride_ext_stay_lodging_meals (6 factors), ride_ext_trip_mileage (4), ride_ext_trip_settlement (4) appended.
- Task 0 CLOSED: frozen 2026-11-25 10:20 CST; gold B=1720.25 (step 9), A=179.66 (step 11), K=1943.41 (step 13, user). Per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK, CACHE-DIFF INFO. Revisions: inlined tool helpers; history made load-bearing via SUM/MAX over the trip's legs and entries. Full dossier in tasks/0.json design_rationale.

## Task 1 — Step 0 (claim)
- Draw: {"task": 1, "prerequisite_problems": 2, "problems": 3, "factor_counts": [5, 4, 6]} -> C=6, D=5, E=4.
- Occupied by task 0: ride_ext_stay_lodging_meals, ride_ext_trip_mileage, ride_ext_trip_settlement and their three tools.
- Claimed: ride_ext_year_end_expiry (E, ride_allotment_expire, expire_year_trips_0d38b23b agent),
  ride_ext_year_allotment_load (D, ride_trip_allotment, load_year_allotment_a6239ac8 agent),
  ride_ext_alt_ride_allowance (C, ride_mileage_approved type late_pickup_alternative, file_alternative_ride_claim_fa98ae6a user).
- Edges: C -> D value_input (gate va_share: the covered value-added share reads the leg year's loaded trips less its debits),
  D -> E state_gate (gate ride_ledger.benefit_year: the previous year's expiry entry). Carried trips are not re-loaded
  (the unexpired previous-year trips stay in the balance), so the ledger integral stays consistent.
- Redesign note: C's first cap ladder used a standing-order condition; changed to return leg AND Pregnancy Care so that
  C's cross-category reads are load-bearing as a whole (auth alone would not move C's number in this world).
- Task 1 structure written; per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (after adding find_pcp_assignments / find_rx_coverages reads so the parent rows enter the closure), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Gold E=2 (step 14), D=23 (step 16), C=61.53 (step 18, user).

## Difficulty-level closing
- Coverage: task 0 = {ride_ext_stay_lodging_meals, ride_ext_trip_mileage, ride_ext_trip_settlement}; task 1 = {ride_ext_year_end_expiry,
  ride_ext_year_allotment_load, ride_ext_alt_ride_allowance}; pairwise disjoint policies and tools; all six policies covered; no idle tool.
- Final gates (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (suite means branches 42.00, steps 16.50;
  history_rows_max 29; branches_max 44); GROUNDING OK; CACHE-DIFF INFO; SCOPE OK. check_traceability not run: KB docs not yet published.
- Prerequisite sentences across the charter: two affirmative ("is fixed only after") and two negated ("is not released/loaded until");
  all state form; no rule names another problem's tool or id.
- Temporary authoring scripts live only in the session scratchpad; nothing temporary remains in this directory.

## Round 2 rework (audits/policy_task/medical_transportation_benefits)
- F-C1 / T0-F1: stay_nights_counted relabelled parameter; nightly-rate ladder replaced by method stay_length_lodging_taper (three-band / two-band / flat piecewise lodging pay). Task 0 values and dossier re-derived (verify.py spec_t0.py).
- F-C2 / T1-F1: multiplier stranded_wait_factor replaced by method stranded_waiting_charge (per-minute / flat / none, added to the fare). Task 1 claim re-derived (verify.py spec_t1.py).
- Observations closed: O-RC-1, O-RC-2, O-RC-3, O-RC-4, O-RC-5, O-AB-1, O-PS-1, O-PS-2, O-OV-2, O-OV-3, O-OV-4, persona weekday slip.
- Full gate block re-run: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK;
  check_traceability NOT OK only on the unlock tool names, which reach the agent through the KB that is not yet published.

## Round 3 rework (audit revision_2)
- F-C4 / T0-F2: settlement clock middle tier now reads the return leg's registration after the outbound date (extended stay), reachable by settled trips; gold unchanged.
- F-C3 / T1-F2: waiting-charge ladder partitions late pickups only (metered from window end / metered from threshold / flat), flat charge moved into the baseline; claim unchanged, waiting baseline and all-baseline figures updated.
- O-FL-4: mid-drive miles 100 -> 150; O-FL-5: regional/metro trip miles 50/150 -> 150/200; no task value moved.
- Gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred (fails only on the six hidden tool names in unlock steps; KB not published).
