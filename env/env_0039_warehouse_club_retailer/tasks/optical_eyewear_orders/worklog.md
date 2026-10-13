# optical_eyewear_orders — instantiation worklog (M=2)

2026-10-05T20:37Z START (single thread). Read: references (3), blueprint.yaml, products/optical.yaml,
db_schema.json, share_tools.py, gate scripts. Base copied verbatim into optical.extended.yaml.

## Draw (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=2, factor_counts=[6, 4, 6]
- task 1: prerequisite_problems=3, factor_counts=[4, 4, 4, 5]

## Global constraints noted at Step 0
- optical_charge_posted triggers membership_reward_accrued when reward_eligible=true; optical_credit_posted
  triggers membership_reward_reversed when reward_eligible=true. Every task tool therefore fixes
  reward_eligible=False and only writes charges that never earn (remake charges) or credits against charges
  whose flag is false (jobs ordered under a non-Plus membership). Seeds keep both jobs on Club memberships.
- Credit-posting subjects inherit the dedup gate optical_vision_plan_billing.one_allowance_per_charge
  (action arg source_txn_id); charge-posting subjects inherit optical_agg_discount_stacking.one_discount_route
  (action arg optical_order_id). Root of task 0 uses subject [optical_charge_posted] only.
- Identifier band: phones 6145550500-6145550599, member numbers 1005xxxxxxxx.

## Space budget (7 extended policies, 7 tools)
- task 0 (root + 2): accidental-damage replacement charge (USER, 6 factors) <- remake overcharge waiver on an
  out-of-window prescription-change remake (agent, 6) and design switch-down difference credit (agent, 4).
- task 1 (root + 3): base-lens cancellation refund of an in-lab job (agent, 5) <- member's cancellation
  confirmation with frame return-to-stock refund (USER, 4), lens option refund (agent, 4), lens material
  refund (agent, 4).
Tools (uuid8 generated once each): post_switch_difference_credit_2fd39c69, waive_remake_overcharge_01693abf,
authorize_damage_replacement_0a7f54ae (user) | confirm_eyewear_cancellation_a25e55a5 (user),
refund_lens_option_d067b0d2, refund_lens_material_ad7f47c2, post_lens_cancellation_refund_d976b5a7.
- 2026-10-05T20:45:38 task0 policies written (switch credit 4f, late rx waiver 6f, accidental replacement 6f); task_tools T0 3 tools CONTRACT OK
- task0 seed + skeleton written (_build_t0_state.py / _build_t0.py, temporary). Handling-time recompute (_sens.py 0):
  switch credit 57.50 (gap 50.00 full x1.10 + 2.50 - 0); factor baselines 30.00/52.50/55.00/42.50, all-baseline 10.00
  late rx waiver 21.29 (late charge 38.70: 149.99x20% + 15.00, x0.75, +4.95); baselines 10.04/0.00/32.54/14.54/16.79/16.29, all 0.00
  accidental replacement 55.81 (321.49 x15% x0.95 + 10 + 0); baselines 71.08/86.35/71.08/58.22/45.81/70.81, all 111.45
- task0 revision: replay flagged dangling FKs (empty membership_card_id / item_price_id) and 7 unread rows ->
  dropped the membership fee + card issuance noise rows and the empty FK fields, read optical ledger by customer,
  added find_order_holdings (write steps moved 9/11/13 -> 10/12/14; NODES/TRACING/CONTRACT/CLOSURE/RATIONALE
  propagated). Rationale figures re-verified (opening-ledger replacement 46.00; sequential reductions 39.37/20.62).
- task0 per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK,
  REPLAY OK (closure 26 = initial 26). Prereq skip run: no switch credit -> 64.01, no waiver -> 40.54 (gold 55.81).
- task0 manual values gates: tree root=user write; both edges state-form, one affirmative ('fixed only after'),
  one negated ('not fixed until'); each waited-on state is booked by exactly one tool of the difficulty; persona
  names neither prerequisite; tools check nothing; all under one frozen_time; near-misses: stale order sale
  (2025-09-20), stale card statement (2025-09) + gas entry, 2024 single-vision job.
- task1 design (Step 0): customer Thaddeus Okonkwo-Lindqvist (Business Membership, Visa Business), job in_lab
  Northgate Premium Progressive Lenses, trivex, photochromic added 2026-09-27; root = lens cancellation refund
  (agent, 5f) <- member's cancellation confirmation + frame return refund (USER, 4f, state_gate on status),
  option cancellation refund (agent, 4f, value_input via lab retention pool), material cancellation refund
  (agent, 4f, value_input). Planned figures: frame 147.50, option 50.52, material 9.50, lens refund 81.95.
- 2026-10-05T21:00:17 task1 tools (4) CONTRACT OK; task1 policies written (frame return 4f, option refund 4f, material refund 4f, lens cancellation refund 5f)
- task1 seed/prose written; _sens.py 1: frame 147.50 (baselines 164.00/139.25/153.50/142.50, all 165.00), option 50.52
  (81.00/35.29/46.52/47.52, all 74.00), material 9.50 (33.50/6.50/7.00/14.50, all 27.00), lens refund 81.95
  (60.45/49.70/71.20/75.50/86.95, all 37.51). Skip runs: no confirmation -> 81.95 (state gate: status/frame row differ),
  no option refund -> 68.31, no material refund -> 79.38 (texts corrected from first draft 68.44/79.39).
- fix: option overwrite.replaced_by was not a verbatim rule sentence (period vs comma) -> quoted the full sentence.
- task1 per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK, REPLAY OK.
- final difficulty-wide gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK
  (suite means branches 49.00 / steps 16.00; history_rows_max 13; branches_max 53), GROUNDING OK, CACHE-DIFF INFO,
  SCOPE OK. check_traceability: NOT OK by design until the KB (docs/) is rendered — the only missing sources are the
  hidden task-tool names (3 in task 0, 4 in task 1), which the published KB carries.
- closure: 7 extended policies, 7 task tools, pairwise disjoint scopes (task 0: 3 policies/3 tools; task 1: 4/4);
  every task calls an owner=user tool; no handoff in gold. Temporary authoring scripts deleted.

## Rework round 2 (audits/policy_task/optical_eyewear_orders: _difficulty.md, 0.md, 1.md read in full)
- Plan: G4/T0-4/T1-3 drop docstring example amounts; O2 neutral docstrings; G1 P2 fall-through as the design's
  outside-coverage percentage; G3 P2 anchor stated as "the latest non-adapt remake, when opened before"; O8 quote both
  anchor sentences; O7 P1 zero-length window guard; G2 P5 settles options one at a time (first un-refunded in a fixed
  order); O3 P5/P6 scope wording without a timing connective; O9 option = light-adaptive/blue-light/anti-reflective
  stated in P4; T1-1 restructure task 1: root = member's cancellation confirmation booking the lens refund (user),
  frame return refund becomes an agent prerequisite (new tools, new uuid8s); O6 replace fresh-exam lowering with a
  card-spend lowering; T0-3/T0-6 seed rx-change remake at 60.00 (=40% x 149.99); T0-5 add closed old membership +
  closed card near-miss; T0-7/T1-5/T1-6 correct proof assertions.
- rework: task_tools.py — examples removed from all amount args (G4); option/material docstrings neutral (O2); retired confirm_eyewear_cancellation_a25e55a5 and post_lens_cancellation_refund_d976b5a7; new refund_frame_to_stock_fae456d1 (agent) and confirm_eyewear_cancellation_51323feb (user, cancels + lens refund). TASK TOOL CONTRACT OK
- rework: charter edited through a temporary loader that rewrites only the extended_policies section (base text
  byte-identical). P1 pro-rata tier now requires a window of at least one day (O7). P2 fall-through = the design's
  outside-coverage remake percentage in rule, baseline and overwrite (G1); anchor tiers restated as "the latest
  non-adapt remake on the job ... opened before" = compute (G3); overwrite[1].replaced_by quotes both anchor
  sentences (O8). P4 frame return refund retargeted to refund_frame_to_stock_fae456d1, subject credit only, option
  kinds named (O9). P5 settles option charges one at a time, first un-refunded of light-adaptive / blue-light /
  anti-reflective (G2), scope sentence without timing connective (O3). P6 scope wording (O3). P7 retargeted to the
  member's confirm_eyewear_cancellation_51323feb (cancels + lens refund), frame edge = state form on the frame
  refund credit (T1-1), fresh_exam_lowering replaced by retention_card_spend_lowering (O6). EXTENDED OK (--task 0).
- rework task 0: seed prescription-change remake 59.99 -> 60.00 (T0-3/T0-6); closed 2008 Business Membership
  9dd9f55c... + closed Business Store Card 08ef0056... as loyalty near-miss, profile_opened_date 2008-04-01 (T0-5);
  waiver 21.29 -> 21.30, P2 factor baselines 10.05/0.00/32.55/14.55/16.80/16.30 (all 0.00); P1 57.50 and P3 55.81
  unchanged; skip runs 64.01 / 40.54 unchanged; rationale §7 + revision log rewritten (T0-7). Per-task gates all OK.
- rework task 1: evaluation steps 9/10 -> unlock/call refund_frame_to_stock_fae456d1 (147.50); steps 15/16 ->
  unlock_user/call_user confirm_eyewear_cancellation_51323feb (lens refund 77.65); persona hand-over now the lens
  refund and closes on the confirmation (T1-1); contract steps 10/16, closure edge[0] (frame refund, state gate),
  order_uniqueness, edge_load_bearing (63.00 / 74.89; pool 265.49 / 224.47, T1-5), no_user_hint, tools_do_not_block,
  computations[3] (factor figures 56.15/45.40/66.90/75.50/82.65, fall-back 37.51), rationale rewritten (T1-6 opening
  pool 274.99 -> 60.24). Per-task gates OK.
- observations kept with reasons: O4 (base lifecycle lists cancellation/remake opening as agent transitions; the
  member confirms or authorizes his own write on the call — base frozen, recorded in rationale); O5 (method ladders
  keep one algorithm-changing tier each: P1 pro-rata, P5 pro-rata/subtraction); P2 multi prescription-change jobs
  (rx_booked sums them) — not exercised by any world.
- final gates (round 2): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK; TRACEABILITY NOT OK pending the KB render (missing = hidden tool names only).
  Temporary helpers (_ext.py, _sens.py) deleted.
