# Renderer scan-first findings — product transport, render round 1 (renderer findings filed verbatim by the coordinator)

# Render source scan — transport (bus_eligibility_and_stops), env_0078, round 1
Gate line: `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN` (ok). Source: tasks/bus_eligibility_and_stops/transport.extended.yaml (EXT below) + task_tools.py.
compute_basis sweep (B5): every quote is verbatim in its rule; every baseline.rule sentence, replaced_by and policy_source is verbatim in its rule. Tool docstrings match their bodies (B6). Findings below are rule-vs-compute or structure mismatches. STOP: no document written.

## S1 (B1, P1 transport_ext_meal_status_fee_adjustment): cap leaves out cancellation/proration credits
- Rule (EXT l.924): "...never below zero and never more than the fee net of every credit already against it, rounded half-up to the cent once on the result"
- Compute (l.952/970): `credits_against_fee: "meal_waiver_credits + SUM(... credit_reason='household_cap') + prior_corrections"`; `result: "RND(MN(MX(0, fee_posted - credits_against_fee), ...`
- The policy is scoped to ended/cancelled assignments too (l.927 "the last day of the adjustment window is the end_date of an assignment in status ended or cancelled"; compute `window_last_day`). A `cancellation_window` or `capacity_revocation_proration` credit against the fee is "a credit already against it" by the rule but is not in the cap.
- Witness (hypothetical): annual fee 240.00 posted in July, reduced waiver 120.00; Free status took effect Aug 1 (before the first school day); family cancels within 10 days of start, cancellation credit 120.00 posts (net fee now 0.00). Rule: adjustment capped at 0.00. Compute: cap = 240 - 120 = 120 → 120 × 1 month / 10 = 12.00.

## S2 (B1 window edge, P1): "inside the permit period" vs "on or after the first school day"
- Rule (l.933): "for a status resting on a household application received after the fee posted, inside the permit period and in an earlier calendar month than the month the status took effect, the month of receipt adds ..."
- The rule's own definition of the period (l.924): "running from August through May for a school_year fee, August through December for a fall_semester fee and January through May for a spring_semester fee".
- Compute (l.967 `receipt_part`): `DAYS(period_first_school_day, application_received) >= 0` — i.e. on or after Aug 12 / Jan 6.
- An application received Aug 1-11 (or Jan 1-5) is inside the permit period by the rule's words but adds nothing in compute. Ladder text (l.1062) repeats "inside the permit period".

## S3 (B1, P1 + P2): MX(1, months the fee covers) where the rule divides by the months themselves
- P1 rule (l.931): "the held-seat charge is the fee less its application charge, times the held months divided by the months the fee covers plus the held months." Compute (l.964): `... / (MX(1, fee_months) + ...)`.
- P2 rule (l.1123) same sentence; compute (l.1164) `/ (MX(1, fee_months) + ...)`. P2 rule (l.1120): "Every month a schedule below adds is added to the credited share at one month's share of the months the fee covers (one divided by them)"; compute (l.1171) `notice_months / MX(1, fee_months)`.
- For a semester fee posted on or after the first school day, the months the fee covers are a day-count fraction ("the calendar days from the posting day to the period's last day divided by the calendar days from the period's first school day to its last day, times the months of the permit period") and fall below 1 when the fee posts in roughly the last fifth of the semester (e.g. a fall seat signed in December). Rule and compute then give different figures. (P4 is unaffected: seat months are whole months ≥ 1.)
- Witness (hypothetical): fall seat offered Nov 20, signed Dec 8 → fee months = 5 × 23/141 ≈ 0.816; held fraction rule 1/1.816 ≈ 0.551 vs compute 1/2 = 0.5.

## S4 (B1 boundary, P3 transport_ext_offered_seat_permit_fee): equality at the walk-zone figure is undefined
- Rule (l.1342): "a rider living inside that walk zone has walk_zone_add_annual added ...; a rider living outer_band_miles or more and outside the walk zone has outer_band_less_annual or outer_band_less_semester added; any other rider has nothing added."
- Compute (l.1369): `F('measured_distance_miles') < rider_walk_zone` (inside) and `>= K('outer_band_miles') and >= rider_walk_zone`.
- The rule never says whether a distance equal to the walk zone is inside. walk_zone_miles_secondary = 1.50 = outer_band_miles: a secondary rider measured at exactly 1.50 mi gets +24.00 under "inside includes the boundary" and -24.00 under compute (elementary 1.00 mi: +24.00 vs 0). Needs an explicit "less than" / "at or under" wording.

## S5 (B1 negative lag, P1): status that took effect after the window's last day still adds a month
- Rule (l.932) Annual tier: "the whole calendar months after the month the status took effect through the month of the last day of the adjustment window, plus the month the status took effect counted as month_part_whole month when it took effect on or before the 10th day ..."; compute (l.966) `MX(0, MONTHS(status_effective, ..) - MONTHS(window_last_day, ..)) + (K('month_part_whole') if ...)`.
- When the assignment ended/cancelled before the status took effect (window last day earlier than the effective month), both rule and compute still add the effective month (and S2's receipt month, l.933/967, has no window test either), crediting a month after service ended. The rule states no handling for an effective date after the window's last day; B1 asks for it (e.g. "nothing when the status took effect after the last day of the adjustment window").

## S6 (A4/A10, P3 and P1): a record selection shared by two factors lives inline in each, and one factor sentence leans on another's
- P3: the distance-table sentence (l.1342, factor walk_zone_distance) reads "against the walk zone of the rider's school level on that enrollment record" — "that enrollment record" is defined only in the school-level sentence (l.1341, factor school_level_rate): "the rider's grade on the latest-registered district enrollment record for the school year". Compute re-reads the same XLATEST grade inline in `level_rate` and `rider_walk_zone`. A4: "Shared record selections are a plain binding stated once in the rule"; the walk-zone factor doc cannot name its record without the other factor's sentence.
- P1: the household-application read is the factor binding `application_received` (factor application_receipt_part) and is re-read inline in `counted_months` (factor month_count_method: "or rests on a household application received in an earlier calendar month"); the shared selection (which application: the one the status on file rests on) is not a plain binding stated once.

## S7 (B1, P4 transport_ext_seat_fee_meal_waiver): cap counts credits that are not against the fee
- Rule (l.1521): "never more than the fee net of every credit already against it"; compute (l.1553) `credits_against_fee: "SUM('transport_ledger', 'amount', event_type='transport_fee_credit')"` — every credit on the assignment, including `free_replacement` credits that base transport_bus_pass posts against replacement pass fees (a non-damage pass exchange is credited "in full the same way" on courtesy permits too). Lower reachability (needs a pass exchange before the seat waiver is figured), same class as S1.

## S8 (C4 out-of-scope fallback, P4): in-force base waiver text vs compute
- replaced_by (l.1497) keeps for every non-seat fee: "waived by credit from the student's School Nutrition meal status on the posting date". Compute (l.1559) returns 0 whenever the status on file "took effect after the fee's posting date", rather than the status held on the posting date. They diverge for a non-seat fee whose student's status changed after posting, if the posting-date status is visible in the meal records. Flagged for the coordinator's judgment; lower priority than S1-S6.
