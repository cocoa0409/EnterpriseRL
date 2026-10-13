# Policy-task audit — repair_and_emergency_service / task 0

## source_derivation_frozen

- Auditor: independent policy-task auditor. Freeze time: 2026-10-05T15:55Z.
- Inputs: `/tmp/erl37/views/repair_and_emergency_service/task_0.masked.json` (sha256 04797b9e28e1fc16b686564e0ea2b9e3bdfba1c6f216d59d8452f8926ff2b8d0: frozen_time, user_scenario, initial_state), service.extended.yaml (4357430a…4c23a), task_tools.py (b2417a58…6be53), blueprint products (plan/filter/install/warranty tier parameters), share_tools.py.
- Masked and unread at freeze: evaluation_criteria, computations, db_closure, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure. `tasks/0.json` not opened.
- contamination_disclosure: none. The gate snapshot shows only counts (actions 20, computations 4, factors 18, …), no scored values.

World (frozen_time 2026-10-05 10:40 EDT; date of handling 2026-10-05):
- customers 3309aee3…: Harold Kowalczyk, discount_program senior_65_plus, phone 6145553271, PIN 7340.
- equipment 97893bee… central AC (R-410A, Harbison-installed 2016-05-23); c3c4da05… gas furnace.
- service_tickets 3f6cacf1…: Standard Service Call, status completed, scheduled 2026-07-17, window 08:00-12:00, arrived_at 2026-07-17T13:12, symptom no_cool, equipment 97893bee (AC), completed_date 2026-07-17, ticket_balance 840.45.
- service_lines on 3f6cacf1: diagnostic_fee 89.00 (66c5d28e); member_diagnostic_rate 89.00; repair_parts txv_replace 196.00; repair_labor txv_replace 689.00; member_repair_discount 29.40 and 103.35; refrigerant 3.8 lb 338.20 (8b2b8c20); payment card 250.00. Sum: 1312.20 − 471.75 = 840.45 = ticket_balance (consistent). No late_arrival_credit, member_refrigerant_allowance or late_payment_charge line.
- plan_agreements 91333d08…: Comfort Club Silver, active, enrolled 2020-06-15, term 2026-06-15..2027-06-14, monthly, auto_renew true, consecutive_terms 7. Silver tier (plan.yaml): refrigerant_allowance_lbs_per_term 0.0, scheduling_priority priority, no_heat_no_cool_response_hours 0, diagnostic_fee_member_usd 0, repair_discount_pct 15.
- plan_billing_entries: monthly dues charges and ach_autopay dues payments posted 2026-06-15, 07-15, 08-15, 09-15; no late_fee line.
- plan_service_entries: completed tune-ups 2025-06-30 (AC), 2025-11-03 (furnace), 2026-06-22 (AC); visit grants 2025-06-15, 2026-06-15.
- install_projects a5decb52…: Advantage Series, closed 2016-06-03.
- warranty_contracts 5ae7d403…: 5-Year Labor Protection on 97893bee (the AC), active, coverage 2023-06-09..2028-06-08; only claim entry is the activation limit grant (no pending claim).
- filter_subscriptions 39b19309…: Pleated MERV 11 (merv 11, depth 1 in), active.

### policy_self_consistency (this task only)

- Charter-global conclusions cited, not restated: `_difficulty.md` → policy_conflict_scan, rule_compute_equivalence, action_binding_and_uuids, prerequisite_graph, prerequisite_sentences, override_declarations.
- F-G1 (late-payment compute ignores "not yet charged"): on this world the call carries no late_payment_charge line, so "periods counted and not yet charged" = periods counted; rule and compute agree here. No consequence on task 0.
- Override consequences on this world:
  - member_benefits' term-wide allowance vs the extended per-call allowance: base on Silver (0.0 lb/term) gives 0; extended gives a positive value (below). Declared override; merged reading unique (extended governs).
  - discount_stacking's per-line cap vs on_time_credit: the diagnostic fee line 66c5d28e is already fully offset by the 89.00 member_diagnostic_rate, so under the base per-line cap the on-time credit would be 0.00; the declared override measures it against the invoice balance. Declared; unique.
  - late-payment grace/per-charge sentences: declared; base would give grace 30, one 1.5 % charge per 30 days; extended governs.
- Handling time: each write evaluated on initial_state + preceding synchronous writes: on-time credit and refrigerant allowance on the opening world (neither reads the other except through the on-time cap, see problem_chain); late-payment charge after both; first installment after the late-payment charge.
- Real-world waits: none. Every input is a seeded row, a preceding write's line/balance, or the customer's payment-method choice. The base clause "A balance that is owing only because a protection contract claim … is still being decided accrues no late-payment charge" does not apply: warranty_claim_entries holds only the activation grant (no claim filed, nothing pending).

### problem_chain

Root problem (raised by the customer): settle the past-due balance on ticket 3f6cacf1 under a payment arrangement, first installment today (service_ext_past_due_installment; on_request; owner user).

Walk:
1. Past-due installment rule: "The first installment of a payment arrangement is not taken until the invoice carries a late-payment charge for every charging period that has run past the customer's late-payment grace." At opening: day 80 after completion > grace (45, below); no late_payment_charge line on 3f6cacf1 → unmet. The rule that writes late-payment charges is service_ext_late_payment_charge.
2. Late-payment rule: "No late-payment charge is figured until the invoice of a call whose technician arrived after the end of the booked window and the arrival grace carries the late-arrival credit owed on it." Arrived 13:12 vs window end 12:00 + 10-min grace (Silver = priority) → late; class credit 25 > 0; no late_arrival_credit line → unmet. Writer: service_ext_on_time_credit.
3. Late-payment rule: "The late-payment charge is fixed only after every refrigerant line on an active member's call carries the member refrigerant allowance line owed on it." Agreement active; refrigerant line 8b2b8c20 has no member_refrigerant_allowance naming it; allowance owed > 0 (below) → unmet. Writer: service_ext_refrigerant_allowance.
4. On-time credit rule and refrigerant allowance rule carry no prerequisite sentence → leaves.

Derived tree: past_due_installment ← late_payment_charge (value_input: p_bal and p_late) ← {on_time_credit (value_input: l_bal), refrigerant_allowance (value_input: l_bal)}. Prerequisite problems n = 3, value_input edges 3 ≥ max(n−1,1) = 2; acyclic; owner=user problem present (root, pay_past_due_installment_4c600ae8, handed to the customer). Topological order: {on_time_credit, refrigerant_allowance} (either order) → late_payment_charge → past_due_installment. Isomorphic to the declared `prerequisite` edges.

Load-bearing runs (skip one write, replay the rest):
- skip on-time credit: l_bal = 840.45 − 151.30 = 689.15 → late charge 3.45 (vs 3.07); installment changes.
- skip refrigerant allowance: l_bal = 840.45 − 75.00 = 765.45 → late charge 3.83 (vs 3.07).
- skip late-payment charge: p_bal 614.15, p_late 0 → first installment 0 + RND(614.15/4) = 153.54 (vs 156.61).
Every edge bears weight.

Parallel edges (on_time_credit, refrigerant_allowance share ticket_balance): on-time credit is capped at the balance when it posts; balance before either is 840.45, after the allowance 689.15 — both far above the 75.00 credit, so the cap never binds and both orders give the same terminal state.

Tools judge no prerequisite: every body in task_tools.py writes one line and moves ticket_balance by the amount passed (`_difficulty.md` → action_binding_and_uuids).

Persona: raises only the payment arrangement. It does not name the late charge, the on-time credit or the allowance. Its conditional lines ("Only if the agent asks whether the technician arrived on time…", "If the agent tells you that something has to be added to or taken off the bill … go ahead") are passive responses that authorise the corrective writes without pointing at them. It closes after the payment confirmation, which is where the derived solution ends.

### task_independent_derivation

Act now (no wait, no refusal): completed call, balance owing, 80 days > 30 since completion (past-due eligibility); customer verified by phone + PIN (find_customers → verify_customer_identity).

1. On-time credit (agent; post_on_time_credit_a011cbd0; handling time = opening world).
   - Class credit (Standard) 25 > 0. Grace: active Silver, scheduling_priority priority → 10 min. Cut-off 2026-07-17T12:10; arrived 13:12 → late. Minutes past window end + grace = 62 → "more than 60 and no more than 120" → multiplier 1.5.
   - Level: active agreement and call's unit 97893bee under active contract 5ae7d403 → 40.
   - Comfort addition: symptom no_cool, active agreement, Silver no_heat_no_cool_response_hours 0 (no guarantee) → 15.
   - Amount = RND(40 × 1.5) + 15 = 75.00; balance 840.45 → cap not binding → **75.00**. Params: ticket_id 3f6cacf1…, source_line_id 66c5d28e… (diagnostic fee line), customer_id 3309aee3…, agreement_id 91333d08…, recall_of_ticket_id "".
2. Refrigerant allowance (agent; post_refrigerant_allowance_39aa6c52; opening world).
   - Billed: 3.8 lb, 338.20 → 89.00/lb. Tier pounds (Silver) 0.0.
   - Loyalty: 7 consecutive terms → +0.5. Maintenance count: monthly + auto-renew → completed tune-ups in last 24 months (whole months < 24): 2025-06-30 (15), 2025-11-03 (11), 2026-06-22 (3) → 3 → +0.5. Installation closed 2016-06-03 → 124 whole months ≥ 120 → +0.2. Unit 97893bee under active contract → +0.3. Active filter MERV 11 < 13 → +0.2.
   - Allowance 1.7 lb; covered = min(3.8, 1.7) = 1.7; value = 1.7 × 89.00 = **151.30**, quantity 1.7. Params: source_line_id 8b2b8c20…, agreement_id 91333d08…, customer_id, recall "".
3. Late-payment charge (agent; post_late_payment_charge_b790dc9b; after 1 and 2).
   - l_bal = 840.45 − 75.00 − 151.30 = 614.15. Days since completion: 80.
   - Grace: ach_autopay dues drafts with < 3 whole months to 2026-10-05: 09-15, 08-15, 07-15 (06-15 is exactly 3 whole months → excluded) → 3 → 45 days.
   - Period: active, billed monthly → 35 days. Periods: 80 − 45 = 35 days past grace; first period opens on day 46; a further full period would complete on day 81 → **1** period (compute's `int((80−45−1)/35)+1 = 1` agrees).
   - Rate: no late_fee in plan_billing_entries → 1 %. Relief: enrolled 2020-06-15 → 75 whole months ≥ 60 → 0.5.
   - Charge = RND(614.15 × 1/100 × 1 × 0.5) = RND(3.07075) = 3.07 ≥ 2.00 → **3.07**. Opening-world contrast (l_bal 840.45): 4.20.
4. First installment (customer; pay_past_due_installment_4c600ae8; after 3; handed over).
   - p_bal = 614.15 + 3.07 = 617.22. Installments: 7 consecutive terms ≥ 6 → 3; filter active, 1-inch (thinner) → +1 → 4. Minimum: call's unit under active contract → 300; 617.22 ≥ 300 → n = 4.
   - Up front: active agreement with autopay drafts in last 12 months → late-payment charges alone = 3.07.
   - First installment = 3.07 + RND((617.22 − 3.07)/4) = 3.07 + 153.54 = **156.61**; payment_method card (persona: debit card, "which is a card payment"). Opening-world contrast (no late charge, no credits): p_bal 840.45 → 0 + RND(840.45/4)=210.11.
- Terminal state: four new service_lines (late_arrival_credit 75.00, member_refrigerant_allowance 1.7 lb/151.30, late_payment_charge 3.07, payment 156.61 card); ticket_balance 840.45 − 75.00 − 151.30 + 3.07 − 156.61 = 460.61; status stays completed.
- Read set: find_customers, verify_customer_identity, find_service_tickets, find_service_lines, find_plan_agreements, find_plan_billing_entries, find_plan_service_entries, find_install_projects, find_warranty_contracts, find_filter_subscriptions (+ KB tier parameters for Silver and MERV 11). All reachable.

Second-reading check on the period count (the world sits on the boundary 35 = 35): reading "one for the first day past the grace plus one for each full period that has run past the grace" would give 2 periods → 6.14 and a first installment of 6.14 + RND(614.15/4) = 159.68. This reading counts the first period twice (once for its first day, once as a "further" full period) and contradicts the rule's own day-0 convention measured from the first day past the grace; it is not defensible as a second answer. Recorded as observation O0-1, not red.

### factor_weight

Gold candidates above; baseline substitutions recomputed on the handling-time world of each write.

refrigerant_allowance (gold 151.30):
| factor | label honest? | tier taken / rows | baseline input | value under baseline |
| --- | --- | --- | --- | --- |
| consecutive_term_pounds | parameter, yes | ≥6 terms (consecutive_terms 7) → 0.5 | 0 | 1.2 lb → 106.80 |
| maintenance_count_window | method, accepted (term-only fall-through) | monthly+auto-renew → 24-month count 3 | term count = 1 (2026-06-22) | count 1 → 0.3 → 1.5 lb → 133.50 |
| maintenance_count_pounds | parameter, yes | count 3 → 0.5 | 0 | 106.80 |
| harbison_installation_pounds | parameter, yes | closed 124 months → 0.2 (install a5decb52) | 0 | 133.50 |
| protection_contract_pounds | parameter, yes | call's unit under 5ae7d403 → 0.3 | 0 | 124.60 |
| filter_subscription_pounds | parameter, yes | active MERV 11 → 0.2 (39b19309) | 0 | 133.50 |
Baseline rule alone: tier pounds 0.0 → allowance 0 → 0.00 (definite, ≠ gold). Near-miss: the 2025-06-30 AC tune-up (counted only under the 24-month window; excluded under the term or 12-month method) and the plan_visit_grant rows (not completed visits). Stamp: none. Cross-difficulty rows present (plan, install, warranty, filter).

on_time_credit (gold 75.00):
| factor | label honest? | tier / rows | baseline | value |
| --- | --- | --- | --- | --- |
| arrival_grace | parameter, yes | priority → 10 min (Silver) | 15 | 57 min late → mult 1 → 55.00 |
| lateness_multiplier | **labelled method, is a number** (2/1.5/1 in one product) | 62 min → 1.5 | 1 | 55.00 |
| credit_level | parameter, yes; multi-source | active + unit under contract → 40 | class 25 | 52.50 |
| comfort_call_addition | parameter, yes | no_cool + no response guarantee → 15 | 0 | 60.00 |
Baseline rule alone: class credit 25.00, earned (13:12 > 12:15) → 25.00 ≠ gold. Near-miss: arrival 57 minutes past the standard-grace cut-off (≤ 60) vs 62 minutes past the customer's grace; the furnace c3c4da05 carries no contract. Honest `method` factors: 0 (fails the floor; F-G3).

late_payment_charge (gold 3.07):
| factor | label honest? | tier / rows | baseline | value |
| --- | --- | --- | --- | --- |
| late_payment_grace | parameter, yes; multi-source | 3 ach_autopay drafts in 3 months → 45 | 30 | 2 periods → 6.14 |
| charging_period_length | parameter (unreal condition, F-G4) | monthly → 35 | 30 | 2 periods → 6.14 |
| late_payment_rate | parameter, yes; multi-source | no late fee 24 m → 1 % | 1.5 % | 4.61 |
| tenure_relief | **labelled method, is a number** | 75 months → 0.5 | 1 | 6.14 |
Baseline rule alone: grace 30, period 30, 1.5 %, relief 1 → 2 periods → RND(614.15 × 1.5 % × 2) = 18.42 ≠ gold. Near-miss: the 2026-06-15 autopay draft (exactly 3 whole months, excluded). Honest `method` factors: 0 (F-G3). Observation O0-2: plan_billing_entries are seeded only from 2026-06, so the 24-month "no late fee" tier rests on absence over a mostly unseeded window.

past_due_installment (gold 156.61):
| factor | label honest? | tier / rows | baseline | value |
| --- | --- | --- | --- | --- |
| installment_count | parameter, yes | 7 terms → 3 | 1 | n=2 → 310.15 |
| filter_subscriber_installments | parameter (unreal condition, F-G4) | active 1-inch → +1 | 0 | n=3 → 207.79 |
| arrangement_minimum | parameter, yes | unit under contract → 300 | 750 | 617.22 < 750 → n=1 → 617.22 |
| up_front_amount | method, honest; multi-source | autopay drafts in 12 m → late charges alone | 0 up front | 154.31 |
Baseline rule alone: single payment of the whole balance → 617.22 ≠ gold. Near-miss: none found — the warranty contract is on the call's unit, every autopay draft lies well inside 12 months, the filter is plainly 1-inch, the terms count plainly ≥ 6; every factor is applied by inspection. (finding T0-F3)

Task-level counts: multi-source factors present (credit_level, late_payment_grace, late_payment_rate, up_front_amount); cross-difficulty present and seeded (plan, install, warranty, filter rows all in initial_state). Per computation 4–6 factors with ≥2 parameter: met; ≥1 honest method: met for refrigerant_allowance and past_due_installment, **not met** for on_time_credit and late_payment_charge.

### frozen verdict (pre-reveal)

- Policy self-consistency: PASS for this world (charter-global F-G1 has no consequence here).
- Problem tree: PASS.
- Factors: **SOURCE-FACTOR RED** (F-G3 on on_time_credit and late_payment_charge; F-G4 on late_payment_charge.charging_period_length, refrigerant_allowance.maintenance_count_window, past_due_installment.filter_subscriber_installments, refrigerant consecutive_term_pounds' scope conjunct; T0-F3 no near-miss in past_due_installment). Each factor bears weight on this world.
- Unique solution: PASS pending GT comparison (derived sequence and values above).

## source_gt_comparison

- Reveal: `tasks/0.json` first opened at 2026-10-05T15:49:36Z, in the same shell command that first recorded the frozen files' hashes (`_difficulty.md` fcc16773…cfe3, `task_0.md` f2d0986b…db7f, `task_1.md` 687e0a9e…dcca), so both tasks' derivations were on disk before any GT was read. Timestamp correction: the "Freeze time" values written in the headers of task_0.md (15:55Z) and task_1.md (16:02Z) were estimates and are wrong. The hash record at 15:49:36Z is the actual freeze evidence. The frozen text above is left as it was written.
- Need / authorisation / timing: same. The customer wants a payment arrangement with the first payment today by debit card; gold has the owner=user payment handed to him.
- Necessary read set: same, plus gold reads find_warranty_claim_entries. I had used the claim rows to rule out a pending claim and to rule out a coverage credit, but did not list the finder among the reads. Not a difference in the solution.
- Act now: same. Eligibility (80 days > 30, completed, balance owing): same.
- Object: ticket 3f6cacf1, diagnostic-fee line 66c5d28e, refrigerant line 8b2b8c20, agreement 91333d08: same.
- Parameters: refrigerant allowance quantity 1.7 / amount 151.30 — same. On-time credit 75.00 — same. Late-payment charge 3.07 — same. First installment 156.61 card — same. recall_of_ticket_id "" — same.
- Tool / owner / order: gold runs allowance, then on-time credit, then late charge (all agent), then the installment (user). My derivation lets the allowance and the credit run in either order. Gold's order_uniqueness says the two commute (same DB hash). Same.
- Terminal state: four new lines; balance 460.61. Same: gold's narrative says 617.22 after the charge, and 617.22 − 156.61 = 460.61.
- Closest alternative candidate and why it is excluded: two periods → late charge 6.14 → installment 159.68. It is excluded by the rule's own counting: the first period opens on day 46, and a further full 35-day period completes only on day 81 (O0-1). This is policy text, not a GT choice.
- Problem tree vs `prerequisite_closure`: root service_ext_past_due_installment = mine. Edges past_due→late (value_input, p_bal), late→on_time (value_input, l_bal) and late→refrigerant (value_input, l_bal) = mine. Opening falsity: GT says the July 17 completion is 80 days back, no late charge, arrival 13:12 > 12:10, and the 3.8 lb refrigerant line has no allowance. All values equal mine. resolution_order [refrigerant, on_time, late, past_due] is one of my two admissible orders. Load-bearing figures: GT 153.54 / 3.45 / 3.83, mine 153.54 / 3.45 (skip on-time) / 3.83 (skip allowance). Same values on the same edges.
- factor_weight vs `computations[].factor_sensitivity` / `baseline_result`:
  - refrigerant_allowance: GT 106.8 / 133.5 / 106.8 / 133.5 / 124.6 / 133.5, baseline 0.0. Mine: identical.
  - on_time_credit: GT 55.0 / 55.0 / 52.5 / 60.0, baseline 25.0. Mine: identical.
  - late_payment_charge: GT 6.14 / 6.14 / 4.61 / 6.14, baseline 18.42. Mine: identical.
  - past_due_installment: GT installment_count **310.14**, mine **310.15**. Remaining GT figures 207.79 / 617.22 / 154.31, baseline 617.22: identical.
  - Root cause of the 310.14: 3.07 + (617.22 − 3.07)/2 = 3.07 + 307.075. The rule says "rounded to the cent half up", which gives 307.08 and 310.15. GT's 307.07 is binary-float `round()`: 307.075 is stored as 307.07499999999998863… The engine's RND is `lambda x, n=2: round(float(x), n)` (skills/erl-task-instantiate/scripts/check_compute.py:388). That is not half-up.
- Verdict per relationship:
  - Policy self-consistency: PASS on this world.
  - Problem tree: PASS.
  - Factors: **SOURCE-FACTOR RED**.
  - Unique solution: PASS. Gold equals the independent derivation on every scored parameter, owner, order and terminal state.

## findings

1. **SOURCE-FACTOR RED — no honest `method` factor in on_time_credit or late_payment_charge** (charter finding F-G3, `_difficulty.md` → factor_ladders / findings).
   - Symptom: lateness_multiplier (2 / 1.5 / 1) and tenure_relief (0.5 / 0.75 / 1) are labelled `method`. Each tier only puts a different number into the same product.
   - Evidence: `t_amount: RND(t_level * t_mult, 2) + t_bonus`; `l_raw: RND(l_bal * l_rate / 100 * l_periods * l_relief, 2)`.
   - Consequence on this task: both computations score with zero honest method factors, below the floor of one. The method floor is not met for 2 of the task's 4 computations.
   - Affected: service.extended.yaml, `factors[].effect` of service_ext_on_time_credit and service_ext_late_payment_charge, and the rule sentences defining those multipliers.
2. **SOURCE-FACTOR RED — ladder conditions the business does not weigh** (charter finding F-G4).
   - charging_period_length is set by dues billing cadence. Here: monthly → 35 days. Substituting 30 changes the charge from 3.07 to 6.14.
   - maintenance_count_window is set by billing cadence and auto-renew. Here: 24-month window. The term-only count gives 133.50 instead of 151.30.
   - filter_subscriber_installments is set by filter depth. Here: +1. Without it the installment is 207.79 instead of 156.61.
   - consecutive_term_pounds has an "agreement active" conjunct that holds for every customer who reaches the allowance write.
   - Each of these conditions moves a scored value on this world, so the score depends on conditions the line of business does not weigh.
   - Affected: the corresponding `factors[]` and rule sentences.
3. **SOURCE-FACTOR RED — no near-miss in the past_due_installment computation** (T0-F3).
   - Every factor's evidence is plainly present or absent: the contract is on the call's unit, all four autopay drafts fall well inside 12 months, the filter is plainly 1-inch, and there are 7 terms against a threshold of 6.
   - No record exists that a careless reader would count and the rule excludes.
   - Affected: initial_state (seed design) for the installment computation.
4. **SOURCE-FACTOR RED — recorded factor sensitivity contradicts the rule's rounding** (T0-F4).
   - computations[past_due_installment].factor_sensitivity[installment_count].baseline_result = 310.14, and factor_trace says "baseline 1 -> n = 2 -> 310.14".
   - Recomputed under the rule's "rounded to the cent half up": 310.15.
   - The factor still bears weight (both figures are far from 156.61), but the proof's figure is wrong.
   - Root cause: the evaluator's RND is float `round()`, not half-up. No gold value of this task falls on a binary .xx5 tie, so the gold is unaffected. This was checked for 151.30, 75.00, 3.07075→3.07 and 153.5375→153.54.
   - Affected: tasks/0.json computations[3].factor_sensitivity and factor_trace; the RND primitive (scripts/check_compute.py:388) used to produce them.
5. Observation — F-G1 ("not yet charged" missing from compute) has no consequence here, because the call has no prior late charge.
6. Observation O0-1 — the period count sits exactly on the boundary (35 days past a 45-day grace with 35-day periods). The rule's counting settles it at one period.
7. Observation O0-2 — plan_billing_entries are seeded only from 2026-06, so the "no late fee in 24 months" tier rests on absence over a window that is mostly unseeded.
8. Observation — gold reads find_warranty_claim_entries. My frozen read set omitted it, although my no-pending-claim argument used those rows.

## revision_2

### source_derivation_frozen (revision 2)

- Inputs:
  - `/tmp/erl37/views_r2/repair_and_emergency_service/task_0.masked.json`, sha256 8acd4a54fd17e02a93f4e927c256248d549f783237c87b901721c54afb10bf28. This differs from round 1, so everything is re-derived.
  - service.extended.yaml d4b4f03e…745b (changed).
  - task_tools.py b2417a58… (unchanged).
- Masked and unread at freeze: every round-2 GT field of tasks/0.json.
- contamination_disclosure: round-1 GT of this task (round-1 scored values, factor_sensitivity, prerequisite_closure, design_rationale) was read in round 1 and is known to this auditor. Round-2 GT has not been read.

World diff vs round 1. user_scenario and frozen_time (2026-10-05 10:40 EDT) are unchanged.
- The call has moved to scheduled/completed 2026-07-07: booked 07-02, dispatched 07-07T07:50, arrived 07-07T13:12. The invoice lines are unchanged except their posted_date (2026-07-07); ticket_balance is still 840.45. The persona's "back in July" still holds.
- plan_billing_entries now run back to 2024-08:
  - monthly dues charges and ach_autopay payments, 15th of each month;
  - a Comfort Club `late_fee` 7.50 posted 2024-08-31;
  - two card_by_phone payments on 2024-09-03 (the 2024-08 dues and the late fee).

### policy_self_consistency (r2, this task)

- Charter-global conclusions are cited from `_difficulty.md` → revision_2.
- F-G1 is closed in the charter. On this world there is no prior late_payment_charge line, so periods already charged = 0.
- O-R2-2 consequence on this world:
  - The conditional convention gives 1.5 periods (part payment: 250.00 / 1312.20 = 19.05 % of charges).
  - The unconditional sentence 4, read alone, gives 2 periods (started count).
  - The two readings produce different values (see task_independent_derivation).
- Handling time and waits: as in round 1. There is still no pending warranty claim (activation grant only), and every input is seeded or produced by a preceding write.

### problem_chain (r2)

- The tree is unchanged: past_due_installment ← late_payment_charge (value_input) ← {on_time_credit, refrigerant_allowance} (value_input).
- Opening falsity:
  - no late_payment_charge line, with day 90 > 45 grace;
  - arrived 13:12 > 12:10 (window end + priority grace) with class credit 25 and no late_arrival_credit line;
  - refrigerant line 8b2b8c20 named by no allowance line, agreement active.
- n = 3, 3 value_input edges, user-owned root, acyclic. The order is the same as round 1, and the two leaves commute (the on-time credit is far below the balance either way).
- Load-bearing runs:
  - skip on-time → late charge 5.17 (vs 4.28);
  - skip allowance → 5.42;
  - skip late charge → installment 142.70 (vs 146.98).
- Tools judge nothing (task_tools.py unchanged). The persona raises only the payment arrangement.

### task_independent_derivation (r2)

1. **On-time credit.**
   - Standard class credit 25. Silver priority grace 10 min, so the cut-off is 12:10. Arrival 13:12 is 62 minutes past → multiplier 1.5.
   - Credit base: active agreement, and the call's unit 97893bee is under active contract 5ae7d403 → 10 % of repair labor 689.00 = 68.90 (≥ 25).
   - Comfort addition 15 (no_cool; Silver has no response guarantee).
   - Credit = RND(68.90 × 1.5) + 15 = 103.35 + 15 = **118.35**. The cap does not bind.
   - Lines named: diagnostic fee line 66c5d28e, agreement 91333d08.
2. **Refrigerant allowance.**
   - Tier 0.0 lb.
   - Terms 7 → +0.5.
   - Maintenance count: enrolled 75 months ago (≥ 24) → 24-month window. Tune-ups 2025-06-30, 2025-11-03, 2026-06-22 → 3 → +0.5.
   - Installation closed 124 months ago → +0.2. Contract on the call's unit → +0.3. Filter MERV 11 → +0.2.
   - 1.7 lb × 89.00 = **151.30** (quantity 1.7), naming refrigerant line 8b2b8c20.
3. **Late-payment charge.**
   - Balance l_bal = 840.45 − 118.35 − 151.30 = 570.80. Days = 90.
   - Grace: three ach_autopay drafts with fewer than 3 whole months elapsed (09-15, 08-15, 07-15; 06-15 excluded) → 45. Elapsed past grace = 45.
   - Counting convention: payments 250.00 against charges 1312.20 (19.05 %; something paid, less than a quarter) → prorated: 1 full period + 0.5 for the running period = 1.5.
   - Rate: no Comfort Club late fee in the last 24 months → 1 %. The 2024-08-31 late fee is 25 whole months back and excluded.
   - Relief: 75 months enrolled → 0.5.
   - Charge = RND(570.80 × 1 % × 1.5 × 0.5) = RND(4.281) = **4.28** (≥ 2.00).
   - Opening-world contrast (l_bal 840.45): 6.30.
4. **First installment.**
   - p_bal = 575.08; p_ledger (charges 1316.48 − discounts 491.40 − payments 250.00) = 575.08.
   - Installments: 7 terms → 3, plus 1 for a balance between 500 and 1000 → 4.
   - Minimum: the call's unit is under contract → 300; 575.08 ≥ 300.
   - Up front: autopay drafts in the last 12 months → late charges alone, 4.28.
   - First installment = 4.28 + RND(570.80 / 4) = 4.28 + 142.70 = **146.98**, by card.
5. **Terminal state.** Four new lines; ticket_balance 575.08 − 146.98 = 428.10.

Second reading (O-R2-2):
- Apply sentence 4 (started count) to this part-payer → 2 periods → late charge 5.71 → p_bal 576.51 → first installment 5.71 + 142.70 = 148.41.
- I take this reading as excluded: the rule's "How the charging periods are counted depends on what the customer has paid toward the call" is the specific provision, and sentence 4 is its nothing-paid tier.
- Recorded as an observation; see the comparison.

### factor_weight (r2)

refrigerant_allowance (151.30): substituting each factor's baseline gives
- terms → 106.80;
- window (term count 1 → 0.3) → 133.50;
- count pounds → 106.80;
- installation → 133.50;
- contract → 124.60;
- filter → 133.50.

Baseline alone: 0.00. Near-miss: the 2025-06-30 tune-up (inside the 24-month window, outside the term). Labels are honest.

on_time_credit (118.35): substituting each factor's baseline gives
- grace 15 → 57 minutes late, multiplier 1 → 83.90;
- multiplier 1 → 83.90;
- credit_basis = class 25 → 52.50;
- comfort 0 → 103.35.

Baseline alone: 25.00. Near-miss: 57 vs 62 minutes around the 60-minute line, and the furnace without a contract. One honest method (credit_basis); multi-source.

late_payment_charge (4.28): substituting each factor's baseline gives
- grace 30 → elapsed 60, prorated 2 periods → 5.71;
- convention 'started' → 2 periods → 5.71;
- rate 1.5 → 6.42;
- relief 1 → 8.56.

Baseline alone: 30-day grace, started count, 1.5 %, no relief → 2 periods → 17.12. Near-miss: the 2024-08-31 Comfort Club late fee, outside 24 months (the round-1 O0-2 history gap is now filled), and the 2026-06-15 draft. One honest method.

past_due_installment (146.98): substituting each factor's baseline gives
- installment count 1 → n 2 → 289.68;
- balance-size extra 0 → n 3 → 194.55;
- minimum 750 → one installment → 575.08;
- up front 0 → 143.77.

Baseline alone: 575.08.

**Near-miss: still none that a careless reader would count and the rule excludes.**
- Every autopay draft that decides up_front lies inside 12 months.
- The contract is on the call's own unit.
- The terms count is plainly 7.
- The balance-size tier reads the balance worked out from the invoice lines (575.08). That is a computed quantity, not a record a careless reader would wrongly count.
- The new 2024 card_by_phone payments are irrelevant to this computation's tiers.
- T0-F3 is therefore assessed as **not closed** (pending the reveal, in case GT names a near-miss record I overlooked).

Counts: 4–6 factors, ≥2 parameter, 1 honest method in each computation. Multi-source and cross-difficulty factors are present and seeded.

### frozen verdict (r2, pre-reveal)

- Policy self-consistency: PASS. O-R2-2 is an observation with its second reading quantified.
- Problem tree: PASS.
- Factors: **SOURCE-FACTOR RED**, on T0-F3 only (no near-miss in past_due_installment). All other round-1 factor findings are closed on this world.
- Unique solution: PASS pending comparison.

### source_gt_comparison (r2)

- Reveal: round-2 `tasks/0.json` was first read at 2026-10-05T17:05:01Z. The frozen revision_2 hashes were recorded at 17:04:55Z (task_0.md aa656a0a…1d82, task_1.md 0c81d7a2…6614, _difficulty.md e39f55e2…719e).
- Need, authorisation and timing; read set (gold again includes find_warranty_claim_entries); act now; object; owner and order: all the same.
- Parameters:
  - allowance 1.7 lb / 151.30 — same;
  - on-time credit 118.35 — same;
  - late-payment charge 4.28 — same;
  - first installment 146.98, card — same.
- Terminal state: same.
- Closest alternative: the started-count reading of sentence 4 (late charge 5.71, installment 148.41). The rule's own conditional sentence excludes it (O-R2-2). Gold took the prorated reading, as I did.
- Problem tree vs prerequisite_closure:
  - Edges, kinds and gates: identical.
  - resolution_order [refrigerant, on_time, late, installment] is admissible.
  - Load-bearing figures: GT 142.70 / 5.17 / 5.42, mine 142.70 / 5.17 / 5.42. Identical.
- Factor sensitivity: every figure is identical to my recomputation.
  - refrigerant: 106.8 / 133.5 / 106.8 / 133.5 / 124.6 / 133.5, baseline 0.0.
  - on-time: 83.9 / 83.9 / 52.5 / 103.35, baseline 25.0.
  - late: 5.71 / 5.71 / 6.42 / 8.56, baseline 17.12.
  - installment: 289.68 / 194.55 / 575.08 / 143.77, baseline 575.08.
  - **T0-F4 closed:** no recorded figure now contradicts half-up rounding.
- T0-F3, the reworker's claimed near-miss:
  - Claim (design_rationale and factor_trace): "the invoice's charges total 1312.20, which a careless reader would put in the 1,000-or-more tier".
  - Assessment: **not accepted as a near-miss record.**
    - The 1312.20 is the sum of charge lines that the rule itself counts; the rule then subtracts the discount and payment lines. No record is one the rule excludes (no window, channel or date filter is involved).
    - The obvious careless shortcut, reading the call's ticket_balance, gives the right tier whether taken at the opening (840.45) or at handling time (575.08). The balance-size tier is therefore applied by inspection.
    - Every other installment factor's evidence is still plainly present: all autopay drafts lie inside 12 months, the contract is on the call's unit, and there are 7 terms.
  - This is my judgement on the record, with moderate confidence. The coordinator may weigh it.
- Verdict (r2):
  - Policy self-consistency: PASS.
  - Problem tree: PASS.
  - Factors: **SOURCE-FACTOR RED** (T0-F3 only).
  - Unique solution: PASS.

### findings (r2)

Status of round-1 findings on this task:

| item | status | basis |
| --- | --- | --- |
| F-G1 | closed | charter fix; no prior late charge on this world |
| F-G3 | closed | on_time.credit_basis and late_payment.period_counting_convention are honest methods; the multipliers are relabelled parameter |
| F-G4 | closed | no billing-cadence or filter-depth conditions; scope conjunct removed |
| T0-F3 | **open** | SOURCE-FACTOR RED: the past_due_installment computation still has no record-level near-miss |
| T0-F4 | closed | all figures match half-up |
| O0-2 | closed | dues history seeded back to 2024-08, including a late fee 25 months back |
| O0-1 | superseded | the 35-day period is gone; period counting now goes through the convention |

New on this task:
- Observation O-R2-2: the late-payment rule states an unconditional started count (sentence 4) next to the conditional convention. The second reading gives a late charge of 5.71 and a first installment of 148.41, against gold 4.28 / 146.98. I take the conditional sentence as governing.
- No regression found:
  - the tree, persona, tools and closure are consistent;
  - the on-time cap is still non-binding (118.35 against balances of 689.15 or more);
  - the new history rows are consistent with the agreement: monthly autopay, and a single late fee settled by card_by_phone on 2024-09-03.

## revision_3

### source_derivation_frozen (revision 3)

- Inputs:
  - `/tmp/erl37/views_r3/repair_and_emergency_service/task_0.masked.json`, sha256 d7fd87b95280016f130c5600b88816b2a83948c01f6a90e7ba021beef518b1c6 (changed);
  - charter cb8487ad… (changed);
  - tools unchanged.
- contamination_disclosure: round-1 and round-2 GT of this task is known to this auditor. Round-3 GT has not been read.
- World diff vs revision 2: user_scenario and frozen_time are unchanged. One new call was added:
  - ticket 925ba6ea…, Standard Service Call, completed 2026-09-28, symptom poor_airflow, no unit named, ticket_balance 530.10;
  - its lines: diagnostic_fee 89.00, member_diagnostic_rate 89.00, repair_labor duct_cleaning_whole_home 589.00, and a member discount of 58.90 on that line (Silver duct_cleaning_discount_pct 10).
- Base consistency of the new call:
  - Standard class allows duct cleaning.
  - The member diagnostic rate brings the diagnostic fee to zero, so no diagnostic credit applies.
  - The courtesy program (senior, 10 %) does not replace the member duct-cleaning discount, because 10 % is not higher than 10 %.
  - The call is 7 days past completion, so no late charge is due. The arrival at 09:05 was within the window, so no on-time credit is due. There is no refrigerant line.
  - No write is owed on the new call, and the persona never raises it.

### derivation (r3)

- The tree, rows, order, owners and values are unchanged from revision_2. Every quantity the rules read is "the call's" own lines, and the July call 3f6cacf1 is unchanged.
  - On-time credit: 10 % of **the call's** repair labor (689.00) → 68.90 → ×1.5 + 15 → 118.35.
  - Allowance: 1.7 lb → 151.30.
  - Late charge: the paid share is computed on **the call's** charges (250.00 / 1312.20) → prorated 1.5 periods → 570.80 × 1 % × 1.5 × 0.5 → 4.28.
  - First installment: p_ledger from **the call's** lines = 575.08 → +1 → n = 4 → 4.28 + 142.70 → 146.98, by card.
- The object is unique: the persona's "air-conditioning repair … back in July … replaced a valve … recharged" identifies 3f6cacf1, not the September duct cleaning call.
- Load-bearing runs and factor weights are as in revision_2:
  - refrigerant: 106.80 / 133.50 / 106.80 / 133.50 / 124.60 / 133.50, baseline 0.00;
  - on-time: 83.90 / 83.90 / 52.50 / 103.35, baseline 25.00;
  - late: 5.71 / 5.71 / 6.42 / 8.56, baseline 17.12;
  - installment: 289.68 / 194.55 / 575.08 / 143.77, baseline 575.08.
- **Near-miss for past_due_installment (T0-F3).**
  - The new call's lines (balance 530.10) are records that a careless reader would add to the balance owing, giving the customer's total of 1105.18 and the ≥1000 tier (+2, n = 5, first installment 118.44).
  - The rule excludes them: "The balance owing for this purpose is worked out from the invoice lines: the call's charge lines …".
  - This is a record-level near-miss excluded by the rule's scope. **T0-F3 closed.**
- The new call is also a near-miss for the on-time credit base: summing all of the customer's repair labor (1278.00) would give 127.80. The rule says "the call's repair labor charges", which excludes it.
- O-R2-2 is closed in the charter. The started-count reading now has no textual support for a part-payer ("instead of the standard count").

### frozen verdict (r3, pre-reveal)

PASS on all four relationships: policy self-consistency, problem tree, factors and unique solution.

### source_gt_comparison (r3)

- Reveal: round-3 tasks/0.json was first read at 2026-10-05T18:31:19Z, after the revision_3 hashes were recorded (_difficulty.md 52114da1…, task_0.md d46354c1…, task_1.md 21f3f556…).
- Writes, owners, order, objects and terminal state: identical to my derivation.
  - Gold writes: allowance 1.7 lb / 151.30; on-time credit 118.35; late charge 4.28; installment 146.98, card. All on ticket 3f6cacf1.
  - Gold reads find_service_lines by customer_id, which shows the September call's lines to the agent. A by-ticket read would also reach every scored input.
- prerequisite_closure:
  - Edges, kinds and gates are identical; the resolution order is admissible.
  - Load-bearing figures 142.70 / 5.17 / 5.42 are identical.
- Factor sensitivity and baselines are identical figure for figure:
  - refrigerant 106.8 / 133.5 / 106.8 / 133.5 / 124.6 / 133.5 (baseline 0.0);
  - on-time 83.9 / 83.9 / 52.5 / 103.35 (25.0);
  - late 5.71 / 5.71 / 6.42 / 8.56 (17.12);
  - installment 289.68 / 194.55 / 575.08 / 143.77 (575.08).
- T0-F3: gold's factor_trace now names the September duct-cleaning call (530.10 owing) as the near-miss for balance_size_installments, which is the same record I identified before the reveal. The customer total would be 1105.18 (+2, first installment 118.44); the rule excludes it by "the call's charge lines". Accepted. **T0-F3 closed.**
- Verdict (r3): **PASS** on policy self-consistency, problem tree, factors and unique solution.

### findings (r3)

- Closed: T0-F3 (record-level near-miss now seeded) and O-R2-2 (the conditional count now says "instead of the standard count").
- No open findings on this task.
- No regression:
  - the new call is base-consistent and owes no write;
  - the object stays unique from the persona;
  - every rule the task scores reads the call's own lines.
