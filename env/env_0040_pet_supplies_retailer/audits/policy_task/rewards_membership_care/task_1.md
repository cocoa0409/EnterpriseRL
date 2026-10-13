# Policy-task audit — rewards_membership_care / task 1

## source_derivation_frozen

- Freeze time: 2026-10-06T06:08:51Z (file write time; revision 0). Auditor: independent erl-task-policy-audit agent.
- Inputs and hashes: masked view `/tmp/e40views/policy_task/rewards_membership_care/task_1.view.json` sha256 f9a0d36fb6f6f86398bde8f3a79f2bf9ba7770f6d1a1217043c13c82224e0a95 (frozen_time, user_scenario, initial_state only); member.extended.yaml b9b17c2a…8a33; task_tools.py 656afc4d…df97c; blueprint/ of this scenario.
- Masked and unread at freeze: `tasks/rewards_membership_care/tasks/0.json` and `1.json` in full, worklog.md.
- contamination_disclosure: the gate snapshot seen before deriving prints per-task structural counts (replay "acts 20", solvability "4 10 30", grounding "2 4 4 10"); no value, argument, tier or edge. Task 0's derivation was frozen to disk before this one but no GT of task 0 had been revealed. Blind audit considered valid.
- frozen_time 2026-10-08 (collection / reissue / change date = 2026-10-08). No row of this world lies on a window boundary.

### policy_self_consistency (this task only)

- Charter-global conclusions cited, not restated: `_difficulty.md` § policy_conflict_scan, § rule_compute_equivalence, § action_binding_and_uuids, § prerequisite_graph, § prerequisite_sentences, § override_declarations, § factor_ladders, findings F-3, F-4, observations O-3, O-8, O-9.
- Handling times: P4 on the opening world; P5 on opening + P4 (status active, new fee charge 2026-10-08, term 2026-09-15 – 2027-09-14); P6 on opening + P4 + P5 (reissue row); P7 on opening + P4 + P5 + P6 (reversal row of 84.99 dated 2026-09-30).
- Real-world waits: none. The overdue fee is collected now with the card on file (persona: "go ahead and charge the card on file, the one ending in 4127"; customers.card_last4 4127); return and refund are completed rows (order_events b21299b6… order_return_refund 2026-09-30; order_return_requests status refunded).
- Base eligibilities: P4 within base grace — declined entry bf86a995… 2026-09-22 (= went past due; 2026-09-15 + fee_retry_days 7), 16 days ≤ past_due_grace_days 30. P5 base `certificate_status` (active after P4), dedup (no reissue row exists). P6 balance floor (845 available).
- O-3 has no consequence here: one certificate valid on the order date, one order refund, one order line with an earning in the reversal object.
- O-8 (base "same term dates") has no scored consequence: the record after P4 carries the term 2026-09-15 – 2027-09-14 that P7 reads.
- Consequence of F-3 on this task: `order_evt_rewards` ("A cancelled, refunded or credited line reverses the points it earned in proportion.") on line 659708f4… gives 1019 × 84.99/84.99 = 1019, floored at the balance by base `member_evt_points_reverse` → **845**; P6 gives **224**. P7's input (the reversal's 84.99 of spend) is the same under both.
- Consequence of F-4 on this task: a first Premier enrollment makes 1500 enrollment points due under base `member_enrollment_and_trials` (precedent cdc8b20a… enrollment 1000 on 2024-09-15 with the Plus Annual purchase); no tool books it; no scored parameter changes.

### problem_chain

Root: move up to Tailwise Plus Premier Annual today, quote first, customer completes it at hand-over → P7 (`upgrade_plus_tier_d51b9d82`, owner=user).

P7's sentences and the raw DB at frozen_time:
1. "The upgrade charge is fixed only after every billing period the membership has started carries a charged membership fee." Started periods 2024-09-15 (charge 895eacba…), 2025-09-15 (charge 8053b876…), **2026-09-15: only a declined entry bf86a995…**, no member_fee_charge → **unmet**. The rule that collects a fee for a started, declined period is P4 ("a care agent collects the overdue fee for the billing period whose fee was declined").
2. "The upgrade charge is not fixed until every order line refunded in the last 12 months carries its points reversal on the rewards ledger." Refund b21299b6… 2026-09-30 of line 659708f4… (cat tree); no member_points_reverse row exists on the ledger → **unmet**. Rule that books it: P6.

P6's sentence: "Points on a returned order line are taken back only after the rewards ledger carries the reissue of every certificate used on that order." Line 659708f4… carries certificate_applied_usd 5.00; the only certificate usable on 2026-08-20 is dffb1bfc… (issued 2026-08-18, last usable day 2026-10-01; the others expired 2026-01-03, 03-26, 06-18); no member_certificate_reissue row → **unmet**. Rule that reissues it: P5.

P5's sentence: "A certificate used on a returned order is not reissued until the membership has left the past-due status." member_memberships 4c030b6b… status **past_due** → **unmet**. Leaving past_due by an agent write = P4.

P4: prerequisite []; eligibility met (within grace).

Derived tree: nodes {P4, P5, P6, P7}; edges P7←P4 value_input (term_fee and fee count), P7←P6 value_input (net_spend_12m), P6←P5 state_gate, P5←P4 state_gate; n = 3 prerequisite problems, 2 value_input edges (≥ max(n − 1, 1) = 2); acyclic; unique topological order P4 → P5 → P6 → P7 (P5 needs P4, P6 needs P5); one customer write (P7). Isomorphic to the declared graph. Every edge's state is false at frozen_time (rows above).

Load-bearing runs:
- skip P4 → P7 reads latest fee 59.00 charged 2025-09-15 (= its period start, more than 30 days ago) → standard credit on term 2025-09-15 – 2026-09-14 ending before the change date → credit 0; fees in 36 months 2 → rate 0.05 → (119 − 0) × 0.95 − 27 = **86.05** vs 42.51 — bears weight. P5 is barred by base `certificate_status` while past due — the state gate bears weight as a gate.
- skip P6 → net_spend_12m 1541.35 ≥ 1500 → Premier spend allowance 12 → **36.51** vs 42.51 — bears weight.
- skip P5 → P6 is barred by its own sentence (state gate); P6's value does not read the reissue row.
- Parallel edges: P4's two out-edges (P5, P7) and P7's two in-edges (P4, P6) are ordered by the chain P4 → P5 → P6, so no second order exists; P6's tier-1 test ("no membership fee charged from that entry's date through the refund date") is unaffected by P4's fee dated 2026-10-08.
- Tools judge nothing (task_tools.py 172–367).

Verdict: PASS.

### task_independent_derivation

Need/authorisation/timing (persona): upgrade to Premier today; quote first; "you will do the move yourself when the agent hands it over"; authorises charging the card for a membership payment and sorting the certificate/points of the returned cat tree if the agent raises them; never raises them herself. Closes at the upgrade. Identity: phone 5125550463 to find; email + zip (or card 4127) to verify.

Object: membership 4c030b6b-fa05-47b6-8b6c-063aa91a2a99 (Tailwise Plus Annual, past_due, enrolled 2019-06-02 → 88 months).

1. P4 `reinstate_plus_tier_c2894e52` (agent), opening world, membership_fee_usd 59.00.
   - past-due days 2026-09-22 → 2026-10-08 = 16 > 14 → 59 × (365 − 16)/365 = 56.413699.
   - renewal rate: fee charges after 2023-10-08: 2024-09-15, 2025-09-15 = 2 ≥ 2 and 88 ≥ 60 → **0.10** (near-miss: the declined entry is not a charge).
   - first-decline courtesy: declined entries in 24 months = 1 → **2.00**.
   - Autoship courtesy: charges after 2026-07-08: 07-23, 08-20, 09-17 = 3 → **2.00** (near-miss 06-25).
   - salon courtesy: pass d4e7126f… active, latest visit 2026-09-05, 33 days ≤ 60 → **2.00**.
   - spend courtesy: net_spend_12m after 2025-10-08 = 13 Autoship earnings × 61.74 (802.62) + groom 246.24 + orders 186.43 + 221.07 + 84.99 = **1541.35** (no reversal yet) ≥ 1500 → **3.00** (near-miss: 2025-09-18 earning outside 12 months).
   - 56.413699 × 0.90 = 50.772329; − 9.00 = 41.772329 → **overdue_fee_usd 41.77**; declined_event_id bf86a995-7342-444d-bdb5-2436892562d6.
   - Effect: fee charge 41.77 dated 2026-10-08, billing_period_start 2026-09-15; status active; term 2026-09-15 – 2027-09-14; next billing 2027-09-15.
2. P5 `reissue_returned_certificate_0ad7eee8` (agent), after P4, tier Plus Annual (validity 45, value 5.00).
   - method: last usable day 2026-10-01 < 2026-10-08 and ≥ refund 2026-09-30 → 45 + 7 = **52**.
   - fault: reason damaged, refund 8 days before reissue (> 7) → **10**.
   - tenure: paid tier and 88 ≥ 60 → **6**.
   - redeemer: certificates issued after 2025-10-08: 2025-11-20, 2026-02-10, 2026-05-05, 2026-08-18 = 4 → **6**.
   - Autoship: 3 in three months → **4**.
   - **validity_days 78**; original_event_id dffb1bfc-7907-4261-b4cc-4557c669d878; certificate_value_usd 5.00 (expires 2026-12-24).
3. P6 `reverse_refund_points_2db3868c` (agent), after P5.
   - line 659708f4…: earned 1019 on 84.99 (b6d3b2b8…, 2026-08-20); refunded 84.99 on 2026-09-30; standard 1019.
   - method: refund 2026-09-30 on/after latest declined entry 2026-09-22, no fee charged 2026-09-22 … 2026-09-30 (P4's charge is 2026-10-08) → ⌊84.99 × 8⌋ = ⌊679.92⌋ = **679**.
   - fault share: damaged, earning → refund 41 days ≤ 45 → 0.5 → ⌊339.5⌋ = **339**.
   - allowances: tenure paid & 88 ≥ 60 → 40; spend 1541.35 ≥ 1500 → 30; age 41 > 30 → 20; Autoship charges after 2026-04-08 (04-30 … 09-17) = 6 → 25 (near-miss 04-02).
   - 339 − 115 = 224; caps 1019 (line) and 845 (balance) → **points 224**; source_category order, source_event_id 659708f4-56a3-49b9-9995-fc3c1cfd342a, refund_date 2026-09-30, refunded_spend_usd 84.99.
4. P7 `upgrade_plus_tier_d51b9d82` (owner **user**, handed over), after P6.
   - latest fee 41.77 charged 2026-10-08 after its period's first day 2026-09-15 → tier 1: 41.77 × unused 342 / (2026-10-08 … 2027-09-14 = 342) = **41.77**.
   - rate: fee charges after 2023-10-08 = 3 (incl. P4's) and 88 ≥ 60 → **0.10**.
   - spend: 1541.35 − 84.99 = **1456.36** ∈ [800, 1500) → **6.00**; salon: 33 days → **10.00**; Autoship six months 6 → **8.00**; redeemer 4 certificates issued → **3.00** (the reissue row is a reissue, not an issue; counting it gives 5, same tier).
   - (119 − 41.77) × 0.90 = 69.507; − 27 = 42.507 → **upgrade_charge_usd 42.51**; new_tier Tailwise Plus Premier Annual; **perk_credit_usd 60.00**.
5. Terminal: status active, Premier term 2026-10-08 – 2027-10-07, fee charges 41.77 and 42.51, reissued certificate (78 days), reversal 224 (balance 845 → 621), perk credit 60.00.

Root on the opening world (contrast): latest fee 59.00 charged on its period start 2025-09-15, change date 388 days later → standard credit; term ended 2026-09-14 → unused 0 → credit 0; rate 0.05 (2 fees); spend 1541.35 → 12; → (119 × 0.95) − 33 = **80.05**. The right number is 42.51 because P7's own sentences forbid fixing the charge before P4 and P6.

No second reading found for P4, P5 or P7. P6 has the F-3 cross-category reading (845).

### factor_weight

P4 (scored 41.77; baseline 59.00 → **fall-back 59.00 ≠ 41.77**): past_due_adjustment (method; tier 1 >14 days; rows bf86a995) → under baseline 44.10; renewal_loyalty_rate (parameter, multi-source: fee charges 895eacba/8053b876 + enrolled_on) → 47.41; first_decline_courtesy → 43.77; autoship_courtesy (cross-difficulty autoship, 3 charges) → 43.77; salon_courtesy (multi-source, cross-difficulty groom) → 43.77; spend_courtesy → 44.77. All bear weight. Label note: tiers 1 and 2 of past_due_adjustment differ only by the constant 365/360 (O-9); on this world the 30/360 tier would give 41.74 — the tier taken is decided by the 16 days.

P5 (scored 78; baseline 45 → **fall-back 45 ≠ 78**): reissue_anchor (method; certificate dffb1bfc + refund b21299b6; cross-difficulty order) → 71; fault_extension (order) → 68; reissue_tenure → 72; redeemer_extension → 72; autoship_extension (autoship) → 74. All bear weight. Near-miss: refund 8 days vs fault_wait_days 7; shipment 2026-06-25.

P6 (scored 224; baseline: proportional 1019 capped at balance → **fall-back 845 ≠ 224**): reversal_basis (method, multi-source: declined entry, fee charges, refund row) → 394; return_fault_share (order) → 564; reversal_tenure_allowance → 264; reversal_spend_allowance → 254; reversal_age_allowance → 244; reversal_autoship_allowance (autoship) → 249. All bear weight. Near-miss: shipment 2026-04-02.

P7 (scored 42.51; baseline: 119 − 41.77 × 342/365 = 79.86 → **fall-back 79.86 ≠ 42.51**): unused_term_credit (method) → 44.88; premier_loyalty_rate (multi-source) → 50.23; premier_spend_allowance → 48.51; premier_salon_allowance (groom) → 52.51; premier_autoship_allowance (autoship) → 50.51; premier_redeemer_allowance → 45.51. All bear weight. Near-misses: earning 2025-09-18 (outside 12 months), declined entry vs fee count.

Task level: multi-source ≥ 1, cross-difficulty ≥ 1 with seeded autoship/groom/order rows; no outcome stamp. Each computation keeps ≥ 2 parameter and 1 method factor.

## findings

- **T1-1 SOURCE-POLICY RED (cross-category) — P6's reversal vs `order_evt_rewards`.** Consequence of `_difficulty.md` F-3: the order base clause fixes the reversal of line 659708f4… at 1019 in proportion, floored at the 845 balance (base `member_evt_points_reverse`), against P6's 224. P6 is the more specific rule (it names the missing-reversal case), so this is reported on the strength of the undeclared conflict rather than as an even split. Affected: P6 points; blueprint/products/order.yaml `order_evt_rewards`.
- Observations: F-4 (1500 Premier enrollment points due under base, no tool); the persona carries conditional lines that name the hidden steps ("a membership payment has to be settled before the move", "the cat tree you sent back last month, such as a reward certificate or the points from that order") — passive only, but they pre-describe the prerequisites to the simulator; O-9 on past_due_adjustment / reversal_basis tiers.
- Problem tree, factor weight and unique solution for P4, P5, P7: PASS.

## source_gt_comparison

Reveal time: 2026-10-06T06:09Z, after both task derivations were frozen on disk. Fields read: design_rationale, evaluation_criteria, computations, prerequisite_closure, charter_scope, required_documents.

| item | frozen derivation | GT | same? |
|---|---|---|---|
| need / authorisation / timing | upgrade to Premier today, quote first, customer completes; agent charges card / fixes certificate and points on consent | same | same |
| read set | membership, member ledger, orders/events/RMA, autoship subs/events, groom pass/events, pets | steps 0–11 same set | same |
| now / wait / refuse | act now (grace ends 2026-10-22) | same | same |
| P4 | declined bf86a995…, **41.77** | bf86a995…, 41.77 | same |
| P5 | original dffb1bfc…, 5.00, **78** | identical | same |
| P6 | order, 659708f4…, 2026-09-30, 84.99, **224** | identical | same |
| P7 | Premier, **42.51**, perk **60.00**, owner user | identical | same |
| order | P4 → P5 → P6 → P7 | steps 13 → 15 → 17 → 19 | same |
| charter_scope | {P4, P5, P6, P7} | same + four tools | same |

Problem tree vs `prerequisite_closure`: root, four edges (kinds, gates, forms, sentences, conditions, resolved_by) and resolution_order identical to mine. why_false values: period 2026-09-15 declined with no charge / refund 2026-09-30 without reversal / no reissue of dffb1bfc… / status past_due — each checked against initial_state and true at frozen_time. Skipped effects: P7←P4 86.05 (mine 86.05), P7←P6 36.51 (mine 36.51), the two state gates as terminal-state differences — consistent with mine.

Factor weight vs `computations`: P4 41.77 / 59.0 / 44.1, 47.41, 43.77, 43.77, 43.77, 44.77 — all = mine. P5 78 / 45 / 71, 68, 72, 72, 74 — all = mine. P6 224 / 845 / 394, 564, 264, 254, 244, 249 — all = mine. P7 42.51 / 79.86 / 44.88, 50.23, 48.51, 52.51, 50.51, 45.51 — all = mine.

Closest alternative candidates and exclusion:
- P6 proportional reversal under `order_evt_rewards` (845): GT's own tracing records "standard reversal would be 1019"; GT excludes it only by preferring the member policy — no declared override of the order clause exists (T1-1 stands).
- P7 with the 30/360 tier for P4 (41.74 → different credit): excluded by the rule (16 > 14 days).
- P7 counting the reissue row as a certificate issued (5): same tier; no effect.

Verdicts for task 1:
- Policy self-consistency: **SOURCE-POLICY RED** (cross-category, T1-1 via `_difficulty.md` F-3; scored P6 224 vs 845).
- Problem tree holds: PASS.
- Factors bear weight: PASS (every factor bears weight against an honest baseline; each computation keeps ≥ 2 parameter and ≥ 1 method factor; O-9 recorded).
- Unique solution: PASS for P4, P5, P7 and the write order; P6's value carries the T1-1 second reading (recorded under SOURCE-POLICY, not double-counted).

## revision_2

### source_derivation_frozen (revision 2)

- Frozen before the round-2 tasks/1.json was opened. Inputs: `task_1.r2.view.json` sha256 2c7291036ff30f5580f6be0570428d1b9a20254b2e39047bb229f8a4b53663ea; charter/tool hashes as in `_difficulty.md` § revision_2.
- contamination_disclosure: round-1 GT read in revision 0 after its freeze; every figure below is recomputed on the round-2 world.
- Round-2 world differences:
  - The cat-tree line now carries its reversal on the ledger (45df7237…, 2026-09-30, 1019 points, 84.99).
  - A new cancelled grooming pass c25d4608… (Pepper, Full Groom Pass 4-Visit, 239.40, bought 2026-07-15, earning a93c6d42… 2872 points on 239.40; one visit 2026-08-05; refund d0a0c09d… 2026-09-28 of 154.40 removing 3 visits) has **no reversal**.
  - Order 818a5ecb line 3 and its earning have been removed.
  - The persona's conditional line is now generic ("If the agent tells you that something on your membership has to be paid or sorted out before the move …"), and the hand-over includes "perk credit and welcome points figures".

### problem_chain (r2)

Root P7 (upgrade, owner=user). Its sentences on the raw DB at 2026-10-08:
1. "every billing period the membership has started carries a charged membership fee": period 2026-09-15 has only declined entry bf86a995 → **unmet** → P4.
2. "every purchase refunded in the last 12 months carries its points reversal": the order refund b21299b6 has reversal 45df7237 (met); the grooming-pass refund d0a0c09d has none → **unmet** → P6 (the only rule that books a pass-refund reversal).
3. "a reissue of every certificate used on an order returned in the last 12 months": certificate dffb1bfc (the only one usable on 2026-08-20) has no reissue → **unmet** → P5.
- P5's sentence: status past_due → **unmet** → P4. P4 and P6 have no prerequisites.

Derived tree: P7 ← P4, P7 ← P6, P7 ← P5 (all value_input); P5 ← P4 (state_gate). n = 3 prerequisite problems with 3 value_input edges (≥ 2); acyclic; customer write P7.
- Order: P4 before P5; P6 is free relative to P4/P5. None of P4, P5 or P6 reads another's write: P6's tier-1 test sees P4's fee dated 2026-10-08, outside 2026-09-22 … 2026-09-28; P4 counts earnings, not reversals; P5 counts issues, not reversals. Every legal order gives the same values and terminal state, so there is no parallel-edge ambiguity.
- Load-bearing runs: skip P4 → 86.05; skip P6 → 36.51; skip P5 → 44.01 (redeemer 1.5 instead of 3.0). Each differs from 42.51. P5's gate on P4 holds by base `certificate_status`.
- Tools judge nothing. Verdict: PASS.

### task_independent_derivation (r2)

1. P4 reinstate (opening):
   - 59 × 349/365 = 56.413699; × 0.90 (2 fees in 36 months, 88 months enrolled).
   - Courtesies: first-decline 2.00; Autoship 2.00 (3 shipments); salon 2.00 (visit 2026-09-05, 33 days); activity 3.00 (20 earning entries after 2025-10-08: 13 Autoship, 2 grooming, 5 order; ≥ 15).
   - → **41.77**, declined_event_id bf86a995-7342-444d-bdb5-2436892562d6.
2. P5 reissue (after P4):
   - 45 + 7 (last usable day 2026-10-01, before today, on/after the refund 2026-09-30) + fault 10 (damaged, 8 days) + tenure 6 + redeemer 6 (4 issued in 12 months) + Autoship 4 → **78**.
   - original_event_id dffb1bfc-7907-4261-b4cc-4557c669d878, certificate_value_usd 5.00.
3. P6 reverse (pass c25d4608-32aa-41b4-85d9-0f2edc8a4164):
   - Standard reversal ⌊2872 × 154.40 / 239.40⌋ = 1852.
   - Method: refund 2026-09-28 is on/after declined entry 2026-09-22 with no fee charged 09-22 … 09-28 → ⌊154.40 × 8⌋ = 1235.
   - Usage share: visits used 4 − 3 = 1 → 0.75 → ⌊926.25⌋ = 926.
   - Allowances: tenure 40 (paid tier, 88 months); spend 30 (net 1589.67 before this reversal); age 20 (75 days); Autoship 25 (6 shipments in six months).
   - 926 − 115 = 811; caps 2872 and balance 845 → **points 811**.
   - Args: source_category groom, source_event_id c25d4608…, refund_date 2026-09-28, refunded_spend_usd 154.40.
4. P7 upgrade (after P4, P5, P6):
   - Credit: tier 1 (fee 41.77 charged 2026-10-08, after its period start 2026-09-15) = 41.77.
   - Rate 0.10 (3 fees in 36 months, 88 months).
   - Allowances: spend 6.00 (1674.66 − 84.99 − 154.40 = 1435.27); salon 10.00; Autoship 8.00; redeemer 3.00 (4 issued + 1 reissued = 5).
   - (119 − 41.77) × 0.9 − 27 = 42.507 → **42.51**; perk_credit_usd **60.00**.
   - **enrollment_bonus_points 1500** (first enrollment in Premier; the ledger's only enrollment bonus is the 1000 for Plus Annual on 2024-09-15). Residual reading point: whether an Annual → Premier *upgrade* is an "enrollment" of the Premier tier. The base sentence ("The enrollment_bonus_points of the tier joined are posted once, on the first enrollment of that tier"), the tool docstring ("the enrollment bonus posted with this move … 0 when no enrollment bonus is due") and P2's "Enrollment bonuses post with the enrollment that earns them" read most naturally as 1500. The base event map, however, triggers the enrollment bonus only on `member_enroll` (membership creation). Recorded as observation T1-O2, pending the reveal.

### factor_weight (r2)

- P4 (41.77; fall-back 59.00): 44.10 / 47.41 / 43.77 / 43.77 / 43.77 / activity 44.77. All bear weight. Near-misses: earning 2025-09-18 (outside 12 months), shipment 2026-06-25.
- P5 (78; fall-back 45): 71 / 68 / 72 / 72 / 74. All bear weight.
- P6 (811; fall-back 1852 capped at the balance → 845): basis → 845; usage share → 845; tenure → 845 (851 capped); spend → 841; age → 831; Autoship → 836. All differ from 811. Near-misses: the active pass's visits (not on the cancelled pass); shipment 2026-04-02 outside six months.
- P7 (42.51; fall-back 79.86): 44.88 / 50.23 / 48.51 / 52.51 / 50.51 / 45.51. All bear weight.
- Minimums met; seeded cross-difficulty rows present (groom passes/events including the refund, order events, Autoship events).

### status of round-1 items for this task (pre-reveal)

- T1-1 SOURCE-POLICY (order cross-category): **closed**. The order-line reversal is seeded consistently with `order_evt_rewards`, and P6 now governs pass refunds, which no sibling clause covers.
- Persona-hint observation: closed. F-4: closed (1500, see T1-O2). O-8: closed.
- New: O-12 (open sentence vs closed condition on P7 ← P6) has no consequence here, because the order refund already carries its reversal.

### source_gt_comparison (revision 2)

Revealed at 2026-10-06T09:50:22Z, after both revision-2 derivations were on disk.

| item | revision-2 derivation | round-2 GT | same? |
|---|---|---|---|
| P4 | bf86a995…, 41.77 | identical | same |
| P5 | dffb1bfc…, 5.00, 78 | identical | same |
| P6 | groom, c25d4608…, 2026-09-28, 154.40, 811 | identical | same |
| P7 | Premier, 42.51, perk 60.00, enrollment bonus 1500, user | identical | same |
| order | P4 → P5 → P6 → P7 (P6 free relative to P4/P5, same values) | 13 → 15 → 17 → 19 | same (the GT order is one of the equivalent legal orders) |
| scope | {P4, P5, P6, P7} | same | same |

- Tree vs `prerequisite_closure`: four edges with kinds identical to mine, and why_false values verified against initial_state (period 2026-09-15 uncharged; pass refund without reversal; certificate dffb1bfc without reissue; past_due). Skipped effects 86.05 / 36.51 / 44.01 / status gate equal mine. The closure's `resolution_order` lists P5 before P6. The charter does not require that order (no edge between P5 and P6), and both orders give identical values and terminal states, so this is not a defect.
- Factors vs `computations`: P4 41.77 / 59.0 / 44.1, 47.41, 43.77, 43.77, 43.77, 44.77; P5 78 / 45 / 71, 68, 72, 72, 74; P6 811 / 845 / 845, 845, 845, 841, 831, 836; P7 42.51 / 79.86 / 44.88, 50.23, 48.51, 52.51, 50.51, 45.51. Every figure equals mine.
- T1-O2 (whether a Premier upgrade is an "enrollment"): GT takes 1500, the natural reading of the base sentence, the tool docstring and P2's restored clause. It stays an observation.

Verdicts (revision 2), task 1: policy self-consistency **PASS**; problem tree **PASS**; factors **PASS**; unique solution **PASS**.

Round-1 item closure: T1-1 closed · persona-hint observation closed · F-4 closed (1500) · O-8 closed. New observations O-12 and T1-O2 have no demonstrable consequence. No regression and no new RED.
