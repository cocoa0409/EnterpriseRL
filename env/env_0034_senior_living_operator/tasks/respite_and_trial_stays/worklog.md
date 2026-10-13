# worklog — respite_and_trial_stays (M=2), erl-task-instantiate

## Step 0 draws (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=2, factor_counts=[6,4,6]
- task 1: prerequisite_problems=2, factor_counts=[6,5,5]

## Asset ledger / scope plan
- Booking (respite_booking_create) is avoided: base gate guest_age is authority=mixed over a single
  correlation key and cannot be evidenced by both a system and a caller value in one binding; no task books.
- Conversion (respite_convert) is avoided: every converted_to_category value triggers a credit in another
  category (independent/assisted/memory), which a respite task tool may not write.
- User-owned writes must carry a numeric scored value: the respite_requests intake has no numeric field,
  so the customer's own writes are (a) the guest's signature on a registered extension request, which books
  the added nights (respite_extension + its declared respite_nightly_charge trigger), and (b) a payment.
- task 0 (in-stay): root = signed extension (user, 6 factors); prereqs = level-change segment (agent, 6),
  level-change adjustment credit (agent, 4). Chain: extension -> segment -> credit (both value_input).
- task 1 (reserved): pre-arrival advance payment (user root) + two fee postings; claims nothing of task 0.

## Decisions (unattended)
- A level change recorded by nursing (stay type, care points, level_effective_date updated) but not yet
  re-billed is the record-visible state the task-0 tree starts from: the latest charged segment still bills
  the booked type.

## task 0 closed (per-task gates green: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE)
- results: credit 3346.00, segment 3730.03, extension 1670.90 (baselines 2629.00 / 3976.00 / 1673.00)
- revision: extension history not load-bearing -> added COUNT of level-change segments billing the stay type on record.

## task 1 closed (per-task gates green)
- tree: advance payment (user root) -> returned-payment fee, medication setup (fan-out, both value_input, commute verified)
- results: fee 78.46, setup 92.76, advance 3994.72 (baselines 35.00 / 85.00 / 1444.22)

## difficulty closing
- final gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (history_rows_max=8, branches_max=57), GROUNDING OK, SCOPE OK; CACHE-DIFF info only.
- check_traceability skipped: the published KB does not exist yet.
- temporary authoring scripts removed.

## round 2 — policy_task audit closure
- F1: signed_extension edge condition now states the sentence's existence test (level_change segment billing the stay type on record); closure copy updated.
- F2: relevel_credit identifies the segment being re-leveled by basis + first night + stay type billed of the latest nightly charge; rule sentence added; credit unchanged 3346.00.
- T0-F1: near-misses seeded (closed Maple Glen IL residency; completed 2025 stay with a returned ACH on its own account); gold ledger read by customer_id.
- T1-F1: near-misses seeded (IL return 2025-09-12 outside 12 months; rescinded LifeCare agreement).
- O1/O2/O4 fixed; O-T0-2/O-T1-2 rationale corrected; O-T0-1/O-T1-1 kept (gate recomputes with float rounding), recorded in rationale.
- all gates green (traceability skipped: KB not published); temp scripts and __pycache__ removed.

## round 3 — revision_2 closure
- T1-R2-F1: rescinded LifeCare agreement edc2cbd3 now rescinded 2022-08-19 (day 4 of Harbor View's 7-day period), refund due 2022-09-18, closed 2022-09-12.
- O-T0-R2-1 / O-T1-R2-1: stale proof sentences in the two design rationales corrected.

## round 4 — merge acceptance validate
- task_tools.py no longer imports datetime: sign_stay_extension_37758bab computes the extension segment dates with two pure-integer calendar helpers (_day_number / _ymd, proleptic Gregorian) nested inside the tool so no extra module-level tool appears; round-trip checked over 1600-2421 with no mismatch; replay DB hash of both tasks identical before and after.
