# Worklog — order_item_refunds_fees_and_tips (category: order), M=2

## Step 0 — draw (scripts/draw_counts.py --tasks 2)
{"task": 0, "prerequisite_problems": 3, "problems": 4, "factor_counts": [4, 5, 5, 6]}
{"task": 1, "prerequisite_problems": 3, "problems": 4, "factor_counts": [6, 5, 4, 6]}
=> 8 extended policies, 8 task tools, 42 declared factors; each tree = root + 3 prerequisite problems,
>= 2 value_input edges per task, >= 1 owner=user tool per task.

## Step 0 — difficulty pre-check (blueprint read)
- Claimed events: order_item_refunded, order_fee_refunded, order_fee_charged, order_tip_increased,
  order_tip_reduced, order_rescheduled, order_canceled (+ intake order_review_requests).
- order_tip_increased / order_tip_reduced carry an unconditional trigger into batch (batch_tip_adjusted_up/down):
  no task tool may write them (cross-category write through the event model) -> tips are left out.
- order_fee_waived triggers membership (member_priority_upgrade) -> not written.
- Gate mechanics: SUM/COUNT/MAX/LATEST are scoped to the target order, so every value_input edge must land its
  write on the same order the dependent computation reads. All four problems of each tree act on ONE order.
- Identity preamble: find_customers (step 0) -> verify_customer_identity (step 1), 2 credentials.

## Step 0 — design decisions (difficulty level)
- Every item refund row is bounded by the base dedup gate "never for more than the line's charge minus what was
  already refunded on it"; a full-charge refund (billed-not-found line kept uncapped, a substitution rejection) has no
  room for load-bearing factors. Factor-rich quantities: price-protection excess, weight overage, the part of a
  wrong item refunded when the customer keeps it, the capped grant under the per-order room, the over-cap remainder
  registered for review, the service-fee share, and the amounts customers carry to the review team in their own claims.
- Customer-owned writes available on completed orders: the customer's own claim to the review team (photo review
  when a damaged/quality line is above the photo threshold; limit review when the rolling 90-day limits stop the
  agent). Tip changes are excluded (unconditional trigger into batch); cancellation/reschedule need placed orders.
- The limit-review claim is written with subject order_item_refunded; its policy declares an overwrite of the base
  rolling-limit sentence (order_agg_refund_review) and restates it in extended form, routing a crossing claim to
  the customer's own limit-review claim.
- Tools (uuid8 minted one by one with uuid.uuid4().hex[:8]):
  task 0: refund_wrong_item_79d6dec9 (agent), refund_unfound_item_93423917 (agent),
          register_over_cap_review_9b0d89a0 (agent), submit_limit_review_claim_079a4c96 (user, root)
  task 1: refund_weight_overage_a9b70a98 (agent), refund_substitution_overcharge_0e292d66 (agent),
          refund_service_fee_share_1e350a8d (agent), submit_photo_review_claim_a5aac31c (user, root)
- Task 0 tree (one Standard Delivery order): LR root <- OC (state_gate), OC <- M (value_input), M <- WI (value_input).
  Factor counts drawn [4,5,5,6]: M 4, WI 5, OC 5, LR 6.
- Task 1 tree (one Stock-Up Delivery order): PHOTO root <- WO (value_input), PHOTO <- SF (value_input),
  SF <- WO (value_input), SF <- PP (value_input). Factor counts drawn [6,5,4,6]: PHOTO 6, SF 6, PP 5, WO 4.
- Scope budget: task 0 claims {WI, M, OC, LR}; task 1 claims {WO, PP, SF, PHOTO}; disjoint, jointly all 8.

## Task 0 — Step 1/2 persisted
- order.extended.yaml: base copied verbatim; extended_policies order_ext_wrong_item_kept_refund (5 factors),
  order_ext_unfound_line_refund (4), order_ext_over_cap_review_amount (5), order_ext_limit_review_claim_amount (6).
- task_tools.py: 4 task-0 tools; check_task_tools -> TASK TOOL CONTRACT OK.
- Revision: limit-review window credit read only tier params (P) -> gate "no record evidence"; replaced by the
  basket credit (COUNT of billed lines + SUM of item subtotal). Baseline paragraph of the wrong-item policy named
  class points / basket uplift -> struck (a computation document must be silent about factors).
- DSL limitation noted: compute cannot key on a caller-named line number, so each policy selects its line by a
  record class unique on its order (approved_by_customer / not_found_refunded / perishable-as-ordered); the seed keeps
  exactly one line per class.

## Task 0 — closed
- Gold: WI 6.27 (step 8) -> M 48.86 (step 10) -> OC 11.30 (step 12) -> LR 18.78 (step 14, user). Baselines 3.03 / 33.58 / 1.12 / 11.58.
- Per-task gates all green: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (closure 31/31), SOLVABILITY OK, COMPUTE OK,
  GROUNDING OK, CACHE-DIFF INFO, SCOPE OK. design_rationale written in tasks/0.json.

## Task 1 — Steps 1-5 persisted
- Policies appended: order_ext_weight_overage_refund (4 factors), order_ext_substitution_price_protection (5),
  order_ext_service_fee_share_refund (6), order_ext_photo_review_claim_amount (6) -> multiset [4,5,6,6] = draw [6,5,4,6].
- Tools appended: refund_weight_overage_a9b70a98, refund_substitution_overcharge_0e292d66, refund_service_fee_share_1e350a8d,
  submit_photo_review_claim_a5aac31c (user); TASK TOOL CONTRACT OK (8 tools).
- World tasks/1.json: Desmond Galloway, Cartwise+ Annual (enrolled 2022-02-14, fees 2024/2025/2026-02-14), Whole Foods
  Stock-Up order completed 2026-09-19T12:20, frozen 2026-09-21 14:30 CDT.
- Handling-time run (scratch evalchain): PP 17.40 (baseline 2.50), WO 10.61 (4.42), SF 4.22 (0.32), PHOTO 44.94 (31.19).
  PP/WO swapped -> identical (commute). Skip WO -> SF 3.17, PHOTO 58.66; skip PP -> SF 2.49, PHOTO 44.54; skip SF -> PHOTO 46.33.
- Revision: fee-share method tier 1 first priced the share at the member rate -> 1.725 vs proportional 1.724 rounded to the
  same cent after raises (decorative risk); replaced by the pre-member-saving fee basis (3.42 vs 2.28 raised).

## Task 1 — closed; difficulty-level final run (no --task; check_traceability skipped: KB not yet published)
- EXTENDED OK (8 policies, all covered, disjoint scopes, every task has multi-source + cross-difficulty factors and a user tool)
- TASK TOOL CONTRACT OK (8 tools)
- REPLAY OK (0.json closure 31/31, 1.json closure 19/19)
- SOLVABILITY OK
- COMPUTE OK (suite means branches 64.00, steps 15.00; history_rows_max 42; branches_max 67)
- GROUNDING OK; CACHE-DIFF INFO (no cache trap designed); SCOPE OK
- Union/exclusivity: task 0 {wrong-item, unfound-line, over-cap, limit-review}; task 1 {price protection, weight overage,
  service-fee share, photo review}; every extended policy fires at exactly one gold call; no handoff in any gold.

## Rework round 2 (audits/policy_task/order_item_refunds_fees_and_tips: _difficulty.md, 0.md, 1.md) — plan
- F-1/T0-P1: declare overwrite of "A not_found_refunded line is never billed, so it has nothing to refund." in the
  unfound-line and over-cap policies.
- F-2/T0-T3/F-3: both cap replacements state that the base per-order cap keeps governing every other issue refund;
  the limit-review rule states that a claim crossing the rolling limits books nothing and registers no over-cap
  request; sentence L2 narrowed to the not-found line's over-cap part.
- E-1/T0-T2: every policy with a month window / month tenure states the anniversary month-counting convention.
- X-1/T0-T1: fee-share scope narrowed (declared override): the service fee is shared back only once a price-protection
  or weight-overage refund stands; issue refunds alone leave it standing -> not owed in task 0's world.
- F-4/T1-F1: guarantee relabelled parameter; protection margin rebuilt as a method (protected-price basis).
- F-5/T1-F2: spoilage credit re-laddered on billed vs requested weight (both tiers reachable).
- T1-F3: membership re-dated (enrolled 2022-09-20, annual fees each 20 Sep) -> tenure 47 months (calendar-month
  reader says 48), 2025-09-20 fee exactly 12 months old (excluded), 2023-09-20 fee exactly 36 months old (excluded).
- T0-C1/T1-C1: personas no longer know the prerequisite items.
- Observations E-3, E-5, LR<-M effect wording fixed; E-4 ties checked on gold figures.

## Rework round 2 — closed, per audit item
- F-1 / T0-P1: order_ext_unfound_line_refund and order_ext_over_cap_review_amount each declare an overwrite of
  order_evt_substitutions "A not_found_refunded line is never billed, so it has nothing to refund." (replaced_by the
  unfound rule's opening sentence / a new over-cap sentence "A line billed although its substitution decision records it
  as not found carries a charge to refund despite that decision ...").
- F-2 / T0-T3: both rules now state that their room/over-cap pricing governs only a line recorded as not found, and that
  every other issue refund keeps the base per-order cap with the part above it registered as refund_over_cap.
- F-3 / T0-T3: L2 sentence (limit-review rule + policy_source + condition + task 0 prerequisite_closure) now reads "... once
  the part of every line recorded as not found that lies above its unfound-line room stands as a submitted over-cap
  review request."; the limit-review rule and its overwrite replaced_by say a claim crossing the rolling limits books
  nothing and registers no over-cap request (the whole issue is the customer's claim). Task 0 gold unchanged.
- E-1 / T0-T2: an anniversary month-counting sentence added to all seven month-window rules (wrong-item, unfound,
  over-cap, limit-review, weight-overage, price-protection, fee-share, photo) and quoted in the window bindings'
  compute_basis; task 0 figures unchanged (6.27 / 48.86 / 11.30 / 18.78) and now the only reading.
- X-1 / T0-T1: fee-share rule (and its overwrite replaced_by) now shares the service fee back only once a
  price-protection or weight-overage refund stands; an order with only issue refunds keeps its fee. Compute returns 0
  otherwise. Basis ladder re-cut (plan & weight-overage / plan & none / no plan). Task 0's world owes no fee share.
- F-4 / T1-F1: price_protection_guarantee relabelled parameter; price_protection_margin replaced by the method
  price_protection_protected_price (original price / average of original and billed / cap-raised original). 17.40 unchanged.
- F-5 / T1-F2: photo_review_spoilage_credit re-laddered on billed vs requested weight (both non-fall-through tiers reachable).
- T1-F3: task 1 membership re-dated (enrolled 2022-09-20; fee rows 2022-09-20 first_period, 2023..2026-09-20 renewal):
  tenure 47 anniversary months vs 48 for a calendar-month reader flips fee-share tenure (0.15 vs 0.30) and photo tenure
  (1.00 vs 2.00); the 2025-09-20 and 2023-09-20 fees sit exactly on the 12- and 36-month edges. New gold: SF 4.07,
  PH 43.99 (baselines 0.32 / 31.19); skip effects 57.72 / 45.33 / 3.02 / 2.34; PP/WO order proof re-run.
- T0-C1 / T1-C1: both personas lost the lines naming the prerequisite items; no_user_hint and rationale §8 rewritten.
- Observations: E-3 plan condition written into the over-cap / limit-review fee-part sentences; E-5 "deli" wording;
  limit_review <- unfound `effect` made general; E-4: no scored gold figure sits on a .xx5 tie after rework (the photo
  intermediate is now 39.49); E-2/E-6 unchanged (single line per class; wrong-item guard never binds).
- Final gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK (traceability skipped: KB not published).

## Rework round 3 (audit revision_2) — per item
- T1-F3 residual (weight_overage, price_protection near-miss): tasks/1.json order 6d3cb85e window moved to
  2026-09-19T16:00-19:00 and completed_at to 2026-09-19T18:20 (on time, same date). The rules count "calendar days
  from the date of completed_at to today" = 2; only 44 hours have elapsed, so an elapsed-day reader takes the 1-day
  tier: PP 16.90 instead of 17.40, WO 10.11 instead of 10.61 (also SF days credit and photo spoilage lose their tier).
  Gold figures unchanged; factor_trace, tracing, seed_consistency, read objective, persona ("Saturday evening") and
  rationale updated.
- R2-O1: compute_basis.sf_all_refunded now quotes "the basis is every item refund standing on the order" (verbatim).
- Effect-wording observation: the limit_review <- unfound `effect` was already generalised in round 2 ("... which can
  carry the count or the amount across the limit"); no world fact remains.
- E-4: correction to the round-2 note — the charter's RND is unchanged; the only .xx5 values are in two task-0
  baseline figures (42.845, 39.855 -> 44.57 / 33.58 under float RND vs 44.58 / 33.59 half up); no scored gold figure
  sits on a tie. Left as an observation (tooling primitive).
- R2-O2..R2-O5: observations, no change (dual-use over-cap tool is declared in the over-cap rule; X-1 trigger sentence
  is a scope statement whose stricter S1/S2 sentences sit in the same rule; the base service-fee reversal is declared;
  spoilage realism noted).
- Final gate block round 3: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK (traceability skipped).
