# Policy-task audit — repair_and_emergency_service / task 1

## source_derivation_frozen

- Auditor: independent policy-task auditor. Freeze time: 2026-10-05T16:02Z.
- Inputs: `/tmp/erl37/views/repair_and_emergency_service/task_1.masked.json` (sha256 fd43bd73bd9318f8427a0cc6c7cd1fdbcf8c8f4789b4084699cd19ff1aaae07e), service.extended.yaml (4357430a…4c23a), task_tools.py (b2417a58…6be53), blueprint products, share_tools.py.
- Masked and unread at freeze: evaluation_criteria, computations, db_closure, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure. `tasks/1.json` not opened. Task 0's GT also not yet revealed (both derivations frozen before any reveal).
- contamination_disclosure: none.

World (frozen_time 2026-10-02 11:05 EDT, a Friday; date of handling 2026-10-02):
- customers 4623b2bd…: Denise Okafor, discount_program military_veteran, phone 6145553829, PIN 2618.
- equipment: 1dcde166… heat pump and 393ff4d4… air handler (Harbison 2021); 43d98da6… Lennox gas furnace (not Harbison-installed, 2014).
- service_tickets 2faee4a7…: Weekend Service Call, completed, scheduled 2026-09-26 (Saturday), window 08:00-12:00, arrived 10:20 (on time), symptom maintenance_request, equipment 43d98da6 (furnace), ticket_balance 1018.76.
- service_lines on 2faee4a7: maintenance_tuneup 149.00 (b1f37555; Weekend tuneup_price 149); after_hours_premium 119.00 (07776700; Weekend premium 119); repair_parts inducer_motor_replace 412.00; repair_labor 471.25 (= 377 × 1.25); member_repair_discount 61.80 and 70.69 (15 %). 1151.25 − 132.49 = 1018.76 = ticket_balance. No member_premium_discount, no discount_program line, no payment.
- plan_agreements 07f236d5…: Comfort Club Gold, active, enrolled 2018-03-20, term 2026-03-20..2027-03-19, annual, auto_renew true, consecutive_terms 9. Gold tier: after_hours_premium_discount_pct 50, scheduling_priority priority, repair_discount_pct 15.
- plan_billing_entries: renewal dues 2025-03-20 and 2026-03-20 paid card_on_file; upgrade_proration 25.00 paid 2026-09-08 by card_by_phone (line_type dues_payment).
- plan_service_entries: completed tune-ups on the heat pump 1dcde166 on 2024-04-15, 2024-10-14, 2025-04-21, 2025-10-20, 2026-04-14; none on the furnace.
- install_projects e48eff44…: Performance Hybrid Heat Pump System (two_stage), contract_price 14695, closed 2021-11-19.
- warranty_contracts 8aeb73f7…: 5-Year Labor Protection, matched_system (heat pump + air handler), active, coverage_end 2026-11-08 (37 days after handling). One contract only.
- filter_subscriptions 0526334f…: Media Cabinet MERV 13 (merv 13, depth 4 in), active; shipments 2024-12-05, 2025-06-05, 2025-12-05, 2026-06-05.

### policy_self_consistency (this task only)

- Charter-global conclusions cited: `_difficulty.md` → policy_conflict_scan, rule_compute_equivalence, action_binding_and_uuids, prerequisite_graph, prerequisite_sentences, override_declarations.
- F-G2 (unit multiplier counts non-completed tune-up rows): on this world the call's unit (furnace 43d98da6) has no plan_tuneup_visit row of any entry_reason, so rule and compute both give ×0.9. No consequence on task 1.
- Override consequences on this world:
  - dispatch_fees' premium discount (Gold 50 % of 119 = 59.50) vs extended (points-raised percentage): declared; extended governs; unique.
  - discount_stacking's courtesy clause (10 % of the tune-up line = 14.90) vs extended (raised rate on tune-up lines): declared; unique. Repair lines: member 15 % > courtesy 10 % → no courtesy line on repair lines under the base text the extended rule points back to ("settled as before").
  - flat_rate special-order deposit (50 % of parts amount) and payment due on completion vs extended release payment: declared; unique.
- Base eligibility for the paid tune-up (service_maintenance_tuneup): the furnace is not the agreement's enrolled system (systems_covered 1; every plan tune-up is on the heat pump), so a paid tune-up on it is consistent with "a member who has no visit left for that system". Observation O1-1 only (no scored quantity depends on it).
- Handling time: member premium discount and courtesy discount on the opening world (neither reads the balance); release payment after both.
- Real-world waits: none. The ordering of the part happens after the payment and gates no write.

### problem_chain

Root problem (raised by the customer): pay what is needed today so the special-order inducer motor is ordered (service_ext_special_order_release; on_request; owner user).

Walk:
1. "The special-order deposit payment is taken only after the after-hours premium line on a member's call carries the member premium discount line owed on it." Active Gold member, Weekend call, premium line 07776700 has no member_premium_discount → unmet. Writer: service_ext_member_premium_discount.
2. "No special-order deposit payment is taken until the paid tune-up line of a courtesy-program customer's call carries the courtesy discount line owed on it." military_veteran on profile; Weekend discount_program_applies true; tune-up line b1f37555 has no discount_program line → unmet. Writer: service_ext_courtesy_discount.
3. Both leaves carry no prerequisite sentence.

Derived tree: special_order_release ← {member_premium_discount (value_input d_open), courtesy_discount (value_input d_open)}. n = 2, value_input edges 2 ≥ 1; acyclic; owner=user root (pay_special_order_deposit_ccffba41). Topological order: the two discounts in either order, then the release payment. Isomorphic to the declared edges.

Load-bearing runs: skip premium discount → d_open 230.75 → release 293.79 (vs 180.74); skip courtesy discount → d_open 154.95 → release 217.99. Both bear weight. Parallel edges: neither discount reads the balance; both orders reach the same terminal state.

Tools judge no prerequisite (`_difficulty.md` → action_binding_and_uuids).

Persona: raises only the payment that releases the part; does not name either discount. Conditional consent ("If the agent tells you that something has to be corrected or added on the bill … go ahead") is passive. The persona background calls her "an Air Force veteran" — a fact already on the profile (military_veteran), not a request; observation O1-2. Closes after the confirmation number.

### task_independent_derivation

Act now: completed call with an approved repair awaiting a special-order part (persona: technician found the inducer motor failing, part must be special-ordered, repair approved; Weekend class is truck_stock_only); customer verified by phone + PIN.

1. Member premium discount (agent; post_member_premium_discount_f1d91bca).
   - Standard pct: Gold after-hours 50 (Weekend, not Holiday).
   - Tenure: enrolled 2018-03-20 → 102 whole months ≥ 96 → +15. Prepay: annual + auto-renew → +5. Tune-up window: annual → last 24 months: 2024-10-14 (23 months), 2025-04-21, 2025-10-20, 2026-04-14 → 4 (2024-04-15 at 29 months excluded) → +10. Installation closed 2021-11-19 → 58 whole months < 60 → +10. Filter MERV 13 active → +5.
   - pct = 95 (≤ 100). Discount = RND(119 × 0.95) = **113.05**; source_line_id 07776700…, agreement_id 07f236d5…, customer_id 4623b2bd…, recall "".
2. Courtesy discount (agent; post_courtesy_discount_1179d4e9).
   - Standard rate: Weekend 10 % (applies). Terms 9 ≥ 8 → +4. Closed install two_stage → +3. Shipment window: active 4-inch cabinet → 24 months: all four shipments (oldest 2024-12-05 at 21 months) → 4 → +3. Matched-system contract → +3. Dues paid card_on_file in last 12 months (2026-03-20) → +2 (2026-09-08 is card_by_phone; 2025-03-20 is 18 months back).
   - Rate 25 %. Discount = RND(149 × 0.25) = **37.25**; source_line_id b1f37555…, agreement_id 07f236d5…, customer_id, recall "".
3. Release payment (customer; pay_special_order_deposit_ccffba41).
   - Visit balance: charges 1151.25 − (discounts 61.80 + 70.69 + 113.05 + 37.25) − payments 0 + refunds 0 − (412.00 + 471.25 − 132.49) = **117.70** (= 149 − 37.25 + 119 − 113.05).
   - Deposit rate: Gold priority → 35; install price 14695 ≥ 12000 → −10; contract ends in 37 days (≤ 365) → −3; dues payments in last 24 months: 2025-03-20, 2026-03-20, 2026-09-08 → ≥ 2 → −5; rate 17 %.
   - Unit multiplier: member, call's unit (furnace) has no Comfort Club tune-up on record → 0.9.
   - Deposit = RND(412 × 17 % × 0.9) = RND(63.036) = 63.04. Release payment = 117.70 + 63.04 = **180.74**, payment_method card ("credit card, which is a card payment").
   - Opening-world contrast (no discounts posted): 268.00 + 63.04 = 331.04.
- Terminal state: three new lines (member_premium_discount 113.05, discount_program 37.25, payment 180.74 card); ticket_balance 1018.76 − 113.05 − 37.25 − 180.74 = 687.72 (= repair parts + labor net of member repair discounts, 750.76, minus the 63.04 deposit); status completed.
- Read set: find_customers, verify_customer_identity, find_service_tickets, find_service_lines, find_equipment, find_plan_agreements, find_plan_billing_entries, find_plan_service_entries, find_install_projects, find_warranty_contracts, find_filter_subscriptions, find_filter_entries (+ KB tier parameters). All reachable.

### factor_weight

member_premium_discount (gold 113.05):
| factor | honest? | tier / rows | baseline | value |
| --- | --- | --- | --- | --- |
| enrollment_tenure_points | parameter; scope conjunct (F-G4) | 102 months → 15 | 0 | 80 % → 95.20 |
| prepaid_renewal_points | parameter; scope conjunct (F-G4) | annual + auto-renew → 5 | 0 | 107.10 |
| tune_up_count_window | method, accepted; unreal condition (F-G4) | annual → 24 m count 4 | term count 1 | 5 pts → 107.10 |
| tune_up_points | parameter | count ≥3 → 10 | 0 | 101.15 |
| installation_points | parameter | closed 58 months → 10 | 0 | 101.15 |
| filter_points | parameter | MERV 13 → 5 | 0 | 107.10 |
Baseline rule alone: 50 % → 59.50 ≠ gold. Near-miss: 2024-04-15 tune-up (29 months, outside the 24-month window); installation at 58 months against the 60-month line. Stamp: none.

courtesy_discount (gold 37.25):
| factor | honest? | tier / rows | baseline | value |
| --- | --- | --- | --- | --- |
| consecutive_term_points | parameter | 9 terms → 4 | 0 | 21 % → 31.29 |
| installed_system_points | parameter | two_stage → 3 | 0 | 32.78 |
| shipment_count_window | **labelled method, only the window length differs** (F-G3) | 4-inch → 24 m count 4 | 6 m count 1 | 2 pts → 35.76 |
| shipment_points | parameter | ≥4 → 3 | 0 | 32.78 |
| protection_scope_points | parameter | matched_system → 3 | 0 | 32.78 |
| dues_payment_points | parameter; multi-source | card_on_file 2026-03-20 → 2 | 0 | 34.27 |
Baseline rule alone: 10 % → 14.90 ≠ gold. Near-miss: 2026-09-08 card_by_phone payment (not card on file); 2025-03-20 card_on_file outside 12 months. Honest `method`: 0 (fails the floor).

special_order_release (gold 180.74):
| factor | honest? | tier / rows | baseline | value |
| --- | --- | --- | --- | --- |
| deposit_rate_by_scheduling | parameter | Gold priority → 35 | 50 | 32 % → 236.36 |
| installation_price_points | parameter | 14695 → −10 | 0 | 27 % → 217.82 |
| protection_runway_points | parameter | ends in 37 days → −3 | 0 | 20 % → 191.86 |
| dues_payment_history_points | parameter; multi-source | 3 payments → −5 | 0 | 22 % → 199.28 |
| unit_enrollment_multiplier | **labelled method, is a number** (F-G3) | furnace without plan tune-up → 0.9 | 1 | 187.74 |
Baseline rule alone: 50 % × 412 = 206.00 + 117.70 = 323.70 ≠ gold. Near-miss: the heat pump's five completed tune-ups (a careless reader counts them for the furnace call); contract within 365 days. Honest `method`: 0 (fails the floor).

Task-level counts: multi-source present (dues_payment_points, dues_payment_history_points, unit_enrollment_multiplier); cross-difficulty present and seeded (plan, install, warranty, filter incl. filter_entries). Per computation 4–6 factors and ≥2 parameter: met; ≥1 honest method: met only for member_premium_discount.

### frozen verdict (pre-reveal)

- Policy self-consistency: PASS on this world (F-G2 no consequence here).
- Problem tree: PASS.
- Factors: **SOURCE-FACTOR RED** (F-G3 on courtesy_discount and special_order_release; F-G4 on member_premium_discount's tune_up_count_window and scope conjuncts). Every factor bears weight on this world.
- Unique solution: PASS pending GT comparison.

## source_gt_comparison

- Reveal: `tasks/1.json` first opened at 2026-10-05T15:49:36Z, after the frozen files' hashes were recorded (task_1.md 687e0a9e…dcca). Timestamp correction: the "Freeze time" in this file's header (16:02Z) was an estimate and is wrong. The hash record is the actual freeze evidence. The frozen text above is unchanged.
- Need / authorisation / timing: same. The customer pays the release amount today by credit card (card); owner user.
- Read set: same, including find_filter_entries. Gold also reads find_warranty_claim_entries to show that no claim or coverage credit is owed. My derivation took that from the claim-entry rows without listing the finder. This is not a solution difference.
- Act now, object (ticket 2faee4a7, premium line 07776700, tune-up line b1f37555, agreement 07f236d5): same.
- Parameters, all the same:
  - Member premium discount 113.05.
  - Courtesy discount 37.25 on the tune-up line, naming the agreement.
  - Release payment 180.74, card.
- Tool / owner / order: gold runs the premium discount, then the courtesy discount (agent), then the release payment (user). My derivation allows the two discounts in either order, and gold's order_uniqueness says they commute. Same.
- Terminal state: three new lines. Same.
- Closest alternative candidate:
  - Release payment = the whole balance net of discounts (868.46), or the base 50 % deposit (323.70 before discounts).
  - The extended rule excludes both. It defines the release payment as visit balance + deposit, with the repair's parts and labor set aside, and replaces the base deposit sentence by a declared override.
  - Unit multiplier 0.75 (counting the heat pump's tune-ups) is excluded because the rule reads "a unit with … tune-up on record" for the unit the call concerns.
- Problem tree vs `prerequisite_closure`:
  - Root service_ext_special_order_release: same as mine.
  - Edges release→member_premium_discount and release→courtesy_discount (value_input, d_open, state): same as mine.
  - Opening falsity rows: premium line with no discount and agreement active; tune-up line with no discount_program line and military_veteran on the profile. Same as mine.
  - resolution_order [premium, courtesy, release] is one of my two admissible orders.
  - Load-bearing figures: GT 293.79 / 217.99, mine 293.79 / 217.99. Identical.
- factor_weight vs `computations`:
  - member_premium_discount: GT 95.2 / 107.1 / 107.1 / 101.15 / 101.15 / 107.1, baseline 59.5. Mine identical.
  - courtesy_discount: GT 31.29 / 32.78 / 35.76 / 32.78 / 32.78 / 34.27, baseline 14.9. Mine identical.
  - special_order_release: GT 236.36 / 217.82 / 191.86 / 199.28 / 187.74, baseline 323.7. Mine identical.
- design_rationale asserts a Silver→Gold upgrade on 2026-09-08, before the visit. The seed agrees: an upgrade_proration charge and a dues_payment were posted 2026-09-08, and the agreement is Gold. Gold's premium pct 50 applies on the 09-26 completion date. Consistent.
- Verdict per relationship:
  - Policy self-consistency: PASS on this world.
  - Problem tree: PASS.
  - Factors: **SOURCE-FACTOR RED**.
  - Unique solution: PASS.

## findings

1. **SOURCE-FACTOR RED — no honest `method` factor in courtesy_discount or special_order_release** (charter finding F-G3).
   - shipment_count_window ("last 24 / 12 / 6 months") only changes `within_months` in one XCOUNT.
   - unit_enrollment_multiplier (0.75 / 0.9 / 1) is a number inside `d_deposit: RND(d_parts * d_pct / 100 * d_mult, 2)`.
   - Consequence here: 2 of the task's 3 computations score with zero honest method factors. On this world each of the two factors moves the score (35.76 vs 37.25; 187.74 vs 180.74), but neither tests a method.
   - Affected: `factors[].effect` of service_ext_courtesy_discount and service_ext_special_order_release, and their rule sentences.
2. **SOURCE-FACTOR RED — ladder conditions the business does not weigh** (charter finding F-G4).
   - tune_up_count_window takes its look-back window from dues billing cadence. Here: annual → 24 months, count 4. The term-only count gives 107.10 instead of 113.05.
   - enrollment_tenure_points and prepaid_renewal_points carry an "active agreement" conjunct that holds for every customer who reaches the member premium discount write.
   - Affected: service_ext_member_premium_discount factors and rule sentences.
3. Observation — F-G2 (compute does not filter for completed tune-ups) has no consequence here, because the call's unit has no plan_tuneup_visit row of any kind.
4. Observation O1-1 — the paid tune-up on a non-enrolled furnace while the agreement still shows visits_remaining 1 is consistent with the base rule but is not explained on any record.
5. Observation O1-2 — the persona background names her as a veteran. That fact is already on the profile and is not a request.
6. Near-misses are present in every computation:
   - 2024-04-15 tune-up at 29 months.
   - 2026-09-08 card_by_phone payment.
   - The heat pump's tune-ups, which do not count for the furnace call.

## revision_2

### source_derivation_frozen (revision 2)

- Inputs:
  - `/tmp/erl37/views_r2/repair_and_emergency_service/task_1.masked.json`, sha256 fd43bd73… — identical to round 1, so the world is unchanged.
  - service.extended.yaml d4b4f03e… (changed). Because the charter changed, the task-level derivation is redone.
- contamination_disclosure: round-1 GT of this task is known to this auditor (read in round 1). Round-2 GT has not been read.

### policy_self_consistency (r2, this task)

- Cited from `_difficulty.md` → revision_2.
- F-G2 is closed. On this world the call's unit (the furnace) has no plan_tuneup_visit row of any kind, so the result is unchanged.
- O-R2-2 (combining sentences) on this world: the customer holds 4 products (active agreement, closed installation, active contract ending 2026-11-08, active filter subscription). Both combination rules therefore take their "every award / both reductions" tier, which coincides with reading each "adds / takes off" sentence on its own. Both readings give the same values here, so there is no second answer on this world.
- Waits: none.

### problem_chain (r2)

- Unchanged: special_order_release ← {member_premium_discount, courtesy_discount}, both value_input, both unmet at opening (same rows as round 1). User-owned root, acyclic, and the two leaves commute.
- Load-bearing runs:
  - skip premium discount → release payment 230.75 + 74.16 = 304.91;
  - skip courtesy discount → 154.95 + 74.16 = 229.11.
  Both differ from gold.

### task_independent_derivation (r2)

1. **Member premium discount.**
   - Gold 50. Tenure 102 months → +15. Annual billing with auto-renew → +5.
   - Window: 9 consecutive terms (≥ 3rd term) → 24 months → count 4 (2024-04-15 excluded) → +10.
   - Installation closed 58 months ago → +10. MERV 13 → +5.
   - 95 % of 119.00 = **113.05**.
2. **Courtesy discount.**
   - Weekend 10. Terms 9 → +4. two_stage → +3.
   - Shipments in the last 24 months: 4 → +3. Matched-system contract → +3. Card on file 2026-03-20 → +2.
   - Products held: 4 (≥ 3) → every award is added (+15). Rate 25 → 149.00 × 25 % = **37.25**.
3. **Release payment.**
   - Visit balance 117.70.
   - Rate: priority 35. Reductions: installation 14695 → 10; dues payments in the last 24 months 3 → 5. With 4 products both are taken off → 20 %.
   - Unit multiplier: the furnace has no completed plan tune-up → 0.9.
   - Deposit RND(412 × 20 % × 0.9) = 74.16. Release = **191.86**, by card.
4. **Terminal state.** Three new lines; ticket_balance 1018.76 − 113.05 − 37.25 − 191.86 = 676.60.

### factor_weight (r2)

member_premium_discount (113.05): substituting each factor's baseline gives 95.20 / 107.10 / 107.10 (window → term count 1) / 101.15 / 101.15 / 107.10. Baseline alone: 59.50. Near-miss: the 2024-04-15 tune-up at 29 months. Honest method; tier conditions realistic.

courtesy_discount (37.25): substituting each factor's baseline gives
- terms 0 → 31.29;
- installation 0 → 32.78;
- shipments 0 → 32.78;
- contract 0 → 32.78;
- payments 0 → 34.27;
- bonus_combination baseline (single largest award = 4) → rate 14 → 20.86.

Baseline alone: 14.90. Near-miss: the 2026-09-08 card_by_phone payment and the 2025-03-20 card_on_file payment (18 months back). Honest method.

special_order_release (191.86): substituting each factor's baseline gives
- rate 50 → 247.48;
- installation reduction 0 → 228.94;
- dues reduction 0 → 210.40;
- multiplier 1 → 200.10;
- reduction_combination none → 247.48.

Baseline alone: 323.70. Near-miss: the heat pump's completed tune-ups, which do not count for the furnace call. Honest method.

Counts: met in every computation. Multi-source factors: dues_payment_points, dues_payment_history_points, the two combination factors. Cross-difficulty factors are present and seeded.

### frozen verdict (r2, pre-reveal)

PASS on all four relationships, pending comparison.

### source_gt_comparison (r2)

- Reveal: round-2 `tasks/1.json` was first read at 2026-10-05T17:05:01Z, after the revision_2 freeze (hashes at 17:04:55Z).
- Need, authorisation, read set, object, owner and order: the same.
- Parameters: 113.05 / 37.25 / 191.86, card. Same.
- Terminal state: same.
- Closest alternatives, both excluded by the rule:
  - unit multiplier 0.75 (counting the heat pump's tune-ups) — the rule reads the tune-ups of the unit the call concerns;
  - a deposit without reductions (rate 35 %) — the rule takes both reductions off when 4 products are held.
- Problem tree vs prerequisite_closure:
  - Edges, kinds, gates and order: identical.
  - Load-bearing figures: GT 304.91 / 229.11, mine 304.91 / 229.11. Identical.
- Factor sensitivity: identical to my recomputation.
  - member premium: 95.2 / 107.1 / 107.1 / 101.15 / 101.15 / 107.1, baseline 59.5.
  - courtesy: 31.29 / 32.78 / 32.78 / 32.78 / 34.27 / 20.86, baseline 14.9.
  - special order: 247.48 / 228.94 / 210.4 / 200.1 / 247.48, baseline 323.7.
- O1-1: design_rationale now records that the agreement covers one system (the heat pump), so the furnace tune-up is a paid one. This agrees with the seed (every plan tune-up is on 1dcde166; systems_covered 1). Closed.
- Verdict (r2): **PASS** on all four relationships. Policy self-consistency, problem tree, factors and unique solution all hold.

### findings (r2)

- F-G2 closed (no consequence on this world, as in round 1).
- F-G3 closed for courtesy_discount (bonus_combination) and special_order_release (reduction_combination, with the multiplier relabelled parameter).
- F-G4 closed for member_premium_discount: the window now depends on consecutive terms, and the scope conjuncts are removed.
- O-R2-2 has no consequence here: with 4 products held, the combining sentences coincide with each award sentence read on its own.
- O-R2-3 (courtesy combination baseline "single largest award") has no adverse consequence: the factor bears weight (20.86 vs 37.25) and the all-baseline result equals baseline.rule (14.90).
- No regression found.

## revision_3

### source_derivation_frozen (revision 3)

- Inputs: task_1 masked view fd43bd73… (unchanged since round 1); charter cb8487ad… (changed); tools unchanged.
- contamination_disclosure: round-1 and round-2 GT of this task is known to this auditor. Round-3 GT has not been read.

### derivation (r3)

- The world is unchanged. The only charter changes that touch this task are:
  - the courtesy wording ("earns a courtesy bonus award");
  - the courtesy fall-through ("with one or none, no bonus award is added");
  - the special-order wording ("earns a deposit reduction");
  - the halfway-cent sentence;
  - the member_premium compute_basis fix.
- With 4 products held (active agreement, closed installation, active contract to 2026-11-08, active filter subscription), both combination factors take their "every award / both reductions" tier, as in revision_2.
- Values are unchanged:
  - member premium discount 95 % × 119.00 = 113.05;
  - courtesy 25 % × 149.00 = 37.25;
  - release payment 117.70 + RND(412 × 20 % × 0.9) = 117.70 + 74.16 = 191.86, by card.
- Factor weights are as in revision_2, except courtesy bonus_combination. Its baseline is now "no award", giving rate 10 and 14.90. That still differs from gold, so the factor bears weight, and it equals the all-baseline result 14.90.
- Load-bearing runs: 304.91 / 229.11.

### frozen verdict (r3, pre-reveal)

PASS on all four relationships.

### source_gt_comparison (r3)

- Reveal: round-3 tasks/1.json was first read at 18:31:19Z, after the freeze.
- Writes: 113.05 / 37.25 / 191.86, card. Owners, order, objects and terminal state are identical.
- prerequisite_closure: edges and order identical; load-bearing figures 304.91 / 229.11 identical.
- Factor sensitivity and baselines are identical:
  - member premium 95.2 / 107.1 / 107.1 / 101.15 / 101.15 / 107.1 (59.5);
  - courtesy 31.29 / 32.78 / 32.78 / 32.78 / 34.27 / **14.9** (14.9). The bonus_combination figure is now under the "no award" baseline, which matches my recomputation (O-R2-3 closed).
  - special order 247.48 / 228.94 / 210.4 / 200.1 / 247.48 (323.7).
- Verdict (r3): **PASS** on all four relationships.

### findings (r3)

- Closed: O-R2-3 (courtesy baseline is now "no award", matching baseline.rule) and O-R2-2 (the courtesy and special-order award sentences no longer add to the rate on their own).
- No open findings; no regression.
