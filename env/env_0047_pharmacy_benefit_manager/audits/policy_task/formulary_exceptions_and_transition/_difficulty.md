# Policy-task audit — formulary_exceptions_and_transition / charter-global

## charter_global_frozen

- Scenario: `env/env_0047_pharmacy_benefit_manager`, difficulty `formulary_exceptions_and_transition`, M = 2.
- Freeze time: 2026-10-08 07:21 UTC (written before any task's GT was revealed; nothing in this section derives from a revealed GT).
- Auditor: erl-task-policy-audit subagent (independent of the instantiator; never read `worklog.md`, never read `tasks/*.json` before every per-task derivation was frozen).
- Frozen inputs (sha256, re-verified at audit start):
  - `tasks/formulary_exceptions_and_transition/formulary.extended.yaml` a6fa4d0b4b1ab79468f09e6dcbed95aad92ee340044de6fd401c1ac85795fa1a
  - `tasks/formulary_exceptions_and_transition/task_tools.py` e91de648edbf88565f6b9cb0908d1583050b64106f8cedf1ca3731bcca8b582c
- Permitted reads for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/*.yaml` (variant parameters of the categories the computations read), the extended charter, `task_tools.py`, the erlbench DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (helper definitions only).
- Masked / unread: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, closure fields; the instantiator worklog; any earlier audit (none existed).
- Entry conditions (Step 0): the brief supplied the gate snapshot (check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cross_fire SCOPE OK; check_traceability deferred to the KB stage), the masked views with hashes (task_0.view.json 3ffa66a1…, task_1.view.json 6016ed44… — both re-verified), and the policy-artifact hashes. Entry conditions complete; gates were not re-run by the auditor.

### policy_conflict_scan

Base section: lines 1-877 of the extended file are byte-identical to `blueprint/products/formulary.yaml` (diff shows only one trailing blank line). Base copy verbatim: PASS.

Eight extended policies, each with one target tool and one computed quantity:

| # | policy | subject | computes | target tool (owner) | prerequisites |
|---|---|---|---|---|---|
| 1 | formulary_ext_specialty_transition_days | formulary_transition_fill (specialty channel) | days_supply | record_specialty_transition_supply_d4f54566 (agent) | [] |
| 2 | formulary_ext_retail_transition_days | formulary_transition_fill (retail) | days_supply | record_retail_transition_supply_5b1515b2 (agent) | 1 (value_input, state) |
| 3 | formulary_ext_home_delivery_transition_days | formulary_transition_fill (home delivery) | days_supply | record_home_delivery_transition_supply_6840b972 (agent) | 2 (value_input, state); 4 (value_input, state) |
| 4 | formulary_ext_member_request_priority | formulary_exception_requested (member-opened) | review_priority | submit_member_exception_request_38483004 (user) | [] |
| 5 | formulary_ext_standard_nf_approval_months | formulary_exception_approved (standard NF) | approval_months | approve_standard_nonformulary_exception_57f550b5 (agent) | [] |
| 6 | formulary_ext_tier_approval_months | formulary_exception_approved (tier) | approval_months | approve_tier_exception_8a527f11 (agent) | 5 (value_input, state) |
| 7 | formulary_ext_external_review_priority | formulary_external_review_requested | review_priority | request_external_exception_review_e71b5dce (user) | [] |
| 8 | formulary_ext_expedited_approval_days | formulary_exception_approved (expedited) | approval_days | approve_expedited_exception_8cc2ac55 (agent) | 7 (value_input, action); 6 (state_gate); 5 (state_gate) |

Overlapping subjects and how they are separated:
- Policies 1/2/3 share `formulary_transition_fill`; they are separated by dispensing channel (each tool writes a fixed `dispensing_channel`) and each rule opens by naming its channel. No two of them reach a conclusion on the same fill. Compatible.
- Policies 5/6/8 share `formulary_exception_approved`. 5 is a standard NF approval, 8 is any expedited approval, 6 is "a tier exception request is approved" with no priority restriction in the rule text (only the tool docstring says "decided on the standard timeframe"). An expedited tier approval is therefore claimed by the rule texts of both 6 (months, `tier approval period`) and 8 (calendar days, `exigency period`). No task world contains an expedited tier request, so no task can demonstrate the second answer: recorded as observation O3 below.
- Policy 4 covers member-opened requests only; prescriber-opened requests have no extended priority rule (base timeline governs). Compatible.
- Policy 7 vs base `formulary_external_exception_review`: base fixes eligibility and decision hours, not how the priority is chosen. Compatible.
- Eligibility, time anchors, terminal states: every extended write inherits the base eligibility (active assignment; window `within_transition_window`; `statement_before_approval`; `decide_once`; `one_open_request_per_drug`; `review_only_after_denial`), none of which any extended rule relaxes. Policy 3 adds a channel precondition ("is not dispensed until the records carry an exception request…") that base `formulary_transition_supply` does not state; base says a member "may receive" a transition supply, so this is a strengthening, not a contradiction (observation O11).
- Cross-category read boundaries: every cross-category access is a read (CPARAM / CFIELD / X* aggregates); no extended policy writes another category's tables. Compatible.

Scope exclusivity / completeness (charter view, confirmed against `charter_scope` only after reveal — see task files): the prerequisite graph has exactly two weakly connected components, {1,2,3,4} rooted at 3 and {5,6,7,8} rooted at 8. Two tasks, two components: jointly complete over the eight policies and pairwise disjoint if each task claims one component.

### rule_compute_equivalence

Mechanical sweep: every `compute_basis` value is a verbatim substring of its policy's `rule` (whitespace-normalised; zero misses over all eight policies); every `baseline.rule` sentence is a sentence of its `rule`; no rule contains a snake_case token, tool name or policy id.

Sweep back, rule -> compute, per policy (only the non-trivial points are listed; every other quantity, window, filter, branch, cap/floor, rounding and order is implemented as stated):
- 1 specialty: cycles / cycle length / four allowances / on-hand deduction / order / floor-cap-int all implemented as stated. `paired` reads the keys of `biosimilar_pairs` (Humira -> adalimumab-adaz) as the rule's "pairs the drug with a preferred biosimilar". Two narrowings of compute against rule (observation O1/O6): the drug is a literal (`'Humira'`) and the biosimilar review allowance hard-codes `'adalimumab-adaz'` instead of reading the pair, and is not gated on the pairing the rule's opening clause names ("when the paired preferred biosimilar needs prior authorization").
- 2 retail: the starting length reads only the LATEST specialty / home-delivery transition fill and tests only `fill_date >= transition_start_date`; the rule says "a … supply of another drug dated inside the current transition window that is still running". With one fill per channel, equivalent; not exercised otherwise (observation O5). Home-delivery bridge tier 2: rule "the network applies its maintenance rule after the courtesy fills" also describes `retail90_or_mail` (schema: "after the courtesy fills a maintenance drug must be filled as 90 days at retail or by home delivery"), while compute tests only `mandatory_after_courtesy` — rule broader than compute; no world reaches tier 2 (observation O4).
- 3 home delivery: as stated. Dose cycle from the latest SHIPPED order; processing allowance compares the latest prescription with the latest shipped order.
- 4 member request: as stated; the final comparison sentence ("The comparison is made only after every wait has been added…") governs the earlier baseline sentence by its own wording, so the two do not conflict.
- 5 NF months: as stated; the trial credit is drug-specific in the rule itself ("the acute-migraine formulary alternatives (sumatriptan and Nurtec ODT)") — see observation O2.
- 6 tier months: as stated; "the lower-tier alternative (Trelegy Ellipta)" is drug-specific in the rule (observation O2). Alignment: compute tests the latest expiration among all approvals on the assignment ≥ handling date, equivalent to "an exception approval is in force".
- 7 external review: as stated (`dispensing_pharmacy == 'retail_pharmacy'` matches the schema enum).
- 8 expedited: as stated; all late-decision arithmetic is at date level, as the rule ("the due date being the date of …") prescribes.

Factor ladders against both faces: every tier of every `factors[].ladder` is a sentence of the rule and a branch of its `decides` binding, and every branch of each `decides` binding is a tier the rule states. No tier lives in only one face. PASS (with observations O1, O4, O5, O6).

### action_binding_and_uuids

- `(target_tool, computes)`: eight distinct tools, each claimed by exactly one policy. PASS.
- Tool bodies (`task_tools.py`): each performs one `ctx.create` with fixed channel / type fields and no condition, refusal, error or hint path; none reads another row to decide whether to proceed (the `ctx.find` calls only copy `customer_id`, `drug_strength`, `prescriber_npi`, `exception_type`). The tool layer judges no eligibility and no prerequisite. PASS.
- Docstrings: no docstring names another tool or states a position in a sequence. The only ordering-looking words are effect descriptions ("the fill then appears whenever…", "the day before the same day-of-month", "4 (the first specialty tier)"). PASS.
- uuid8s: d4f54566, 5b1515b2, 6840b972, 38483004, 57f550b5, 8a527f11, 8cc2ac55, e71b5dce — pairwise distinct, no shared prefix or suffix, no sequence. PASS.

### prerequisite_graph

Edges (blocked -> depended-on): 2->1, 3->2, 3->4, 6->5, 8->7, 8->6, 8->5. Every policy fills `prerequisite`; every `problem` is an extended policy id in this file, never a base id, never itself; the graph is acyclic (topological orders exist: 1,2,4,3 and 5,6,7,8). Every `policy_source` is verbatim in the blocked policy's own rule (mechanical check, 7/7). `form` is `state` on six edges and `action` on 8->7, which alone carries `fallback_reason`. `resolved_by` equals the depended-on policy's `target_tool` on all seven edges. `kind`/`gate`: value_input gates `sync_len`, `hd_sync_len`, `pending_ext`, `tier_period`, `review_bridge` all exist in the blocked policy's compute; the two state_gate edges point at `formulary_exceptions.event_type` (a field, not an `eligibility` id — policy 8 has no eligibility block; observation O8). No authoring-viewpoint phrasing ("in this task", "at the opening", "current world") appears in any prerequisite field.

`condition` vs the sentence (check 7):
- 2->1, 3->2: the condition requires "a row with dispensing_channel specialty/retail and a fill_date on or after the transition_start_date for every non-formulary drug whose…" without tying the row to that drug; the sentence ties it ("for every non-formulary drug …, a specialty transition supply"). Slightly weaker; equivalent in every world with one such drug (observation O5).
- 6->5 and 8->5/8->6: the condition computes "fell due" as "latest statement plus the standard decision hours" for every request, while base `formulary_evt_exception_timeline` makes an expedited request due at `exception_expedited_decision_hours`. Equivalent unless an expedited request sits between the two due times; see O7.
- 3->4, 8->7: match the sentence's strength and scope.

### prerequisite_sentences

Four-point test per edge (ordering connective / record-visible state or business action / no tool, policy id, snake token or row id / strength = condition):

| edge | sentence (connective) | form test | names nothing forbidden | strength |
|---|---|---|---|---|
| 2->1 | "…days supply is fixed only after the records carry, for every non-formulary drug whose specialty shipments to the member were still running on the transition start date, a specialty transition supply dated inside the current transition window." (only after) | state, record-visible (`formulary_transition_fills` channel specialty, `specialty_fills` ship_date/days_supply) | yes | closed set by kind ("every NF drug whose…") — matches |
| 3->2 | "…fixed only after the records carry, for every non-formulary drug whose retail fills were still running on the transition start date, a retail transition supply dated inside the current transition window." (only after) | state | yes | matches |
| 3->4 | "A home-delivery transition supply is not dispensed until the records carry an exception request for the drug received on or after the transition start date." (not … until) | state | yes | matches |
| 6->5 | "A tier exception approval's period is fixed only after every non-formulary exception request of the member that fell due earlier carries a decision on record." (only after) | state | yes | see O7 (comparator of "earlier" left implicit) |
| 8->7 | "An expedited approval's period is fixed only after the member has said whether they want an independent review of every earlier denial of the same drug." (only after) | action (member's election, business words) | yes | matches |
| 8->6 | "An expedited approval is not recorded until every tier exception request of the member whose decision fell due earlier carries a decision on record." (not … until) | state | yes | matches (O7 for due-time convention) |
| 8->5 | "An expedited approval is not recorded until every standard non-formulary exception request of the member whose decision fell due earlier carries a decision on record." (not … until) | state | yes | matches |

Fallback test (8->7): asking for review leaves a `formulary_external_review_requested` row; declining leaves nothing, so the state "an external review request is on record for every earlier denial" would force a request on a member who declines. No record-visible state singles out the election. `fallback_reason` justified.

One write per state-form edge (who can bring the waited-on state about, within this difficulty's tools + shared tools):
- 2->1: only `record_specialty_transition_supply_d4f54566` creates a specialty-channel transition fill.
- 3->2: only `record_retail_transition_supply_5b1515b2` creates a retail-channel transition fill.
- 3->4: only `submit_member_exception_request_38483004` creates a `formulary_exception_requested` row (no agent-side request tool exists in this difficulty).
- 6->5 / 8->5: a decision on a STANDARD NF request — `approve_standard_nonformulary_exception_57f550b5` (no deny or withdraw tool exists; the expedited tool is bound by policy 8 to expedited requests).
- 8->6: `approve_tier_exception_8a527f11` only.
No state-form edge has two candidate writes. PASS.

Derivation, sentence + records + depended-on rule -> resolving action (single reading):
- 2->1: the retail rule waits on "a specialty transition supply" for each NF drug whose specialty shipments ran on the transition start date; the records show which drugs (latest `specialty_fill_shipped` ship_date + days_supply ≥ transition_start_date, drug NF on the assigned formulary); the only rule describing the dispensing of a "specialty transition supply" is policy 1 ("A specialty transition supply is the temporary supply of a non-formulary specialty drug that the specialty pharmacy dispenses…") -> record that supply first.
- 3->2: same shape with retail fills and policy 2 ("A retail transition supply is …").
- 3->4: the HD rule waits on "an exception request for the drug received on or after the transition start date"; the only rule that sets up a request in this charter is policy 4 ("When a member opens an exception request on their own behalf…"), whose write is the member's own -> hand the request to the member.
- 6->5: the tier rule waits on a decision for every NF request that fell due earlier; policy 5 ("When a standard non-formulary exception request is approved…") decides such a request -> approve it first (whether approval or denial is the decision is fixed by base `formulary_nonformulary_exception`).
- 8->7: the expedited rule waits on the member's election about every earlier denial of the drug; policy 7 ("When a member asks for an independent external review of a denied exception…") is the action the member takes when they elect it -> ask the member; if yes, hand the review request to the member.
- 8->6, 8->5: as 6->5 with policy 6 / policy 5.

Other checks of this section: no rule carries a second wording of any dependency, a tool name or another problem's id; no depended-on rule restates the blocking sentence (mechanical check); no rule states a cross-problem order that grounds no declared edge (the sibling reads — retail reading home-delivery supplies, home delivery reading specialty supplies, tier alignment reading every approval — are value reads whose direction the declared edges already fix, not order statements); no base rule sentence is used to ground an edge. PASS (observation O7).

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (conclusion per sentence; "follows" = extended leaves the scored quantity as base sets it or narrows within base's permission).

`formulary_transition_supply` (refs of 1, 2, 3; `overwrite: []` on all three):
1. "When transition_fill_allowed is true, a member who is new … may receive a temporary supply of an NF drug they were already taking." — follows (3 adds a channel precondition, a strengthening of a "may").
2. "The transition start date is …; it is recorded on the assignment as transition_start_date." — follows (`F('transition_start_date')`).
3. "A transition fill is allowed only on a date of service no later than transition_window_days …" — follows (not touched).
4. "Each fill is limited to transition_fill_days_supply days supply and to transition_fills_per_drug fills …; the fill is charged at nf_transition_tier." — follows: every extended result is `MN(P('transition_fill_days_supply'), …)`, i.e. within the base maximum ("limited to"), not a different maximum.
5. "Drugs coded EX never receive a transition fill, and a drug that is covered … does not need one." — follows.
6. "A transition notice … within transition_notice_business_days" — not touched.
7. "A transition fill may be allowed only while the formulary assignment is active." — follows.
No undeclared override.

`formulary_nonformulary_exception`, `formulary_tier_exception` (refs of 4, 5, 6, 8): no extended policy changes eligibility, approval grounds, denial reasons, approved tier or the one-open-request limit. Policy 4 sets the priority of a member-opened request; base never sets a member's priority (base `formulary_evt_exception_timeline` only says a prescriber's expedited attestation upgrades a request), so no sentence is displaced. Follows.

`formulary_evt_exception_duration` (refs of 5, 6, 8):
1. "A standard approval is effective on the decision date and runs for exception_approval_months calendar months, its expiration date being …" — superseded for standard NF approvals by 5 and for tier approvals by 6; both declared in `overwrite` with the clause named and the day-before/month-end convention carried into `replaced_by`. Merged semantics unique for every standard approval (every exception is NF or tier).
2. "…an expedited approval runs expedited_exception_duration_days calendar days with the decision date as day 1." — superseded by 8, declared. The rule text of 6 ("When a tier exception request is approved…") also reaches an expedited tier approval without declaring this clause — observation O3 (no world exercises it).
3. "An approval covers only the drug and strength requested unless …" — follows.
4. "A renewal is a new request; …effective date is the day after the current expiration date." — follows (no world is a renewal).
5. "Cost share … counts toward the out-of-pocket maximum …" — follows.
6. "Approved exceptions survive a formulary reassignment only through the end of the plan year …" — not touched; note that 5's tier-1 starting period ("ends with the next plan year") does not conflict, since 5 governs length at decision and this sentence governs survival after a reassignment.

`formulary_evt_exception_timeline` (refs of 5, 6, 8): statement-before-approval, decide-once, clock start and decision hours are followed; 5/6/8 read the decision hours to measure lateness, they do not change the due time. Follows.

`formulary_external_exception_review` (refs of 5, 6, 7, 8): eligibility (latest decision a denial), reviewer hours and overturn effect follow; 7 sets only the requested priority. Follows.

No anonymous intermediate factor, 0/1 multiplier or dropped branch found: the specialty `cycles` tier "switch-with-waiver" lowers the dose cycles inside the base maximum (no base sentence fixes the number of cycles); no extended compute multiplies an existence test onto a base-fixed amount; no base branch (new enrollment vs formulary change; standard vs expedited) is unreachable from an extended selector. No author note calls a base output wrong.

Result: no undeclared override. Charter-level observation O3 only.

### factor_ladders

Per policy (P = parameter, M = method; MS = multi-source: every tier beyond the fall-through combines ≥2 conditions over distinct records; X = cross_difficulty category; fall-through = baseline checked for each):

1 specialty (6 factors; declared 5P/1M):
- biosimilar_switch_cycles P, MS (formulary param + specialty program pairing + specialty waiver), X specialty; tiers 1 / 2 / qty — distinct.
- specialty_cold_chain_allowance P, MS (program cold-chain list + fill delivery_location), X specialty; 2 / 1 / 0.
- biosimilar_review_allowance P, MS (review PA list + authorization history), X review; std/24 / urgent/24 / 0.
- delivery_failure_buffer P, single-source tiers, X specialty; 2 / 1 / 0.
- specialty_scheduling_allowance P, MS (fill dispensing pharmacy + program lead), X specialty; lead / 1 / 0.
- specialty_onhand_deduction M (home: elapsed-day deduction; office: whole-cycle floor; else none — genuinely different algorithms on the same record), X none.
Honest counts: 5P / 1M. PASS.

2 retail (5; declared 3P/2M):
- retail_run_out_alignment M (anchor: specialty supply end / home-delivery supply end / formulary maximum), X none.
- retail_onhand_deduction M (days left / days left + tolerance formula / none), MS (fill dates + network threshold), X retail.
- outside_supply_deduction P, X retail; single-source tiers.
- late_notice_extension P, MS on tier 2 (notice dates + formulary notice period); tier 1 single-source.
- home_delivery_bridge P, MS (retail maintenance choice + network list [+ program]), X retail (value from mail).
Honest counts: 3P / 2M. PASS (tier-1 realism of late_notice_extension for new enrollees: observation O10).

3 home delivery (5; declared 3P/2M):
- home_delivery_cycle_alignment M (anchor + whole-cycle rounding), X none.
- pending_request_extension P, MS (request/decision counts + latest priority), X none.
- home_delivery_onhand_deduction M (whole cycles / all days / none), X mail.
- home_delivery_shipping_allowance P, X mail.
- prescription_processing_allowance P, MS (prescription date/strength vs order), X mail.
Honest counts: 3P / 2M. PASS.

4 member request priority (4; declared 3P/1M):
- member_statement_wait P, declared MS; X mail. Tier 1 = "no supporting statement for the drug received within the statement lookback AND the formulary lets members open requests themselves". The second conjunct holds of every customer who reaches this write: base `formulary_evt_exception_timeline` — "A request may be opened by the prescriber, by the member when member_initiated_request_allowed is true…" — so a member's own request (the only subject of this policy) exists only where it is true; and all six variants set `member_initiated_request_allowed: true`. The conjunct restates the policy's scope and divides no customers. **Finding D-F3 (SOURCE-FACTOR RED, unreal ladder condition).** With it struck, tier 1 is single-source and the factor is not multi-source.
- member_delivery_wait declared **M**: tier 1 "convert the program's standard shipping business days to calendar days" (value 9 on Home Delivery Standard), tier 2 "count the fixed retail pickup wait" (K = 1), tier 3 none (0); each tier contributes one number to the fixed sum `total_wait = decision_days + wait_days + delivery_days + review_wait`. The tiers substitute a different number into the same formula; the conversion inside tier 1 is how that tier's number is obtained, not an alternative algorithm the tier selects for the same quantity (tier 2 has no business-day quantity to convert). The charter's own `home_delivery_shipping_allowance` (policy 3: "the standard shipping time of the member's home delivery program in business days" / fixed standard-shipping allowance / 0) has the same shape and is labelled parameter. **Finding D-F1 (SOURCE-FACTOR RED, mislabelled effect).**
- member_review_wait P, MS (review PA list + authorization dates), X review.
- maintenance_safety_reserve P, MS (retail maintenance list + latest-fill channel), X retail.
Honest counts after D-F1: 4P / **0M** — below the floor of 1 method factor per computation. Total 4 factors (in bounds).

5 standard NF approval months (6; declared 5P/1M):
- plan_year_starting_period M (anchor to plan-year end vs flat standard length; tiers 1 and 2 share the "remaining months + constant" shape with different constants 12 / 6 but yield different values, so they are not one tier written twice), X plan.
- first_approval_shortening P, MS (approval history + review PA list), X review.
- recent_denial_shortening P, X none.
- alternative_trial_credit P, X retail (drug-specific condition, O2).
- quantity_limit_review_shortening P, MS (QL list + PA list), X review.
- late_nf_decision_credit P, X none.
Honest counts 5P / 1M. PASS.

6 tier approval months (5; declared 4P/1M):
- renewal_alignment_period M (end with an in-force approval vs + renewal cycle vs flat), MS (approval rows + dates), X none.
- home_delivery_stable_use_credit P, X mail.
- preferred_alternative_trial_credit P, X retail (drug-specific, O2).
- clinical_ground_credit P, X none.
- late_tier_decision_credit P, X none.
Honest counts 4P / 1M. PASS.

7 external review priority (4; declared 3P/1M):
- review_delivery_failure_reserve P, X specialty.
- review_prior_authorization_wait P, MS (PA list + authorization dates), X review.
- review_dispensing_wait declared **M**: tier 1 "count the program's delivery scheduling lead business days as days" (the CPARAM `delivery_scheduling_lead_business_days`, 2 on Care Management), tier 2 "count the fixed retail pickup wait" (K = 1), tier 3 none (0); each contributes one number to the fixed sum `review_total = review_days + pa_wait + dispense_wait + effect_wait`. Tier 1 does not even convert a unit: it takes the program parameter as days. The same charter labels the identical shape `specialty_scheduling_allowance` (policy 1: "that scheduling lead (counted as days) is added" / short-lead allowance / 0) a **parameter**. **Finding D-F2 (SOURCE-FACTOR RED, mislabelled effect).**
- review_effectuation_wait P, MS on tier 1 (appeal external flag + hours), X appeal.
Honest counts after D-F2: 3P / **0M** — below the floor of 1 method factor per computation.

8 expedited approval days (6; declared 5P/1M):
- pending_review_bridge P, MS (request/decision counts + priority), X none.
- exigency_onhand_supply M (add days left / add whole weeks / nothing), X specialty.
- late_expedited_decision_allowance P, X none.
- appeal_route_allowance P, MS (appeal external flag + concurrency flag), X appeal.
- established_therapy_credit P, X specialty.
- continuation_credit P, MS (approval history + expiry dates), X none.
Honest counts 5P / 1M. PASS.

Ladder shape over all 41 factors: every ladder has three pairwise-disjoint tiers including the fall-through; no two tiers of one ladder select the same value or method; every factor's fall-through equals its `baseline` binding; every `decides` is an input, never `result`; binding sets are disjoint within each policy; every tier is stated in the rule with its condition and value/method. Every tier's value/method is a treatment drawn from the charter's own params, K-keys or another category's parameters.

Per-task aggregates (charter view; each task file confirms on its world): component {1,2,3,4} carries ≥1 multi-source factor (e.g. specialty_cold_chain_allowance) and ≥1 cross-difficulty factor (specialty, review, retail, mail); component {5,6,7,8} likewise (first_approval_shortening MS; plan, review, retail, mail, specialty, appeal). Cross-difficulty categories read: plan, retail, mail, specialty, review, appeal.

### findings

Charter-global findings (the consequence on each world is demonstrated in the task file named):

- **D-F1 — SOURCE-FACTOR RED (mislabelled effect; method floor not met).** Symptom: `formulary_ext_member_request_priority.factors[member_delivery_wait].effect: method`, but its three tiers only select the number added to `total_wait` (9 / 1 / 0 on the seeded programs). Root cause: an allowance selection labelled as a method; the only method factor of the computation is therefore not a method factor. Evidence: compute `delivery_days: "(ship_bd + 2 * int(ship_bd / 5)) if last_by_mail else (K('retail_pickup_days') if last_at_retail else 0)"`, `total_wait: "decision_days + wait_days + delivery_days + review_wait"`; same-shape `home_delivery_shipping_allowance` labelled `parameter`. Consequence: honest method count of this computation = 0 < 1. Affected: `formulary.extended.yaml` policy `formulary_ext_member_request_priority`, `factors[1]`. Bears on task 0.
- **D-F2 — SOURCE-FACTOR RED (mislabelled effect; method floor not met).** Symptom: `formulary_ext_external_review_priority.factors[review_dispensing_wait].effect: method`, tiers select `rv_lead` / `K('retail_pickup_review_days')` / 0 into the fixed sum `review_total`. Evidence: compute `dispense_wait: "rv_lead if rv_pharm == 'northbridge_specialty_pharmacy' else (K('retail_pickup_review_days') if rv_pharm == 'retail_pharmacy' else 0)"`; same-shape `specialty_scheduling_allowance` labelled `parameter`. Consequence: honest method count of this computation = 0 < 1. Affected: policy `formulary_ext_external_review_priority`, `factors[2]`. Bears on task 1.
- **D-F3 — SOURCE-FACTOR RED (unreal ladder: a conjunct that holds of every customer reaching the write).** Symptom: `member_statement_wait` tier 1 conjunct "the formulary lets members open requests themselves". Evidence: base rule sentence quoted above; `member_initiated_request_allowed: true` in all six variants (lines 101, 156, 211, 266, 321, 376). Consequence: the conjunct divides no customer; tier 1 is single-source, so the factor's declared multi-source status does not hold. Affected: policy `formulary_ext_member_request_priority`, rule sentence "A statement wait is added…", `factors[0].ladder[0]`, compute `wait_days`. Bears on task 0.

Observations (no consequence demonstrable on either world; not grounds for rework under this skill):
- O1: compute binds literal drug names (`'Humira'`, `'Xarelto'`, `'Mounjaro'`, `'Ubrelvy'`, `'Breztri Aerosphere'`, `'Rinvoq'`, `'adalimumab-adaz'`) where the rule says "the drug" / "the paired preferred biosimilar"; equivalent on both worlds.
- O2: two general rules carry task-world drug names as conditions — policy 5 "the acute-migraine formulary alternatives (sumatriptan and Nurtec ODT)" for every standard NF approval, policy 6 "the lower-tier alternative (Trelegy Ellipta)" for every tier approval. For any other requested drug these are conditions no PBM weighs; on the only worlds that exercise them (Ubrelvy, Breztri) they are the genuine same-class alternatives.
- O3: an expedited tier approval falls under both policy 6's rule (months) and policy 8's rule (days); policy 6's `overwrite` names only the standard clause. No world has an expedited tier request.
- O4: retail home-delivery bridge tier 2 — rule admits `retail90_or_mail`, compute only `mandatory_after_courtesy`. Not reached.
- O5: retail/home-delivery starting length reads only the latest sibling transition fill and checks only the window start; prerequisite `condition` fields do not tie the row to the drug. Equivalent on both worlds.
- O6: biosimilar review allowance not gated on the pairing named in its opening clause.
- O7: "fell due earlier" (6->5, 8->5, 8->6) leaves its comparator implicit; the `condition` fixes it to the blocked request's due time and computes every due time with standard hours. The alternative reading ("fell due before the handling date") would make policy 6 wait on the expedited Rinvoq approval while policy 8 waits on policy 6 — a cycle with no consistent order — so it yields no second solution.
- O8: the two state_gate edges name a DB field as `gate`; policy 8 has no `eligibility` block.
- O9: policies 4 and 7 attach opposite review-hour values to "no prior authorization in force" vs "expiring within the renewal window"; different quantities, no conflict.
- O10: late_notice_extension tier 1 ("no formulary change notice on record" -> +14 days) would apply to every new-enrollment member, who is never sent a change notice; not exercised (task 0 is a formulary change with a notice).
- O11: policy 3's "not dispensed until … an exception request" is a channel precondition not in base; a strengthening of base's "may receive".

## closing_checklist

Written after both tasks' derivations were frozen (sha256 recorded 2026-10-08 07:25:19 UTC) and revealed (07:26 UTC). The difficulty does **not** close: Step 4 requires every task to PASS all four relationships, and both tasks are SOURCE-FACTOR RED.

| item | status |
|---|---|
| one audit file per task (`0.md`, `1.md`) + `_difficulty.md`; first revision, nothing superseded | done |
| every comparison section carries a PASS | **no**: 0 = SOURCE-FACTOR RED (D-F1, D-F3), 1 = SOURCE-FACTOR RED (D-F2) |
| all 8 extended policies covered; scopes disjoint (task 0 = {1,2,3,4}, task 1 = {5,6,7,8}, per `charter_scope`); task tools and GT closed; uuid8s independent | yes |
| each tree: 3 prerequisite problems, value_input edges 3 (task 0) / 2 (task 1) ≥ 2, one owner=user problem each, acyclic; difficulty-wide graph acyclic | yes |
| every computation 4-6 factors with ≥2 parameter, ≥1 method (honest labels) | **no**: member request priority (task 0) and external review priority (task 1) each have 0 honest method factors |
| per task ≥1 multi-source and ≥1 cross-difficulty factor | yes (after striking member_statement_wait's multi-source status, task 0 still has others) |
| every factor bears weight against an honest baseline; all-baseline result definite and ≠ gold | yes (41/41 factors; 8/8 computations; GT `factor_sensitivity` and `baseline_result` match the auditor's figures exactly) |
| ladders: ≥3 tiers stated in rule, distinct outcomes, real conditions | **no** for member_statement_wait tier 1 (D-F3); yes elsewhere |
| instantiation gates re-run on the final form | not applicable: no final form exists, because the artifacts are unchanged and the difficulty has not closed. The gate snapshot in the brief was all green, and per the skill it was cited, not re-run. |

Source-layer verdict for the difficulty: **not passed** (SOURCE-FACTOR RED on both tasks). Policy self-consistency, the problem trees and the unique solution PASS on both tasks.

## revision_2

### charter_global_frozen (revision 2)

- Re-audit requested by the orchestrator ("round=2"). Round-1 text above is left untouched.
- Inputs: `formulary.extended.yaml` sha256 fce6321434da5409ea3d7af43f3110f5cb86e4595458d7cfdddbf655338cf279 (**changed** from a6fa4d0b…, so every charter-global section is re-derived in full below); `task_tools.py` e91de648… (unchanged, so § action_binding_and_uuids is carried forward by reference on that hash: same eight tools, same bodies, no prerequisite checks, independent uuid8s). Masked views: task_0 2db4992d…, task_1 8e439ad0… (both re-verified). Gate snapshot after rework (brief): all green; traceability deferred. Entry conditions complete.
- Written 2026-10-08 ~08:55 UTC, before either round-2 task JSON was opened. Contamination note: the auditor read the round-1 GT of both tasks in round 1 (disclosed there). Nothing in this section uses a round-2 GT field.

Base copy: lines 1-877 still identical to `blueprint/products/formulary.yaml`. Mechanical sweep (re-run on the new file): every `compute_basis` value is verbatim in its rule; every `baseline.rule` sentence is in its rule; no snake_case token in any rule; all 7 `policy_source` strings are verbatim in the blocked rule; no depended-on rule restates a blocking sentence; every factor's bindings exist in compute and no binding belongs to two factors; `fallback_reason` only on the action-form edge 8->7.

### what changed (charter), and the status of each round-1 item

| item | round-1 finding | change found in the new charter | status |
|---|---|---|---|
| D-F1 | `member_delivery_wait` labelled method, really a parameter | factor removed; replaced by `member_wait_calendar` (method, decides `counted_wait`): tier 1 "treat the summed waits as home delivery business days and convert them to calendar days", tier 2 calendar + retail pickup, tier 3 as-is | **closed as stated** (the new factor genuinely changes how the summed wait is counted, not just a number added), but the replacement brings a new defect, **R2-F1** |
| D-F2 | `review_dispensing_wait` labelled method, really a parameter | factor removed; replaced by `review_wait_calendar` (method, decides `review_total`): tier 1 "add the program's delivery scheduling lead to the summed waits, treat the total as specialty-pharmacy business days and convert it" | **closed as stated**, replaced by new defect **R2-F2** |
| D-F3 | vacuous conjunct "the formulary lets members open requests themselves" | tier 1/2 now split on "the prescriber on the member's latest home delivery prescription has / has not had a coverage review case for the drug within the prescriber-case lookback" (review_cases); `member_initiated_request_allowed` no longer read | **closed** (the new conjunct divides members and is weighed in practice: an engaged prescriber already has the clinical file with the plan) |
| O1 | literal drug names in compute | unchanged | open, observation (claimed "no change") |
| O2 | drug-specific conditions in general rules | rules now say "the formulary alternatives in the drug's therapeutic class (for an acute-migraine drug, sumatriptan and Nurtec ODT)" / "the lower-tier formulary alternative in the drug's class (for a triple-therapy inhaler, Trelegy Ellipta)"; compute still binds those literals (that part is O1) | **closed** at rule level |
| O3 | expedited tier approval claimed by two rules | tier rule now opens "When a tier exception request decided on the standard timeframe is approved" | **closed** |
| O4 | bridge tier 2 rule broader than compute | rule names both programs; compute tests `mandatory_after_courtesy` or `retail90_or_mail` | **closed** |
| O5 | sibling-fill reads; conditions not tied to the drug | both `condition` fields now say "for every non-formulary drug a row for that drug"; compute still reads only the LATEST sibling fill per channel and checks only the window start | **partly closed** (condition fields fixed; compute unchanged; equivalent on both worlds; observation) |
| O6 | biosimilar review allowance not gated on pairing | rule tiers and compute now require `paired` | **closed** |
| O7 | implicit comparator of "fell due earlier" | sentences now say "earlier than the tier exception request" / "earlier than the expedited request", plus a definition sentence in each blocked rule ("For this ordering a request falls due at its latest supporting statement plus the formulary's decision hours for the request's priority"; "For the expedited queue …"); `condition` fields now use "the decision hours of its own priority" | **closed**. The definition sentences define a term of the prerequisite sentence; they name no tool, id or other problem and restate no dependency, so they are not a second wording |
| O8 | state_gate `gate` names a field | unchanged | open, observation (claimed "no change") |
| O9 | opposite PA-hour conventions in 4 and 7 | unchanged | open, observation (claimed "no change") |
| O10 | missing-notice tier hits new enrollees | tier 1 now requires a sponsor formulary change (`F('formulary_change_date') != ''`), rule and ladder likewise | **closed** |
| O11 | HD channel precondition | unchanged | open, observation (claimed "no change") |

Other charter changes found: policy 3 params `pending_expedited_extension_days` 7 -> 3, `pending_standard_extension_days` 14 -> 7. Policy 4 adds params `engaged_prescriber_wait_days` 5 and `prescriber_case_lookback_months` 12 (in place of `statement_confirmation_days`), and reads `review_cases`. Policies 4 and 7: the final comparison sentences are rewritten around the counted wait.

### policy_conflict_scan / override_declarations (revision 2)

Re-derived over all eight policies. Everything concluded in round 1 holds (O3 is now closed), except the two new calendar sentences:

- Policy 4, rule: "The days of the wait are counted by the calendar of the channel that will dispense the drug: when the member's latest fill of the drug was a home delivery order, the decision, statement and review waits are business days of the home delivery pharmacy, so their sum is converted to calendar days by adding two days for every full five business days; …"
- Policy 7, rule: "…when the latest shipped fill was dispensed by Northbridge Specialty Pharmacy, the review, prior-authorization and effectuation waits together with the specialty program's delivery scheduling lead are business days of the specialty pharmacy, so their sum is converted to calendar days …"

The waits these sentences re-unit are defined elsewhere in the same charter in clock hours or calendar days, and nothing in either policy declares an override:
- `exception_standard_decision_hours`: "hours from the start of the decision clock within which a standard exception request must be decided". Base `formulary_evt_exception_timeline`: "the decision is due within exception_standard_decision_hours for a standard request".
- `prescriber_statement_wait_days`: "calendar days after a request is received …". Base: "When no statement has arrived by the end of prescriber_statement_wait_days calendar days after the request was received …".
- `external_exception_review_standard_hours`: "hours from receipt within which the independent reviewer decides a standard external exception review". Base `formulary_external_exception_review`: "The reviewer decides within external_exception_review_standard_hours … from receipt."
- Review package `standard_decision_hours` / `urgent_decision_hours`: "hours from receipt of the case within which a standard/urgent review is decided".
- Appeal `overturn_external_effectuation_hours`: "hours after an external overturn within which coverage is put in effect".

On the same facts — a mail-order member's standard exception request, or an external review whose drug the specialty pharmacy dispenses — the base text says the decision falls 72 clock hours (3 calendar days) after the clock starts and the reviewer decides within 72 hours of receipt. The extended sentence says those same waits are business days of a pharmacy, so they run longer in calendar time (e.g. a 9-business-day sum becomes 11 calendar days). Policy 4 cites only `formulary_nonformulary_exception` and `formulary_tier_exception` in `base_policy_refs`; policy 7 cites `formulary_external_exception_review`. Both carry `overwrite: []`. **Finding R2-F1/R2-F2, SOURCE-POLICY half (undeclared re-definition of base-defined waits)**; the consequence on each world is demonstrated in the task files.

### rule_compute_equivalence (revision 2)

Re-swept. Equivalent, with these observations:
- O1 still applies.
- O5 still applies to the compute side.
- New, R2-O1: policy 4's engaged-prescriber test reads only the LATEST opened Mounjaro review case (`case_npi`, `case_at`), while the rule says "that prescriber has had a coverage review case for the drug opened for the member within the prescriber-case lookback" (any such case). This is equivalent on task 0's world, where only one Mounjaro case exists.
- Policy 7 compute adds `rv_lead` only on tier 1, matching its rule.

### prerequisite_graph / prerequisite_sentences (revision 2)

Same seven edges, same kinds/forms/resolved_by, acyclic, all sentences verbatim. The four-point test is re-run on the reworded sentences:
- 6->5: "…that fell due earlier than the tier exception request carries a decision on record"
- 8->6: "…whose decision fell due earlier than the expedited request carries a decision on record"
- 8->5: same wording as 8->6, for standard NF requests

Each sentence has an explicit comparator, uses "only after" / "not … until", names a record-visible state, and its strength matches its condition ("decision hours of its own priority"). One write per state-form edge is unchanged. The fallback test for 8->7 is unchanged and justified. O7 is closed; O8 is open.

### factor_ladders (revision 2)

Unchanged policies keep their round-1 structure: 1 (5P/1M), 2 (3P/2M), 3 (3P/2M), 5 (5P/1M), 6 (4P/1M), 8 (5P/1M). Policies 1 and 2 changed ladder text (O6, O10) without changing counts.

Policy 4 (4 factors, declared 3P/1M):
- member_statement_wait P, multi-source (exception statements + review cases + mail prescriber), X review. D-F3 closed.
- member_review_wait P, multi-source, X review.
- member_wait_calendar M, X mail.
- maintenance_safety_reserve P, multi-source, X retail.

Policy 7 (4 factors, declared 3P/1M):
- review_delivery_failure_reserve P, X specialty.
- review_prior_authorization_wait P, multi-source, X review.
- review_wait_calendar M, X specialty.
- review_effectuation_wait P, X appeal.

The method labels are now honest: tier 1 transforms the summed wait (a non-linear business-to-calendar conversion of the sum), and is not a number added to an otherwise fixed formula. **But tier 1 of each new method factor selects a treatment no PBM publishes, under a condition no PBM weighs for that quantity.** The reviewer's decision clock, the independent reviewer's clock and the appeal program's effectuation clock are run by the plan, the IRO and the appeal program, not by the dispensing pharmacy. They are defined in this charter in clock hours and calendar days, and no PBM switches them to "business days of the home delivery pharmacy / specialty pharmacy" according to which pharmacy filled the member's last prescription. The unrealistic part is that the condition (latest-fill channel) is used to choose the unit of someone else's clock. Converting the specialty pharmacy's own scheduling lead, already a business-day quantity, would be ordinary. **Finding R2-F1 (policy 4) / R2-F2 (policy 7), SOURCE-FACTOR half (unreal ladder tier).**

Counting only factors that pass the tests (the skill: "a rule the tests strike out is not a factor either"), each of policies 4 and 7 has 0 honest method factors again. That is below the floor of 1, the same count that failed in round 1.

### findings (revision 2)

- **R2-F1 — SOURCE-FACTOR RED + SOURCE-POLICY RED (policy 4, bears on task 0).**
  - Symptom: `member_wait_calendar` tier 1 treats the formulary decision hours, the statement wait and the review package's decision hours as "business days of the home delivery pharmacy" and converts their sum.
  - Root cause: the units of other parties' clocks, defined in hours / calendar days by this charter and its base text, are re-defined by the member's latest-fill channel, with no overwrite.
  - Evidence: quoted above.
  - Consequence: demonstrated in `0.md` § revision_2.
  - Affected: `formulary_ext_member_request_priority` (rule sentence "The days of the wait are counted by the calendar of the channel…", `factors[member_wait_calendar]`, compute `counted_wait`).
- **R2-F2 — SOURCE-FACTOR RED + SOURCE-POLICY RED (policy 7, bears on task 1).**
  - Same shape: `review_wait_calendar` tier 1 treats the independent reviewer's standard hours, the review package's decision hours and the appeal program's effectuation hours as specialty-pharmacy business days.
  - Affected: `formulary_ext_external_review_priority` (rule sentence "The days of the review wait are counted by the calendar of the pharmacy that dispenses the drug…", `factors[review_wait_calendar]`, compute `review_total`).
  - Consequence: demonstrated in `1.md` § revision_2.
- Observations open: O1, O5 (compute side), O8, O9, O11, R2-O1.

### closing_checklist (revision 2)

Written after both revision-2 derivations were frozen (08:53:11 UTC) and revealed (08:54 UTC).

| item | status |
|---|---|
| audit files per task + `_difficulty.md`; revision_2 appended, round-1 text untouched | done |
| every comparison carries a PASS | **no**: task 0 SOURCE-POLICY + SOURCE-FACTOR RED (R2-F1); task 1 SOURCE-POLICY + SOURCE-FACTOR RED (R2-F2) |
| coverage, disjoint scopes, closed tools/GT, independent uuid8s | yes (unchanged tools; scopes as round 1) |
| trees: 3 prerequisites each, value_input 3 / 2, one user write each, acyclic; difficulty graph acyclic | yes |
| 4-6 factors, ≥2 parameter, ≥1 method with honest and real tiers | **no** for policies 4 and 7: their only method factors (member_wait_calendar, review_wait_calendar) carry an unreal tier 1 |
| ≥1 multi-source and ≥1 cross-difficulty per task | yes |
| every factor bears weight; all-baseline ≠ gold | yes (41/41; GT figures match the auditor's exactly) |
| instantiation gates on the final form | not applicable; the brief's post-rework snapshot is all green and is cited, not re-run |

Round-1 REDs: D-F1, D-F2 and D-F3 are closed as stated. D-F1 and D-F2 are each replaced by a new RED at the same factor (R2-F1, R2-F2), so the round-1 consequence — no valid method factor in the member-request and external-review computations — persists. No regression elsewhere. The difficulty does **not** pass the source-layer audit in revision 2.

## revision_3

### charter_global_frozen (revision 3)

- Re-audit "round=3". Revision-1 and revision-2 text above is untouched.
- Inputs:
  - `formulary.extended.yaml` sha256 ec70e0983328fb59de0bfb47091cecf219021515745cb5e96e283c67ee289673 (**changed**; charter-global sections re-derived below).
  - `task_tools.py` e91de648… (unchanged; § action_binding_and_uuids carried forward on that hash).
  - views: task_0 2db4992d… (unchanged since revision 2); task_1 11c8bd58… (changed).
  - Gate snapshot (brief): all green, traceability deferred.
- Written before either round-3 task JSON was opened. Contamination note: the round-1 and round-2 GT of both tasks were seen in earlier rounds (disclosed there).
- Scope of the change:
  - Base lines 1-877 still verbatim.
  - Only policies 4 (`formulary_ext_member_request_priority`, +3 lines) and 7 (`formulary_ext_external_review_priority`, +8 lines) changed length. The other six keep their revision-2 line spans; their structure re-checks clean and their values reproduce revision 2 exactly on both worlds.
  - Mechanical sweep, all eight policies, 0 issues: compute_basis verbatim; baseline sentences in the rule; every compute binding has a basis; no snake tokens; prerequisite sentences verbatim and not restated; factor bindings disjoint and existing.
  - Factor counts: 6 (5P/1M), 5 (3P/2M), 5 (3P/2M), 4 (3P/1M), 6 (5P/1M), 5 (4P/1M), 4 (3P/1M), 6 (5P/1M). Every ladder has 3 tiers.

### status of the revision-2 items

| item | change found | status |
|---|---|---|
| R2-F1 (policy 4, calendar re-unit of the decision/statement/review waits) | Rule now: "every wait above is a number of calendar days counted from the handling date, as the formulary, the review package and the prescriber statement define them, and their sum fixes the ready day; when the member's latest fill of the drug was a home delivery order, a ready day that falls on a Saturday or a Sunday is moved to the following Monday, because the home delivery pharmacy ships only Monday through Friday; when the latest fill was at a retail pharmacy, a ready day that falls on a Sunday is moved to the following Monday, because network pharmacies dispense Monday through Saturday; in every other case the ready day is taken as it falls". Compute: weekday of NOW + int(sum) (anchor 2026-01-05, a Monday), +2 for a Saturday / +1 for a Sunday ready day on mail, +1 for a Sunday on retail. | **closed.** The base clocks keep their defined units (hours/24 -> calendar days). The channel only decides which weekdays a ready day may fall on, which is the dispensing pharmacy's own fact, so there is no undeclared re-definition. The tiers change how the ready day is placed (a weekday roll convention), so the method label is honest; the three tiers are distinct; the treatment (a mail pharmacy that does not ship at weekends, a retail pharmacy closed on Sundays) is ordinary industry practice; no sibling charter contradicts it (mail and specialty count their own leads in business days). |
| R2-F2 (policy 7, same for the reviewer's/review package's/appeal clocks) | Rule now: "every wait above is a number of calendar days … as the independent reviewer's, the review package's and the appeal program's hours define them …; when the latest shipped fill was dispensed by Northbridge Specialty Pharmacy, which ships only Monday through Friday, a ready day that falls on a Saturday or a Sunday is moved to the following Monday and the specialty program's delivery scheduling lead, which is counted in business days, is then counted forward from that day over Mondays through Fridays only; …retail: Sunday -> Monday and the retail pickup wait is added". Compute: `review_base + rv_roll + rv_lead + 2·int((rv_start_weekday + rv_lead)/5)`. | **closed.** The external reviewer's hours stay calendar time, and only the specialty pharmacy's own lead is counted in business days — consistent with the specialty charter ("the fill is scheduled with the member at least delivery_scheduling_lead_business_days business days before delivery"). The business-day formula is correct for any weekday start Monday-Friday (checked: Tue + 2 business days = Thu, 2 calendar days; Fri + 2 = Tue, 4). The method label is honest and the tiers are distinct and real. |
| R2-O1 (engaged test reads only the latest case) | Rule and ladder now say "the latest coverage review case for the drug opened for the member was / was not opened by the prescriber on the member's latest home delivery prescription … within the prescriber-case lookback" | **closed** (rule = compute) |
| O1, O5 (compute side), O8, O9, O11 | unchanged | open, observations |

New observation R3-O1: both ready-day computations place the ready day at `NOW + int(sum of waits)`, truncating a fractional sum. The rules say the waits are "a number of calendar days" without stating how a fractional sum (for example a 36-hour clock = 1.5 days) is placed. Every wait on both worlds is a whole number of days, so this has no consequence here.

### conflict scan / overrides / prerequisite graph / sentences / factor ladders (revision 3)

- Re-derived: every revision-2 conclusion stands, with R2-F1 and R2-F2 removed.
- No new conflict: policies 4 and 7 now take the base clocks in their defined units.
- The prerequisite graph and all seven sentences are unchanged and pass.
- Factor ladders: policies 4 and 7 each have one honest, real method factor again (`member_wait_calendar`, `review_wait_calendar`). D-F3's replacement condition (latest review case by the current prescriber) stands.

### findings (revision 3)

- No RED at charter level.
- Observations: O1, O5 (compute side), O8, O9, O11, R3-O1.

### closing_checklist (revision 3)

Written after both revision-3 derivations were frozen (10:08:14 UTC) and revealed.

| item | status |
|---|---|
| one file per task + `_difficulty.md`; revisions 1-3 preserved; every revision-3 comparison carries a PASS | yes (task 0 PASS ×4, task 1 PASS ×4) |
| all 8 extended policies covered; task scopes pairwise disjoint ({1,2,3,4} / {5,6,7,8}, per `charter_scope`); task tools and GT closed; uuid8s independent and frozen | yes |
| trees: 3 prerequisite problems each; value_input edges 3 and 2 (≥ 2); one owner=user problem each; no cycle; the difficulty-wide graph is acyclic | yes |
| every computation 4-6 factors, ≥2 parameter, ≥1 honest and real method; ≥1 multi-source and ≥1 cross-difficulty per task; ladders of 3 tiers stated in the rule, distinct, real | yes |
| every factor bears weight on its world against an honest baseline; all-baseline result definite and ≠ gold | yes (41/41 factors, 8/8 computations; GT figures equal the auditor's) |
| instantiation gates on the final form | the orchestrator's post-rework snapshot (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK, traceability deferred to the render stage) is cited, not re-run, per the skill |

Round-2 REDs: R2-F1 and R2-F2 are closed. Round-1 REDs D-F1/D-F2/D-F3 remain closed. No new RED, no regression. Open observations (not grounds for rework): O1, O5 (compute side), O8, O9, O11, R3-O1.

**This difficulty passes the source-layer policy-task audit in revision 3.**

## revision_4

### scope and carry-forward (revision 4)

- Re-audit "round=4", triggered by the whole-scenario validator ("forbidden 'from datetime' (real clock)"). There were no round-3 REDs. Revisions 1-3 are untouched.
- Inputs (verified 2026-10-08 12:21 UTC):
  - `formulary.extended.yaml` ec70e098… — **unchanged** since revision 3.
  - views task_0 2db4992d… and task_1 11c8bd58… — **unchanged**.
  - `task_tools.py` f5ed59673e5fc78d88bfe4b1550919db2bb7c0c2d93d132ad8262de22fcba288 — **changed** (was e91de648…).
  - Gate snapshot (brief): all green including TRACEABILITY; validate_scenario VALID.
- Carried forward by reference on the two unchanged hashes (charter ec70e098…, views): § policy_conflict_scan, § rule_compute_equivalence, § prerequisite_graph, § prerequisite_sentences, § override_declarations and § factor_ladders as concluded in revision 3. None of them reads the tool module.
- Re-derived, because the tool module changed: § action_binding_and_uuids, plus the per-task conclusions that rest on the runnable tool effects ("tools do not judge prerequisites"; the rows the gold writes leave, which later computations read).

### action_binding_and_uuids (revision 4)

AST of the new module:
- Sole import: `from erlbench import ToolContext, tool`. No `datetime`, no real clock.
- Same eight functions, with the same names, uuid8s, `@tool(owner=…, rw="write")` decorators and parameter lists as in revision 1. The orchestrator's AST comparison also reports identical docstrings.
- Every body is straight-line: no `if`/`raise`/`assert`/`try` statement in any tool, so no tool refuses, errors or hints on a missing prerequisite.

The only change is inside the three approval tools: function-local `datetime` arithmetic is replaced with proleptic-Gregorian ordinal-day helpers (`_ordinal`, days from 0000-03-01; `_civil`, its inverse).
- Standard NF and tier tools: the expiration is the day before the same day-of-month `approval_months` later, clamped to that month's last day: `month_len` = ordinal(1st of the next month) − ordinal(1st of the month); expiration = civil(ordinal(y2, m2, min(d, month_len)) − 1).
- Expedited tool: expiration = civil(ordinal(today) + days − 1).

Equivalence test (auditor's temp harness, a fake `ToolContext`, deleted afterwards):
- Every start date from 2024-01-01 through 2029-12-31, including the 2024 and 2028 leap days and every month-end.
- Months {1,2,3,6,7,11,12,13,16,18,24} for both month tools; days {1,2,7,28,30,31,52,54,60,90,365,366} for the expedited tool.
- Compared against the round-3 `datetime` semantics: **74,528 cases, 0 mismatches.**

Rows written are unchanged in every field the charter or the computations read:
- The month tools write `formulary_exception_approved`, exception_type fixed per tool, review_priority standard, decision_reason criteria_met, effective = today.
- The expedited tool writes the given exception_type and review_priority expedited.
- The three transition tools write a `formulary_transition_fills` row with fill_date = today and their fixed channel.
- The two user tools write `formulary_exception_requested` / `formulary_external_review_requested` with the given priority and event_at = now.

All checks pass. uuid8s are unchanged (independent, frozen).

### closing_checklist (revision 4)

| item | status |
|---|---|
| revision-4 conclusions per task (`0.md`, `1.md`) carry a PASS | yes |
| coverage, disjoint scopes, closed tools/GT, independent uuid8s | yes (tool names/uuids unchanged; tool effects equivalent) |
| trees, factors, weights, baselines | carried forward from revision 3 on unchanged charter and view hashes; the scored GT is unchanged (writes and computations identical to revision 3) |
| gates on the final form | the orchestrator's post-rework snapshot (all OK incl. TRACEABILITY, validate_scenario VALID) is cited |

No round-3 RED existed. No new defect, no regression. Open observations unchanged: O1, O5 (compute side), O8, O9, O11, R3-O1. **The difficulty still passes the source-layer policy-task audit in revision 4.**
