# worklog — coverage_reviews_prior_auth_step_therapy (category review, M=2)

draw_counts.py --tasks 2:
- task 0: prerequisite_problems=1, factor_counts=[5, 4]
- task 1: prerequisite_problems=3, factor_counts=[6, 6, 4, 4]

Difficulty-level pre-check: base review product closes (cases, authorizations); the only numeric write
fields of this category are review_cases.requested_quantity_per_30 and
review_authorizations.approved_quantity_per_30, so every scored computation is a quantity per rolling
30 days on a quantity limit exception. Owner=user writes available: a member-filed request (base
review_evt_case_intake: member_initiated_review_allowed) — task 0 uses the first-time request, task 1
the renewal request.

Plan (scope budget):
- task 0: member-filed first-time QL request (user, 4 factors) -> QL exception approval (agent, root, 5 factors).
- task 1: continuity-of-care QL authorization (agent), member-filed renewal request (user),
  renewal approval (agent, root), appeal-overturn effectuation (agent).

## task 0 — closed
- policies: review_ext_member_request_quantity (user tool file_coverage_review_request_fd0cbfbe, 4 factors),
  review_ext_exception_approved_quantity (agent tool approve_quantity_exception_611b3a5d, 5 factors, root).
- revisions: retail dose-change/replacement override factors dropped (they contradict rolling 30-day quantity
  limit mechanics: an early refill above the limit would reject) -> replaced by lapsed-approval and cash-paper-claim
  factors. Sponsor profile and accumulator ledger rows dropped from the seed (outside the replay closure).
  retail_carryover_on_move relabelled cross_difficulty mail; direction_change_allowance cross_difficulty null.
- gates --task 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

## task 1 — design (draw: prerequisite_problems=3, factor_counts=[6, 6, 4, 4])
Root: renewal approval (6). Prereqs: member-filed renewal request (user, 4) <- continuity-of-care authorization (4);
appeal-overturn authorization on another acute migraine drug (6). Edges: root->request (value_input, state form,
affirmative), request->continuity (value_input, state form, negated), root->overturn (value_input, state form, affirmative).
World: new member (program effective 2026-08-10, Northbridge Clinical Standard), prior carrier letter for sumatriptan
50 mg x18 on a member-opened case wrongly pended and denied; Ubrelvy quantity case denied, appeal overturned 2026-10-05.

## task 1 — closed
- policies: review_ext_continuity_quantity (grant_continuity_authorization_38eb93b7, 4), review_ext_overturn_quantity
  (grant_overturn_authorization_6da113c2, 6), review_ext_renewal_request_quantity (file_renewal_request_18124eb7, user, 4),
  review_ext_renewal_approved_quantity (approve_quantity_renewal_696a9005, root, 6). Gold values 16 / 28 / 19.5 / 14.
- gates --task 1: REPLAY OK, COMPUTE OK, EXTENDED OK, SOLVABILITY OK, GROUNDING OK, SCOPE OK.

## difficulty closing
- coverage: 6 extended policies, task 0 claims 2, task 1 claims 4, pairwise disjoint; 6 task tools, each named by one policy.
- final run (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (suite means
  branches=66.50, steps=19.00; history_rows_max=20, branches_max=88), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
- check_traceability not run (needs the published KB).
- authoring helpers deleted.

## round 2 — policy-task audit rework
- F-1: renewal approval `other_drug` is 'none' for a Nurtec ODT renewal; rule's other-drug sentence says so.
- F-2: overturn prerequisite sentence narrowed to "the other acute migraine drug" (= condition = compute);
  overturn rule now covers sumatriptan too (triptan step limited to gepant overturns), so no hop is unresolvable.
- F-3: current_strength_count relabelled parameter (decides strength_ratio); home_delivery_move_allowance became
  the honest method (prorated running retail fill / whole fill within 7 days / nothing). Task 1 world: latest
  sumatriptan fill 2026-09-11 -> 2026-09-21. Values: continuity 16 -> 16.2, renewal request 19.5 -> 19.725
  (case rvc_064f224b2eea), renewal approval 14 unchanged.
- F-4: all five multiple ladders = whole package maximum / 7/8 of it / 3/4 of it (params partial_share, default_share,
  cap_share_*); Standard-package values unchanged, so task 0 figures unchanged.
- O-2 ("for the drug") and O-8 (one unit per opioid day) wording; personas read the label's strength line;
  task 1 close bound to "the request you filed" being approved; renewal_growth_multiple described as single-record.
- Final gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK. Helpers deleted.
