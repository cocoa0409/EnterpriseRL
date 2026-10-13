# Policy-task audit — damage_claims_and_protection / task 1

## source_derivation_frozen

- Round 1. Freeze time: written between 2026-10-07T19:03:44Z and 19:07:05Z; file hash recorded at 19:07:05Z before any reveal. Auditor: independent policy-task auditor (Claude agent).
- Source: `/tmp/erl45_views/r1/damage_claims_and_protection/task_1.view.json` (sha256 4b4f04d99fe52df573619d18f0bb1ba46a571180873286601e5ba88ebfaed779; frozen_time, user_scenario, initial_state only), `protect.extended.yaml` e56da7e0…e363c, `task_tools.py` 9109faa6…cddb8a0, blueprint.
- Masked and not read before this freeze: everything in `tasks/0.json` / `tasks/1.json` beyond the views; both worklogs. Task 0's GT has not been revealed either (all M derivations are frozen before any reveal).
- contamination_disclosure: none.

### policy_self_consistency (this task only)

Charter-global conclusions cited from `_difficulty.md` (§ policy_conflict_scan, § rule_compute_equivalence, § action_binding_and_uuids, § prerequisite_graph, § prerequisite_sentences, § override_declarations, § factor_ladders F-G1). No undeclared override; the income lost-nights override is declared.

- Handling time: property and pet on the opening world; income after both reimbursement rows exist. Opening-world income figure differs (below).
- No real-world waits: all three claims approved 2026-10-01 with evidence complete; guest requests, guest payments, escalations, calendar block and host cancellation records all precede frozen_time 2026-10-07 09:20 CDT. Every fact reachable via the share finders (`find_protection_claims/events/plans`, `find_listings`, `find_listing_events` (stay_id or listing_id), `find_host_accounts`, `find_host_account_events`, `find_stays`).
- Base gates: filing (check_out 2026-08-18 → property/pet filed 2026-08-20, income 2026-08-24; 2 and 6 days ≤ 14) ✓; guest requests sent first ✓; guest paid partial on each (60.00 / 35.00 / 20.00) ✓; escalation after deadline and within 30 days (property 12, pet 12, income 25 days) ✓; coverage (check-in 2026-08-14 ≥ effective 2021-03-15, plan active; level Plus since 2026-02-16) ✓; income_loss_covered true on Plus ✓; plan year from 2026-03-15 has 0 paid claims ✓; no reimbursement on any of the three claims ✓. Act now.

### problem_chain

- Root problem: accept the lost-income settlement on claim 4634294e-1189-403c-9f68-346b4ba692f1 — `protect_ext_income_loss_settlement`, `accept_income_loss_settlement_ab094655` (owner=user).
- Prerequisite sentences in the income rule: (1) "The income-loss settlement is not fixed until the plan's HostCover ledger shows a reimbursement on every approved property-damage claim of the same stay." (2) "The income-loss settlement is likewise not fixed until the ledger shows a reimbursement on every approved pet-damage claim of the same stay."
- At frozen_time: stay 4006f145-bb4d-44d0-b1d0-83cc8477f0eb carries approved property claim 605bc43f-… and approved pet claim a85b2e37-…; protection_events has 7 rows (1 premium, 3 requests, 3 guest payments), none `protect_reimbursement_paid` → both states false.
- Resolving writes: property rule → `pay_property_damage_reimbursement_941cbbf5` (agent); pet rule → `pay_pet_damage_reimbursement_a5391300` (agent). Neither rule carries a prerequisite sentence. Tree closed.
- Derived tree: {income (root, user), property (agent), pet (agent)}; edges income → property, income → pet, both value_input (enter `in_stay_settled` → `in_deductible`); order {property, pet} (either) → income. n = 2, value_input edges 2 ≥ max(1,1); one user write; acyclic. Isomorphic to the declared prerequisite.
- Load-bearing runs: both skipped → income 499.70; property skipped only → 583.03; pet skipped only → 583.03; both written → 666.37. Each edge bears weight.
- Parallel edges: property's figure does not read pet's write and vice versa — pet deductible is the order-free equal share 250/3; property's deductible factor is decided by the professional-tier tier (host Professional Host, listing Entire Home), and its Superhost branch's "claim from another stay" excludes same-stay rows; the remaining aggregate (200,000.00) is not binding and the paid-claim count reaches 2 < 6. Both orders give property 1,554.60 and pet 586.13 — one terminal state.
- No waiting; tools do not judge prerequisites (`_difficulty.md` § action_binding_and_uuids).
- Persona: raises only the root ("you want to accept the lost-income settlement and get the money paid out"). Reactive: "If the agent asks what else the dog and the guests damaged, you say … and that you filed for those too" (only on the agent's question; observation O-T1-1); "If the agent says other claims from that stay have to be paid before the lost-income settlement can be offered, you say fine, go ahead and do it" (passive authorisation). Closes on acceptance.

### task_independent_derivation

1. Need/authorisation: Darnell Okoro (d92373e0-…), host account a9b9b28e-… (Professional Host, Okoro Stays LLC); accept the lost-income settlement himself when handed the step, with the claim id and amount the agent gives; authorises the agent to pay the other claims of the stay first; no payout or plan change. Identity: phone 6155275318; verify with last4 5642 + email darnell@okorostays.com or DOB 1977-09-03.
2. Act now on all three.
3. Objects: plan d49a983f-77a5-4c2d-851b-c6f719303800 (HostCover Plus, active, tier_changed_date 2026-02-16); listing 9fadc62c-… (Entire Home, pet_fee 75.00, photo_count 26); damaging stay 4006f145-… (check-in 2026-08-14, fee assessed 2026-08-14); cancelled stay 1f113763-… (Delgado, cancelled_by_host 2026-08-19); block 2026-08-21 → 2026-08-30 (listing_events b3ee5d04-…, block_reason host_cancellation); host_cancellation_recorded 54e34abc-… band 30_days_to_48_hours, initiated_by host; quality reviews 2026-04-01 pass, 2026-07-01 warning, 2026-10-01 warning (most recent).
4. Property (opening world): depreciation 30 months → 13-36 → 20 %; condition most recent review warning → 85 %; escalation DAYS(2026-08-23, 2026-09-04) = 12 → 95 %; deductible share 250/3 = 83.333…, factor Professional Host + Entire Home → 1.5 → 125.00; net guest 60.00 < 125.00 → subtract deductible 125.00; covered 2,600 × 0.80 × 0.85 × 0.95 = 1,679.60; net 1,554.60; cap min(100,000, 200,000) → **1,554.60**. Write `pay_property_damage_reimbursement_941cbbf5(claim_id="605bc43f-bf0a-4bef-8233-b091275533b3", amount=1554.60)`.
5. Pet (opening world): depreciation 48 → 37-60 → 40 %; pet-fee 75.00 → (0,100) → 90 %; condition warning → 90 %; escalation 12 → 95 %; deductible 250/3 = 83.333…; net guest 35.00 < 83.33 → subtract deductible; covered 1,450 × 0.60 × 0.90 × 0.90 × 0.95 = 669.465; net 586.1317; cap min(5,000, 100,000, 200,000) → **586.13**. Write `pay_pet_damage_reimbursement_a5391300(claim_id="a85b2e37-7dfa-49f4-a3b4-4c0c027fba33", amount=586.13)`.
6. Income (after 4 and 5): lost-nights — Plus covers income loss, blocked nights DAYS(2026-08-21, 2026-08-30) = 9 > 7 → 1,890 × 7 / 9 = 1,470.00; timing — host-initiated, 30_days_to_48_hours → 80 %; escalation DAYS(2026-08-27, 2026-09-21) = 25 → 22-30 → 85 %; new-cover 2026-02-16 → 2026-08-14 = 179 days → 75 %; deductible 250 × (3 − 2)/3 = 83.333…; net guest 20.00 < 83.33 → subtract deductible; covered 1,470 × 0.80 × 0.85 × 0.75 = 749.70; net 666.3667; cap min(100,000, 200,000 − 2,140.73) → **666.37**. Opening-world contrast: **499.70**. Customer calls `accept_income_loss_settlement_ab094655(claim_id="4634294e-1189-403c-9f68-346b4ba692f1", amount=666.37)`.
7. Terminal state: three `protect_reimbursement_paid` rows on plan d49a983f posted 2026-10-07 (1,554.60; 586.13; 666.37). No denial, handoff or setting change.

### factor_weight

Property:

| factor | label | tier (records) | baseline input | value under baseline | weight |
| --- | --- | --- | --- | --- | --- |
| property_depreciation_share | P | 13-36 → 20 % (item_age_months 30) | 0 | 1,974.50 | bears |
| property_condition_share | P, cross listing | warning → 85 % (listing_events 2026-10-01 quality_outcome warning) | 100 | 1,851.00 | bears |
| property_escalation_share | P | 12 days → 95 % | 100 | 1,643.00 | bears |
| property_deductible_factor | P, multi-source, cross host | Professional Host AND Entire Home → 1.5 (host_accounts.variant_name; listings.variant_name) | 1 | 1,596.27 | bears |
| property_guest_payment_method | M | 0 < 60.00 < 125.00 → deductible alone | payments + deductible | 1,494.60 | bears, struck by F-G1 |

- Fall-back (2,600 − 60.00 − 83.33): **2,456.67** ≠ 1,554.60. Near-miss: the 2026-04-01 `pass` review (excluded by "most recent"); the pet and income claims' guest payments on the same stay (excluded by "recorded on the property-damage claim"). No outcome stamp. Surviving: 4 P, **0 M**.

Pet:

| factor | label | tier (records) | baseline input | value under baseline | weight |
| --- | --- | --- | --- | --- | --- |
| pet_depreciation_share | P | 37-60 → 40 % (age 48) | 0 | 1,032.44 | bears |
| pet_fee_share | P, cross listing | 0 < 75.00 < 100 → 90 % (listings.pet_fee) | 100 | 660.52 | bears |
| pet_condition_share | P, cross listing | warning → 90 % | 100 | 660.52 | bears |
| pet_escalation_share | P | 12 days → 95 % | 100 | 621.37 | bears |
| pet_guest_payment_method | M | 0 < 35.00 < 83.33 → deductible alone | payments + deductible | 551.13 | bears, struck by F-G1 |

- Fall-back (1,450 − 35.00 − 83.33): **1,331.67** ≠ 586.13. Near-miss: the 2026-04-01 pass review. Surviving: 4 P, **0 M**.

Income:

| factor | label | tier (records) | baseline input | value under baseline | weight |
| --- | --- | --- | --- | --- | --- |
| income_lost_nights_method | M, multi-source, cross listing | covered AND 9 blocked > 7 → prorate (Plus income_loss_covered; listing_events block 08-21→08-30) | in_loss 1,890.00 | 880.57 | bears |
| income_cancellation_timing_share | P, cross host | host + 30_days_to_48_hours → 80 % (host_account_events 54e34abc) | 100 | 853.79 | bears |
| income_escalation_share | P | 25 days → 85 % | 100 | 798.67 | bears |
| income_new_cover_share | P, cross host | 179 days → 75 % (tier_changed_date 2026-02-16; fee assessed 2026-08-14) | 100 | 916.27 | bears |
| income_guest_payment_method | M | 0 < 20.00 < 83.33 → deductible alone | payments + deductible | 646.37 | bears, struck by F-G1 |

- Fall-back (1,890 − 20.00 − 83.33): **1,786.67** ≠ 666.37. Near-miss: enrollment 2021-03-15 vs last level change 2026-02-16 (new-cover); the `host_cancellation_penalty_charged` row for the same stay, which repeats the band but carries initiated_by none (the rule reads the cancellation record); the cancelled stay's own row. Surviving: 3 P + 1 M (lost-nights) — meets the floors.
- Cross-difficulty seed checks: host_cancellation_recorded band agrees with the host charter (2 days before check-in → 30_days_to_48_hours); penalty 25 % × 2,010.00 = 502.50 ✓; block covers the cancelled stay's nights per listing_evt_calendar_block ✓; host fee 15.5 % × 1,035.00 = 160.43 ✓; premium 1.5 % × 960.00 = 14.40 ✓.
- Task-level: multi-source ✓ (property deductible factor, lost-nights); cross-difficulty ✓ (listing, host). Method floor fails on property and pet.

## findings

- **SOURCE-FACTOR RED (F-G1 consequence)** — symptom: the property (1,554.60) and pet (586.13) computations each have a single `method` factor, the guest-payment ladder, whose middle and fall-through tiers select the same subtraction. Root cause: `_difficulty.md` § factor_ladders F-G1. Evidence: `pr_offset`, `pe_offset`; rule "when no net guest payment stands, the payments and the deductible are both subtracted". Demonstrated consequence: at 0.00 net payments, property gives 1,679.60 − 125.00 = 1,554.60 under T2 and 1,679.60 − (0.00 + 125.00) = 1,554.60 under T3; the factor is struck and property and pet keep 0 `method` factors (floor 1). Income keeps the lost-nights method and is not below the floor. Affected: protect_ext_property_settlement and protect_ext_pet_damage_settlement `factors[*_guest_payment_method]`. First round.
- Observation O-T1-1: persona discloses the sibling claims only when asked what else was damaged — not a short-circuit.
- Observation: condition share reads a review dated after the damaging stay (2026-10-01) — `_difficulty.md` O-L3 (here 2026-07-01 is also a warning, so no second answer); pet-fee share O-L4; escalation shares O-L1.
- Policy self-consistency, problem tree, unique solution: no defect in the blind derivation (pending GT comparison).

## source_gt_comparison

- Reveal time: 2026-10-07T19:07:05Z (same command that hashed the frozen files, hashes printed first), after both derivations were frozen (task_1.md sha256 at freeze 6eb3fab2…c72285). `tasks/1.json` read in full; worklog.md not read.

| item | blind derivation | GT | same? |
| --- | --- | --- | --- |
| need / authorisation / timing | accept lost-income settlement now, customer's own act; agent authorised to pay the other claims first | request_alignment; step 18 owner user; steps 14, 16 owner agent | same |
| identity | phone; last4 5642 (+ phone/email/DOB) | find_customers(phone); verify(phone + last4) | same |
| read set | plans, claims, events, listings, listing events, host accounts, host events, stays | steps 2-12 (adds payout methods, guest stays) | same in substance |
| now/wait/refuse | act now on all three | act now | same |
| objects | property 605bc43f-…, pet a85b2e37-…, income 4634294e-…; block/cancellation on stay 1f113763-… | same | same |
| property amount | 1,554.60 | step 14 1554.6 | same |
| pet amount | 586.13 | step 16 586.13 | same |
| income amount | 666.37 | step 18 666.37 | same |
| tool / owner / order | property, pet (either order) → income (user) | 14 property → 16 pet → 18 income; order_uniqueness states pet-first gives the same DB hash | same |
| terminal state | three reimbursement rows | same | same |

- Closest alternatives excluded: income before the damage claims (499.70) — excluded by the two "not fixed until" sentences; income with only one prerequisite settled (583.03) — excluded by "every approved … claim of the same stay" for both categories; whole verified loss 1,890 instead of 7/9 (880.57) — excluded by the lost-nights rule ("when the blocked nights exceed income_loss_max_nights, the verified loss is multiplied by income_loss_max_nights and divided by the blocked nights"); enrollment instead of last level change for new-cover (916.27) — excluded by the rule's "from the plan's last level change".
- prerequisite_closure value-by-value: root income = mine; edges income → property and income → pet, value_input, in_stay_settled, state = mine; why_false "0 reimbursed claims of 3" = mine; skipped_effect 583.03 each = mine; flips_to_true deductible 83.33 = mine; resolution_order [property, pet, income] consistent with my either-order derivation; order_uniqueness (same terminal state either order) = my parallel-edge argument.
- factor_sensitivity / baseline_result figure-by-figure: property 1,974.50 / 1,851.00 / 1,643.00 / 1,596.27 / 1,494.60, baseline 2,456.67 — all equal; pet 1,032.44 / 660.52 / 660.52 / 621.37 / 551.13, baseline 1,331.67 — all equal; income 880.57 / 853.79 / 798.67 / 916.27 / 646.37, baseline 1,786.67 — all equal.
- Proof-field checks: design_rationale §4-§7 world assertions (dates, days 12 / 25 / 179, band, block nights, guest payments, deductible 83.33) agree with the seed and my recomputation.

Verdict by relationship:
- Policy self-consistency: PASS.
- Problem tree: PASS.
- Factors: **SOURCE-FACTOR RED** — F-G1 (property and pet computations each left with 0 method factors; income passes).
- Unique solution: PASS.

**Task 1 verdict: SOURCE-FACTOR RED.**

## findings (post-reveal additions)

- None new. Pre-reveal findings unchanged.

## edit_disclosure

After the reveal, the only edit made above the comparison sections was to the freeze-time and reveal-time metadata lines. The first-written times (19:05Z / 19:12Z / 19:16Z / 19:20Z) were made up and did not match the clock; they were replaced with the recorded times (19:03:44Z directory creation, 19:07:05Z hash and reveal). No derivation, figure or finding was changed. Because of this edit, the freeze hashes quoted above no longer match the current file bytes.

## revision_2

### source_derivation_frozen (r2)

- Written between 2026-10-07T21:36:11Z and 21:37:49Z (clock reads), before any round-2 task JSON was opened.
- Source: `/tmp/erl45_views/r2/damage_claims_and_protection/task_1.view.json` sha256 4b4f04d9…5e363c. It is byte-identical to the round-1 view (JSON compared equal), so world and persona are unchanged. Charter and tools changed (`_difficulty.md` § revision_2). Because the charter moved, the per-task sections are re-derived, not carried forward.
- Masked: round-2 `tasks/1.json` beyond the view; worklog.md.
- contamination_disclosure: round-1 GT for this task is known to the auditor (1,554.60 / 586.13 / 666.37); those figures followed the round-1 guest-payment method, which round 2 replaces. No round-2 GT seen.

### policy_self_consistency (r2, this task)

- Charter-global: `_difficulty.md` § revision_2. Handling time, no-wait and base gates: unchanged world, same conclusions as round 1 (all PASS).

### problem_chain (r2)

Unchanged and re-verified: root income (user); two state-form, value_input prerequisite sentences (property, pet); no reimbursement rows at frozen_time; resolved by the two agent tools; parallel edges order-free. The r2 proportional method reads only each claim's own A, D and P, so pet and property still do not read each other. Load-bearing: income 486.37 with both damage claims unpaid, 567.48 with one, **648.59** with both. Tools do not judge.

### task_independent_derivation (r2)

- Property: A = 2,600 × 0.80 × 0.85 × 0.95 = 1,679.60; D = 250/3 × 1.5 = 125.00; Plus proportional: 125.00 + 60.00 × 1,554.60/1,679.60 = 180.5347…; net 1,499.0653… → **1,499.07**. `pay_property_damage_reimbursement_941cbbf5("605bc43f-bf0a-4bef-8233-b091275533b3", 1499.07)`.
- Pet: A = 1,450 × 0.60 × 0.90 × 0.90 × 0.95 = 669.465; D = 83.333…; 83.333… + 35.00 × 586.1317/669.465 = 113.9766…; net 555.4884… → **555.49**. `pay_pet_damage_reimbursement_a5391300("a85b2e37-7dfa-49f4-a3b4-4c0c027fba33", 555.49)`.
- Income (after both): A = 1,470.00 × 0.80 × 0.85 × 0.75 = 749.70; D = 250 × 1/3 = 83.333…; 83.333… + 20.00 × 666.3667/749.70 = 101.1102…; net 648.5898… → **648.59**; cap not binding (200,000 − 2,054.56). Customer runs `accept_income_loss_settlement_ab094655("4634294e-1189-403c-9f68-346b4ba692f1", 648.59)`. Opening-world contrast 486.37.
- No exact half-cent tie in any scored figure.

### factor_weight (r2)

| computation | factor | tier | value under its baseline | weight |
| --- | --- | --- | --- | --- |
| property 1,499.07 | depreciation P | 13-36 → 20 % | 1,918.07 | bears |
| | condition P (listing) | most recent review 2026-10-01 warning → 85 % | 1,794.80 | bears |
| | escalation P | 12 days → 95 % | 1,587.24 | bears |
| | deductible factor P (multi-source, host) | Professional Host ∧ Entire Home → 1.5 | 1,539.24 | bears |
| | recovery sharing M | Plus → proportional | 1,494.60 | bears |
| pet 555.49 | depreciation P | 37-60 → 40 % | 1,000.06 | bears |
| | pet-fee P (listing) | 75.00 → 90 % | 629.44 | bears |
| | condition P (listing) | warning → 90 % | 629.44 | bears |
| | escalation P | 12 days → 95 % | 590.51 | bears |
| | recovery sharing M | Plus → proportional | 551.13 | bears |
| income 648.59 | lost-nights M (multi-source, listing) | covered ∧ 9 > 7 → ×7/9 | 862.30 | bears |
| | timing P (host) | host, 30_days_to_48_hours → 80 % | 835.57 | bears |
| | escalation P | 25 days → 85 % | 780.56 | bears |
| | new-cover P (host) | 179 days → 75 % | 897.93 | bears |
| | recovery sharing M | Plus → proportional | 646.37 | bears |

- Method tiers on this world (Premier-type / Plus / Essential-type): property 1,554.60 / 1,499.07 / 1,494.60; pet 586.13 / 555.49 / 551.13; income 666.37 / 648.59 / 646.37 — distinct in every computation (F-G1 closure shown on this world).
- Whole-baseline fall-backs: 2,456.67 / 1,331.67 / 1,786.67 — definite, each ≠ gold.
- Near-misses as round 1. Surviving counts: property 4P+1M, pet 4P+1M, income 3P+2M. Multi-source ✓; cross-difficulty ✓.

### findings (r2, pre-reveal)

- F-G1 consequence for task 1: closed.
- O-L3/O-L4 (condition and pet-fee shares): see `_difficulty.md` § revision_2 › factor_ladders. O-L4 closed; O-L3 kept as a softened observation. In this world the 2026-07-01 review is also a warning, so the post-stay reading still gives no second answer.
- O-T1-1 unchanged. No new defect found pre-reveal.

### source_gt_comparison (r2)

- Reveal: 2026-10-07T21:37:59Z, after both round-2 derivations were frozen (task_1.md sha256 e58b97c8…bfbc at 21:37:54Z). Round-2 `tasks/1.json` read; worklog.md not read.

| item | blind r2 | GT r2 | same? |
| --- | --- | --- | --- |
| need / authorisation / identity / reads | as round 1 | steps 0-12 as round 1 | same |
| property | 1,499.07 | 1499.07 (step 14) | same |
| pet | 555.49 | 555.49 (step 16) | same |
| income | 648.59 | 648.59 (step 18) | same |
| order / owners | property, pet (either) → income (user) | 14 → 16 → 18 | same |
| terminal state | three reimbursement rows | same | same |

- prerequisite_closure value-by-value: both edges (value_input, in_stay_settled, state, verbatim policy_source) = mine; skipped-edge figures 567.48 (one) and 486.37 (both) = mine; flips-to-true 648.59 = mine.
- factor_sensitivity figure-by-figure — property 1,918.07 / 1,794.80 / 1,587.24 / 1,539.24 / 1,494.60, baseline 2,456.67; pet 1,000.06 / 629.44 / 629.44 / 590.51 / 551.13, baseline 1,331.67; income 862.30 / 835.57 / 780.56 / 897.93 / 646.37, baseline 1,786.67 — all equal to mine.
- Closest alternatives excluded: made-whole (Premier-type) offsets 1,554.60 / 586.13 / 666.37 (the round-1 figures) — the plan is HostCover Plus, whose tier is proportional sharing; insurer-first offsets 1,494.60 / 551.13 / 646.37 — that tier is Essential.

Round-2 verdict by relationship: policy self-consistency PASS; problem tree PASS; factors PASS (F-G1 closed; property and pet each have one surviving method factor, income two); unique solution PASS.

**Task 1 revision_2 verdict: PASS.**

### findings (r2, post-reveal)

- No new defect; no regression (world and persona unchanged; the changed quantities are exactly the recovery-sharing offsets).
- Observations carried: O-T1-1, O-L1, O-L2, O-L3 (softened), O-RC1-3, O-R2-1, O-R2-2.
