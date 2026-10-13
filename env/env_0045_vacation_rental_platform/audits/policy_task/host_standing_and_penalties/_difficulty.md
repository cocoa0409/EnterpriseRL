# Policy-task audit — host_standing_and_penalties / charter-global

## charter_global_frozen

- auditor: erl-task-policy-audit (independent Claude agent; not the instantiator)
- freeze time: 2026-10-07T19:20Z, written before any task's GT was revealed
- frozen inputs (sha256, matched against the coordinator's SHA256SUMS):
  - `tasks/host_standing_and_penalties/host.extended.yaml` bfe6e9be47b4dd86d988ff3454c20c64259aa3426d1c2f2bb1373c064cf1573b
  - `tasks/host_standing_and_penalties/task_tools.py` 0a815c03be73db4f3fad48140f29cbc0898b0a3ce894b9ddadde860ad4e1b4a7
  - `/tmp/erl45_views/r1/host_standing_and_penalties/task_0.view.json` dd9d768d4ee2eb3508ef8777e906095e01d33d6f4240c700af70022a514820bc
  - `/tmp/erl45_views/r1/host_standing_and_penalties/task_1.view.json` ff5385848fb0cb228d55c1158f72e1b65b89e691de9fe579f0fb1f22107a74f4
- permitted: `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml), the extended charter, task_tools.py, the two masked views (frozen_time, user_scenario, initial_state only), `erlbench/`, the instantiate-skill compute DSL (`skills/erl-task-instantiate/scripts/check_compute.py`, read for primitive semantics only).
- masked / unread: `tasks/*.json` in full (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), `tasks/host_standing_and_penalties/worklog.md`, the scenario `worklog.md`, any sibling difficulty's tasks or audits.
- entry conditions (Step 0): gate snapshot supplied (`/tmp/erl45_views/r1/host_standing_and_penalties/gate_snapshot.txt`): check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all OK; check_cache_diff INFO; check_traceability NOT OK, which the brief explains as expected before KB rendering (it scans `docs/`). Masked views and hashes supplied and verified. Entry conditions met.

Charter shape: base section (verbatim host category) + 4 extended policies:

| extended policy | subject | computes | target_tool (owner) | prerequisite |
| --- | --- | --- | --- | --- |
| host_ext_superhost_redecision | host_tier_updated | variant_name | apply_superhost_decision_f25b833f (agent) | [] |
| host_ext_superhost_travel_credit | host_travel_credit_issued | amount | claim_superhost_travel_credit_0d8c95c2 (user) | -> host_ext_superhost_redecision (value_input, state form) |
| host_ext_professional_plus_enrollment | host_tier_updated | variant_name | enroll_professional_tier_a874e389 (user) | [] |
| host_ext_professional_fee_rerating | host_service_fee_refunded | amount | refund_rerated_host_fee_9248fd19 (agent) | -> host_ext_professional_plus_enrollment (value_input, state form) |

### policy_conflict_scan

- Overlapping subjects: `host_tier_updated` is the subject of two extended policies (redecision, enrollment) and of base `host_tier_assignment`. The two extended policies are separated by object: redecision speaks only of "An individual host account's Superhost assessment ... while the account is suspended" and sets Superhost/Standard Host; enrollment speaks only of "A Professional Host account moves into Professional Host Plus only when the host enrolls it in person". No world satisfies both subjects at once (an account with a business_name or >= 11 live listings is a professional account under the base precedence and is never assessed for Superhost). Compatible.
- Triggers/eligibility/time anchors: redecision is `state_due` after an approved account_suspension appeal; travel credit `state_due` on a completed run; enrollment and re-rating `on_request`. The 12-month / 6-month / 3-month windows are all defined as "records dated fewer than that many whole calendar months before the date of" the decision / credit / enrollment, consistently; the re-rating's day-count windows (backdate_days / backdate_window_days) are calendar days. No conflicting anchors.
- Terminal states: redecision -> host_accounts.variant_name (Superhost | Standard Host) + superhost_since + last_tier_change_date; enrollment -> variant_name (Professional Host Plus | Professional Host) + last_tier_change_date; credit -> one host_travel_credit_issued row; re-rating -> one host_service_fee_refunded row per stay. No two policies write the same field with different values in one world.
- Cross-category read boundaries: credit reads rewards (holding variant/status); enrollment reads listing (listings, listing_events, listing_reinstatement_requests); re-rating reads listing (listings) and protect (protection_plans). All read-only, all declared in `cross_category`.
- **Base/extended conflict that is NOT declared**: see finding D-1 below (variant `entry_gate`, `parameter_schema` meanings and the base measure `host_msr_consecutive_met_quarters` still state the base thresholds the extended policies relax).
- Claimed scope vs difficulty claim: blueprint `difficulties[host_standing_and_penalties].claim.event_types` = [host_cancellation_recorded, host_cancellation_penalty_charged, host_cancellation_penalty_waived, host_service_fee_refunded, host_restriction_lifted, host_account_reinstated, host_account_deactivated, host_tier_updated, host_taxpayer_info_updated]. Extended subjects used: host_tier_updated (x2), host_service_fee_refunded — inside the claim — and **host_travel_credit_issued, which is in no difficulty's claim** (blueprint.yaml lines 29/56/83/109/133). See observation D-O1.
- Scopes of the M=2 tasks: task 0 = {host_ext_superhost_redecision, host_ext_superhost_travel_credit}; task 1 = {host_ext_professional_plus_enrollment, host_ext_professional_fee_rerating} (derived from the prerequisite graph and the views; to be compared against `charter_scope` after reveal). Pairwise disjoint; jointly they cover all 4 extended policies. Seven of the nine claimed event types (cancellation recorded/charged/waived, restriction lifted, reinstated, deactivated, taxpayer info) are touched by no extended policy (observation D-O2).

### rule_compute_equivalence

host_ext_superhost_redecision — every binding has a verbatim `compute_basis` quotation that is a sentence fragment of the `rule`: asmt_* (recorded metrics of the LATEST host_superhost_assessed row), suspension_lifted_on/suspension_days ("counted from its suspended date to the date its account_suspension appeal was approved"), strikes_overturned ("policy strike overturned on a policy_strike appeal approved within the 12 months before the decision"), response_floor (3-tier), met_assessments_12m / response_sum_12m / assessments_12m / response_sum_6m / assessments_6m / response_figure (3-tier), stays_requirement (3-tier), met_assessments_all / rating_floor (3-tier), stays_met, standards_met, result. Sweep back: every rule sentence is implemented, except the eligibility-only sentences (deferral "recorded with its metrics and without an outcome"; "decided at once" after the approved suspension appeal), which are triggers, not quantities. Each factor ladder tier is a rule sentence and a branch of its `decides` binding. PASS, with observation D-O3 (RND is Python `round`, i.e. half-to-even on binary floats, while the rule says "rounded half up"; no value in either world lands on a half-cent).

host_ext_superhost_travel_credit — bindings tier_credit, earlier_credits/base_amount, completing_nights/stays_bonus_rate, completing_stays/run_stays_sum/run_assessments/suspension_lifted_on/run_suspension_days/stays_counted, met_response_*/response_bonus, rewards_tier/rewards_bonus, met_rating_*/rating_bonus, credit_total, result each quote the rule. Sweep back: **the rule sentence "When the run reaches superhost_credit_consecutive_quarters assessments, the host earns one travel credit for the run" has no binding** — `result` gates only on `tier_credit > 0`, never on the run length (observation D-O4: rule promise not implemented in compute; in task 0's world the run is exactly 4, so no scored consequence is demonstrable). `credit_total` rounds the stays bonus separately (`RND(stays_bonus_rate * stays_counted, 2)`) while the rule rounds only the sum; rates and stays are integral, so no divergence is reachable. Ladders all present in rule and compute. PASS with D-O4.

host_ext_professional_plus_enrollment — listed/snoozed/live_count_std, pending_reinstatements/live_count (3-tier), home_villa_live/live_requirement (3-tier), new_listings, rated_sum/count 3m/6m, all_sum/count_3m, listing_rating (3-tier), warnings_12m/suspensions_12m/rating_floor (3-tier), qualifies_plus, result: all quoted. Sweep back: rule's "Enterprise Partner is never reached by an enrollment" is honoured by `result` (Plus | Professional Host only). Minor: live_count tier 2 compute `MONTHS(F('restricted_until'), NOW) < 12` also admits a restricted_until in the future (negative months), while the rule says "falls within the 12 months before the enrollment"; unreachable in task 1 (restricted_until empty). PASS.

host_ext_professional_fee_rerating — stay_ref/stay_checkin/stay_fee/stay_fee_refunded/stay_base (the LATEST host_service_fee_assessed stay), tier_pct, moved_on, qualifying_date, in_effect (3-tier tier start), start_pct (3-tier), account_months/tenure_discount, live_listings/instant_live/instant_discount, plus_plans/standard_plans/cover_discount, rerated_pct, rerated_fee, result (gate `in_effect and tier_pct < fee/base`). Sweep back: "one refund for each stay, the most recently assessed stay first" — compute computes only the most recent stay; any further stay would need a re-evaluation per stay (acceptable for a one-stay world; noted as observation D-O5). PASS.

### action_binding_and_uuids

- (target_tool, computes): (apply_superhost_decision_f25b833f, variant_name), (claim_superhost_travel_credit_0d8c95c2, amount), (enroll_professional_tier_a874e389, variant_name), (refund_rerated_host_fee_9248fd19, amount) — each claimed by exactly one policy. PASS.
- uuid8s f25b833f, 0d8c95c2, a874e389, 9248fd19: no shared prefix, no sequence, no adjacent values; each frozen with its tool. PASS.
- Docstrings name no other tool and state no position in a sequence. Each contains "Afterwards the host account shows ..." describing its own call's post-state (not a cross-action order) — observation only.
- Function bodies: none reads a policy condition, aggregates history or refuses a call; `claim_*` and `refund_*` only look up customer_id; the two tier tools only `ctx.update`. The tool layer judges no prerequisite. PASS.
- Observation D-O6: both tier-setting docstrings (`apply_superhost_decision_f25b833f`, `enroll_professional_tier_a874e389`) enumerate all six tiers as acceptable `variant_name` values, including tiers their policies never produce (e.g. the agent-owned Superhost tool lists "Professional Host Plus when the account moves into the professional programme"). The policy text resolves which write may set which tier ("moves into Professional Host Plus only when the host enrolls it in person"), so no second solution is demonstrated; the docstring breadth is recorded only.

### prerequisite_graph

- Every extended policy has `prerequisite` filled ([] for redecision and enrollment). Edges: travel_credit -> redecision; rerating -> enrollment. Both `problem` ids are extended policies of this file, not base, not self. Acyclic (two disjoint 2-node chains).
- Edge travel_credit -> redecision: `policy_source` "The travel credit for a run is fixed only after the account holds the host tier that its most recent Superhost assessment earns it." is verbatim in the travel-credit rule (sentence 4). form=state, no fallback_reason (correct). kind=value_input, gate=tier_credit — a binding that exists (`tier_credit: P('superhost_travel_credit_usd')`). resolved_by = apply_superhost_decision_f25b833f = redecision's target_tool; its effect (variant_name -> Superhost) makes P('superhost_travel_credit_usd') go 0.00 -> 100.00, exactly the stated `effect`. Condition matches the sentence's strength. PASS.
- Edge rerating -> enrollment: `policy_source` "A host service fee is not re-rated until the account holds the professional tier that its live listings and listing ratings qualify it for." verbatim in the re-rating rule (sentence 2). form=state, no fallback_reason. kind=value_input, gate=tier_pct (exists: `P('host_service_fee_pct')`). resolved_by = enroll_professional_tier_a874e389 = enrollment's target_tool; effect (variant_name -> Professional Host Plus, last_tier_change_date -> today) changes tier_pct 15.50 -> 15.00 and moved_on. Observation D-O7: the `condition` adds "and host_accounts.last_tier_change_date is the date of that move", which the sentence does not say; it is a necessary by-product of any move, so it neither strengthens nor weakens the gate in any reachable world.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any prerequisite field. PASS.

### prerequisite_sentences

Four-point test:

1. "The travel credit for a run is fixed only after the account holds the host tier that its most recent Superhost assessment earns it." — ordering connective "only after"; waited-on state "the account holds the host tier that its most recent Superhost assessment earns it" is record-visible (host_accounts.variant_name vs the newest host_superhost_assessed row) with no action, performer or tool; no tool name, policy id, snake_case token or row id; scope = the most recent assessment, matching `condition`. PASS.
   Derivation (single reading): the newest assessment row may carry no outcome (redecision rule: "recorded with its metrics and without an outcome"); which policy's write makes the tier equal what that assessment earns? Only the redecision rule says "that assessment is decided at once on its recorded metrics, and the account's tier is set by the decision"; the enrollment rule concerns Professional Host accounts only. One write: apply_superhost_decision_f25b833f.
2. "A host service fee is not re-rated until the account holds the professional tier that its live listings and listing ratings qualify it for." — connective "not ... until"; state "the account holds the professional tier that its live listings and listing ratings qualify it for" (host_accounts.variant_name vs the enrollment computation over listings / quality assessments); no tool/id/snake_case. PASS.
   Derivation: which write sets a professional tier from live listings and listing ratings? The enrollment rule ("An enrollment places the account in Professional Host Plus when its live-listing count is at least its live-listing requirement and its listing rating is at least its rating floor"; "moves into Professional Host Plus only when the host enrolls it in person"). One write: enroll_professional_tier_a874e389 (owner user).
- Depended-on rules do not restate either sentence (redecision rule never mentions the credit; enrollment rule never mentions re-rating). PASS.
- Second wordings of the same dependency inside the blocked rules (observation D-O8, no divergent reading demonstrated):
  - travel credit rule: "whether the host earns it is decided by the tier the account holds after the decision on the completing assessment" (action form, "after the decision") and "an assessment ... later decided as met counts as met";
  - re-rating rule: "When an account moves into a professional tier whose host_service_fee_pct is lower than the percentage its stays were assessed at, the host service fee on each stay assessed on or after the tier start is re-rated" (action form, "moves into").
  Both are the `replaced_by` texts of declared overrides and point at the same single write as the state-form sentence, so they yield the same resolving action.
- Undeclared cross-problem order: the redecision rule's "Once the suspension is lifted on an approved account_suspension appeal, that assessment is decided at once" orders the decision after the base reinstatement (host_account_reinstated, base policy host_evt_appeals_and_reinstatement), which has no task tool and no extended policy in this charter. In task 0's world the reinstatement has already happened (status active), so no two orders are reachable; observation D-O9.

### override_declarations

Sentence-by-sentence sweep of each `base_policy_refs` entry (finding half only; demonstrations live in the task files):

host_ext_superhost_redecision
- host_tier_assignment: precedence sentence — followed (individual account). Starter graduation — not touched. "Individual Standard Hosts and Superhosts are assessed ... the assessment is met when ... superhost_alt_min_nights_12m" — **declared** (overwrite #2). "A met assessment promotes a Standard Host to Superhost; a not-met assessment demotes a Superhost to Standard Host; otherwise the tier is unchanged" — compatible ("any other decision leaves the account a Standard Host"). "Superhost is lost at once on suspension" — compatible. "A tier change applies to stays booked after it" — not touched.
- host_evt_appeals_and_reinstatement: "it does not restore Superhost status, which returns only through a later met assessment" — **declared** (overwrite #1). Appeal window / approval sentences — followed (the decision waits on the approved account_suspension appeal).
- host_evt_strikes_and_suspension: "ends Superhost status", "A strike overturned by an approved policy_strike appeal no longer counts" — compatible.
- **Not declared**: (a) `variants[Superhost].entry_gate: {quarterly_assessment: met, min_avg_rating: 4.80, min_response_rate_pct: 90.00, max_cancellation_rate_pct: 1.00, min_stays_12m: 10, or_min_stays_and_nights_12m: [3, 100]}`; (b) `parameter_schema` meanings "superhost_min_avg_rating: decimal stars, lowest average guest rating for Superhost", "superhost_min_response_rate_pct: decimal percent, lowest message response rate for Superhost", "superhost_min_stays_12m: int, completed stays in the lookback needed for Superhost"; (c) base event field `host_superhost_assessed.assessment_outcome: met or not_met` (the extended rule introduces an assessment "without an outcome"). The extended decision awards Superhost below each of (a)/(b) — rating floor 4.75/4.78, response floor 85/88, stays requirement 8/9. → finding D-1.

host_ext_superhost_travel_credit
- host_evt_superhost_travel_credit: "A Superhost whose run ... receives one Roamhaven travel credit of superhost_travel_credit_usd, and the run then restarts." — **declared** (#1). "Only a tier whose superhost_travel_credit_usd is above 0.00 earns the credit" — kept verbatim. "a host who is not a Superhost on the day of the completing assessment earns nothing for the run" — **declared** (#2). "issued once per completing assessment, is not cash, never paid to a payout method" — kept.
- host_tier_assignment — nothing touched.
- **Not declared**: (a) base measure `host_msr_consecutive_met_quarters` ("number of consecutive host_superhost_assessed rows with assessment_outcome met counted back from the newest"), still listed under base `host_evt_superhost_travel_credit.measures`; the extended run counts a row whose recorded outcome is `none` "later decided as met" as met; (b) `parameter_schema` "superhost_travel_credit_usd: decimal USD, Roamhaven travel credit issued after the required consecutive met assessments", which the extended re-reads as only the "standard base amount". → finding D-1.

host_ext_professional_plus_enrollment
- host_tier_assignment: "Professional Host Plus for an account with at least professional_plus_min_live_listings live listings and an average guest rating of at least professional_plus_min_avg_rating" — **declared** (#1). "The tier of a host account is decided in this order of precedence, the first that applies winning" — **declared** (#2); observation D-O10: replacing only the lead clause leaves the rest of that base sentence (the tier list "Enterprise Partner for ...; Professional Host Plus for ...; Professional Host for ...; then ... Superhost, Standard Host or Starter Host") without its governing clause; merged semantics for tiers other than Plus is not restated. No task exercises it.
- **Not declared**: `variants[Professional Host Plus].entry_gate: {live_listings_at_least: 25, min_avg_rating: 4.70}` and `parameter_schema` "professional_plus_min_live_listings: int, live listings needed for Professional Host Plus", "professional_plus_min_avg_rating: decimal stars, lowest average guest rating for Professional Host Plus". The enrollment places an account into Plus with a live-listing requirement of 14/19 and a rating floor of 4.60/4.65. → finding D-1.

host_ext_professional_fee_rerating
- host_evt_service_fee: "assessed once per stay at check-in on the host-fee base ..." — kept. "The percentage is host_service_fee_pct of the account's tier when the stay's fee_structure equals the tier's fee_structure" — **declared** (#1). Observation D-O11: the replaced_by ("The re-rated fee is the stay's host-fee base as assessed times the re-rated percentage") speaks of the re-rated fee, not of the assessment; superseding the assessment-percentage clause leaves the original assessment percentage for same-structure stays unstated in the merged charter. The re-rating reads the historical percentage from the record ("the fee assessed divided by the stay's host-fee base"), so no task value depends on it. "split_fee_host_pct / host_only_fee_default_pct" — not touched. "When guest refunds funded_by host are issued after the payout release ... never exceeds the fee assessed on the stay" — compatible (re-rating subtracts fee already refunded, floors at 0). "A stay cancelled ... never assessed" — not touched.
- host_tier_assignment: "A tier change applies to stays booked after it" — **declared** (#2); "stays already booked keep the fee_structure frozen on them" — kept (both tiers host_only_fee).
- Observation D-O12: base event `host_service_fee_refunded.fee_base_amount: "the host-funded amount refunded to the guest"` vs the re-rating tool's `fee_base_amount: "the stay's host-fee base the re-rated percentage was applied to"`; not named in any overwrite. In a re-rating there is no guest refund, and the tool requires a positive value, so a reader following the base field meaning has no positive value to pass; recorded as observation (no defensible second value).

Disguised forms: no anonymous intermediate factor found (all deviations sit in named bindings); no 0/1 multiplier zeroing a base amount except the declared `tier_credit > 0` gate, which is the base sentence kept verbatim; no dropped base branch.

### factor_ladders

| policy | factor | effect | decides | tiers (values / methods) | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| redecision | suspension_response_floor | parameter | response_floor | 85.00 / 88.00 / 90.00 | yes (suspension span: host_accounts.suspended_date + account_suspension appeal decided_at; AND policy_strike appeal) | — |
| redecision | response_figure_window | method | response_figure | 12-month average of all assessments / 6-month average / the assessment's own figure | no | — |
| redecision | stay_length_stays_requirement | parameter | stays_requirement | 8 / 9 / 10 | no | — |
| redecision | tenure_rating_floor | parameter | rating_floor | 4.75 / 4.78 / 4.80 | no | — |
| credit | earlier_credits_base_amount | parameter | base_amount | 1.50x / 1.25x / 1.00x tier credit | no | — |
| credit | nights_stays_bonus_rate | parameter | stays_bonus_rate | 3.00 / 2.00 / 1.00 | no | — |
| credit | suspension_stays_counted | method | stays_counted | 12-month average excluding completing assessment / 12-month average of all / completing assessment's stays | yes (suspended_date window AND suspension span from appeal) | — |
| credit | met_response_bonus | parameter | response_bonus | 25 / 10 / 0 | no | — |
| credit | rewards_membership_bonus | parameter | rewards_bonus | 40 / 20 / 0 | no | rewards |
| credit | met_rating_bonus | parameter | rating_bonus | 20 / 10 / 0 | no | — |
| enrollment | pending_reinstatement_live_count | method | live_count | listed+snoozed+pending requests / listed only / listed+snoozed | partly (tier 2: no pending request AND restricted_until window) | listing |
| enrollment | portfolio_mix_live_requirement | parameter | live_requirement | 14 / 19 / 25 | yes (business_name AND listing mix) | listing |
| enrollment | new_listing_rating_window | method | listing_rating | 3-month pass/warning avg / 6-month pass/warning avg / 3-month all-outcome avg | no | listing |
| enrollment | quality_record_rating_floor | parameter | rating_floor | 4.60 / 4.65 / 4.70 | yes (warning count AND suspension count) | listing |
| rerating | qualifying_date_tier_start | method | in_effect | tier start = qualifying date / move − 30 days / move date | no | listing |
| rerating | booking_size_start_pct | parameter | start_pct | 14.50 / 14.75 / tier pct | no | — |
| rerating | account_tenure_discount | parameter | tenure_discount | 0.25 / 0.10 / 0 | no | — |
| rerating | instant_book_discount | parameter | instant_discount | 0.20 / 0.10 / 0 | no | listing |
| rerating | hostcover_discount | parameter | cover_discount | 0.15 / 0.05 / 0 | yes (protection_plans levels vs listings count) | protect |

- Counts per computation: redecision 4 (3 parameter, 1 method); credit 6 (5 parameter, 1 method); enrollment 4 (2 parameter, 2 method); re-rating 5 (4 parameter, 1 method). All within 4–6, >= 2 parameter, >= 1 method.
- Per task (by the derived scopes): task 0 — multi-source yes (suspension_response_floor, suspension_stays_counted), cross_difficulty rewards (rewards_membership_bonus); task 1 — multi-source yes (portfolio_mix_live_requirement, quality_record_rating_floor, hostcover_discount), cross_difficulty listing and protect.
- Every ladder has exactly 3 tiers, pairwise disjoint as stated; no two tiers of one ladder share a value or method; every `decides` is an input binding, never `result`; binding sets are pairwise disjoint within each policy; each tier (condition + value/method) is stated in the `rule` and implemented by a branch of the `decides` binding; each fall-through equals the policy's `baseline` for that input; every `baseline` value is what `baseline.rule` states (standard floor/figure/requirement, tier credit, stays_bonus_rate_standard x completing stays, no bonus, listed+snoozed, professional_plus_min_*, 3-month all-outcome average, move date, tier pct, no discount).
- Labels: the `method` factors change the algorithm (which records are averaged / which records make the count / which anchor supplies the tier start). Observation D-O13: `qualifying_date_tier_start` tiers 2 and 3 differ only by a constant offset of the anchor (move − 30 days vs move date); the ladder is still a method because tier 1 sources the anchor from another record (the listing's first_listed_date). Not a mislabel by itself.
- Business reality of conditions and outcomes: every condition divides the customers that reach the write (none is universal); the redecision's "at least 1 but fewer than long_suspension_days" range has a universally true lower bound (any account whose assessment fell inside a suspension was suspended for >= 1 day) but the range as a whole is not universal. Realism observations (no RED demonstrated, but recorded because the brief makes scenario realism a stated priority):
  - D-O14: the redecision stacks three reliefs (rating floor, response floor/figure, stays requirement) so that an account failing every published Superhost standard except cancellation (task 0: 4.77 < 4.80, 76 < 90, 9 < 10 and 76 < 100 nights) is awarded Superhost; each relief alone is a defensible platform policy (Airbnb's own alternative route of 3 stays + 100 nights embodies the stay-length idea), but no platform publishes a Superhost decision that waives all three published standards at once, and the charter's own `entry_gate` and `parameter_schema` contradict it (D-1).
  - D-O15: the enrollment stacks a halved live-listing requirement (14 vs 25 for a business whose Entire Home/Luxury Villa share is >= 50 %), counting registration-suspended listings with undecided reinstatement requests as live, dropping not_assessed ratings and lowering the floor to 4.60 for a clean record; together they admit a ~12-live-listing portfolio into a programme the charter itself defines as "for large, highly rated portfolios" with "live listings needed for Professional Host Plus: 25".
  - D-O16: the re-rating's tenure, Instant Book and HostCover discounts and booking-size percentages apply only to retroactively re-rated stays, so a re-rated stay ends below the new tier's own published host_service_fee_pct (task 1: 14.15 % vs Professional Host Plus 15.00 %) while every later stay of the same account pays 15.00 %; internally consistent as written, but an unusual economic shape for a platform fee schedule.
  - D-O17: the quality_record_rating_floor fall-through ("standard" 4.70) is in practice the treatment of accounts with a quality suspension in the last 12 months, while every clean account gets 4.60; the published standard is thus not what the ordinary customer gets. A business could publish this as a clean-record relief, so recorded only.

### findings

**D-1 — SOURCE-POLICY RED (undeclared override of base charter content; bears on task 0 and task 1)**
- Symptom: the base section of the extended charter still states, in structured form outside any policy sentence, the very thresholds the extended policies relax, and no `overwrite` names them.
- Root cause: the overwrite mechanism was applied to the policy-rule clauses only (host_tier_assignment, host_evt_superhost_travel_credit), while the same content also lives in `variants[].entry_gate`, `parameter_schema` meanings and the base measure `host_msr_consecutive_met_quarters`, all of which are base charter text rendered with the policy.
- Evidence (verbatim, host.extended.yaml):
  - L218 `entry_gate: {quarterly_assessment: met, min_avg_rating: 4.80, min_response_rate_pct: 90.00, max_cancellation_rate_pct: 1.00, min_stays_12m: 10, or_min_stays_and_nights_12m: [3, 100]}` (Superhost)
  - L62 `superhost_min_avg_rating: "decimal stars, lowest average guest rating for Superhost"`; L63 `superhost_min_response_rate_pct: "decimal percent, lowest message response rate for Superhost"`; L65 `superhost_min_stays_12m: "int, completed stays in the lookback needed for Superhost"`
  - L70 `superhost_travel_credit_usd: "decimal USD, Roamhaven travel credit issued after the required consecutive met assessments; 0.00 where not a perk"`
  - L708–710 `host_msr_consecutive_met_quarters ... measure: number of consecutive host_superhost_assessed rows with assessment_outcome met counted back from the newest, restarting after each travel credit issued`; L660 `assessment_outcome: met or not_met`
  - L336 `entry_gate: {live_listings_at_least: 25, min_avg_rating: 4.70}` (Professional Host Plus); L76 `professional_plus_min_live_listings: "int, live listings needed for Professional Host Plus"`; L77 `professional_plus_min_avg_rating: "decimal stars, lowest average guest rating for Professional Host Plus"`
  - versus the extended rules: redecision "The decision's rating floor is rating_floor_long_tenure for an account with at least long_tenure_met_assessments Superhost assessments recorded as met ..." (4.75), "The decision's response floor is response_floor_long_suspension_pct ..." (85.00), "The decision's stays requirement is stays_requirement_long_stays ..." (8); enrollment "The live-listing requirement of an enrollment is live_requirement_home_heavy ..." (14), "The rating floor of an enrollment is rating_floor_clean ..." (4.60); credit "an assessment recorded without an outcome during a suspension and later decided as met counts as met", "The travel credit is the sum of its base amount and its stays bonus ..." .
- Demonstrated consequence: in the same situation the two passages reach different conclusions — demonstrated per task in `task_0.md` (Superhost vs Standard Host; credit vs no credit) and `task_1.md` (Professional Host Plus vs Professional Host; refund vs no refund).
- Affected artifact/location: `host.extended.yaml` — the `overwrite` lists of host_ext_superhost_redecision, host_ext_superhost_travel_credit and host_ext_professional_plus_enrollment (none names these base items); base `variants[Superhost|Professional Host Plus].entry_gate`, `parameter_schema` L62/63/65/70/76/77, `measures[host_msr_consecutive_met_quarters]`, `events[host_superhost_assessed].fields.assessment_outcome`.
- Relation to previous revisions: first audit of this difficulty.

Observations (no consequence demonstrated; not grounds for rework by themselves):
- D-O1 scope: host_ext_superhost_travel_credit's subject `host_travel_credit_issued` is outside this difficulty's claimed event_types (and outside every difficulty's claim); check_cross_fire reports SCOPE OK, so it collides with no sibling.
- D-O2 coverage: 7 of 9 claimed event types have no extended policy (expected with M=2).
- D-O3 RND is half-to-even on binary floats; rules say half up. No half-cent value reached.
- D-O4 the run-length condition of the credit is not implemented in compute.
- D-O5 the re-rating compute handles only the most recently assessed stay.
- D-O6 tier-tool docstrings enumerate all six tiers.
- D-O7 re-rating edge `condition` adds last_tier_change_date.
- D-O8 second (action-form) wordings of each declared dependency inside the blocked rules.
- D-O9 redecision rule orders the decision after a base reinstatement with no edge.
- D-O10 precedence lead clause replaced without restating the remaining tier list.
- D-O11 the assessment-percentage clause of host_evt_service_fee is superseded by a re-rating sentence.
- D-O12 base meaning of host_service_fee_refunded.fee_base_amount differs from the re-rating tool's.
- D-O13 tier-start ladder tiers 2/3 differ by a constant offset.
- D-O14 – D-O17 realism of stacked reliefs and of the re-rating discount schedule (see factor_ladders).

## closing_checklist

Written 2026-10-07 after both reveals; everything above this heading was frozen before any reveal (sha256 of this file at freeze: 0ce7850f7e5e4cb78808842a2a3881af0ba1ce9bd2934ab231a405c8afa703b4, recorded 2026-10-07T19:21:25Z). Timestamp correction: the "freeze time 19:20Z" above was an estimate; the hash record is the true freeze.

**Status: NOT CLOSED.** Step 4 requires every task to PASS all four relationships; both tasks carry SOURCE-POLICY RED from D-1.

| item | state |
| --- | --- |
| per-task files 1:1 with tasks, `_difficulty.md` alongside | yes: `task_0.md`, `task_1.md`; first revision, no older revision to preserve |
| every comparison section PASS | no — task 0 and task 1: SOURCE-POLICY RED (D-1); all other relationships PASS; blind derivations agree with GT on every scored value |
| extended policies fully covered; scopes pairwise disjoint | yes — task 0 {redecision, travel_credit}, task 1 {enrollment, rerating}; matches each `charter_scope` |
| task tools / GT closed; uuid8s independent and frozen | yes (§ action_binding_and_uuids) |
| each tree: 1–3 prerequisites, ≥ max(n−1,1) value_input, ≥1 owner=user, acyclic; difficulty graph a DAG | yes — each tree n = 1, 1 value_input edge, user write present (task 0 root claim; task 1 enrollment); two disjoint edges |
| every computation: self-sufficient baseline, 4–6 factors (≥2 parameter, ≥1 method), per task ≥1 multi-source and ≥1 cross-difficulty, ladders ≥3 tiers stated in full, distinct outcomes, every factor bears weight, whole baseline definite and ≠ gold | yes on structure and weight (baseline fall-backs: Standard Host, 109.00, Professional Host, 0.00); realism of stacked reliefs recorded as D-O14–D-O17, not RED |
| instantiation gates re-run on the final form | not re-run by the auditor (Step 0: cited only); last snapshot: all green except check_traceability (expected NOT OK before KB render) and check_cache_diff (INFO) |

Open finding blocking close: **D-1** (undeclared override of base `entry_gate` / `parameter_schema` / measure text), demonstrated in `task_0.md` § findings T0-1 and `task_1.md` § findings T1-1.

---

## revision_2

### charter_global_frozen (revision_2)

- auditor: erl-task-policy-audit (same independent auditor as round 1; not the reworker)
- clock: inputs hashed 2026-10-07T21:20:38Z; this section written 2026-10-07T21:27Z, before any round-2 task JSON was opened
- inputs (sha256 verified against the coordinator's list):
  - `host.extended.yaml` f59f802cc1609989d71b75f038bc72760d5e13132da437a31103a3541f93c180 (round 1: bfe6e9be…c064cf1573b) — **changed**, so every charter-global section is re-derived in full below
  - `task_tools.py` 23e4adf04caa62ab5a9ea27f521897c67647ded4be8ed9bf1d754232fa97b2ff (round 1: 0a815c03…dde860ad4e1b4a7) — **changed**
  - views `/tmp/erl45_views/r2/host_standing_and_penalties/task_0.view.json` 3a4ac056…a9aeb1, `task_1.view.json` c1d5de0a…a7355c
  - base layer: the base section of the extended charter (lines 1–1055) is byte-identical to `blueprint/products/host.yaml` (diff shows only the trailing blank line), so the base copy is verbatim.
- masked and unread at this point: `tasks/*.json` (round 2), `tasks/host_standing_and_penalties/worklog.md`, the reworker's notes beyond the item-id list in the brief.
- contamination_disclosure: this auditor read the round-1 GT of both tasks during round 1 (recorded in the round-1 `source_gt_comparison` sections). The round-2 worlds and policies differ (new seed figures, new factor ladders, new tool signatures), so the round-2 derivations are recomputed from the round-2 charter and views; the round-1 conventions (step layout, near-miss intent) are known to the auditor and are disclosed as prior exposure, not as a source.
- Entry conditions: gate snapshot supplied (`/tmp/erl45_views/r2/host_standing_and_penalties/gate_snapshot.txt`): all OK except check_traceability NOT OK (expected before `docs/` render) and check_cache_diff INFO. Met.

### policy_conflict_scan (revision_2)

- Same four extended policies, same subjects, target tools, owners and prerequisite edges as round 1 (travel_credit → redecision; rerating → enrollment). Subject overlap on host_tier_updated is still separated by object (individual Superhost decision vs Professional Host enrollment), and the tool enums now enforce the same split (see action_binding_and_uuids).
- Thresholds: the redecision compares its figures with the published `superhost_min_avg_rating` 4.80, `superhost_min_response_rate_pct` 90.00, `superhost_max_cancellation_rate_pct` 1.00, `superhost_min_stays_12m` 10 / alt 3 + 100 nights; the enrollment compares with `professional_plus_min_live_listings` 25 and `professional_plus_min_avg_rating` 4.70. These equal the base `variants[Superhost].entry_gate` and `variants[Professional Host Plus].entry_gate` values. What the extended policies now redefine is the figure compared (rating / response / stays figure; live-listing count; listing rating), and that redefinition sits inside the base clauses each policy declares superseded (host_tier_assignment's met-criteria clause, which named the measures host_msr_avg_rating_365d / host_msr_completed_stays_365d; its Professional Host Plus clause).
- Scopes: unchanged and disjoint (task 0 {redecision, travel_credit}; task 1 {enrollment, rerating}); D-O1 (host_travel_credit_issued outside every difficulty claim) and D-O2 (7 of 9 claimed event types untouched) unchanged, as the reworker states.

### rule_compute_equivalence (revision_2)

- redecision: every binding (asmt_*, suspension_lifted_on, suspension_days, lookback_suspension_days, strikes_overturned, decided_rate, met_assessments_12m, response_sum/assessments 12m/6m, response_figure, met_assessments_all, rating_sum/count 12m/6m, rating_figure, stays_sum_6m, stays_count_6m, stays_figure, stays_met, standards_met, result) quotes a rule sentence; the sweep back finds every quantity sentence implemented. Note: `stays_figure` tier 1 is computed as `MX(asmt_stays, stays_sum_6m − asmt_stays)`, which equals "the larger of ... the decided assessment and ... the assessment before it, the other assessment dated within the 6 months" only when the 6-month window holds exactly two assessments; on the quarterly schedule a 6-month window ("fewer than 6 whole months") always holds exactly two, so no divergence is reachable. PASS.
- travel credit: D-O4 closed — the rule now states "the credit for an incomplete run is 0.00" and `result` gates on `met_run >= superhost_credit_consecutive_quarters`. The rule carries two run definitions (consecutive met assessments back from the newest restarting after each credit, via host_msr_consecutive_met_quarters; and "on the quarterly assessment schedule a run is complete when the account's Superhost assessments recorded as met and dated within the 12 months before the credit number at least superhost_credit_consecutive_quarters"); on a quarterly schedule a 12-month window holds at most four assessments, so the two coincide whenever the run can complete; observation R2-O1 (no divergent world reachable from a quarterly seed). PASS.
- enrollment: listed/snoozed/live_count_std, pending_reinstatements/live_count (tier 2 now bounded `0 <= MONTHS < 12`), account_months/rating_window, warnings_12m/suspensions_12m/na_weight, the per-window sums and counts, round1–3 num/den, pooled / per-round / latest-round ratings, new_in_window, listing_rating, qualifies_plus, result: all quoted; "rounded half up to 2 decimal places only at the end" implemented by a single RND. PASS.
- rerating: unchanged bindings; the restated assessment-percentage sentence and "booked with no host-funded guest refund behind it" are quoted. PASS.
- D-O3 (RND is half-to-even on binary floats) unchanged; no half-cent value is reached in either round-2 world (83.19088…, 90.6725, 4.70485…, 489.59 exactly).

### action_binding_and_uuids (revision_2)

- (target_tool, computes) pairs and uuid8s unchanged and unique (f25b833f, 0d8c95c2, a874e389, 9248fd19). PASS.
- Signatures changed: `apply_superhost_decision_f25b833f(host_account_id, assessment_event_id, assessment_outcome, tier_change, variant_name)` now also writes `assessment_outcome` and `tier_change` onto the decided assessment row (task_tools.py L50–52); `refund_rerated_host_fee_9248fd19(host_account_id, stay_id, amount)` no longer takes `fee_base_amount` and writes 0.0 (L166–171).
- D-O6 / T1-O3 closed: the Superhost tool's `variant_name` enum admits only Superhost / Standard Host ("Professional Host Plus never, for the same reason"); the enrollment tool admits only Professional Host / Professional Host Plus. Exactly one tool can set each tier the policies produce.
- Bodies still check nothing and refuse nothing (pure `ctx.update` / `ctx.create`). PASS.
- Docstrings still say "Afterwards ... shows" of their own post-state; no other tool is named and no cross-action order is stated (observation, unchanged).

### prerequisite_graph (revision_2)

- Edges, kinds, gates, forms, resolved_by unchanged; acyclic. D-O7 closed: the rerating edge's `condition` no longer adds last_tier_change_date and now reads "Professional Host Plus when its live-listing count and listing rating meet professional_plus_min_live_listings and professional_plus_min_avg_rating".
- travel_credit edge: condition "host_accounts.variant_name equals the tier that the decision recorded on the account's most recent host_superhost_assessed record gives it (Superhost when that record's assessment_outcome is met); an assessment that fell inside a suspension later overturned carries that decision only once it has been decided again on its metrics." effect now also states that the decided assessment is recorded as met, so `met_run` reaches 4. Both match the tool effect (row outcome + tier). PASS.

### prerequisite_sentences (revision_2)

- Both `policy_source` sentences unchanged, verbatim in their blocked rules, four-point test PASS as in round 1.
- Single-write resolution: travel credit — the only write that records a decision on an assessment and sets Superhost is apply_superhost_decision_f25b833f (enrollment enum excludes Superhost). Rerating — the only write that sets Professional Host Plus is enroll_professional_tier_a874e389 (Superhost tool enum excludes it). PASS (stronger than round 1).
- D-O8 reduced: the blocked rules still restate their dependency once more, now in state form ("whether the host earns it is decided by the tier that the decision recorded on the completing assessment gives the account"; "When an account holds a professional tier whose host_service_fee_pct is lower ..."), pointing at the same single write; no action-form second wording remains. Observation only.
- D-O9 closed: the redecision rule now waits on a record state ("once its account_suspension appeal stands approved"), not on the reinstatement write.

### override_declarations (revision_2)

Sentence sweep per `base_policy_refs`:
- redecision vs host_tier_assignment: met-criteria clause declared (overwrite #2, now with figures compared against the unchanged published thresholds); "A met assessment promotes a Standard Host to Superhost; a not-met assessment demotes ..." compatible — the decision records `promoted` / `unchanged`; precedence, starter graduation, "lost at once on suspension" compatible. vs host_evt_appeals_and_reinstatement: "does not restore Superhost status, which returns only through a later met assessment" declared (#1). vs host_evt_strikes_and_suspension: compatible. Base event field `assessment_outcome: met or not_met` — now respected (the seed records the in-suspension assessment as `not_met`; the decision writes `met` / `not_met`; "none is never the outcome of a decision"). Base measure `host_msr_consecutive_met_quarters` — now used by the credit rule as written.
- travel credit vs host_evt_superhost_travel_credit: amount sentence declared (#1); "a host who is not a Superhost on the day of the completing assessment earns nothing" declared (#2); "Only a tier whose superhost_travel_credit_usd is above 0.00 earns the credit", dedup and not-cash sentences kept.
- enrollment vs host_tier_assignment: Plus clause declared with the base thresholds (#1); precedence lead clause declared and now restated ("follows the order of precedence of the tier assignment, except that ...") — D-O10 closed.
- rerating vs host_evt_service_fee: assessment-percentage clause declared and its assessment meaning restated (D-O11 closed); host-funded refund sentence compatible; base event field `host_service_fee_refunded.fee_base_amount` ("the host-funded amount refunded to the guest") now written as 0.0 by the tool, consistent (D-O12 closed). vs host_tier_assignment: "A tier change applies to stays booked after it" declared.

**Ruling on the reworker's open residue "D-1(b)"** (the credit amount departs from the base parameter meaning `superhost_travel_credit_usd: "decimal USD, Roamhaven travel credit issued after the required consecutive met assessments; 0.00 where not a perk"`): **PASS, recorded as observation R2-O2 — not SOURCE-POLICY RED.** Grounds:
1. The base policy sentence that fixes the credit amount ("receives one Roamhaven travel credit of superhost_travel_credit_usd") is declared superseded in overwrite #1 and replaced by the extended amount rule; the base policy layer therefore states no surviving amount rule that conflicts.
2. What remains is the `parameter_schema` description of a parameter that the extended rule uses as exactly that parameter: "The standard base amount is the tier's superhost_travel_credit_usd" (it is the policy's `baseline`, and the fall-through tier of `earlier_credits_base_amount`). This is the same relation every factor in this charter bears to the base parameter it modulates — e.g. the re-rating's re-rated percentage (14.15 % in task 1) against `host_service_fee_pct: "decimal percent of the host-fee base withheld as the host service fee on stays whose fee_structure equals this tier's fee_structure"`, which round 1 did not red-light either. Red-lighting a parameter description because a declared computation varies the quantity around it would red-light the factor design itself (baseline = base standard value, factors deviate), which the skill requires.
3. This narrows, and states the line of, the round-1 D-1 finding: round 1's RED rested on the extended policies **lowering the published thresholds themselves** (rating floor 4.75/4.78 and response floor 85/88 and stays requirement 8/9 against the Superhost `entry_gate` 4.80/90/10; live-listing requirement 14/19 and rating floor 4.60/4.65 against the Professional Host Plus `entry_gate` 25/4.70) — values stated in the tier definitions that no declared clause covered — and on the run measure / outcome enum the old credit rule bypassed. Round 1 listed the `superhost_travel_credit_usd` meaning inside D-1 as corroboration; on re-examination it does not carry a demonstrable conflict of its own beyond the declared amount override, and it is withdrawn from the RED. The withdrawal is made before any round-2 GT is read and does not depend on any GT value.
- The same line governs two related residues, both observations: R2-O3 — `parameter_schema` glosses such as `superhost_min_stays_12m: "completed stays in the lookback needed for Superhost"` and `max_active_listings: "most live (listed or snoozed) listings the account may hold"` describe the base measures, while the extended decision compares a stays figure that can come from the previous assessment, and the enrollment counts registration-suspended listings with undecided reinstatement requests in its live-listing count; both redefinitions sit inside the clauses declared superseded (which named those measures), and the thresholds compared are the published ones.

### factor_ladders (revision_2)

| policy | factor | effect | decides | tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| redecision | suspension_response_proration | method | decided_rate | prorate over all suspension days in the lookback / prorate over days beyond short_suspension_grace_days 3 / recorded rate | yes (suspension span from host_accounts + approved account_suspension appeal; AND approved policy_strike appeal) | — |
| redecision | run_response_window | parameter | response_figure | 12-month average / 6-month average / decided rate alone | no | — |
| redecision | tenure_rating_window | parameter | rating_figure | 12-month average / 6-month average / recorded rating | no | — |
| redecision | suspension_stays_figure | method | stays_figure | max(decided, previous) / floor(avg of the two) / recorded stays | no | — |
| credit | (unchanged six factors; response thresholds now 92 / 88, rating thresholds 4.90 / 4.85) | 5 parameter + 1 method | | | suspension_stays_counted | rewards |
| enrollment | pending_reinstatement_live_count | method | live_count | + pending registration reinstatements / listed only / listed + snoozed | partly | listing |
| enrollment | tenure_rating_window | parameter | rating_window | 9 / 6 / 3 months | no | — |
| enrollment | quality_record_not_assessed_weight | parameter | na_weight | 0.0 / 0.5 / 1.0 | yes (warning rows AND suspension rows) | listing |
| enrollment | new_listing_round_averaging | method | listing_rating | mean of per-round weighted averages / latest round alone / pooled weighted average | no | listing |
| rerating | (unchanged five factors) | 4 parameter + 1 method | | | hostcover_discount | listing, protect |

- Counts: redecision 4 (2 parameter, 2 method); credit 6 (5, 1); enrollment 4 (2, 2); rerating 5 (4, 1). Per task: task 0 multi-source (suspension_response_proration, suspension_stays_counted) and cross-difficulty rewards; task 1 multi-source (quality_record_not_assessed_weight, hostcover_discount) and cross-difficulty listing / protect. PASS.
- Every ladder has 3 tiers, pairwise disjoint, distinct outcomes; each tier is a rule sentence and a branch of its `decides`; each fall-through equals the `baseline`, and each `baseline` is what `baseline.rule` states (recorded rate; decided rate as the standard response figure; recorded rating; recorded stays; listed + snoozed; 3-month window; weight 1; pooled average). PASS.
- Labels: the two window factors (`run_response_window`, `tenure_rating_window` in the redecision) carry the same 12-month / 6-month / single-record shape that round 1 accepted as `method` for response_figure_window; selecting the averaging window is equally readable as a parameter (the window length), with the third tier the degenerate window holding only the decided assessment. Either label is defensible; no mislabel is demonstrated (observation R2-O4). The enrollment's `tenure_rating_window` (9 / 6 / 3 months) is a plain parameter. Factor id `tenure_rating_window` is used in two policies (observation, ids are per policy).
- Business reality: D-O14 is resolved in substance — the decision no longer lowers any published standard; it corrects the figures for days the host was suspended (prorated response rate, a 12-month rating average for long-tenured hosts, the better of two quarters' stays when ≥ 14 suspension days fall in the lookback), which is the kind of adjustment a platform makes after overturning a wrongful suspension. D-O15 is resolved in substance — the Plus threshold stays at 25 live listings and 4.70; the reliefs are counting listings held only by pending registration paperwork and down-weighting not_assessed ratings for a clean or warned record. D-O17's shape persists in the not_assessed weighting (the standard weight 1.0 applies in practice to accounts with a quality suspension in the last 12 months, while a clean account's not_assessed ratings weigh 0); a platform could publish this as benefit of the doubt for clean records — observation R2-O5. D-O16 (re-rated stay ends below the new tier's own rate) unchanged.

### findings (revision_2, charter-global)

- **D-1 — closed.** Thresholds now equal the published entry gates; the outcome enum and the run measure are respected; the remaining residue D-1(b) is ruled PASS (R2-O2 above). Per-task confirmation is in each task file's revision_2.
- No new charter-global RED found.
- Observations carried: D-O1, D-O2, D-O3, D-O5, D-O13, D-O16 (unchanged, as the reworker states); D-O8 (reduced); new R2-O1 (two coincident run definitions), R2-O2 (D-1(b) ruling), R2-O3 (parameter glosses vs redefined figures), R2-O4 (window-factor labels), R2-O5 (not_assessed weight fall-through).
- Closed observations: D-O4, D-O6, D-O7, D-O9, D-O10, D-O11, D-O12, D-O14, D-O15 (in substance), T1-O3 (via D-O6).

### closing_checklist (revision_2)

Written 2026-10-07 after both round-2 reveals (round-2 frozen hashes recorded 2026-10-07T21:27:55Z; `_difficulty.md` b2671254cad28b0526149d3efb3e684998154974c94b5b7c446382c49e37ee5f). Clock correction: the "written 2026-10-07T21:27Z" line in charter_global_frozen (revision_2) was an estimate; the clock read immediately after that section was written is 21:26:43Z.

**Status: CLOSED.** Both tasks PASS all four relationships in revision_2.

| item | state |
| --- | --- |
| per-task files 1:1, `_difficulty.md` alongside, old revisions preserved | yes — round-1 text untouched; revision_2 appended under `## revision_2` in all three files |
| every comparison section PASS | yes — task 0 PASS, task 1 PASS (revision_2); blind derivations equal GT on every scored value and every factor/baseline figure |
| extended policies fully covered; scopes pairwise disjoint | yes — task 0 {redecision, travel_credit}, task 1 {enrollment, rerating}, equal to each `charter_scope` |
| task tools / GT closed; uuid8s independent and frozen | yes — unchanged uuid8s; enums now partition the tiers between the two tier tools |
| each tree 1–3 prerequisites, ≥ max(n−1,1) value_input, ≥ 1 owner=user, acyclic; difficulty graph a DAG | yes — n = 1 each, one value_input edge each, user writes: task 0 claim, task 1 enrollment |
| every computation: self-sufficient baseline, 4–6 factors (≥ 2 parameter, ≥ 1 method), per task ≥ 1 multi-source and ≥ 1 cross-difficulty, ladders ≥ 3 tiers stated in full, distinct outcomes, real conditions/outcomes, every factor bears weight, whole baseline definite and ≠ gold | yes — whole baselines Standard Host / 109.00 / Professional Host / 0.00 against Superhost / 212.00 / Professional Host Plus / 46.71 |
| instantiation gates on the final form | cited, not re-run by the auditor: coordinator's round-2 snapshot on the final hashes — all OK; check_traceability NOT OK expected until `docs/` is rendered (to be re-run after step 3); check_cache_diff INFO |

Round-1 RED disposition: D-1 / T0-1 / T1-1 closed; residue D-1(b) ruled PASS (observation R2-O2, with grounds above). Open observations carried to the KB stage: D-O1, D-O2, D-O3, D-O5, D-O8 (reduced), D-O13, D-O16, T0-O2, T1-O1, R2-O1 – R2-O5.

---

## revision_3

### charter_global_frozen (revision_3)

- auditor: same independent auditor; clock read 2026-10-07T22:39:00Z at start, this section written ~22:40Z, before either round-3 task JSON was opened
- trigger: the coordinator's whole-scenario check (`/tmp/erl45_validate/validate_r1.txt`) rejected both tasks' frozen_time ('2026-10-06T10:15:00', '2026-10-06T14:30:00') under `erlbench/validate.py` L226–228 (`^\d{4}-\d{2}-\d{2}\b` — the `T` right after the day leaves no word boundary). There was no round-2 RED.
- inputs: `host.extended.yaml` f59f802cc1609989d71b75f038bc72760d5e13132da437a31103a3541f93c180 and `task_tools.py` 23e4adf04caa62ab5a9ea27f521897c67647ded4be8ed9bf1d754232fa97b2ff — **both identical to revision_2**; views `/tmp/erl45_views/r4/host_standing_and_penalties/task_0.view.json` 79ce2fab…54f24d0e, `task_1.view.json` b20d5711…573d1 (verified).
- Carry-forward: because both shared inputs are byte-identical to the round that produced them, every charter-global section of `## revision_2` (policy_conflict_scan, rule_compute_equivalence, action_binding_and_uuids, prerequisite_graph, prerequisite_sentences, override_declarations incl. the D-1(b) ruling, factor_ladders, findings) is carried forward by reference without re-derivation; grounds: the two hashes above.
- contamination_disclosure: the auditor has read the round-1 and round-2 GT of both tasks in earlier rounds (disclosed there). Round-3 checks below rest on the round-3 views, the unchanged charter and the runtime code.

### frozen_time format change (charter-independent, both tasks)

- View diff r2 → r4 (field by field): `user_scenario` identical, `initial_state` identical, only `frozen_time` changed — task 0 '2026-10-06T10:15:00' → '2026-10-06 10:15:00 CDT'; task 1 '2026-10-06T14:30:00' → '2026-10-06 14:30:00 PDT'.
- Format: matches the runtime clock convention (`erlbench/determinism.py` Clock docstring: "e.g. '2025-11-14 03:40:00 EST' (starts with YYYY-MM-DD)") and passes the validator regex.
- Zones are the customers' own: Delia hosts in Nashville (US Central, daylight time on 6 October → CDT); Harbor & Pine Stays is in San Diego (US Pacific, daylight time → PDT). Date and wall-clock time are unchanged.
- Consumers of the clock: every task tool takes `ctx.now()[:10]` (task_tools.py L48, L91, L113, L162); the compute DSL takes `str(frozen_time)[:10]` (check_compute.py `NOW`); `verify_customer_identity` stores `ctx.now()` verbatim as a timestamp only. Every policy window in this charter is counted in calendar dates. The date part is still 2026-10-06 in both tasks, so no window, tier or tool effect can move.
- Re-evaluation of every computation's own compute on the r4 views (temporary script, removed): decision Superhost (each factor baseline and whole baseline Standard Host); credit 212.00 (162.00 / 201.00 / 208.00 / 202.00 / 192.00 / 202.00; whole 109.00; 0.00 at the opening); enrollment Professional Host Plus (each baseline Professional Host); re-rating 46.71 (0.00 / 38.06 / 38.06 / 39.79 / 41.52; whole 0.00; 0.00 at the opening) — identical to revision_2.
- No new charter-global defect; no regression.

### closing_checklist (revision_3)

Written 2026-10-07 after both round-3 reveals (frozen hashes 2026-10-07T22:39:44Z; `_difficulty.md` 580fd1e9dd838f9ee4b43d30c7794e362c21e4a98ab492a8685c4c7568644f21). Clock correction: "~22:40Z" above is an estimate; the true freeze is the 22:39:44Z hash record.

**Status: CLOSED** (unchanged from revision_2).

| item | state |
| --- | --- |
| per-task files 1:1; earlier revisions preserved | yes — `## revision_3` appended; revision_1 and revision_2 text untouched |
| every comparison section PASS | yes — task 0 PASS, task 1 PASS (revision_3) |
| scopes, tools / GT closure, uuid8s, trees, factors | carried from revision_2 (charter and tools byte-identical; the views differ only in frozen_time; the scored solutions are identical) |
| instantiation gates on the final form | cited: coordinator snapshot `/tmp/erl45_views/r4/host_standing_and_penalties/gate_snapshot.txt` — all OK, **check_traceability now OK** (docs rendered), check_cache_diff INFO; validate_scenario VALID |

Open observations carried to the KB stage: unchanged from revision_2.
