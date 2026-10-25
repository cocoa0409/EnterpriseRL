# worklog — extended_day_care_billing (env_0078_public_school_district)

Round 1 design notes are in plan.md (kept for history; its round-1 tree is retired). Round 2 rebuilds both trees; tasks/0.json and tasks/1.json carry the full dossier in design_rationale.

## Round 2 rebuild
- Draws (draw_counts.py): task 0 prerequisite_problems=3, factor_counts=[5,4,4,4]; task 1 prerequisite_problems=1, factor_counts=[4,5].
- Task 0 (frozen_time 2026-11-20 10:30:00 CST, Ngozi Okafor): root care_ext_current_year_payment_plan (owner user) <- care_ext_late_pickup_fee_schedule, care_ext_late_payment_fee_schedule, care_ext_booked_day_fee_schedule (three state-form value_input edges; the fee postings commute).
- Task 1 (frozen_time 2026-08-04 11:20:00 CDT, Maren Lindqvist): root care_ext_prior_year_installment_payment (owner user) <- care_ext_notice_period_credit (action form, declared fallback).
- Retired: care_ext_meal_rate_tuition_credit, care_ext_late_fee_reassessment, care_ext_account_settlement_payment and their tools; the round-1 notice credit and installment factors (tenure, refund weeks, uplift, up-front fee, older-balance addition).
- Manual gates (both tasks): problem tree walked hop by hop; every edge engaged, unmet at the opening, satisfiable by its resolver, load-bearing by skip replay; persona asks only for the root and volunteers no prerequisite fact; base eligibility per write subject aligned (policy_scope, day_fee_on_active_enrollment, courtesy_waiver_remaining, certified_funds_after_returns); every factor's tier rests on seeded rows, its baseline is the computation document's standard value and substituting it moves the scored number; cross-difficulty reads (enroll grade, enroll status/withdrawal date and record type, meals benefit level/effective date) bear weight; decoy/absent-record probes listed per task.
- Sweeps: compute_basis / baseline / prerequisite sentence / replaced_by verbatim in their rules (0 misses); forbidden task_tools substrings none; no factor id inside a tool name; no figure within 1e-6 of a half cent; frozen_time format valid; traceability pre-render shows only the unlock tool-name misses expected before the KB is published; validate_scenario shows only the not-yet-rendered required documents.

## REWORK round 2 claims
- C-OVR-1: the tuition re-pricing policy is retired; every new policy overwrites, sentence by sentence, the base clause it changes (late pickup fee, late payment fee posting, day fees, suspension, notice billing, prior-year registration gate) and scopes the change to its own case.
- C-OVR-2: the notice credit rule no longer restates the retired base clause; the billing end is stated generically and only the standard notice period, labelled standard, names the base length; all other baselines are labelled standard.
- C-PRE-1: each edge is carried by exactly one prerequisite sentence in the blocked rule; no resolver rule carries a second trigger wording of an edge.
- C-PRE-2: every state-form edge now waits on exactly the object its resolver prices (most recent chargeable pickup, most recently posted tuition charge, most recent booking request), so the resolver satisfies it in every engaged world.
- C-SCOPE-1: the advance clause is gone; the payment plan is scoped to current-year enrollments and prior-year balances go to the installment arrangement.
- C-A1: every factor reads only its own bindings and record primitives; billing end, shares, counts and amounts are assembled in plain bindings only.
- C-A2: every assembly sentence is a generic order sentence naming no factor quantity.
- C-A6: every method factor's tiers differ by an input or an operation (quarter-hour ceiling / minimum block / as recorded; percentage with floor / base fee / none; camp / early-release / drop-in selection; fee-first / minimum-floored / equal share; by-day / by-week / standard proration); counting day is now a parameter.
- C-A8: no factor re-applies a discount already embedded in a recorded amount; every fee is a new posting priced from raw records and the hardship terms change a payment count, not a discounted base.
- C-A9-1: the case-number status-count factor is retired; every ladder's text matches its compute, and the whole-week proration tier now requires the district record it names.
- C-REAL: notice charges, hardship cuts on penalties, prepayment advance, autopay relief, hardship uplift and the older-balance surcharge are removed; remaining tiers are keyed district schedules, proration conventions, CCS family share and NSLP meal status.
- C-COUNT: each policy now meets its drawn factor count with at least one method and two or more parameters, and each task has a multi-source and a cross-difficulty factor.
- O1: every baseline sentence is labelled standard and no rule restates a retired clause.
- O2: the tool with the ordering word in its docstring is retired; no new tool docstring ties its write to another problem's write (only "then shows in the billing history" describes the effect, and "first payment/installment" names the amount quoted).
- O3: the meal-application status-dating policy is retired, so no cross-product dating divergence remains.
- O4: base unchanged (frozen); seeds keep end_date equal to the requested last day, and no factor reads the age of end_date.
- O5: the repeat addition counts late payment fees already posted on a single-year enrollment before the month's own fee posts, as its sentence states.
- O6: the padded ladders (tenure notice, proportional unpaid scale, three block sizes) are removed.
- O7: the service-date ordering framing clause is replaced by a pricing scope on the most recent chargeable pickup with the posting-order norm stated as policy.
- O8: autopay relief is removed.
- O-0a: task 0 skip figures are recomputed by replay with the skipped step removed.
- O-0b: the persona's paid-ahead acceptance line is removed; she asks only for the plan.
- O-0c: the pending fees are recent postings awaiting the desk (state_due), recorded as such in the dossier.
- O-1a: the returned draft now posts before the due day, so the 2025-26 late fee posts one day after the due day as the base requires.
- O-1b: end_date stays the requested last day and nothing reads its age.
- O-1c: the day-0 notice convention is kept and stated in the rule's counting sentence.
REWORK round 2: gates 7/7 green

## Round 3 rebuild notes
- Task 0 (frozen_time 2026-11-12 10:30:00 CST): late payment fee and booked-day fee schedules rebuilt; world gains Chidi's sister Amara (second Creek Kids Club holding, sibling position 1) and moves to 2026-11-12 so every pending fee is a recent posting; the household ledger is read by household.
- Task 1 (frozen_time 2026-08-04 11:20:00 CDT): notice credit and installment rules revised (tier record tests, combination sentences); world unchanged.
- Per-task manual gates re-walked on both worlds (edges engaged, unmet, satisfiable, load-bearing by skip replay; reordered fee postings give identical values; every factor moves its scored value; baselines are the computation documents' standard values; decoy and absent-record probes listed in each dossier).
- Sweeps: verbatim quotes 0 misses; forbidden task_tools substrings none; no factor id inside a tool name; no figure within 1e-6 of a half cent; traceability pre-render shows only the unlock tool-name misses; validate_scenario shows only the not-yet-rendered required documents. No R6 factor is used.

## REWORK round 3 claims
- C-OVR-3: the late payment fee schedule no longer measures an unpaid part; whether a month owes a fee stays with the in-force base sentence (oldest-first allocation, remittances, credits, returned payments never paid), restated in the scoped overwrite, and the schedule sets only the amount; the waiting edge sentence and condition use the same base test.
- C-A1: the base late fee is now defined by the baseline sentence and every factor binding reads only records; assembly (form amount, rate charged, counts, shares) sits in plain bindings over baseline-defined quantities.
- C-A2: every combination sentence in all six policies is stated once and by kind of part only (parts that set an amount, add a fixed amount, set a share, set or limit or add or take away a count, set a date), naming no factor quantity.
- C-A6: the booked-day value selection is retired into the standard sentence (base day-type pricing); the new method (flat free rate / larger of free rate and a share of the day rate / day rate) and the late-fee form (larger of base fee and a percentage / percentage / base fee) differ by an input or an operation in every pair; the late pickup minimum block no longer coincides with quarter-hour rounding.
- C-A9-2: the whole-week proration tier, its rule sentence and compute now test the same records (district record with no withdrawal on or before the requested last day; enrollment withdrawn, no suspension date, a withdrawal notice on file).
- C-REAL: the posting-delay stage addition and the frequent-booking discount are removed, not reworded; replacements are R1 keyed schedules (plan, sibling position recorded on the charge, tuition rate basis recorded on the charge) and an R1 percentage-or-flat late fee form.
- C-COUNT: the late payment fee and booked-day fee schedules each carry four honest factors with one method and at least two parameters; no R6 factor is used anywhere.
- R2-O1: the order framings remain normative posting rules of the policy, each matching the record selection its compute uses.
- R2-O2: closed with the 10-minute minimum block.
- R2-O3: the notice-on-file guard is now stated in the notice-length sentence and tiers.
- R2-O4: kept as a parameter; its tiers are one remittance input, so relabelling it a method would fail A6.
- R2-O5: kept; residence is an accepted R1 key on an R5 installment limit.
- R2-O6: the Q2/Q3 combination sentences now name parts by kind only.
- O4: base-internal and inert; nothing reads end_date.
REWORK round 3: gates 7/7 green

## Round 4 rebuild notes
- Late payment fee schedule: sibling_late_fee_share removed; returned_payment_late_addition added (R6, below). Assembly sentence now reads base-fee/charge parts first, fixed additions next, one rounding.
- Task 0 world: seeded September and October late fees and the two payments that cleared them repriced under the revised schedule; Amara stays as a decoy holding; every other row unchanged. Task 1 untouched.
- Sweeps: verbatim quotes 0 misses; forbidden task_tools substrings none; no factor id inside a tool name; no figure within 1e-6 of a half cent; stale-figure sweep over both task files clean (the only "sibling share" mention is the dossier's history line); traceability pre-render shows only the unlock tool-name misses; validate_scenario shows only the not-yet-rendered required documents.

## REWORK round 4 claims
- C-REAL: sibling_late_fee_share is removed, not reworded; no factor of the late payment fee reads the sibling position, so the sibling dimension stays only in the tuition charge; no other factor of any policy is X1-X4.
- C-COUNT: the late payment fee schedule is back to four factors (plan base fee, fee form method, repeat late months, returned-payment addition) with one method and three parameters; all other policies keep their counts.
- R6 returned_payment_late_addition: record key = the enrollment's care_returned_payment rows in the 12 months before the fee posts (a recorded status); figures 5.00 / 10.00; contradicts no base clause (the base returned-payment fee and certified-funds rule stay in force); not a named X1 mechanism; reads only records, stacks on no dimension another factor of this computation uses, nothing already in a recorded amount; minimal (one slot). No R1-R5 factor could take it: meal status would be a hardship cut on a penalty, sibling position stacks with the tuition sibling discount, days past due would key on the desk's posting time, caps mask the other factors on this world, and plan, charge size/form and repeat months are already used.
- R3-O1: kept as observed; the owe-test stays with the base sentence the rule restates and with the waiting edge, and the computation prices only the amount.
- R3-O2: kept; a one-day desk lag, and the amount does not depend on the posting date.
- R2-O1, R2-O4, R2-O5, O4: unchanged and accepted.
- Task 1 and every item closed in revision_3 (C-OVR-3, C-A1, C-A2, C-A6, C-A9-2, C-OVR, C-PRE, C-SCOPE, A8, B-class) are unchanged and re-verified by the gate block.
REWORK round 4: gates 7/7 green

## Round 5 notes (renderer scan-first findings, render_r1.md)
- Edits limited to rule/ladder text and request selection; both task worlds and every scored value are unchanged. Probe runs: a later cancelled booking is skipped (the pending booking is still priced); a world with only declined bookings prices nothing.
- Sweeps: verbatim quotes 0 misses; no figure within 1e-6 of a half cent; traceability pre-render shows only the unlock tool-name misses; validate_scenario shows only the not-yet-rendered required documents.

## REWORK round 5 claims
- F1: verified (compute's fall-through also prices a student with no enrolled district record); the late pickup rate sentence and the booked-day grade sentence now name that case with the 01-05 tier, in rule, quotes and ladder text.
- F2: verified (a CCS enrollment with no remittance ever posted got the whole charge in compute but no stated base); the credit-base sentence and its second tier now state the whole charge for that case.
- O1: kept as a stated scope test, because the policy prices only 2026-27 enrollments ("and only of such an enrollment") and the other-year sentences restate the base fees the base day-fee policy still charges; pricing every other year in compute would widen the out-of-scope surface C4 asks to keep small.
- O2: closed as a B2 decoy item; the booked-day policy, the notice credit and the payment plan's booked-day prerequisite sentence and condition now select only received or completed requests (later receipt wins, the received one on an exact tie), and the notice-on-file counts use the same status filter.
- Policy-audit items closed through revision_4 (C-REAL, C-COUNT, R6 returned-payment addition, C-OVR-3, C-A1, C-A2, C-A6, C-A9-2 and earlier) are unchanged; every combination sentence keeps its order.
REWORK round 5: gates 7/7 green

## Round 6 notes (KB audit, policy_kb/extended_day_care_billing revision_1)
- Edits limited to the look-back sentences, quotes and ladder tiers of three policies; compute already counts exactly the stated window (COUNT within_months over the returned rows' posted_date), so no compute line changed. Boundary probes on the task 0 world: a return posted on the same day a year back is not counted, the next day is, the posting day itself is, a later day is not.
- Scored figures, baselines and sensitivities of both tasks are unchanged (task 0: four computations; task 1: two), as are both worlds. The base certified-funds measure text is untouched (base prefix unchanged; blueprint untouched).

## REWORK round 6 claims
- SRC-1: verified; the three look-back sentences said "before the day ..., counted back to the same day of the month" while compute counts the end day and excludes the start day; returned_payment_late_addition, plan_returned_payment_rule and arrangement_returned_payment_term now state both ends in rule, quotes and ladder text (a return counts when it posted after the same day of the month twelve months earlier, the last day of that month when it has no such day, and on or before the day the fee posts or the day of the payment), which is what the existing compute counts.
- O-1, O-2, O-3: KB-side observations for the renderer; no source change needed (the apposition, the hypothetical warning date and the 45/46 boundary row stay as source states them).
- O-4: verified and left; the booking gates (active status, holiday camp access, drop-in allowance) stay with the in-force base day-fee eligibility the agent applies before posting, and the repeat count's "earlier billing months" equals all late-fee rows whenever a month's fee is priced before it posts, which every priced world of the suite satisfies.
- R6 returned_payment_late_addition: unchanged in key and figures; only its window wording is now exact.
- All policy-audit and renderer items closed through earlier rounds stay closed; every combination sentence keeps its order.
REWORK round 6: gates 7/7 green

## Round 7 notes (seed-only; KB re-audit revision_2, SRC-2)
- care.extended.yaml and task_tools.py are byte-identical (sha256 prefixes 8e283b9ed3a5e94d and 38804948550844e6). Only task 1's transfer request, its 2026-27 enrollment registration date, the persona's move timing and the dossier seed note changed; task 0 is untouched.
- Exhaustive other-category pass (both worlds), each row against docs/<product> as of its posting date:
  - T1 transfer request: re-seeded (see SRC-2).
  - T1 2026-27 Non-Resident Transfer record: type admits a household profile with no in-district residence and an approved non-resident request; Cypress Hollow is not closed to the type; no residency proof required (verified date empty); returning student, so enrolled on verification; registration inside the 10-day acceptance period; effective on the first day.
  - T1 2025-26 Attendance Zone record: zoned campus, residency verified within 30 days of registration, completed at the close of the year with the last instructional day and no leaver reason.
  - T1 meal account and 2025-26 application: determined within 10 operating days; Free (Household Application) in 2025-26, Prior-Year Carryover from 2026-07-01, inside the carryover period on the frozen date; reaches the named student only.
  - T0 records for Chidi (2025-26 PK4 State-Eligible: age, in-district, free-or-reduced basis, residency in 30 days, completed; 2026-27 KG Attendance Zone: zoned, residency re-verified) and Amara (2026-27 grade 04 Attendance Zone): consistent with age, zone, residency and close-of-year rules.
  - T0 meal accounts and 2026-27 application: household-income application determined within 10 operating days, reduced from its determination date, reaching both children (household reach); verification sample not selected.
  - No transport, activity, device or music rows are seeded in either world.
- Scored figures, baselines and sensitivities are unchanged in both tasks; the residence term keeps its Non-Resident Transfer tier.

## REWORK round 7 claims
- SRC-2: verified (a 2026-05-04 request is outside the Non-Resident Transfer window and its 2026-06-18 decision is after the decision day); the request is re-seeded as filed 2026-01-20 inside the window, approved 2026-04-14 by the decision day, accepted within the acceptance period by the 2026-27 registration of 2026-04-20, with the family's move to outside the district dated January 2026 in the persona and dossier, so the record and the enrollment resting on it are what the enroll rules produce.
- Exhaustive cross-product seed pass: every meals and enroll row of both worlds checked against its owning product's published docs; no other member found; no transport, activity, device or music rows are seeded.
- Charter and tools unchanged (byte-identical), so every policy-audit, renderer and KB item closed through round 6 stays closed.
REWORK round 7: gates 7/7 green
