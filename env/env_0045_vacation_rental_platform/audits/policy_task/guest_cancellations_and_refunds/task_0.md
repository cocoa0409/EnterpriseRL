# Policy-task audit — guest_cancellations_and_refunds / task 0

## source_derivation_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), revision 1.
- Freeze time: 2026-10-07T19:21:38Z (before any task JSON of this difficulty was opened).
- Input: masked view `/tmp/erl45_views/r1/guest_cancellations_and_refunds/task_0.view.json`, sha256 `7a5232d409359320c4339c5338190181cffdeee713eed12d8a24cba47574a587` (recomputed, matches); charter `8b4135a7...b202`, tools `a280571e...d82e`.
- Fields permitted: frozen_time, user_scenario, initial_state; the charter, tool contracts, blueprint. Masked and unread: evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, worklog.md.
- contamination_disclosure: none. The brief carried no scored value; no recursive search touched `tasks/*.json`.

Charter-global conclusions are cited from `env/env_0045_vacation_rental_platform/audits/policy_task/guest_cancellations_and_refunds/_difficulty.md` (hereafter `_difficulty.md`) by heading.

### policy_self_consistency (this task only)

Cited, not restated: `_difficulty.md` § policy_conflict_scan, § rule_compute_equivalence, § action_binding_and_uuids, § prerequisite_graph, § prerequisite_sentences, § override_declarations, § factor_ladders.

World (frozen_time 2026-10-07T17:05:00): guest Nadia Petrov `28dd4981…`; target stay `79bb8aae-50c8-4104-9449-a9fc71dc0b16` (HMQ7RX42TD): Long-Term, monthly_installments, split_fee, standard rate, TX-AUSTIN, check_in 2026-10-07, check_out 2026-12-21, nights 75, guest_count 3, pet_count 1, nightly_subtotal 8160.00, cleaning 220.00, pet_fee_total 150.00, extra_guest_fee_total 600.00, guest_service_fee 1095.60, occupancy_tax 0.00, total_price 10225.60, status cancelled_by_guest, cancelled_at 2026-10-07T13:40:00. Ledger on it: installment 1 collected 3990.08 (2026-08-28), installment 0 collected 672.00 with request ffa3b72d (accepted guest_count_change 2->3). No refund rows. Rewards: Rewards Gold, active (priority_support_line true, dedicated_concierge false); 80.00 credits redeemed on this stay (2026-08-28), none reinstated. Seed consistency checked: 3990.08 = 30 x 108.80 + 220 + 150 = 3634.00, + 12% 436.08, - 80 credits; 672.00 = 600 + 12%.

Handling time (check 4): pet and extra-guest refunds are evaluated on the opening world (neither reads the other: card share is on tier 1, no reinstatement row, so the "amounts already refunded" denominator is not read); the SF refund after both are posted; the notice charge after all three (it reads none of them). No later write is computed early.

No real-world waits (check 5): every input is a seeded record (stay row, ledger, Rewards rows) or the synchronous effect of an earlier write of this task. The cancellation already happened (cancelled_at on record). Payout release: `payout_evt_release` releases no earlier than 24 h after 00:00 of check_in_date (2026-10-08 00:00); no payout row exists, so refund_stage before_payout_release is a present fact, not a wait.

Charter-global defects bearing on this task — consequences demonstrated here:

- **F-1 (SOURCE-POLICY RED) on this task.** The notice charge is "booked as the installment that covers the first unpaid notice night" (installment 2). Base `stay_evt_payment_schedule`, not overwritten on this sentence: "each installment carries the guest service fee and occupancy tax attributable to the amounts it collects"; `stay_booking_terms`: guest service fee = guest_service_fee_pct (12.00 on Long-Term) of the service-fee base. Reading A (base): the installment collects 1 night at 108.80; attributable fee 12% = 13.06; tax 0 (exempt kept) -> **121.86**. Reading B (extended, Rewards relief 50% for a Gold member): fee RND(108.80 x 0.12 x 0.50) = 6.53 -> **115.33**. Both stand on unoverwritten text that will be rendered together; the stay's own installments 1 and 0 on this very stay carried the full 12% (436.08, 72.00) although the guest was Gold at booking (tier_upgrade bonus 25.00 posted 2025-11-16), so the records side with Reading A. Two defensible scored values for the root write.

### problem_chain

Walked from the root's rule:

- Root (customer's need: "pay whatever you still owe on this stay, now and from your own card"): `stay_ext_departure_notice_charge`, write `pay_notice_charge_caff8891`, owner user.
- Its rule's prerequisite sentences: "The notice charge is not collected until the stay's ledger carries the guest-cancellation refund owed on the stay's pet fee." / "... on the stay's extra-guest fee." / "... on Roamhaven's guest service fee." At frozen_time the ledger of stay 79bb8aae has no refund row of any component (only the two collections) -> all three states false. The refunds are owed (> 0.00) as computed below.
- Who books those states: the pet-fee policy, the extra-guest-fee policy, the departure service-fee policy (by their own rules). The SF policy's own rule carries "The guest-service-fee refund on a cancellation is fixed only after the stay's ledger carries the pet-fee refund that cancellation owes." and the same for the extra-guest fee -> both false at opening.
- Pet and extra-guest rules carry no prerequisite sentence -> leaves.

Derived tree: nodes {notice (root, user), pet (agent), extra (agent), SF (agent)}; edges notice<-pet state_gate, notice<-extra state_gate, notice<-SF state_gate, SF<-pet value_input, SF<-extra value_input. n = 3 prerequisite problems, value_input edges = 2 >= max(n-1,1) = 2. One owner=user write (root). Acyclic. Isomorphic to the declared `prerequisite` fields.

Topological order: {pet, extra} (either order) -> SF -> notice (handed to the guest).

Load-bearing runs: skip pet -> SF = RND((331.78 + 54.40) x 0.12 x (1 - 80/10225.60)) = **45.98** (vs 55.33); skip extra -> SF = **15.83**; skip SF -> the root's gate is unmet and the terminal ledger lacks the SF refund row. The three state_gate edges do not change the root's amount (the notice charge reads no refund), they bear weight only as gates and as terminal rows.

Parallel edges: pet and extra both feed SF and both gate the root; neither reads the other on this world (card-share tier 1; the tier-2 denominator that would read earlier refunds is not taken — see `_difficulty.md` F-5), so either order gives the same terminal state.

Tools judge no prerequisite: `task_tools.py` bodies of all four tools only create the row (see `_difficulty.md` § action_binding_and_uuids).

Persona: raises only the root ("You are calling to pay whatever you still owe"); never names a refund. It pre-authorises agent writes and reacts passively ("if they tell you something has to be done first, you say that's fine, go ahead"). Closes when told the payment went through — which is the last write. Observation: the sentence "You are happy for the agent to take care of anything Roamhaven needs to put through on the reservation before you pay" is an attitude, not a named prerequisite; it does not steer to any specific write. PASS on persona boundary.

### task_independent_derivation

Act now (all inputs on record; the stay is cancelled; nothing waits).

Identity via `verify_customer_identity` (phone 5125551468, DOB 1986-03-14). Object: stay 79bb8aae (confirmation HMQ7RX42TD).

Common quantities: nights 75; cancel_offset = DAYS(2026-10-07, 2026-10-07) = 0 (cancellation dated on the check-in date, after check-in per persona "checked in this morning" and the lifecycle "A confirmed stay becomes checked_in on its check_in_date"); unspent nights = 75 - 0 - 1 = 74; night price RND(8160/75) = 108.80; card share (Rewards credits redeemed 80.00, none reinstated, tier 1): 1 - 80/10225.60 = 0.99217650.

Nightly refund: none due. Notice-charge overwrite: "On a stay paid in monthly installments, the nightly amounts collected pay for the stay's nights in date order, and a guest cancellation refunds the nightly price only of collected nights that fall after the notice nights." Collected nights: installment 1 covers nights 1-30 (10-07..11-05); notice nights 10-08..11-06; no collected night falls after them -> 0.00, no row. Cleaning: not refunded on or after check-in (`cleaning_fee_refund_after_check_in: false`). Occupancy tax: 0 on the stay.

1. **Pet-fee refund** (`refund_pet_fee_41a7068c`, agent; opening world): pet notice nights = after_check_in_notice_nights 30 (Long-Term); pet-refundable nights = 75 - 0 - 1 - 30 = 44; share (monthly, collections begun) = 44/75; deep-clean share (dated on the check-in date) 20%, courtesy (Gold: priority line, no concierge) 50% waived -> kept 10%; card share 0.99217650. Amount = RND(150 x 44/75 x 0.90 x 0.99217650) = **78.58**. Args: charge_component pet_fee, refund_reason guest_cancellation, request_id "" (rests on no request), funded_by host, refund_stage before_payout_release.
2. **Extra-guest-fee refund** (`refund_extra_guest_fee_b492f389`, agent; opening world): notice 30; refundable nights 44; share 44/75; linen 10% on the check-in date, courtesy 50% -> kept 5%; card share. Amount = RND(600 x 44/75 x 0.95 x 0.99217650) = **331.78**. Args: extra_guest_fee, guest_cancellation, "", host, before_payout_release.
3. **Departure SF refund** (`refund_service_fee_f4bed6e4`, agent; after 1 and 2): rate 12.00 (split-fee, Long-Term); refunded fee base (monthly, cancelled on/after check-in, collections begun) = nightly 0.00 + pet 78.58 + extra 331.78 = 410.36; arrival-night courtesy (dated on the check-in date, Gold priority) 50% of 108.80 = 54.40; card share. Amount = RND((410.36 + 54.40) x 0.12 x 0.99217650) = **55.33**. Args: guest_service_fee, guest_cancellation, "", platform, before_payout_release. On the opening world (no add-on refunds yet) it would be RND(54.40 x 0.12 x 0.9922) = 6.48; 55.33 is right because the rule fixes it "only after" the add-on refunds are on the ledger.
   Service-fee cap (`stay_agg_service_fee_refund_cap`, in force): other stays with a guest-cancellation SF refund > 0 dated 2025-10-08..2026-10-07: 9f29245e (2026-03-01) only -> 1 < 3, not capped. Near-miss: 8746ddca's SF refund of 2025-05-01 falls outside the window.
4. **Notice charge** (`pay_notice_charge_caff8891`, owner user, handed to the guest; after 1-3): notice nights 30 (Long-Term), notice_count min(30, 74) = 30; installments collected = 2 collections - 1 installment-0 row = 1 -> covered nights 30 -> paid notice nights min(30, 30 - 0 - 1) = 29; unpaid 1 (night of 2026-11-06); charged nights price 108.80; fee base (monthly, installment 1 collected) = 108.80; fee rate 12.00; Rewards relief (priority, no concierge) 50% -> fee RND(108.80 x 0.12 x 0.50) = 6.53; tax: stay 75 >= TX-AUSTIN exempt minimum 30 and nights kept 0 + 1 + 30 = 31 >= 30 -> 0. Amount = **115.33**; installment_number = the installment covering the first unpaid notice night (night 31) = **2**. The persona pays "with exactly the reservation, installment number and amount the agent gives you".
   Opening-world contrast: the root's amount does not read the prerequisites, so it is 115.33 on the opening world too.

Write sequence and owners: refund_pet_fee (agent) and refund_extra_guest_fee (agent) in either order -> refund_service_fee (agent) -> pay_notice_charge (user, handed over). Terminal state: three stay_refund_issued rows (78.58, 331.78, 55.33) and one stay_payment_collected row (installment 2, 115.33) on stay 79bb8aae.

Closest alternatives and exclusion: (a) 121.86 for the notice charge — not excluded by the charter (F-1); (b) installment_number 0 or 1 — excluded: "booked as the installment that covers the first unpaid notice night", and base defines installment 0 as an alteration increase; (c) counting the installment-0 row as a covering installment (-> 60 nights covered, unpaid 0, charge 0) — excluded by base "installment_number ... 0 for an alteration increase"; (d) nightly refund 3264.00 under base "lesser of collected" — excluded, that clause is declared superseded.

### factor_weight

Notice charge (gold-by-derivation 115.33):

| factor | label | tier taken (rows) | baseline input | scored value under baseline |
| --- | --- | --- | --- | --- |
| notice_length | parameter | Long-Term, 75 nights -> 30 (stays.nights, variant Long-Term) | 1 | 41.39 (notice 1 -> kept 2 < 30, exemption lost: tax RND((2 x 108.80 + 970 x 2/75) x 0.17) = 41.39, no unpaid night) |
| notice_night_coverage | method | monthly -> 1 installment covers 30 nights (ledger: installment 1, installment 0 excluded) | every notice night paid | 0.00 |
| notice_fee_rate | parameter | split-fee Long-Term -> 12.00 | 14.20 | 116.52 |
| notice_fee_base | method | monthly, installment 1 collected -> charged nights only | + attributable fees 12.93 | 116.10 |
| notice_tax_exemption | method | exempt and kept 31 >= 30 -> no tax | fee base x 17% = 18.50 | 133.83 |
| rewards_fee_relief | parameter (cross-difficulty: rewards) | Gold, priority line -> 50 | 0 | 121.86 |

Baseline alone (`baseline.rule`: 1 notice night, every night paid by the confirmation collection, 14.20 on charged nights + attributable fees, rate tax): unpaid 0 -> **0.00**, definite and different from 115.33. Near-miss: the installment-0 collection (alteration increase) a careless reader counts as a covering installment; nights kept 31 vs exempt minimum 30. No outcome stamp.
Structural validity: see `_difficulty.md` F-2 — on this write every customer is Long-Term monthly; notice_length, notice_night_coverage and notice_fee_rate bear weight here only against tiers/baselines no customer reaching this write can occupy (the baseline itself, "the collection at confirmation covers every night of the stay", yields 0 for every such customer). Surviving factors: notice_tax_exemption, rewards_fee_relief, and at most notice_fee_base -> fewer than 4 factors and 1 parameter. **SOURCE-FACTOR RED**.

Pet refund (78.58): pet_notice_nights 30 vs baseline 1 -> 130.37; pet_refund_share 44/75 vs baseline nightly-refunded/subtotal = 0 -> 0.00; pet_deep_clean_share 20 vs 0 -> 87.31; pet_clean_courtesy 50 vs 0 -> 69.85; pet_credit_funded_part 0.99218 vs 1 -> 79.20. Baseline alone: share 0 -> 0.00 (definite, differs). All 5 bear weight; multi-source: pet_refund_share (stays.payment_plan + collection rows), credit part (redeemed + reinstated rows); cross-difficulty rows seeded (Gold membership 2a063d5c, redemption 82722266). Near-miss: the 150.00 pet-fee refund on stay 8746ddca (another stay).
Extra-guest refund (331.78): notice 30 vs 1 -> 550.46; share vs 0 -> 0.00; linen 10 vs 0 -> 349.25; courtesy 50 vs 0 -> 314.32; credit vs 1 -> 334.40. Baseline alone 0.00. All bear weight. Near-miss: the 32.00 extra-guest refund on stay 8746ddca.
SF refund (55.33): refund_fee_percentage 12 vs 14.20 -> 65.48; refunded_fee_base tier 1 vs nightly only -> 6.48; arrival_night_courtesy 50 vs 0 -> 48.86; credit vs 1 -> 55.77. Baseline alone: 14.20% x nightly refunds 0 -> 0.00. All bear weight numerically; but `refunded_fee_base`'s fall-through ("nightly refunds only" for every pay-in-full stay) is the unreal ladder of `_difficulty.md` F-3 — its weight here is measured against a treatment the rule's own reason ("prepaid its pet and extra-guest fees") contradicts for pay-in-full stays. **SOURCE-FACTOR RED**. Near-miss: the nightly refunds 640.00 / 472.00 on other stays (rule: "on the ledger for the cancellation").

Task-level: multi-source factor present (pet_refund_share, credit parts, arrival_night_courtesy); cross-difficulty (Rewards) factor present with rows seeded (subject to `_difficulty.md` F-8).

Provisional verdict (pre-reveal): SOURCE-POLICY RED (F-1, two values for the root write); SOURCE-FACTOR RED (F-2 notice-charge factor structure; F-3 SF fee-base fall-through); problem tree PASS; unique solution otherwise determined (115.33 / installment 2, 78.58, 331.78, 55.33), conditional on F-1.

## source_gt_comparison

- Reveal time: 2026-10-07T19:24:22Z, after both task files were frozen (frozen file hashes at 19:23:26Z: `_difficulty.md` 2353c5e6…3125, `task_0.md` 09486440…3a86, `task_1.md` d66ffc5c…bd2).
- Fields revealed: evaluation_criteria, computations, prerequisite_closure, charter_scope, required_documents, design_rationale, solvability_contract.

Item by item (blind derivation vs GT):

| item | blind | GT | same? |
| --- | --- | --- | --- |
| need / authorisation / timing | pay what is owed now, own card; agent may post Roamhaven's entries first | same (request_alignment) | same |
| now / wait / refuse | act now | act now | same |
| object | stay 79bb8aae | 79bb8aae | same |
| pet refund | refund_pet_fee_41a7068c, pet_fee, guest_cancellation, "", host, before_payout_release, 78.58 | identical | same |
| extra-guest refund | refund_extra_guest_fee_b492f389, extra_guest_fee, guest_cancellation, "", host, before, 331.78 | identical | same |
| SF refund | refund_service_fee_f4bed6e4, guest_service_fee, guest_cancellation, "", platform, before, 55.33 | identical | same |
| notice charge | pay_notice_charge_caff8891 (user), installment 2, 115.33 | identical | same |
| order / owners | {pet, extra} -> SF -> notice (user, handed over) | pet, extra, SF, notice; order_uniqueness: pet/extra either order | same |
| terminal state | 3 refund rows + 1 collection on 79bb8aae | same | same |
| charter_scope | {notice, pet, extra, SF} | same four policies and tools | same |

Problem tree vs `prerequisite_closure` (value against value): root stay_ext_departure_notice_charge = mine. Edges: notice->pet state_gate (gate stay_transactions.charge_component) = mine; notice->extra state_gate = mine; notice->SF state_gate = mine; SF->pet value_input (sf_addon_refunds) = mine; SF->extra value_input = mine. resolution_order [pet, extra, SF, notice] = my topological order (with pet/extra interchangeable, as GT's order_uniqueness also states). Load-bearing figures: skip pet -> SF 45.98 (mine 45.98); skip extra -> 15.83 (mine 15.83); neither -> 6.48 (mine 6.48 opening-world value). Same.

Factor weight vs `computations[].factor_sensitivity` / `baseline_result` (figure against figure):
- notice (expected 115.33 = mine): notice_length 41.39 = 41.39; notice_night_coverage 0.00 = 0.00; notice_fee_rate 116.52 = 116.52; notice_fee_base 116.10 = 116.10; notice_tax_exemption 133.83 = 133.83; rewards_fee_relief 121.86 = 121.86; baseline_result 0.00 = 0.00.
- pet (78.58): 130.37 / 0.00 / 87.31 / 69.85 / 79.20 all equal; baseline 0.00 = 0.00.
- extra (331.78): 550.46 / 0.00 / 349.25 / 314.32 / 334.40 all equal; baseline 0.00 = 0.00.
- SF (55.33): 65.48 / 6.48 / 48.86 / 55.77 all equal; baseline 0.00 = 0.00.
- GT `tier_taken` labels for pet_refund_share / extra_guest_refund_share ("the stay is paid in monthly installments") and refunded_fee_base omit the ladder's second condition ("and its collections have begun"); label truncation only (observation).

Closest candidate and its exclusion: for the root, the closest candidate is 121.86 (no Rewards relief, base "each installment carries the guest service fee ... attributable to the amounts it collects"). GT excludes it only by the extended rule; no `overwrite` names that base sentence (F-1). The installment-0 trap (charge 0.00) is excluded by base's event definition, as GT's near-miss card also says.

Verification of the proof's world assertions:
- `prerequisite_closure.edges[*].unresolved_at_frozen_time.why_false` (all five edges): "At frozen_time the cancelled stay's only ledger entry is the installment 1 collection" — **false**: the stay also carries the installment-0 collection `initial_state.stay_transactions.9ebf069f-33ad-4f1a-8950-f76899827f2c` (672.00, request ffa3b72d), seeded by the instantiator's revision (6). The conclusion it supports (no stay_refund_issued row on the stay) is true.
- `solvability_contract.temporal_feasibility[grace_hours].boundary_check.at_boundary`: "2026-08-28T19:42:00 booked, 2026-10-07T13:40:00 cancelled: 958 elapsed hours" — **false**: the elapsed time is 953.97 hours (953 h 58 min). The conclusion (> 48, grace not met) is true.
- All other world assertions checked true: SP3's SF refund outside the cap window, count 1 < 3; the 672.00 collection = 600 + 72; installment 1 = 3264 + 220 + 150 + 436.08 - 80; 4 refund rows on SP2 and 6 on SP3; release no earlier than 2026-10-08T00:00; "removing the Rewards membership changes four factors; removing the redemption changes three".

Verdict per relationship:
- Policy self-consistency: **SOURCE-POLICY RED** (F-1, demonstrated: 115.33 vs 121.86 for the root write).
- Problem tree: tree holds (independent walk isomorphic to GT, all edges false at opening and load-bearing, user write present, n=3 with 2 value_input edges). **SOURCE-CHAIN RED** on the proof only: the false "only ledger entry" assertion in every `prerequisite_closure` edge.
- Factors: **SOURCE-FACTOR RED** (F-2 notice-charge ladders restate the write's scope -> fewer than 4 surviving factors and 1 parameter on the root computation; F-3 SF fee-base fall-through).
- Unique solution: apart from F-1, the derivation equals GT on every write, argument, owner and order. **SOURCE-TASK RED** on the proof only: the false "958 elapsed hours" assertion. No second reading of need, authorisation, object or order.

**Task 0 verdict: SOURCE-POLICY RED + SOURCE-FACTOR RED (+ SOURCE-CHAIN RED and SOURCE-TASK RED on proof assertions only).**

## findings

1. **SOURCE-POLICY RED — undeclared override on the root's guest service fee (F-1).**
   Symptom: two defensible amounts for `pay_notice_charge_caff8891`. Root cause: the notice charge is "booked as the installment that covers the first unpaid notice night", and base `stay_evt_payment_schedule` says "each installment carries the guest service fee and occupancy tax attributable to the amounts it collects"; the extended rule's "Roamhaven Rewards members get relief on the guest service fee of a notice charge ... priority_fee_relief_pct percent" reduces it, and the policy's `overwrite` names from `stay_evt_payment_schedule` only "Money is collected only on a confirmed or checked-in stay." Evidence: extended yaml `stay_ext_departure_notice_charge.rule` / `.overwrite`; base `stay_evt_payment_schedule.rule`; ledger rows 01eb841f (installment 1, SF 436.08 at the full 12% for the same Gold guest) and 9ebf069f (SF 72.00 at 12%). Consequence: Reading A 108.80 + 13.06 = 121.86; Reading B (gold) 108.80 + 6.53 = 115.33. Affected: extended charter `stay_ext_departure_notice_charge` (overwrite list), scored argument `amount` of the user write. First revision.
2. **SOURCE-FACTOR RED — notice-charge factor structure (F-2).**
   Symptom: three of six declared factors divide no customer who reaches the write. Root cause: an unpaid notice night can exist on an in-progress stay only on a Long-Term monthly stay (charter: `monthly_installments_available` only on Long-Term; Long-Term `pay_part_now_available: false`; pay-in-full collects all nights; a pay-part-now balance due 14-35 days before check-in lapses the stay after 48 h). Evidence: tiers of notice_length ("long_term_min_nights nights or more"), notice_night_coverage ("paid in monthly installments"), notice_fee_rate (part "long_term_min_nights nights or more"; fall-through 14.20 unreachable), notice_fee_base (tier "pay-part-now" unreachable). Consequence: on this world the baseline that these factors "bear weight" against (1 notice night; every night paid at confirmation; 14.20%) is a treatment no notice-charge customer can receive; surviving factors are notice_tax_exemption and rewards_fee_relief (at most notice_fee_base too) — below 4 factors and 2 parameters. Affected: `stay_ext_departure_notice_charge.factors`, `computations[notice]`. First revision.
3. **SOURCE-FACTOR RED — departure SF `refunded_fee_base` fall-through (F-3).**
   Symptom: the fee-base ladder includes refunded pet and extra-guest fees only for a monthly stay, "whose collections have begun and so prepaid its pet and extra-guest fees", and excludes them for every other cancellation on or after check-in. Evidence: base `stay_evt_payment_schedule` "Under pay_in_full the whole total_price is collected as installment 1 when the stay is confirmed" (pay-in-full stays prepaid those fees too); base `service_fee_base_components` includes pet_fee_total and extra_guest_fee_total. Consequence: the factor's measured weight on this world (55.33 vs 6.48) is against a fall-through that contradicts the rule's own stated reason for the tier and withholds the service fee on refunded add-ons from pay-in-full guests. Affected: `stay_ext_departure_service_fee_refund.factors[refunded_fee_base]`. First revision.
4. **SOURCE-CHAIN RED (proof field) — false "only ledger entry" assertion.** `prerequisite_closure.edges[0..4].unresolved_at_frozen_time.why_false` says the installment 1 collection is the stay's only ledger entry; row `stay_transactions.9ebf069f-33ad-4f1a-8950-f76899827f2c` (installment 0, 672.00) is also on it. Conclusion unaffected; the proof field is stale after revision (6). Affected: task 0 `prerequisite_closure`. First revision.
5. **SOURCE-TASK RED (proof field) — false elapsed-hours figure.** `solvability_contract.temporal_feasibility[grace_hours]` asserts 958 elapsed hours; recomputed 953.97 h. Conclusion unaffected. Affected: task 0 `solvability_contract`. First revision.
6. Observation — persona line "You are happy for the agent to take care of anything Roamhaven needs to put through on the reservation before you pay" pre-authorises unnamed agent entries; it names no prerequisite and does not steer.
7. Observation — GT `tier_taken` labels truncate the two-condition tiers (see comparison).
8. Observation — the credit-funded part returns credits that no write of this task reinstates (`_difficulty.md` F-6); cross-difficulty factor reads Rewards, which no difficulty claims (`_difficulty.md` F-8).

## revision_2

### source_derivation_frozen (revision 2)

- Freeze time: 2026-10-07T21:12:29Z (before the round-2 task JSON was opened). Revision 1 text above is unchanged.
- Inputs: view `/tmp/erl45_views/r2/guest_cancellations_and_refunds/task_0.view.json` `4c7fe62383f638c6c29e05841faadb7ad7188f7a0a4679d51c7ba7105e20e67a`; charter `ed0b001c…14a1`; tools `bbb8e9e1…b7bb`. The view differs from r1 only in installment 1 on stay 79bb8aae: 3772.04 (was 3990.08) = 3264.00 + 220.00 + 150.00 + RND(3634.00 x 12% x 50%) 218.04 - 80.00 credits. That is the monthly installment-1 courtesy for a Gold guest, consistent with the r2 first-installment overwrite ("following the guest's Rewards tier active when installment 1 is collected"; Gold since 2025-11-16).
- Masked and unread: evaluation_criteria, computations, prerequisite_closure, charter_scope, required_documents, design_rationale, solvability_contract, worklog.md (round 2).
- contamination_disclosure: the r1 GT of this task was revealed in revision 1 (115.33 / 78.58 / 331.78 / 55.33). Every r2 figure below is recomputed from the r2 charter and view.

Charter-global conclusions: cited from `_difficulty.md` § revision_2.

### policy_self_consistency (revision 2, this task)

- F-1 on this task: closed. The notice charge's fee relief is now a declared exception to "each installment carries the guest service fee … attributable to the amounts it collects" (`stay_ext_departure_notice_charge.overwrite[3]`). Reading A (121.86 in r1) no longer has an undeclared base sentence behind it. The stay's installment 1 (3772.04) now also carries the Gold courtesy, so the records no longer point to a no-relief reading.
- Handling time and no-wait arguments unchanged from revision 1 (re-checked on the r2 view): pet and extra on the opening world, SF after both, notice last; no real-world wait; refund_stage before_payout_release.
- SF cap: other stays with a guest-cancellation SF refund > 0 dated 2025-10-08..2026-10-07: 9f29245e only -> 1 < 3, not capped (R2-O1 has no consequence here).

### problem_chain (revision 2)

Unchanged tree, walked again from the r2 rules: root notice charge (user) <- pet, extra, SF (state_gate); SF <- pet, extra (value_input). All four prerequisite states false at opening (the stay's ledger has only the installment-1 and installment-0 collections). n = 3, value_input edges 2. Load-bearing on the r2 world: skip pet -> SF **26.23**; skip extra -> SF **11.15**; neither -> **6.48** (gold-by-derivation 30.91). Pet and extra read neither each other nor any refund (card-share tier 1, and tier 2 no longer reads refunds), so their order is free. Persona unchanged (only root raised; passive consent).

### task_independent_derivation (revision 2)

Act now; object stay 79bb8aae; night price 108.80; card share 1 - 80/10225.60 = 0.99217650.

1. Pet-fee refund (agent): unchanged rule on this world -> RND(150 x 44/75 x 0.90 x 0.99217650) = **78.58**; pet_fee, guest_cancellation, "", host, before_payout_release.
2. Extra-guest-fee refund (agent): **331.78**; extra_guest_fee, guest_cancellation, "", host, before_payout_release.
3. SF refund (agent, after 1-2): fee base = nightly 0.00 + cleaning 0.00 + pet 78.58 + extra 331.78 = 410.36 (nightly refund under the new "lesser of" exception: collected 3264.00 - price of the 31 nights kept 3372.80 -> floored 0.00; cleaning not refunded on or after check-in); share returned (dated on the check-in date) 50 % -> 205.18; arrival courtesy (Gold, on the check-in date) 54.40 in full; rate 12.00; card share. Amount = RND((205.18 + 54.40) x 0.12 x 0.99217650) = **30.91**; guest_service_fee, guest_cancellation, "", platform, before_payout_release. Opening-world value 6.48.
4. Notice charge (user, handed over, after 1-3): nights kept = 1 (through 10-07) + 30 notice nights (Long-Term) + 0 % of the 44 later nights (Long-Term keeps none) = 31; kept price 31 x 108.80 = 3372.80; paid = 1 monthly installment (installment 0 excluded) x 30 nights x 108.80 = 3264.00; owed nightly 108.80 (night 31, 2026-11-06); no owed fees (installment 1 collected); fee rate 12.00; relief = Rewards Gold priority 50 + returning-guest 10 (one credit earning in 24 months: 2025-11-17; the 2025-11-16 tier-upgrade bonus is not an earning) = 60 % -> fee RND(108.80 x 0.12 x 0.40) = 5.22; tax 0 (75 >= 30 and 31 kept >= 30). Amount **114.02**, installment_number **2** (the installment covering night 31).

Write sequence: {pet, extra} -> SF -> notice (user). Terminal state: refund rows 78.58, 331.78, 30.91 and collection 114.02 (installment 2) on 79bb8aae.

Closest alternatives: notice 115.33 (no returning-guest relief) — excluded by the rule's returning-guest sentence and the seeded earning row; 120.55 (no Rewards relief) — excluded by the active Gold tier; SF 55.33 (full share) — excluded by "a cancellation dated on or after the check-in date returns in_stay_fee_share_pct percent"; notice 0.00 by counting installment 0 — excluded as in r1.

### factor_weight (revision 2)

Notice (114.02): notice_length 30 vs baseline 1 -> 41.39; later_nights_kept 0 vs 100 -> 5131.01; notice_fee_rate 12 vs 14.20 -> 114.98; notice_tax_exemption none vs 17 % of fee base -> 132.52; rewards_fee_relief 50 vs 0 -> 120.55; returning_guest_relief 10 vs 0 -> 115.33. All six bear weight. Baseline alone (1 notice night, every later night kept, 14.20 %, rate tax, no relief): kept 75, owed 4896.00, fee 695.23, tax 832.32 -> **6423.55**, definite, not gold. Near-misses: installment-0 collection; tier-upgrade bonus row; nights kept 31 vs exempt minimum 30. Real-ladder test (`_difficulty.md` revision_2 § factor_ladders): pass.
Pet (78.58) and extra (331.78): unchanged figures from revision 1 (130.37 / 0.00 / 87.31 / 69.85 / 79.20; 550.46 / 0.00 / 349.25 / 314.32 / 334.40); baselines alone 0.00.
SF (30.91): refund_fee_percentage 12 vs 14.20 -> 36.57; late_cancellation_fee_share 50 vs 100 -> 55.33; arrival_night_courtesy 50 vs 0 -> 24.43; credit part vs 1 -> 31.15. Baseline alone (14.20 % of every refunded component) -> **58.27**. All bear weight; 3 parameter / 1 method.
Task-level: multi-source (pet_refund_share; credit parts; arrival_night_courtesy) and Rewards cross-category rows seeded (subject to F-8).

Provisional verdict (pre-reveal): all four relationships PASS on the charter and world; the proof fields (r1 defects 4 and 5) are checked after the reveal.

### source_gt_comparison (revision 2)

- Reveal time: 2026-10-07T21:13:20Z, after both revision-2 task sections were frozen (hashes at 21:13:14Z: `_difficulty.md` 9fcce649…7445, `task_0.md` 18c3a2b1…1039, `task_1.md` 38559939…99cf).

| item | blind (r2) | GT (r2) | same? |
| --- | --- | --- | --- |
| pet refund | refund_pet_fee_41a7068c, pet_fee, guest_cancellation, "", host, before_payout_release, 78.58 | identical | same |
| extra-guest refund | …, extra_guest_fee, …, host, before, 331.78 | identical | same |
| SF refund | …, guest_service_fee, …, platform, before, 30.91 | identical | same |
| notice charge (user) | installment 2, 114.02 | identical | same |
| order | {pet, extra} -> SF -> notice | [pet, extra, SF, notice], pet/extra free | same |
| charter_scope | {pet, extra, SF, notice} | same | same |

Problem tree vs `prerequisite_closure`: root, five edges, kinds, gates and resolution_order identical to mine; load-bearing 26.23 / 11.15 / 6.48 equal mine.
Factors vs `computations`: notice expected 114.02 (= mine), baseline_result 6423.55 (= mine); sensitivities 41.39 / 5131.01 / 114.98 / 132.52 / 120.55 / 115.33 all equal mine. Pet 130.37 / 0.00 / 87.31 / 69.85 / 79.20, baseline 0.00; extra 550.46 / 0.00 / 349.25 / 314.32 / 334.40, baseline 0.00; SF 36.57 / 55.33 / 24.43 / 31.15, baseline 58.27 — all equal mine.

Round-1 item closure on this task:
- F-1 (SOURCE-POLICY RED): **closed** — declared overwrite; the closest alternative (115.33, no returning-guest relief; 120.55, no Rewards relief) is excluded by declared rule text and seeded rows.
- F-2, F-3 (SOURCE-FACTOR RED): **closed** (see `_difficulty.md` revision_2 § factor_ladders).
- Proof field `prerequisite_closure.why_false`: **closed** — now "the cancelled stay's ledger holds two collections and nothing else: installment 1 (3772.04 …) and the installment-0 increase … (672.00)", true against the view.
- Proof field `solvability_contract` elapsed hours: **closed** — now "953.97 elapsed hours (953 h 58 min)", true.
- `tier_taken` labels: **closed** — pet/extra share labels now carry "and its collections have begun"; `refunded_fee_base` is gone.

Regression and new-defect check on this task's proof (world assertions re-verified): ledger rows, 953.97 h, cap count 1 < 3, installment 1 = 3634.00 + 218.04 - 80.00, 31 kept nights vs 30, one earning 2025-11-17, Long-Term `after_check_in_refund_pct` 100, Moderate keeping half — all true. One false assertion found:
- `design_rationale` INITIAL_STATE ROWS: "removing the installment 1 row changes the nights paid, adds the uncollected fees and the credit offset to the charge and zeroes every share-based refund". The last clause is **false**: with row 01eb841f removed, the installment-0 collection 9ebf069f remains, so `COUNT(stay_payment_collected) >= 1` still holds and the pet and extra-guest shares stay on their monthly tier (44/75), giving 78.58 and 331.78 again, not 0.00 (and the SF refund, which reads them, is unchanged at 30.91). The first two clauses are true. The round-1 text of the same card ("… changes … every share-based amount") was already false for the same reason and was missed in revision 1; it is recorded now.

Verdict per relationship (revision 2): policy self-consistency PASS; problem tree PASS; factors — the factors themselves PASS, **SOURCE-FACTOR RED on one proof sentence only** (the false counterfactual above, which argues that the share tiers rest on the installment-1 row); unique solution PASS.

**Task 0 revision_2 verdict: SOURCE-FACTOR RED (proof field only: design_rationale counterfactual about removing installment 1); all four relationships otherwise PASS; every round-1 RED closed; no regression.**

### findings (revision 2)

1. Round-1 findings 1-5 and the label observation (7): closed as listed above. Observations 6 and 8: unchanged (not claimed changed).
2. **SOURCE-FACTOR RED (proof field) — false counterfactual in `design_rationale`.** Symptom: the seed-necessity card claims removing installment 1 "zeroes every share-based refund". Root cause: the share tier's condition is "collections have begun", and the installment-0 collection on the same stay keeps it met. Evidence: `stay_ext_departure_pet_fee_refund.compute.pet_refund_share` (`COUNT('stay_transactions', event_type='stay_payment_collected') >= 1`), row `stay_transactions.9ebf069f-33ad-4f1a-8950-f76899827f2c`. Consequence: the proof asserts a weight the installment-1 row does not carry; recomputed pet 78.58 / extra 331.78 with the row removed. The scored solution is unaffected. Affected: task 0 `design_rationale` (INITIAL_STATE ROWS). Pre-existing in substance since revision 1 (missed then).
3. Observation — `design_rationale` calls the nights-paid computation "plumbing (not factors, the same for every customer)"; it varies by payment plan but is now part of the baseline method, not a declared factor. Author's framing, no consequence.

## revision_3

### source_derivation_frozen (revision 3)

- Frozen 2026-10-07T21:45:23Z, before the round-3 task JSON was opened. Earlier revisions untouched.
- Inputs: view `task_0.view.json` (r3) hash identical to revision 2; charter `ed0b001c…14a1` and tools `bbb8e9e1…b7bb` identical to revision 2. The world, the charter and the tool contracts are unchanged, so revision 2's `policy_self_consistency`, `problem_chain`, `task_independent_derivation` and `factor_weight` for this task are **carried forward by reference** (the blind solution and every figure stand as frozen in revision 2). Only the proof fields of the task JSON, which may have moved, are re-judged after the reveal.
- contamination_disclosure: round-1 and round-2 GT of this task are known from earlier revisions; the round-3 JSON is unopened at this freeze.

### source_gt_comparison (revision 3)

- Reveal time: 2026-10-07T21:45:40Z, after the revision-3 freeze (file hashes at 21:45:34Z: `_difficulty.md` 222268c3…97f1, `task_0.md` d127fd17…3ef4, `task_1.md` b2a77f66…bd7).
- Scored solution unchanged: refund_pet_fee 78.58, refund_extra_guest_fee 331.78, refund_service_fee 30.91 (args as in revision 2), pay_notice_charge installment 2 / 114.02 (user); computations expected and baseline_result 78.58 / 0.00, 331.78 / 0.00, 30.91 / 58.27, 114.02 / 6423.55, and every factor_sensitivity figure equal to revision 2 and to my carried-forward derivation. `prerequisite_closure` unchanged (five edges, kinds, order, load-bearing 26.23 / 11.15 / 6.48). Same / same / same.

Revision-2 item closure:
- Finding 2 (SOURCE-FACTOR RED, proof field): **closed.** The INITIAL_STATE card now reads: removing installment 1 "changes the nights paid (none) and adds the uncollected fees and the credit offset to the charge; it does not move the pet and extra-guest shares, because the installment-0 collection 9ebf069f still shows that collections have begun on the stay (78.58 and 331.78 again, and the service-fee refund that reads them stays 30.91); removing both collections would drop those shares to their fall-through, the nightly refund on the ledger (0.00)". Verified clause by clause against the compute: without 01eb841f, `first_installment_collected` = 0 -> paid nightly 0, owed fees and the 80.00 credit offset apply; `COUNT(stay_payment_collected)` = 1 -> share tier unchanged -> 78.58 / 331.78 / SF 30.91; without both rows the count is 0 -> fall-through = nightly guest-cancellation refunds on the ledger (none) / subtotal = 0.00. True. The only remaining occurrence of the old phrase is the REVISIONS (8) entry quoting it as the corrected claim, which is accurate.
- Observation 3 (wording): **closed** — the factor card now says the nights paid, uncollected fees and credit offset are "part of the baseline method rather than declared factors (stated in the rule's standard paragraph and varying only by payment plan)", which matches the charter.

Regression check on the other proof fields: `why_false` (two collections, 3772.04 and 672.00), 953.97 elapsed hours, `tier_taken` labels with both conditions — unchanged and true. No new world assertion found false.

Verdict per relationship (revision 3): policy self-consistency PASS; problem tree PASS; factors PASS; unique solution PASS.

**Task 0 revision_3 verdict: PASS.**

## revision_4

### source_derivation_frozen (revision 4)

- Frozen 2026-10-07T22:38Z, before the round-4 task JSON was opened. Earlier revisions untouched.
- Inputs: r4 view `task_0.view.json`; the only change from r3 is frozen_time -> "2026-10-07 17:05:00 CDT". Charter unchanged; tool module changed only in posted_at formatting (see `_difficulty.md` § revision_4).
- Per-task re-judgement of what the clock change could move: the handling date stays 2026-10-07 (every compute reads the date part only); the 13:40 cancellation and the 17:05 handling time are both Central local; the 48-hour booking-grace test (953.97 h) and the payout-release boundary (2026-10-08 00:00) are unchanged. The booked posted_at stays "2026-10-07T…" ISO local, so later reads by date or by ledger order are unchanged. No persona line refers to the clock format.
- Therefore revision 2's per-task sections (policy_self_consistency, problem_chain, task_independent_derivation, factor_weight), as carried forward in revision 3, stand **by reference**: the blind solution and every figure are unchanged.
- contamination_disclosure: rounds 1-3 GT of this task known; round-4 JSON unopened at this freeze.

### source_gt_comparison (revision 4)

- Reveal time: 2026-10-07T22:38:20Z, after the revision-4 freeze (hashes at 22:38:14Z: `_difficulty.md` d5af08d4…, `task_0.md` 7a06f99b…, `task_1.md` 691252a6…).
- frozen_time in the JSON: "2026-10-07 17:05:00 CDT" (the old ISO stamp no longer appears anywhere in the file). The runtime posted_at the tools book: `"2026-10-07 17:05:00 CDT"[:19].replace(" ", "T")` = "2026-10-07T17:05:00" (checked), the same as under round 3.
- Scored solution unchanged and equal to my carried-forward derivation: pet 78.58, extra-guest 331.78, SF 30.91 (arguments identical to revision 2), notice charge installment 2 / 114.02 (user). Computations expected/baseline 78.58/0.00, 331.78/0.00, 30.91/58.27, 114.02/6423.55; every factor_sensitivity figure as in revision 2. prerequisite_closure: same five edges, kinds, gates, order and load-bearing figures (26.23 / 11.15 / 6.48). design_rationale and proof fields: no change in substance (the REVISIONS card records the earlier rounds; the round-3 initial-state card is retained).
- Regressions: none. New defects: none.

Verdict per relationship (revision 4): policy self-consistency PASS; problem tree PASS; factors PASS; unique solution PASS.

**Task 0 revision_4 verdict: PASS.**
