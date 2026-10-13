# Policy-task audit — weekly_certification_and_benefit_payment / charter-global

## charter_global_frozen

- Revision: revision_1 (first audit of this difficulty; no earlier revision exists in this directory).
- Freeze time: 2026-10-10T13:32Z. Auditor: erl-task-policy-audit, independent of the instantiator. Read nothing written by the instantiator except the audited artifacts.
- Frozen inputs (sha256, re-checked against the coordinator's brief before reading):
  - `tasks/weekly_certification_and_benefit_payment/claim.extended.yaml` 314161f53928e240f64d5ad33fd8d15c3a9ad54ed80cb802d3462da106b025be
  - `tasks/weekly_certification_and_benefit_payment/task_tools.py` a84f7fd35e866cc5c2b1b460d0e3bfe6a00c42f660a1b061df2aa7daa3ad29a9
  - blind views `task_0.blind.json` 9b3da304…dcb52, `task_1.blind.json` 76ade9f0…3e17 (frozen_time, user_scenario, initial_state only)
- Read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/claim.yaml` plus the cross-category products (`overpay.yaml`, `idv.yaml`, `withhold.yaml`, `appeal.yaml`) for the seeded rows the factors read; the extended charter; `task_tools.py`; the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`, used only for the meaning of `CFIELD`/`LATEST`/`within_months`).
- Masked and not read at the time this section was written: everything in `tasks/<i>.json` beyond the blind views (`evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, db_closure fields), `worklog.md`, the instantiator's transcripts, other scenarios, sibling difficulties.
- This section is built from the charter, the schema and the tool contracts alone and contains nothing derived from a revealed GT.
- Gate snapshot supplied by the coordinator (cited, not re-run): check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cache_diff, check_cross_fire all rc=0; check_traceability deferred to render; validate_scenario errors only "required document not found" (pre-render). Entry conditions met.

Base section: `python yaml.safe_load` of the extended charter's `category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies` equals `blueprint/products/claim.yaml` key for key (all True); the only added key is `extended_policies` (8 policies).

### policy_conflict_scan

The 8 extended policies and the problem tree each of the two tasks claims (derived from `user_scenario` + the rules, scopes not read from the masked `charter_scope`):

| Task | Root | Prerequisite problems |
| --- | --- | --- |
| 0 | `claim_ext_extension_entitlement` (EB first determination) | `claim_ext_parent_shortfall_supplement`, `claim_ext_dependency_redetermination`, `claim_ext_payment_election_lead` |
| 1 | `claim_ext_regular_weekly_payable` | `claim_ext_waiting_week_value`, `claim_ext_dependency_disallowance`, `claim_ext_holiday_pay_report` |

Scopes are pairwise disjoint and jointly cover the 8 extended policies.

Overlaps examined:
- Subject `claim_benefit_paid` is shared by `parent_shortfall_supplement` (payment_kind supplemental, a week already paid) and `regular_weekly_payable` (payment_kind weekly, latest certified week): disjoint by payment kind and by base `one_payment_per_week_and_kind`. No conflict.
- Subject `claim_entitlement_credited` is shared by `dependency_redetermination` (credit on a determined claim) and `extension_entitlement` (first determination on a filed EB claim): disjoint by trigger object. No conflict.
- `dependency_redetermination` and `dependency_disallowance` both rewrite `claims.dependency_allowance`: triggers are complementary ("dependents on record exceed" vs "counts more dependents than are now on record"). No conflict.
- Both tasks' worlds use UCFE claims (`employer_charge_share` 0.0), so the payment tools' fixed `charge_code="non_charged"` agrees with base `claim_evt_payable_amount` ("non_charged when the share is zero"). The tools' docstrings restrict them to "a claim of a program not charged to employers"; a Regular/CWC claim could not be paid with them (observation O-6 below).
- Cross-category read boundaries: extension_entitlement reads overpay; payment_election_lead reads idv; dependency_disallowance reads appeal and withhold; waiting_week_value and regular_weekly_payable read overpay. All declared in `cross_category`.
- Conflicts with base found in this scan are carried in `override_declarations` and `findings` (F-1 … F-4).

### rule_compute_equivalence

Swept every binding of every policy against its `compute_basis` quotation and back against the rule. Equivalent except:

- **F-5 `claim_ext_dependency_redetermination.frac`**: compute adds `and credits > 0` (credits = SUM of `claim_entitlement_credited`) to both non-fall-through tiers; the rule's tier sentences ("the steady-earner standard fraction when the standard base period was used and base-period wages are at least the steady-earner ratio times high-quarter wages") carry no such condition, and the `compute_basis` given for `credits` is the trigger sentence, which states no condition on prior credits. A tier condition living only in compute.
- **F-6 `claim_ext_waiting_week_value.other_ded`**: rule: "other pay is deducted as the weekly payable rule states". Compute: `opay if opay_type == 'vacation_pay' or opay_type == 'holiday_pay' else 0`. The base weekly payable rule (`claim_evt_payable_amount`, still in force for the waiting-week policy, which declares no overwrite) deducts "the weekly-prorated base-period-employer pension times the pension offset share, using the claimant-contributed share"; the extended weekly payable rule deducts holiday pay at one half when one day's hours were worked and adds it to earnings below one day. Compute implements neither for pensions or part-week holiday pay.
- **F-7 `claim_ext_payment_election_lead.other_verified`**: `CFIELD('idv','verified_date', claim_id=HID, status='verified')` returns the first verified case of the claimant on the claim (DSL: `hs[0]`), which may be the theft re-verification itself; the rule's middle tier is "another identity verification case on the claim was verified within those days and no such re-verification was". Divergent when a stale theft case and a recent other case are both verified.
- Observation O-1 `claim_ext_holiday_pay_report.rate`: compute's middle tier also requires `lat_h > 0`; the rule's middle tier ("the window carries some hours but fewer than the minimum") does not, and is undefined (division by zero) when the latest week has 0 hours. No world of this difficulty reaches it.
- Observation O-2 `claim_ext_extension_entitlement.op_penalty_pct`: `CPARAM('overpay','penalty_pct', claim_id=HID)` reads the first overpayment of any status; the rule's "a fraud overpayment stands against the parent claim" is read as any fraud classification. Same answer when one overpayment exists.

Everything else (windows `within_months`/`MONTHS`, `DAYS` anchors, the "rounded up" ceilings `int((x + w - 0.01)/w)`, caps, floors, rounding points, grouping "both deductions … in one step") has a verbatim basis sentence and no rule sentence lacks an implementation.

### action_binding_and_uuids

| Policy | target_tool | computes | owner |
| --- | --- | --- | --- |
| dependency_redetermination | record_dependency_redetermination_c7b3c182 | amount | agent |
| payment_election_lead | elect_payment_method_0e517696 | lead_business_days | user |
| parent_shortfall_supplement | issue_supplemental_payment_38b81267 | amount | agent |
| extension_entitlement | determine_extension_entitlement_db601fac | max_benefit_amount | agent |
| dependency_disallowance | record_dependency_disallowance_f94a20ca | amount | agent |
| holiday_pay_report | certify_week_by_phone_ea18d1f2 | other_pay_amount | user |
| waiting_week_value | record_waiting_week_428070c9 | amount | agent |
| regular_weekly_payable | issue_weekly_payment_6cd10c49 | amount | agent |

- Each `(target_tool, computes)` is claimed by exactly one policy. The share tools carry only two writes (`verify_caller_identity`, `transfer_to_human_agent`), so no shared write competes with a task tool.
- uuid8s c7b3c182, 0e517696, 38b81267, db601fac, f94a20ca, ea18d1f2, 428070c9, 6cd10c49: eight distinct values, no shared prefix/suffix, no sequence pattern. PASS.
- Every function body performs its write unconditionally (no refusal, no error, no hint when a prerequisite is unresolved): confirmed by reading all eight bodies.
- Docstrings name no other tool and state no position in a sequence. The only ordering word is "read from the claim lookup before the call" in argument descriptions (a read, not another problem): observation O-3.

### prerequisite_graph

Edges (problem ← prerequisite), as declared:

| Blocked policy | Prerequisite | kind | gate | form |
| --- | --- | --- | --- | --- |
| parent_shortfall_supplement | dependency_redetermination | value_input | da | state |
| parent_shortfall_supplement | payment_election_lead | state_gate | claims.payment_method_effective_date | state |
| extension_entitlement | parent_shortfall_supplement | value_input | paid | action (fallback_reason present) |
| extension_entitlement | dependency_redetermination | value_input | da | state |
| holiday_pay_report | waiting_week_value | state_gate | claim_ledger.event_type | state |
| waiting_week_value | dependency_disallowance | value_input | da | state |
| regular_weekly_payable | waiting_week_value | value_input | served | state |
| regular_weekly_payable | dependency_disallowance | value_input | da | state |
| regular_weekly_payable | holiday_pay_report | value_input | opay | state |

- `prerequisite` filled on all 8 (`[]` on redetermination, election, disallowance). Every `problem` is an extended policy id of this file, none self-referential. Graph acyclic (two components; topological orders: redetermination, election → supplemental → EB; disallowance → waiting → holiday → weekly).
- Every `policy_source` is a verbatim sentence of the blocked policy's own `rule` (located by substring search).
- `fallback_reason` present exactly on the one action-form edge.
- `resolved_by` equals the depended-on policy's `target_tool` on every edge, and each tool's effect (allowance/ledger write, ledger entry, certification row, `payment_method_effective_date`) makes the stated gate hold or changes the named binding.
- `kind`: every value_input `gate` names a binding that exists in the blocked compute (`da`, `paid`, `served`, `opay`); the two state_gates name the record field their sentence reads.
- `condition` strength (observation O-4): three conditions add a clause their sentence does not carry — supplemental←redetermination adds "the redetermination credit stands in the claim ledger"; EB←redetermination adds "its latest monetary determination date is the redetermination date"; weekly←disallowance adds "the reduction stands in the claim ledger"; EB←supplemental adds "its remaining balance is zero and its status is exhausted". Each added clause is a side effect of the same single resolving write (or, for exhaustion, a base eligibility already required by `claim_agg_program_sequence`), so no reading changes; recorded as observation.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` text.

### prerequisite_sentences

Four-point test on each sentence (connective / waited-on state or action / no tool, id, snake_case, row id / strength equal to the condition):

1. supplemental ← redetermination: "A supplemental correction is computed only once the claim's dependency allowance counts every dependent added to the record." — "only once"; state of `claims.dependency_allowance` vs `claims.dependents_count`; clean; strength = condition minus the ledger clause (O-4). The one write that brings it about: the dependency redetermination (the disallowance moves the allowance the other way). Derivation: claim shows dependents 2, allowance set at one dependent → read the redetermination rule ("issued on a claim whose dependents on record exceed the dependents its current dependency allowance was set for") → that write. Single reading. PASS.
2. supplemental ← election: "A supplemental payment is not issued until the claim carries a payment method election recorded after the latest identity theft re-verification of the claimant was verified." — "not … until"; state (an election on the claim, and the verified date of the idv case); clean; strength = condition. One write: the payment election (the only write touching `payment_method`). The recording date of an election is not a stored field; it is read off `payment_method_effective_date` minus at least the program lead (observation O-5). PASS.
3. EB ← supplemental (action): "The Extended Benefits maximum benefit amount is fixed only after the shortfall on the parent claim's last paid week has been paid to the claimant as a supplemental correction." — "only after"; names the action in business words; clean. Fallback test: the `fallback_reason` argues only against the state "balance zero / exhausted". The record-visible state "the parent claim's ledger carries a payment of kind supplemental for its last paid week" is left only by the supplemental write and would single it out → the fallback is unjustified (observation O-7, naming that state).
4. EB ← redetermination: "The Extended Benefits maximum benefit amount is not fixed until the parent claim's dependency allowance counts every dependent added to the record." — PASS as (1).
5. holiday report ← waiting week: "A week after the first week of a benefit year is certified only after the claim carries a waiting-week entry." — "only after"; state = ledger row `claim_waiting_week_served`; one write (record_waiting_week). PASS.
6. waiting ← disallowance: "The value of a waiting week is not fixed until the claim's dependency allowance no longer counts any dependent removed from the record." — PASS; one write (disallowance).
7. weekly ← waiting: "A weekly payment is not fixed until the claim carries a waiting-week entry for the first otherwise-payable week of its benefit year." — PASS. Second wording of the same dependency inside the same rule: the standard-method sentence "nothing is payable before the claim carries its waiting week count of waiting-week entries" (observation O-8; both wordings agree on every world because waiting_week_count is 1 or 0).
8. weekly ← disallowance: "A weekly payment is fixed only after the claim's dependency allowance no longer counts any dependent removed from the record." — PASS.
9. weekly ← holiday report: "A weekly payment is issued only after the week being paid carries the claimant's weekly certification." — PASS; one write (phone certification is the only certification write).

- No depended-on rule restates the blocked sentence. No rule states a cross-problem order that grounds no declared edge (the EB rule's "credits … and makes the claim active" and the waiting-week rule's "the week valued is the latest week certified … at the time the entry is made" are consistent with, and entailed by, edge 5).
- Base sentences stating cross-problem order (`claim_evt_waiting_week`: "No weekly payment is issued … until the waiting week has been served"; `claim_agg_program_sequence`: EB "only when the claim named in its parent_claim_id has status exhausted") do not ground any edge; every edge has its own extended sentence. Observation only.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (finding half only; consequences are demonstrated in the task files):

**dependency_redetermination** (ref `claim_monetary_eligibility`): declared — the MBA sentence. Undeclared:
- "The dependency allowance is the per-dependent amount times the number of dependents on record, counting no more than the maximum number of dependents." The extended policy sets the redetermined allowance with a per-dependent amount of 18/16 instead of the program's 15 and caps it at 7.5%/8% of the WBA. The scored `dependency_allowance` and the credit are the quantity this base sentence governs. **F-1 (undeclared override).**
- Other sentences (base period, eligibility test, WBA formula, credit mechanics, redetermination number, request window) are followed or not touched.

**payment_election_lead** (ref `claim_payment_method`): declared — the lead-time sentence. "Only the claimant may ask", "not while hold reason is fraud_review", debit-card replacement — inherited. PASS.

**parent_shortfall_supplement** (refs `claim_agg_program_sequence`, `claim_evt_payable_amount`, `claim_evt_waiting_week`): declared — the earnings-deduction/disregard sentence and the full-time-hours sentence. Undeclared:
- "The other-pay deduction is vacation and holiday pay allocated to the week where deductible, plus the weekly-prorated base-period-employer pension times the pension offset share, using the claimant-contributed share where the claimant paid into the plan; severance pay is not deducted." The supplemental deducts a claimant-contributed pension at 0.25 or 0.375 instead of the claimant-contributed share (0.5). **F-2 (undeclared override).**
- Payable amount sentence ("WBA plus dependency allowance minus both deductions, rounded down …"), status/once-per-kind/supplemental-only correction, payment method in force, charge code, offsets after computation — followed.

**extension_entitlement** (refs `claim_monetary_eligibility`, `claim_extended_program_entitlement`, `claim_agg_program_sequence`): declared — the EB entitlement sentence as a whole. That sentence also carried the eligibility clause "the claimant must show the minimum weeks of full-time base-period employment"; `replaced_by` restates nothing of it, so the declared supersession removes an eligibility test (observation O-9: declared, so legal; no record of base-period employment weeks exists in any world, so no reading changes). Parent-exhausted gate (`claim_agg_program_sequence`) inherited and honoured.

**dependency_disallowance** (ref `claim_monetary_eligibility`): declared — "A monetary redetermination … books only the difference from the previous maximum benefit amount …". Undeclared:
- The dependency-allowance sentence (as for F-1): the disallowance's redetermined allowance uses 18/16 per dependent, counts a removed dependent at 0.5/0.25, and caps at 4%/6% of the WBA. **F-3 (undeclared override).**
- "The maximum benefit amount is the lesser of the maximum duration weeks times the weekly benefit amount plus dependency allowance and the base-period-wage fraction times base-period wages, rounded down to the whole dollar." The disallowance changes the MBA by `weeks × decrease × appeal share` instead of recomputing it; the redetermination policy declared this very sentence superseded, the disallowance did not. **F-3 (same finding, second sentence).**

**holiday_pay_report** (ref `claim_evt_weekly_certification`, `overwrite: []`): the base sentences (channels, opening day, active/on_hold, once per week, timeliness, the questions asked, work-search) are followed; the base says the claimant reports holiday pay and says nothing about valuing it, so the extended valuation adds a quantity rather than overriding one. PASS.

**waiting_week_value** (ref `claim_evt_waiting_week`, `overwrite: []`): 
- Base: "A waiting week is recorded only for a week that would otherwise have been paid in full or in part; … a week with excess earnings or full-time hours … does not serve" and "A waiting week is recorded only while claim_msr_waiting_weeks_served is below the program's waiting week count". Extended: the value "is zero for a week whose hours reach the program's full-time hours threshold or when the claim already carries its waiting week count of entries", with its own thresholds (36/34). On a week of 33 hours with a recall date the base says the week does not serve (32-hour program threshold) while the extended threshold of 36 values it. **F-4 (undeclared override; conditional on worlds with such a week).**

**regular_weekly_payable** (refs `claim_agg_program_sequence`, `claim_evt_payable_amount`, `claim_evt_waiting_week`): declared — disregard/earnings sentence, full-time sentence, other-pay sentence. Undeclared:
- "The payable amount is the weekly benefit amount plus dependency allowance minus both deductions, rounded down to the whole dollar, never below zero and never more than the remaining benefit balance; a payable amount of zero records no payment." The extended pays one half or three quarters of the dependency allowance when counted earnings exceed the disregard (anonymous intermediate `da_paid`). **F-2b (undeclared override).**
- The declared supersession of the other-pay sentence drops the pension offset entirely (no extended sentence deducts any pension). Declared, so legal; a dropped branch (observation O-10; the federal pension-offset requirement makes the result unrealistic for the business).

### factor_ladders

Effect labels judged by what the tiers change (a `method` tier must change the algorithm; a `parameter` tier a number):

| Policy | Factor | Label | Honest? | Tiers distinct | Multi-source tiers | Cross-difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| redetermination | per_dependent_amount_redetermination | parameter | yes | 18/16/15 | deps + effective date (same row) | — |
| | credited_weeks_redetermination | method | yes (tier 1 reads the balance) | yes | no | — |
| | allowance_ceiling_redetermination | parameter | yes | 7.5%/8%/none | no | — |
| | wage_cap_fraction_redetermination | parameter | yes | .36/.35/.3333 | base period type + wages (+ compute-only ledger credits, F-5) | — |
| election | prenote_days | parameter | yes | 5/2/0 | ledger cancellations + ledger payments | — |
| | verification_days | parameter | yes | 3/1/0 | idv cases | idv |
| | payment_cycle_rounding | method | **no** — every tier is "round the total up to a multiple of k", k = 5, 2, 1 (as counted); only the number changes (F-8) | yes | no | — |
| | change_review_days | parameter | yes | 3/1/0 | no | — |
| supplemental | disregard_share_supplemental | parameter | yes | .5/.4/.3 | training (claim) + attachment hours (certifications) | — |
| | full_time_threshold_supplemental | parameter | yes | 36/34/32 | separation + recall date | — |
| | excess_earnings_rate_supplemental | method | **no** — deduction = r × excess, r = 0.5, 0.75, 1 (F-8) | yes | no | — |
| | pension_share_supplemental | parameter | yes | .25/.375/std | no | — |
| EB | eb_fraction | parameter | yes | .52/.51/.5 | parent wages (claim) + weekly payment count (ledger) | — |
| | parent_entitlement_measure | method | yes | yes | no | overpay |
| | training_weeks_added | parameter | yes | 2/1/0 | training + age (same row) | — |
| | training_week_value | parameter | yes | wba+da / wba+da/2 / wba | da + determination age | — |
| disallowance | remaining_dependent_amount | parameter | yes | 18/16/15 | no | — |
| | disallowance_weeks | method | yes (tier 2 reads the balance) | yes | payments + balance | — |
| | provisional_allowance_ceiling | parameter | yes | 4%/6%/none | no | — |
| | pending_monetary_appeal_share | parameter | yes | .5/0/1 | no | appeal |
| | supported_removed_dependent | parameter | yes | .5/.25/0 | no | withhold |
| holiday | holiday_history_window | method | **no** — tiers select 12, 6 or 3 months for the same window sum (F-8) | yes | no | — |
| | holiday_regular_rate | method | algorithm yes, but **its ladder is the baseline itself** (F-9) | yes | no | — |
| | holiday_hours_credited | parameter | yes | 4/6/8 | no | — |
| | holiday_pay_share | parameter | yes | .5/.75/1 | no | — |
| waiting | waiting_disregard_share | parameter | yes | .4/.35/.3 | dependents (claim) + earnings (certification) | — |
| | waiting_full_time_threshold | parameter | yes | 36/34/32 | no | — |
| | waiting_excess_rate | method | **no** — r × excess, r = 0.5, 0.75, 1 (F-8) | yes | no | — |
| | waiting_allowance_counted | parameter | yes | ½/¾/full | earnings + hours | — |
| | waiting_integrity_reduction | parameter | yes | 40/60/0 | overpay status + date | overpay |
| weekly | weekly_disregard_share | parameter | yes | .4/.35/.3 | recall date (claim) + earnings (certification) | — |
| | weekly_full_time_threshold | parameter | yes | 36/34/32 | separation + claim age | — |
| | weekly_excess_rate | method | **no** — r × excess, r = 0.5, 0.75, 1 (F-8) | yes | no | — |
| | weekly_allowance_paid | parameter | yes | ½/¾/full | earnings + hours | — |
| | weekly_holiday_treatment | method | yes (tier 1 moves the pay into earnings) | yes | no | — |
| | weekly_integrity_reduction | parameter | yes | 40/60/0 | overpay status + date | overpay |

Counts after the label test (genuine `method` factors per policy): redetermination 1, election **0**, supplemental **0**, EB 1, disallowance 1, holiday **0** (window is a parameter; the rate factor is struck by F-9), waiting **0**, weekly 1. Factor totals 4,4,4,4,5,4,5,6 (holiday drops to 3 once F-9 strikes the rate factor). `parameter` ≥ 2 everywhere. **F-8/F-9 → the election, supplemental, holiday and waiting policies each lack a genuine method factor.**

Other structural results:
- Every ladder has ≥3 tiers stated in full in the rule and implemented in `decides` (both directions), except F-5 (a compute-only condition in `frac`).
- No two tiers of a ladder select the same value or method.
- Tiers that overlap as stated (**F-10**): `parent_entitlement_measure` (a non-fraud overpayment at status established and a fraud overpayment can stand against the same parent at once; the rule gives no precedence: paid − principal vs zero), `waiting_integrity_reduction` and `weekly_integrity_reduction` (a waiver-pending and an any-other-status misreported-earnings overpayment can both lie within the window: 40 vs 60). Compute settles them by ordering (`CPARAM`/`CFIELD` first row), which the rule does not state.
- Fall-through = baseline for every factor except `holiday_regular_rate` (F-9): `baseline.rule` states the full three-tier rate rule ("the regular hourly rate is the gross earnings divided by the hours worked … when those hours reach the minimum hours, the latest certified week's earnings divided by its hours when some but fewer hours were reported, and otherwise that claim's high-quarter wages divided by the quarter hours"), while the factor's fall-through and `baseline` binding are `RND(F('high_quarter_wages') / K('quarter_hours'), 2)` alone.
- `training_week_value`: `baseline.rule` adds no training weeks, so it states no value for a training week; the factor's baseline `wba` is not stated by `baseline.rule` (observation O-11).
- Realism (observations, no RED claimed): several tiers rest on conditions no unemployment-insurance program is known to weigh for the quantity — per-dependent amounts that rise with claim age (18/16 vs the statutory 15), an earnings disregard that varies with the distance of a recall date (weekly payable) or with "attachment hours" (supplemental), a full-time threshold keyed to a federal separation in the first 182 days, EB training add-on weeks (a TRA, not an EB, feature), and the dropped pension offset (O-10). Recorded as O-12; I did not judge any of them demonstrably unreal for this audit's purposes.
- Cross-difficulty factors and categories: election→idv; EB→overpay; disallowance→appeal, withhold; waiting→overpay; weekly→overpay. Multi-source factors exist in both trees (task 0: eb_fraction, disregard_share_supplemental; task 1: weekly_disregard_share, waiting_disregard_share).

### findings

| Id | Verdict | Finding | Bears on |
| --- | --- | --- | --- |
| F-1 | SOURCE-POLICY RED | dependency_redetermination overrides the base dependency-allowance sentence (per-dependent 18/16, ceiling) without naming it in `overwrite` | task 0 (demonstrated there) |
| F-2 | SOURCE-POLICY RED | parent_shortfall_supplement overrides the base other-pay sentence (claimant-contributed pension at 0.25/0.375 instead of the claimant-contributed share 0.5) without naming it | task 0 |
| F-2b | SOURCE-POLICY RED | regular_weekly_payable pays ½ or ¾ of the dependency allowance against the base payable-amount sentence ("plus dependency allowance") without naming it | task 1 |
| F-3 | SOURCE-POLICY RED | dependency_disallowance overrides the base dependency-allowance sentence and the base MBA sentence without naming them | task 1 |
| F-4 | SOURCE-POLICY RED (conditional) | waiting_week_value values weeks the base says do not serve (own thresholds; zero-value entry when the count is already served) with `overwrite: []` | no task world reaches it (task 1 week has 17 h, count 0) |
| F-5 | SOURCE-POLICY RED (rule/compute) | `frac` carries `credits > 0` only in compute | task 0 world: no consequence (credits 12,032 > 0) |
| F-6 | SOURCE-POLICY RED (rule/compute) | waiting-week other-pay deduction ignores pensions and the part-week holiday rule that "as the weekly payable rule states" imports | no task world reaches it (task 1 waiting week has no other pay) |
| F-7 | SOURCE-POLICY RED (rule/compute) | `other_verified` can select the theft re-verification case itself | no task world reaches it |
| F-8 | SOURCE-FACTOR RED | five factors labelled `method` only change a number (cycle k, rate r ×3, window months) | tasks 0 and 1 |
| F-9 | SOURCE-FACTOR RED | holiday_regular_rate's ladder is the baseline; its fall-through is not the baseline | task 1 |
| F-10 | SOURCE-FACTOR RED (structural) | tiers overlap as stated in parent_entitlement_measure and both integrity reductions | task 0 / task 1: no overlap in either world (one overpayment each) |

Observations O-1 … O-12 are listed in the sections above.

## closing_checklist

Written after both reveals (2026-10-10T13:36:01Z). The section above was frozen before any reveal and has not been changed since.

The difficulty is **not closed**:

| Task | Policy self-consistency | Problem tree | Factors | Unique solution | Overall |
| --- | --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED (F-1, F-2) | PASS | SOURCE-FACTOR RED (F-8; false proof figure) | derivation = GT; residual second answers are F-1/F-2 | RED |
| 1 | SOURCE-POLICY RED (F-2b, F-3) | PASS | SOURCE-FACTOR RED (F-8, F-9, overpay seed vs charter, false multi-source claim) | derivation = GT; residual second answers are F-2b/F-3 | RED |

Step 4 items that do hold:
- Audit files correspond one-to-one with tasks 0 and 1.
- The scopes are pairwise disjoint and cover all 8 extended policies (GT `charter_scope` agrees).
- Every task tool has an independent uuid8.
- Each tree has 3 prerequisite problems, at least 2 `value_input` edges and one `owner=user` write, and the difficulty-wide graph is acyclic.
- Every computation's all-baseline number differs from gold (task 0: 0, 2, 18.0, 6,025; task 1: 390, 371, 184.0, 425).

Items that fail are F-1, F-2, F-2b, F-3, F-8, F-9 and the overpay seed contradiction. The instantiation-stage gates were not re-run on a final form, because no rework has happened.

## revision_2

### charter_global_frozen (revision_2)

- Re-audit round 2. Frozen 2026-10-10 18:11Z (host UTC clock), before any round-2 GT field was read. The revision_1 text above is preserved unchanged.
- Inputs (sha256 re-checked against the coordinator's brief):
  - `claim.extended.yaml` e2a2d2d042b996601f58ea3159ad5ca54454662a7db4e4f9a209269241a78d41 (**changed** from 314161f5…), so every charter-global section is re-derived in full below.
  - `task_tools.py` a84f7fd35e866cc5c2b1b460d0e3bfe6a00c42f660a1b061df2aa7daa3ad29a9 (unchanged), so `action_binding_and_uuids` of revision_1 is carried forward by reference on that hash.
  - Blind views `task_0.blind.json` c5468a55…ef2e (from `tasks/0.json` 1c84bd86…f949) and `task_1.blind.json` ff08aa20…a360 (from `tasks/1.json` 30a376f2…f9a). Both hashes matched.
- Base copy: still key-for-key equal to `blueprint/products/claim.yaml`; only `extended_policies` is added.
- The coordinator's gate snapshot after rework is all rc=0 (cited, not re-run); traceability is still deferred.
- contamination_disclosure (round level): this auditor read the round-1 GT of both tasks during revision_1. The round-2 derivations therefore cannot be naive to the round-1 conventions. No round-2 GT field (`evaluation_criteria`, `computations`, `prerequisite_closure`, `design_rationale`, `charter_scope`, worklog) was read before the per-task revision_2 freezes. The reworker's item-id claims were treated as claims only.

### policy_conflict_scan (revision_2)

Subjects, triggers, objects and cross-category boundaries are unchanged from revision_1. Scopes are still pairwise disjoint and jointly complete on the derived trees (task 0: redetermination, election, supplemental, EB; task 1: disallowance, waiting week, holiday report, weekly payment). No new conflict between extended policies.

### rule_compute_equivalence (revision_2)

- Every `compute_basis` quotation is a verbatim substring of its rule (mechanical sweep). Binding names without a basis are only raw field reads (`wba`, `da`) and one alias (`result`).
- **F-5 closed.** The `frac` tiers now state the third condition in the rule ("and the entitlement credited on the claim already reaches the program's base-period-wage fraction times base-period wages, rounded down to the whole dollar"); compute implements `credits >= int(P('mba_bpw_fraction') * F('base_period_wages'))`.
- **F-6 closed.** The waiting-week rule now states its own other-pay treatment ("in full for vacation or holiday pay, at the program's pension offset share for an employer-funded pension and at the program's claimant-contributed share for a claimant-contributed pension …"); `other_ded` implements exactly that. The reference to "the weekly payable rule" is gone.
- **F-7 closed.** `other_verified` is now `XLATEST('idv','idv_cases','verified_date', claim_id=HID)` behind the theft branch.
  - Case 1: if the latest verified case is the theft case and it lies outside the window, every other case is older and also outside, so tier 2 is correctly not taken.
  - Case 2: if any other case is more recent, XLATEST returns it.
  - In both cases this is equivalent to the rule's "the most recently verified identity verification case on the claim, of any other pathway".
- **O-1 addressed.** The holiday rate's middle tier now requires "that latest week reports hours worked", matching `lat_h > 0`.
- O-2 addressed: the EB measure now uses `XCOUNT` of both fraud classifications and `XSUM` of established principals. Residual observation: "stands against" is read as any status for fraud overpayments; no world reaches the difference.
- New observation R2-O1: the weekly-payable standard method no longer states "nothing is payable before the claim carries its waiting week count", while compute still zeroes the result when `served < waiting_week_count`. This is grounded by the rule's own prerequisite sentence and by base `claim_evt_waiting_week`, so no reading changes.

### action_binding_and_uuids (revision_2)

Carried forward from revision_1 by the unchanged `task_tools.py` hash a84f7fd3…; the `(target_tool, computes)` claims in the charter are unchanged (re-checked).

### prerequisite_graph (revision_2)

- Same nine edges as revision_1, same kinds and gates. EB←supplemental is now `form: state` with no `fallback_reason`, which closes O-7.
- Graph acyclic; every `policy_source` verbatim in its own rule; every `resolved_by` equals the depended-on target tool.
- **O-4 addressed:** the four conditions now carry exactly their sentence's strength:
  - supplemental←redetermination and EB←redetermination: "counts every dependent on record";
  - weekly←disallowance: "no longer counts a dependent removed from the record";
  - EB←supplemental: "carries a supplemental payment for its last paid week".

### prerequisite_sentences (revision_2)

- EB←supplemental (new state form): "The Extended Benefits maximum benefit amount is fixed only after the parent claim's last paid week carries a supplemental payment for its shortfall."
  - Connective "only after".
  - Waited-on state: a ledger row of kind supplemental for the last paid week.
  - No tool, id or snake_case token.
  - Exactly one write of the difficulty brings it about (the supplemental tool; the weekly tool's kind is `weekly` by policy).
  - PASS.
- **O-8 addressed:** the weekly rule no longer carries a second wording of the waiting-week dependency.
- All other sentences: unchanged and PASS as in revision_1.

### override_declarations (revision_2)

- **F-1 closed.** The redetermination's `overwrite` now also names "The dependency allowance is the per-dependent amount times the number of dependents on record, counting no more than the maximum number of dependents." The whole sentence is superseded, so the ceiling is covered too.
- **F-2 closed.** The supplemental's `overwrite` now names the other-pay sentence ("The other-pay deduction is vacation and holiday pay allocated to the week where deductible, plus the weekly-prorated base-period-employer pension …"); the extended standard method restates vacation/holiday/pension/severance.
- **F-2b closed.** The weekly payment's `overwrite` now names "The payable amount is the weekly benefit amount plus dependency allowance minus both deductions …". Residual observation R2-O2: that superseded sentence also carried "a payable amount of zero records no payment", which the extended rule does not restate. The tool argument is "always positive", so no reading changes in any world.
- **F-3 closed.** The disallowance's `overwrite` now names both the dependency-allowance sentence and the MBA sentence.
- **F-4 closed.** The waiting-week standard method now says "a week whose hours reach the program's full-time hours threshold does not serve and is not valued, nor is any week valued once the claim carries its waiting week count of entries". The recall-dependent figure is now only an "hours base" for the earnings fractions, so it no longer decides whether a week serves. Residual observation R2-O3: base "a week with excess earnings … does not serve" is judged by "would otherwise have been paid", and the extended rule doesn't say which payable formula decides that. No task world is near it (task 1's waiting week pays 382 under the base formula and 430 under the extended one).
- **O-10 closed.** The weekly payable standard method deducts pensions at the program shares again.
- **O-9 "addressed" — regression.** The EB `overwrite.superseded_clause` is now only the clause "its maximum benefit amount is the lesser of …". The rest of the base sentence, including "**the claimant must show the minimum weeks of full-time base-period employment**" (EB variant `eb_min_weeks_employment` 20), is therefore back in force for the first EB determination.
  - No table of the schema records weeks of base-period employment: `claims` carries quarters and wage totals only, and the claim measures have no such quantity.
  - So the test can be met only from what the claimant says. Whether that bears on a task is demonstrated in `0.md` revision_2 (**R2-F1**).

### factor_ladders (revision_2)

Relabels and new tiers (charter-global structure only):

| Policy | Factor | Label now | Judgement |
| --- | --- | --- | --- |
| election | payment_cycle_rounding | method | genuine: round up to a multiple of 5 / add 2 card-activation days without rounding / as counted — two different operations |
| supplemental | excess_earnings_rate_supplemental | parameter | honest now |
| supplemental | pension_deduction_supplemental (new) | method | genuine: subtract a 10% WBA pension disregard then apply the share / whole pension at 0.375 / whole pension at the standard share |
| holiday | holiday_history_window | parameter | honest now |
| holiday | holiday_regular_rate | method | genuine; `baseline.rule` now states the rate as HQW ÷ quarter hours, which equals the fall-through and the factor's `baseline` (**F-9 closed**) |
| waiting | waiting_excess_rate | parameter | honest now |
| waiting | waiting_hours_base (was full-time threshold) | parameter | honest |
| waiting | waiting_allowance_counted | method | genuine: allowance × unworked share of the hours base / ¾ / full |
| weekly | weekly_excess_rate | parameter | honest now |

- Genuine method factors per policy: redetermination 1, election 1, supplemental 1, EB 1, disallowance 1, holiday 1, waiting 1, weekly 1.
- Totals 4/4/4/4/5/4/5/6, parameters ≥2 everywhere.
- **F-8 closed.**
- **F-10 closed:**
  - EB measure tiers are now "one or more non-fraud … established and no fraud" / "any fraud" / "neither" — disjoint;
  - both integrity reductions are now "any misreported-earnings overpayment within the 12-month window with a balance due" / "such overpayments exist and all carry no balance due" / "none" — disjoint.
- **O-11 closed:** `baseline.rule` of the EB now states "a training week, wherever one is added, is valued at the weekly benefit amount".
- No two tiers share a value or method. Every tier is stated in the rule and implemented in compute.
- Realism (O-12) is unchanged in kind. New tiers (card activation days, pension disregard, proportional allowance) are plausible business treatments; recorded as observation only.

### findings (revision_2)

| Id | Verdict | Status |
| --- | --- | --- |
| F-1, F-2, F-2b, F-3, F-4, F-5, F-6, F-7, F-8, F-9, F-10 | — | closed (evidence above) |
| R2-F1 | SOURCE-TASK RED (demonstrated in `0.md`) | **new**: the base EB minimum-weeks-of-employment test is back in force with no record or persona answer to establish it |
| R2-O1 … R2-O3 | observation | new, no world consequence |
| O-3, O-5, O-6, O-12, O-13 | observation | unchanged (reworker left them with reasons; none is a red light) |

### closing_checklist (revision_2)

Written after the round-2 reveals (2026-10-10T18:12:42Z). The revision_2 charter-global section above was frozen before them.

| Task | Policy | Tree | Factors | Unique solution | Overall |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | SOURCE-CHAIN RED (R2-F2: false "parent is not exhausted" in edge_load_bearing; proof only) | PASS | SOURCE-TASK RED (R2-F1: EB minimum-weeks eligibility re-inherited with no record or persona answer) | RED |
| 1 | PASS | PASS | PASS | PASS | PASS |

- All round-1 REDs (F-1, F-2, F-2b, F-3, F-5, F-6, F-7, F-8, F-9, F-10, the overpay seed, both false proof figures) are verified closed against the artifacts.
- F-4 is closed with residual observation R2-O3.
- Step 4 items that hold:
  - one-to-one audit files;
  - disjoint scopes covering the 8 policies;
  - independent uuid8s;
  - every tree has 3 prerequisites, ≥2 value edges, a user write, and is acyclic;
  - every computation has 4–6 factors with ≥2 parameter, ≥1 genuine method, honest baselines and all-baseline numbers ≠ gold;
  - multi-source and cross-difficulty factors are present and seeded consistently.
- The difficulty is **not closed** because of task 0 (R2-F1, R2-F2). The instantiation gates were not re-run by this auditor; the coordinator's round-2 snapshot is all rc=0.

## revision_3

### charter_global_frozen (revision_3)

- Re-audit round 3. Frozen 2026-10-10 19:02Z (host UTC clock), before any round-3 GT field was read. revision_1 and revision_2 are preserved unchanged above.
- Inputs (sha256 re-checked against the coordinator's brief):
  - `claim.extended.yaml` a93c5ea904a5c9f47a0ef95111d78d49b4c75d09c76ee61f621f91d6f3bf71f9: **changed** from e2a2d2d0…, so every charter-global section is re-derived below.
  - `task_tools.py` a84f7fd3…: unchanged, so `action_binding_and_uuids` is carried forward on that hash.
  - Views c5468a55…ef2e and ff08aa20…a360: unchanged (`tasks/0.json` bb166333…a548, `tasks/1.json` df3014cd…264c).
- Base copy: still key-for-key equal to the blueprint product.
- The coordinator's gate snapshot after rework is all rc=0 (cited).
- contamination_disclosure: the round-1 and round-2 GT of both tasks were read in earlier revisions, so this derivation is not naive to them. No round-3 GT field and no worklog were read before the revision_3 freezes.
- Method used to find what changed (no copy of the round-2 charter was kept):
  - re-dump every extended policy;
  - compare overwrite, params, factors, ladders, baselines and compute names against the revision_2 dumps;
  - check that key revision_2 rule sentences are still present verbatim;
  - replay the derived write sequences of both tasks through the charter's own compute on the views. All figures — per-factor and all-baseline — equal revision_2.
- The only change found is in `claim_ext_extension_entitlement`.

### policy_conflict_scan / rule_compute_equivalence / prerequisite_graph / prerequisite_sentences (revision_3)

- **Unchanged from revision_2 except EB.** For the seven other policies, overwrites, params, factor ladders and baselines are identical. Their `compute_basis` quotations are verbatim in their rules, their prerequisite sources are verbatim in their rules, and the replayed figures are identical. The revision_2 conclusions are carried forward.
- **EB.**
  - A new rule sentence: "For an Extended Benefits claim, the claimant shows the minimum weeks of full-time base-period employment through their wage equivalent: the parent claim's base-period wages must be at least the wage-weeks test times the parent's weekly benefit amount, and an Extended Benefits claim whose parent wages fall short of that is determined with a maximum benefit amount of zero."
  - It is implemented as `result = 0 if F('base_period_wages') < K('wage_weeks_test') * wba else …`, and quoted in `compute_basis.result`. Rule and compute are equivalent.
  - The eb_frac basis sentences are verbatim and match the compute (below).
  - The EB prerequisite edges and sentences are unchanged.

### override_declarations (revision_3)

- **R2-F1 closed at the charter level.** The EB `overwrite` now has a second entry. Its `superseded_clause` "the claimant must show the minimum weeks of full-time base-period employment" is a verbatim clause of base `claim_extended_program_entitlement`. Its `replaced_by` is the wage-equivalent sentence above, verbatim in the EB rule.
- The test is now record-visible: parent `base_period_wages` against 40 × parent `weekly_benefit_amount`.
- It matches a real EB alternative: federal EB lets a state accept 40 × WBA in base-period wages in place of 20 weeks of work.
- Residual observation R3-O1: "determined with a maximum benefit amount of zero" stands where the business would issue an ineligibility. The EB rule's first sentence ("… and makes the claim active") would then activate a zero-balance claim. No world of this difficulty reaches it.

### factor_ladders (revision_3)

`eb_fraction` (parameter) was re-tiered:

| Tier | Condition | Value |
| --- | --- | --- |
| 1 | ≥ 20 weekly payments on the parent **and** parent BPW ≥ 60 × WBA | 0.52 |
| 2 | ≥ 20 weekly payments **and** BPW < 60 × WBA | 0.51 |
| fall-through | fewer than 20 weekly payments | 0.5 |

- Why it had to change: the round-2 tiers keyed on BPW ≥ 40 × WBA. After the new gate, every customer who reaches this write meets that, so the round-2 ladder would have rested on a universal condition. The re-tiering removes this.
- The fall-through stays reachable. Under the gate, BPW/WBA lies in about [40, 104] (BPW ≤ 4 × HQW, WBA = HQW/26), so the 60 × WBA split is reachable on both sides. The maximum benefit amount can be as low as 0.3333 × 40 × WBA ≈ 13.3 WBA, so a parent can be exhausted with fewer than 20 weekly payments.
- Every non-fall-through tier is a conjunction over distinct records (parent ledger + claims row): multi-source.
- Tiers are disjoint and the values are distinct.
- The rule, the `compute_basis` and the `decides` binding agree in both directions.
- The label is honest (number only).
- Baseline 0.5 equals the fall-through and `baseline.rule` ("the Extended Benefits fraction is one half").
- The EB still has 4 factors (3 parameter, 1 method); all other policies are unchanged.

### findings (revision_3)

| Id | Status |
| --- | --- |
| R2-F1 | closed at the charter level; task 0 demonstration in `0.md` revision_3 |
| R2-F2 | per-task proof field; checked in `0.md` after the reveal |
| R3-O1 | new observation (zero-MBA determination wording), no world consequence |
| R2-O1, R2-O2, R2-O3, O-3, O-5, O-6, O-12, O-13 | unchanged observations |
| New red lights at the charter level | none |

### closing_checklist (revision_3)

Written after the round-3 reveals (2026-10-10T19:02:37Z). The revision_3 charter-global section above was frozen before them.

| Task | Policy | Tree | Factors | Unique solution | Overall |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | SOURCE-CHAIN RED (R3-F1: `design_rationale` still says "the parent is not exhausted") | SOURCE-FACTOR RED (R3-F2: `design_rationale` names the removed round-2 eb_fraction tier) | PASS | RED (proof text only) |
| 1 | PASS | PASS | PASS | PASS | PASS (no regression) |

- R2-F1 is closed (declared, record-visible wage-equivalent test; met on task 0's world).
- R2-F2 is closed in `prerequisite_closure` but not in `design_rationale` (R3-F1).
- The eb_fraction re-tiering is sound: it is no longer universal, its fall-through is reachable, it is multi-source and it bears weight (6,854 vs 7,089).
- No charter-level red light remains. Every Step 4 structural item holds, as in revision_2.
- The difficulty is **not closed**, solely on the two task-0 `design_rationale` sentences, which carry no scored value. The instantiation gates were not re-run by this auditor; the coordinator's round-3 snapshot is all rc=0.

## revision_4

### charter_global_frozen (revision_4)

- Re-audit round 4. Frozen 2026-10-10 20:02Z (host UTC clock), before any round-4 GT field was read. Revisions 1–3 are preserved above.
- Hashes, re-checked:
  - `claim.extended.yaml` a93c5ea9…71f9 and `task_tools.py` a84f7fd3…a29a9: both **unchanged** since revision_3. Per the re-audit rule, every charter-global section of revision_3 (and the sections it carried forward) is **carried forward by reference on these two hashes**, not re-derived. No charter-level red light stands.
  - Views c5468a55…ef2e and ff08aa20…a360: unchanged.
  - `tasks/0.json` 0cef5e05…c37c and `tasks/1.json` 34251016…b902: both changed (proof/GT fields only).
- contamination_disclosure: the GT of rounds 1–3 was read in earlier revisions; no round-4 GT field was read before the revision_4 freezes.

### closing_checklist (revision_4)

Written after the round-4 reveals (2026-10-10T20:02:21Z).

| Task | Policy | Tree | Factors | Unique solution | Overall |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS | PASS |

Step 4 checklist:
- **Audit files:** they map one-to-one onto tasks 0 and 1, `_difficulty.md` sits alongside them, revisions 1–4 are preserved, and every comparison section ends in a verdict. The latest verdicts are PASS for both tasks.
- **Scope and tools:** all 8 extended policies are covered, and the two task scopes are pairwise disjoint over their whole problem trees. Task tools and GT are closed, and the 8 task tools carry independent, frozen uuid8s.
- **Problem trees:** each tree has 3 prerequisite problems and at least 2 `value_input` edges (task 0: 3, task 1: 4). Each has an `owner=user` write (task 0: the payment election; task 1: the phone certification). The difficulty-wide prerequisite graph is acyclic.
- **Computations:** every computation has an honest, self-sufficient baseline whose all-baseline number differs from gold (task 0: 0, 2, 18, 6,024; task 1: 390, 371, 184.0, 425). Each declares 4–6 factors, with at least 2 `parameter` and at least 1 genuine `method`, and every ladder is three-tier, disjoint, stated in full in its rule and bears weight. Each task has multi-source factors and cross-difficulty factors with charter-consistent seeds (task 0: idv, overpay; task 1: appeal, withhold, overpay).
- **Gates:** the instantiation-stage gates on this final form are the coordinator's round-4 re-run, all rc=0 (cited, not re-run by this auditor; check_traceability is deferred to render).

**The difficulty passes the source-layer policy-task audit.** Open observations (not grounds for rework) are listed in the revision_2 and revision_3 findings tables.

## revision_5

### charter_global_frozen (revision_5)

- Re-audit round 5, triggered by policy-side items raised by the render-layer KB audit. Frozen 2026-10-10 21:30Z (host UTC clock), before any round-5 GT field and before any item of `audits/policy_kb/...` was read. Revisions 1–4 are preserved above.
- Inputs (sha256 re-checked):
  - `claim.extended.yaml` 5e0f3f24919a5ed790b63f4f4fcf73f52ce0924c36e32bff2f8be056e2f29420: **changed**, so the charter-global sections are re-derived below.
  - `task_tools.py` a84f7fd3…: unchanged, so `action_binding_and_uuids` is carried forward.
  - Blind views c5468a55…ef2e and ff08aa20…a360: unchanged.
  - `tasks/0.json` 1c83cc08…f90e and `tasks/1.json` 15e1f814…8746: changed.
  - Also present in the views directory: `task_*.runtime.json` (not mine; not opened).
- contamination_disclosure: the GT of rounds 1–4 was read earlier. The coordinator's brief named the seven KB-audit item categories (weekly full-time threshold, child-support order lookup, verification-days lookup, holiday `min_hours`, inputs never read by standard methods, Extended Benefits training-week default, stale authoring note); only those labels were known before this freeze.
- Base copy: still key-for-key equal to the blueprint product.

### changes found and rule/compute equivalence (revision_5)

The compute, baseline, inputs, `cross_category` and ladders of all 8 policies were dumped and compared against the revision_2/3 dumps. Changes found:

| Policy | Change | Rule ⇄ compute |
| --- | --- | --- |
| regular_weekly_payable | Threshold sentence now says it "is both the hours at or above which the week pays nothing and the hours against which the low, mid and part-week fractions are measured"; `gross_q` replaced by `hours_q` in `da_paid` (drops the vacuous `gross_q >= 0`) | equivalent: `result` zeroes at `hours >= thr`, and the fractions use `thr` |
| dependency_disallowance | Child-support factor now "at least one … Current Support Order binding the claimant, on any of the claimant's claims, stands at status active or suspended" / "none active or suspended and at least one … at status requested"; compute `XCOUNT` over the claimant's orders by status (was `CFIELD` first row) | equivalent; tiers disjoint; multi-order worlds resolved by the rule |
| payment_election_lead | Theft tier now "the most recently verified Identity Theft Victim Re-Verification case on the claim"; compute `XLATEST` (was `CFIELD` first row) | equivalent |
| extension_entitlement | `baseline.rule` now "the training weeks added are zero and each training week is valued at the weekly benefit amount, so the training addition … is zero"; inputs list the overpay principal sum; `cross_category` note restated | baseline self-sufficient; sentences verbatim in the rule |
| holiday_pay_report | `baseline.params` drops `min_hours` (unused by the HQW-rate standard method) | equivalent |

Mechanical sweep over all 8 policies:
- every `compute_basis` quotation and every `baseline.rule` sentence is verbatim in its rule;
- every prerequisite `policy_source` is verbatim in its rule;
- every `baseline.params` entry is read by compute;
- no authoring-viewpoint phrase ("this task", "audit", "gold", "revision", "worklog", "at the opening") appears in any policy.

Observation **R5-O1**: the weekly payable `baseline.params` still lists `waiting_week_count`. Compute reads it (`served < P('waiting_week_count')`), but `baseline.rule` no longer mentions it, because that gating lives in the prerequisite sentence and base `claim_evt_waiting_week`. No reading changes.

### override_declarations / prerequisite_graph / prerequisite_sentences / policy_conflict_scan (revision_5)

- Overwrites: 2 / 1 / 3 / 2 / 3 / 0 / 0 / 4 per policy, the same entries as revision_3.
- Prerequisite edges and sentences: unchanged (all sources verbatim; same nine edges; acyclic).
- Scopes: unchanged and disjoint.
- The revision_3 conclusions are carried forward on these grounds. The threshold sentence's base override (base "A week in which hours worked reach the full-time hours threshold …") stays declared in the weekly `overwrite`.

### factor_ladders (revision_5)

- Only the wording of `supported_removed_dependent` and `verification_days` changed. Both remain three-tier, disjoint, distinct-valued and honestly labelled `parameter`, and each fall-through equals its baseline.
- Factor counts and method/parameter mix are unchanged from revision_3 (4/4/4/4/5/4/5/6; one genuine method each).

### findings (revision_5, pre-reveal)

- No charter-level red light.
- New observation R5-O1.
- Earlier observations unchanged.

### kb_audit_policy_side_items (revision_5, read after the freeze)

Read after 21:31Z: the "Policy-side notes" and rule/compute lines of `audits/policy_kb/weekly_certification_and_benefit_payment/0.md` and `1.md`. Each item was checked against the round-5 charter (5e0f3f24…):

| KB-audit item | Status in round-5 charter | Evidence |
| --- | --- | --- |
| Weekly payable: standard sentence "program's full-time hours threshold pays nothing" vs compute `hours >= thr`; vacuous `gross_q >= 0` | **closed** | The factor sentence now states that the threshold "is both the hours at or above which the week pays nothing and the hours against which the low, mid and part-week fractions are measured", and compute `result` uses `thr`. The standard sentence remains the baseline, which the factor replaces. `da_paid` now reads `hours_q`; the `gross_q` term is gone. |
| Disallowance: `CFIELD('withhold', …)` without a claim filter vs "binding the claimant" | **closed** | The rule now says "on any of the claimant's claims" with explicit active/suspended → requested precedence; compute `XCOUNT` by status over the claimant's orders. |
| Election verification lookup (`CFIELD` first row; "of any other pathway") | **closed** | The rule now reads "the most recently verified Identity Theft Victim Re-Verification case" and "of whatever pathway"; compute uses `XLATEST` for both. |
| Holiday `baseline.params` lists unused `min_hours` | **closed** | `min_hours` was removed from `baseline.params`; it remains a param of the rate ladder only. |
| Inputs listed but not read by the standard method (WBA in the redetermination and disallowance computation documents) | **no charter defect** | Both charters' compute read `wba` only through their ceiling factors, which is correct. `baseline.rule` does not name WBA, and the residue is in the rendered inputs tables (render side). Nothing in the charter needs or received a change for this. |
| EB baseline training-week default carried only through the valuation ladder | **closed** | `baseline.rule` now: "the training weeks added are zero and each training week is valued at the weekly benefit amount, so the training addition … is zero". |
| Stale note: EB `cross_category[overpay].note` "classification penalty share" | **closed** | The note now reads "counts the fraud overpayments against the parent claim and sums the principal of its non-fraud overpayments at status established", matching compute. |
| Facet residues of `parameter_schema` (`eb_regular_mba_fraction`, `eb_min_weeks_employment`) | **outside this audit's write/verdict scope** | These are blueprint-level texts, not this difficulty's charter; recorded as observation R5-O2 for the blueprint owner. |
| "counted earnings" / "hours base" defined in sibling factors | unchanged | Observation (the source couples them consistently). |

### closing_checklist (revision_5)

Written after the round-5 reveals.

| Task | Policy | Tree | Factors | Unique solution | Overall |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS | PASS |

- Every policy-side item raised by the KB audit that lies in this charter is closed, or verified not to be a charter defect.
- No new red light, and no regression: all gold values, per-factor figures, all-baseline figures and edge figures are unchanged since revision_2/3/4.
- Step 4 items all hold as listed in revision_4's checklist (re-checked on the round-5 charter: coverage, disjoint scopes, uuid8s, trees, acyclicity, 4–6 factors with ≥2 parameter / ≥1 method, honest self-sufficient baselines, multi-source and seeded cross-difficulty factors).
- The instantiation gates on this final form are the coordinator's round-5 re-run, all rc=0 (cited).
- Observations: R5-O1, R5-O2, and the earlier ones.
- **The difficulty passes the source-layer policy-task audit (revision_5).**
