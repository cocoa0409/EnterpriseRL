# worklog — primary_care_assignment (category pcp), M=2

## Step 0 — difficulty pre-check (2026-09-24)
- Read references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml (difficulty summary/claim), products/pcp.yaml, db_schema.json, share_tools.py.
- Draw (scripts/draw_counts.py --tasks 2):
  - task 0: prerequisite_problems=2, factor_counts=[4, 6, 4]
  - task 1: prerequisite_problems=1, factor_counts=[6, 4]
  - => 5 extended policies, 5 task tools, 24 declared factors in total.
- Numeric-write audit of the pcp category (the scored parameter of every problem must be a machine-recomputable number;
  the compute DSL has no date constructor, so a computed date cannot be a gold argument):
  - claimed events pcp_assign / pcp_end / pcp_change_log / pcp_location_update carry only one numeric field,
    pcp_assignments.distance_miles (a geocoded straight-line distance no policy computes from records);
    their other written values are dates, enums, NPIs and names.
  - the only policy-computable numeric in the category is pcp_events.referral_visits on pcp_referral_issue
    (base pcp_referrals: "covers up to referral_max_visits, or standing_referral_max_visits for a standing referral").
  - DECISION: every problem of both trees is a referral-sizing write (pcp_referral_issue, referral_visits), set in the
    difficulty's PCP-assignment situations (a PCP leaving the network, a PCP change that left referrals on an earlier
    assignment). pcp_referral_issue is a declared pcp event claimed by no other difficulty, so no cross-difficulty overlap.
    Deviation from the claimed event list is recorded here for the coordinator; the blueprint is untouched.
- Base automatic clauses to respect: pcp_activate (system, effective date), pcp_end by system on supersession/exit/dismissal,
  auto-assignment after the choice period, age-out reassignment. Seeds keep every open assignment consistent (one active,
  no pending) so none of them fires an obligation the task set cannot carry.
- Governing base policy of pcp_referral_issue: pcp_referrals only (eligibility referral_from_active_pcp: the assignment the
  referral is written on must be active).
- Tool uuids (generated one per tool with uuid.uuid4().hex[:8]): carry_over_referral_de0684af,
  issue_standing_referral_d300bbad, elect_continuity_of_care_ec21b6d4 (task 0); issue_specialist_referral_96d4855f,
  request_second_opinion_76735634 (reserved for task 1, written only when task 1 is built).

## Scope plan (principle C)
- task 0 (3 problems): root = member's own continuity-of-care election with the exiting PCP (user);
  prereq chain: continuity <- standing referral (agent) <- carry-over of an unexpired referral from an earlier assignment (agent).
- task 1 (2 problems): root = member's own second-opinion referral (user); prereq: single specialist referral to the
  treating specialist on the current assignment (agent).
- Disjoint: five policies, five tools; task 1 keeps the single-referral and second-opinion space entirely unoccupied by task 0.

## Task 0 — build log
- Step 1: policies written to pcp.extended.yaml: pcp_ext_referral_carryover (4 factors), pcp_ext_standing_referral (6),
  pcp_ext_continuity_of_care (4, root). Draw [4,6,4] matched (multiset).
- Step 2: task_tools.py: carry_over_referral_de0684af (agent), issue_standing_referral_d300bbad (agent),
  elect_continuity_of_care_ec21b6d4 (user). check_task_tools: TASK TOOL CONTRACT OK.
- Step 3: tasks/0.json initial_state seeded (Ingrid Solvang-Mercado; phone 4025550417, medicaid PR53718264, ssn 5824).
- Step 5 handling-time recomputation (scratch harness = check_compute.build_env/eval_compute):
  - carry-over on earlier assignment: recorded 6, used (middle window, 6m) 4, left 2, bridge 1, relationship 1, travel 1 -> 5
    factor baselines: used window->3, bridge->4, relationship->4, travel->4; all-baseline 0.
  - standing (after carry-over): allowance 24 + monitoring 4 + post-hospital 2 + travel 4 + lab 2 = 36; x 6/12 = 18; cap 24 -> 18;
    less carried 5 -> 13. baselines: allowance->7, monitoring->11, alignment->19, post-hospital->12, travel->11, lab->12; all 7.
    skip carry-over -> 18 (edge load-bearing).
  - continuity (after standing): window 120, rate 3 -> ceil(360/90)=4; co-management -2; ER +1 -> 3. baselines: window->2,
    rate->2, co-management->5, ER->2; all 2. skip standing -> 4 (edge load-bearing).
- Revisions: helpers inlined in task_tools.py (check_extended read them as tools); reads restructured (rx coverage->fills,
  ride benefit->trips, visits by customer) so the replay closure equals initial_state; continuity extended window 120->135
  (param search: cross-off and history-zero recomputations previously coincided with gold 3). Continuity gold now 4
  (baselines 2/2/6/3, all 2; skip standing 5; cross-off 3; history-zero 3).
- Task 0 per-task gates (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Manual values gates (task 0): length = chain of 2 hops, breadth = plan/rx/ride/auth + own history; user tool = the member's own
  continuity election (her decision, completed on the spot); persona names no prerequisite and closes after the election;
  base eligibility (active assignment) holds pre-write for all three writes; no real-world wait anywhere.

## Task 1 — build log
- Occupied by task 0: carry-over, standing, continuity policies and their three tools. Claimed now: pcp_ext_specialist_referral
  (single referral sizing, agent, 6 factors) and pcp_ext_second_opinion (member's own second-opinion referral, user, 4 factors,
  root). Draw --task 1: prerequisite_problems=1, factor_counts=[6,4] -> single 6, second opinion 4. No headroom left after task 1
  (M=2): all five policies covered.
- Story: Desmond Achterberg-Nwosu (Expansion Adult, PCMH since 2026-02-01) wants a second opinion before the knee replacement his
  orthopedic surgeon requested (surgical authorization submitted 2026-09-10); the surgeon's only referral came from the previous
  Standard PCP and expired 2025-11-29, so the current assignment carries no referral to him.
- Step 5 recomputation: single referral 8 (baselines 5/7/7/7/7/12, all 4); second opinion 7 (5/6/5/6, all 1; skip referral 5).
- Seed: Desmond Achterberg-Nwosu; phone 4025550862, medicaid PR58204613, ssn 5391. pcp_visits dropped (unread by any factor).
- Task 1 per-task gates (--task 1): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Manual values gates (task 1): single hop, value-bearing; breadth plan/auth/rx/ride; user tool = the member's own second-opinion
  request (his right and his choice of specialist, completed on the spot); persona names no prerequisite; no real-world wait.

## Difficulty closing (2026-09-24)
- Final gates (no --task): EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (suite means
  branches 49.00, steps 16.50; history_rows_max 9; branches_max 54) / GROUNDING OK / CACHE-DIFF INFO (optional) / SCOPE OK.
- check_traceability NOT RUN: the KB documents are not published yet (run after erl-kb-doc-render).
- Coverage: 5 extended policies, each claimed by exactly one task (task 0: carry-over, standing, continuity; task 1: single
  referral, second opinion); 5 task tools, disjoint; every task calls one owner=user tool.
- Prerequisite sentence directions across the charter: continuity (negated, "not fixed until"), standing (affirmative,
  "fixed only after"), second opinion (affirmative, "recorded only after").
- Open note for the coordinator: all five problems are referral-sizing writes (pcp_referral_issue), not the claimed
  pcp_assign/pcp_end/pcp_change_log/pcp_location_update events, because those carry no policy-computable number.

## Rework round 2 (policy-task audit round 1: task 0 RED G-1/G-2, task 1 PASS)
- G-1 (undeclared override): pcp_ext_continuity_of_care base_policy_refs += pcp_provider_exit; overwrite declares
  superseded_clause "A member in active treatment may keep seeing the exiting provider for continuity_of_care_days after the
  exit date" -> replaced_by the window-ladder sentence (now opening with "in place of a fixed continuity-of-care period").
  Task 0 dossier section 5 corrected.
- G-2 (mislabelled method): used_visit_window relabelled parameter (ladder values = look-back lengths); specialist_travel
  becomes the method factor (>=4 legs -> legs // 2; 1-3 -> flat 1; none -> 0; param travel_two replaced by legs_per_visit).
  Carry-over still 4 factors (3 parameter, 1 method).
- Observations closed cheaply: O-G3 (referral_type single filter on carry-over LATEST + rule "most recent single referral"),
  O-G7 (docstrings), O-G9/O-G10 (trailing whole-month window sentence in all five rules), O-G11 (RND guard in standing),
  O-G15 (active-treatment definition in continuity).
- Left as observations: O-G4, O-G5, O-G8, O-G12, O-G13, O-G14, O-T1-1 (no consequence on either world); O-G6 is
  scenario-level (claimed events carry no policy-computable number; blueprint frozen).
- Recomputation after edits: every expected / factor baseline / whole baseline identical to round 1 on both worlds.

## Rework round 3 (policy-task audit revision_2: task 0 RED G-3, task 1 PASS; G-1/G-2 closed)
- G-3: continuity's active-treatment definition widened from "a visit in the last half-year" to "a visit in the last year",
  with an explicit sentence that a member whose visits all predate the last half-year is still in active treatment; the
  trailing-period sentence now names the last year (twelve whole months). The continuity_rate ladder (cadence / maintenance /
  standard) is unchanged and all three tiers are reachable by eligible members; the baseline (standard rate) is the treatment
  of an eligible member with no visit in the last half-year.
- Recomputation: all expected / factor baselines / whole baselines unchanged on both worlds.
- O-R2-1, O-R2-2 left as observations (no consequence on either world); O-G6 unchanged (blueprint frozen).
