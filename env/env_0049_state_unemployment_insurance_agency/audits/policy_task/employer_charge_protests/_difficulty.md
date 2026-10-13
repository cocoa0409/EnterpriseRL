# Policy-task audit — employer_charge_protests / charter-global

## charter_global_frozen

- Auditor: erl-task-policy-audit agent (independent of the instantiator; no instantiator transcript, worklog or prior audit of this difficulty read).
- Freeze time: 2026-10-10 ~13:27Z (written before any task's GT was revealed; nothing in this section is derived from `evaluation_criteria`, `computations`, `charter_scope`, `prerequisite_closure`, `design_rationale`, `solvability_contract` or `required_documents`).
- Frozen inputs (sha256, re-checked against the coordinator's brief before reading):
  - `tasks/employer_charge_protests/charge.extended.yaml` 58db9616a6ef62cf75d08485fed93bca785add1e49f4e9518d0f554d85983a27
  - `tasks/employer_charge_protests/task_tools.py` 811d5e08b5df06bf614eff443733c214888d9ee778e7a16158093a7e62ec1b17
  - blind views `task_0.blind.json` dee15a90…, `task_1.blind.json` 18786b48… (only `frozen_time`, `user_scenario`, `initial_state`).
- Also read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json` (charge_*, employer_* tables), `blueprint/share_tools.py` (employer and charge lookups), `blueprint/products/charge.yaml`, `blueprint/products/taxacct.yaml` (variant parameters and the penalty/interest, payments and charges-and-billing rules only, for the cross-category reads), and the DSL semantics in `~/.claude-sub/skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`, `MONTHS`, `DAYS`, `_within`).
- Masked and unread at freeze: every task file `tasks/<i>.json`, `tasks/employer_charge_protests/worklog.md`, the scenario `worklog.md`, the other difficulties' audits.
- Entry conditions (Step 0): the coordinator supplied the gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cache_diff, check_cross_fire all rc=0; check_traceability deferred to render; validate_scenario's only errors are pre-render "required document not found"), the masked views and their hashes. Hashes match on disk. Input complete.

### policy_conflict_scan

Base section of the extended file vs `blueprint/products/charge.yaml`: parsed and compared key by key (`category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies`) — all identical. The base copy is verbatim.

Extended policies (4), forming two disjoint two-node trees:

| policy | subject | target_tool (owner) | computes | prerequisite |
|---|---|---|---|---|
| charge_ext_protest_amount | charge_protest_filed | file_charge_protest_73ec7ae2 (user) | protested_amount | [] |
| charge_ext_protest_relief_credit | charge_protest_granted | grant_charge_protest_0f56e95e (agent) | relief_credit_amount | ← charge_ext_protest_amount (value_input, state) |
| charge_ext_response_disputed_amount | charge_separation_response_filed | submit_separation_response_153a3a70 (user) | disputed_charge_amount | [] |
| charge_ext_response_relief_credit | charge_relief_determined | determine_charge_relief_e2b9af19 (agent) | relief_credit_amount | ← charge_ext_response_disputed_amount (value_input, state) |

Overlap scan:
- Subjects are pairwise distinct; the two relief-credit policies compute the same quantity name on different events and different tools (protest_pending→relieved vs responded→relieved), so they never fire on the same transition. Lifecycle (`charge_protest_granted` from protest_pending; `charge_relief_determined` from responded) keeps the two trees on disjoint position states.
- Both relief-credit policies overwrite the same two base sentences (charge_evt_relief_grounds "A granted relief credits back every charge already posted within its scope"; charge_evt_credits "A relief credits the whole remaining charge of every posting within the relief's scope") with event-specific replacements ("The relief credit of a protest decision …" / "The relief credit of a determination on a separation response …"). The replacements are scoped by event, so they do not collide with each other.
- Time anchors: protest window (statement_mailed_date + 30, inclusive) and response window (notice_mailed_date + 10, inclusive) are inherited from base untouched.
- Cross-category reads: all four read `taxacct` only (employer_accounts.variant_name, employer_tax_ledger, employer_wage_reports, CPARAM late_payment_interest_rate_monthly); declared in each `cross_category` block.
- Scopes of the two tasks (inferred from the blind `user_scenario`s, to be confirmed against `charter_scope` at reveal): task 0 = {charge_ext_protest_amount, charge_ext_protest_relief_credit}; task 1 = {charge_ext_response_disputed_amount, charge_ext_response_relief_credit}. Pairwise disjoint and jointly complete over the 4 extended policies.
- Observation (scope claim): blueprint claims `charge_chargeability_determined` and `charge_protest_denied` for this difficulty, but no extended policy or task tool covers them. No relationship is affected.

### rule_compute_equivalence

charge_ext_protest_amount
- stmt_quarter ← "the named statement being the most recently mailed statement of benefit charges on the position" (LATEST by statement_mailed_date) — equivalent.
- listed_charges ← "the total of the charges that statement lists … each at its posted amount" (SUM posted, charge_quarter = stmt_quarter) — equivalent.
- starting_amount / account_class / billed_for_quarter / reserve_posted_for_quarter ← the three-tier sentence — equivalent (`'Reimbursing' in` / `'Contributory' in` the taxacct class name; billed/posted > 0).
- credits_taken_out — **not equivalent**. Rule: "Where a credit for a recovered overpayment has been posted on the position since the statement's quarter, every credit posted on the position since that quarter is taken out …; where only credits for cancelled payments have been posted since that quarter, those cancelled-payment credits are taken out; where no credit has been posted since that quarter, nothing is taken out." Compute: `recovery_credits_since = COUNT(recovery) − COUNT(recovery, charge_quarter=stmt_quarter)`, `credits_taken_out = credits_all − credits_in_quarter` — i.e. "every credit whose quarter is not the statement's quarter". (a) It excludes credits posted in the statement's quarter, which the inclusive reading of "since that quarter" includes; (b) it includes credits posted in quarters earlier than the statement's quarter, which "since" never includes; (c) tier 2 does not test "only" (an appeal/relief credit posted since that quarter alongside a cancelled-payment credit falls into the compute's tier 2, while the rule's ladder has no tier for it — the third tier is "no credit has been posted", not "otherwise"). See finding F1; (a) bites task 0.
- support_share / amended_quarters ← "number at least four / one to three / none" (XCOUNT amended, filed_date within 12 months; DSL `_within` = 0 ≤ MONTHS(filed, NOW) < 12) — equivalent.
- answer_share ← three tiers; compute uses responses_on_record and DAYS(response_due_date, response_date) unless late_good_cause — equivalent.
- interest_months ← "whole months from the due date to the payment plus one … ; when that bill is unpaid and its due date has passed, … to the protest plus one …; none otherwise" — equivalent (MONTHS is whole months, day-adjusted).
- interest_rate ← three tiers — equivalent.
- disputed_principal / protested_principal / protest_interest / result ← the build-order sentence with its three rounding points — equivalent.

charge_ext_protest_relief_credit
- relief_reach ← "Where the recorded protest ground disputes … wages or … status, every charge posted on the claim times the wage-record relief share; where … agency error or … recovered overpayment was not credited, the total of the charges posted in the quarter of the statement the protest names; any other recorded ground takes in no charge already posted" — equivalent (grounds wrong_wages / not_base_period_employer; agency_error / overpayment_recovered; protested_quarter read from the latest charge_protest submission).
- credits_deducted ← three tiers — equivalent.
- support_share — rule says the amended wage reports "cover at least four quarters / one to three quarters"; compute counts report rows (XCOUNT), not distinct quarters covered. Latent divergence (two amended reports for one quarter count twice). Observation O3; no consequence in task 0 (four rows, four distinct quarters).
- answer_abatement — equivalent; result with MX(0, …) and a single rounding point — equivalent.

charge_ext_response_disputed_amount
- counted_charges, charges_left_out, promptness_share (DAYS(notice_mailed_date, NOW) vs P('response_window_days') and 5), standing_share (XCOUNT late_report penalties, entry_date within 12 months), result — each equivalent to its sentence; no invented basis.

charge_ext_response_relief_credit
- relief_reach (with responses_on_record > 0 and the class flags P('relief_voluntary_quit_without_good_cause') etc.), relief_window, credits_netted, account_standing, response_promptness, result — each equivalent to its sentence.

No compute binding lacks a rule sentence; no rule sentence that bears on a scored quantity lacks a binding, except the (a)/(b)/(c) gap above.

### action_binding_and_uuids

- `(target_tool, computes)`: (file_charge_protest_73ec7ae2, protested_amount), (grant_charge_protest_0f56e95e, relief_credit_amount), (submit_separation_response_153a3a70, disputed_charge_amount), (determine_charge_relief_e2b9af19, relief_credit_amount) — each claimed by exactly one policy.
- Function bodies: each tool performs one create + one update and returns a receipt; none reads status, timeliness, grounds or amounts to refuse or warn. The tool layer judges no prerequisite (file_charge_protest writes protest_pending regardless of prior status; grant/determine write relieved regardless of prior status).
- Docstrings name no other task tool and carry no ordering word about other actions. "The employer can afterwards see the protest among its submissions" describes the visible effect of the same call, not a sequence (observation only). "as returned by the charge position lookup" refers to a shared read tool by description; acceptable.
- uuid8s: 73ec7ae2, 0f56e95e, 153a3a70, e2b9af19 — four distinct values, no shared prefix or suffix, no sequential pattern. Pass.
- Enum note: `protest_ground` accepts wrong_wages, but the grant tool's `relief_basis` has no wrong_wages; its docstring maps it explicitly ("not_base_period_employer means this employer paid no base-period wages or the wages charged to it are wrong"). Single reading.

### prerequisite_graph

- `prerequisite` filled on all four policies (two `[]`).
- Edges: charge_ext_protest_relief_credit → charge_ext_protest_amount; charge_ext_response_relief_credit → charge_ext_response_disputed_amount. Both `problem`s are extended ids in this file, neither is a base policy or self. Graph acyclic (two disjoint chains of length 1).
- `policy_source` verbatim in its own rule (checked by string containment): both True.
- `form: state` on both, no `fallback_reason` — consistent.
- `kind: value_input`, `gate` names: `protest_ground_recorded` (a compute binding of charge_ext_protest_relief_credit, = F('protest_ground'), which selects the relief_reach tier) and `reported_reason` (a compute binding of charge_ext_response_relief_credit, = F('separation_reason_reported'), which selects the reach tier). Both genuine value inputs.
- `resolved_by` equals the depended-on policy's target_tool on both edges; the tool effects (protest_pending + protest_date + protest_ground + charge_protest submission; responded + response_date + separation_reason_reported + separation_response submission) make the `condition` hold.
- `condition` texts contain no authoring-viewpoint phrasing ("in this task", "at the opening").
- Observation O4: edge A's `condition` requires status protest_pending; the prerequisite sentence ("carries a written protest of the statement, with the protest ground and the protest date recorded on it") does not name the status. A position with an earlier denied protest of the same statement would satisfy the sentence and not the condition. Latent; task 0's position carries no earlier protest.

### prerequisite_sentences

Edge A (charge_ext_protest_relief_credit ← charge_ext_protest_amount)
- Sentence: "The relief credit of a protest decision is fixed only after the position carries a written protest of the statement, with the protest ground and the protest date recorded on it."
- Four-point test: ordering connective "only after" joining the policy's own result (the relief credit) to a waited-on state ✓; state named in record words (charge_positions.protest_ground, protest_date; charge_requests charge_protest) with no action, performer or tool ✓; no tool name, policy id, snake_case token or row id ✓; strength: matches the condition except the status (O4).
- Exactly one write of this difficulty brings the state about: file_charge_protest_73ec7ae2 (only writer of protest_ground/protest_date/charge_protest). grant/determine/submit do not write it. ✓
- Derivation: sentence → the position must carry a written protest with ground and date → charge_ext_protest_amount's own rule ("A written protest that disputes the employer's base-period wages or its base-period status states an amount protested …") is the policy whose write lodges a protest → its write (owner user) is the resolving action. Single reading.
- The depended-on rule does not restate the sentence; no second wording elsewhere in the blocked rule.

Edge B (charge_ext_response_relief_credit ← charge_ext_response_disputed_amount)
- Sentence: "The relief credit of a determination on a separation response is not fixed until the position carries the employer's separation response, with the separation reason it reports and the date it was received recorded on it."
- Four-point test: "not … until" ✓; state form in record words (separation_reason_reported, response_date, separation_response submission) ✓; no tool/id/snake_case ✓; strength matches the condition ✓.
- One write brings it about: submit_separation_response_153a3a70 ✓.
- Derivation: sentence → the employer's separation response with reason and date must be on the position → charge_ext_response_disputed_amount's rule ("A separation response that answers a notice of claim … states a disputed charge amount …") is the policy whose write lodges it; base charge_evt_notice_and_response confirms "Only the employer or a third-party administrator holding its power of attorney may respond" → a customer-owned write. Single reading.

Undeclared cross-problem orders: none of the four extended rules states an order between problems other than its own prerequisite sentence. Base rules carry lifecycle background (notice → response → determination; statement → protest) but no task tree rests on a base sentence alone.

### override_declarations

charge_ext_protest_amount (overwrite: []) vs base_policy_refs [charge_evt_statement_and_protest, charge_evt_credits, charge_evt_notice_and_response, charge_agg_proportional_share]: the amount protested is a quantity no base sentence governs; protest window, channels, new-ground rule, credit caps, response window and proportional share are followed. No conflict.

charge_ext_protest_relief_credit (overwrites the two relief-credit sentences, named verbatim; the replacement is in the rule):
- charge_evt_relief_grounds: "Relief from charges is granted only on a ground the employer's class allows" — followed for wage/status and agency-error grounds (allowed for every class); "Relief for benefits paid in error is refused when … pattern …" — not restated but not contradicted (inherited); "Relief granted on the regular claim also covers … Extended Benefits charges" — inherited.
- charge_evt_credits: "A credit always names the single posted charge it reduces, and never exceeds charge_msr_remaining_charge" — NOT overwritten, and the replacement books the whole relief credit "against the single posted charge that still stands within the relief reach". Wherever the credit exceeds that charge's remaining amount the two sentences conflict (finding F3, latent; per-task check).
- charge_evt_notice_and_response: "A late response is treated as timely only when the employer shows good cause; otherwise payments issued before the late response stay charged even if relief is later granted." — NOT overwritten; the answer-abatement tier for a late response (0.9 × reach, the reach including charges for payments issued before the late response) handles the same quantity differently (finding F2, latent; neither task has a late response).

charge_ext_response_disputed_amount (overwrite: []): new quantity; no base sentence governs it. No conflict.

charge_ext_response_relief_credit (overwrites the two relief-credit sentences):
- charge_evt_relief_grounds part-time sentences ("Continuing part-time relief lasts only for weeks …") — the credit quantity is overwritten; eligibility followed.
- charge_evt_notice_and_response late-response bar — NOT overwritten; the promptness tier "more days … than the response window allows" credits 0.9 × the relief window, which includes payments issued before the late response (F2, latent).
- charge_evt_credits "never exceeds charge_msr_remaining_charge" — same as above (F3, latent).

### factor_ladders

| policy | factor | effect | decides | tiers (incl. fall-through) | multi-source | cross_difficulty |
|---|---|---|---|---|---|---|
| protest_amount | statement_starting_amount | method | starting_amount | 3 | yes (class ∧ bill / class ∧ reserve posting) | taxacct |
| protest_amount | credits_taken_out | method | credits_taken_out | 3 (rule gap, F1(c)) | no | — |
| protest_amount | protest_documentation_share | parameter | support_share | 3 | no | taxacct |
| protest_amount | notice_answer_share | parameter | answer_share | 3 | tier 2 (response ∧ due date ∧ no good cause) | — |
| protest_amount | interest_months | method | interest_months | 3 | yes (bill due ∧ payment date) | taxacct |
| protest_amount | protest_interest_rate | parameter | interest_rate | 3 | tier 2 (class ∧ reserve posting) | taxacct |
| protest_relief_credit | relief_reach | method | relief_reach | 3 | no (one field) | — |
| protest_relief_credit | credits_deducted | method | credits_deducted | 3 | tier 2 (cancel rows ∧ no recovery rows) | — |
| protest_relief_credit | wage_record_relief_share | parameter | support_share | 3 | no | taxacct |
| protest_relief_credit | answer_abatement | parameter | answer_abatement | 3 | tier 2 | — |
| response_disputed | response_counted_charges | method | counted_charges | 3 | yes (statements ∧ charges) | — |
| response_disputed | response_charges_left_out | method | charges_left_out | 3 | no | — |
| response_disputed | answer_promptness_share | parameter | promptness_share | 3 | date ∧ class window | — |
| response_disputed | dispute_standing_share | parameter | standing_share | 3 | no | taxacct |
| response_relief_credit | relief_reach_by_reported_separation | method | relief_reach | 3 | yes (reported reason ∧ class flag) | — |
| response_relief_credit | relief_window | method | relief_window | 3 | yes | — |
| response_relief_credit | credits_netted | method | credits_netted | 3 | no | — |
| response_relief_credit | relief_standing_share | parameter | account_standing | 3 | no | taxacct |
| response_relief_credit | relief_promptness_share | parameter | response_promptness | 3 | date ∧ class window | — |

Counts as declared: protest_amount 6 (3 method, 3 parameter); protest_relief_credit 4 (2/2); response_disputed 4 (2/2); response_relief_credit 5 (3/2). Every `decides` is an input, never `result`; binding sets are disjoint within each policy. Every tier of every ladder is stated in its rule (condition and value/method) and implemented by its `decides` binding (re-checked against the rule text above). Every factor's fall-through equals the policy's `baseline` for that input; every `baseline.rule` sentence is in the rule (string containment, all True); `baseline.params` keys are the fall-through keys. Labels: method factors change what is summed/selected or the date span; parameter factors substitute a number — honest.

Reality of the ladders (charter-global judgement; consequences per task):
- statement_starting_amount, credits_taken_out / credits_deducted / charges_left_out / credits_netted, relief_reach, relief_window, counted_charges, interest_months: conditions and outcomes are ones a UI charge unit weighs (what was billed or posted to the reserve, credits already given, which statement is in issue, separation reason vs class relief grounds, late payment of a reimbursement bill).
- **protest_interest_rate, tier 2** ("the reserve interest rate of one half of one percent per month when the employer is contributory and the quarter's charges have been posted to its reserve account"): unreal. The taxacct charter, whose records this tier reads, states "For a contributory employer they are posted against the reserve account, which lowers its reserve ratio at the next computation date but creates nothing due" and "Contributions and reimbursement bills unpaid after their due date carry interest" — reserve-posted charges carry no interest in this world, and no UI agency charges or credits interest on charges posted to an experience-rating reserve. The tier is also inert: interest_months has non-zero tiers only for a reimbursement bill, which a contributory account never receives, so 0.005 × 0 = 0 in every consistent world. Finding F4.
- **dispute_standing_share and relief_standing_share** (late report penalties on the tax account in the last twelve months → 0.75 / 0.90 / 1.00 of the disputed charges or the relief credit): the condition is not one a UI agency weighs for that quantity. Relief from benefit charges and the charges an employer disputes rest on the separation, the wages and the payments (base charge_evt_relief_grounds lists the grounds; the only compliance test the base charter knows is the pattern of failure to respond to notices, charge_msr_failed_responses); the employer's wage-report filing penalties are a tax-account matter already sanctioned by the penalty itself (taxacct_evt_penalty_interest). Finding F5.
- **answer_promptness_share and relief_promptness_share, tier 2** ("more than five days but within the response window" → 0.95): the condition is not one a UI agency weighs. Base charge_evt_notice_and_response: "A response is timely only when it is received no later than the response window after the notice of claim mailing date … a response received on the last day is timely". A timely response on day 8 is, in this charter and in every state's practice, simply timely; no agency discounts relief for answering on day 6–10 instead of day 1–5. Finding F6. (Tier 1, a late response, is a condition the business weighs.)
- protest_documentation_share / wage_record_relief_share: amended wage reports are how wrong base-period wages are corrected, so the condition is related; but the count is taken over every amended report of the tax account in the last twelve months, for any quarter and any worker, and the fall-through (zero) makes the published standard computation of an amount protested $0.00 on every world. Observation O1 (the "standard computation" of both protest policies always yields 0.00; it is definite and differs from any non-zero gold, so it is not demonstrated RED).
- notice_answer_share / answer_abatement (0.80 unanswered, 0.90 late without good cause): the condition is weighed by the business (failure-to-respond and late-response bars); the haircut values are synthetic. Observation O2.

Per-task requirement (multi-source and cross_difficulty over each task's computations): task 0's computations carry statement_starting_amount (multi-source, taxacct) — satisfied as declared; task 1's carry response_counted_charges / relief_reach_by_reported_separation (multi-source) and dispute_standing_share / relief_standing_share (taxacct) — as declared; whether they survive the reality test is decided per task.

### findings

- **F1 — SOURCE-POLICY (rule/compute and two readings of "since the statement's quarter"), bears on task 0.** Symptom: the credits taken out of a protest differ according to whether credits posted in the statement's own quarter are "posted since that quarter". Root cause: rule sentence "every credit posted on the position since that quarter is taken out of the protest" vs compute `credits_all − credits_in_quarter` (quarter ≠ statement quarter). Also (b) earlier quarters included by compute, (c) the rule's tier 2/3 leave "non-recovery, non-cancel credits since that quarter" unassigned. Evidence: charge.extended.yaml charge_ext_protest_amount rule sentence 6 and compute lines `recovery_credits_since`, `cancel_credits_since`, `credits_taken_out`. Consequence: demonstrated in 0.md (two values). Affected: charge_ext_protest_amount rule + compute.
- **F2 — SOURCE-POLICY observation (latent undeclared override).** charge_evt_notice_and_response "otherwise payments issued before the late response stay charged even if relief is later granted" is in both relief-credit policies' base_policy_refs and is not overwritten, while their late-response tiers (answer_abatement 0.90; relief_promptness 0.90) credit charges for payments issued before the late response. Not demonstrable here: neither task's world has a late response. Bears on no task.
- **F3 — SOURCE-POLICY observation (latent).** charge_evt_credits "never exceeds charge_msr_remaining_charge" is not overwritten while both relief-credit replacements book the whole credit against one charge. Per-task check shows the credit stays within that charge's remaining amount in both tasks, so no consequence.
- **F4 — SOURCE-FACTOR RED (unreal tier), bears on task 0** (protest_interest_rate is one of its factors): see factor_ladders. Demonstration: quotation of taxacct_evt_charges_and_billing "creates nothing due" against tier 2's 0.005/month on reserve-posted charges; the tier is inert in every consistent world.
- **F5 — SOURCE-FACTOR RED (condition not weighed by the business), bears on task 1** (both of its computations): dispute_standing_share and relief_standing_share.
- **F6 — SOURCE-FACTOR RED (condition not weighed by the business; contradicts base timeliness), bears on task 1** (both of its computations): tier 2 of answer_promptness_share and relief_promptness_share.
- O1–O4 observations as above; scope-claim observation (two claimed event types with no policy).

## closing_checklist

Written after both reveals (2026-10-10 13:30Z). The section above is pre-reveal and unchanged except its freeze-time stamp line, which was corrected to the real clock after the reveal.

The difficulty does **not** close: not every task passes all four relationships.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
|---|---|---|---|---|
| 0 (0.md) | SOURCE-POLICY RED (F1) | PASS | SOURCE-FACTOR RED (F4) | SOURCE-TASK RED (T0-1: 274.88 vs 0.00) |
| 1 (1.md) | PASS | PASS | SOURCE-FACTOR RED (F5, F6) | PASS |

Checklist state:
- Per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; `_difficulty.md` alongside; no earlier revision exists. Comparison sections present; not all carry PASS.
- Coverage and scope: the 4 extended policies are covered; task scopes {protest_amount, protest_relief_credit} and {response_disputed_amount, response_relief_credit} are pairwise disjoint (each spans its whole tree); task tools and GT are closed; four independent uuid8s. ✓
- Trees: each has 1 prerequisite problem, 1 value_input edge (≥ max(n−1,1) = 1), an owner=user write, no cycle; the difficulty graph is two disjoint edges, acyclic. ✓
- Factors: declared counts in bounds and every declared factor bears weight numerically on its task's world against an honest baseline, whole baselines 0.00 ≠ gold. Not met on reality: F4 (task 0, one tier), F5 and F6 (task 1, the tiers gold takes; after striking, task 1's computations fall below 4 factors / 2 parameter and lose their only cross-difficulty factors).
- Instantiation-stage gates on the final form: not re-run by this audit (no final form exists while REDs stand; artifact hashes are unchanged from the coordinator's snapshot: charge.extended.yaml 58db9616…, task_tools.py 811d5e08…).

## revision_2

### charter_global_frozen (revision 2)

- Auditor: erl-task-policy-audit agent (same auditor as round 1; independent of the instantiator and the reworker). Freeze: 2026-10-10 18:21Z, written before any round-2 task file (tasks/0.json, tasks/1.json) was opened. Nothing below rests on revised GT.
- Inputs re-hashed on disk and matching the coordinator's brief: charge.extended.yaml 48398cf0a1f0f80431d61eccef2f8a72121408344de6d8c19bce6d0dc7449a4b (**changed** from 58db9616… → every charter-global section re-derived below); task_tools.py 811d5e08b5df06bf614eff443733c214888d9ee778e7a16158093a7e62ec1b17 (unchanged → the round-1 action_binding_and_uuids conclusion is carried forward on that hash, plus a re-check that no target_tool changed); blind views task_0 dee15a90… (unchanged), task_1 1729841f… (persona changed; initial_state identical to round 1 row by row as recorded in 1.md).
- Masked and unread at freeze: tasks/0.json (ee822228…), tasks/1.json (e28fddcd…), both worklogs, the reworker's notes. The reworker's claims were received as item ids only and are treated as claims, not evidence.
- Gate snapshot (coordinator, after rework): check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cache_diff, check_cross_fire all rc=0; check_traceability deferred. Entry conditions met.

### policy_conflict_scan (revision 2)

- Base section still verbatim (key-by-key equality with blueprint/products/charge.yaml re-run: all True).
- Same four extended policies, same subjects, target tools and computes; two disjoint two-node trees as in round 1. `(target_tool, computes)` still unique per policy.
- New overwrite entries: both relief-credit policies now also overwrite charge_evt_notice_and_response "otherwise payments issued before the late response stay charged even if relief is later granted" (superseded clause verbatim in base: True; replacement verbatim in the extended rule: True). The retained half of that base sentence ("A late response is treated as timely only when the employer shows good cause") agrees with both replacements (good cause → whole share). The two replacements are event-scoped and do not collide.
- charge_ext_response_disputed_amount now lists charge_evt_relief_grounds in base_policy_refs; it reads the class relief flags only to size the disputed amount, and no base sentence governs that quantity. No conflict.
- Cross-category: protest_amount and protest_relief_credit read taxacct; response_disputed_amount reads taxacct (class, reserve credits, bill); response_relief_credit now declares `cross_category: []` and its compute reads no other category — consistent.
- Scope observation (two claimed event types with no policy) unchanged.

### rule_compute_equivalence (revision 2)

charge_ext_protest_amount
- credits_taken_out: rule now reads "Credits posted in the statement's own quarter are already netted in what was billed or posted for that quarter, so only credits posted on the position in a quarter other than the statement's quarter are looked at: where a credit for a recovered overpayment is among them, every credit posted on the position in a quarter other than the statement's quarter is taken out …; where no recovered-overpayment credit is among them but credits for cancelled payments are, those cancelled-payment credits are taken out; otherwise nothing is taken out." Compute `recovery_credits_outside`, `cancel_credits_outside`, `credits_taken_out = credits_all − credits_in_quarter` — equivalent on all three points raised in round 1 ((a) statement-quarter credits excluded by both; (b) earlier quarters included by both, "a quarter other than"; (c) the ladder now ends in "otherwise"). **F1 closed.**
  - Observation R2-O1: the justifying clause "already netted in what was billed or posted for that quarter" is true for the bill and reserve-posting tiers of the starting amount but not for its fall-through tier ("the total of the charges the statement lists, each at its posted amount", gross). The operative instruction is unambiguous ("only credits posted … in a quarter other than the statement's quarter are looked at"), so no second value follows; recorded as a false aside, latent.
- protest_interest_basis (new; replaces protest_interest_rate) ← "The monthly protest interest is, when the employer's tax account shows interest assessed for the statement's quarter, the latest month of that assessed interest in proportion to the protested principal over the amount billed for the quarter; when no interest has yet been assessed for that quarter but the employer finances benefits by reimbursement and the bill for the quarter is past its due date, the protested principal times the late-payment interest rate of the employer's tax account class; and nothing otherwise." Compute: tier 1 additionally requires `billed_for_quarter > 0` (the divisor). Observation R2-O2: for a contributory employer with contribution interest assessed for the statement's quarter the rule's tier 1 holds with no "amount billed" to divide by, while the compute falls through to 0; inert, because interest_months is 0 without a reimbursement bill. Equivalent wherever the result can be non-zero.
- protest_interest / result: "the monthly protest interest times the number of interest months, rounded to the cent" — equivalent.
- Remaining bindings unchanged from round 1 — equivalent.

charge_ext_protest_relief_credit
- New cap: "never more than the charge still standing on the position (every charge posted less every credit posted)" ← `standing_on_position`, `MN(…, standing_on_position)` — equivalent.
- wage-record share now "number at least four / one to three" (counts reports), = XCOUNT. **O3 closed.**
- Remaining bindings unchanged — equivalent.

charge_ext_response_disputed_amount (redesigned)
- counted_charges — equivalent (unchanged).
- basis_amount ← financing-basis sentence: contributory ∧ reserve credited (XCOUNT taxacct_reserve_credited > 0) → counted charges; reimbursing ∧ billed for the latest statement quarter → the bill; otherwise 0 — equivalent.
- charges_left_out — equivalent (unchanged).
- class_share ← "the whole when the position's charge class allows relief for a voluntary quit, a discharge for misconduct and a refused offer of work; when the class allows continuing part-time relief and none of those separation grounds, … the most recent charge posted over the counted charges …; and zero otherwise" — equivalent.
- window_share ← "the whole when the response is received no later than the response window after the notice of claim mailing date; nine tenths when it is received after the window while the position still awaits its response …; and zero otherwise …". Compute adds `awaiting_response` to tier 1. Latent only (a response is lodged only on a noticed position, lifecycle noticed→responded), no consequence.
- result — equivalent.

charge_ext_response_relief_credit (redesigned)
- relief_window, credits_netted — unchanged, equivalent.
- ground_share ← the three-tier sentence (with responses_on_record > 0 and the class flags) — equivalent.
- answer_share ← "the whole when the response on record was received no later than the response window … or was late with good cause shown; nine tenths when it was received after the window without good cause; and zero when no response is on record" — compute DAYS(response_due_date, response_date) > 0 ∧ timeliness ≠ late_good_cause — equivalent (due date = mailing date + window).
- result "the relief window times the relief ground share, less the credits netted from it, never below zero, times the relief answer share, rounded to the cent" — equivalent.
- Self-asserted cap ("because the credits netted are every credit standing on the position, the relief credit never exceeds the charge still standing there"): checked — in both non-empty netting tiers the credits netted equal every credit on the position, and the relief window never exceeds every charge posted, so the claim holds.

### action_binding_and_uuids (revision 2)

task_tools.py unchanged (811d5e08…) and every policy's target_tool is unchanged → round-1 conclusion carried forward: unique bindings, no prerequisite judged by any tool body, four independent uuid8s.

### prerequisite_graph (revision 2)

- Same two edges, same `problem`, `kind: value_input`, `form: state`, `resolved_by`, `gate` bindings (protest_ground_recorded; reported_reason) present in compute. Acyclic. `policy_source` verbatim in its own rule: both True.
- Edge A sentence now "The relief credit of a protest decision is fixed only after the position carries a **pending** written protest of the statement, with the protest ground and the protest date recorded on it." — now at the strength of the `condition` (protest_pending). **O4 closed.**
- Edge B effect text updated to the new shares; condition unchanged. No authoring-viewpoint phrasing.

### prerequisite_sentences (revision 2)

Four-point test re-run on both sentences: ordering connective ("only after" / "not … until"), state form in record words, no tool/id/snake_case token, strength equal to the condition — pass. One resolving write each (file_charge_protest_73ec7ae2; submit_separation_response_153a3a70); the depended-on rules do not restate them; no undeclared cross-problem order in any extended rule. Derivations as in round 1.

### override_declarations (revision 2)

- charge_ext_protest_amount, charge_ext_response_disputed_amount: overwrite [] — new quantities, no base sentence handled differently.
- charge_ext_protest_relief_credit / charge_ext_response_relief_credit: the late-response bar is now declared (**F2 closed**). charge_evt_credits "never exceeds charge_msr_remaining_charge" is still not overwritten; the protest relief credit is now capped at the position's standing charge and the response relief credit is bounded by it (see above). Both book against "the single posted charge that still stands", so where exactly one charge stands the cap equals that charge's remaining amount. Residual (observation R2-O3, latent): where several charges stand, the position-wide cap can exceed the one named charge's remainder. **F3 closed for every world where "the single" charge has a referent**, which includes both tasks.

### factor_ladders (revision 2)

| policy | factor | effect | tiers | fall-through reachable by a customer at this write? | cross_difficulty |
|---|---|---|---|---|---|
| protest_amount | statement_starting_amount | method | 3 | yes | taxacct |
| protest_amount | credits_taken_out | method | 3 | yes | — |
| protest_amount | protest_documentation_share | parameter | 3 | yes | taxacct |
| protest_amount | notice_answer_share | parameter | 3 | yes | — |
| protest_amount | interest_months | method | 3 | yes | taxacct |
| protest_amount | protest_interest_basis | method | 3 | yes | taxacct |
| protest_relief_credit | relief_reach | method | 3 | yes | — |
| protest_relief_credit | credits_deducted | method | 3 | yes | — |
| protest_relief_credit | wage_record_relief_share | parameter | 3 | yes | taxacct |
| protest_relief_credit | answer_abatement | parameter | 3 | yes | — |
| response_disputed | response_counted_charges | method | 3 | yes | — |
| response_disputed | response_financing_basis | method | 3 | yes | taxacct |
| response_disputed | response_charges_left_out | method | 3 | yes | — |
| response_disputed | response_class_share | parameter | 3 | **no — no charge class reaches it** | — |
| response_disputed | answer_window_share | parameter | 3 | **no — a response is lodged only on a position still awaiting it** | — |
| response_relief_credit | relief_window | method | 3 | yes | — |
| response_relief_credit | credits_netted | method | 3 | yes | — |
| response_relief_credit | relief_ground_share | parameter | 3 | yes (e.g. lack of work) | — |
| response_relief_credit | relief_answer_share | parameter | 3 | **no — a determination on a response always has a response on record** | — |

Declared counts: protest_amount 6 (4 method / 2 parameter); protest_relief_credit 4 (2/2); response_disputed 5 (3/2); response_relief_credit 4 (2/2). Every tier stated in the rule and implemented in its binding; fall-throughs equal the baselines; baseline sentences all in the rules (string containment True); labels honest.

Reality:
- **protest_interest_basis** replaces protest_interest_rate. Tier 1 pro-rates the interest actually assessed on the quarter's bill to the protested principal; tier 2 estimates it at the class late-payment rate when the bill is past due and no interest is yet booked; fall-through none. Real (taxacct_evt_charges_and_billing: "interest runs on an unpaid bill as on unpaid contributions"); the contributory reserve-interest tier is gone. **F4 closed.**
- dispute_standing_share, relief_standing_share, answer_promptness_share, relief_promptness_share removed. **F5 and F6 closed** (no factor now weighs late-report penalties or a day-6-to-10 timely response).
- **New defect R2-F1 — response_class_share (response_disputed_amount).** The fall-through ("zero otherwise") is reached by no charge class. Enumerating the seven variants of this charter: Separating Employer — Most Recent, Base Period Employer — Proportional Share, Combined Wage Claim Contributing Employer, Extended Benefits State-Share Employer allow all three separation grounds → tier 1 (1.00); Continuing Part-Time Base Period Employer and the two Reimbursing classes allow none of them and allow continuing part-time relief → tier 2. No position can sit on the fall-through, so the ladder has two real tiers, and the baseline value 0.00 (`class_share_none`, which the baseline rule calls "the shares of a response that can put nothing in dispute") is a value no responding employer is ever given — the straw man the skill names (a zero where the standard method gives a figure: for the four separation-relief classes the standard share is the whole).
- **New defect R2-F2 — answer_window_share (response_disputed_amount).** The fall-through ("zero otherwise, a position no longer awaiting a response being chargeable without relief") cannot hold of any customer who reaches this write: the write is charge_separation_response_filed, lifecycle `noticed → responded` only, so every response is lodged on a position still awaiting it and falls in tier 1 or tier 2. Two real tiers; the baseline 0.00 (`answer_lapsed`) is a share no lodged response can take.
- **New defect R2-F3 — relief_answer_share (response_relief_credit).** The fall-through ("zero when no response is on record") cannot hold at this write: the policy's own prerequisite sentence says the credit "is not fixed until the position carries the employer's separation response", and the subject charge_relief_determined transitions only from `responded`. Its baseline rule — "In the standard determination no response is on record and no relief is due" — describes a determination the same rule forbids. Two real tiers; baseline 0.00 is a straw man. (relief_ground_share's fall-through, by contrast, is reachable and real: a response reporting lack of work earns no relief.)
- Observation R2-O4 — response_financing_basis: tier 1 ("contributory … and holds a reserve account credited with its contributions") is the identity on the counted charges, and its fall-through gives "nothing" to a contributory employer with no reserve credit yet, while taxacct_evt_charges_and_billing posts such an employer's charges against its reserve all the same ("For a contributory employer they are posted against the reserve account"). Borderline; the reimbursing half of the fall-through ("a reimbursing employer not yet billed having paid nothing") is a defensible treatment. Not raised to RED.
- O1 (zero standard computation) now extends to all four policies; O2 (answer-share haircut values) unchanged.

Per-task multi-source / cross_difficulty, as declared: task 0 — statement_starting_amount (multi-source, taxacct); task 1 — response_financing_basis (multi-source: class ∧ reserve credits / class ∧ bill; taxacct). Whether these survive, and the counts after striking R2-F1..F3, are decided per task.

### findings (revision 2)

Round-1 items:
- F1 — closed (rule now states "a quarter other than the statement's quarter"; compute equal; "otherwise" ends the ladder). Residual aside R2-O1 (observation).
- F2 — closed (late-response bar declared in both relief-credit overwrites).
- F3 — closed where "the single" standing charge exists (cap / bound added); residual R2-O3 latent.
- F4 — closed (protest_interest_rate replaced by a real interest basis).
- F5, F6 — closed (factors removed from both response policies).
- O3, O4 — closed. O1, O2, scope observation — remain observations (the reworker's reasons sit in the worklog, unread here; they do not change an observation's status).

New in revision 2 (all bear on task 1):
- **R2-F1 — SOURCE-FACTOR RED**: response_class_share fall-through unreachable by any class; baseline 0.00 is a straw man.
- **R2-F2 — SOURCE-FACTOR RED**: answer_window_share fall-through unreachable at a response write; baseline 0.00 is a straw man.
- **R2-F3 — SOURCE-FACTOR RED**: relief_answer_share fall-through unreachable at a determination; baseline rule contradicts the policy's own prerequisite sentence.
- R2-O1..O4 observations as above.

### closing_checklist (revision 2)

Written after the round-2 reveals (18:23Z). The revision_2 sections above were frozen before them.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
|---|---|---|---|---|
| 0 | PASS (F1 closed) | PASS | PASS (F4 closed) | PASS (T0-1 closed) |
| 1 | PASS | PASS | SOURCE-FACTOR RED (R2-F1..F3 straw-man baselines on unreachable fall-throughs; no near-miss) | PASS |

The difficulty still does **not** close (task 1). Round-1 items: F1, F2, F4, F5, F6, O3, O4 closed; F3 closed wherever the single standing charge exists (residual R2-O3 latent); O1, O2 and the scope observation remain observations. Coverage, scope disjointness (re-confirmed against both charter_scope fields), uuid8s, trees (one prerequisite, one value_input edge, a user write, acyclic) — all hold. Instantiation-stage gates were not re-run by this audit; the coordinator's round-2 snapshot (all rc=0) covers the current hashes (charge.extended.yaml 48398cf0…, task_tools.py 811d5e08…).

## revision_3

### charter_global_frozen (revision 3)

- Freeze: 2026-10-10 ~19:09Z, before any round-3 task file was opened. Same auditor; independent of the instantiator/reworker.
- Hashes on disk match the brief: charge.extended.yaml f8288e37a8f9187b27fe7fbf51e3f9722c31fdc032da4fd814e6b9c12c39fea9 (**changed** → charter-global sections re-derived); task_tools.py 811d5e08… (unchanged → action_binding_and_uuids carried forward; every target_tool re-checked unchanged); blind views task_0 dee15a90… (unchanged), task_1 c5c7efcc… (seed and persona changed).
- Masked/unread at freeze: tasks/0.json (cec2458c…), tasks/1.json (5a372094…), worklogs, reworker notes. Reworker claims taken as item ids only.
- Gate snapshot (coordinator, round 3): all rc=0; traceability deferred.

### what changed in the charter (located by re-reading every extended policy)

- Base section: still verbatim (key-by-key equality True).
- charge_ext_protest_amount: the aside "Credits posted in the statement's own quarter are already netted in what was billed or posted for that quarter, so" is removed; the sentence now begins "Only credits posted on the position in a quarter other than the statement's quarter are looked at: …". Compute, factors, params, baseline unchanged. **R2-O1 closed.**
- charge_ext_protest_relief_credit: unchanged.
- charge_ext_response_disputed_amount: response_class_share tier 1 now also requires "the position charges a regular or combined wage claim" (compute: `'Extended Benefits' not in F('variant_name')`), and the fall-through is described "as on an Extended Benefits state-share position, whose relief follows the determination on the regular claim". answer_window_share redesigned: on time → 1.00; after the due date with no charge posted after the due date → 0.90; otherwise (after the due date with a charge posted while overdue) → 0.75 (`answer_late_charged`). Baseline params now [class_share_none, answer_late_charged].
- charge_ext_response_relief_credit: relief_answer_share redesigned the same way (on time or late with good cause → 1.00; late without cause, no charge after due → 0.90; otherwise → 0.75); the overwrite of the late-response bar now carries this sentence; the baseline rule now reads "In the standard determination the response on record reports a separation for which no relief is due and was received after the due date without good cause once a payment had been charged, so the relief window holds no charge, no credit is netted, the relief ground share is zero and the relief answer share is three quarters." Baseline params [ground_share_none, answer_late_charged].

### policy_conflict_scan / override_declarations (revision 3)

- Subjects, tools, computes, scopes as before; (target_tool, computes) unique.
- Overwrites: all superseded clauses verbatim in base; all replacements verbatim in the extended rules (True ×6). The response relief credit's late-bar replacement now has three tiers; consistent with the retained half of the base sentence ("A late response is treated as timely only when the employer shows good cause") — good cause → whole share.
- response_class_share's Extended Benefits fall-through agrees with base charge_evt_relief_grounds "Relief granted on the regular claim also covers the employer's Extended Benefits charges on the same claimant" and `eb_relief_follows_regular: true`. No conflict.
- Observation carried (R3-O2, base-internal, latent): base lifecycle "noticed → chargeable by system: The response window passed with no response" vs base's own late-response provisions and the late tiers of both window/answer shares — a late response is lodgeable only while the lapse has not yet been processed. The tension is inside base and is not exercised by either task.

### rule_compute_equivalence (revision 3)

- response_class_share: tier 1 rule "the position charges a regular or combined wage claim and its charge class allows relief for a voluntary quit, a discharge for misconduct and a refused offer of work" vs compute (three class flags ∧ class name not Extended Benefits). Equivalent over this charter's classes: the only class whose entry gate admits an Extended Benefits claim while allowing all three separation grounds is Extended Benefits State-Share Employer (the reimbursing classes, which also admit EB claims, fall to the part-time tier).
- answer_window_share: tier 1 "received no later than the response window after the notice of claim mailing date" vs `DAYS(response_due_date, NOW) <= 0` — equivalent because the position's response_due_date is the mailing date plus the window (base). Tier 2/3 split on "a benefit charge has been posted on the position after that due date" vs `DAYS(due, latest charge entry_date) > 0` — equivalent.
- relief_answer_share: `late_without_cause` (DAYS(due, response_date) > 0 ∧ timeliness ≠ late_good_cause), then `charge_after_due` — equivalent to the three-tier sentence.
- Everything else unchanged from revision 2 — equivalent.

### prerequisite_graph / prerequisite_sentences (revision 3)

Unchanged: both edges' sentences verbatim in their own rules (True), state form, value_input, one resolving write each, acyclic, four-point test passes.

### factor_ladders (revision 3)

Reachability of every fall-through at its write (the round-2 defect class):

| policy | factor | fall-through | reachable? |
|---|---|---|---|
| response_disputed | response_class_share | 0.00 — Extended Benefits State-Share Employer position | **yes**: enumeration over the 7 variants → Separating, BPE, CWC tier 1; Continuing Part-Time and both Reimbursing tier 2; **Extended Benefits State-Share → fall-through** |
| response_disputed | answer_window_share | 0.75 — response after the due date with a charge posted while overdue | **yes** (as far as base admits late responses at all, R3-O2) |
| response_relief_credit | relief_answer_share | 0.75 — response on record late without cause with a charge posted while overdue | **yes**; no longer conditioned on "no response on record" |
| response_relief_credit | relief_ground_share | 0.00 — e.g. lack of work | yes (unchanged) |
| protest policies | all | unchanged | yes |

Reality:
- response_class_share: three real tiers — full share for classes that can obtain separation relief on a regular/CWC claim; the one contestable week for part-time-only classes; nothing for an EB state-share position, whose relief follows the regular determination (base). Real. **R2-F1 closed.**
- answer_window_share / relief_answer_share: on time (or good cause) → whole; late without a charge while overdue → 0.90; late with a payment charged while overdue → 0.75. The condition — lateness and whether payments were charged while the answer was overdue — is the very thing the base late-response bar weighs ("payments issued before the late response stay charged"); haircut values are synthetic (O2 class). Real. **R2-F2, R2-F3 closed.**
- Counts: protest_amount 6 (4/2), protest_relief_credit 4 (2/2), response_disputed 5 (3 method / 2 parameter), response_relief_credit 4 (2/2). All tiers in the rules, fall-throughs = baselines, labels honest.
- **Observation R3-O1 (baseline narrative self-contradictory, no numeric consequence).** response_disputed_amount baseline: "In the standard response no benefit has yet been charged when the employer answers, … and the answer window share is three quarters, the share of a response received after the due date when a payment has been charged while the answer was overdue" — "no benefit has yet been charged" and "a payment has been charged" cannot both describe one response. response_relief_credit baseline: "… was received after the due date without good cause once a payment had been charged, so the relief window holds no charge" — with a payment charged and no statement mailed, the relief window rule makes it "every charge posted", not "no charge". Each baseline still yields one definite number (0.00: counted charges / ground share zero), and each declared factor baseline equals its fall-through, so no relationship is shown to fail; recorded because a reader of the computation document meets a standard case that cannot exist.
- R2-O3 (single-charge cap residual), R2-O4 (financing basis identity/contributory fall-through), O1, O2, scope observation: unchanged, remain observations.

### findings (revision 3)

- R2-F1, R2-F2, R2-F3 — **closed** (fall-throughs reachable and real; see table).
- R2-O1 — **closed** (false aside removed; operative instruction unchanged).
- New: R3-O1 (self-contradictory baseline narratives, observation), R3-O2 (base-internal lapse vs late response, observation). No new RED at charter level.

### closing_checklist (revision 3)

Written after the round-3 reveals (19:09Z); the revision_3 charter-global sections above were frozen before them.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | SOURCE-CHAIN RED (R3-T1-1: proof field only — edge_load_bearing / design_rationale name a "zero tier" of relief_answer_share that no longer exists; the tree itself holds) | PASS | PASS |

- Round-2 REDs R2-F1, R2-F2, R2-F3 (charter) and R2-T1-1, R2-T1-2 (task 1) are closed; R2-O1 and the row-count observation closed. Task 0 did not regress.
- The difficulty does not close while R3-T1-1 stands. Every substantive check passes: coverage and scope disjointness, unique (tool, computes) bindings, unchanged uuid8s, one prerequisite with one value_input edge and a user write per tree, acyclic graph; every computation has 4–6 real factors (≥2 parameter, ≥1 method) bearing weight against reachable, honest fall-throughs, with a near-miss per computation and seeded cross-difficulty evidence in each task.
- Observations standing: O1, O2, R2-O3, R2-O4, R3-O1, R3-O2, scope (two claimed event types with no policy).
- Gates: not re-run by this audit; the coordinator's round-3 snapshot (all rc=0) is on the current hashes (charge.extended.yaml f8288e37…, task_tools.py 811d5e08…).

## revision_4

### charter_global_frozen (revision 4)

- Freeze: 2026-10-10 ~20:03Z, before any round-4 task file was opened. Same auditor.
- Hashes on disk match the brief: charge.extended.yaml 9d602d53a78610048be915d350949a547b8f8460673c72ee35651fc0b2b8a686 (changed); task_tools.py 811d5e08… (unchanged); blind views dee15a90… and c5c7efcc… (both unchanged from round 3).
- Masked/unread at freeze: tasks/0.json (3538fabe…), tasks/1.json (f6236481…), worklogs, reworker notes.
- Gate snapshot (coordinator, round 4): all rc=0; traceability deferred.

### what changed in the charter (verified, not taken from the brief)

- Base section verbatim (key-by-key True).
- Re-read every extended policy's params, compute bindings, factor ladders, factor baselines, prerequisite and overwrite entries: identical to revision 3 for all four policies (same expressions, same tier conditions and values, same baseline bindings class_share_none / answer_late_charged / ground_share_none / answer_late_charged, same prerequisite sentences verbatim in their rules, same overwrites verbatim on both sides).
- Changed: the "standard" sentence of the two response policies, in both the rule and baseline.rule (each baseline sentence is in its rule: True ×2 per policy):
  - charge_ext_response_disputed_amount: "In the standard computation, with no factor applied, the response counts no charge, the financing basis is nothing and no charge is left out; the response class share takes its default of zero, the value an Extended Benefits state-share position receives because its relief follows the determination on the regular claim; and the answer window share takes its default of three quarters, the value of a late answer once a payment has been charged while it was overdue."
  - charge_ext_response_relief_credit: "In the standard computation, with no factor applied, the relief window holds no charge and no credit is netted; the relief ground share takes its default of zero, the value of a reported separation for which no relief is due; and the relief answer share takes its default of three quarters, the value of an answer received after the due date without good cause once a payment had been charged while it was overdue."
- Protest policies unchanged from revision 3.

### baseline coherence (R3-O1)

- The rewritten sentences no longer narrate one impossible response; each states the default of each input and names the real situation that default belongs to. Every named default equals its factor's fall-through tier (counted charges: no charge; financing basis: nothing; left out: nothing; class share 0.00 = EB state-share tier; window share 0.75 = late-and-charged tier; relief window: no charge; netted: nothing; ground share 0.00 = no-relief separation; answer share 0.75 = late-without-cause-and-charged tier). No contradiction remains. **R3-O1 closed.**
- Self-sufficiency: from the baseline alone a reader computes disputed amount = RND(MX(0, 0 − 0) × 0.00 × 0.75) = 0.00, and relief credit = RND(MX(0, 0 × 0.00 − 0) × 0.75) = 0.00 — definite on every world. Whether they differ from gold is checked per task.

### other charter-global sections (revision 4)

policy_conflict_scan, rule_compute_equivalence, action_binding_and_uuids, prerequisite_graph, prerequisite_sentences, override_declarations and factor_ladders: carried forward from revision 3 on the strength of the verification above (only the two standard sentences changed; no binding, tier, edge or overwrite moved). Their revision-3 conclusions stand: no charter-level RED. Observations standing: O1, O2, R2-O3, R2-O4, R3-O2, scope.

### closing_checklist (revision 4)

Written after the round-4 reveals (20:03Z); the revision_4 sections above were frozen before them.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

The difficulty passes the source-layer audit.
- Per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; `_difficulty.md` alongside; revisions 1–4 preserved in order; the latest comparison section of each task carries PASS on all four relationships.
- Coverage and scope: the 4 extended policies are covered; task scopes {protest_amount, protest_relief_credit} and {response_disputed_amount, response_relief_credit} are pairwise disjoint, each spanning its whole tree; task tools and GT closed; four independently generated uuid8s (73ec7ae2, 0f56e95e, 153a3a70, e2b9af19), unchanged since round 1.
- Trees: each has one prerequisite problem, one value_input edge (≥ max(n−1, 1)), an owner=user write (protest / separation response), state-form prerequisite sentences verbatim in the blocked rules; the difficulty's prerequisite graph is two disjoint edges, acyclic.
- Factors: protest_amount 6 (4 method / 2 parameter), protest_relief_credit 4 (2/2), response_disputed_amount 5 (3/2), response_relief_credit 4 (2/2); every ladder ≥ 3 tiers stated in full in its rule, distinct in outcome, with reachable and real conditions and outcomes; every factor bears weight on its task's world against its baseline; each whole baseline gives a definite 0.00 ≠ gold (274.88, 272.16, 345.60, 345.60); per task a multi-source and a cross-difficulty factor with seeded taxacct rows (task 0: statement_starting_amount; task 1: response_financing_basis); a near-miss per computation (task 0: the in-quarter cancelled-payment credit and the 2024-Q4 amendment 15 months back; task 1: the response on the inclusive tenth day).
- Gates: not re-run by this audit; the coordinator's round-4 snapshot (all rc=0) is on the final hashes (charge.extended.yaml 9d602d53…, task_tools.py 811d5e08…, tasks/0.json 3538fabe…, tasks/1.json f6236481…).
- Observations standing (no demonstrated consequence; not grounds for rework): O1 (standard computations give 0.00 on every world), O2 (synthetic haircut values on answer shares), R2-O3 (position-wide cap vs one named charge when several charges stand), R2-O4 (financing-basis tier 1 is the identity; contributory fall-through vs taxacct reserve posting), R3-O2 (base lapse vs late response), scope (charge_chargeability_determined and charge_protest_denied claimed with no policy).

## revision_5

### charter_global_frozen (revision 5)

- Freeze: 2026-10-10 ~21:18Z, before round-5 tasks/0.json (6ce3697f…) / tasks/1.json (cb68a82e…) and before the render-layer KB audit (audits/policy_kb/employer_charge_protests/) were opened. The P1–P4 descriptions used here are the one-line summaries in the coordinator's brief.
- Hashes on disk match the brief: charge.extended.yaml ebe9951a25d999b581a80a8b062ec4ed1ea5288d8f7469762c8798da77d7b0b4 (changed); task_tools.py 811d5e08… (unchanged); blind views dee15a90… / c5c7efcc… (unchanged). New files task_0.runtime.json / task_1.runtime.json have appeared in /tmp/coord0049/views/employer_charge_protests/; they are not part of this audit's inputs and were not opened.
- Gate snapshot (coordinator, round 5): all rc=0.

### what changed in the charter (verified)

- Base section verbatim (key-by-key True).
- charge_ext_protest_amount:
  - monthly protest interest, tier 1 now "when the employer's tax account shows interest assessed for the statement's quarter **and an amount billed for that quarter**"; factor ladder tier 1 the same; compute unchanged (interest_assessed_latest > 0 and billed_for_quarter > 0). Rule and compute now agree on the divisor guard. **P2 closed**; this also closes my R2-O2 (the same gap seen from the contributory side).
  - interest months now "when the **latest payment applied to the reimbursement bill** for the statement's quarter was received after the bill's due date …; when **no payment has been applied to that bill** and its due date has passed …"; compute bill_paid_on now filters component='reimbursement' (and inputs.history matches). Equivalent: the latest reimbursement-component payment for the quarter is the latest payment applied to that bill; "no payment applied" = no such row. **P3 closed.**
- charge_ext_protest_relief_credit and charge_ext_response_relief_credit, two new rule sentences each:
  - "This replacement governs only the relief credit of a protest decision [of a determination on a separation response]; a relief that an appeal decision grants still credits the whole remaining charge of every posting within the relief's scope." This scopes the two overwrites of "A granted relief credits back every charge …" / "A relief credits the whole remaining charge …" to their own events and leaves the appeal path (charge_relief_by_appeal; charge_evt_credits "an appeal decision relieving the employer credits as a relief does") on the base clause. Each superseded clause is still in base verbatim; the two event-scoped replacements and the appeal path no longer compete for one clause. **P4 closed.**
  - "For a protest decision [determination on a separation response] the class term that payments issued before a late response stay charged even if relief is later granted is applied only through the answer abatement [relief answer share] …, and no payment is kept charged on that account beyond it." This is now the replaced_by of the late-bar overwrite in both policies (verbatim in the rule: True). It names the variant parameter relief_bar_for_payments_before_late_response (true for every class) by its meaning and states how it is applied, so the class term and the retired base clause no longer give a second reading. **P1 closed** by declaration.
- charge_ext_response_disputed_amount: unchanged.
- All other params, compute bindings, factor ladders, factor baselines, prerequisites: unchanged (re-read). Prerequisite sentences verbatim in their rules (True ×2); baseline sentences in rules (True for all four).

### checks re-run on the changed text

- Override declarations: every superseded clause verbatim in base and every replacement verbatim in its rule (True ×6). The merged semantics are unique: protest decision → its own credit formula with the late bar applied through the abatement; response determination → its own formula with the late bar through the answer share; appeal relief → base clause. No undeclared override found in the new sentences.
- Prerequisite sentences: the new sentences state no cross-problem order, name no tool, policy id or snake_case token; no second wording of either prerequisite.
- Rule/compute: P2, P3 as above; nothing else moved.
- Factor ladders: unchanged in structure and reality (revision 3/4 conclusions stand); protest_interest_basis and interest_months ladders now state their conditions exactly as computed.
- Mechanical replay of every computation on both blind worlds (DSL evaluator from check_compute.py, inline, no file written; post-write worlds built by applying the user tool's documented effect): task 0 protested_amount 274.88, relief credit 272.16 (skip-protest 0.00); task 1 disputed amount 345.60, relief credit 345.60 (skip-response 0.00); every factor's baseline substitution as in revision 4 (580.31 / 3,157.74 / 0.00 / 343.60 / 272.16 / 272.16; 0.00 / 340.20 / 0.00 / 340.20; 0.00 / 0.00 / 691.20 / 0.00 / 259.20; 0.00 / 691.20 / 0.00 / 259.20). No scored value moved.

### findings (revision 5)
- P1, P2, P3, P4 (render-layer audit, policy side) — closed in the charter (evidence above). R2-O2 closed with P2.
- No new defect. Observations standing: O1, O2, R2-O3, R2-O4, R3-O2, scope.

### closing_checklist (revision 5)

Written after the round-5 reveals (21:18Z); the revision_5 sections above were frozen before them.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
|---|---|---|---|---|
| 0 | PASS | PASS | SOURCE-FACTOR RED (R5-T0-1: proof field only — "39.08 x 272.16 / 3,908.10 = 2.7216" ×4; true 2.72153; scored 274.88 unaffected) | PASS |
| 1 | PASS | PASS | PASS | PASS |

- P1–P4 (render-layer audit, policy side): closed in the charter; R2-O2 closed with P2. No scored value moved; no regression in either task (mechanical replay and GT both give 274.88 / 272.16 and 345.60 / 345.60 with unchanged sensitivities).
- R5-T0-1 is a defect of tasks/0.json proof text only; it predates this round and was missed by this auditor in revisions 2–4 (disclosed in 0.md). The difficulty does not close until it is corrected.
- All other closing items as in revision 4 (coverage, disjoint scopes, uuid8s, trees, factor counts and reality, baselines definite and ≠ gold, near-misses, seeded cross-difficulty rows). Gates: coordinator's round-5 snapshot all rc=0 on charge.extended.yaml ebe9951a…, task_tools.py 811d5e08…; not re-run here.
- Observations standing: O1, O2, R2-O3, R2-O4, R3-O2, scope.

## revision_6

### charter_global_frozen (revision 6)

- Freeze: 2026-10-10 ~21:37Z, before round-6 tasks/0.json (eaac8a65…) / tasks/1.json (cbecf569…) were opened.
- charge.extended.yaml ebe9951a… and task_tools.py 811d5e08… are byte-identical to revision 5 (hashes re-computed on disk), and the blind views (dee15a90…, c5c7efcc…) are unchanged. Per the re-audit rule, every charter-global section is carried forward from revision 5 on the strength of those two hashes; nothing in them is re-derived or altered.
- Gate snapshot (coordinator, round 6): all rc=0, now including TRACEABILITY OK.

### closing_checklist (revision 6)

Written after the round-6 reveals (21:37Z); the revision_6 freeze above preceded them.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

The difficulty passes the source-layer audit.
- R5-T0-1 closed; the auditor's own sweep of every stated equation in both tasks' proof text found no further false figure.
- Charter (ebe9951a…) and tools (811d5e08…) unchanged since revision 5; every revision-4/5 closing item stands: coverage of the four extended policies; disjoint task scopes spanning whole trees; four independent uuid8s; one prerequisite problem with one value_input edge and a user write per tree, state-form sentences verbatim in the blocked rules, acyclic graph; factor counts 6 / 4 / 5 / 4 with ≥2 parameter and ≥1 method, every ladder real with reachable fall-throughs, every factor bearing weight; whole baselines 0.00 ≠ gold (274.88, 272.16, 345.60, 345.60); multi-source and seeded cross-difficulty factors per task; a near-miss per computation; P1–P4 closed in the charter.
- Gates: coordinator's round-6 snapshot all rc=0, including TRACEABILITY OK, on the final hashes (charge.extended.yaml ebe9951a…, task_tools.py 811d5e08…, tasks/0.json eaac8a65…, tasks/1.json cbecf569…); not re-run here.
- Observations standing (not grounds for rework): O1, O2, R2-O3, R2-O4, R3-O2, scope (two claimed event types with no policy).
