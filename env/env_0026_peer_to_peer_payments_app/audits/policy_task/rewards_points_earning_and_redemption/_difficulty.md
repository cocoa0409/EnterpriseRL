# Policy-task audit — rewards_points_earning_and_redemption / charter-global

## charter_global_frozen

- Round: r1 (first audit round). Auditor: independent policy-task auditor (claude-opus-5-5), not the authoring agent.
- Freeze time: 2026-09-24T23:41Z, written before any task's GT was revealed. Nothing in this section is derived from a revealed GT.
- Frozen inputs (sha256):
  - `tasks/rewards_points_earning_and_redemption/rewards.extended.yaml` = `0f6396002c4edeaea2f6a01ab73adcd5f8a76d6775c791c05af09faf1470a025`
  - `tasks/rewards_points_earning_and_redemption/task_tools.py` = `ea80fe55695ac79cc82e808d43fb1d726810e529360ff7b9a4973c0366c3f8e4`
  - the base section (lines 1-952 of the extended file) was diffed against `blueprint/products/rewards.yaml`: identical except for one trailing blank line (verbatim copy holds).
- Permitted and read: `blueprint/blueprint.yaml`, `blueprint/products/rewards.yaml`, `blueprint/share_tools.py`, the extended charter, `task_tools.py`, the two coordinator-built masked views (`task_index`, `frozen_time`, `user_scenario`, `initial_state` only), the gate snapshot `snap/d4_r1.txt`.
- Masked and not read for this section: `tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), `worklog.md`, any other audit.
- Entry conditions (step 0): gate snapshot supplied with commands and output lines — check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK (0.json 14 acts / 1.json 14 acts, match True), check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cross_fire SCOPE OK; check_traceability deferred by the coordinator (KB not yet published). Masked views supplied with hashes, re-verified by sha256sum: 0.view.json `82f925ec4a92b21e54d131bdd77c98a313eb58518ba723787d8bef91d5da5776`, 1.view.json `628055405491a58673dca41a98301d5a9e22994d6fb9d987e9c1f85157d19088` (both match the brief). Entry conditions met.

### policy_conflict_scan

Six extended policies, all on `rewards`:

| policy | subject | target_tool (owner) | computes | trigger |
| --- | --- | --- | --- | --- |
| rewards_ext_anniversary_bonus_amount | rewards_bonus (anniversary) | credit_anniversary_bonus_4deaf7db (agent) | points | state_due |
| rewards_ext_refund_clawback_points | rewards_clawback | post_refund_clawback_4ceb9a03 (agent) | points | state_due |
| rewards_ext_whole_balance_gift_card_value | rewards_redemption (gift_card) | redeem_points_gift_card_91c84320 (user) | cash_value | on_request |
| rewards_ext_late_fulfilment_courtesy_points | rewards_goodwill_credit | credit_late_fulfilment_courtesy_4e426c94 (agent) | points | state_due |
| rewards_ext_quarterly_milestone_bonus_amount | rewards_bonus (quarterly_milestone) | credit_quarterly_milestone_bonus_7b7b30cf (agent) | points | state_due |
| rewards_ext_whole_balance_charity_value | rewards_redemption (charity) | donate_points_to_charity_56fec22b (user) | cash_value | on_request |

- Overlapping subjects: two policies write `rewards_bonus` (anniversary vs quarterly_milestone) and two write `rewards_redemption` (gift_card vs charity). Each pair is split by bonus_type / redemption_type, and each supersedes only its own half of the shared base sentence (see `override_declarations`). No two policies decide the same quantity for the same object.
- Eligibility / state: both redemption policies inherit "Points can be redeemed only while the membership status is active" and restate it; the bonus policies inherit "bonuses are credited while the membership is active". Compatible.
- Time anchors: every extended ladder uses one convention, restated verbatim in each rule ("A date lies within the last N months when it is later than the same calendar day N months before the handling date and not later than the handling date"; whole years = whole months // 12). The clawback window uses base's calendar-day count; the courtesy policy uses Federal Reserve business days as in base. No two anchors collide on one quantity.
- Terminal states: every tool is a single ledger insert plus a points_balance delta; no status transitions. Compatible.
- Cross-category reads: wallet (plan, direct deposits, opened_date) and card (active physical card tier, card_transactions purchases / refunds / is_foreign) only, each declared in the policy's `cross_category`.
- Scope: the gate claims task 0 = {anniversary, clawback, gift card} and task 1 = {courtesy, milestone, charity} — verified against each policy's `prerequisite` graph (two connected components, see `prerequisite_graph`). Pairwise disjoint and jointly complete over the six extended policies.
- One latent conflict inside a policy, recorded under findings D2: both whole-balance redemption rules say "only redeemable points can be redeemed" and, in the next sentence, that the points redeemed are "the points balance on the handling date rounded down"; on any tier with points_pending_days > 0 and pending points on the ledger these give two numbers.

### rule_compute_equivalence

Swept binding by binding for all six policies; every binding has a `compute_basis` quotation that is a verbatim substring of its `rule`, and every rule sentence that bears on the number is implemented.

- Anniversary: 12-month earning spend less 12-month clawback spend (`anniv_earn_spend_12m`, `anniv_clawed_spend_12m`, `anniv_year_spend`), three-way form (`anniv_bonus_form`: `int(spend*0.11)` / tier + `int((spend-30000)*0.05)` / tier), tenure by whole years, DD supplement by 12-month XSUM of `wallet_direct_deposit` + linked plan, card supplement by the active physical card's variant, clean-record by 12-month clawback COUNT, sum. Rounding points ("rounded down", "the added part rounded down") match `int(...)`. Tier amount = `P('anniversary_bonus_points')`, "the tier held on the credit date" = the handling tier. Equivalent.
- Clawback: latest `card_merchant_refund` (amount, source_txn_id, date), purchase amount and date by `card_txn_id`, purchase points = earning + boost entries for that purchase, standard = ceiling of the proportional share (`-int((-x)//1)` = round up), age by `DAYS`, age share with round-up, loyalty/category/card-activity reliefs, `MX(0, …)` floor, then `MN(…, MX(0, points_balance))` only when `negative_balance_allowed` is False. The window eligibility (≤ clawback_window_days) is a gate, not a binding. Equivalent.
- Gift card: whole balance floored to the increment, 3-month spend measure, the four additive cents-per-point lifts, the plan multiplier (Onyx/Summit + DD ≥ 3000 in the last month; paid plan + DD ≥ `dd_boost_threshold`), single floor to the cent at the end (`int(RND(...,6))/100`). Equivalent — except that the rule's "only redeemable points can be redeemed" is not implemented in `gc_redeem_points` (finding D2).
- Courtesy: tier amount + loyalty (years ∧ 12-month net spend) + card + plan (Summit / Onyx or Prime) + redemption count (any kind, 12 months) supplements, then repeat adjustment by the 12-month count of prior courtesy entries (×2 / `int(×1.5)` / as is). The "at most goodwill_max_credits_per_year times over the rolling 365 days" cap is a gate. Equivalent.
- Milestone: streak count of `quarterly_milestone` entries in 12 months (×2 / `int(×1.25)` / as is), tenure, 3-month DD + plan, card, 12-month foreign `card_purchase` count, 3-month grocery+dining earning-entry count, sum. The rule's acting base "the milestone_bonus_points of the tier held on the quarter's last day" is implemented as `P('milestone_bonus_points')`, the handling tier; the two coincide only when no tier review has moved the membership since the quarter's last day (finding D3).
- Charity: whole balance floored, giving lift (12-month charity count ∧ years), account-age lift by `MONTHS(opened_date, NOW)`, 3-month spend lift, 1-month DD lift (≥ 5000 / ≥ `dd_boost_threshold`), 3-month card-activity lift, boost multiplier by 12-month boost-earning count, single floor at the end. Same unimplemented "only redeemable points" clause as the gift card (D2).
- Every factor ladder tier appears both as a rule sentence and as a branch of its `decides` binding, and every branch is a rule tier. No tier lives in only one face.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). No docstring adds a confirmation, review or waiting step. No docstring names another tool, gives a sequence position, or uses before / after / first / then / until. The only "once" occurrences are about the tool's own receipt ("balance left once the redemption is booked"). Two docstring details are recorded as observations (D5, D8): both bonus tools accept either `bonus_type`, and the courtesy docstring states "Courtesy points are available to redeem at once". The second is consistent with the base measure `rewards_msr_redeemable_points`, which does not list `rewards_goodwill_credit` among pending rows.
- The tool bodies judge nothing: each looks up the membership, inserts one row with the given values, and adjusts `points_balance`. There is no branch, refusal or hint on any state.
- uuid8s: 4deaf7db, 4ceb9a03, 91c84320, 4e426c94, 7b7b30cf, 56fec22b. All distinct. None shares a prefix beyond one leading hex digit (three begin with `4`, which is within chance for six random values). No sequence or adjacency pattern. Nothing suggests batch derivation.

### prerequisite_graph

- Every policy fills in `prerequisite`. Anniversary, courtesy and milestone have `[]`.
- Edges:
  - E1: clawback ← anniversary. `kind: value_input`, `gate: clawback_balance_cap` (exists in clawback compute), `form: state`, `resolved_by: credit_anniversary_bonus_4deaf7db` (= the anniversary policy's `target_tool`).
  - E2: gift card ← clawback. `value_input`, `gc_redeem_points` (exists), `state`, `post_refund_clawback_4ceb9a03` (= the clawback policy's `target_tool`).
  - E3: charity ← courtesy. `value_input`, `ch_donate_points` (exists), `state`, `credit_late_fulfilment_courtesy_4e426c94`.
  - E4: charity ← milestone. `value_input`, `ch_donate_points`, `state`, `credit_quarterly_milestone_bonus_7b7b30cf`.
- Every `problem` names an extended policy in this file, never a base policy and never itself. The graph is two components: anniversary → clawback → gift card, and {courtesy, milestone} → charity. It is acyclic.
- Every `policy_source` is a verbatim sentence of the blocked policy's own `rule`: E1 is clawback rule sentence 2, E2 is gift-card rule sentence 3, E3 and E4 are charity rule sentences 3 and 4.
- No `fallback_reason` is present, and none is needed since all four edges are state form.
- `condition` vs sentence:
  - E1 "for every anniversary … a rewards_bonus entry of bonus_type anniversary dated on or after that anniversary" matches the sentence's strength.
  - E2 "every card_merchant_refund … refunds an earning purchase … dated no later than clawback_window_days" matches.
  - E3 "every gift_card or charity redemption … fulfilled later than … business days … within goodwill_max_credits_per_year" matches the sentence's "the courtesy credit owed", which inherits the cap.
  - E4 "every ended calendar quarter whose qualifying spend reached the … threshold of the tier held on its last day … an entry dated after that quarter's last day" matches.
- `effect` statements are true of the compute: each resolving write moves `points_balance`, which feeds the named binding. E1's effect is conditional on `negative_balance_allowed` being false, as it says itself. Whether it bears weight is per task.
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite` field.

### prerequisite_sentences

The four-point test was applied to each edge.

| edge | sentence | connective | waited-on state (record-visible) | tool / id / snake_case | strength |
| --- | --- | --- | --- | --- | --- |
| E1 | "The points clawed back are fixed only after the ledger carries the anniversary bonus for every enrolment anniversary the membership has reached while active." | only after | anniversary bonus entries on the ledger | none | = condition |
| E2 | "A whole-balance gift card redemption is not valued until the ledger carries a clawback entry for every merchant refund of an earning purchase posted within the clawback window." | not … until | clawback entries on the ledger | none | = condition |
| E3 | "A whole-balance charity donation is recorded only after the ledger carries the courtesy credit owed for every gift card or charity redemption fulfilled later than its fulfilment period." | only after | courtesy credit entries | none | = condition |
| E4 | "Before a whole-balance charity donation is valued, the ledger must carry the quarterly milestone bonus for every ended quarter whose qualifying spend reached the milestone." | before | quarterly milestone bonus entries | none | = condition |

- Single resolving write per state (policy surface): the only rule that books an anniversary bonus entry is the anniversary policy's rule. The only rule booking a clawback entry is the clawback policy's. The only rule booking a courtesy credit is the courtesy policy's. The only rule booking a milestone entry is the milestone policy's. Each hop therefore resolves to exactly one policy. At the tool layer, both bonus tools accept `bonus_type` ∈ {anniversary, quarterly_milestone} (D5). The reader identifies the write from the rules, and the rules name only one booking policy per entry kind, so the hop is not ambiguous.
- Derivations a reader performs:
  - E1: sentence → "anniversary bonus" → the anniversary rule "is owed for each anniversary … booked as one entry … credited only if the ledger carries no anniversary bonus entry dated on or after the most recent anniversary" → credit that bonus.
  - E2: sentence → "clawback entry for every merchant refund … within the clawback window" → the clawback rule "the refund assessed is the latest merchant refund … booked as one entry … against the refunded card purchase" → post the clawback.
  - E3: sentence → the courtesy rule's lateness test and its "booked as one entry against the late redemption" → credit the courtesy.
  - E4: sentence → the milestone rule "owed for a calendar quarter once that quarter has ended … booked as one entry carrying the quarter" → credit the milestone.
  - Each has one reading.
- No rule carries a second wording, a tool name or another policy id for its dependency. No depended-on rule restates the blocked sentence.
- Undeclared cross-problem orders in extended rules: none. Base rule `rewards_points_expiry_rules` says "a member who wants value from the points redeems them before closing". That is a base cross-problem order that grounds no edge here, and no task rests on it (observation D9).
- Scope-width observations (D4) are not demonstrable on either world:
  - E1 says "every enrolment anniversary", while the anniversary rule can only credit the most recent one.
  - E2 says "every merchant refund", while the clawback rule assesses only "the latest merchant refund".

### override_declarations

Swept sentence by sentence against each `base_policy_refs` entry:

- anniversary vs `rewards_bonuses`:
  - Sentence 1 (anniversary half: "the anniversary bonus of anniversary_bonus_points is credited on each anniversary …"): replaced (amount and booking date change) and declared.
  - Sentence 2 (dedup by bonus_type + bonus_period): replaced by the "dated on or after the most recent anniversary" test and declared.
  - Sentence 3 (referral): not governed.
  - Sentence 4 ("bonuses are credited while the membership is active, and bonus points are subject to points_pending_days"): followed and restated.
  - No undeclared override.
- clawback vs `rewards_clawback_rules`:
  - Sentence 1 (proportional, rounded up, on the refund date): replaced by assessment-day booking plus age share and reliefs, and declared. The declared superseded clause covers the whole quantity, so the anonymous intermediates (age share, reliefs, `MX(0,…)` floor) sit inside a declared replacement.
  - Sentences 2 and 3 (window, counting): followed.
  - Sentence 4 (negative-balance cut): followed, adding "never below zero" on the cap, which does not change the quantity on a non-negative balance.
  - Sentence 5 (unlinked / dispute / out-of-window credits never claw back): followed.
- gift card vs `rewards_redemption_rules`:
  - Sentence 1 (active): followed.
  - Sentence 2 (only redeemable points): restated but not honoured by the whole-balance quantity on tiers with pending points (D2). This is an undeclared deviation when pending points exist.
  - Sentence 3 (increment, minimums): followed, with minimums inherited.
  - Sentence 4 (gift card value): its clause "gift card value points times gift_card_cents_per_point" is replaced and declared, and the base "divided by 100 and rounded down to the cent" is kept as a single final rounding.
  - Sentences 5-7: not governed / followed.
- courtesy vs `rewards_goodwill`:
  - Sentences 1 and 2: followed.
  - Sentence 3's clause "The credit is goodwill_points_per_credit of the tier held on the credit date": replaced and declared.
  - The once-per-redemption, 365-day cap and "no other complaint" clauses: followed.
- milestone vs `rewards_bonuses`:
  - Sentence 1 (milestone half): replaced (qualifying spend defined as net of clawbacks, amount changed) and declared.
  - Sentence 2 (dedup): replaced and declared.
  - Sentence 4: followed.
- charity vs `rewards_redemption_rules`:
  - "donation value points times charity_cents_per_point": replaced and declared.
  - The partner-charity and "match never credited" clauses: followed.
  - The same sentence-2 deviation as the gift card (D2).
- Disguised forms: no 0/1 multiplier zeroes a base-fixed quantity outside a declared replacement, and no base branch is dropped. The clawback `MX(0, …)` sits inside the declared replacement.

### factor_ladders

| policy | factor | label | ladder (3 tiers, fall-through last) | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| anniversary | anniversary_bonus_form | method | spend×0.11 in place of tier amount / tier + (spend−30000)×0.05 / tier amount | no | — |
| | anniversary_tenure_supplement | parameter | 2000 / 1000 / 0 | no | — |
| | anniversary_direct_deposit_supplement | parameter | 1500 / 750 / 0 | yes (plan ∧ DD total) | wallet |
| | anniversary_card_supplement | parameter | 1000 / 500 / 0 | no | card |
| | anniversary_clean_record_supplement | parameter | 500 / 250 / 0 | no | — |
| clawback | clawback_refund_age | method | ×0.5 round-up / ×0.75 round-up / as is | no | card |
| | clawback_loyalty_relief | parameter | 750 / 300 / 0 | yes (years ∧ spend) | — |
| | clawback_category_relief | parameter | 300 / 100 / 0 | no | — |
| | clawback_card_activity_relief | parameter | 400 / 150 / 0 | no | card |
| gift card | gift_card_engaged_spender_lift | parameter | +0.15 / +0.05 / 0 ¢ | yes (spend ∧ years) | — |
| | gift_card_card_tier_lift | parameter | +0.10 / +0.05 / 0 ¢ | no | card |
| | gift_card_redeemer_lift | parameter | +0.05 / +0.02 / 0 ¢ | no | — |
| | gift_card_boost_lift | parameter | +0.05 / +0.02 / 0 ¢ | no | — |
| | gift_card_plan_multiplier | method | ×1.10 / ×1.05 / as is | yes (plan ∧ DD) | wallet |
| courtesy | courtesy_loyalty_supplement | parameter | 1500 / 500 / 0 | yes (years ∧ spend) | — |
| | courtesy_card_supplement | parameter | 1000 / 500 / 0 | no | card |
| | courtesy_plan_supplement | parameter | 750 / 300 / 0 | no | wallet |
| | courtesy_redemption_supplement | parameter | 500 / 200 / 0 | no | — |
| | courtesy_repeat_adjustment | method | ×2 / ×1.5 round-down / as is | no | — |
| milestone | milestone_streak_adjustment | method | ×2 / ×1.25 round-down / as is | no | — |
| | milestone_tenure_supplement | parameter | 2500 / 1200 / 0 | no | — |
| | milestone_direct_deposit_supplement | parameter | 2000 / 800 / 0 | yes (plan ∧ DD) | wallet |
| | milestone_card_supplement | parameter | 1500 / 750 / 0 | no | card |
| | milestone_travel_abroad_supplement | parameter | 900 / 350 / 0 | no | card |
| | milestone_everyday_spend_supplement | parameter | 600 / 250 / 0 | no | — |
| charity | charity_giving_lift | parameter | +0.20 / +0.10 / 0 ¢ | yes (count ∧ years) | — |
| | charity_account_age_lift | parameter | +0.08 / +0.04 / 0 ¢ | no | wallet |
| | charity_spend_lift | parameter | +0.10 / +0.05 / 0 ¢ | no | — |
| | charity_deposit_lift | parameter | +0.06 / +0.03 / 0 ¢ | no | wallet |
| | charity_card_activity_lift | parameter | +0.05 / +0.02 / 0 ¢ | no | card |
| | charity_boost_multiplier | method | ×1.05 / ×1.02 / as is | no | — |

- Counts as declared: anniversary 5 (4 parameter, 1 method), clawback 4 (3 / 1), gift card 5 (4 / 1), courtesy 5 (4 / 1), milestone 6 (5 / 1), charity 6 (5 / 1). All within 4-6.
- Every ladder has three pairwise-disjoint tiers stated in full in the rule and implemented in `decides`. No two tiers of one ladder share a value or method. Every fall-through equals the factor's `baseline`: 0, the standard clawback, the tier amount, or ×1 / "as it stands". `decides` is never `result`, and bindings are disjoint within each policy.
- Per task, by gate-claimed scope:
  - Task 0 has multi-source factors (DD supplement, loyalty relief, engaged lift, plan multiplier) and cross-difficulty factors (wallet, card).
  - Task 1 has multi-source factors (courtesy loyalty, milestone DD, charity giving) and cross-difficulty factors (wallet, card).
- **Label honesty (finding D1, SOURCE-FACTOR RED).** Only `anniversary_bonus_form` changes the algorithm: spend-based replacement vs tier-plus-increment vs flat tier amount. The other five `method` factors pick a number m for one fixed stage of an unchanged formula, and their fall-through is the same stage with m = 1:
  - `clawback_refund_age`: aged = ceil(standard × m), m ∈ {0.5, 0.75, 1}. The standard is already an integer, so ceil(standard × 1) = standard, which is the fall-through.
  - `gift_card_plan_multiplier`: value = floor(points × rate × m) / 100, m ∈ {1.10, 1.05, 1}.
  - `courtesy_repeat_adjustment`: adjusted = floor(total × m), m ∈ {2, 1.5, 1}. total is an integer, so ×2 needs no rounding and ×1 is "as it stands".
  - `milestone_streak_adjustment`: amount = floor(tier_amount × m), m ∈ {2, 1.25, 1}.
  - `charity_boost_multiplier`: value = floor(points × rate × m) / 100, m ∈ {1.05, 1.02, 1}.

  In each case one expression with a tier-selected number reproduces every tier exactly. That is the skill's "a factor labelled `method` whose tiers only substitute a different number into the same formula (a rate, a fee, a threshold)". Counting only honest labels, the clawback, gift card, courtesy, milestone and charity computations each carry 0 `method` factors against the floor of 1. The anniversary computation is the only one that meets it.
- Realism of conditions and outcomes: no tier condition holds for every customer who reaches its write. No fall-through is a straw man: each is the charter's own published standard (the tier amount, the standard rate, the proportional clawback). Some conditions are unusual for a points program but not demonstrably ones no business weighs (observation D8): the anniversary clean-record supplement (no clawback in 12 months), a gift card rate lift and a donation multiplier driven by the count of boost earnings, and the clawback relief for travel/dining refunds.

### findings

- **D1 — SOURCE-FACTOR RED (charter-global structure; consequence demonstrated per task).**
  - Symptom: five of the six `method` labels sit on multiplier stages.
  - Root cause: a tier-selected multiplier or share is labelled `method` although the tiers only substitute a number into one fixed expression.
  - Evidence: the five compute lines `aged_clawback`, `gc_plan_multiplier` + `result`, `cty_adjusted`, `ms_streak_amount`, `ch_boost_multiplier` + `result`, and their `factors[].effect: method` in `rewards.extended.yaml` (lines 1199/1236, 1391/1473, 1567/1647, 1738/1768, 1971/2069). The single-expression rewrites are given in `factor_ladders` above.
  - Consequence: the per-computation floor of one honest `method` factor fails for clawback and gift card (task 0) and for courtesy, milestone and charity (task 1).
  - Affected: the `factors` of those five policies.
  - Bears on: tasks 0 and 1.
- **D2 — observation (charter-global; no consequence on either world).**
  - Evidence: `rewards_ext_whole_balance_gift_card_value.rule` sentence 1 "only redeemable points can be redeemed" vs sentence 2 "the points redeemed are the points balance on the handling date rounded down to a whole multiple of redemption_increment_points". The same pair appears in `rewards_ext_whole_balance_charity_value.rule` sentences 1-2. `gc_redeem_points` / `ch_donate_points` use `F('points_balance')` with no pending deduction.
  - On a tier with points_pending_days > 0 and pending rows, the two sentences give two different point counts, and base `rewards_redemption_rules` sentence 2 is overridden without a declaration.
  - Both tasks' members are Obsidian (points_pending_days 0), so neither world realises it.
- **D3 — observation (charter-global; no consequence in task 1).**
  - Evidence: the milestone rule "The milestone tier amount is the milestone_bonus_points of the tier held on the quarter's last day", implemented as `P('milestone_bonus_points')` (the handling tier).
  - Rule and compute diverge whenever a tier review since the quarter's end moved the member.
  - Task 1's membership has `tier_qualified_date` 2024-01-01, so the two coincide there.
- **D4 — observation (scope width of E1/E2).**
  - E1 requires the anniversary bonus for "every enrolment anniversary" reached while active. The anniversary rule can only book the most recent one ("credited only if the ledger carries no anniversary bonus entry dated on or after the most recent anniversary"). A world with an older unpaid anniversary would make E1 unsatisfiable.
  - E2 requires a clawback for "every merchant refund" in window, while the clawback rule assesses only "the latest merchant refund". A world with two unclawed refunds would leave the gift card unvaluable.
  - Neither world realises either case: task 0 has anniversary entries for 2023-2025, and its earlier refund of 2026-03-02 already carries its clawback.
- **D5 — observation.** `credit_anniversary_bonus_4deaf7db` and `credit_quarterly_milestone_bonus_7b7b30cf` both accept `bonus_type` ∈ {anniversary, quarterly_milestone, not_applicable}, so either tool can write an entry of the other kind. The policy surface still names one booking policy per kind, so no hop ambiguity is demonstrable.
- **D6 — observation (vocabulary; per-task consequence in task 0's file).**
  - The spend measures say "the spend carried by earning entries".
  - The clawback rule contrasts "its earning entry and any boost entry for it", while the gift-card and charity rules speak of "boost earning entries".
  - The boost rows also carry `spend_amount`, the same purchase's spend.
  - The compute reads `rewards_cashback_earned` only.
  - Counting boost rows would count one purchase's spend twice, which is what makes the cashback-only reading the principled one.
- **D7 — observation.** The `inputs.history` metadata omits the 12-month clawback-spend read in the courtesy policy and the 3-month clawback-spend read in the charity policy, although both are in compute. There is no scoring effect.
- **D8 — observation.** The realism notes in `factor_ladders` above: the clean-record supplement, the boost-count lift and multiplier, and the category relief. Separately, on tiers whose goodwill_max_credits_per_year is 1 (Member, Silver), one prior courtesy credit within 365 days already blocks the next credit, so the repeat-adjustment tiers "exactly one" and "two or more" are unreachable there (the windows differ by the 12-month vs 365-day convention only at the edge). Obsidian (cap 4) is unaffected.
- **D9 — observation.** Base `rewards_points_expiry_rules` states a cross-problem order ("redeems them before closing"). No edge rests on it, and neither task involves closure.

## closing_checklist

(Pending: written only after both tasks' blind derivations are frozen and compared. See the post-reveal note appended below.)

### r1 post-reveal status (written 2026-09-24T23:47Z, after both comparisons)

Not closed. The Step 4 checklist is not written because two relationships fail:

| task | policy self-consistency | problem tree | factors | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | SOURCE-FACTOR RED (T0-R1 ← D1; T0-R2 false near-miss assertion) | PASS (blind derivation = GT on every argument) | SOURCE-FACTOR RED |
| 1 | PASS | PASS | SOURCE-FACTOR RED (T1-R1 ← D1; T1-R2 false near-miss assertions) | PASS (blind derivation = GT on every argument) | SOURCE-FACTOR RED |

- Items of the checklist that already hold:
  - one audit file per task, plus this file;
  - scopes are pairwise disjoint and cover all six extended policies;
  - task tools are closed with independent uuid8s;
  - each tree has 2 prerequisite problems and 2 `value_input` edges, one `owner=user` write, and no cycle, and the difficulty-wide graph is a DAG;
  - every factor bears weight against an honest baseline, and every all-baseline number differs from gold.
- Items that fail: the one-honest-`method`-per-computation floor (D1) in 5 of 6 computations, and the truth of three near-miss assertions in `design_rationale`.
- The instantiation-stage gates were not re-run by this auditor (the audit does not modify artifacts). The coordinator's snapshot `snap/d4_r1.txt` stands as supplied.

## revision_2

### charter_global_frozen (r2)

- Round r2 (re-audit after rework). Auditor: the same independent policy-task auditor (claude-opus-5-5). Frozen 2026-09-25T00:05Z, before either r2 task JSON was opened. The r1 text above is left untouched. r1 file hashes at the start of r2: `_difficulty.md` 69e9c011…dce8, `0.md` 5ce3007e…9195, `1.md` 1a1dded5…bc8.
- Shared inputs changed, so every charter-global section is re-derived in full, not carried forward:
  - `rewards.extended.yaml` r1 `0f639600…a025` → r2 `b72678cf2a5e85807963e95bd200ff4054e91ce725b051f58e7a3233d5121661`
  - `task_tools.py` r1 `ea80fe55…f8e4` → r2 `67433db6e3181968f3f14c6372adc38358f47b73e80e5a986c27105b77e4edc8`
  - The base section (lines 1-952) is still identical to `blueprint/products/rewards.yaml`, apart from the trailing blank line.
- Entry conditions:
  - The r2 masked views match the brief: `coord/views/…/r2/0.view.json` `2532a08e…573f` and `1.view.json` `700177d6…ad28`.
  - The gate snapshot `coord/snap/d4_r2.txt` shows all seven gates OK (check_compute now reports branches 47/46 and history rows 66/74). check_traceability is deferred as before.
- Masked and not read before the freeze: `tasks/*.json` and `worklog.md`.

### policy_conflict_scan (r2)

- Same six policies, subjects, target tools and owners as r1. No new overlapping quantity.
- Scope partition (task 0 = anniversary/clawback/gift card, task 1 = courtesy/milestone/charity) is unchanged, disjoint and complete.
- **D2 is closed.** Both whole-balance rules now read "A whole-balance gift card redemption [charity donation] is available only when none of the points balance is still pending, so that the whole balance is redeemable, and the points redeemed [donated] are then the points balance on the handling date rounded down …". Balance-based points and "only redeemable points" can no longer diverge.
- **D3 is closed on the amount.** The milestone tier amount is now "the milestone_bonus_points of the tier held on the credit date", which equals `P('milestone_bonus_points')`. Eligibility still reads "the milestone_quarterly_spend_threshold of the tier held on the quarter's last day". That is an eligibility gate, not a compute binding, and it is inside the declared replacement of base sentence 1.
- No new conflict.

### rule_compute_equivalence (r2)

The re-swept items are listed below. Everything unchanged since r1 was re-read and still holds.

- Anniversary: new rule sentence "Earning entries are the entries that credit base and category points on a card purchase; boost entries, which carry the same purchase's spend, are not earning entries." It matches the `event_type='rewards_cashback_earned'` filter. The same definition sentence is added to the clawback, gift card, courtesy, milestone and charity rules. **D6 is closed.** The gift card rule's "boost earning entries" is now "boost entries".
- Clawback:
  - `rate_method_clawback` = ceil(refund × `P('base_earn_rate_points_per_dollar')`) ⇔ "the rate-method clawback is the refunded amount times the base_earn_rate_points_per_dollar of the tier held on the handling date, rounded up to whole points".
  - `aged_clawback` = rate / `MN(standard, rate)` / standard ⇔ the three-way age sentence.
  - The reliefs, the `MX(0,…)` floor and the cap are unchanged. Equivalent.
- Gift card: `gc_value_cents` ⇔ the plan-valuation sentence:
  - banded: points × rate + `MX(0, points − 5000)` × 0.10;
  - block: points × rate + (points // 5000) × 250;
  - flat: points × rate.
  - `result` floors once. Equivalent.
- Courtesy: `cty_volume_12m` (sum of redemption points, any kind, 12 months) and `cty_form` (volume × 0.02 / tier + (volume − 100000) × 0.01 / tier) ⇔ rule sentences 6-7. The repeat adjustment is removed from rule and compute alike. `result` is the sum. Equivalent.
- Milestone: `ms_spend_measure` (3-month net) and `ms_form` (spend × 1.5 / tier + `MX(0, spend − P(threshold))` × 0.5 / tier) ⇔ the streak-form sentence. The threshold "of the tier held on the credit date" is `P('milestone_quarterly_spend_threshold')`. Equivalent.
- Charity: `ch_redemptions_12m` (any kind) and `ch_value_cents`:
  - banded: points × rate + `MX(0, points − 20000)` × 0.10;
  - block: points × rate + (points // 10000) × 200;
  - flat: points × rate.
  - This matches the charity-valuation sentence. Equivalent.
- **D7 is closed.** `inputs.history` now lists the clawback-spend reads for courtesy (12 months) and charity (3 months).

### action_binding_and_uuids (r2)

- Same six tools, same uuid8s, still one policy per `(target_tool, computes)`.
- **D5 is closed.** `credit_anniversary_bonus_4deaf7db` and `credit_quarterly_milestone_bonus_7b7b30cf` no longer take `bonus_type`. Each hard-codes its own ("this tool books anniversary bonuses only" / "… quarterly milestone bonuses only").
- Bodies are still unconditional: one insert plus a balance delta, no branch on state.
- No docstring carries before / after / first / then / until.

### prerequisite_graph and prerequisite_sentences (r2)

- **D4 is closed.**
  - E1 is now "The points clawed back are fixed only after the ledger carries the anniversary bonus for the most recent enrolment anniversary the membership has reached while active.", with the condition narrowed to "the most recent anniversary". That is exactly what the anniversary rule can book.
  - E2 is now "A whole-balance gift card redemption is not valued until the ledger carries a clawback entry for the latest merchant refund of an earning purchase posted within the clawback window.", with a matching condition. That is exactly the refund the clawback rule assesses.
  - Both keep the four-point test: the connectives are "only after" / "not … until", the state is record-visible, there is no tool, id or code token, and the strength matches the condition.
- E3 and E4 are unchanged and pass as in r1.
- Graph: two components, acyclic. `kind`/`gate`/`resolved_by` are unchanged and valid (`clawback_balance_cap`, `gc_redeem_points`, `ch_donate_points` all exist).
- Residual observation (new, R2-O1): E4's "for every ended quarter … a quarterly milestone bonus entry dated after that quarter's last day", together with the milestone dedup "no quarterly milestone bonus entry dated after the last day of the quarter", means one later entry satisfies every earlier quarter. A world with two consecutive qualifying, unpaid quarters would have one of them unpaid but E4 satisfied. Neither task's world realises this, and it is not demonstrable.

### override_declarations (r2)

- Clawback: the new age method sits inside the declared replacement of base sentence 1. The rest is followed as in r1.
- Gift card and charity: the replaced_by texts are updated to the valuation methods and declared. The "available only when none of the points balance is still pending" sentence narrows the base, but no longer contradicts base sentence 2 (D2 closed).
- Courtesy: the declared replacement now describes form + supplements.
- Milestone: base sentence 1, including "at the tier held on the last day of a quarter", is named as superseded. The credit-date amount tier is therefore a declared change.
- No undeclared override.

### factor_ladders (r2)

| policy | method factor (r2) | tiers | genuinely different algorithms? |
| --- | --- | --- | --- |
| anniversary | anniversary_bonus_form | spend × 0.11 replaces tier / tier + (spend − 30000) × 0.05 / tier | yes (unchanged) |
| clawback | clawback_age_method | refund × base rate (replaces the proportional share) / min(proportional, rate) / proportional | yes: a different base quantity and a min-of-two selection |
| gift card | gift_card_plan_valuation | banded pricing above 5000 points / per-5000-point block bonus / flat | yes: three functional forms |
| courtesy | courtesy_volume_form | volume × 0.02 replaces tier / tier + excess × 0.01 / tier | yes |
| milestone | milestone_streak_form | 3-month spend × 1.5 replaces tier / tier + (spend − threshold)⁺ × 0.5 / tier | yes |
| charity | charity_valuation | banded above 20000 points / per-10000-point block bonus / flat | yes |

- **D1 is closed.** Every computation now carries exactly one `method` factor that changes the algorithm, not a number in a fixed stage. Every other factor is an additive `parameter` ladder as in r1.
- Counts:
  - anniversary 5 (4 parameter / 1 method);
  - clawback 4 (3/1);
  - gift card 5 (4/1);
  - courtesy 5 (4/1);
  - milestone 6 (5/1);
  - charity 6 (5/1).
- Multi-source and cross-difficulty factors:
  - task 0: multi-source are DD, loyalty, engaged lift and plan valuation; cross-difficulty are card and wallet.
  - task 1: multi-source are courtesy loyalty, milestone DD and charity giving; cross-difficulty are card and wallet.
- Every ladder has 3 disjoint tiers stated in full in its rule and implemented in `decides`. No two tiers share a value or method. Every fall-through equals its baseline.
- Observations (new):
  - R2-O2: `clawback_age_method`'s middle tier min(standard, rate) equals the rate method whenever the refunded purchase earned at least the tier's base rate per USD, which is the usual case, since base + category + direct-deposit points ≥ base. It differs only when the earning was cut (per-purchase or monthly cap, or earned at a lower tier's rate). So the two upper tiers are distinct methods that often give the same number. No two tiers are identical as stated, and neither task realises the middle tier.
  - D8 residue: the anniversary clean-record supplement, the gift card boost lift and the clawback category relief remain; the charity boost multiplier and the courtesy repeat adjustment are gone. None is demonstrable as a treatment no business would publish.

### findings (r2)

- D1 closed. D2 closed. D3 closed. D4 closed. D5 closed. D6 closed. D7 closed.
- D8: partially addressed, observation only.
- D9: unchanged, observation.
- New: R2-O1 and R2-O2, both observations only.
- No new charter-global RED.

### closing_checklist (r2, written after both r2 comparisons)

| task | policy self-consistency | problem tree | factors | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS (blind = GT on every argument) | **PASS** |
| 1 | PASS | PASS | PASS | PASS (blind = GT on every argument) | **PASS** |

- Report files correspond one to one with tasks 0 and 1, with this file alongside. r1 text is preserved above each `## revision_2`, and every comparison section of r2 carries a PASS.
- Coverage and scope:
  - all six extended policies are covered;
  - task scopes (each whole tree) are pairwise disjoint;
  - the task tools are closed over GT;
  - the six uuid8s are independent and unchanged.
- Trees:
  - each has 2 prerequisite problems and 2 `value_input` edges (floor 1), one `owner=user` write and no cycle;
  - the difficulty-wide graph is a DAG in two components.
- Factors:
  - every computation has 4-6 factors, with ≥ 2 parameter and exactly 1 honest method;
  - each task has ≥ 1 multi-source and ≥ 1 cross-difficulty factor, whose wallet and card rows are seeded;
  - every ladder has 3 disjoint tiers stated in the rule;
  - every factor bears weight against an honest baseline, and every all-baseline number differs from gold.
- Item-by-item closure of r1:
  - D1, D2, D3, D4, D5, D6 and D7 are closed.
  - T0-R1, T0-R2, T1-R1 and T1-R2 are closed.
  - T0-O1 and T0-O2 are closed.
  - D8 is partially addressed and remains an observation.
  - D9 and T1-O1 are unchanged and remain observations.
  - New observations R2-O1 and R2-O2 are charter-global and realised in neither world.
- Gates on the final form: the auditor did not re-run them. The coordinator's post-rework snapshot `coord/snap/d4_r2.txt` shows EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE all OK, with traceability deferred to step 3.
- The difficulty passes the source-layer policy-task audit in r2.

## revision_3

### charter_global_frozen (r3)

- Round r3, triggered by the coordinator's check_traceability failure on task 1 after the KB render (`coord/snap/rewards_render_r1.txt`: "'2026-Q3' (call_agent_discoverable_tool:arguments.bonus_period) has NO verbatim source in the agent-reachable context").
- Auditor: the same. Frozen 2026-09-25T01:07Z, before the r3 task JSONs were opened. r2 file hashes at the start of r3: `_difficulty.md` a3cb7546…7118, `0.md` b61861e9…944f, `1.md` ae95df28…f871.
- Shared inputs are unchanged, re-verified by sha256sum: `rewards.extended.yaml` `b72678cf…1661` and `task_tools.py` `67433db6…edc8`, both equal to r2. Per the re-audit rule, every charter-global section of `## revision_2` (conflict scan, rule/compute equivalence, action binding and uuids, prerequisite graph and sentences, override declarations, factor ladders, findings) is **carried forward by reference, not re-derived**, on the grounds of these two unchanged hashes.
- Entry conditions:
  - r3 views: `0.view.json` `2532a08e…573f` (identical to r2) and `1.view.json` `c56d0c8d…c8f4` (changed).
  - Gate snapshot `coord/snap/d4_r3.txt`: all eight gates OK, including TRACEABILITY OK (1.json copied 20, missing 0).
- One discrepancy against the brief, recorded here and examined per task. The brief says "Only tasks/1.json changed", yet `tasks/0.json` now hashes `57c9bc773e4d3158d5aa15aaf7ba2356a58640add17eb02615438469af7d5f20`, whereas at the r2 reveal it was `f8db86b7…c466`. Task 0's view is unchanged, so the edit can only be in masked fields. It is compared after the freeze in `0.md#revision_3`.

### closing_checklist (r3, written after both r3 comparisons)

| task | policy self-consistency | problem tree | factors | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** (carried forward: view, charter and tools unchanged; GT fields identical) |
| 1 | PASS | PASS | PASS | PASS | **PASS** (one added wallet deposit; no tier, value, condition or near-miss moved; `2026-Q3` reachable via `find_wallet_transactions` before the milestone write) |

- The r2 checklist items all still hold: coverage, disjoint scopes, closed tools with independent uuid8s, 2-problem trees with 2 `value_input` edges and an owner=user write, a DAG, 4-6 factors with ≥ 2 parameter / 1 honest method per computation, and multi-source and cross-difficulty factors per task.
- New observations in r3:
  - R3-O1: the payroll reference is used as the verbatim echo of the milestone period.
  - R3-O2: the `tasks/0.json` bytes changed although the brief says only 1.json did. No scored or verified field differs.
- Gates on the final form: the coordinator's `coord/snap/d4_r3.txt` shows all eight OK, including TRACEABILITY OK. Not re-run by the auditor.
- The difficulty passes the source-layer policy-task audit in r3.
