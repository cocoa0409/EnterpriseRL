# worklog — reservation_cancellations_and_no_shows (category booking), M=2

## Step 0 draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=3 (4 problems), factor_counts=[5,4,4,4]
- task 1: prerequisite_problems=1 (2 problems), factor_counts=[4,4]

## Step 0 structural analysis (why the trees look the way they do)
Gate facts read from check_compute/check_extended: compute history primitives are scoped to ONE holding
(the reservation); own-category cross reads are forbidden; task tools write only this category. Hence a
value_input edge can only join two writes on the SAME reservation.
Money writes on one reservation carry exactly one independent rich quantity (the penalty owed); the
deposit movements after it (forfeit = net penalty, refund = remainder) are residuals of that quantity.
A residual can carry no factor of its own without breaking the deposit ledger; a residual can be a
factor-bearing problem only if it carries its own business rule (a handling fee the hotel keeps).
Modifications on a confirmed reservation give independent rich quantities: room-type re-pricing,
occupancy re-pricing, and the resort advance-deposit requirement for the changed room.
Every task needs >=1 owner=user write and the root must be the customer's own ask, the last write.

## Decisions
- D1 task 0 = consolidation at a resort (Ashbury Resort & Spa): guest asks to add her parents to her own
  room. Tree: add adults (root) <- room-type change (value_input: capacity, rate) ; add adults <- deposit
  top-up for the new room (state) ; deposit top-up <- room-type change (value_input: requirement reads the
  new rate) ; add adults <- removal of the same adults from the other reservation of the same stay (state:
  an adult is registered on one room per night). Room-type change is the guest's own confirmation (user).
  Deposit top-up uses event booking_deposit_collect (not in the blueprint claim list, no other difficulty
  owns booking events; base single-collection clause overridden by declaration). Requirement is computed
  on the room portion so that adding/removing adults never re-opens the deposit (no post-root obligation).
- D2 task 1 = late cancellation at a resort, app posted the plan's standard first-night penalty from the
  deposit: refund (root, guest's own refund instruction = user) <- penalty correction reversal
  (value_input: net penalty). Separate forfeit entry folded by declared overwrite (the penalty settled from
  money held is retained in the deposit; refund = held - net penalty - handling fee).
- D3 base frozen; every deviation declared in overwrite.

## Revision R1 (before any policy written)
- Symptom: a customer-chosen change (new room type, number of adults to add) is not visible to compute
  (build_env exposes only records, params and cross reads) -> a modification priced on a value the
  customer states cannot be machine-recomputed. Root cause: compute is records-only.
- Change: every computation is records-determined. Task 0 is rebuilt around an occupancy update the guest
  already made in the mobile app (records show 4 adults in a standard king at the double-occupancy rate,
  deposit not adjusted). Owed corrections, all records-determined:
  room move to the lowest-priced room type sleeping the adults (RC) -> extra-person re-pricing (OCC)
  -> advance-deposit top-up for the corrected rate (DT, root, paid by the guest = owner=user).
  4th problem: the parents' own room (B&B Package, same resort, same nights) cancelled late in the app,
  where the app retained the plan's standard first night from its deposit; the correction reversal of
  the excess (RV) must stand before any further deposit is collected from the same guest for the same
  stay (credits before debits).  value_input edges: OCC<-RC, DT<-OCC.  state/action edge: DT<-RV.
- Task 1: no-show at a resort reservation with a deposit; night audit marked it, charge not yet posted.
  NS (no-show charge, settled from money held) -> RF (refund of the money held beyond the charge, less a
  deposit handling fee; guest's own refund instruction = owner=user). value_input: RF<-NS.
  The separate forfeit entry is folded by declared overwrite in RF (the charge settled from money held
  is kept from the deposit; no forfeit entry is posted).

## Task 0 — policies written (Step 1) and first recomputation (Step 5 draft)
- Policies on disk: booking_ext_capacity_room_move (5 factors), booking_ext_extra_person_reprice (4),
  booking_ext_deposit_topup (4), booking_ext_penalty_excess_reversal (4). Tools on disk; TASK TOOL
  CONTRACT OK (4 tools).
- Draft world: frozen 2026-12-26 09:10 EST; R_a Flexible Rate SANRS standard_king, 4 adults recorded by
  the app at the 2-adult rate 389.00, 6 nights from 2026-12-27 (peak), deposit 435.68; R_b B&B Package
  same resort/nights, cancelled 2026-12-25 18:20 (after the 3-day resort deadline), app kept 493.92 from
  its deposit (penalty + forfeit). Platinum Elite, 31 night credits, Premier card, 5 stay credits in 12
  months (Dec-2025 stay is the near-miss at 12 months), Beach & Pool Club at SANRS (1 dependant).
- Handling-time results (scratch evaluator over the real tools): RC 408.75, OCC 435.42, RV 329.01,
  DT 91.00. Factor baselines: RC 398.83/421.50/414.00/418.75/414.70 (all-baseline 429.00); OCC
  425.42/462.08/442.08/440.75 (458.75); RV 164.10/316.11/287.78/310.69 (0.00); DT 0.00/266.57/
  222.68/149.52 (51.99). Edge skips: skip RC -> OCC 415.67, DT 67.11; skip OCC -> DT 58.74;
  skip RV -> DT unchanged 91.00 (state gate; terminal state loses the reversal row).
- R2: pct_cap_advance 0.30 -> 0.25 (the stay-share cap and club relief baselines coincided at 266.57).
- Task 0 closed: tasks/0.json written (persona, initial_state 28 rows, solvability_contract, evaluation
  16 actions, computations with factor_sensitivity, prerequisite_closure, design_rationale). Per-task gates
  --task 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK. History rows touched in task 0 = 2 (suite max >= 8 must come from task 1).

## Task 1
- Policies booking_ext_no_show_charge (4 factors) and booking_ext_deposit_refund (4) and tools
  post_no_show_charge_68d6e4c0 / request_deposit_refund_05a65982 (owner=user) written.
- World: Edwin Ashcombe, Ashbury Reserve Carmel 71820457, Semi-Flexible Saver, one-bedroom suite
  790.00, 4 nights from 2026-11-26 (peak), no_show; four deposit payments (booking + three upgrades)
  = 872.95; Silver Elite 18 credits, Ashbury Rewards card, 5 stay credits in 12 months.
- Results: no-show charge 739.88 (baselines 709.05/822.09/778.82/778.82, all 872.95); refund 125.09
  (133.07/106.07/122.42/123.09, all 133.07); skip the charge -> refund 845.95.
- R3: steady_stays 8 -> 6 so the 12-month near-miss bears on the tier. R4: COMPUTE flagged the no-show
  history as not load-bearing (LATEST is not zeroed by the gate) -> the saver rule now also requires the
  reservation to carry more than one deposit payment (COUNT), rule/basis/ladder updated together.
  R5: refund overwrite replaced_by made a verbatim substring of the rule.
- Per-task gates --task 1 green (REPLAY, EXTENDED, COMPUTE hist=9, SOLVABILITY, GROUNDING, SCOPE, TOOLS).

## Final difficulty run (no --task)
EXTENDED OK; TASK TOOL CONTRACT OK (6 tools); REPLAY OK (0.json 28/28, 1.json 26/26);
SOLVABILITY OK; COMPUTE OK (branches mean 50.50, steps mean 13.00, history_rows_max 9, branches_max 69);
GROUNDING OK; SCOPE OK; CACHE-DIFF INFO (no cache trap). Traceability skipped: KB not yet published.
Known realism risks for the audits: (1) the further deposit writes booking_deposit_collect, an event the
blueprint claim lists for no difficulty (single-collection clause overridden by declaration);
(2) the refund's handling-fee factors and the no-show refund on a no_show reservation rest on declared
overwrites of booking_evt_deposit_settlement; (3) the deposit top-up waits on the reversal of the other
reservation's excess (action-form edge across two reservations of the same stay).
Temporary authoring scripts lived in /tmp/erl36 (outside the write domain); __pycache__ removed.

# Round 2 rework (audit: audits/policy_task/reservation_cancellations_and_no_shows/{_difficulty,0,1}.md)
Plan, item by item (decisions recorded before editing):
- F1 / T0-1: declare in booking_ext_penalty_excess_reversal.overwrite the base booking_evt_penalty_reversal
  clause "penalty_basis_misapplied applies when ... only the excess is reversed", replaced by the extended
  sentence that measures the excess against the penalty the late-cancellation rules owe.
- F2 a/b, T0-2, T1-1: stay-history ladders now count "stays credited" (stay night-credit postings), say
  so in words, and state the window boundary (a posting on the same calendar day twelve months earlier is
  outside). Compute unchanged (XCOUNT of postings, MONTHS < 12) -> rule and compute agree.
- F3: the move rule states that a move never lowers the rate (no supplement when the new differential is
  below the old one), so the floor in gross_diff now has a basis sentence.
- F4 / T0-3 / T1-3: the three co-brand-card reliefs are removed. Replacements: reversal -> holiday
  (peak-season) penalty floor (resorts publish stricter holiday terms); no-show and refund -> direct
  booking member courtesy / processing-fee waiver (book-direct member benefit).
- F5 / T1-2: late_change_saver_pricing removed; the no-show charge's method factor is now the no-show
  night basis (package inclusions not served are not charged; extended stays pay a share of the stay).
  Task 1 world rebuilt: B&B Package Rate, 7 nights over Thanksgiving, deposit grown under the further-
  deposit rule to 1.75 nights, so the no-show charge stays below the money held and the refund is real.
- T0-5: rationale corrected (2025-12-20 is 12 months and 6 days back).
- Observations also closed: topup <- reversal converted to state form (a penalty reversal entry naming
  the kept penalty); strengthened conditions rewritten to the sentence's strength; extra-person ladder
  outcomes expressed as plan charge plus a season supplement (no B&B inversion); deposit_topup second
  overwrite (at-booking deposit) dropped, base at-booking clause stays in force; refund overwrite
  replaced_by no longer extends "on the guest's own instruction" to relocations; inputs.history completed.
- Kept with reason: booking_deposit_collect outside the blueprint claim (no other route exists for a
  further deposit; recorded); elite courtesies and card_upgrade_credit (observations, not RED).
- Round 2, task 0 done: charter patched (RC floor sentence, OCC stays wording + boundary + season
  supplements, DT state-form edge / dropped second overwrite / full inputs.history, RV new block with the
  declared base reversal clause and holiday_penalty_floor in place of card_penalty_relief). Recomputed:
  RC 408.75, OCC 435.42 (unchanged), RV 329.01 -> 219.07 (baselines 127.46/310.69/197.57/150.36, all 0.00),
  DT 91.00 (unchanged). 0.json traces, closure, contract, rationale updated. --task 0: EXTENDED, COMPUTE,
  SOLVABILITY, REPLAY, GROUNDING, SCOPE OK.
- Round 2, task 1 done: world rebuilt (B&B Package Rate, one-bedroom suite 832.00, 7 nights from
  2026-11-25, booked 2026-07-01, deposits 616.00 / 562.10 / 173.25 / 250.25 = 1601.60 under the
  further-deposit rule; frozen 2026-11-27; 12-month near-miss posting moved to 2025-11-27). New no-show
  charge 1532.64 (baselines 759.02/1601.60/1601.60/1580.04, all 915.20); refund 65.86 (68.96/48.71/
  64.82/63.79, all 68.96); skip the charge -> 1592.60. Persona, traces, contract, rationale updated.

## Round 2 closure list
- F1 / T0-1 -> overwrite of booking_evt_penalty_reversal's penalty_basis_misapplied clause declared.
- F2 / T0-2 / T1-1 -> stay ladders count stays (postings) and state the window boundary, rule = compute.
- F3 -> move rule states "A move never lowers the nightly rate" (basis of the gross_diff floor).
- F4 / T0-3 / T1-3 -> card reliefs removed; holiday_penalty_floor (reversal), direct-booking courtesy
  (no-show) and direct-booking fee waiver (refund) added.
- F5 / T1-2 -> late_change_saver_pricing removed; no_show_night_basis method; task 1 world rebuilt.
- T0-4 / T1-4 / charter observations -> state-form topup<-reversal edge, conditions at sentence strength,
  season supplements (no B&B inversion), dropped at-booking overwrite on deposit_topup, refund
  replaced_by narrowed, inputs.history completed; kept: booking_deposit_collect outside the claim,
  elite courtesies, card_upgrade_credit (observations).
- T0-5 -> near-miss wording corrected.
Final run: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE (hist max 9, branches max 69),
GROUNDING, SCOPE OK; CACHE-DIFF INFO. Traceability skipped (KB unpublished).

# Round 3 rework (audit revision_2: task 0 PASS, task 1 RED on F6 / T1-5)
Decision: F6 is closed by conforming to the plan's release rule, not by overriding it. Real no-show
practice for a plan that releases the nights after the first (B&B Package, Flexible, Saver...) is one
night; the extended-stay share is removed. no_show_night_basis now chooses what the one no-show night
contains (services not provided are not charged): package plan -> the night less the package supplement;
another plan with adults beyond those the rate covers -> the night less their extra-adult charge;
otherwise the plan's basis (first night, or the whole stay on a plan that retains it). The rule now says
in words that the nights after the first stay released as the plan provides, so the base release
sentence stays in force and needs no override.
Task 1 world re-tuned so every factor still bears weight: booked 2026-08-10 (107 days before arrival,
so the further-deposit cap tier does not apply and the deposit is 2 nights = 1830.40 after three
upgrades), refund long-hold days 120 -> 100 (booked 109 days before the refund). Task 0 untouched.
- Round 3 results: task 0 unchanged (408.75 / 435.42 / 219.07 / 91.00, every baseline unchanged).
  Task 1: no-show charge 729.83 (baselines 759.02/810.92/768.24/752.40, all 915.20); refund 1091.57
  (1100.57/1080.32/1088.57/1085.57, all 1100.57); skip the charge -> 1821.40. Extra-adult tier limited
  to plans that release the nights after the first (Advance Purchase keeps its full-stay retention).
  Deposits re-derived 616.00 / 730.40 / 198.00 / 286.00 = 1830.40. 1.json traces, closure, contract,
  rationale updated. Round-2 observation "1702.94" disappears with the extended-stay tier.
- Round 3 closure: F6 / T1-5 -> no_show_night_basis conforms to the release rule (no override needed);
  observations carried unchanged (claim boundary, courtesies, card upgrade credit, state_gate field,
  adults above 6, handling-day posting edge, seeded no_show without the event-triggered charge).
- Final run: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE (hist max 9, branches max 69),
  GROUNDING, SCOPE OK; CACHE-DIFF INFO; traceability skipped.
