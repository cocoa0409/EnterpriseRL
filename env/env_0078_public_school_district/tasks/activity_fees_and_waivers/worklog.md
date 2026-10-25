# worklog — activity_fees_and_waivers (env_0078)

## REWORK round 2 claims
Audit: audits/policy_task/activity_fees_and_waivers/{_difficulty.md,0.md,1.md} (revision_1). Every finding was verified against the artifacts before changing them; none was disputed.

Charter items (_difficulty.md):
- P1 → closed: all elapsed/used/spent counts now test clearance as of the date the status took effect (clearance_date <= effective date); the two trip counts were removed with F4.
- P2 → closed: each carry-back scope is now a record test ("a ... entry that carries no free_meal_waiver or reduced_meal_waiver credit"), implemented in compute (in_scope requires no waiver on that entry).
- P3 → closed: every carry-back is held to the fee net of waiver AND household_cap credits on that entry (base field rule "never more than the source charge net of earlier credits").
- P4 → closed: season-weeks text removed; the midpoint is one stated convention, half (rounded down) of the season's days from season_start_dates, counted from clearance, by season for per-season fees and for the school year otherwise.
- P5 → closed: every rule and baseline states the standard computation in its own words with one generic order sentence ("Any adjustment this schedule sets out ..."); no assembly sentence names a factor quantity.
- F1 → closed: every ratio-denominator factor (carryback_season_length, season_week_count, deposit_lead_tier, balance_lead_tier) and every additive add-on (hardship/medical/arrival, 7 factors) removed; the season length is now a plain base-derived binding.
- F2 → closed: schedule_base_rule removed as a factor; the unpaid/paid split is a plain binding stated once.
- F3 → closed: the three carry-back share ladders are no longer factors; the share is a plain base mapping applied inside the stated scope.
- F4 → closed: every factor struck as invented removed (tapers, due-date share, lead/spent prorations, notice share, used weeks, documentation shares, medical/hardship/arrival add-ons, release_doc_tier); no replacement invented.
- F5 → NOT closable without inventing factors: shortfall documented below for the coordinator's ruling.
- O1 → closed: with the hardship share gone, a late withdrawal without a qualifying statement credits 0.00 and books no credit row.
- O2 → closed: both trip-schedule overwrite tails now restate the standing trip schedule for a trip the district cancels for unsettled fees at the balance due date.
- O3 → closed: the leaving rule names the selection ("the latest by the date on it"); statements sharing a date share the value read.
- O4 → kept (observation): the lifecycle wording in the two user-tool docstrings describes the object's own state, not a tool order.
- O5 → kept (observation): the state is singled out by the rules (only a pre-clearance cancellation leaves withdrawn with no clearance date).
- O6 → closed: every waiver/cap read is filtered by the fee entry's own id.

Task items:
- 0.md#1 → per F1/F3/F4/F5: task 0 keeps elapsed_count_rule (carry-back) and leaving_share_tier (leaving credit); figures recomputed and propagated to GT, computations, closure and rationale; shortfall below.
- 0.md#2 → per P5.
- 0.md#3, 0.md#4 → observations, unchanged (passive persona line; credit balance refundable within 30 days, not owed at once).
- 1.md#1 → per F1–F5: task 1 keeps departure_share_tier and release_share_tier; the carry-backs keep none; enrollment and records-log rows and reads that fed only removed factors were removed; figures recomputed and propagated.
- 1.md#2 → per P5.
- 1.md#3 → closed: the physician statement row is gone (no factor reads it) and the persona no longer claims a note was turned in.
- 1.md#4 → observation, unchanged.

Factor shortfall per policy (drawn vs kept; dimensions checked):
- activity_ext_waiver_carryback (draw 4, kept 1 method): share by tier (only Free/Reduced non-zero; the zero tier is the scope), fee component (one waivable participation fee), cap (no cap credit; other participations unreadable in the DSL), season length (one value per season - plain).
- activity_ext_leaving_credit (draw 5, kept 1 parameter): type percentages (constant per variant, inside the ladder), midpoint convention (one value per season - plain), equipment (returned), installments (unavailable), late fee (on time), cut / ineligibility (not engaged).
- activity_ext_trip_deposit_carryback (draw 4, kept 0) and activity_ext_trip_balance_carryback (draw 5, kept 0): share (two non-zero tiers), component (fixed), cap (trip fees never count), proration (the trip has not taken place), installments (not on the plan).
- activity_ext_trip_cancellation (draw 6, kept 1 parameter) and activity_ext_trip_deposit_release (draw 5, kept 1 parameter): days-left schedule kept; documentation/medical/hardship/arrival removed as invented; a documented medical exception is real but no physician statement exists on this registration; late fee, equipment and installments not engaged.
- Task-level floors: task 0 keeps one multi-source factor (leaving_share_tier) and one cross-difficulty factor (elapsed_count_rule, meals); task 1 keeps neither.

Gate block (final, no --task): EXTENDED NOT OK (factor floors only), TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE NOT OK (factor floors and draw counts only), GROUNDING OK, SCOPE OK; traceability: only the six unlock tool-name misses (pre-render).
REWORK round 2: gates RED check_extended check_compute

## REWORK round 2 claims (continued)
Ruling read: audits/render_source/realism_bar.md (R1–R5 accepted, X1–X4 rejected, floors not waived). Audit files unchanged since the first section; every item id keeps the closure listed above (P1–P5, F1–F4, O1–O6, 0.md#1–4, 1.md#1–4). Item F5 (factor floor) is still open, for the reason below.

Why the drawn counts cannot be met with R1–R5 shapes on this difficulty's write events (checked event by event):
- Every task tree needs one owner=user write (owner_ruling (a)/(b)). The only user writes this charter allows are the family's withdrawal or cancellation credit, and the family's payment.
  - Withdrawal or cancellation credit: R2 (one timing schedule) plus the type percentages. A second proration on the same dates is X2. The meal-status waiver and household cap are already posted credits (X3).
  - Payment: R5 plan eligibility plus R5/R2 installment count or due count. When every installment is due, the payment equals the balance, so the count and remainder rules stop mattering.
  - None of these reaches 4 factors. Both draws need a user write with at least 4: task 0 is [5,4], task 1 is [5,5,4,6].
- Agent charge postings (activity_fee) are the only multi-dimensional writes, per the ruling's "Design consequence".
  - Usable keys on one participation: activity, campus level, grade band, season/semester, enrollment type (residence/employee child), start-date proration. That gives at most 5. A 6th (CEP or meal status) is either X2 against the separate waiver credits, or blocked by the frozen schema meaning of activity_fee.amount ("Fee before waivers").
  - The keys the ruling cites for multi-child pricing are sibling position and the household cap. The compute DSL scopes every history read to the one target holding and rejects own-category cross reads, so a household's other participations cannot be read.
- One technical route exists, and it needs a coordinator ruling because it changes what "target holding" means.
  - check_compute.build_env falls back to any table's row id. With target_holding_id set to the household (customers row), history reads filter on customer_id and can see every participation of the household.
  - That makes sibling position (R1) and the household cap (R5) computable. It also allows the family's own registration (activity_registration, a family act) to be a user write whose fee is computed at posting from activity, campus level, sibling position, enrollment type and start-date proration (5 keys).
  - On that route, P() and F() cannot be used (the customers row has no variant, and check_extended checks F() fields against activity_participations). Policies would read participation fields through LATEST over activity_participations, using a stated selection rule.
  - I have not taken this route, because it reinterprets the computation contract ("the holding in this category that this calculation acts on").
- Artifacts are unchanged from the first section of this round: honest factors only, all P-items closed.

Gate block (no --task): EXTENDED NOT OK (factor floors only), TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE NOT OK (factor floors and draw counts only), GROUNDING OK, SCOPE OK.
REWORK round 2: gates RED check_extended check_compute

## REWORK round 2 claims (continued 2)
Ruling applied: the household-row target is rejected (not used); the family's own registration/packet submission is approved as the customer write, with fees computed at posting. Audit item ids keep the closures listed in the first section (P1–P5, F1–F4, O1–O6, 0.md#1–4, 1.md#1–4). F5 (factor floor) is still open; findings below.

Technical constraint found first (check_compute.state_before/build_env): a computation is evaluated on initial_state plus the earlier gold writes, and its target holding must already exist there.
- A registration that creates its own participation cannot be scored on that participation.
- The only way to carry the approved route is a participation opened before the call (for example, opened by the director's roster) whose fees post when the parent submits the signed packet. That needs a declared overwrite of activity_evt_fees S1 ("On the registration date every fee component ... posts"), and the participation's registration_date then means the roster date.
- That framing is workable, and I used it in the placements below.

Placement tried for task 0 (draw [5,4]): root = travel fee posting (agent), waiting on the parent's packet submission, which posts the participation fee (user).
- Fine Arts Performing Ensemble (the best fit: travel fee, overnight permission, middle and high levels). Accepted keys found, each a three-tier ladder on records:
  - participation fee: ensemble (band/orchestra, theatre, otherwise), grade band x level (grade 06 at a middle school, 07–08 at a middle school, otherwise), enrollment type (non-resident, employee child, otherwise), late join (spring-semester join, mid-fall join, otherwise) = 4.
  - travel fee: ensemble, enrollment type, late join = 3.
  - Rejected for both: campus level on its own (only two values for Fine Arts, so no three-tier ladder); season (the ensemble is year-round); CEP and meal status (X2 against the separate waiver credits, and the schema meaning "Fee before waivers"); roster level (Fine Arts is cleared at not_applicable, so it is not on records).
- UIL Academic and Robotics Team (three levels): participation fee = activity, campus level, enrollment type, late join = 4 (grade band within a level is not a dimension this program's fees vary on); travel fee = activity, campus level, enrollment type, late join = 4.
- Result: the best task-0 placement gives [4,4] against [5,4]. The computation short by one is the 5-count problem, whichever of the two writes carries it.

Placement tried for task 1 (draw [5,5,4,6], one participation):
- Best honest menu per write:
  - packet participation fee: 5 at most (HS athletics: sport, season, campus, enrollment type, late join; grade band duplicates the varsity/sub-varsity level).
  - travel fee: 4.
  - leaving / cut / injury credit computed from raw records: 3 (the timing schedule; the meal-status waiver share only where no waiver credit is posted; the type's credit percentage). The household cap readable from this participation's own credits is a subtraction, not a ladder.
  - late registration fee: 2 (lateness, campus level).
  - equipment charge: 2 (replacement charge, days late).
  - payment: 2.
- No single participation carries a travel fee and a five-key sport schedule: HS athletics posts no travel fee, and Fine Arts and UIL Academic have no seasons. So the best four-problem tree on one participation reaches [5,4,3,2] or [4,4,3,2] against [5,5,4,6]. The computations short are the 6-count problem and the second 5-count problem.

Artifacts are unchanged from the first section of this round (honest factors only). I did not build a redesign that still fails the floors.

Gate block (no --task): EXTENDED NOT OK (factor floors only), TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE NOT OK (factor floors and draw counts only), GROUNDING OK, SCOPE OK.
REWORK round 2: gates RED check_extended check_compute

## REWORK round 2 claims (final)
Rulings applied: realism_bar.md AMENDMENT 1 (R6 only in slots that R1–R5 cannot fill); household-row targeting rejected and not used; the family's packet submission and payment are the owner=user writes (owner_ruling (d)). Base files unchanged. Overwrites are declared and scoped:
- activity_evt_fees S1/S2: fees of a roster-opened participation post when the packet is submitted.
- activity_payments_and_installments: the installment sentence, Fine Arts only.
The two programs' overwrite tails exclude each other by name. The earlier carry-back and leaving-credit design has been replaced in full. All six policies, the six tools and both tasks were rebuilt.

Items:
- P1 → closed by replacement: no elapsed/used counts remain. Every date read is a records-log received date, a ledger posted date, the roster date or a named param date, and each has a stated selection rule (latest by received date; the first checked_out checkout).
- P2, P3 → closed by replacement: no carry-back credits. Credits enter only through the installment's net reads, where each fee entry is netted against activity_fee_credit rows that carry that entry's own id (source_activity_ledger_id) and is never taken below 0.00.
- P4 → closed: proration uses stated conventions only. These are school_year_weeks 40, whole weeks from the roster date, and a flat spring share on or after spring_start_date.
- P5 → closed: each rule states its own standard computation and has one generic order sentence. No assembly sentence names a factor quantity.
- F1–F4 → closed: no X1–X4 factor remains. Every factor is R1–R5, or R6 under the amendment with the tags below. No factor cancels another. No floor creates an amount: each MX(0, ...) only clamps, and a 0.00 result posts nothing.
- F5 → closed: the drawn counts are met exactly. Task 0 is [5,4] and task 1 is [5,5,4,6]; check_compute matches them.
- O1–O3, O6 → closed by replacement. The withdrawal, trip-cancel and leaving rules are gone. Every waiver, credit and fee read is filtered by the fee entry's own id or fee_component.
- O4, O5 → observations: the tool docstrings describe only each object's own state.
- 0.md#1–4 and 1.md#1–4 → closed by the rebuilt tasks. Each task has:
  - A passive persona that states only the root request.
  - Edges that are engaged and unmet at the opening (no records-log or ledger rows) and that the packet resolves.
  - Load-bearing skips: task 0 travel 0.00; task 1 installment 147.00 / 122.50 / 168.87, and travel and late 0.00.
  - Probe tables kept in the rationales.

R6 factors (AMENDMENT 1). Each is keyed on a recorded attribute, uses plausible figures, has no conflict, is not X1 and passes XF. The R6 count per computation equals the draw minus its honest R1–R5 factors.

Task 0:
- booking_lead_tier (travel fee, draw 5, 4 honest, 1 R6).
  - Record key: records_log received_date of overnight_travel_permission, against the regional date.
  - Why R6: the UIL travel fee has only rate, level, residence and season keys on R1–R5.

Task 1 packet fee (draw 5, 4 honest, 1 R6):
- instrument_program_tier.
  - Record key: instrument_checkouts.usage_type, status checked_out.
  - Why R6: Fine Arts has no season or cap lever, and grade band is already the level factor.

Task 1 travel fee (draw 6, 4 honest, 2 R6):
- late_booking_tier.
  - Record key: the latest received_date among the packet's activity_document_received entries, against the trip date.
- instrument_haul_tier.
  - Record key: instrument_checkouts.usage_type.
- Why R6: no fifth or sixth R1–R5 key on a Fine Arts trip fee.

Task 1 late fee (draw 5, 3 honest, 2 R6):
- concert_rush_tier.
  - Record key: the packet received date, against arts_concert_date.
- fitting_tier.
  - Record key: instrument_checkouts.usage_type.
- Why R6: the lateness schedule, level and residency are the only honest keys.

Task 1 first installment (draw 4, 2 honest, 2 R6):
- plan_lead_tier.
  - Record key: the days from the roster date to the payment date.
- late_placement_tier.
  - Record key: the late fee's ledger posted_date, against the concert.
- Why R6: the plan count (R5) and travel placement (R2) are the only honest plan levers.

History: suite_max is now 9 history rows. The Fine Arts travel and late fees count the packet as received when its last form arrives, so they read all three forms on the records log. The installment reconciles three fee entries against their credits.

Sweeps:
- The compute_basis quotes are verbatim in each policy's text (checked by script).
- Stale proof text was swept, and the rationales were rewritten.

Gate lines (no --task):
- EXTENDED OK
- TASK TOOL CONTRACT OK
- REPLAY OK
- SOLVABILITY OK
- COMPUTE OK (history_rows_max=9, branches_max=71)
- GROUNDING OK
- SCOPE OK
- Traceability: only the five unlock tool-name misses before rendering.

Frozen times: T0 2027-01-27 15:30:00 CST; T1 2027-02-02 17:05:00 CST.
REWORK round 2: gates 7/7 green

## REWORK round 3 claims
Audit read in full: _difficulty.md (revision_1 and revision_2), 0.md and 1.md (both revisions), and realism_bar.md with AMENDMENT 1. Base files are unchanged. Every round-2 fix still holds; the revision_1 items were closed by replacement in round 2.

Charter items (revision_2):
- TS → closed. Both travel fees now price the trips the student actually takes. The rule lists each program's four scheduled 2026-27 trips. The method is uil_trip_share_rule / arts_trip_share_rule, R3, with three tiers: all four trips remaining = 100; two or three = that number out of four; one or none = the published single-trip percent per trip. No "spring trips only" framing remains.
- IN → closed. instrument_program_tier is removed. The Fine Arts packet's fifth slot is arts_campus_tier (R1, keyed on the campus on the enrollment record). Nothing in the participation fee or the attire package charges for the district instrument.
- LF → closed by removal. The Fine Arts late fee policy and its tool are gone.
  - Both packet policies overwrite base S2: an in-scope participation posts no late registration fee, and each tail names the sibling program.
  - With that, no discount or uplift on a penalty fee remains anywhere in the charter.
  - The UIL "late fee after 14 days" promise that no tool posted (observation UL) is also gone.
- FL → closed. Factor counts are UIL packet 4, UIL travel 5, Fine Arts packet 5, Fine Arts travel 6, Fine Arts concert attire 5 and first installment 4. Each policy has at least 2 parameter factors and 1 method factor, and the drawn counts match ([5,4] and [5,5,4,6]).
  - The new fourth task-1 problem is the concert attire package, an agent write on the uniform_package component, computed from raw records.
- A3 → closed. Each trip-date sentence is now read by two factors, the trip share and the booking or late-booking amount. A script sweep found no plain binding used by only one factor; the one hit (the attire packet's received date) was moved into concert_order_tier's bindings.
- B8 → closed across the whole class. "(day trips)", "(the beginner method book)" and "(the beginner group travels a shorter route)" are removed. The parentheticals left are variant names, base text, "(100 percent)" and one stated selection rule.
- RO → closed across the whole class. Every rule, overwrite and tail scopes itself with the exact record test "a <type> participation for the 2026-27 school year whose registration date is after 2026-08-03". "Roster-opened", "the director's roster opens" and "roster date" no longer appear in the charter or the tasks; the rules say "registration date".
  - The join, membership and rental-term methods were re-tiered inside that scope (full year within the grace days after the first practice / weekly proration / flat spring share), so no tier lies outside it.
- Observation, month-end due dates → kept as an observation: due dates fall on the same day of the following months, and the task date (the 2nd) has no month-end case.
- Observation, whose campus → closed for the new factors: the campus tiers read the campus on the enrollment record. The level tiers keep the participation's campus; it agrees with the enrollment campus in both worlds.
- Observation, the installment travel sentence → closed: the sentence now reads only "the travel fee the Fine Arts travel fee schedule owes".
- Observation WV → still not engaged: both students are Paid, so no meal-status waiver is owed when the fees post.

Task items (revision_2):
- 0.md#1 → closed per TS/FL: the travel fee's method is the trip share. Its figures were recomputed and propagated to GT, the computations and the rationale.
- 0.md#2 → closed per A3.
- 0.md#3 → unchanged: the round-1 items were closed by replacement, and the persona stays passive.
- 1.md#1 → closed per TS.
- 1.md#2 → closed per IN.
- 1.md#3 → closed per LF: the tree is now packet, travel and attire before the installment. Every edge is engaged and unmet at the opening and resolved by the packet or the fee postings.
- 1.md#4 → closed per FL.
- 1.md#5 → closed per A3.
- 1.md#6 → observations:
  - late_booking_tier and instrument_haul_tier remain R6-waived. Haul is moving the instrument on the trip, which the music usage fee (maintenance and cleaning) does not cover.
  - The up-front share of the first installment still follows from the published placement rules.
  - The zoned-campus note is unchanged.

R6 (AMENDMENT 1), all previously graded `R6-WAIVED`; the conditions are unchanged:
- booking_lead_tier, UIL travel: 4 honest + 1 R6. Record key: the received_date of the latest overnight_travel_permission, against the first team trip on or after it.
- late_booking_tier, Fine Arts travel: 4 honest + 2 R6. Record key: the packet's received date, against the first ensemble trip on or after it.
- instrument_haul_tier, Fine Arts travel: same computation. Record key: the music checkout usage_type in status checked_out.
- Why R6 for both travel slots: the travel fee's only honest keys are rate, level, residency and the trip share.
- Every other factor is R1–R5:
  - concert_order_tier: R2, days from the packet to the next concert on a goods fee.
  - plan_lead_tier and attire_placement_tier: R2.
  - plan_count_tier: R5.

A6 method pairs (all pass):
- The trip share: constant 100 vs a data-selected count out of four vs the published single-trip percent times the count. Their reachable values never coincide (100 / 50 or 75 / 0 or 30).
- The join, membership and rental-term rules: 100 vs whole-week proration vs a published flat share.
- travel_placement_rule: the whole net vs the net over the pre-trip due dates vs 0.

No factor cancels another, and no factor reads another factor's binding. X2 check: the trip share reads the registration date, while the booking, late-booking and concert-order amounts read the packet's received date, so no two factors in one computation share a date.

Sweeps:
- The compute_basis, baseline, policy_source and replaced_by texts are verbatim in each rule (script).
- The tool tokens are clean.
- No factor id is a substring of a tool name.
- The rationales, necessities and tracings were rewritten.

Gate lines (no --task):
- EXTENDED OK
- TASK TOOL CONTRACT OK
- REPLAY OK
- SOLVABILITY OK
- COMPUTE OK (history_rows_max=9, branches_max=90)
- GROUNDING OK
- SCOPE OK
- Traceability: only the six unlock tool-name misses before rendering.

Frozen times: T0 2027-01-27 15:30:00 CST; T1 2027-02-02 17:05:00 CST.
REWORK round 3: gates 7/7 green

## REWORK round 4 claims
Audit read in full: _difficulty.md through revision_3 with its post-freeze notes, 0.md and 1.md through revision_3, and realism_bar.md with AMENDMENTS 1 and 2. Base files are unchanged. Every item closed in revision_3 stays closed: RO, B8, A3, IN, LF, and the trip-share dimension under TS.

Items (revision_3):
- TR → verified and closed. A script confirmed that only uil_trip_share_rule and arts_trip_share_rule had a fall-through tier that differed from the declared baseline.
  - Both ladders, their rule sentences and their computes are reordered: one or none → the single-trip percent per trip; two or three → that number out of four; otherwise → the full travel fee (100 percent), which is the declared baseline.
  - The same sweep now finds every factor's fall-through equal to its baseline across all six policies.
  - The A6 half of TR was withdrawn by the auditor; it still passes, because the count tier adds an input and the reachable values stay distinct.
- AT → verified and closed. The base calls uniform_package_fee a "Student-kept apparel package" and says it is "ordered in the student's name".
  - rental_term_rule and every rental or proration parameter and sentence are removed, so the package is priced whole.
  - The method slot is now rush_order_rule (method, R2). It counts the calendar days from the packet's received date to the ensemble's next concert. Fewer than rush_short_days → rush_base_add plus rush_day_rate per day short; rush_short_days to under rush_mid_days → a flat rush_mid_add; otherwise → nothing, which is the baseline. This replaces the old concert_order_tier on the same dimension, so nothing is stacked.
  - The fifth slot is order_timing_tier (parameter, R2). The registration date is compared with the ensemble's published group order date and winter order date: after the winter order → individual_order_add; after the group order → winter_order_add; otherwise nothing.
  - The two factors read different recorded dates (packet received date vs registration date), so this is not X2. Neither factor prorates, and the attire fee keeps its drawn count of 5.
- FL → closed. Every policy now has a valid method factor with fall-through equal to baseline: uil_trip_share_rule, arts_trip_share_rule and rush_order_rule join the four methods that already passed. The counts are unchanged and match the draws ([5,4] and [5,5,4,6]).
- 0.md#1 (TR/FL) → closed per TR. Task 0's numbers are unchanged, because its world takes the two-or-three tier.
- 0.md#2 → stays closed (TS, A3, RO).
- 1.md#1 (TR) → closed per TR.
- 1.md#2 (AT) → closed per AT. The attire and installment figures, sensitivities, skip effects, tracings and rationale were recomputed and propagated.
- 1.md#3 (FL) → closed per FL.
- 1.md#4 → stays closed (TS, IN, LF, A3, RO).
- Observations → unchanged:
  - The campus source is stated in each rule.
  - Month-end due dates do not arise in the task worlds.
  - plan_total is the baseline's quantity, as the auditor's r3 A3 note accepts.

R6 (AMENDMENT 1): unchanged and still graded R6-waived by the auditor: booking_lead_tier, late_booking_tier, instrument_haul_tier. Condition 6 still holds (UIL travel 4 honest + 1; Fine Arts travel 4 honest + 2). The new attire factors are R2 timing schedules, not R6.

Sweeps:
- Every factor's fall-through tier equals its baseline.
- compute_basis, baseline, policy_source and replaced_by are verbatim in each rule.
- No single-factor plain binding remains, other than the accepted plan_total.
- No stale rental, concert_order or prior-round figures remain in the tasks.
- The rationales were rewritten.

Gate lines (no --task):
- EXTENDED OK
- TASK TOOL CONTRACT OK
- REPLAY OK
- SOLVABILITY OK
- COMPUTE OK (history_rows_max=9, branches_max=88)
- GROUNDING OK
- SCOPE OK
- Traceability: only unlock tool-name misses before rendering.

Frozen times: T0 2027-01-27 15:30:00 CST; T1 2027-02-02 17:05:00 CST.
REWORK round 4: gates 7/7 green

## REWORK round 5 claims
Input: audits/render_source/activity_fees_and_waivers/render_r1.md, the only file there, read in full. Each finding was checked against the yaml, the compute and blueprint.yaml before any change. Base files are unchanged, and both task worlds are unchanged. Every item the policy audit closed stays closed: revision_4 was CLEAN, all combination sentences keep their order, and every factor's fall-through tier still equals its baseline.

- F1 → verified and closed. The installment compute subtracted credits of every reason, and it summed every fee entry of a component while netting only the latest. The fix aligns the rule and the compute and closes the whole class (all three fee nets):
  - The rule now states the selection and tie rule: "Each fee is the latest entry of its fee component on the participation's ledger by posted date, the one recorded first when two share that date, and its net is that entry less the free_meal_waiver, reduced_meal_waiver and household_cap credits posted on it, never below 0.00".
  - The compute reads that one entry's amount (a SUM filtered by its id) and subtracts three SUMs filtered by credit_reason, each sourced to that entry.
  - New bindings fi_*_fee and fi_*_credits quote the net sentence.
  - Probes: the gold total is unchanged; a billing_correction credit leaves it unchanged; an older second fee entry leaves it unchanged; a reduced_meal_waiver on the latest entry lowers it as the rule says.
- F2 → verified and closed. blueprint.yaml lists "Sunflower Early Childhood Center, five elementary schools (...)", so Sunflower is not an elementary campus. It is removed from the elementary or-chain in uil_packet_fee.level_amount and uil_travel_fee.trip_level_amount, the only two policies that used it.
- F3 → verified and closed across the whole class. Every level or trip-group tier that reads F('campus') now says so: "for a participation at an elementary / a middle school campus whose student's enrollment record shows ...". Their ladders read "the participation's campus is ...". This covers uil_packet_fee, uil_travel_fee and arts_travel_fee. arts_packet_fee and arts_attire_fee already say "the campus on the student's district enrollment record". The task-0 tier_taken text was updated to match.
- The task values, sensitivities and skip effects are unchanged; the rationales hold as written.

Gate lines (no --task):
- EXTENDED OK
- TASK TOOL CONTRACT OK
- REPLAY OK
- SOLVABILITY OK
- COMPUTE OK (history_rows_max=9, branches_max=88)
- GROUNDING OK
- SCOPE OK
- Traceability: only unlock tool-name misses before rendering.

Frozen times: T0 2027-01-27 15:30:00 CST; T1 2027-02-02 17:05:00 CST.
REWORK round 5: gates 7/7 green

## REWORK round 6 claims
Audit read in full: _difficulty.md revision_5, plus 0.md and 1.md revision_5 (both tasks PASS). The one charter item is EN. Base files are unchanged, and so are both task worlds and every scored figure: expected values, sensitivities and skip effects were re-verified. Every combination sentence keeps its order, and every item closed in earlier rounds stays closed.

- EN → verified and closed across the whole class.
  - Verification: the enroll base says "A student who withdrew may be registered again in the same school year with entry_type re_entry". All 16 CFIELD('enroll', …, student_id, school_year) reads took the first matching row and stated no selection.
  - Compute: all 16 reads in the 5 policies now carry status='enrolled'. The reads are uil_packet ar_grade, lv_grade, en_type; uil_travel tr_grade, tl_grade, tn_type; arts_packet ea_grade, el_grade, cp_campus, rs_type; arts_travel ar_grade, tg_grade, tr_type; arts_attire ak_grade, ag_grade, ac_campus.
  - Rules: every rule sentence that names the record now says "the student's district enrollment record in status enrolled for the school year". Every ladder says "the enrollment record in status enrolled …", and the cross_category notes and reads (status added) match.
  - Tie: a withdrawn and re-registered year has exactly one record in status enrolled, because the withdrawn record keeps status withdrawn. That gives one reading with no tie.
  - Absent record: with no enrolled record for the school year, every enrollment-based tier takes its "otherwise" value.
  - Probes (run this round): a withdrawn 2026-27 decoy at another campus with Attendance Zone, stored before the real record, is not read, and the packet fee is unchanged. With only the withdrawn record on file, every enrollment tier falls to "otherwise".
  - No decoy is seeded. Neither world can honestly carry a withdrawn 2026-27 record: task 0's mid-year move is a transfer placement on the existing record, and task 1's student is new to the district. The probe is stated in both rationales instead.
- 0.md r5 and 1.md r5 → no items; both tasks pass and the values are unchanged. Task 0's tier_taken texts were updated to the new ladder wording.

Gate lines (no --task):
- EXTENDED OK
- TASK TOOL CONTRACT OK
- REPLAY OK
- SOLVABILITY OK
- COMPUTE OK (history_rows_max=9, branches_max=88)
- GROUNDING OK
- SCOPE OK
- Traceability: only unlock tool-name misses before rendering.

Frozen times: T0 2027-01-27 15:30:00 CST; T1 2027-02-02 17:05:00 CST.
REWORK round 6: gates 7/7 green

## REWORK round 7 claims (seed-only)
Audit read in full: audits/policy_kb/activity_fees_and_waivers/_difficulty.md, 0.md and 1.md (KB-VERDICT revision_1: task0=PASS, task1=PASS, kb=CLEAN, src=S1). activity.extended.yaml and task_tools.py are byte-identical (sha256 dab248c303c40c97… / 0040d1ba3cee1ae1…), task 0 is untouched, and base files are unchanged.

- S1 → verified and closed.
  - docs/music/due_back_dates_and_late_return_charges says "Large Instrument Usage (Tuba, Cello, String Bass) | May 21" and "The five school-year usage types share the due-back date of May 21".
  - The seeded checkout d7032204 carried 2027-05-27. It is re-seeded to 2027-05-21, the May 21 of its 2026-27 school year.
  - The rest of the row was checked against docs/music/, and every field is consistent:
    - usage type and instrument: tuba is listed under Large Instrument Usage;
    - grade 06 is admitted, and band is a listed ensemble course;
    - the 2026-27 enrollment record is in status enrolled, as the eligibility doc requires;
    - one row stands for the home-and-school pair, with the home instrument's serial;
    - status checked_out and the school year match;
    - the checkout date is a school-year checkout after the January 4 mid-year start, as the usage-fee schedule allows;
    - the repair, overdue, loss, police and return fields are empty, as they should be for an open checkout.
  - The usage-fee ledger row and the condition report stay as accepted residue: no gold step reads them, as the KB auditor's ruling notes.
- No other member: the auditor's exhaustive pass found no other inconsistent cross-product seeded row in either task.
- Scored figures are unchanged, re-verified this round: all four task-1 writes, every computation's expected value, baseline and sensitivities, and every skip effect are identical. Task 0 was not rebuilt.
- KB observations (concert attire grouping, installment count after the plan end, the base "ordered at clearance" wording, the zoned campus) are not source REDs and are left as recorded.

Gate lines (no --task):
- EXTENDED OK
- TASK TOOL CONTRACT OK
- REPLAY OK
- SOLVABILITY OK
- COMPUTE OK (history_rows_max=9, branches_max=88)
- GROUNDING OK
- SCOPE OK
- TRACEABILITY OK

Frozen times: T0 2027-01-27 15:30:00 CST; T1 2027-02-02 17:05:00 CST.
REWORK round 7: gates 7/7 green
