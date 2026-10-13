# Policy-task audit — host_standing_and_penalties / task 0

## source_derivation_frozen

- auditor: erl-task-policy-audit (independent Claude agent)
- freeze time: 2026-10-07T19:30Z — written before the GT of ANY task of this difficulty was revealed
- view used: `/tmp/erl45_views/r1/host_standing_and_penalties/task_0.view.json` sha256 dd9d768d4ee2eb3508ef8777e906095e01d33d6f4240c700af70022a514820bc (frozen_time, user_scenario, initial_state only)
- charter: `host.extended.yaml` bfe6e9be…c064cf1573b; tools: `task_tools.py` 0a815c03…dde860ad4e1b4a7 (see `_difficulty.md` § charter_global_frozen)
- masked and unread at freeze: the whole of `tasks/0.json` beyond the view (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), `worklog.md` files.
- contamination_disclosure: none. The brief carried no scored value; no search ran over `tasks/`. The policy's own `compute` was evaluated on the view world with the DSL of `check_compute.py` (temporary script, removed) solely to cross-check the hand derivation below.

World (frozen_time 2026-10-06T10:15:00, date 2026-10-06):
- customer 6793fd26… Delia Marchetti (phone 6155553412, id last4 3586).
- host_accounts 5cf665d9…: Standard Host, active, opened 2019-04-02, business_name "", superhost_since "", last_tier_change_date 2026-09-17, suspended_date 2026-09-17, restricted_until "".
- host_account_events: 12 host_superhost_assessed rows 2024-Q1 … 2026-Q3 all `met` (2024-Q1 tier_change promoted); 2026-Q4 row (event_date 2026-10-01) average_rating 4.77, response_rate_pct 76.0, cancellation_rate_pct 0.0, stays_12m 9, nights_12m 76, assessment_outcome `none`; host_travel_credit_issued 2024-10-01 (2024-Q4, 175.00) and 2025-10-01 (2025-Q4, 204.00); host_policy_strike_recorded 2026-09-17 safety_violation.
- host_appeals: account_suspension approved (submitted 2026-09-18T09:12, decided 2026-10-02T15:40); policy_strike approved on the strike (submitted 2026-09-18T09:20, decided 2026-10-02T15:38).
- rewards_memberships: Rewards Gold, active, valid through 2026-12-31.
Reachability: every row above is reachable by `find_customers`, `find_host_accounts`, `find_host_account_events`, `find_host_appeals`, `find_rewards_memberships` once identity is verified; the persona supplies the phone and ID last4 for `verify_customer_identity`.

### policy_self_consistency (this task only)

- Charter-global conclusions are cited, not restated: `_difficulty.md` § rule_compute_equivalence, § action_binding_and_uuids, § prerequisite_graph, § prerequisite_sentences, § override_declarations, § factor_ladders.
- Handling time: redecision is evaluated on the opening world (it has no prerequisite) at 2026-10-06, "the date of the decision"; the credit is evaluated after the redecision write (variant_name Superhost, superhost_since and last_tier_change_date 2026-10-06), "the date of the credit" 2026-10-06. If the decision were dated at the lift (2026-10-02, "decided at once"), every window gives the same rows (2025-10-01 is 12 whole months before both dates), so the numbers below are unchanged.
- Real-world waits: none. Both appeals are decided in the seed; the assessment metrics are recorded; Rewards membership is on file; the redecision is a synchronous agent write; the claim is a synchronous user write.
- **Consequence of `_difficulty.md` finding D-1 on this world (SOURCE-POLICY RED):**
  - Reading A (base charter text left undeclared): Superhost `entry_gate` "{quarterly_assessment: met, min_avg_rating: 4.80, min_response_rate_pct: 90.00, max_cancellation_rate_pct: 1.00, min_stays_12m: 10, or_min_stays_and_nights_12m: [3, 100]}" and `parameter_schema` "superhost_min_avg_rating: lowest average guest rating for Superhost". On the 2026-Q4 record: 4.77 < 4.80, 76.0 < 90.00, 9 < 10 and 76 < 100 nights → not Superhost → the account stays Standard Host → `superhost_travel_credit_usd` = 0.00 → "only a tier whose superhost_travel_credit_usd is above 0.00 earns it" → no credit. In the same reading the base measure `host_msr_consecutive_met_quarters` ("consecutive ... rows with assessment_outcome met counted back from the newest") gives 0 because the newest row is recorded `none`, again no credit.
  - Reading B (extended rule): Superhost (derivation below) and a credit of 212.00.
  - The two passages reach different conclusions on the same world (no tier change / no credit vs Superhost / 212.00), and no overwrite names the entry_gate, the parameter meanings or the measure.

### problem_chain

Walked from the root:
- Root: the customer asks for "the travel credit for this run put on your account today" → host_ext_superhost_travel_credit (target claim_superhost_travel_credit_0d8c95c2, owner user).
- Its rule's prerequisite sentence: "The travel credit for a run is fixed only after the account holds the host tier that its most recent Superhost assessment earns it." At 2026-10-06 the most recent assessment is the 2026-Q4 row (event_date 2026-10-01, assessment_outcome `none`); the account holds Standard Host (host_accounts.variant_name), while the decision on that row's recorded metrics earns Superhost (below). The state is false at the opening.
- Which write brings it about: the redecision rule ("that assessment is decided at once on its recorded metrics, and the account's tier is set by the decision") → host_ext_superhost_redecision, target apply_superhost_decision_f25b833f (owner agent). Its own rule has no prerequisite sentence; its trigger (suspension lifted on an approved account_suspension appeal) already holds: host_accounts.status active and appeal 140ede9e… approved 2026-10-02.
- Derived tree: nodes {travel_credit (root, user), redecision (agent)}; edge travel_credit → redecision, kind value_input (tier_credit); topological order: redecision, then credit. n = 1 prerequisite problem, value_input edges = 1 ≥ max(0,1) = 1. Acyclic. One owner=user write (the root claim).
- Load-bearing run: skip the redecision → tier stays Standard Host → tier_credit 0.00 → `result` 0.0 (no credit). With it → 212.00. The edge bears weight.
- Parallel edges: none.
- Tool layer: `apply_superhost_decision_f25b833f` and `claim_superhost_travel_credit_0d8c95c2` bodies perform `ctx.update` / `ctx.create` only; neither checks the tier, the run or the assessment (task_tools.py L41–45, L71–83). PASS.
- Persona: raises only the credit; does not mention the suspension, the strike, the assessment or any tier change unless asked ("Only if the agent asks whether anything unusual happened recently ..."). The line "If the agent tells you that something on your account has to be updated or decided first, you say that is fine and that they can go ahead" is a passive authorisation conditioned on the agent, not a hint offered by the customer. Persona closes after the claim is read back — where the derived solution closes. PASS.

### task_independent_derivation

1. Need/authorisation/timing: the travel credit for the run, on her own host account, today; she authorises the agent to update/decide what is needed first; she accepts the credit herself when told. Authorisation for the agent-owned redecision and the hand-over of the user-owned claim are both expressed. No unanswerable ask.
2. Now/wait/refuse: act now. Suspension appeal approved within the window (2026-09-17 → 2026-09-18, 1 day ≤ 30); account active; no future event needed.
3. Object: host account 5cf665d9-6699-481a-9d1d-1bbe8feef403; assessment 2026-Q4 (row 828396d1…); credit booked against 2026-Q4.
4. Step 1 — identity: `verify_customer_identity(customer_id=6793fd26-40e5-4630-86c4-f117c49908ef, phone_number=6155553412, government_id_last4=3586)` (owner agent).
5. Step 2 — redecision (handling time: opening world, 2026-10-06):
   - recorded metrics: rating 4.77, response 76.0, cancellation 0.0, stays 9, nights 76.
   - response floor: most recent suspension 2026-09-17 → appeal approved 2026-10-02 = 15 calendar days ≥ long_suspension_days 14; policy_strike appeal 516a67d3… approved 2026-10-02, within 12 months → response_floor_long_suspension_pct **85.00** (baseline 90.00).
   - response figure: assessments dated within 12 whole months before 2026-10-06 = 2026-01-01 (93), 2026-04-01 (92), 2026-07-01 (91), 2026-10-01 (76); 2025-10-01 is exactly 12 whole months back and excluded. Met among them = 3 ≥ full_run_met_assessments 3 → average of all four = 352/4 = **88.00** (baseline 76.0).
   - stays requirement: 76 ≥ 7 × 9 = 63 → stays_requirement_long_stays **8** (baseline 10).
   - rating floor: met assessments over whole history = 11 (2024-Q1 … 2026-Q3) ≥ 8 → rating_floor_long_tenure **4.75** (baseline 4.80).
   - standards: 4.77 ≥ 4.75; 88.00 ≥ 85.00; 0.0 < 1.00; 9 ≥ 8 → met → **variant_name = Superhost**.
   - write: `apply_superhost_decision_f25b833f(host_account_id=5cf665d9-6699-481a-9d1d-1bbe8feef403, variant_name="Superhost")` (owner agent). Effect: superhost_since and last_tier_change_date 2026-10-06.
   - on the opening world without the decision the tier is Standard Host (contrast for the root below).
6. Step 3 — travel credit (handling time: after the redecision, 2026-10-06):
   - run: decided-met assessments back from the newest since the last credit (2025-10-01, 2025-Q4): 2026-Q4 (decided met), Q3, Q2, Q1 = 4 = superhost_credit_consecutive_quarters → earned, booked against **2026-Q4**; tier after the decision Superhost, superhost_travel_credit_usd 100.00 > 0.
   - base amount: earlier credits = 2 (2024-10-01, 2025-10-01) → 1.50 × 100.00 = **150.00** (baseline 100.00).
   - stays bonus rate: completing assessment nights 76 ≥ 50 and < 100 → **2.00** (baseline 1.00).
   - stays counted: most recent suspension began 2026-09-17 (within 12 months) and lasted 15 days ≥ 14 → average of completed stays at assessments dated within 12 months other than the completing one = (12 + 11 + 10)/3 = **11** (baseline 9) → stays bonus 22.00.
   - response bonus: assessments recorded as met within 12 months = 2026-Q1/Q2/Q3: (93 + 92 + 91)/3 = 92.00 → ≥ 90, < 95 → **10.00** (baseline 0).
   - Rewards bonus: active Rewards Gold → **20.00** (baseline 0).
   - rating bonus: (4.92 + 4.91 + 4.90)/3 = 4.91 → ≥ 4.90, < 4.95 → **10.00** (baseline 0).
   - amount = 150.00 + 22.00 + 10.00 + 20.00 + 10.00 = **212.00**.
   - on the opening world (before the decision): tier_credit 0.00 → 0 (no credit).
   - write (handed to the host): `claim_superhost_travel_credit_0d8c95c2(host_account_id=5cf665d9-6699-481a-9d1d-1bbe8feef403, assessment_quarter="2026-Q4", amount=212.00)` (owner user).
7. Sequence: verify_customer_identity (agent) → apply_superhost_decision_f25b833f (agent) → claim_superhost_travel_credit_0d8c95c2 (user). Terminal state: host account Superhost since 2026-10-06; one host_travel_credit_issued row 2026-Q4, 212.00.
8. Closest alternative readings:
   - Reading A of D-1 (base entry_gate / parameter meanings / base run measure): Standard Host, no credit — see policy_self_consistency (SOURCE-POLICY RED).
   - "counts as met" applied to the bonus averages: the credit rule's clause "an assessment recorded without an outcome during a suspension and later decided as met counts as met" sits in the run sentence; the bonus sentences say "assessments recorded as met". If the decided-met 2026-Q4 row (76 / 4.77) were averaged in, response 88.00 → no response bonus and rating 4.875 → no rating bonus → 192.00. The rule's distinct verbs ("decided as met" for the run vs "recorded as met" for the bonuses) and the redecision rule's "recorded with its metrics and without an outcome" (the row stays `none` after the tier write) exclude it; recorded as observation T0-O1 (weaker reading), not as a second defensible answer.

### factor_weight

Redecision (scored value variant_name = Superhost; whole-baseline fall-back = Standard Host ≠ gold-as-derived):

| factor | label honest | tier taken / evidence rows | baseline per baseline.rule | value under its baseline |
| --- | --- | --- | --- | --- |
| suspension_response_floor | parameter: 85/88/90 numbers — yes | tier 1: suspended_date 2026-09-17 (host_accounts) → account_suspension appeal 140ede9e… decided 2026-10-02 = 15 d; policy_strike appeal 516a67d3… approved 2026-10-02 | 90.00 ("standard response floor is superhost_min_response_rate_pct") — matches | 88.00 < 90.00 → Standard Host (bears weight) |
| response_figure_window | method: 12-m average / 6-m average / single figure — yes | tier 1: 3 met assessments in 12 m (2026-Q1/Q2/Q3) | 76.0 ("standard response figure is the response rate recorded at the assessment") — matches | 76.0 < 85.00 → Standard Host (bears) |
| stay_length_stays_requirement | parameter — yes | tier 1: nights 76 ≥ 63 | 10 — matches | 9 < 10, alt 76 < 100 → Standard Host (bears) |
| tenure_rating_floor | parameter — yes | tier 1: 11 met assessments in history (rows 2024-01-01 … 2026-07-01) | 4.80 — matches | 4.77 < 4.80 → Standard Host (bears) |

Travel credit (scored amount 212.00; whole-baseline fall-back = 100.00 + 1.00 × 9 = **109.00** ≠ 212.00):

| factor | label | tier taken / rows | baseline | amount under its baseline |
| --- | --- | --- | --- | --- |
| earlier_credits_base_amount | parameter — yes | tier 1: credit rows ab3a6a89… (2024-10-01), 72f3ba55… (2025-10-01) | tier credit 100.00 — matches | 162.00 |
| nights_stays_bonus_rate | parameter — yes | tier 2: nights 76 (row 828396d1…) | 1.00 — matches | 201.00 |
| suspension_stays_counted | method — yes (which records are averaged) | tier 1: suspended_date 2026-09-17 + appeal decided 2026-10-02 (15 d) | completing stays 9 — matches | 208.00 |
| met_response_bonus | parameter — yes | tier 2: avg 92.00 over 2026-Q1/Q2/Q3 | 0 — matches ("no response bonus otherwise") | 202.00 |
| rewards_membership_bonus | parameter — yes; cross_difficulty rewards | tier 2: rewards_memberships 9a6dd8ab… Rewards Gold, active | 0 — matches | 192.00 |
| met_rating_bonus | parameter — yes | tier 2: avg 4.91 | 0 — matches | 202.00 |

- Stamps: no field names a tier outcome. The assessment rows' `assessment_outcome` values are the history the rule counts, not a stamp of the factor's tier; the 2026-Q4 row's `none` is the deferral the rule describes. Rewards tier is read from the membership holding the rule names.
- Cross-difficulty evidence seeded: the Rewards Gold membership row is present and conforms to the rewards charter's variant list (blueprint/products/rewards.yaml L187) and lifecycle (active). Rewards is a product category but not the category of any difficulty (blueprint difficulties: stay, listing, host, payout, protect) — observation T0-O2; check_compute counts "another category" as cross-difficulty.
- Near-miss: redecision — the 2025-10-01 assessment (met, response 95) lies exactly 12 whole months before the decision and is excluded by "fewer than that many whole calendar months" (including it moves the figure to 89.40, outcome unchanged); the 2026-Q4 row's `none` is excluded from the met counts. Credit — the decided-met but recorded-`none` 2026-Q4 row is excluded from the "recorded as met" averages by the rule alone, and including it changes the amount (192.00); the 2025-10-01 assessment is excluded from every 12-month window.
- Counts surviving: redecision 4 factors (3 parameter, 1 method); credit 6 (5 parameter, 1 method); task-level multi-source ≥ 1 (suspension_response_floor, suspension_stays_counted), cross-difficulty ≥ 1 (rewards_membership_bonus). PASS.
- Realism (cited, `_difficulty.md` D-O14): the redecision awards Superhost to a record failing three published standards; consequence is D-1, not a separate RED.
- Seed consistency check: the two earlier credits reproduce under the extended formula (2024-Q4: 100 + 2.00 × 15 + 25 + 20 + 0 = 175.00; 2025-Q4: 125 + 2.00 × 12 + 25 + 20 + 10 = 204.00), so the seeded history is coherent with the policy.

Frozen verdict before reveal: policy self-consistency **SOURCE-POLICY RED** (D-1 consequence above); problem tree PASS; factors PASS; unique solution under reading B PASS (observation T0-O1).

## source_gt_comparison

- Reveal: `tasks/0.json` opened 2026-10-07T19:21Z, immediately after the on-disk hashes of all three frozen files were recorded (`_difficulty.md` 0ce7850f…a703b4, `task_0.md` f3a8f4e5…8a108a4, `task_1.md` 5e8d999d…170a9b6, taken at 2026-10-07T19:21:25Z). Timestamp correction (no content change to the frozen section): the "freeze time" lines above were written as estimates (19:30Z / 19:40Z); the true freeze is the hash record at 19:21:25Z, which precedes the reveal. Both tasks were frozen before either GT was opened.

Item by item:

| item | frozen derivation | GT | same? |
| --- | --- | --- | --- |
| need / authorisation / timing | credit for the run, today; agent may decide first; host accepts in person | solvability_contract.request_alignment + persona lines | same |
| read set | customer, host account, events, appeals, Rewards | find_customers(phone), verify, find_host_accounts, find_host_account_events, find_host_appeals, find_rewards_memberships | same (GT adds the finder call that precedes verify) |
| now / wait / refuse | act now | act now | same |
| eligibility | suspension appeal approved, account active; no 2026-Q4 credit yet | stage_provenance preexisting; one_credit_per_run holds | same |
| object | account 5cf665d9…, assessment 828396d1… (2026-Q4) | same ids | same |
| redecision variant_name | Superhost | Superhost (computations[0].expected) | same |
| redecision intermediates | 15 d, 1 overturned strike, floor 85.00, figure 88.00, req 8, met-all 11, floor 4.75 | factor_trace identical | same |
| credit amount | 212.00 | 212.0 | same |
| assessment_quarter | 2026-Q4 | 2026-Q4 | same |
| tool / owner / order | verify (agent) → apply_superhost_decision (agent) → claim (user) | unlock+call apply (agent) → unlock_user + user call claim | same |
| terminal state | Superhost since 2026-10-06; credit row 2026-Q4 212.00 | same | same |

Problem tree vs `prerequisite_closure` (value against value): root host_ext_superhost_travel_credit = root_problem; edge travel_credit → redecision, kind value_input, gate tier_credit, form state, policy_source identical; why_false evidence variant_name = Standard Host and 828396d1….assessment_outcome = none — the same rows I cited; resolution_order [redecision, travel_credit] = mine; edge_load_bearing "amount 0.00 instead of 212.00" = my skip run (0.0 vs 212.00); tools_do_not_block = my function-body reading. Same.

`factor_weight` vs `computations[].factor_sensitivity` / `baseline_result` (figure against figure):
- redecision: suspension_response_floor Standard Host / Standard Host; response_figure_window Standard Host / Standard Host; stay_length_stays_requirement Standard Host / Standard Host; tenure_rating_floor Standard Host / Standard Host; whole baseline Standard Host / "Standard Host". Same.
- credit: earlier_credits_base_amount 162.00 / 162.0; nights_stays_bonus_rate 201.00 / 201.0; suspension_stays_counted 208.00 / 208.0; met_response_bonus 202.00 / 202.0; rewards_membership_bonus 192.00 / 192.0; met_rating_bonus 202.00 / 202.0; whole baseline 109.00 / 109.0. Same.

Closest candidate and its exclusion: averaging the decided-met 2026-Q4 row into the "recorded as met" bonus averages (192.00) — excluded by the rule's "assessments recorded as met" against the run sentence's "decided as met", and by the row remaining `none` after the tier write; GT's design_rationale §10 names the same near-miss. The D-1 reading (Standard Host, no credit) is NOT excluded by any declared overwrite — see findings.

Verification of world assertions in the proof fields (spot-checked against the view): "removing 2024 rows drops the met count below 8" (11 − 4 = 7) true; the two seeded credits reproduce under the extended formula (175.00, 204.00) true; "2025-10-01 is exactly 12 whole months back" true (MONTHS = 12); "D with step 7 skipped = 0.0" true. No false assertion found.

Verdict: policy self-consistency **SOURCE-POLICY RED** (D-1, demonstrated below); problem tree PASS; factors bear weight PASS; unique solution PASS on the extended reading (the RED is the second reading the undeclared base text supplies).

## findings

**T0-1 — SOURCE-POLICY RED (consequence of `_difficulty.md` finding D-1 on this task)**
- Symptom: the merged charter states two incompatible answers to "does the 2026-Q4 decision make Delia a Superhost, and is a travel credit due?".
- Root cause: base `variants[Superhost].entry_gate`, `parameter_schema` meanings of superhost_min_avg_rating / superhost_min_response_rate_pct / superhost_min_stays_12m, the base measure `host_msr_consecutive_met_quarters` and `assessment_outcome: met or not_met` are not named in any `overwrite` of host_ext_superhost_redecision or host_ext_superhost_travel_credit (`_difficulty.md` § override_declarations, § findings D-1).
- Evidence: host.extended.yaml L218 (entry_gate), L62/L63/L65 (parameter meanings), L708–710 (measure), L660 (outcome enum) vs the redecision rule's floors (L1131–1134, L1114–1119, L1127–1130) and the credit rule's "later decided as met counts as met" (L1309–1310); world: row 828396d1… rating 4.77, response 76.0, stays 9, nights 76, outcome none.
- Demonstrated consequence: reading A → 4.77 < 4.80 (and 76 < 90, 9 < 10, 76 < 100 nights) → Standard Host; run measure = 0 because the newest row is `none` → no credit (scored decision Standard Host, no claim). Reading B → Superhost, claim 212.00 against 2026-Q4 (= GT). Two answers on the same world.
- Affected: `host.extended.yaml` overwrite lists of host_ext_superhost_redecision and host_ext_superhost_travel_credit; scored parts: step 7 variant_name, step 9 existence and amount.
- Relation to previous revisions: first audit.

Observations (no RED):
- T0-O1 "counts as met" vs "recorded as met" (192.00 vs 212.00): the weaker reading; the near-miss GT intends. Worth carrying to the KB audit, where a looser rendering could merge the two verbs.
- T0-O2 the cross-difficulty factor reads rewards, a product no difficulty claims; satisfies check_compute's "another category" definition.
- T0-O3 realism: the persona says "the credit for the last two runs turned up on your account on its own each October", yet this run's credit must be accepted by the host in person through a user tool; no sentence of the travel-credit rule says the host accepts the credit (only the tool docstring does). The design_rationale states the reason ("a host's in-person acts carry no number except accepting the travel credit"): the user-owned write was chosen to meet the hand-over requirement rather than taken from platform practice (real platforms issue such coupons automatically).
- T0-O4 realism (`_difficulty.md` D-O14): the prerequisite awards Superhost to a record below three published standards at once.

---

## revision_2

### source_derivation_frozen (revision_2)

- auditor: same independent auditor as round 1; section started after 2026-10-07T21:26:43Z (clock read), before `tasks/0.json` (round 2) was opened
- view: `/tmp/erl45_views/r2/host_standing_and_penalties/task_0.view.json` sha256 3a4ac0568641633553031ac055b82bae0250cd85692f6fea5de60c3efcd9aeb1; charter f59f802c…3c93c180; tools 23e4adf0…a97b2ff
- masked: all of round-2 `tasks/0.json` beyond the view; worklogs.
- contamination_disclosure: the auditor read the round-1 GT of this task in round 1 (round-1 world: Q4 row 4.77 / 76.0 / outcome none; gold Superhost, 212.00). The round-2 world differs (Q4 row 4.75 / 80.0 / outcome not_met; 2026-Q1..Q3 response 94.5 / 93 / 92; earlier credits 185.00 / 214.00) and the round-2 policy differs; everything below is recomputed from the round-2 charter and view. The policy's own compute was evaluated on the view with the check_compute DSL (temporary script, removed) to cross-check the hand figures.

World changes vs round 1 (from the view): 2026-Q4 assessment row 828396d1… now average_rating 4.75, response_rate_pct 80.0, stays 9, nights 76, **assessment_outcome not_met, tier_change unchanged** (decided on the base standards during the suspension); 2026-Q1 response 94.5, Q2 93.0, Q3 92.0; travel credits 2024-Q4 185.00 and 2025-Q4 214.00. Account, appeals, strike, Rewards Gold unchanged. Persona: earlier credits were "offered" in the app and accepted by her; otherwise unchanged.

#### policy_self_consistency (this task, revision_2)

- Charter-global conclusions: cited from `_difficulty.md` § revision_2 (all subsections).
- Round-1 T0-1 (D-1 consequence) re-tested on this world: reading A of round 1 rested on the extended policy lowering the published Superhost thresholds. In round 2 the decision compares with 4.80 / 90.00 / 1.00 / 10 (or 3 + 100 nights) — the `entry_gate` values — and the figures compared are defined inside the declared-superseded met-criteria clause. The base outcome enum is respected (not_met → decided again → met). The run measure host_msr_consecutive_met_quarters, applied to the records after the decision write, gives 4 (2026-Q1..Q4 met since the 2025-Q4 credit). Reading A therefore no longer yields a second answer from an undeclared base statement; the remaining base gloss residues (R2-O2 credit amount, R2-O3 stays gloss) are ruled observations in `_difficulty.md` § override_declarations (revision_2). **T0-1 closed.**
- Handling time: decision on the opening world, 2026-10-06; credit after the decision write. No real-world wait (appeals decided 2026-10-02; metrics recorded; Rewards on file).

#### problem_chain (revision_2)

- Root: travel credit (claim_superhost_travel_credit_0d8c95c2, user). Prerequisite sentence unchanged. At the opening the newest assessment (2026-Q4) was recorded not_met during the suspension (suspended 2026-09-17, assessment 2026-10-01, appeal approved 2026-10-02), and the redecision rule says such an assessment "has that assessment decided again once its account_suspension appeal stands approved"; the decision on its metrics earns Superhost (below), while the account holds Standard Host and the row says not_met. State false at the opening; edge condition's last clause ("carries that decision only once it has been decided again") matches.
- A reader who compared only the record (not_met) with the tier (Standard Host) would think the state already holds; the redecision rule's first sentence is what tells the reader the record is to be decided again — the hop is discoverable from the rules and records alone.
- Tree: {travel_credit (root, user) → redecision (agent)}, value_input (tier_credit; also met_run via the row write), order redecision → credit. n = 1, one value_input edge, one user write, acyclic.
- Load-bearing: skip the decision → tier Standard Host (tier_credit 0.00) and met_run 3 → 0.00. A decision call that set only the tier would still leave met_run 3 → 0.00; the tool writes both in one call.
- Tools judge nothing (task_tools.py L50–55, L90–101). Persona raises only the credit; passive consent line unchanged; closes after the claim read-back. PASS.

#### task_independent_derivation (revision_2)

1. Need/authorisation/timing as round 1; the persona now matches the user-owned acceptance ("the app offered you the credit and you accepted it").
2. Act now.
3. Objects: account 5cf665d9-6699-481a-9d1d-1bbe8feef403; assessment 828396d1-7b41-4038-adb9-48d0b4280e71 (2026-Q4).
4. `verify_customer_identity(customer_id=6793fd26-40e5-4630-86c4-f117c49908ef, phone_number=6155553412, government_id_last4=3586)`.
5. Decision (opening world, 2026-10-06):
   - suspension 2026-09-17 → appeal approved 2026-10-02 = 15 days ≥ 14; policy_strike appeal approved 2026-10-02 within 12 months → tier 1 proration. Suspension days inside the lookback = min(DAYS(2026-09-17, 2026-10-01) = 14, 15) = 14. Decided rate = min(100, 80.0 × 365 / (365 − 14)) = 29200 / 351 = 83.1908… → **83.19** (baseline 80.0).
   - response figure: 3 assessments recorded met within 12 whole months (2026-Q1/Q2/Q3; 2025-10-01 is 12 months back, excluded) → 12-month average with the decided rate: (94.5 + 93.0 + 92.0 + 83.19) / 4 = 362.69 / 4 = 90.6725 → **90.67** ≥ 90.00 (baseline = decided rate 83.19).
   - rating figure: 11 assessments recorded met over the history (2024-Q1 … 2026-Q3) ≥ 8 → 12-month average (4.92 + 4.91 + 4.90 + 4.75) / 4 = **4.87** ≥ 4.80 (baseline 4.75).
   - stays figure: 14 suspension days in the lookback ≥ 14 → larger of the decided assessment (9) and the other assessment within 6 months (2026-07-01: 10; 2026-04-01 is 6 whole months back, excluded) = **10** ≥ 10 (baseline 9; alt route 76 < 100 nights fails).
   - cancellation 0.00 < 1.00.
   - → met → **Superhost**, recorded on the row as met / promoted.
   - write: `apply_superhost_decision_f25b833f(host_account_id=5cf665d9-6699-481a-9d1d-1bbe8feef403, assessment_event_id=828396d1-7b41-4038-adb9-48d0b4280e71, assessment_outcome="met", tier_change="promoted", variant_name="Superhost")` (agent).
6. Credit (after the decision; row 828396d1… met):
   - run: 2026-Q1..Q4 met after the 2025-Q4 credit = 4; met within 12 months = 4 ≥ 4 → complete; tier Superhost, 100.00.
   - base 1.50 × 100.00 = **150.00** (2 earlier credits).
   - stays bonus rate: nights 76 → **2.00**; stays counted (suspension within 12 months, 15 days ≥ 14) = avg(12, 11, 10) = **11** → 22.00 (baseline 9 → 18.00).
   - response bonus: recorded rates of met assessments within 12 months (94.5, 93.0, 92.0, 80.0) = 359.5 / 4 = 89.875 → ≥ 88, < 92 → **10.00**. (If the decided rate 83.19 were used for the 2026-Q4 row instead of the recorded 80.0: 90.67, same tier — no value at stake.)
   - Rewards Gold → **20.00**.
   - rating bonus: (4.92 + 4.91 + 4.90 + 4.75) / 4 = 4.87 → ≥ 4.85, < 4.90 → **10.00**.
   - amount = 150.00 + 22.00 + 10.00 + 20.00 + 10.00 = **212.00**; booked against **2026-Q4**.
   - `claim_superhost_travel_credit_0d8c95c2(host_account_id=5cf665d9-6699-481a-9d1d-1bbe8feef403, assessment_quarter="2026-Q4", amount=212.00)` (user).
   - opening-world contrast: 0.00 (Standard Host, met_run 3).
7. Order: verify → decision (agent) → claim (user). Terminal: row 828396d1… met/promoted; Superhost since 2026-10-06; credit row 2026-Q4 212.00.
8. Closest alternatives: decide the row `met` but tier_change `unchanged` — excluded by the docstring enum ("promoted when a met decision moves a Standard Host up to Superhost") and the rule ("records the assessment as met with the tier effect promoted"); stays figure from 2026-Q2 (11) — excluded by the 6-month window, same outcome anyway; credit at 100.00 by the parameter gloss — ruled out as a defensible reading (`_difficulty.md` R2-O2).

#### factor_weight (revision_2)

Decision (gold-as-derived Superhost; whole baseline Standard Host):
| factor | label | tier / rows | baseline | under its baseline |
| --- | --- | --- | --- | --- |
| suspension_response_proration | method — prorated vs raw rate | tier 1: host_accounts.suspended_date, appeals 140ede9e… / 516a67d3… | 80.0 | figure 89.88 < 90 → Standard Host |
| run_response_window | parameter (window) — see R2-O4 | tier 1: 3 met in 12 months | decided rate 83.19 | 83.19 < 90 → Standard Host |
| tenure_rating_window | parameter (window) | tier 1: 11 met overall | 4.75 | 4.75 < 4.80 → Standard Host |
| suspension_stays_figure | method | tier 1: 14 lookback suspension days | 9 | 9 < 10 → Standard Host |

Credit (gold-as-derived 212.00; whole baseline 100.00 + 1.00 × 9 = **109.00**): earlier_credits_base_amount → 162.00; nights_stays_bonus_rate → 201.00; suspension_stays_counted → 208.00; met_response_bonus → 202.00; rewards_membership_bonus → 192.00; met_rating_bonus → 202.00. Each differs from 212.00.

- Stamps: none decides a tier; the row's `not_met` is the in-suspension outcome the rule tells the reader to re-decide.
- Cross-difficulty: Rewards Gold row present (rewards is a product no difficulty claims — T0-O2, unchanged).
- Near-misses: lookback suspension days 14 (to the assessment date) vs suspension length 15 (to approval); 2025-10-01 assessment exactly 12 months back; 2026-04-01 assessment exactly 6 months back (excluded from the stays pair); the recorded vs decided 2026-Q4 response rate in the bonus average (same tier).
- Seed coherence: the earlier credits reproduce under the round-2 credit rule (2024-Q4: 100 + 2 × 15 + 25 + 20 + 10 = 185.00; 2025-Q4: 125 + 2 × 12 + 25 + 20 + 20 = 214.00).
- Counts: decision 4 (2/2), credit 6 (5/1); multi-source and cross-difficulty present. PASS.

Frozen verdict (revision_2, before reveal): policy self-consistency PASS (T0-1 closed); problem tree PASS; factors PASS; unique solution PASS.

### source_gt_comparison (revision_2)

- Reveal: round-2 `tasks/0.json` opened 2026-10-07T21:28Z, after the revision_2 frozen sections of all three files were hashed at 2026-10-07T21:27:55Z (`_difficulty.md` b2671254…37ee5f, `task_0.md` 09d29242…fc336, `task_1.md` 7e38c494…fc79c). Both tasks' revision_2 derivations were frozen before either round-2 GT was opened.

| item | frozen (r2) | GT (r2) | same? |
| --- | --- | --- | --- |
| read set | customer, account, events, appeals, Rewards | find_customers, verify, find_host_accounts, find_host_account_events, find_host_appeals, find_rewards_memberships | same |
| decision call | (5cf665d9…, 828396d1…, met, promoted, Superhost) | identical arguments | same |
| decision intermediates | 83.19 / 90.67 / 4.87 / 10 | 83.19 / 90.67 / 4.87 / 10 (factor_trace) | same |
| credit call | (5cf665d9…, 2026-Q4, 212.00), user | identical, user | same |
| credit intermediates | 150 / 2.00 × 11 / 10 / 20 / 10; met_run 4 | identical; met_run 4 (3 at the opening) | same |
| order / owners | verify → decision (agent) → claim (user) | same | same |
| terminal | row met/promoted; Superhost; credit 212.00 | same | same |

- Problem tree vs `prerequisite_closure`: root, edge (value_input, tier_credit, state, same policy_source), resolution_order [redecision, travel_credit], why_false rows (variant_name Standard Host, 828396d1….assessment_outcome not_met, superhost_since empty), load-bearing (0.00 vs 212.00; met run 3 vs 4) — all equal to the frozen tree.
- factor_weight vs factor_sensitivity / baseline_result: decision — Standard Host ×4 / Standard Host ×4, whole baseline Standard Host / Standard Host; credit — 162.00 / 201.00 / 208.00 / 202.00 / 192.00 / 202.00 vs 162.0 / 201.0 / 208.0 / 202.0 / 192.0 / 202.0, whole baseline 109.00 / 109.0. Same.
- Closest candidate exclusion: recorded not_met taken as final (GT §10 names it) — excluded by the redecision rule's first sentence; flat 100.00 credit — excluded on the R2-O2 ruling.
- Proof-field assertions spot-checked (80 × 365 / 351 = 83.19; 89.88 for the unprorated figure; 2025-10-01 12 months back; 2026-Q3 stays 10; met run 3 → 4) — all true.
- Verdict (revision_2): **PASS** — policy self-consistency PASS, problem tree PASS, factors bear weight PASS, unique solution PASS.

### findings (revision_2)

Round-1 items, verified against the reworker's claims:
| id | claim | verified |
| --- | --- | --- |
| T0-1 (SOURCE-POLICY RED) | changed | **closed** — thresholds are the published ones; outcome enum and run measure respected; no undeclared base statement yields a second answer on this world |
| T0-O1 ("counts as met" vs "recorded as met") | no longer applicable | **confirmed** — the decision writes `met` on the row, so the bonus averages include 2026-Q4 by its record; the recorded-vs-decided-rate variant gives the same tier (89.88 vs 90.67, both 88–92) |
| T0-O2 (rewards claimed by no difficulty) | no change | unchanged, observation |
| T0-O3 (acceptance in person not in rule; persona said auto-issued) | changed | **closed** — rule: "booked ... when the host accepts it"; persona: "the app offered you the credit and you accepted it" |
| T0-O4 (realism of stacked reliefs) | (via D-O14) | **closed in substance** (`_difficulty.md` revision_2 factor_ladders) |

New: none RED. Observations R2-O2 (D-1(b) ruled PASS) and R2-O3 bear on this task as rulings, not defects. Regressions: none found (prerequisite edge, single resolving write, tool neutrality, persona closure all hold; the seed's historic credits reproduce under the round-2 rule).

---

## revision_3

### source_derivation_frozen (revision_3)

- written ~2026-10-07T22:40Z, before round-3 `tasks/0.json` was opened; view `/tmp/erl45_views/r4/host_standing_and_penalties/task_0.view.json` sha256 79ce2fabdb14de5bd58ce31808de079a5ee7fe0213e5aec813afa76854f24d0e; charter and tools unchanged (see `_difficulty.md` § revision_3).
- contamination_disclosure: round-1 and round-2 GT of this task were read in earlier rounds (disclosed there).
- Only change in the view: frozen_time → '2026-10-06 10:15:00 CDT' (user_scenario and initial_state byte-identical to revision_2's view). Date part unchanged (2026-10-06), zone is the customer's local daylight zone; every clock consumer reads the date part only (`_difficulty.md` § revision_3, frozen_time format change).
- policy self-consistency, problem tree, factor weight, task derivation: carried forward from `## revision_2` of this file by reference — every input they rest on (charter, tools, user_scenario, initial_state, date) is identical; re-evaluated compute confirms the same values.
- Expected solution (unchanged): decision Superhost via apply_superhost_decision_f25b833f(5cf665d9…, 828396d1…, met, promoted, Superhost) (agent) → claim_superhost_travel_credit_0d8c95c2(5cf665d9…, 2026-Q4, 212.00) (user); factor and whole-baseline figures as revision_2.
- Frozen verdict (revision_3, before reveal): PASS on all four relationships.

### source_gt_comparison (revision_3)

- Reveal: round-3 `tasks/0.json` opened 2026-10-07T22:40Z, after the revision_3 frozen sections of all three files were hashed at 2026-10-07T22:39:44Z (`_difficulty.md` 580fd1e9…44f21, `task_0.md` c3712f4a…05251, `task_1.md` 404d03f5…ea43c). Clock correction: "written ~22:40Z" in the frozen section above is an estimate; the hash record at 22:39:44Z is the true freeze and precedes the reveal.
- GT vs revision_2 GT (as recorded in this file's revision_2 comparison), item by item: frozen_time '2026-10-06 10:15:00 CDT'; evaluation_criteria — same tool sequence and owners, write arguments identical: steps 8 (agent, decision: met / promoted / Superhost on 828396d1…) and 10 (user, claim 2026-Q4, 212.0); computations Superhost / baseline Standard Host / factor baselines Standard Host ×4, and 212.0 / 109.0 / 162.0, 201.0, 208.0, 202.0, 192.0, 202.0; prerequisite_closure — same root, edge, kind, gate and resolution_order; charter_scope identical; no residual '2026-10-06T' stamp anywhere in the file. File size 93669 → 93673 bytes, exactly the +4 of the frozen_time rewrite.
- Frozen expectation vs GT: same on every item.
- Verdict (revision_3): **PASS** — policy self-consistency PASS, problem tree PASS, factors bear weight PASS, unique solution PASS.

### findings (revision_3)

- Round-2 RED to close: none existed. The frozen_time rewrite is verified as format-only: the date and local time are unchanged, the zone is the customer's, every consumer reads the date part, and every scored value and baseline is unchanged. No new defect, no regression. Observations carried from revision_2 unchanged.
