# Policy-task audit — guest_cancellations_and_refunds / task 1

## source_derivation_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), revision 1.
- Freeze time: 2026-10-07T19:22:40Z (before any task JSON of this difficulty was opened).
- Input: masked view `/tmp/erl45_views/r1/guest_cancellations_and_refunds/task_1.view.json`, sha256 `0cf409af18ba40281e0484be61fcefe6774f91ac91f0a51eede6ceb76ff1f756` (recomputed, matches); charter `8b4135a7...b202`, tools `a280571e...d82e`.
- Fields permitted: frozen_time, user_scenario, initial_state; charter, tool contracts, blueprint. Masked and unread: evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, worklog.md.
- contamination_disclosure: none.

Charter-global conclusions are cited from `env/env_0045_vacation_rental_platform/audits/policy_task/guest_cancellations_and_refunds/_difficulty.md` (hereafter `_difficulty.md`).

### policy_self_consistency (this task only)

Cited, not restated: `_difficulty.md` § policy_conflict_scan, § rule_compute_equivalence, § action_binding_and_uuids, § prerequisite_graph, § prerequisite_sentences, § override_declarations, § factor_ladders.

World (frozen_time 2026-10-07T19:30:00): guest Tomasz Brennan `053ed15b…`; target stay `45312cde-9ff8-47a3-8337-7a3c84048b55` (HQ5VD8L2XP): Long-Term, monthly_installments, split_fee, standard, request_to_book, CO-DENVER, booked 2026-10-05T21:14, check_in 2026-10-07, check_out 2026-12-06, nights 60, nightly_subtotal 6480.00, cleaning 240.00, no pet / extra fees, guest_service_fee 806.40, occupancy_tax 0.00, total 7526.40, status checked_in. Ledger on it: two stay_payment_failed rows for installment 1, 3857.60 each (attempt 1 2026-10-06T19:02:30, attempt 2 2026-10-07T07:02:30); no collection. Request 0ce103b2: travel_issue, approved, misrepresented, discovered 14:40, submitted 17:45, decided 18:20 on 2026-10-07. Rewards: Rewards Platinum, active (priority_support_line true, dedicated_concierge false); tier_upgrade bonus 50.00 posted 2026-10-07 (Platinum reached today; earlier 10.00 bonus 2025-04-15 = Silver); credits earned 2025-04-16 (24.41) and 2026-06-16 (14.51); 40.00 redeemed on this stay 2026-10-05; none reinstated.
Seed consistency: 3857.60 = 30 x 108.00 + 240 = 3480.00, + 12% 417.60, - 40 credits — the scheduled installment 1 computed with no Rewards courtesy (the guest was Silver, no priority line, on 2026-10-06). Other stay 86dd9894 (monthly, 35 nights): 3137.12 and 505.12 reproduce exactly at 12% with no courtesy.

Handling time (check 4): installment 1 is evaluated on the opening world; the travel nightly refund after installment 1 is on the ledger; the travel SF refund after the nightly refund. No later write computed early.

No real-world waits (check 5): grace period: first failed attempt 2026-10-06T19:02:30, 48 h boundary 2026-10-08T19:02:30, elapsed 24 h 27 min -> still inside; the guest pays now (persona authorises). The travel issue is already approved on record (no back-office wait); reported 3 h after discovery (<= 72). Payout: no release row; earliest release 2026-10-08 00:00 + 24 h -> before_payout_release is a present fact.

Charter-global defects bearing on this task — consequences demonstrated here:

- **F-1 (SOURCE-POLICY RED) on this task.** Base `stay_evt_payment_schedule`, not overwritten (`overwrite: []` on `stay_ext_first_installment_payment`): installment 1 of a monthly stay "covers the first installment_nights nights", "the cleaning, pet and extra-guest fees are collected with installment 1, and each installment carries the guest service fee and occupancy tax attributable to the amounts it collects"; with `stay_booking_terms` (12.00 on Long-Term) and `rewards_evt_redemption` (credits apply to installment 1): Reading A = 3480.00 + 417.60 + 0 - 40.00 = **3857.60** — the very amount the stay's own two failed collection rows record for installment 1. Reading B (extended courtesy, Platinum priority line, 50% of the fee spared): 3480.00 + 208.80 - 40.00 = **3648.80**. Two defensible amounts for the user's write `pay_first_installment_26275b3d`; the seeded failed rows give Reading A record support (they predate today's tier upgrade, which the KB reader must infer from a bonus row to explain the gap).
- `_difficulty.md` F-4 (travel first-night tier 2) is a structural defect of a factor this task's nightly computation declares; this world sits on tier 1 (submitted on the check-in date), so it does not move this task's numbers.

### problem_chain

Walked from the root's rule:

- Root (need: "Roamhaven's own service fee back for a place that is not what Roamhaven advertised"): `stay_ext_travel_issue_service_fee_refund`, write `refund_travel_service_fee_041715de`, agent.
- Its rule: "The service-fee refund of a travel issue is fixed only after the stay's ledger carries the nightly refund of that travel issue." Ledger of 45312cde has no refund row -> false at opening.
- Who books a travel-issue nightly refund: `stay_ext_travel_issue_nightly_refund` (its rule: "the host-funded nightly part of the travel-issue refund is refunded"). Its rule: "The nightly refund of a travel issue is not fixed until the stay's ledger carries the collection of every installment whose first night has arrived." Installment 1's first night is 2026-10-07 (today); the ledger has only failed rows for installment 1 -> false at opening.
- Who books a collection of installment 1 on a live stay: `stay_ext_first_installment_payment` ("the guest pays installment 1 from their own payment method and it is recorded as installment 1 of the stay"), owner user. Its rule carries no prerequisite sentence -> leaf.

Derived tree: root travel SF <- travel nightly (value_input, via the nightly refund on the ledger) <- first installment (value_input, via the count of collected installments). n = 2, value_input edges 2 >= 1; one owner=user write; acyclic; isomorphic to the declared `prerequisite` fields. Topological order: first installment (user) -> travel nightly (agent) -> travel SF (agent).

Load-bearing runs: skip installment 1 -> collected installments 0 -> covered affected nights 0 -> nightly refund 0.00 (no row) -> SF = RND((0 + 240 + 54) x 0.12 x 0.99468537) = **35.09**; skip nightly -> SF **35.09** (vs 289.62). Both edges bear weight.

No parallel edges. Tools judge no prerequisite (`_difficulty.md` § action_binding_and_uuids).

Persona: raises only the root; mentions no installment, no nightly refund. Conditional, passive lines: "If the agent tells you a payment on this reservation was declined and has to be made before anything else, you say you'll pay it right away ... make it yourself with exactly the reservation and amount the agent gives you"; "If the agent says Roamhaven has other entries to put through on the reservation, you tell them to go ahead." Background "you switched banks last week" explains the decline without naming the prerequisite. Closes on "the service fee refund has been issued" = the last write. "Your host, Lauren, apologised and said she would sort things out on her end" is a distractor with no policy content (the nightly refund is booked by Roamhaven, funded by host); observation. PASS on persona boundary.

### task_independent_derivation

Act now. Identity: phone 3035551274, DOB 1979-11-08. Object: stay 45312cde, request 0ce103b2.

Common: night price RND(6480/60) = 108.00; card share (40.00 redeemed, none reinstated) = 1 - 40/7526.40 = 0.99468537.

1. **Installment 1** (`pay_first_installment_26275b3d`, owner user, handed to the guest; opening world): coverage (Long-Term, monthly) = 30 x 108.00 + 240.00 = 3480.00; fee rate 12.00 (split-fee Long-Term); courtesy (Platinum: priority line, no concierge) 50% -> fee RND(3480 x 0.12 x 0.50) = 208.80; tax: 60 >= CO-DENVER exempt minimum 30 -> 0; credits outstanding 40.00. Amount = **3648.80** (Reading B; Reading A 3857.60 per F-1).
2. **Travel nightly refund** (`refund_travel_nightly_d238de09`, agent; after 1): affected nights from 2026-10-07 (submitted on the check-in date) to 12-05 = 60; severity misrepresented 50; loyalty: 2 credit earnings within 24 months (2025-04-16, 2026-06-16) -> +10; tier uplift (priority, no concierge) +5 -> share 65; coverage (monthly, 1 collected installment) = min(30, 60) - 0 = 30 nights; first affected night (submitted on the check-in date) 100%; gross = 108.00 x (100 + 29 x 65)/100 = 2143.80; card share -> RND(2143.80 x 0.99468537) = **2132.41**. Args: charge_component nightly, refund_reason travel_issue, request_id 0ce103b2-4c5d-49e5-b9da-052ffaf6f8b8, funded_by host, refund_stage before_payout_release. Opening-world value: 0.00 (no collected installment).
3. **Travel SF refund** (`refund_travel_service_fee_041715de`, agent; after 2): rate 12.00; fee base (misrepresented) = nightly travel refund 2132.41 + whole cleaning fee 240.00 = 2372.41; arrival courtesy (submitted on the check-in date, priority) 50% of 108.00 = 54.00; card share. Amount = RND((2372.41 + 54.00) x 0.12 x 0.99468537) = **289.62**. Args: guest_service_fee, travel_issue, 0ce103b2-…, platform, before_payout_release. Opening-world value 35.09.

Terminal state: one stay_payment_collected row (installment 1, 3648.80) and two stay_refund_issued rows (2132.41 nightly, 289.62 guest_service_fee) on stay 45312cde. Travel refunds are never capped (`stay_agg_service_fee_refund_cap`).

Closest alternatives: (a) installment 1 = 3857.60 — not excluded (F-1); (b) severity read from the base `travel_issue_refund_pct_by_category` (misrepresented 50) — same number; (c) counting the 2026-10-07 and 2025-04-15 tier_upgrade bonus rows as earnings (-> still >= 2, same tier) — excluded by "credits ... earned on completed stays"; (d) counting the other stay 86dd9894's installment-2 collection — excluded, the rule reads "the stay's ledger"; (e) a cleaning-fee travel refund — not owed (misrepresented is not in travel_issue_cleaning_fee_categories), and the SF fee base takes the whole cleaning fee from the stay row, not from a refund.

### factor_weight

Installment 1 (3648.80): installment_one_coverage (method) 30 nights + fees vs baseline whole stay -> 7083.20; installment_one_fee_rate (parameter) 12 vs 14.20 -> 3687.08; installment_one_fee_courtesy (parameter, cross-difficulty Rewards Platinum 543c3447) 50 vs 0 -> 3857.60; installment_one_tax (method) exempt vs 15.75% -> 4196.90. Baseline alone (whole stay, 14.20%, rate tax, less credits) = **8692.64**, definite, differs. Near-miss: the 3857.60 failed-attempt rows (computed under the guest's Silver tier the day before). No outcome stamp (the tier is the membership's variant, not an outcome field). 4 factors, 2 parameter / 2 method.

Travel nightly (2132.41): severity 50 vs 100 -> 3222.78; loyalty +10 vs 0 -> 1820.87; tier uplift +5 vs 0 -> 1976.64; paid_night_scope 30 vs 60 -> 4227.21; first_night 100 vs share 65 -> 2094.81; credit part vs 1 -> 2143.80. Baseline alone (every affected night in full) = **6480.00**. All bear weight. Near-miss: tier_upgrade bonus rows (2025-04-15, 2026-10-07) not earnings; the stay completed today (86dd9894) has no earning row yet. `travel_first_night_treatment` fails the real-ladder test charter-wide (`_difficulty.md` F-4); striking it leaves 5 factors (3 parameter / 2 method), bound still met.

Travel SF (289.62): fee pct 12 vs 14.20 -> 342.72; fee base +cleaning vs nightly only -> 260.97; courtesy 50 vs 0 -> 283.18; credit vs 1 -> 291.17. Baseline alone 14.20% x 2132.41 = **302.80**. All bear weight. Near-miss: the other stays' guest-cancellation SF refunds (not travel_issue).

Task-level: multi-source factor present (travel_fee_arrival_courtesy: submission date + Rewards tier; credit parts); cross-difficulty Rewards rows seeded (membership, earnings, redemption) — subject to `_difficulty.md` F-8.

Provisional verdict (pre-reveal): SOURCE-POLICY RED (F-1: 3857.60 vs 3648.80 for the user's write); SOURCE-FACTOR RED (F-4 on a declared factor; does not move this task's numbers); problem tree PASS; otherwise unique (3648.80, 2132.41, 289.62).

## source_gt_comparison

- Reveal time: 2026-10-07T19:24:22Z, after both task files were frozen (frozen hashes at 19:23:26Z: `_difficulty.md` 2353c5e6…3125, `task_0.md` 09486440…3a86, `task_1.md` d66ffc5c…bd2).
- Fields revealed: evaluation_criteria, computations, prerequisite_closure, charter_scope, required_documents, design_rationale, solvability_contract.

| item | blind | GT | same? |
| --- | --- | --- | --- |
| need / authorisation / timing | Roamhaven's SF back; guest pays a declined payment when told; agent may post other entries | same (request_alignment) | same |
| now / wait / refuse | act now (grace runs to 2026-10-08T19:02:30) | act now | same |
| object | stay 45312cde, request 0ce103b2 | same | same |
| installment 1 | pay_first_installment_26275b3d (user), 3648.80 | identical | same |
| travel nightly | refund_travel_nightly_d238de09, nightly, travel_issue, 0ce103b2…, host, before_payout_release, 2132.41 | identical | same |
| travel SF | refund_travel_service_fee_041715de, guest_service_fee, travel_issue, 0ce103b2…, platform, before, 289.62 | identical | same |
| order / owners | installment 1 (user) -> nightly -> SF | same | same |
| terminal state | 1 collection + 2 refunds on 45312cde | same | same |
| charter_scope | {first installment, travel nightly, travel SF} | same three policies and tools | same |

Problem tree vs `prerequisite_closure`: root stay_ext_travel_issue_service_fee_refund = mine; edge SF->nightly value_input gate travel_fee_nightly_refunds = mine; edge nightly->first installment value_input gate travel_installments_collected = mine; resolution_order [first installment, nightly, SF] = mine. Load-bearing: without installment 1 nightly 0.00 (mine 0.00) and SF 35.09 (mine 35.09); without nightly SF 35.09 (mine 35.09). Same.

Factor weight vs `computations[]` (figure against figure):
- installment 1 (3648.80 = mine): coverage 7083.20 = 7083.20; fee rate 3687.08 = 3687.08; courtesy 3857.60 = 3857.60; tax 4196.90 = 4196.90; baseline_result 8692.64 = 8692.64.
- travel nightly (2132.41): 3222.78 / 1820.87 / 1976.64 / 4227.21 / 2094.81 / 2143.80 all equal; baseline 6480.00 = 6480.00.
- travel SF (289.62): 342.72 / 260.97 / 283.18 / 291.17 all equal; baseline 302.80 = 302.80.

Closest candidate and its exclusion: installment 1 = 3857.60. GT's design_rationale treats it as a stale record (computed while the guest was Rewards Silver, before today's Platinum upgrade — verified: 10.00 Silver bonus 2025-04-15, 50.00 Platinum bonus 2026-10-07, 2026 qualifying nights 5 + 35 = 40 = Platinum `qualifying_nights_min`). That explains the record, but it does not exclude Reading A, which rests on base text and not on the record: `stay_evt_payment_schedule` "each installment carries the guest service fee ... attributable to the amounts it collects" (12% x 3480.00 = 417.60) is in force and not named in the policy's `overwrite: []`. F-1 stands.

Verification of the proof's world assertions: checked true — "The stay's ledger holds only two stay_payment_failed rows"; reported 3 h 05 min after discovery; grace boundary 2026-10-08T19:02:30; release no earlier than 2026-10-08T00:00; Platt Park stay credits post one day after check-out (`credit_posting_days_after_checkout: 1`); thirteen ledger rows; five Rewards rows as listed; the 2025 cancelled Platt Park stay carries the cited nightly and SF rows. No false assertion found.

Verdict per relationship:
- Policy self-consistency: **SOURCE-POLICY RED** (F-1, demonstrated: 3857.60 vs 3648.80 for the user's write).
- Problem tree: **PASS** (isomorphic, both edges false at opening and load-bearing, user write present, n=2 with 2 value_input edges, no tool validation, persona raises only the root).
- Factors: every declared factor bears weight against an honest baseline, baselines alone give definite numbers different from gold, near-misses present, multi-source and Rewards rows seeded. **SOURCE-FACTOR RED** only through the charter-global unreal tier of `travel_first_night_treatment` (`_difficulty.md` F-4); this world is on its tier 1 and the computation keeps 5 valid factors (3 parameter / 2 method) after striking it.
- Unique solution: equal to GT on every write, argument, owner and order, apart from F-1. PASS otherwise.

**Task 1 verdict: SOURCE-POLICY RED + SOURCE-FACTOR RED (charter-global F-4, no numeric consequence on this task).**

## findings

1. **SOURCE-POLICY RED — undeclared override on installment 1's guest service fee (F-1).**
   Symptom: two defensible amounts for `pay_first_installment_26275b3d`. Root cause: `stay_ext_first_installment_payment.rule` "Roamhaven Rewards members get a courtesy on the guest service fee of installment 1 ... spared installment_fee_courtesy_priority_pct percent of it" deviates from base `stay_evt_payment_schedule` "each installment carries the guest service fee and occupancy tax attributable to the amounts it collects" (with `stay_booking_terms` 12.00 on Long-Term); `overwrite: []`. Evidence: extended yaml; base policy text; failed collection rows `stay_transactions.1d98d346…` and `527a5aa7…` recording installment 1 at 3857.60. Consequence: Reading A 3480.00 + 417.60 - 40.00 = 3857.60; Reading B (gold) 3480.00 + 208.80 - 40.00 = 3648.80. The downstream refunds read only the count of collections, so they are the same under both readings. Affected: extended charter `stay_ext_first_installment_payment.overwrite`; scored argument `amount` of the user write. First revision.
2. **SOURCE-FACTOR RED — `travel_first_night_treatment` tier 2 outcome (F-4, charter-global).** For a no_access / uninhabitable issue reported the day after check-in the first affected night is refunded at 75 while every later one is refunded at 100. Not exercised here (tier 1, submitted on the check-in date); the computation's bound survives without it. Affected: `stay_ext_travel_issue_nightly_refund.factors[travel_first_night_treatment]`. First revision.
3. Observation — persona line "Your host, Lauren, apologised and said she would sort things out on her end" is a distractor without policy content; it does not move the solution.
4. Observation — a stay checked in today with installment 1 still declined sits at the edge of the blueprint summary's POLICY_NOT_COVERED item "a missed monthly installment on a stay already in progress"; the extended rule covers the case explicitly (`_difficulty.md` O-6).
5. Observation — `refund_travel_nightly_d238de09` and `refund_travel_service_fee_041715de` describe `stay_id` as the stay "whose pet fee is refunded" (`_difficulty.md` O-4).
6. Observation — Rewards: the guest jumped from Silver to Platinum today but only the Platinum upgrade bonus is seeded; whether reaching Gold on the same day also grants Gold's 25.00 bonus is a Rewards-charter question with no bearing on any scored value here.

## revision_2

### source_derivation_frozen (revision 2)

- Freeze time: 2026-10-07T21:12:58Z (before the round-2 task JSON was opened). Revision 1 text above is unchanged.
- Inputs: view `/tmp/erl45_views/r2/guest_cancellations_and_refunds/task_1.view.json` `0cf409af18ba40281e0484be61fcefe6774f91ac91f0a51eede6ceb76ff1f756` (identical to r1); charter `ed0b001c…14a1` (changed); tools `bbb8e9e1…b7bb` (changed). The per-task sections are re-derived because the charter changed.
- Masked and unread: evaluation_criteria, computations, prerequisite_closure, charter_scope, required_documents, design_rationale, solvability_contract, worklog.md (round 2).
- contamination_disclosure: the r1 GT of this task was revealed in revision 1 (3648.80 / 2132.41 / 289.62). The r2 figures below are recomputed from the r2 charter.

### policy_self_consistency (revision 2, this task)

- F-1 on this task: closed. `stay_ext_first_installment_payment.overwrite` now replaces the base sentence for "installment 1 of a stay paid in monthly installments … following the guest's Rewards tier active when installment 1 is collected". This is a monthly stay; the guest's active tier now is Platinum (priority line). Reading A (3857.60 at the full 12 %) is now contrary to declared text; the two declined attempts at 3857.60 are explained by the tier then in force (Silver, no priority line, until today's Platinum upgrade: 50.00 bonus 2026-10-07). Single reading 3648.80.
- F-4 on this task: closed charter-wide; this world uses tier 1 (submitted on the check-in date) anyway.
- Handling time / no wait: unchanged (grace to 2026-10-08T19:02:30; the first-installment rule now says "the stay, still confirmed or checked in, is inside the failed-payment grace period" — this stay is checked in and inside it).

### problem_chain (revision 2)

Unchanged: root travel SF <- travel nightly (value_input) <- first installment (value_input, user). Both states false at opening (two failed rows, no collection, no refund). Load-bearing: skip installment 1 -> nightly 0.00, SF 35.09; skip nightly -> SF 35.09. Persona unchanged.

### task_independent_derivation (revision 2)

1. Installment 1 (user): 30 x 108.00 + 240.00 = 3480.00; fee 12 % less 50 % (monthly, Platinum priority) = 208.80; tax 0 (60 >= 30); less 40.00 credits -> **3648.80**.
2. Travel nightly (agent, after 1): share 50 + 10 (two earnings in 24 months) + 5 (priority) = 65; 30 covered nights; first night 100 (submitted on the check-in date); gross 108.00 x (100 + 29 x 65)/100 = 2143.80; card share (credits tier 1, unchanged formula) -> **2132.41**; nightly, travel_issue, request 0ce103b2-4c5d-49e5-b9da-052ffaf6f8b8, host, before_payout_release.
3. Travel SF (agent, after 2): (2132.41 + 240.00 + 54.00) x 12 % x 0.99468537 -> **289.62**; guest_service_fee, travel_issue, 0ce103b2…, platform, before_payout_release.

### factor_weight (revision 2)

Installment 1: coverage -> 7083.20; fee rate -> 3687.08; courtesy (now "monthly and priority line", multi-source over the stay's plan and the Rewards tier) -> 3857.60; tax -> 4196.90; baseline alone 8692.64. Travel nightly: 3222.78 / 1820.87 / 1976.64 / 4227.21 / 2094.81 / 2143.80, baseline alone 6480.00; `travel_first_night_treatment` now passes the real-ladder test. Travel SF: 342.72 / 260.97 / 283.18 / 291.17, baseline alone 302.80. All bear weight; counts within bounds; Rewards rows seeded.

Provisional verdict (pre-reveal): all four relationships PASS.

### source_gt_comparison (revision 2)

- Reveal time: 2026-10-07T21:13:20Z, after both revision-2 task sections were frozen (hashes at 21:13:14Z: `_difficulty.md` 9fcce649…7445, `task_0.md` 18c3a2b1…1039, `task_1.md` 38559939…99cf).

| item | blind (r2) | GT (r2) | same? |
| --- | --- | --- | --- |
| installment 1 (user) | 3648.80 | 3648.80 | same |
| travel nightly | nightly, travel_issue, 0ce103b2…, host, before_payout_release, 2132.41 | identical | same |
| travel SF | guest_service_fee, travel_issue, 0ce103b2…, platform, before, 289.62 | identical | same |
| order | installment 1 -> nightly -> SF | same | same |
| charter_scope | {first installment, travel nightly, travel SF} | same | same |

Problem tree vs `prerequisite_closure`: root, two value_input edges, gates, resolution_order and load-bearing figures (0.00 / 35.09) identical to mine.
Factors vs `computations`: 3648.80 / baseline 8692.64 with 7083.20 / 3687.08 / 3857.60 / 4196.90; 2132.41 / baseline 6480.00 with 3222.78 / 1820.87 / 1976.64 / 4227.21 / 2094.81 / 2143.80; 289.62 / baseline 302.80 with 342.72 / 260.97 / 283.18 / 291.17 — all equal mine. Courtesy `tier_taken` now names both conditions (monthly plan and Rewards tier).

Round-1 item closure on this task:
- F-1 (SOURCE-POLICY RED): **closed** — declared overwrite scoped to monthly installment 1 and to the tier active at collection; 3857.60 is excluded by declared text, and the declined rows are explained by the earlier Silver tier (verified: 10.00 Silver bonus 2025-04-15; 50.00 Platinum bonus 2026-10-07; 2026 qualifying nights 5 + 35 = 40 = Platinum minimum).
- F-4 (SOURCE-FACTOR RED, charter-global): **closed** — tier 2 is a 75 % floor.

Regression and new-defect check: world assertions in `design_rationale` and `prerequisite_closure` re-verified true (two failed rows only; grace to 2026-10-08T19:02:30; 3 h 05 min report; credits post one day after check-out; five Rewards rows; thirteen ledger rows). No false assertion, no new defect.

Verdict per relationship (revision 2): policy self-consistency PASS; problem tree PASS; factors PASS; unique solution PASS.

**Task 1 revision_2 verdict: PASS.**

### findings (revision 2)

1. Round-1 findings 1 (F-1) and 2 (F-4): closed. Observations 3-6: 5 (tool docstring) closed by O-4; 3, 4, 6 unchanged and still observations only.

## revision_3

### source_derivation_frozen (revision 3)

- Frozen 2026-10-07T21:45:23Z, before the round-3 task JSON was opened. Earlier revisions untouched.
- Inputs: view `task_1.view.json` (r3) hash identical to revision 2; charter `ed0b001c…14a1` and tools `bbb8e9e1…b7bb` identical to revision 2. The world, the charter and the tool contracts are unchanged, so revision 2's `policy_self_consistency`, `problem_chain`, `task_independent_derivation` and `factor_weight` for this task are **carried forward by reference** (the blind solution and every figure stand as frozen in revision 2). Only the proof fields of the task JSON, which may have moved, are re-judged after the reveal.
- contamination_disclosure: round-1 and round-2 GT of this task are known from earlier revisions; the round-3 JSON is unopened at this freeze.

### source_gt_comparison (revision 3)

- Reveal time: 2026-10-07T21:45:40Z, after the revision-3 freeze.
- The file was rewritten (mtime 21:44:56Z) but its scored and proof content is unchanged from revision 2: installment 1 3648.80 (user), travel nightly 2132.41, travel SF 289.62; computations 3648.80 / 8692.64, 2132.41 / 6480.00, 289.62 / 302.80 with every factor_sensitivity figure as in revision 2; two value_input edges, order unchanged; `why_false` and the design_rationale cards re-read and still true (two failed rows; Silver -> Platinum today; two earnings in 24 months; credits post one day after check-out). No change claimed and none found; no regression.

**Task 1 revision_3 verdict: PASS.**

## revision_4

### source_derivation_frozen (revision 4)

- Frozen 2026-10-07T22:38Z, before the round-4 task JSON was opened. Earlier revisions untouched.
- Inputs: r4 view `task_1.view.json`; the only change from r3 is frozen_time -> "2026-10-07 19:30:00 MDT". Charter unchanged; tool module changed only in posted_at formatting (see `_difficulty.md` § revision_4).
- Per-task re-judgement of what the clock change could move: the handling date stays 2026-10-07 (every compute reads the date part only); the failed attempts (2026-10-06T19:02:30, 2026-10-07T07:02:30), the request times (14:40 / 17:45 / 18:20) and the handling time are all Mountain local; elapsed grace 24 h 27 min of 48 and the 3 h 05 min report window are unchanged. The booked posted_at stays "2026-10-07T…" ISO local, so later reads by date or by ledger order are unchanged. No persona line refers to the clock format.
- Therefore revision 2's per-task sections (policy_self_consistency, problem_chain, task_independent_derivation, factor_weight), as carried forward in revision 3, stand **by reference**: the blind solution and every figure are unchanged.
- contamination_disclosure: rounds 1-3 GT of this task known; round-4 JSON unopened at this freeze.

### source_gt_comparison (revision 4)

- Reveal time: 2026-10-07T22:38:20Z, after the revision-4 freeze.
- frozen_time in the JSON: "2026-10-07 19:30:00 MDT" (no ISO stamp of it left). Tool posted_at = "2026-10-07T19:30:00" (checked), unchanged from round 3.
- Scored solution unchanged and equal to my carried-forward derivation: installment 1 3648.80 (user), travel nightly 2132.41, travel SF 289.62 (arguments identical to revision 2). Computations 3648.80/8692.64, 2132.41/6480.00, 289.62/302.80 with every factor_sensitivity figure as before; prerequisite_closure unchanged (two value_input edges; 0.00 / 35.09). Grace and reporting windows unchanged in local Mountain time.
- Regressions: none. New defects: none.

Verdict per relationship (revision 4): all four PASS.

**Task 1 revision_4 verdict: PASS.**
