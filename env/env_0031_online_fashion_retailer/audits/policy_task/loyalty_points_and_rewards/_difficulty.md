# Policy-task audit — loyalty_points_and_rewards / charter-global

## charter_global_frozen

- Scenario: `env/env_0031_online_fashion_retailer`; difficulty `loyalty_points_and_rewards`; category `loyalty`; M = 2 (tasks 0, 1).
- Auditor: erl-task-policy-audit sub-agent (independent of the instantiating agent). Freeze time of this section: 2026-10-05T00:55Z (wall clock), written before any task's GT was revealed.
- Freeze hashes (re-checked with `sha256sum -c HASHES.txt`, all OK):
  - `tasks/loyalty_points_and_rewards/loyalty.extended.yaml` 20c7a7efee924bbbda447db58b6a1f1aeeea8582336b5fc313935bb50c6e5268
  - `tasks/loyalty_points_and_rewards/task_tools.py` db8e23361e1d0091c97ed21526f0f0ad1acce9401971cf829e1ad1763d3aa25e
  - `blueprint/products/loyalty.yaml` 5c09dab9cbc7f47306538254236577de29950c8eeb3ea45f198282bc443bfd39; `blueprint/db_schema.json` d5842a71…1189; `blueprint/share_tools.py` 4027df5f…2dc5
- Fields permitted: blueprint (blueprint.yaml, db_schema.json, share_tools.py, products/loyalty.yaml), the extended charter, task_tools.py, the coordinator's masked views `audits/_views/policy_task/loyalty_points_and_rewards/{0,1}.view.json` (frozen_time, user_scenario, initial_state only).
- Fields masked and not read while this section was written: `tasks/loyalty_points_and_rewards/tasks/*.json` in full (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure), `tasks/loyalty_points_and_rewards/worklog.md`, the scenario-level `worklog.md`, any earlier audit. No recursive search touched `tasks/`.
- Entry conditions (Step 0): gate snapshot `audits/_views/policy_task/loyalty_points_and_rewards/GATES.txt` shows EXTENDED, TASK-TOOL-CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK, CACHE-DIFF INFO, traceability deferred to the KB stage; masked views and hashes supplied (`HASHES.txt`). Entry conditions met; the gates were cited, not re-run.
- Base copy: `diff <(sed -n 1,1199p loyalty.extended.yaml) blueprint/products/loyalty.yaml` differs only by one trailing blank line — the base section is verbatim.

### policy_conflict_scan

Extended policies (5), with subject, trigger, target tool and owner:

| policy | subject | trigger | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- | --- |
| loyalty_ext_returned_merchandise_reversal | loyalty_points_reversed | state_due | post_points_reversal_46de2c04 (agent) | points_reversed | [] |
| loyalty_ext_delivery_failure_goodwill | loyalty_bonus_posted | on_request | accept_goodwill_points_7ea0a08d (user) | goodwill_points | value_input <- reversal |
| loyalty_ext_missing_points_adjustment | loyalty_points_earned | state_due | post_missing_points_b5bbe1fa (agent) | points | [] |
| loyalty_ext_tier_upgrade | loyalty_tier_changed | state_due | write_tier_upgrade_189dabab (agent) | variant_name | value_input <- missing points |
| loyalty_ext_birthday_make_good | loyalty_bonus_posted | on_request | claim_birthday_bonus_8dc2d134 (user) | birthday_points | value_input <- tier upgrade |

Overlapping subjects:
- `loyalty_bonus_posted` is shared by goodwill and birthday make-good. They are separated by bonus_type and bonus_reference (claim id vs year) and by distinct tools; neither rule's trigger can fire on the other's object (goodwill needs an approved delivery claim; the make-good needs a birthday not posted because the tier carried 0). No conflict.
- `loyalty_points_earned` (missing points) vs base `loyalty_evt_points_earning` (dispatch posting, system-run, no tool here): different earning sources (missing_points_adjustment vs online_order). No conflict.
- Time anchors: every extended policy evaluates on the handling date (the frozen date plus the preceding synchronous writes). Windows: 12 months ending on the handling date, exclusive of the date exactly 12 months before (reversal, goodwill, tier, birthday, missing points 6/12 months); current calendar year (goodwill annual cap, tier spend window for >= 24 months). Compatible.
- Cross-category reads: returns, orders, claims, pass, preorders as declared in each `cross_category`; the EXTENDED gate confirms the declared reads match compute. Reads only, never writes, so no boundary conflict.
- Terminal states: reversal and missing points change `loyalty_ledger` + `points_balance`; tier upgrade changes `variant_name`, `tier_start_date`, `tier_valid_through`; goodwill and birthday add bonus rows. No two policies write the same field with different values in one state.

Task scopes (claimed scope inferred from user_scenario + prerequisite graph; confirmed against `charter_scope` only after reveal): task 0 = {goodwill (root), reversal}; task 1 = {birthday make-good (root), tier upgrade, missing points}. Pairwise disjoint; jointly complete over the 5 extended policies.

### rule_compute_equivalence

Mechanical check (script over the yaml): every `compute_basis` value is a verbatim substring of its policy's `rule` (0 misses); compute keys == compute_basis keys for all 5 policies; every `baseline.rule` sentence is a verbatim sentence of the `rule`; every `superseded_clause` is verbatim in its base rule; every `replaced_by` is verbatim in the extended rule; every prerequisite `policy_source` is verbatim in its own rule.

Semantic sweep, policy by policy (rule sentence -> binding):

- Reversal: object (settled return, its order), reversed spend (credited merchandise − restocking fee − Rewards-Note share, to the cent), original multiplier, trailing 12-month return share and earning count, three-tier multiplier, reason share, service-recovery share, plan share, combined share, single rounding — each implemented. Inventions: `MX(0, refunded_merch - restock_fee)` floors at zero and `return_share_pct = 0 if qual_12m == 0` define cases the rule is silent on (observation O1). `ret_id = CFIELD('returns','return_id', status='settled')` does not implement the rule's object filter "no points reversal stands on the ledger for that return and order"; with two settled returns its pick is unspecified (observation O2; CFIELD multi-match semantics are not in the auditor's read domain).
- Goodwill: approved claim and its order, order net points, claim-type start, paid-delivery / repeat-failure / tenure uplifts added into one rate, rounding, per-case cap, annual cap. `MX(0, order_net_points)` floors a negative net at zero, which the rule does not state (O1).
- Missing points: qualifying spend, tier multiplier plus four accelerators, late-credit factor, single rounding. **`x_order = CFIELD('preorders','fulfilment_order_id', status='fulfilled')` does not implement the rule's object sentence** "The order concerned is the dispatched order the request names; when that order fulfilled a reservation, it is the order recorded as the reservation's fulfilment order." -> finding G4.
- Tier upgrade: spend window by membership age, store-credit relief, deposit credit, status credit, rounding, highest tier met, never lowered. **`deposits_12m = XSUM('preorders','reservation_events','amount_usd', within_months=12, …, event_type='preorders_deposit_captured')` sums deposits on every reservation of the customer**, while the rule credits "deposits captured in the 12 months ending on the handling date on the member's Deposit Pre-Order" -> finding G6.
- Birthday make-good: tier amount, shopping factor, three gifts, rounding, zero rule. **`month_merch = XSUM(... within_months=1 ...)` is a trailing one-month window ending on the claim date**, while the rule reads "the merchandise booked on the member's orders placed in the current calendar month" -> finding G5.
- Every factor ladder tier appears both as a rule sentence and as a branch of its `decides` binding, and every branch is a stated tier (checked for all 21 factors). No tier lives only in compute.

### action_binding_and_uuids

- Five `(target_tool, computes)` pairs, each claimed by exactly one policy; no base policy names a task tool.
- Tool bodies (`task_tools.py`) each do one create/update with the values passed in; none reads eligibility, none refuses, none hints. Docstrings carry no ordering word about other actions and name no other tool ("before the annual review re-evaluates it" in `write_tier_upgrade_189dabab.tier_valid_through` describes the validity date, not a sequence of tool calls).
- uuid8 tails: 46de2c04, 7ea0a08d, b5bbe1fa, 189dabab, 8dc2d134 — pairwise distinct, no shared prefix, no sequence, no adjacency. PASS.
- Owners: two `owner="user"` tools (goodwill acceptance, birthday claim) — the rules state the in-person act ("credited only when the member accepts it in person"; "the member claims it in person"). The blueprint's difficulty summary assigns goodwill and other bonuses to the agent and only closure to the customer (observation O3; the summary is not a policy sentence, so no conflict with the charter).

### prerequisite_graph

| edge | kind / gate | form | policy_source located verbatim in own rule | resolved_by = depended-on target_tool | gate binding exists |
| --- | --- | --- | --- | --- | --- |
| goodwill -> reversal | value_input / order_net_points | state | yes | yes (post_points_reversal_46de2c04) | yes |
| tier upgrade -> missing points | value_input / window_qual | state | yes | yes (post_missing_points_b5bbe1fa) | yes |
| birthday -> tier upgrade | value_input / tier_amount | state | yes | yes (write_tier_upgrade_189dabab) | yes |

- `prerequisite` present on all 5 policies ([] on reversal and missing points); every `problem` is an extended policy id of this file, none is a base id or self; graph is acyclic (two disjoint chains). No `fallback_reason` present and none required (all state form).
- `effect` statements hold: a reversal row on the claim's order lowers `order_net_points`; a missing earning entry adds to `window_qual`; a tier write changes `P('birthday_bonus_points')`.
- `condition` wording vs sentence: edge goodwill->reversal condition says "every return in status settled on the approved claim's order", sentence says "every refunded return made against the order the claim concerns" — the condition keys on settled, the sentence on refunded (observation O4; identical on both task worlds). Edge birthday->tier condition "variant_name equals the tier the tier-upgrade rule yields … at handling time" is satisfied only once that rule is itself worked out after its own prerequisite (observation O5; see task 1 problem_chain). No authoring-viewpoint wording ("in this task", "at the opening").

### prerequisite_sentences

1. Goodwill: "The goodwill grant is fixed only after the points ledger carries a reversal entry for every refunded return made against the order the claim concerns." — connective "only after"; waits on a record-visible state (points ledger, reversal entry, refunded return — the words of `find_loyalty_ledger` "reversals" and the return finders); no tool, id, snake_case token; strength: universal over refunded returns on that one order. Exactly one write of this difficulty creates a `loyalty_points_reversed` row: the reversal policy's tool. Derivation: sentence -> look up returns of the claim's order with a refund and the ledger by return_id -> where absent, the reversal rule ("When a return of an order that earned points has been refunded and no points reversal stands on the ledger for that return and order, the agent posts the reversal") is the policy that writes it. Single reading. The reversal rule does not restate the sentence. PASS.
2. Tier upgrade: "The tier the membership takes is worked out only after every dispatched order placed under the member's profile within the missing-points request window carries its earning entry on the points ledger." — "only after"; record-visible state (dispatched orders, earning entry, points ledger); no tool/id; only the missing-points policy's tool writes an earning entry (dispatch postings are system-run). Derivation: list orders shipped/delivered/closed placed within 90 days, match ledger by order_id, the one lacking an entry is resolved under the missing-points rule ("A dispatched order of the member that carries no earning entry is owed its points, and the agent posts one missing_points_adjustment entry for it"). Single reading. PASS.
3. Birthday make-good: "The birthday bonus is not posted until the membership carries the tier its tier-qualifying spend has reached under the tier rules." — "not … until"; record-visible state (the tier the membership carries); "tier-qualifying spend" is the defined term of the extended tier-upgrade rule, which supersedes the base ytd measure, so "the tier rules" resolve to the extended upgrade rule; only `write_tier_upgrade_189dabab` changes `variant_name`. Single reading. PASS.
- No rule states a cross-problem order beyond these three sentences (sweep of all five extended rules). Base rules: `loyalty_evt_reward_conversion` "Conversion is blocked while the total points_balance is below zero" is a state gate on a system process with no tool here; it grounds no edge and no task rests on it (no finding).

### override_declarations

Sentence-by-sentence against every `base_policy_refs` entry (finding half only; each task file demonstrates the consequence on its own world):

- Reversal vs `loyalty_evt_points_reversal`: trigger sentence and multiplier/rounding sentence are superseded and declared; reversed-spend sentence followed (note-paid part made proportional — a refinement, same quantity); active/suspended, one-per-return-order, never-earned, negative balance, tier unaffected, notes never withdrawn — all inherited. No undeclared override.
- Goodwill vs `loyalty_evt_goodwill_points` / `loyalty_evt_bonus_points`: grant formula superseded and declared. **Base eligibility "A goodwill grant requires a delivery claim on record for the referenced order whose status is approved or resolved" is narrowed by the extended selector "The claim concerned is the member's delivery claim in status approved" (and compute `status='approved'`): the resolved branch is dropped without an `overwrite` entry** -> finding G1. Dedup per claim, availability, tier-on-posting-date caps, active-only — inherited.
- Missing points vs `loyalty_evt_missing_points` / `loyalty_evt_points_earning`: computation sentence superseded and declared. Base trigger "When a member reports that a dispatched order did not earn points, the agent posts…" vs extended `state_due` "is owed its points, and the agent posts one…" — the extended rule still names "the dispatched order the request names", so the report remains the object source (observation O6). Recording: extended records "that tier's tier_points_multiplier" while its own rule calls tier + accelerators "The multiplier applied", and the base event field reads "tier_multiplier_applied: The multiplier applied (copied from the tier)" — the explicit extended sentence and the tool docstring ("the tier_points_multiplier of the tier the membership holds today … for example 1.00") pin one value (observation O7).
- Tier upgrade vs `loyalty_tier_qualification`: the upgrade trigger clause is superseded and declared. **Base "tier_start_date becomes that posting date and tier_valid_through becomes 31 December of the calendar year that follows the qualifying year" vs extended "the new tier takes effect on the date it is written and is valid through 31 December of the calendar year after that date" — not in any `overwrite`** -> finding G2. Never-lowered, active-only, review sentences — compatible.
- Birthday make-good vs `loyalty_evt_bonus_points` / `loyalty_evt_goodwill_points`: birthday posting sentence and once-per-reference sentence superseded and declared; the two goodwill sentences declared superseded "for" the make-good never conflicted with it (observation O8: harmless declarations whose rendering must not mark the base goodwill eligibility as superseded for the goodwill policy). Tenure, active-only, availability — inherited.

### factor_ladders

| policy | factor | label | decides | tiers | multi-source | cross_difficulty | label honest |
| --- | --- | --- | --- | --- | --- | --- | --- |
| reversal | return_record_multiplier | method | mult_used | 3 | yes (reversal entries x earning entries) | — | borderline, accepted (O9) |
| reversal | return_reason_share | parameter | reason_share | 3 | no | returns | yes |
| reversal | service_recovery_share | parameter | claim_share | 3 | tier 2 yes (order claim x claim_events) | claims | yes |
| reversal | unlimited_membership_share | parameter | plan_share | 3 | no (one pass row) | — | yes |
| goodwill | claim_type_grant_basis | method | starting_grant | 3 | no | claims | yes (different base quantity per tier) |
| goodwill | paid_delivery_uplift | parameter | paid_delivery_uplift | 3 | yes (pass x orders) | — | yes |
| goodwill | repeat_failure_uplift | parameter | repeat_failure_uplift | 3 | no | claims | yes |
| goodwill | membership_tenure_uplift | parameter | tenure_uplift | 3 | no | — | yes |
| missing | unlimited_earning_accelerator | parameter | plan_accel | 3 | no | — | yes |
| missing | reservation_fulfilment_accelerator | parameter | reservation_accel | 3 | no | preorders | yes |
| missing | basket_accelerator | parameter | basket_accel | 3 | yes (order lines x ledger count) | — | yes |
| missing | low_return_accelerator | parameter | low_return_accel | 3 | no | returns | yes |
| missing | late_credit_factor | **method** | late_factor | 3 | no | — | **no — G7** |
| tier | membership_age_spend_window | method | window_qual | 3 | no | — | yes (different window) |
| tier | store_credit_reversal_relief | parameter | deduct_share | 3 | no | returns | yes |
| tier | deposit_status_credit | parameter | deposit_share | 3 | no | preorders | yes |
| tier | unlimited_status_credit | parameter | status_rate | 3 | no | — | yes |
| birthday | birthday_month_shopping_factor | **method** | shop_factor | 3 | no | — | **no — G8** |
| birthday | birthday_tenure_gift | parameter | tenure_gift | 3 | no | — | yes |
| birthday | birthday_unlimited_gift | parameter | plan_gift | 3 | no | — | yes |
| birthday | birthday_items_bought_gift | parameter | items_gift | 3 | no | — | yes |

- Every factor: bindings pairwise disjoint within its policy (checked), `decides` is an input not `result`, 3 pairwise-disjoint tiers including the fall-through, no two tiers select the same value or method, every tier stated in the rule with its condition and value/method, fall-through equals the factor's `baseline`, and the baseline equals what `baseline.rule` states for that input (orig multiplier, share 1, per-case cap, uplift 0, accelerator 0, factor 1, calendar-year window, full deduction, no deposit credit, no status credit, gift 0).
- `baseline.rule` self-sufficient for all five (reversal: spend x base x original multiplier; goodwill: per-case cap then caps; missing: qualifying x base x tier multiplier; tier: calendar-year spend vs thresholds; birthday: tier birthday points). `baseline.params` names match.
- Counts per policy (as labelled): reversal 4 (1 method, 3 parameter); goodwill 4 (1/3); missing 5 (1/4); tier 4 (1/3); birthday 4 (1/3). After G7/G8: **missing points 5 (0 method, 5 parameter) and birthday 4 (0 method, 4 parameter) fall below the 1-method floor.**
- Categories read by cross_difficulty factors: returns, claims, preorders. `pass` and `orders` are not difficulties of this scenario and are correctly left `cross_difficulty: null`.
- Business-realism notes (observations, consequence not demonstrable): reversal shares that reverse fewer points for a defective/not-as-pictured reason, a claim on the order, or an Unlimited plan (O10); missing-points accelerators (Unlimited, reservation, basket, low-return) that pay a corrected posting more than the charter's own dispatch-posting rule would ever have paid on the same order (O11).

### findings

- **G1 — SOURCE-POLICY RED (charter-level, undeclared override / dropped branch).** Symptom: the extended goodwill policy only ever selects an approved claim. Root cause: base `loyalty_evt_goodwill_points` "A goodwill grant requires a delivery claim on record for the referenced order whose status is approved or resolved" vs extended "The claim concerned is the member's delivery claim in status approved" + compute `CFIELD('claims', 'order_id', status='approved')`; no `overwrite` names the base sentence. Demonstration (constructed situation): a Gold member whose damaged-parcel claim is `resolved` with no goodwill row asks for goodwill — base: eligible, a grant is computed; extended: no claim concerned, no grant. Bears on: task 0 (claims this policy) — no consequence on task 0's world (the customer's claim is approved; see 0.md).
- **G2 — SOURCE-POLICY RED (charter-level, undeclared override).** Base `loyalty_tier_qualification` "tier_start_date becomes that posting date and tier_valid_through becomes 31 December of the calendar year that follows the qualifying year" vs extended "the new tier takes effect on the date it is written and is valid through 31 December of the calendar year after that date"; no `overwrite` entry. Demonstration: spend reaches Silver on a 2025-12-20 posting, the upgrade is written 2026-01-05 — base valid through 2026-12-31, extended 2027-12-31 (`tier_valid_through` is a scored tool argument). Bears on: task 1 — no consequence on task 1's world (qualifying posting and write fall on the same handling date).
- **G4 — SOURCE-POLICY RED (charter-level, rule/compute non-equivalence).** Rule: "The order concerned is the dispatched order the request names; when that order fulfilled a reservation, it is the order recorded as the reservation's fulfilment order." Compute: `x_order = CFIELD('preorders', 'fulfilment_order_id', status='fulfilled')`. Demonstration: a member with no fulfilled reservation names an unearned order — rule: that order; compute: no order (all line sums over an absent id, result 0). Bears on: task 1 — no consequence on task 1's world (the named order is the fulfilled reservation's order).
- **G5 — SOURCE-POLICY RED (charter-level, rule/compute non-equivalence).** Rule: "the merchandise booked on the member's orders placed in the current calendar month"; compute `month_merch = XSUM('orders','order_lines','amount_usd', within_months=1, date_field='event_date', event_type='orders_line_booked')`. Demonstration: a claim on 17 August with a line booked 25 July — rule excludes it, a one-month trailing window includes it. Bears on: task 1 — no consequence (claim date 31 August; trailing month = calendar month).
- **G6 — SOURCE-POLICY RED (charter-level, rule/compute non-equivalence).** Rule: "deposits captured in the 12 months ending on the handling date on the member's Deposit Pre-Order"; compute `deposits_12m` sums `preorders_deposit_captured` over every reservation. Demonstration: a member with a Made-to-Order deposit captured in the window — compute credits it, the rule does not. Bears on: task 1 — no consequence (one deposit event, on the Deposit Pre-Order).
- **G7 — SOURCE-FACTOR RED (structure).** `late_credit_factor` is labelled `method` but its tiers are "multiplied by 1.10 before rounding" / "multiplied by 1.05 before rounding" / "taken as computed": one formula `round(q × base × multiplier × f)` with `f ∈ {K('long_delay_factor')=1.10, K('short_delay_factor')=1.05, 1.0}` — a rate substituted into the same formula, i.e. a `parameter`. The missing-points computation then has no honest `method` factor. Bears on: task 1 (demonstrated in 1.md).
- **G8 — SOURCE-FACTOR RED (structure).** `birthday_month_shopping_factor` is labelled `method` but its tiers "doubled" / "multiplied by 1.5" / "taken as it stands" are `round(tier_amount × s)` with `s ∈ {K('big_month_factor')=2.0, K('some_month_factor')=1.5, 1.0}` — a parameter. The birthday computation then has no honest `method` factor. Bears on: task 1.
- Observations: O1 (compute floors/zero-division cases the rule is silent on), O2 (reversal object pick with several settled returns), O3 (blueprint summary assigns goodwill posting to the agent; charter makes it a user acceptance), O4 (goodwill edge condition "settled" vs sentence "refunded"), O5 (birthday edge condition wording), O6 (missing-points trigger shift report -> state_due), O7 (recorded multiplier wording), O8 (birthday policy declares supersession of goodwill sentences it does not conflict with), O9 (`return_record_multiplier` tiers select 1.00 / midpoint / recorded multiplier — the multiplier's source changes, accepted as a method; strict reading would class it as a rate), O10/O11 (realism notes above). Also: every computing rule states the baseline formula as an unconditional sentence ahead of the factor sentences (e.g. goodwill "The grant starts from the goodwill_points_per_case_cap of the tier held on the posting date." then "The starting figure depends on the claim type: …"); a whole-rule reading resolves it as general-then-specific, and the baseline-in-rule form is what the charter contract requires (O12).

## closing_checklist

Written after both reveals (2026-10-05T00:59Z); nothing above this heading was changed after any reveal.

- Per-task files: `0.md`, `1.md` correspond one-to-one with tasks 0 and 1; first revision, no earlier audit exists.
- Scope: `charter_scope` task 0 = {returned_merchandise_reversal, delivery_failure_goodwill; post_points_reversal_46de2c04, accept_goodwill_points_7ea0a08d}; task 1 = {missing_points_adjustment, tier_upgrade, birthday_make_good; post_missing_points_b5bbe1fa, write_tier_upgrade_189dabab, claim_birthday_bonus_8dc2d134} — matches the pre-reveal inference; pairwise disjoint; all 5 extended policies and 5 task tools covered; uuid8s independent (see § action_binding_and_uuids).
- Problem trees: task 0 n=1 (1 value_input), task 1 n=2 (2 value_input); each has one owner=user root; the difficulty's prerequisite graph is acyclic with no cross-task edge.
- Factors: task 0 — both computations pass (4 factors, 1 method, 3 parameter each; multi-source and cross-difficulty present; every factor bears weight; fall-backs 62 and 400 differ from gold). Task 1 — every factor bears weight and the fall-backs (168, Member, 250) differ from gold, but the missing-points and birthday computations have no honest method factor (G7, G8).
- Comparison sections: task 0 **SOURCE-TASK RED** (T0-F1, false seed-consistency assertion; scored values match); task 1 **SOURCE-FACTOR RED** (T1-F1, T1-F2; scored values match).
- Charter-level SOURCE-POLICY findings without a consequence on either task's world: G1, G2, G4, G5, G6.
- Gate re-run on the final form: not performed — the artifacts were not changed by this audit (hashes unchanged: extended 20c7a7ef…, task_tools db8e2336…), and the coordinator's snapshot `GATES.txt` stands.
- **Difficulty status: NOT CLOSED** — the source-layer audit does not pass while T0-F1, T1-F1/F2 and the charter-level G-findings stand.

## revision_2

### charter_global_frozen (revision 2)

- Re-audit round 2. Written 2026-10-05T04:31Z (wall clock) before `tasks/0.json` and `tasks/1.json` of round 2 were opened; nothing in this section is derived from a round-2 reveal. Revision 1 above is left untouched.
- Hashes (`r2/HASHES.txt`, all OK): `loyalty.extended.yaml` **2584eafdda45e38fc2016e382bb2d146ae6bb95e974488d477b6d36ec3371503** (changed from 20c7a7ef… — every charter-global section is re-derived), `task_tools.py` db8e23361e1d0091c97ed21526f0f0ad1acce9401971cf829e1ad1763d3aa25e (unchanged — § action_binding_and_uuids carried forward by reference on that hash), views `r2/0.view.json` 447a0269…5d2c, `r2/1.view.json` 221ccc70…341b. Base section still verbatim with `blueprint/products/loyalty.yaml` (5c09dab9…; diff = one trailing blank line).
- Entry conditions: `r2/GATES.txt` — EXTENDED, TASK-TOOL-CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; CACHE-DIFF INFO; traceability deferred. Met.
- Masked and unread while writing: round-2 `tasks/*.json`, `worklog.md`. Disclosure: the auditor read the round-1 task JSONs during revision 1 (after that round's freeze); round-2 figures below are recomputed from the round-2 charter and views, and round-1 GT is not used as evidence.

### policy_conflict_scan (r2)

Same five policies, subjects, triggers, tools, owners and prerequisite graph as revision 1. New scope statement in the missing-points rule: "This adjustment governs the points of reservation fulfilment orders …; any other order without its earning entry is credited under the missing-points rule as it stands." — partitions orders between the extended and the base missing-points rule; no overlap. Goodwill now excludes resolved claims by a declared overwrite. Task scopes unchanged and disjoint (to be confirmed against `charter_scope` at reveal).

### rule_compute_equivalence (r2)

Mechanical check re-run: 0 compute_basis misses, compute keys == basis keys, all baseline sentences in rule, all superseded clauses verbatim in base, all replaced_by and policy_source verbatim in own rule — for all 5 policies.
- G4 re-checked: rule now "The order concerned is the order recorded as the fulfilment order of the member's reservation in status fulfilled", and scopes the policy to reservation fulfilment orders; compute `x_order = CFIELD('preorders', 'fulfilment_order_id', status='fulfilled')` implements exactly that. **Closed.** (Residual: with two fulfilled reservations both rule and compute leave the pick open — same class as O2, observation.)
- G5 re-checked: rule now "the merchandise booked on the member's orders placed within the month ending on the claim date (an order dated on the same day of the previous month not counting)" = `within_months=1`. **Closed.** (The birthday `cross_category` note still reads "Merchandise booked in the birth month" — note field only, observation N1.)
- G6 re-checked: `deposit_reservation = CFIELD('preorders','reservation_id', variant_name='Deposit Pre-Order')`, `deposits_12m` filtered by `reservation_id=deposit_reservation` = "on the member's Deposit Pre-Order". **Closed.**
- O1: reversal rule now states "(never below zero)" and "(zero when no qualifying spend was posted in those months)"; goodwill rule states net points "never taken below zero". **Closed.**
- New computations: missing points `rounded_points` + `late_credit` ("the product is rounded …; the late credit is then added"; late credit "10 percent of the rounded points, itself rounded … never less than 25 points; for 14 to 44 days, a flat 15 points; for fewer than 14 days, nothing") — implemented exactly. Birthday `boosted_amount` ("doubled" / "that merchandise is credited again as birthday points, at base_points_per_usd times the tier_points_multiplier of the tier held on the claim date, rounded … and added to the tier amount" / "stands") — implemented exactly. Reservation ladder now names every reservation type (Seasonal / Made-to-Order 0.25; Standard / Supplier Direct Back-Order none) — compute matches.

### action_binding_and_uuids (r2)

Carried forward from revision 1 by reference (task_tools.py hash unchanged, target_tool/computes pairs unchanged).

### prerequisite_graph (r2)

Unchanged edges, kinds, gates, forms, resolved_by; acyclic; no fallback_reason. Conditions re-worded: goodwill edge "every refunded return made against the approved claim's order (a return in status settled whose refund was issued)" — now matches the sentence's "refunded return" (**O4 closed**); birthday edge "the tier the tier-upgrade rule yields when that rule is worked out on a ledger that already carries every earning entry its own prerequisite requires" (**O5 closed**).

### prerequisite_sentences (r2)

The three sentences are verbatim unchanged; four-point test and single-writer derivations of revision 1 still hold (the tier sentence's state "every dispatched order … carries its earning entry" is written only by `post_missing_points_b5bbe1fa`, whether the order falls under the extended or the base missing-points rule). No new cross-problem order in any rule.

### override_declarations (r2)

- G1: goodwill now declares superseding the base sentence "A goodwill grant requires a delivery claim on record for the referenced order whose status is approved or resolved; …" with "A goodwill grant is made while the claim stands approved, as part of making the member whole on it; a claim already resolved has had its compensation booked and is closed to a further goodwill grant." — the narrowing is declared and the merged meaning is single. **Closed.**
- G2: tier upgrade now declares superseding "tier_start_date becomes that posting date and tier_valid_through becomes 31 December of the calendar year that follows the qualifying year (`tier_validity_years_after_qualifying_year`)." with "the new tier takes effect on the date it is written and is valid through 31 December of the calendar year that follows the year in which the tier-qualifying spend reached its threshold" — the validity anchor returns to the qualifying year and the start-date change is declared. **Closed.**
- Missing points: the computation clause stays declared; the late credit and the fulfilment-order scope sit inside the superseded "computed exactly as the dispatch posting" clause. O6 (trigger still framed by the base "request window") unchanged — observation.
- Birthday: overwrite replaced_by text updated to the shopping boost; declarations otherwise as revision 1 (O8 unchanged; note both goodwill and birthday now supersede the same base goodwill sentence, each for its own policy, with compatible meanings).

### factor_ladders (r2)

- G7: `late_credit` (method) — tiers "a percentage credit: 10 percent of the rounded points, rounded half up, with a floor of 25 points" / "a flat credit of 15 points, whatever the size of the order" / "no late credit": a proportional-with-floor credit, a fixed credit independent of the points, and none — the tiers change the form of the computation, not one constant in one formula. Honest method. **Closed.** Fall-through = baseline 0 (baseline.rule has no late credit).
- G8: `birthday_shopping_boost` (method) — "doubled" (multiplicative on the tier amount) / "the merchandise is credited again as points at base_points_per_usd times the tier multiplier … added to the tier amount" (additive, driven by the merchandise amount and the tier multiplier) / "stands". Different algorithms. Honest method. **Closed.** Fall-through = baseline (tier amount).
- Other 19 factors unchanged in label, ladder, bindings and baselines (reservation ladder now enumerates all reservation types; outcomes unchanged). Counts: reversal 4 (1 m / 3 p), goodwill 4 (1/3), missing points 5 (1/4), tier 4 (1/3), birthday 4 (1/3). Cross-difficulty categories: returns, claims, preorders.
- O9, O10, O11, O12 unchanged (observations).

### findings (r2)

- Revision-1 charter findings G1, G2, G4, G5, G6, G7, G8: closed (above).
- O1, O4, O5: closed. O2, O3, O6–O12: unchanged observations.
- New observation N1: birthday `cross_category[orders].note` "Merchandise booked in the birth month decides the shopping factor" no longer matches the rule's window ("within the month ending on the claim date"); the note is not a rule sentence and produces no second value.
- No new charter-level RED.

### closing_checklist (r2)

Written after the round-2 reveals (2026-10-05T04:32Z); § revision_2 above was frozen before them.
- Per-task files 0.md, 1.md each carry `## revision_2` (frozen derivation, comparison, findings); revision 1 text untouched.
- Scopes: task 0 {reversal, goodwill}, task 1 {missing points, tier upgrade, birthday} — disjoint, jointly cover the 5 extended policies and 5 task tools; uuid8s independent (task_tools.py unchanged).
- Trees: task 0 n=1 (1 value_input), task 1 n=2 (2 value_input); one owner=user root each; graph acyclic, no cross-task edge.
- Factors: every computation 4–5 factors with ≥ 2 parameter and 1 honest method; multi-source (paid_delivery_uplift / return_record_multiplier; basket_accelerator) and cross-difficulty (returns, claims; preorders, returns) per task; every factor bears weight against an honest baseline; every fall-back differs from gold.
- Round-1 REDs: G1, G2, G4, G5, G6, G7/T1-F1, G8/T1-F2, T0-F1 — all closed. Observations O1, O4, O5, T0-O2, T1-O2, T1-O1 closed; O2, O3, O6–O12 unchanged; new observations N1 (birthday cross_category note), T0-N1 (stale count in task 0 rationale). No new RED, no regression.
- Gates: coordinator snapshot `r2/GATES.txt` all green on the hashes audited (extended 2584eafd…, task_tools db8e2336…); not re-run by the auditor.
- **Difficulty status: source-layer audit PASS (task 0 PASS, task 1 PASS).**
