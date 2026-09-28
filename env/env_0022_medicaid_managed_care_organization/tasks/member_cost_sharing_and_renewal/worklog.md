# worklog — member_cost_sharing_and_renewal (category plan)

## Step 0 — difficulty pre-check
- Read references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/plan.yaml,
  db_schema.json, share_tools.py (verify threshold K=2; finder find_customers).
- Numeric fields writable through the claimed events: plan_claims.member_cost_share (plan_claim_adjusted,
  plan_cost_share_refund), plan_premiums.amount + plan_memberships.premium_balance (plan_premium_paid).
  plan_premium_waived is avoided: its base gate hardship_statement is caller_statement over
  (membership_id, coverage_month), which would force an internal membership uuid into the persona.
  Notices / ID cards / preference / reinstate carry no numeric field, so no computed problem can land there.
- The only owner=user business write in this line is the family paying its own CHIP premium, so both
  tasks are CHIP Kids families (the only category with a premium ladder).
- CHIP children hold PrairieRx Children (all pharmacy copays 0.00), so pharmacy copays never move a cap
  total here; cross-difficulty evidence comes from auth (approved authorizations) and pcp (assignment /
  visit records).
- Draw (scripts/draw_counts.py --tasks 2):
  task 0: prerequisite_problems=3, factor_counts=[6, 6, 6, 4]
  task 1: prerequisite_problems=2, factor_counts=[5, 5, 6]
- Claim adjustments per one claim cannot carry 4-6 load-bearing factors (a whole reversal is a copy of the
  booked copay), so every claims-side problem is a batch re-rating over a class of paid claims in the
  counting window, booked as one adjustment entry that names the latest claim of the class (declared
  overwrite of the one-claim grain sentence of plan_evt_claim_adjustment).

## Space budget (7 policies, 7 tools)
- task 0 (open CHIP membership): root over-cap refund <- family pays premium arrears (user)
  <- own-PCP visit re-rating batch <- well-child visit re-rating batch.
- task 1 (CHIP membership ended for premium non-payment, lockout running): root family pays the lockout
  balance (user) <- therapy course re-rating batch <- ambulance transport re-rating batch (revised from an
  earlier pre-coverage / true-emergency plan: those classes admit no load-bearing factor ladders).
- Tool uuids generated one per tool: b068d625 fdc43b6b ea94b99c 0e97c2c0 44198c5a 7ffa3e71 8b982fa6.

## Task 0 — closed
- Customer Zuri Halvorsen-Mbeki (CHIP Kids, open membership, coverage 2025-11-01), frozen 2026-07-28 11:05 CDT.
- Tree: root plan_ext_over_cap_refund (6 factors) <- plan_ext_past_due_premium_payment (user, 6)
  <- plan_ext_own_pcp_visit_rerating (4) <- plan_ext_office_visit_preventive_rerating (6); all edges state form,
  value_input; fan-out; commute verified (reverse replay gives a byte-identical terminal DB).
- Handling-time values: re-ratings 36.00 and 29.00, payment 13.75, refund 265.98; skip sensitivity 301.98 / 294.98 / 217.23.
- Revisions: K1 scope baseline equalled result -> added 2025-12-16 previous-provider visit; P2 care reward decorative
  under max-stacking -> averaging tier; replay flagged 5 unread seed rows -> claims read by customer, rx coverage read,
  card notices dropped; payment tool settles the billed month so the zero-balance state is reachable.
- Gates --task 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Occupied after task 0: the four policies above and tools b068d625, fdc43b6b, ea94b99c, 0e97c2c0.

## Task 1 — closed
- Customer Anouk Brevard-Oyelowo (CHIP Kids, ended 2026-04-30 for premium non-payment at renewal; lockout to
  2026-07-29), frozen 2026-06-30 11:40 CDT. Draw: prerequisite_problems=2, factor_counts=[5,5,6].
- Tree: root plan_ext_lockout_balance_payment (user, 5) <- plan_ext_therapy_course_rerating (6)
  <- plan_ext_ambulance_transport_rerating (5); both edges state form, value_input (gate credit_offset); commute verified.
- Handling-time values: course re-rating 73.50, ambulance re-rating 28.50, payment 98.00; skip sensitivity 171.50 / 126.50.
- Cross-world check: in world 1 the task-0 state-due policies evaluate to 0.00; in world 0 the task-1 re-ratings evaluate to 0.00.
- Revisions: review date moved to a month end (course scope was decorative with a day-23 review); unread pharmacy rows
  dropped; PCP / therapy-authorization month bindings guarded so a missing record yields 0.00 instead of an error.

## Difficulty-level gates (final run, no --task)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (branches mean 102.5, steps mean 19.0,
  history_rows_max 58, branches_max 117); GROUNDING OK; SCOPE OK; CACHE-DIFF INFO (optional).
- check_traceability NOT run: the KB documents are not yet published (it reads the published KB).
- Coverage: 7 extended policies, each claimed by exactly one task; 7 task tools, pairwise disjoint across tasks.

## Round 2 — rework against audits/policy_task/member_cost_sharing_and_renewal/{_difficulty,0,1}.md
Plan (item -> change):
- F1 (RED): each re-rating policy declares an overwrite of plan_evt_copay's schedule sentence; no tier ever leaves a
  copay on preventive care (office re-rating: telehealth well-child tier and vaccine "immunization visit" tier and the
  well-child schedule fall-through removed/replaced by non-preventive fold-in rules).
- F2 (RED, task 0): every rule states "rounded half up to the cent"; every RND gets a half-up guard; task 0 recomputed.
- F4 (RED, task 1): void-bill and credit-offset ladders redesigned so every tier is reachable by a lockout payer and
  no conjunct restates the policy's scope.
- 1.md seed RED: auth row expired after its end date, care episode closed at membership end; therapy/ambulance/lockout
  conditions re-keyed to records valid for an ended membership.
- Observations: F3 window wording made rolling; F5 continuous-eligibility anchor; F7 tele/IHA scoped to the current
  assignment log; F9 carry-over sentence declared; F10 health-home copay distinct; F6/F8/F11 recorded.
Round 2 — closed items:
- F1: own-PCP, office, therapy and ambulance re-ratings each declare plan_evt_copay's schedule sentence superseded by a
  sentence of their own rule; the office re-rating returns every logged well-child visit in full and its factors act only
  on non-preventive visits (telehealth sick, same-day sick, vaccine-day sick, medication check, coordinated follow-up);
  task-0 world updated (telehealth visit is a sick visit; superseded-log telehealth sick visit; refill-day visit added).
- F2: all rules "rounded half up to the cent"; every RND carries half_up_guard; the task-0 cap tie resolves identically
  on both faces; task-0 expected values recomputed at handling time.
- F4: lockout void-bill ladder keyed on when the post-termination bill posted; credit-offset ladder keyed on which
  credits were booked; no conjunct restates the scope; every tier reachable.
- 1.md seed RED: therapy authorization expired (closed_date day after end, units released); care episode closed at
  membership end (membership_ended); therapy/ambulance/lockout conditions read an authorization approved on a request in
  the window (approved or since expired) and an episode enrolled in the window; therapy intake fall-through is a
  carried-over/retro course and never exceeds the course.
- F3 window wording, F5 continuous-eligibility anchor (plan_continuous_eligibility added to lineage), F6 reward-credit
  sentence, F7 current-assignment scoping, F9 carry-over sentence declared, F10 health-home copay 0.50.
- Recorded only: F8 (paid-less-balance tier), F11 (review-reach method label), adjust-once observation, persona
  conditional-line observation.
- Final gate block: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK;
  CACHE-DIFF INFO; SCOPE OK; check_traceability not run (KB not yet published).
