# worklog — referral_and_authorization_management (M=2)

## Step 0 draw (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1, factor_counts=[6, 6]
- task 1: prerequisite_problems=2, factor_counts=[4, 5, 4]

## Scope plan (asset ledger)
Numeric landing fields of the referral line are units (grant rows, units_remaining), validity dates
(valid_through) and the stated figure of a patient-signed request record. Patient-own writes the
difficulty sanctions: the appeal consent (no numeric field; a denied referral admits no other write, so
no tree can hold it) and the out-of-network cost-share acknowledgement; the base also lets a patient
move an open referral to another provider/site. Design:
- task 0 (imaging): root = extend_study_authorization_f1ccb059 (agent, added validity days, 6 factors)
  <- confirm_imaging_site_change_a21d40f9 (user, pre-service estimate at the named site, 6 factors)
- task 1 (out-of-network continuation): root = grant_extension_visits_d2c34b29 (agent, visits, 5 f)
  <- sign_oon_cost_share_acknowledgement_95eb7797 (user, per-visit cost share, 4 f)
  <- lengthen_referral_validity_fab859e3 (agent, added validity days of a visit extension, 4 f)
Known compromise: the two user writes record their stated USD figure in the signed request record's
reference and receipt (referral_requests has no amount column).

## Task 0 (closed, per-task gates)
- policies referral_ext_study_site_estimate (6 f) and referral_ext_study_validity (6 f) appended to referral.extended.yaml
- verification (check_compute evaluator on handling-time world): estimate 285.0 (factor baselines 260/110/110/360/185/325, all 25);
  extension 50 on the opening world, 33 after the site change (factor baselines 50/26/29/27/27/32, all 30)
- revision: task_tools helper `_shift` was counted as a tool by check_extended -> inlined the date arithmetic
- revision: empty FK strings in appointments/appointment_events/billing_transactions flagged dangling by replay -> seeded as null
- gates --task 0: TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK;
  check_extended red only on the three task-1 tools not yet named by a policy (closed with task 1)

## Task 1 (closed)
- policies referral_ext_oon_visit_share (4 f), referral_ext_visit_validity (4 f), referral_ext_extension_visits (5 f)
- verification: share 198.75 (baselines 168.75/60/60/245, all 30); lengthening 65 (40/87/61/64, all 60);
  visits 4 (3/3/2/5/5, all 2); 0 without the acknowledgement, 2 without the lengthening; both parallel orders same hash
- revision: check_compute flagged referral_ext_visit_validity history as not load-bearing (LATEST is not zeroed by
  the floor test) -> course span now rests on a COUNT of unit uses in the two months before the handling date
- revision: suite history_rows_max was 7 (< 8) -> the two-month window above lifts it to 10

## Final gate block (no --task)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (branches mean 48.50, steps mean 13.50,
history_rows_max 10, branches_max 49) / GROUNDING OK / CACHE-DIFF INFO / SCOPE OK. check_traceability deferred until the
KB is published.

## Round 2 — policy-task audit r1 (audits/policy_task/referral_and_authorization_management)
- F-1: referral_ext_extension_visits.overwrite now also names referral_unit_accounting ("... an extension grants
  extension_units (none where that is 0) ...") and, for O-13, "Units are granted only when the referral status is approved."
- F-2: acknowledgement rule's "Before an Out-of-Network Referral is extended" sentence rewritten without order.
- F-3: weekend_roll / course_roll relabelled parameter (2 / 1 / 0 days, stated in the rules).
- F-4: site-estimate copay ladder now by financial class; baseline = specialist copay; task 0 account -> High-Deductible
  Health Plan Account, ledger line -> deductible charge; estimate 285.00 -> 340.00 (factor baselines 390/60/60/460/240/380, all 50).
- task-1 finding 2(b): coverage_verified_date 2026-06-26 (exactly 90 days, boundary near miss for course_recheck and
  share_collection_rate); internal course allowance 2; deductible charge 184.00; share 198.75 -> 129.00; 65 and 4 unchanged.
- task-1 finding 3: closure edge conditions copied from the charter.
- O-1 active span = extension_validity_days + 24; O-2 numbers stated, keys renamed, ladder values in words; O-3 open-course
  tier "approved and still has units"; O-4 lengthen docstring; O-6 edge effect; O-11 waived fees count; O-T0-1/O-T1-1
  no_user_hint quotes the conditional line. Base section still byte-identical to blueprint/products/referral.yaml.
- Final gate block green again (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK).

## Round 3 — runtime lint (erlbench/validate.py _FORBIDDEN_TOKENS)
- task_tools.py: removed `from datetime import date, timedelta`; the two date shifts (extend_study_authorization,
  lengthen_referral_validity) now use an integer-only proleptic Gregorian helper (`_Calendar.shift`, a class so the gates do not
  count it as a tool). Checked against datetime on 200,000 random dates/offsets: 0 mismatches. Gold replay with the old and new
  tools: identical DB hashes and identical receipts for both tasks. Charter and task JSON content unchanged.
- Gates: replay --check REPLAY OK, then the full block green; LINT OK.
