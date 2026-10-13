# Policy-task audit — listing_settings_and_compliance / task 1

## source_derivation_frozen

- Auditor: erl-task-policy-audit (independent Claude agent). Revision 1. Freeze time: 2026-10-07T19:40Z.
- Inputs: masked view `/tmp/erl45_views/r1/listing_settings_and_compliance/task_1.view.json` (sha256 0a383ab0ffa42ba21c69842411f5f1498c8d26230c3166d0b1682f8ef1035d87: frozen_time, user_scenario, initial_state only), `listing.extended.yaml` (e0068140…), `task_tools.py` (376399fd…), `blueprint/`.
- Masked and unread at freeze: the full `tasks/1.json` and `tasks/0.json`, both worklogs, other audits. Task 0's derivation was frozen to disk before this one was written; no GT of either task has been revealed.
- contamination_disclosure: none.

### policy_self_consistency (this task only)

- Charter-global conclusions are cited from `audits/policy_task/listing_settings_and_compliance/_difficulty.md` (§override_declarations, §rule_compute_equivalence, §action_binding_and_uuids, §prerequisite_graph, §prerequisite_sentences, §factor_ladders, findings G-1 … G-8).
- Handling time: frozen_time 2026-09-29 14:40 CDT → day of change/reset/request = 2026-09-29. The minimum-stay raise and the extra-guest reset are each evaluated on the opening world (the floor reads strikes, claims, reinstatements and quality rows; the extra-guest ceiling reads nightly_rate, extra_guest_threshold, claims and the plan — neither reads the other's field). The suggested nightly rate is evaluated after both, before the host's save.
- Real-world waits: none — all inputs are seeded decisions (claims decided ≤ 2026-06-24, reinstatement decided 2025-07-18, strikes, assessments ≤ 2026-07-01) or synchronous prior writes.
- Bearing of charter-global defects on this world:
  - G-1: the extra-guest and pricing computations are two of the four affected — demonstrated under factor_weight.
  - G-3 (pricing reads cleaning_fee with no ordering sentence): not reached — house cleaning fee 260.00 against an Entire Home cleaning-fee ceiling of at least 750.00.
  - G-2: a literal reader of "minimum_nights_floor … lowest minimum-night setting the host may choose" keeps the floor at 1 (the declared baseline); the extended rule explicitly adds party-prevention nights — not a second defensible answer.
  - G-4: not reached (64 stays).

### problem_chain

Root problem: the host wants the East Nashville house set to exactly Roamhaven's suggested nightly price and to save it himself → listing_ext_pricing_assist_rate ("a host may ask for it to be worked out and saves it as the listing's nightly rate in person").

| edge | sentence (root's own rule) | kind | opening state | unmet? |
| --- | --- | --- | --- | --- |
| E1 → listing_ext_minimum_stay_floor | "A suggested nightly rate is not worked out until the minimum stay on the listing stands at or above the listing's minimum-stay floor." | value_input (cleaning_per_night) | `listings[dbae6bad…].minimum_nights = 2`; floor on 2026-09-29 = 3 | yes |
| E2 → listing_ext_extra_guest_fee_ceiling | "The suggested nightly rate is fixed only after the extra-guest fee on the listing stands at or below the listing's extra-guest ceiling." | value_input (all_in_night) | `extra_guest_fee = 70.0`; ceiling on 2026-09-29 = 62.21 | yes |

Neither depended-on policy has a prerequisite. Derived tree: pricing ← {min-stay raise, extra-guest reset}; n = 2, value_input edges 2 ≥ 1 ✓; acyclic ✓; customer's own write: root `save_nightly_rate_d0fc8a90` is owner user, handed over per persona ✓.

- Order: {min-stay raise, extra-guest reset} in either order, then the host's save. The two writes touch different fields and neither computation reads the other's field or any fee-change row → one terminal state.
- Load-bearing runs (suggested rate, adjustment 0.11 × 0.75 = 0.0825): gold-candidate 395 + 730.5067 × 0.0825 = 455.27; skip E1 (min stay 2): 395 + 773.84 × 0.0825 = 458.84; skip E2 (fee 70): 395 + 761.6667 × 0.0825 = 457.84; opening world: 395 + 805.00 × 0.0825 = 461.41. Both edges bear weight.
- Tool bodies judge nothing (task_tools.py lines 182–200, 229–247, 275–293) ✓.
- Customer mentions no prerequisite ("you don't bring up any setting yourself") ✓.

### task_independent_derivation

1. Need / authority / timing: Jalen Whitmore wants the house's nightly rate set to exactly the Pricing Assist suggestion, told to him and handed over so he saves it himself; not the loft. Identity: phone 6155552716 + ID last4 2049 match `customers[e3431df1…]` → verify. Support changes authorised: "go ahead".
2. Act now: listing listed, host account ec82698f… active; suggestion clamped to 300 … 25000 is not binding.
3. Object: listing dbae6bad-7183-4ada-bd98-65d7ab113c1a ("East Nashville 4BR, Hot Tub & Big Porch", Entire Home, TN-NASHVILLE).
4. Minimum-stay floor on 2026-09-29:
   - party_violation strikes on the host account < 12 months: c669bce6 (2026-07-05) → 1 → 1 night; 86356bbe (2025-06-14, 15 months) excluded (near-miss).
   - approved property_damage claims on the listing < 12 months: b78ceacc (2026-06-10) → 1 → 1 night; dab5ed95 (2026-03-02) denied → excluded; 25ad0f29 (2025-06-15, 15 months) excluded.
   - most recent approved safety reinstatement 1e9b0778, decided 2025-07-18 → 14 whole months (≥ 12, < 24) → 1 night.
   - party-prevention nights 3. Quality assessments < 12 months: 144383ce (2025-10-01), 44b32cc2 (2026-01-01), 9c565810 (2026-04-01), 8971dd34 (2026-07-01) — 4, all pass (35efd502 2025-07-01 is 14 months) → halved, half night up → 2.
   - floor = 1 (Entire Home minimum_nights_floor) + 2 = **3**; 2 < 3 → `raise_minimum_stay_1aeaa300(dbae6bad…, 3)`.
5. Extra-guest ceiling on 2026-09-29 (on the opening nightly rate 395.00):
   - per-guest portion 395.00 / 6 = 65.8333…
   - approved property_damage verified losses < 24 months: 25ad0f29 2100.00 + b78ceacc 1450.00 = 3550.00 ≥ 2500 → +0.15 (dab5ed95 denied excluded).
   - active plan 9744e045… HostCover Standard: per_claim_limit_usd 25000 (> 5000, ≤ 25000) → +0.05; income_loss_max_nights 0 → +0.06. Addition 0.26.
   - plan effective 2025-02-14 → 19 whole months (≥ 12, < 36) → × 0.75 → 0.195.
   - share 0.945; ceiling = RND(min(300, 65.8333 × 0.945)) = RND(62.2125) = **62.21**; 70.00 > 62.21 → `reset_extra_guest_fee_9609655d(dbae6bad…, 62.21)`.
6. Suggested nightly rate on 2026-09-29 after both:
   - all-in night = 395.00 + 260.00 / 3 + 62.21 × (10 − 6) = 395.00 + 86.6667 + 248.84 = 730.5067.
   - rating: latest quality assessment 8971dd34 avg 4.86 ≥ 4.80, reviews 14 ≥ 10 → +0.06.
   - demand: latest Superhost assessment 75a166b3 (2026-07-01) nights_12m 212 (≥ 150, < 250) → +0.02.
   - Superhost tier → +0.03.
   - responsiveness: 75a166b3 response_rate_pct 99.0 ≥ 98 → +0.02.
   - listing age: first_listed 2025-02-14 → 19 whole months (≥ 12, < 24) → −0.02.
   - total 0.11. Confidence: pass/warning/suspension assessments < 24 months: 35efd502, 144383ce, 44b32cc2, 9c565810, 8971dd34 = 5 (58cd23e0 not_assessed excluded) → (≥ 3, < 6) → × 0.75.
   - suggested = RND(395.00 + 730.5067 × 0.0825) = RND(455.2668) = **455.27**.
   - Opening-world contrast (no prerequisite writes): 461.41.
7. Sequence: verify identity → `raise_minimum_stay_1aeaa300(dbae6bad…, 3)` and `reset_extra_guest_fee_9609655d(dbae6bad…, 62.21)` (agent, either order) → tell the host 455.27, hand over → `save_nightly_rate_d0fc8a90(dbae6bad…, 455.27)` (user). Terminal: minimum_nights 3, extra_guest_fee 62.21, nightly_rate 455.27, three change rows dated 2026-09-29.
8. Other state_due policies on this host's listings: none due. House: pet_fee 0.00, cleaning 260.00 (far below ceilings). Loft 6acdf2b3…: floor = 1 + 1 (host-wide strike; no loft claims, reinstatements or assessments) = 2 = its minimum stay; extra-guest 20.00 vs RND(189/2 × 0.91) = 86.00; cleaning 95.00, pet 0.00.

### factor_weight

Minimum-stay computation (opening world). Gold-candidate 3; baseline (`minimum_nights_floor` alone) = **1** ≠ ✓.

| factor | label | tier / evidence | baseline | floor under baseline |
| --- | --- | --- | --- | --- |
| party_strike_nights | parameter ✓ | one — host_account_events c669bce6 (host) | 0 | 1 + ceil(2/2) = 2 ✓ |
| property_damage_nights | parameter ✓ | one — protection_claims b78ceacc (protect) | 0 | 2 ✓ |
| safety_reinstatement_nights | parameter ✓ | older — reinstatement 1e9b0778 | 0 | 2 ✓ |
| party_nights_assessment_record | method (accepted, `_difficulty.md` §factor_ladders) | clean record — 4 passes | as is | 1 + 3 = 4 ✓ |

Near-miss: strike 86356bbe (15 months), claim 25ad0f29 (15 months), denied dab5ed95, assessment 35efd502 (14 months). Surviving 3 P + 1 M ✓; no multi-source factor here.

Extra-guest computation (opening world). Gold-candidate 62.21; baseline (395/6 × 0.75, capped 300) = **49.38** ≠ ✓.

| factor | label | tier / evidence | baseline | value under baseline |
| --- | --- | --- | --- | --- |
| damage_loss_addition | parameter ✓ | high — 3550.00 (protect) | 0 | RND(65.8333 × 0.8325) = 54.81 ✓ |
| per_claim_limit_addition | parameter ✓ | mid — Standard 25000 | 0 | 59.74 ✓ |
| income_loss_addition | parameter ✓ | none paid — Standard 0 nights | 0 | 59.25 ✓ |
| plan_phase_in | **no** — share 0.5/0.75/1 in one formula (G-1); realism weak (G-8) | mid — effective 2025-02-14 | 1 | 66.49 ✓ |

Near-miss: denied claim dab5ed95. Surviving 3 P, **0 M** → SOURCE-FACTOR RED (G-1).

Pricing computation (after both prerequisite writes). Gold-candidate 455.27; baseline (current rate) = **395.00** ≠ ✓.

| factor | label | tier / evidence | baseline | value under baseline |
| --- | --- | --- | --- | --- |
| rating_adjustment | parameter ✓ (multi-source, G-7 caveat) | high — 8971dd34 (4.86, 14) | 0 | 395 + 730.5067 × 0.0375 = 422.39 ✓ |
| demand_adjustment | parameter ✓ | mid — 212 nights (host) | 0 | 444.31 ✓ |
| superhost_adjustment | parameter ✓ | Superhost (host) | 0 | 438.83 ✓ |
| responsiveness_adjustment | parameter ✓ | high — 99.0 % (host) | 0 | 444.31 ✓ |
| listing_age_adjustment | parameter ✓ | mid — 19 months | 0 | 466.22 ✓ |
| assessment_confidence | **no** — share 0.5/0.75/1 (G-1) | mid — 5 assessed quarters | 1 | 475.36 ✓ |

Near-miss: 58cd23e0 (not_assessed) excluded from the confidence count; earlier Superhost assessment a8784886 (205 nights, 98.5 %) is not the most recent. Surviving 5 P, **0 M** → SOURCE-FACTOR RED (G-1).

Task-level: multi-source ≥ 1 (rating_adjustment) ✓; cross-difficulty ≥ 1 (host strikes and assessments, protect claims and plan — all seeded) ✓.

### findings (frozen, pre-reveal)

- **T1-1 — SOURCE-FACTOR RED** via `_difficulty.md` G-1: the extra-guest and pricing computations carry no honest method factor.
- **T1-2 — observation (existing logic).** The host account carries a second party_violation strike on 2026-07-05 (c669bce6). Under listing_evt_safety_standards a party breach confirmed by trust and safety suspends the listing with reason safety, and under listing_evt_reinstatement a suspended listing returns to listed only through an approved request; both listings are listed with no 2026 suspension or reinstatement on record. If that strike concerned the house, a coherent record would carry a 2026 safety approval, moving safety_reinstatement_nights to the "recent" tier (2): party nights 4 → halved 2 → floor still 3, so no scored figure moves; the strike row names no listing.
- **T1-3 — observation (realism).** The prerequisite order makes support cut the extra-guest fee from 70.00 to 62.21 on the old $395 rate. Then the host's own save of 455.27 would raise the ceiling to RND(455.27/6 × 0.945) = 71.71, which the original 70.00 fee sits under. The host ends with a lower fee than the charter would require once the new rate is saved. The order is stated by the rule, so this is no second reading, but no real support desk would do it this way.
- **T1-4 — observation (seed realism, positive).** The history is coherent with the charter at each logged change: the 55→70 extra-guest change on 2026-06-25 was within that day's ceiling (480/6 × 0.945 = 75.60); the 5→2 minimum-stay change on 2026-06-16 equalled that day's floor (1 + ceil(2/2) = 2); HostCover reimbursements reproduce from the protect charter (2100 × 0.80 − 250 = 1430; 1450 − 250 = 1200).

## source_gt_comparison

- Freeze record:
  - The header's "Freeze time" was an estimate written ahead.
  - The frozen sections of this file were on disk at 2026-10-07T19:20:47Z (sha256 b8ee3514f65e84aa1c8bde50161205e8630395bf2dae331def28d0bf45f01b90 before this append), after task_0.md (19:19:54Z) and `_difficulty.md` (19:18:43Z).
  - GT was first read at 2026-10-07T19:20:55Z (`tasks/0.json`, then `tasks/1.json`).
  - No GT was seen before this derivation was frozen. The frozen text above is unchanged.
- Need / authorisation / timing: same. The nightly-rate save is handed to the host as an owner=user call. Support performs the two corrections.
- Read set:
  - GT adds find_listing_reinstatement_requests, which the derivation used (row 1e9b0778).
  - GT adds find_protection_events, which the derivation did not need.
  - The other reads are the same.
- Now / wait / refuse: same (act now).
- Object: same (house dbae6bad…; loft excluded).
- Parameters, all equal:

  | write | GT | derivation |
  | --- | --- | --- |
  | minimum_nights | 3 | 3 ✓ |
  | extra_guest_fee | 62.21 | 62.21 ✓ |
  | nightly_rate | 455.27 | 455.27 ✓ |

- Tool / owner / order: same. GT runs the min-stay raise, then the extra-guest reset, then the host's save. The derivation allowed the two corrections in either order, as GT's order check also does.
- Terminal state: same. No other state_due policy is due on either listing (derivation item 8). GT [12] agrees.
- Problem tree vs `prerequisite_closure`, value against value:

  | item | GT | derivation |
  | --- | --- | --- |
  | edge → min-stay | value_input, cleaning_per_night | same |
  | min-stay why_false | 2 vs floor 3 | same |
  | min-stay skipped effect | 458.84 | 458.84 |
  | edge → extra-guest | value_input, all_in_night | same |
  | extra-guest why_false | 70.00 vs 62.21 | same |
  | extra-guest skipped effect | 457.84 | 457.84 |
  | both skipped | 461.41 | 461.41 |

  `resolution_order` matches the derivation's order.
- Factors vs `computations`, figure against figure:

  | computation | GT baseline_result | derivation | GT sensitivity | derivation |
  | --- | --- | --- | --- | --- |
  | min-stay | 1 | 1 | 2 / 2 / 2 / 4 | 2 / 2 / 2 / 4 ✓ |
  | extra-guest | 49.38 | 49.38 | 54.81 / 59.74 / 59.25 / 66.49 | same ✓ |
  | pricing | 395.0 | 395.00 | 422.39 / 444.31 / 438.83 / 444.31 / 466.22 / 475.36 | same ✓ |

  Tiers taken agree.
- Closest alternative candidates, all excluded by the rules:
  - 458.84 / 457.84 / 461.41: the two prerequisite sentences require the corrections first.
  - 475.36: the not_assessed quarter is excluded by "not_assessed quarters not counting".
  - Floor 2: rounding the half night down is excluded by "rounded up to a whole night".
  - Reading the loft's Essential plan (per-claim 5000 → +0.10; effective 2021-03-20 → full phase-in) would give an extra-guest ceiling of RND(395/6 × 1.06) = 69.78 and a suggestion of 457.76. This is excluded because the rule reads "the listing's active plan".
- Proof assertions checked:
  - why_false narratives: the 2026-06-16 floor of 2, the 2026-06-25 ceiling of 75.60, and the claim approval date 2026-06-24.
  - design_rationale [6] removal figures: 58.76, floor 2, 75.60.
  - The reimbursement figures.
  - "no restriction from strikes": one strike in the 365 days ending 2026-07-05.
  - All agree with the recomputation. No contradicted assertion was found.
- Verdict: **SOURCE-FACTOR RED (T1-1)**.
  - Policy self-consistency: PASS for this task, except the charter-global label defect.
  - Problem tree: PASS.
  - Unique solution: PASS.

## findings

1. **T1-1 — SOURCE-FACTOR RED**, via `_difficulty.md` §findings G-1.
   - Symptom: on this world, plan_phase_in and assessment_confidence bear weight but only substitute a number into one formula:
     - plan_phase_in: share 0.75 → 1 moves 62.21 to 66.49.
     - assessment_confidence: share 0.75 → 1 moves 455.27 to 475.36.
   - Demonstrated consequence: counting honest labels, the extra-guest computation has 0 method factors and the pricing computation has 0. The minimum bound is 1.
   - Affected:
     - listing.extended.yaml listing_ext_extra_guest_fee_ceiling.factors[3]
     - listing.extended.yaml listing_ext_pricing_assist_rate.factors[5]
     - computations[1] and [2]
     - design_rationale [14], whose words "addition phased 0.5/0.75/1; adjustment total weighted 0.5/0.75/1" describe a multiplier.
2. T1-2, T1-3 and T1-4 (frozen observations) stand. None is a red light, because none moves a scored figure or opens a second reading.
3. Observation: GT reads find_protection_events, which the policy surface does not need.

## revision_2

### source_derivation_frozen (revision 2)

- Auditor: erl-task-policy-audit, round 2.
- This section was appended at 2026-10-07T21:19Z, before any round-2 GT was read. task_0's revision_2 derivation was already on disk.
- Inputs: view `/tmp/erl45_views/r2/…/task_1.view.json` (sha256 ebfd7eb055825ac8ba2041a4f9c954804169c6f62078003fd5dc518e31eb5b0f), charter e432286d…, tools 376399fd….
- contamination_disclosure: none for round 2. The round-1 GT values belong to the round-1 charter; every figure below is recomputed.
- View diff against round 1:
  - frozen_time, user_scenario and every house row are unchanged.
  - Added: an approved safety reinstatement request 41cb8f75… on the **loft** 6acdf2b3… (submitted 2026-07-09, decided 2026-07-30).
  - Changed: the loft's minimum_nights 2 → 4.

### policy_self_consistency (this task, revision 2)

- Charter-global conclusions are cited from `_difficulty.md` §revision_2.
- Handling time: 2026-09-29 for every write. The min-stay raise and the extra-guest reset each read the opening world; neither reads the other's field. Pricing is computed after both.
- No real-world waits.
- G-3 is not reached: the house cleaning fee is 260.00, against a cleaning-fee ceiling of at least 750.

### problem_chain (revision 2)

| edge | kind | opening | target on 2026-09-29 | unmet? |
| --- | --- | --- | --- | --- |
| pricing → min-stay | value_input (cleaning_per_night via expected_stay_nights) | minimum_nights 2 | floor 3 | yes |
| pricing → extra-guest | value_input (all_in_night) | extra_guest_fee 70.00 | ceiling 63.20 | yes |

- n = 2; 2 value_input edges ✓. The owner=user root is handed over ✓. Acyclic. The two writes commute.
- Load-bearing (suggestion):

  | world | suggestion |
  | --- | --- |
  | gold-candidate | 446.11 |
  | min-stay raise skipped | 447.20 |
  | extra-guest reset skipped | 448.02 |
  | both skipped | 449.10 |

  Both edges bear weight.
- The tools judge nothing, and the persona names no prerequisite.

### task_independent_derivation (revision 2)

1. Need, identity, authorisation and object are unchanged. The object is house dbae6bad….
2. Minimum-stay floor (policy unchanged):
   - strike c669bce6 (2026-07-05) → 1 night;
   - approved property_damage b78ceacc within 12 months → 1 night;
   - the house's most recent approved safety reinstatement is 1e9b0778, decided 2025-07-18, 14 months back → 1 night;
   - party nights 3;
   - 4 all-pass assessments in 12 months → halved and rounded up → 2;
   - floor **3**, so `raise_minimum_stay_1aeaa300(dbae6bad…, 3)`.
   - New near-miss: the loft's request 41cb8f75 (decided 2026-07-30, 1 month back) would give the "recent" tier, but the rule reads "the most recent reinstatement request **of the listing**", which excludes it.
3. Extra-guest ceiling:
   - per guest 395 / 6 = 65.8333;
   - party_violation strike c669bce6 within 12 months → 36-month look-back;
   - approved property_damage losses within 36 months: 25ad0f29 2100 + b78ceacc 1450 = 3550 ≥ 2500 → +0.15 (dab5ed95 is denied);
   - Standard per-claim limit 25000 → +0.05;
   - income-loss 0 nights → +0.06;
   - share 0.70 + 0.26 = 0.96;
   - ceiling RND(65.8333 × 0.96) = **63.20**, so `reset_extra_guest_fee_9609655d(dbae6bad…, 63.20)`.
4. Suggested nightly rate:
   - Expected stay: the latest Superhost assessment 75a166b3 has 64 stays (≥ 10) and 212 nights, so (3 + 212 / 64) / 2 = 3.15625 nights.
   - Cleaning per night: 260 / 3.15625 = 82.3762.
   - Extra guests: 4 × 63.20 = 252.80.
   - All-in night: 395 + 82.3762 + 252.80 = 730.1762.
   - Adjustments:

     | adjustment | evidence | value |
     | --- | --- | --- |
     | rating | assessment within 3 months is 8971dd34 (2026-07-01: 4.86, 14 reviews) | +0.04 |
     | demand | 212 nights | +0.02 |
     | Superhost | tier | +0.02 |
     | responsiveness | 99.0 % | +0.01 |
     | listing age | 19 months | −0.02 |
     | total | | 0.07 |

   - Suggested rate: RND(395 + 730.1762 × 0.07) = RND(446.1123) = **446.11**.
   - Contrast on the opening world: 449.10.
5. Sequence: verify identity → min-stay raise 3 and extra-guest reset 63.20 (agent, either order) → hand over → host saves 446.11.
6. Stray state_due check:
   - House: pet 0; cleaning 260 is within its ceiling.
   - Loft (Entire Apartment, Essential plan), minimum-stay floor:
     - strike → 1 night;
     - no loft claims;
     - its own approved safety reinstatement 41cb8f75 is 1 month old → 2 nights;
     - party nights 3;
     - **no loft quality assessment is seeded**, so assessments_12m = 0 and the nights are counted as they are → 3;
     - floor 1 + 3 = 4, equal to its minimum stay of 4 → not due.
   - Loft extra-guest: 189 / 2 = 94.50; strike → 36-month look-back with no loss; share 0.70 + 0.10 + 0.06 = 0.86 → 81.27, against a fee of 20.00 → not due.
   - Loft cleaning 95 and pet 0 → not due.
   - No stray due policy.
7. Existing logic around the 2026-07-05 strike (round-1 T1-2): the loft now carries a safety reinstatement submitted 2026-07-09 and approved 2026-07-30. That places the second party breach on the loft, suspended and reinstated through an approved request, consistent with listing_evt_safety_standards and listing_evt_reinstatement. The loft row shows suspension_reason none, as the reinstatement event resets.
8. History coherence under the round-2 charter:
   - 2026-06-25, extra-guest 55 → 70:
     - the 2025-06-14 strike is 12 months back, so not within 12 but within 24 → 24-month look-back;
     - 3550 → +0.15;
     - share 0.96 × 480 / 6 → 76.80 ≥ 70 ✓.
   - 2025-03-01, extra-guest 40 → 55:
     - no strike → 12-month look-back, no loss;
     - share 0.81 × 450 / 6 → 60.75 ≥ 55 ✓. The 450 rate before 2026-05-20 is read from the 450 → 480 change row.
   - The minimum-stay changes are unchanged from round 1 ✓.

### factor_weight (revision 2)

| computation | factor | value under baseline | moves? |
| --- | --- | --- | --- |
| min-stay (gold 3; all-baseline 1) | strike / damage / reinstatement | 2 / 2 / 2 | ✓ |
| | record | 4 | ✓ |
| extra-guest (gold 63.20; all-baseline 46.08) | damage_lookback_by_party_record (M) | 12-month look-back → losses 1450 → +0.08 → 58.59 | ✓ |
| | damage_loss_addition | 53.33 | ✓ |
| | per_claim_limit_addition | 59.91 | ✓ |
| | income_loss_addition | 59.25 | ✓ |
| pricing (gold 446.11; all-baseline 395.00) | expected_stay_length (M) | spread over min stay 3 → 446.41 | ✓ (by 0.30) |
| | rating | 416.91 | ✓ |
| | demand | 431.51 | ✓ |
| | Superhost | 431.51 | ✓ |
| | responsiveness | 438.81 | ✓ |
| | listing age | 460.72 | ✓ |

- Near-misses:
  - min-stay: strike 86356bbe (15 months), claim 25ad0f29 (outside 12 months), denied dab5ed95, the loft's reinstatement request.
  - extra-guest: 25ad0f29 is inside only because of the strike-lengthened look-back.
  - pricing: a8784886 (older assessment); 35efd502 (2025-07-01) lies outside the 3-month rating window.
- Counts: min-stay 1 M + 3 P; extra-guest 1 M + 3 P; pricing 1 M + 5 P ✓.
- Multi-source: rating_adjustment ✓. Cross-difficulty: host and protect, seeded ✓.

### findings (revision 2, frozen, pre-reveal)

- **T1-1 — closed** via G-1 closure: the extra-guest and pricing computations now carry honest method factors that bear weight.
- **T1-2 — closed.** The 2026-07-05 strike now has its safety suspension/reinstatement trail on the loft.
- **T1-3 — unchanged observation (realism).** After the host saves 446.11, the extra-guest ceiling would be RND(446.11 / 6 × 0.96) = 71.38, which the original 70.00 sits under. The rule-forced order still has support cut a fee that the root write would have made lawful.
- **T1-4 — unchanged.**
- **T1-5 — new observation (seed vs charter).**
  - The loft has been listed since 2021-03-20, yet no loft quality assessment is seeded. listing_evt_quality_assessment assesses every listed listing each quarter.
  - The loft's minimum-stay compliance turns on that absence: with zero rows its floor is 4, which equals its minimum stay. Had its recent quarters been all pass, the floor would be 3 (still compliant); had any been a warning, the floor would be 7 and the floor policy would be due on the loft.
  - No figure of the scored tree moves, and the agent can only read the world as seeded. Recorded as an observation.
- No new red light pre-reveal.

### source_gt_comparison (revision 2)

- Reveal: round-2 `tasks/1.json` was first read at 2026-10-07T21:19:30Z. This file's revision_2 frozen section was already on disk at 21:19:24Z (sha256 of the whole file before this append: b85280c8371c0e9dfafccdec85030009a68d8b496eeee9ec87d483bf7682238a).
- Need, authorisation and timing; now/wait/refuse; object: same.
- Read set: GT reads reinstatement requests by customer, which also returns the loft's 2026 request. The rule's "of the listing" excludes it, as the derivation did.
- Writes, value against value:

  | write | GT | derivation |
  | --- | --- | --- |
  | minimum_nights | 3 | 3 ✓ |
  | extra_guest_fee | 63.2 | 63.20 ✓ |
  | nightly_rate (owner user) | 446.11 | 446.11 ✓ |

  Order: min-stay → extra-guest → save, inside the commuting class ✓. No other write; no stray due policy on house or loft ✓.
- prerequisite_closure:
  - Edges: value_input, value_input ✓.
  - why_false: 2 vs 3 and 70.00 vs 63.20 ✓. History clauses: floor 2 on 2026-06-16; ceiling 76.80 on 2026-06-25 with a 24-month look-back ✓.
  - Load-bearing: 447.20 / 448.02 ✓ (derivation 447.20 / 448.02).
- computations, figure against figure:

  | computation | baseline_result | sensitivity |
  | --- | --- | --- |
  | min-stay | 1 ✓ | 2 / 2 / 2 / 4 ✓ |
  | extra-guest | 46.08 ✓ | 58.59 / 53.33 / 59.91 / 59.25 ✓ |
  | pricing | 395.0 ✓ | 446.41 / 416.91 / 431.51 / 431.51 / 438.81 / 460.72 ✓ |

- Proof assertions in rationale [6], each recomputed and agreeing:
  - the 2025-03-01 ceiling of 60.75;
  - the 2025-07-20 floor of 5;
  - without b78ceacc: floor 2 and ceiling 58.59;
  - without the 2026-09-08 rate cut: 76.80;
  - "the loft (minimum stay 4 = its floor)".
- Status of round-1 items:
  - T1-1 closed.
  - T1-2 closed (the loft safety reinstatement trail).
  - T1-3 and T1-4 unchanged (observations).
- New: observation T1-5 (no loft quality history seeded). It changes no scored figure or assertion.
- Regressions: none.
- **Verdict revision 2: PASS.** Policy self-consistency PASS; problem tree PASS; factors bear weight PASS; unique solution PASS.

### findings (revision 2)

- Observation T1-3 (realism, unchanged): the rule-forced order has support cut the extra-guest fee to 63.20 at the old rate. After the host's 446.11 save, 70.00 would sit under the new ceiling of 71.38.
- Observation T1-5 (new; seed vs charter): the loft has been listed since 2021 with no quality assessment seeded. Its minimum-stay compliance (floor 4) rests on that absence. Scored values are unaffected.
- Charter-global observations are cited from `_difficulty.md` §revision_2.
