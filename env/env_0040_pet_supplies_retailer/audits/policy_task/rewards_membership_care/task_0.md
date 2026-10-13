# Policy-task audit — rewards_membership_care / task 0

## source_derivation_frozen

- Freeze time: 2026-10-06T06:07:48Z (file write time; revision 0). Auditor: independent erl-task-policy-audit agent.
- Inputs and hashes: masked view `/tmp/e40views/policy_task/rewards_membership_care/task_0.view.json` sha256 692e497ea548918d2759fe89a4d1d638bac6500b0ed1febab9f87c315697c6a4 (fields: frozen_time, user_scenario, initial_state only); member.extended.yaml b9b17c2a…8a33; task_tools.py 656afc4d…df97c; blueprint/ of this scenario.
- Masked and unread at freeze: `tasks/rewards_membership_care/tasks/0.json` and `1.json` in full (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), worklog.md.
- contamination_disclosure: before deriving, the auditor saw the orchestrator's gate snapshot, which prints per-task structural counts (replay "acts 18", solvability "3 10 28", grounding "2 3 3 10"). No scored value, tool argument, factor tier or tree edge was visible in it. No other contact with GT. Blind audit considered valid.
- frozen_time 2026-10-06 (posting/purchase date = 2026-10-06). Window convention as in `_difficulty.md` § rule_compute_equivalence; no row of this world lies on a window boundary.

### policy_self_consistency (this task only)

- Charter-global conclusions cited, not restated: `_difficulty.md` § policy_conflict_scan, § rule_compute_equivalence, § action_binding_and_uuids, § prerequisite_graph, § prerequisite_sentences, § override_declarations, § factor_ladders, findings F-1, F-3, F-4.
- Handling time: P1 on the opening world; P2 on opening + P1's earning row (dated 2026-09-14, points_balance +P1); P3 on opening + P1 + P2 (variant VIP, tier_effective_on 2026-10-06, bonus row). No later write is computed early.
- Real-world waits: none. Every fact consumed is a seeded row (autoship shipment 2026-09-14, ledger, groom pass/visits, order fee) or the synchronous effect of an earlier write of this task; the purchase is paid with the card on file (customers.card_last4 4386) today.
- Consequence of F-3 on this task: `autoship_evt_rewards_earn` ("Each charged Autoship shipment earns Pals Rewards points on its merchandise subtotal after the Autoship discount at the member's base earn rate multiplied by points_multiplier") applied to shipment c7916092 gives ⌊(71.96 − 3.60) × 10 × 2⌋ = **1367** points for its earning entry; P1 gives **2152** (derivation below). Two KB clauses fix different numbers for the same ledger entry. P1 is the more specific rule (it names the missed-earning case), which is why this is reported on the strength of the undeclared conflict rather than as an even split between readings.
- Consequence of F-4 on this task: base `member_enrollment_and_trials` makes a first Plus Annual enrollment due 1000 enrollment bonus points (precedent row 41c28e7c… enrollment 500 on 2025-11-03 for Plus Monthly); no tool can book it. No scored parameter changes.

### problem_chain

Walked from the root using only the rules and the raw DB.

Root: the customer asks to buy Tailwise Plus Annual today with the card on file and wants the price quoted first → P3 (`buy_plus_tier_1a1727fb`, owner=user). P3's prerequisite sentence: "The first-term Plus Annual fee is fixed only after the membership carries the free tier that its qualifying spend has earned."

Test of that state on the raw DB at frozen_time:
- Held: `member_memberships e3994121…` variant **Pals Rewards Insider**, status active, tier_effective_on 2026-03-03.
- Earned (base `member_tier_qualification`: qualifying spend = "purchases that earned points, net of reversals"; upgrade "once member_msr_spend_current_year reaches" the threshold; measure = Σ qualifying_spend of member_points_earn − Σ of member_points_reverse in the calendar year):
  - 2026 earn rows: 9 Autoship earnings (2026-01-05 … 2026-08-17) × 68.36 = 615.24; orders 87.41 + 24.99 + 18.47 = 130.87; reversal 2026-05-30 24.99 → **721.12** (< 750 VIP threshold, ≥ 250 Insider).
  - 2025 (prior year, seeded): groom 335.16 + 3 × 68.36 = **540.24**.
  - Highest free tier its qualifying spend has earned = **Insider** = the tier held.
- **The state P3 waits on already holds at the opening.** Read top-down, P3's sentence names no unmet state, so no prerequisite problem is reachable from the root.

The tree the charter actually encodes, found only bottom-up:
- P1 is `state_due`: "When a customer's most recent charged Autoship shipment has no points earning on the rewards ledger …". Most recent charged shipment = autoship_events c7916092-76ab-421c-a04e-0e1b55c80aa6 (2026-09-14, seq 15); no member_points_earn row has source_event_id c7916092… → unmet.
- Posting it adds 68.36 to 2026 qualifying spend: 721.12 → **789.48 ≥ 750** → VIP becomes earned; P2 ("When the qualifying spend of a free-tier membership has earned the next free tier above the one it holds") becomes due, and P2's own sentence ("not posted until the rewards ledger carries a points earning for every charged Autoship shipment of the last 12 months") is then satisfied (seq 3–15, 2025-10-13 … 2026-09-14, all with earnings).
- Only after P1 does P3's state become false (VIP earned, Insider held) and P2 resolve it.
- Nodes {P1, P2, P3}; edges P3←P2 (value_input via loyalty_rate), P2←P1 (declared value_input via net_spend_12m; in this world it is also what makes P2 eligible at all); order P1 → P2 → P3; one customer write (P3, owner=user). Isomorphic to the declared graph — but the P3←P2 edge's condition ("variant_name equals the highest free tier whose qualifying spend threshold the membership's qualifying spend has reached") is **true at frozen_time** (Insider = Insider), and P2's trigger is false at frozen_time.
- Load-bearing runs: skip P1 → 2026 spend 721.12, P2 not due, P3 at Insider rate (fee 37.77 vs 31.41) — bears weight. Skip P2 after P1 → P3 at Insider rate 37.77 — bears weight.
- No parallel edges; no waits; tool bodies (task_tools.py 21–169) check nothing.

Verdict for this relationship: **SOURCE-CHAIN RED** (a declared prerequisite already satisfied at the opening; the tree is not derivable from the root's prerequisite sentence and the records). Detail in findings T0-1.

### task_independent_derivation

Need/authorisation/timing (persona): buy Plus Annual today, card on file, quote first; the customer completes the purchase herself at hand-over with "your membership, Tailwise Plus Annual and exactly the amount the agent quoted"; consents to "something on your rewards account [that] has to be put right first … posting points or changing your tier". Raises only the root; never mentions points/tiers. Closes at the purchase. Identity: phone 6175550417 to find; zip 02144 + card 4386 or email to verify (2 matches). No extra ask.

Act now (all three problems), object `membership_id e3994121-5ea7-44e8-b42f-ef220a20f879`.

**Reading B — the chain the charter encodes (P1 → P2 → P3):**

1. P1 `post_missing_points_02f0bcb5` (agent), handling time = opening, tier held Insider (base_points_per_usd 10, max 7500), Autoship Everyday points_multiplier 2 (autoship.yaml).
   - ship_spend 71.96 − 3.60 = 68.36; standard ⌊68.36×10×2⌋ = ⌊1367.2⌋ = 1367.
   - apology: tenure MONTHS(2021-04-18, 2026-10-06) = 65; member_points_earn rows dated after 2026-07-06: 2026-07-20, 2026-08-17 → 2 (< 3) → not high; ≥ 24 months and ≥ 1 → **75**. Near-miss: order earning 2026-07-05 (9d4eba80…) just outside three months.
   - milestone: shipment_seq 15 ≥ 12 → **100**.
   - streak: charged shipments after 2026-04-06: 04-27, 05-25, 06-22, 07-20, 08-17, 09-14 → 6 ≥ 6 → **100**. Near-miss 2026-03-30.
   - bundle: groom pass 2bb77929… active, visits_remaining 2 ≥ 2 → **80**.
   - sum 1722; days 2026-09-14 → 2026-10-06 = 22 > 21 → ⌊1722 × 1.25⌋ = **2152**; cap 7500 → **points 2152**.
   - Args: source_category autoship, source_event_id c7916092-76ab-421c-a04e-0e1b55c80aa6, purchase_date 2026-09-14, qualifying_spend_usd 68.36, points 2152.
2. P2 `apply_earned_tier_ebf561a6` (agent), handling time = after P1 (2026 spend 789.48 → VIP earned), tier held Insider, new_tier **Pals Rewards VIP**.
   - standard 500 (vip_upgrade_bonus); method: tier_upgrade entry of 500 after 2024-10-06 → 0e9856d2… 2024-11-20 → re-earning → ⌊500/2⌋ = **250** (near-miss 2022-06-30 entry of 200).
   - net_spend_12m (after 2025-10-06): 13 Autoship earnings × 68.36 = 888.68 + orders 130.87 − reversal 24.99 = **994.56** ≥ 937.50 → **250** (opening value 926.20 → 100; groom earning 2025-10-01 just outside 12 months).
   - fast-track: tier_effective_on 2026-03-03 → latest earning 2026-09-14 = 195 days → **100** (opening value 2026-08-17 → 167 → 200).
   - cross: shipments after 2026-07-06: 07-20, 08-17, 09-14 = 3 ≥ 3 and active pass → **150**.
   - tenure 65 ≥ 60 → **100**.
   - **upgrade_bonus_points 850**.
3. P3 `buy_plus_tier_1a1727fb` (owner **user**, handed over), handling time = after P2 (VIP held).
   - not in trial (latest fee 2026-02-03, 245 days < 365).
   - returning credit: 245 days in (182, 365] → latest fee alone **5.99** (no fee after 2026-04-06 for the six-month sum).
   - loyalty: VIP and 65 ≥ 36 months → **0.20**.
   - Autoship credit: 6 shipments in six months → **4.00**; shipping-fee credit: one shipping fee (190c9c99…, 2026-07-05) → **1.50** (near-miss: ship-to-home order 5e70ce12… with no fee row); spend credit 994.56 ∈ [800, 1500) → **2.50**; salon credit: active pass, latest visit 2026-09-02, 34 days ≤ 60 → **3.00** (older visit 2026-03-21).
   - (59 − 5.99) × 0.80 = 42.408; − 11.00 = 31.408 → **first_charge_usd 31.41**, plus_tier Tailwise Plus Annual.
   - Persona hands-over line supplies membership, tier and amount.
4. Terminal: Autoship earning row for c7916092 (2152), tier VIP effective 2026-10-06 with tier-upgrade bonus 850, Plus Annual purchased with term 2026-10-06 – 2027-10-05 and fee charge 31.41; points balance 612 + 2152 + 850 = 3614.

**Reading A — root-only, entailed by P3's sentence + the DB:** P3's state holds (Insider earned and held), no prerequisite write, P3 on the opening world: Insider and 65 ≥ 36 → rate 0.08; net_spend_12m 926.20 → spend credit 2.50; other credits as above → (59 − 5.99) × 0.92 − 11.00 = 37.7692 → **first_charge_usd 37.77**, single write `buy_plus_tier_1a1727fb`.

Root on the opening world (contrast number required by the skill): 37.77. The right number under the charter's intended tree is 31.41 only if the reader discovers P1 by an unprompted ledger audit; nothing in P3's rule leads there.

### factor_weight

All on the handling-time worlds above (Reading B).

P1 (scored 2152; baseline rule alone: standard 1367, cap 7500 → **fall-back 1367 ≠ 2152**):
| factor | label honest | tier taken / rows | baseline encodes baseline.rule | scored under its baseline |
|---|---|---|---|---|
| missed_earning_apology | parameter, yes | low (65 months; 2 earnings in 3 months: 62f80c1e 07-20, f2e4ed68 08-17) — multi-source | yes (0) | ⌊1647×1.25⌋ = 2058 ≠ 2152 |
| subscription_milestone | parameter, yes | high (seq 15, autoship_events c7916092) — cross-difficulty autoship | yes (0) | 2027 |
| autoship_streak | parameter, yes | high (6 charges 2026-04-27…09-14) — cross-difficulty | yes (0) | 2027 |
| salon_bundle | parameter, yes | high (groom_passes 2bb77929 active, 2 left) — cross-difficulty groom | yes (0) | 2052 |
| late_posting_adjustment | method, yes (multiply vs add vs none) | >21 days (22) | yes (sum as is) | 1722 |
No stamp names an outcome. Near-misses: 2026-07-05 order earning (3-month window), 2026-03-30 shipment (6-month window). Survivors: 5 (4 parameter, 1 method).

P2 (scored 850; baseline: standard 500 → **fall-back 500 ≠ 850**):
| factor | label honest | tier taken / rows | scored under baseline |
|---|---|---|---|
| upgrade_bonus_method | **no** (multiplier substitution, `_difficulty.md` F-1) | re-earning (0e9856d2, 500 on 2024-11-20) | 1100 |
| over_achievement | parameter | high (994.56 ≥ 937.50) | 600 |
| fast_track | parameter | middle (195 days) | 750 |
| cross_program | parameter, multi-source | high (3 shipments + active pass) — cross-difficulty autoship/groom | 700 |
| membership_tenure | parameter | high (65 months) | 750 |
Near-misses: 2022-06-30 tier-upgrade 200 (outside 24 months, unequal), groom earning 2025-10-01 (outside 12 months). Every factor bears weight; but with F-1 the computation has **0 honest method factors** → SOURCE-FACTOR RED (T0-3).

P3 (scored 31.41; baseline: 59.00, not in trial → **fall-back 59.00 ≠ 31.41**):
| factor | label honest | tier taken / rows | scored under baseline |
|---|---|---|---|
| returning_member_credit | method, yes | latest fee alone (fee 5f66dba4, 2026-02-03, 245 days) | 36.20 |
| plus_loyalty_rate | parameter | VIP ≥ 36 months (after P2) | 42.01 |
| autoship_credit | parameter | high (6) — cross-difficulty autoship | 35.41 |
| shipping_fee_credit | parameter | low (1 fee, order_events 190c9c99) — cross-difficulty order | 32.91 |
| plus_spend_credit | parameter | low (994.56) | 33.91 |
| salon_credit | parameter, multi-source | high (active pass + visit b0c2cb55 2026-09-02) — cross-difficulty groom | 34.41 |
Near-misses: shipping-fee-free ship-to-home order 5e70ce12, visit 2026-03-21, fees older than six months. All 6 bear weight.

Task-level: multi-source ≥ 1 (apology, cross_program, salon_credit); cross-difficulty ≥ 1 with seeded rows present (autoship_subscriptions/events, groom_passes/events, order_events). Seed stamps: none naming a tier.

## findings

- **T0-1 SOURCE-CHAIN RED — root prerequisite already satisfied at the opening; tree not derivable top-down.** Symptom: P3's only prerequisite state holds at frozen_time, so a reader at the root finds no prerequisite problem. Root cause: the qualifying spend that P3's sentence (and P2's trigger) read crosses the VIP threshold only after P1's write, but P3 carries no sentence leading to P1, and P2's sentence leading to P1 is reached only once P2 is due. Evidence: P3 rule "The first-term Plus Annual fee is fixed only after the membership carries the free tier that its qualifying spend has earned."; edge condition "member_memberships.variant_name equals the highest free tier whose qualifying spend threshold the membership's qualifying spend has reached"; base `member_tier_qualification` and measure `member_msr_spend_current_year`; initial_state member_memberships e3994121 (Insider), member_events 2026 earnings/reversal summing 721.12, 2025 summing 540.24, autoship_events c7916092 without earning. Demonstrated consequence: the edge P3←P2 is true on the raw DB at frozen_time; the declared depth (2 prerequisite problems) is reachable only bottom-up through an unprompted ledger audit. Affected: member.extended.yaml P3 prerequisite/rule, P2 rule/trigger, task 0 initial_state; the scored write order P1→P2→P3.
- **T0-2 SOURCE-TASK RED — two defensible answers for the root.** Reading A (root's sentence + DB, act only within the customer's need): one write, `buy_plus_tier_1a1727fb` with first_charge_usd **37.77**. Reading B (proactive ledger repair, then chain): P1 2152 → P2 VIP 850 → P3 **31.41**. Same root cause as T0-1; affected: the scored write set and first_charge_usd.
- **T0-3 SOURCE-FACTOR RED — P2 computation has no honest method factor.** Consequence of `_difficulty.md` F-1 on this task's world: the re-earning tier selects ⌊500 × 0.5⌋ = 250 where the other tiers would select 500 × 2 = 1000 or 500 × 1 = 500 — the same formula with a different multiplier. Affected: P2 factors.
- **T0-4 SOURCE-POLICY RED (cross-category) — P1's posted points vs `autoship_evt_rewards_earn`.** Consequence of `_difficulty.md` F-3: 1367 (autoship base clause) vs 2152 (P1) for the earning entry of shipment c7916092. Affected: P1 points; blueprint/products/autoship.yaml `autoship_evt_rewards_earn`.
- Observations: F-4 enrollment bonus (1000) due on a first Plus Annual enrollment with no tool; persona's conditional consent lines ("something on your rewards account has to be put right first … posting points or changing your tier") pre-describe the hidden steps to the simulator — passive only, not red; P2←P1 effect text omits that the posting is what makes VIP earned.

## source_gt_comparison

Reveal time: 2026-10-06T06:09Z, after `task_0.md` (06:07:48Z) and `task_1.md` (06:08:51Z) were both frozen on disk. Fields read: design_rationale, solvability_contract, evaluation_criteria, computations, prerequisite_closure, charter_scope, required_documents.

| item | frozen derivation (Reading B / A) | GT | same? |
|---|---|---|---|
| need / authorisation / timing | buy Plus Annual today, quote first, customer completes at hand-over; agent writes consented | same (solvability_contract.request_alignment) | same |
| read set | membership, member ledger, autoship subs/events, groom pass/events, orders/events/RMA, pets | steps 0–11 identical set | same |
| now / wait / refuse | act now | act now | same |
| P1 object / args | c7916092…, 2026-09-14, 68.36, autoship, **2152** | identical, points 2152 | same |
| P2 tier / bonus | Pals Rewards VIP, **850** | VIP, 850 | same |
| P3 tier / charge, owner | Tailwise Plus Annual, **31.41**, user | Tailwise Plus Annual, 31.41, user | same |
| order | P1 → P2 → P3 | steps 13 → 15 → 17 | same |
| Reading A (root only) | single write, 37.77 | not in GT | **different — GT does not exclude it** |
| charter_scope | {P1, P2, P3} | {P1, P2, P3} + three tools | same |

Problem tree vs `prerequisite_closure` (value against value):
- root member_ext_plus_annual_first_fee = mine. Edges, kinds, gates, forms, sentences, resolved_by: identical to mine.
- resolution_order [missed earning, earned tier, purchase] = mine.
- Edge P3←P2 `unresolved_at_frozen_time.why_false`: "The membership still shows Pals Rewards Insider although, **once the missed earning is booked**, its 2026 net qualifying spend (789.48) has reached the VIP threshold of 750." At frozen_time the 2026 net qualifying spend is 721.12 (the closure's own figure, design_rationale §2: "the 2026 net qualifying spend shows 721.12 instead of 789.48"), so the condition "variant_name equals the highest free tier whose qualifying spend threshold the membership's qualifying spend has reached" is **true** at frozen_time (Insider = Insider). The closure's "why false" is a statement about the world after step 13, not at the opening — it contradicts my recomputation and confirms T0-1.
- Edge P2←P1 `edge_load_bearing.skipped_effect`: "upgrade_bonus_points 850 -> 800 (net spend 926.20 …, fast-track 167 days …)". Recomputed: without step 13 the 2026 qualifying spend is 721.12 < 750, so P2's trigger ("has earned the next free tier above the one it holds") is false and no VIP bonus is posted at all; 800 is the value of a write the policy does not permit in that world. Mine: the edge bears weight, but by removing P2 entirely (and P3 → 37.77), not by 850 → 800. Proof assertion contradicted (supports T0-1).
- Edge P3←P2 skipped effect 31.41 → 37.77: same as mine.
- design_rationale §10 asserts that from the published rules alone the reader goes "the purchase rule says the fee waits on the earned tier; the membership shows Insider; the tier-qualification rule needs 2026 spend; the ledger shows no earning for the latest shipment and the earned-tier rule says its bonus waits on every shipment's earning". The step from "2026 spend" to "the earned-tier rule" is not entailed: the ledger's 2026 spend (721.12) earns Insider, so the earned-tier rule is not due and its sentence is never reached top-down. solvability_contract step 13 `action_semantics` locates the discovery elsewhere: "A charged Autoship shipment with no earning on the ledger is a debt the membership is owed whatever the customer called about (state_due)" — i.e. bottom-up discovery outside the customer's need, which is exactly Reading B's precondition.

Factor weight vs `computations` (figure against figure):
- P1: expected 2152 = mine; baseline_result 1367 = mine; sensitivity apology 2058, milestone 2027, streak 2027, bundle 2052, late 1722 — all = mine.
- P2: expected 850 = mine; baseline 500 = mine; method 1100, over-achievement 600, fast-track 750, cross 700, tenure 750 — all = mine. design_rationale §4 calls upgrade_bonus_method an algorithm change ("half vs double vs unchanged"); F-1/T0-3 stands: the three tiers are one formula with a substituted multiplier.
- P3: expected 31.41 = mine; baseline 59.0 = mine; 36.20, 42.01, 35.41, 32.91, 33.91, 34.41 — all = mine.

Closest alternative candidate and its exclusion: Reading A (37.77, one write). GT does not exclude it with policy/world evidence; its only exclusion is the state_due proactivity of P1, which the root's prerequisite sentence does not reach. Not excluded.

Verdicts for task 0:
- Policy self-consistency: **SOURCE-POLICY RED** (cross-category, T0-4 via `_difficulty.md` F-3).
- Problem tree holds: **SOURCE-CHAIN RED** (T0-1; plus the false skipped-effect assertion T0-5 below).
- Factors bear weight: **SOURCE-FACTOR RED** (T0-3 via F-1; every other factor bears weight against an honest baseline).
- Unique solution: **SOURCE-TASK RED** (T0-2: 31.41 chain vs 37.77 root-only).

Additional finding from the reveal:
- **T0-5 SOURCE-CHAIN RED (proof assertion) — `prerequisite_closure.edge_load_bearing` for member_ext_earned_tier_bonus → member_ext_missed_autoship_earning** asserts "850 -> 800" on skipping step 13; on the world without step 13 VIP is not earned (721.12 < 750), so P2 is not due and the bonus is not posted at all. Affected: tasks/0.json prerequisite_closure.edge_load_bearing[1], design_rationale §3(b) "Deletion run: bonus 850 -> 800" and §9 "S without step 13 = 800". Same root cause as T0-1 (the posting is a state gate on P2's trigger, declared and argued only as a value input).

## revision_2

### source_derivation_frozen (revision 2)

- Frozen before the round-2 tasks/0.json was opened. Inputs: `task_0.r2.view.json` sha256 b33960c27348cbacf37d3d3893634e7f9ff4423d8d75c19fcb22f6fb7a9746d0; member.extended.yaml 2d6b4d81…0a70; task_tools.py f8889f06…6c3e.
- contamination_disclosure: round-1 GT of this task was read in revision 0, by protocol after its freeze. All figures below are recomputed on the round-2 world (`/tmp/e40audit_scripts/calc_r2.py`).
- Round-2 world differences found by reading the view: order line 5c6e50cb (bolster bed) is now 155.99 with earning 1559 (was 87.41/874); order 5e70ce12 is billed 180.98. The persona now says only "If the agent tells you that something on your account has to be sorted out first …", and the hand-over now includes "the welcome points figure the agent tells you, or zero".
- Charter-global conclusions cited from `_difficulty.md` § revision_2.

### problem_chain (r2)

- Root P3 (buy Plus Annual, owner=user). Its sentence: "fixed only after the membership carries the free tier that its qualifying spend has earned."
- Opening test: the membership holds Insider. 2026 net qualifying spend = 9 × 68.36 + 155.99 + 24.99 + 18.47 − 24.99 = **789.70 ≥ 750**, so VIP is earned and not held → **unmet at the opening**. Running the 2026 ledger forward, the threshold was crossed by the 2026-08-17 earning. The rule that applies an earned free tier is P2 ("a care agent applies that earned tier").
- P2's sentence: "not posted until the rewards ledger carries a points earning for the most recent charged Autoship shipment." The most recent charge is c7916092 (2026-09-14, seq 15), and no earning cites it → **unmet**. The rule that posts it is P1.
- Tree: P3 ← P2 (value_input, loyalty rate), P2 ← P1 (value_input, net_spend_12m and latest-earning date); order P1 → P2 → P3; customer write P3. It is derivable top-down from the root.
- Load-bearing runs: skip P2 → P3 at Insider rate 37.77 (vs 31.41). Skip P1 → P2 = 0 + 100 + 200 + 150 + 100 = 550 (vs 600). P2 is still due in that world, because the VIP spend is reached without the posting. Tools judge nothing.
- **T0-1 closed. T0-5 closed** (on the round-2 world, skipping P1 leaves P2 due, so a skipped-effect figure is meaningful; it will be compared at the reveal).

### task_independent_derivation (r2)

1. P1 `post_missing_points_02f0bcb5` (opening world, Insider, multiplier 2 from subscription 78e43da8 "Autoship Everyday"):
   - net_spend_12m 994.78 (12 Autoship earnings 820.32 + orders 199.45 − 24.99; groom 2025-10-01 outside) → Insider with ≥ 750 → tier rate **12**.
   - apology: 65 months, 2 earnings in three months → **+0.5**. Milestone seq 15 → **+1.0**. Streak 6 → **+1.0**.
   - summed 14.5; 22 days > 21 → ×1.25 = 18.125 per $.
   - ⌊68.36 × 18.125 × 2⌋ = **2478** (cap 7500).
   - Args: autoship, c7916092-76ab-421c-a04e-0e1b55c80aa6, 2026-09-14, 68.36, **2478**.
2. P2 `apply_earned_tier_ebf561a6` (after P1): new_tier **Pals Rewards VIP**.
   - method: 500-point entry 2024-11-20 within 24 months → re-earning → max(0, 500 − 500) = **0**.
   - over-achievement: net_spend_12m 1063.14 ≥ 1.4 × 750 = 1050 → **250**.
   - fast-track: 2026-03-03 → 2026-09-14 = 195 → **100**.
   - cross: 3 shipments + active pass → **150**. Tenure 65 → **100**.
   - **upgrade_bonus_points 600**.
3. P3 `buy_plus_tier_1a1727fb` (user, after P2):
   - (59 − 5.99) × 0.80 − (4.00 + 1.50 + 2.50 + 3.00) = 31.408 → **first_charge_usd 31.41**.
   - **enrollment_bonus_points 1000**: first Plus Annual enrollment; the ledger's only enrollment bonus is 500 for Plus Monthly on 2025-11-03; Plus Annual enrollment_bonus_points = 1000.
   - plus_tier Tailwise Plus Annual.

Second readings checked:
- Root-only (37.77): excluded, because the root's own sentence is unmet at the opening.
- P1 posted at the held rate (10 → 2136): excluded by the tier-rate sentence (Insider with 12-month spend ≥ 750).
- Counting the posting being made among the "last three months" earnings (3 → apology 1.0 → 2563): excluded by handling time (the entry does not exist before it is written).
- Enrollment bonus 0 (buying a paid tier on an existing membership treated as a tier change): not supported by the text ("tier joined … first enrollment of that tier") or the seeded precedent (500 posted with the Plus Monthly purchase on this same membership). 1000 stands.

### factor_weight (r2)

- P1 (gold 2478; fall-back 1367): tier_rate → 2136; apology → 2392; milestone → 2307; streak → 2307; late method → 1982. All bear weight. Near-misses: 2026-07-05 earning (3 months), 2026-03-30 shipment (6 months).
- P2 (gold 600; fall-back 500): method (std) → 1100; over_achievement → 350; fast_track → 500; cross_program → 450; tenure → 500. All bear weight; the method label is honest (F-1 closed → **T0-3 closed**). Near-misses: the 2022 entry of 200; groom earning 2025-10-01.
- P3 (gold 31.41; fall-back 59.00): 36.20 / 42.01 / 35.41 / 32.91 / 33.91 / 34.41. All bear weight.
- Multi-source and cross-difficulty minimums met; seeded rows present.

### status of round-1 items for this task (pre-reveal)

- T0-1 SOURCE-CHAIN: closed. T0-2 SOURCE-TASK: closed (37.77 no longer defensible). T0-3 SOURCE-FACTOR: closed. T0-4 SOURCE-POLICY (autoship cross-category): closed via P1's explicit rate sentence (O-11 recorded). T0-5: closed in substance, to be checked against the round-2 closure text. Persona-hint observation: closed (generic wording). F-4 here: closed (tool argument plus base sentence → 1000).

### source_gt_comparison (revision 2)

Revealed at 2026-10-06T09:50:22Z, after the revision-2 derivations of both tasks were on disk (09:50:17Z).

| item | revision-2 derivation | round-2 GT | same? |
|---|---|---|---|
| P1 points / args | 2478; autoship, c7916092…, 2026-09-14, 68.36 | identical | same |
| P2 tier / bonus | VIP, 600 | VIP, 600 | same |
| P3 charge / enrollment bonus / owner | 31.41 / 1000 / user | 31.41 / 1000 / user | same |
| order | P1 → P2 → P3 | steps 13 → 15 → 17 | same |
| scope | {P1, P2, P3} | same | same |

- Tree vs `prerequisite_closure`: edges, kinds and order are identical. The P3←P2 `why_false` now reads "2026 net qualifying spend on the ledger at the opening (789.70) has already reached the VIP threshold", which equals my opening recomputation; the edge is false at the opening. The P2←P1 skipped effect "600 -> 550 … VIP is still due on the 789.70 already recorded" equals my figure (550). **T0-5 closed.**
- Factors vs `computations`: P1 2478 / 1367 / 2136, 2392, 2307, 2307, 1982; P2 600 / 500 / 1100, 350, 500, 450, 500; P3 31.41 / 59.0 / 36.2, 42.01, 35.41, 32.91, 33.91, 34.41. Every figure equals mine.
- Closest alternatives (root-only 37.77; P1 at held rate 2136; enrollment bonus 0) are excluded by the rule sentences cited in the frozen section.

Verdicts (revision 2), task 0: policy self-consistency **PASS**; problem tree **PASS**; factors **PASS**; unique solution **PASS**.

Round-1 item closure: T0-1 closed · T0-2 closed · T0-3 closed · T0-4 closed (O-11 observation) · T0-5 closed · persona-hint observation closed · F-4 closed. No regression and no new RED in this task.
