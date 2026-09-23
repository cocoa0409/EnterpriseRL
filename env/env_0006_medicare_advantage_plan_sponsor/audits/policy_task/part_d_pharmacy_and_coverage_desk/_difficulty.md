# Policy-task audit — part_d_pharmacy_and_coverage_desk / charter-global

## charter_global_frozen

- freeze time: 2026-09-21 (audit session), pre-reveal. Nothing in this section is derived from any masked GT field.
- auditor: independent source-layer auditor (not the instantiating agent).
- frozen inputs, sha256[:16] recomputed on disk at freeze time:
  - `env/env_0006_medicare_advantage_plan_sponsor/tasks/part_d_pharmacy_and_coverage_desk/pdp.extended.yaml` = `395a18d5ba3507c7` (matches brief)
  - `env/env_0006_medicare_advantage_plan_sponsor/tasks/part_d_pharmacy_and_coverage_desk/task_tools.py` = `d8da38d60b74418b` (matches brief)
  - masked views `_masked_views/0.masked.json` = `1e7a3e7485b34dde`, `_masked_views/1.masked.json` = `1bb1077d3c06fc19` (both match brief)
- fields permitted: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/pdp.yaml`, `blueprint/products/egwp.yaml`, `blueprint/products/allowance.yaml`, `blueprint/products/advantage.yaml`, the extended charter, `task_tools.py`, and each task's `frozen_time` / `user_scenario` / `initial_state` only.
- fields explicitly masked and not read before this freeze: `evaluation_criteria`, `computations` (incl. `expected`, `factor_trace`, `factor_sensitivity`, `baseline_result`, step/arg), `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`.

### entry_conditions

The brief supplied the gate snapshot with actual output lines for `check_extended.py`, `check_task_tools.py`, `replay_tasks.py`, `check_solvability.py`, `check_compute.py`, `check_grounding.py` and `check_cross_fire.py`, all green, plus the two masked-view hashes. `check_traceability` is correctly deferred to the render stage and `check_cache_diff` is informational. Entry conditions are complete; the gates were cited, not re-run, at freeze time. A green gate is the qualification to enter this audit, not evidence of correctness.

**Hazard recorded (not contamination).** The session scratchpad `/tmp/claude-10250/.../scratchpad` already contained the *instantiating* agent's working files (`t0_eval.py`, `ec1.json`, `calc0.py`, `rationale0.md`, `dr0.txt`, `state0.json`, …), which carry GT. The auditor read none of them: only filenames and byte sizes were ever visible, from one `ls`. All audit working files were written to a separate `_audit/` subdirectory and every file read back was one the auditor had written. No scored value, gold parameter or intermediate reached the auditor from that path.

### policy_conflict_scan

Five extended policies, five distinct `target_tool`s, five distinct `computes`:

| policy | target_tool | computes | subject | trigger |
|---|---|---|---|---|
| `pdp_ext_penalty_relief` | `post_penalty_removal_e1c246c8` | `removal_amount` | `pdp_penalty_removal` | state_due |
| `pdp_ext_premium_arrears_settlement` | `authorize_arrears_payment_7dfec3b3` | `payment_amount` | `pdp_premium_payment` | on_request |
| `pdp_ext_troop_restatement` | `restate_out_of_pocket_total_a40a5cef` | `restated_out_of_pocket_total` | `pdp_coverage_stage_update` | state_due |
| `pdp_ext_exception_approval_term` | `issue_exception_decision_dd13544d` | `approval_term_days` | `pdp_coverage_determination_decision` | state_due |
| `pdp_ext_counter_cost_share` | `settle_counter_fill_eaef344a` | `member_paid_amount` | `pdp_pharmacy_claim_adjudication` | on_request |

No two policies claim the same subject event, the same target tool or the same computed quantity. Time anchors are disjoint in kind (`posted_date` for the premium pair, `fill_date` / `received_date` for the pharmacy trio) and all resolve against the single `frozen_time` clock. Cross-category read boundaries are declared per policy and do not overlap: `penalty_relief` reads `egwp` only; `troop_restatement` reads `allowance` only; the other three declare `cross_category: []`.

Claimed scopes are pairwise disjoint and jointly complete over the five extended policies:
- task 0 spans `{pdp_ext_premium_arrears_settlement (root), pdp_ext_penalty_relief}`;
- task 1 spans `{pdp_ext_counter_cost_share (root), pdp_ext_troop_restatement, pdp_ext_exception_approval_term}`.

Base-copy fidelity: every key of `blueprint/products/pdp.yaml` (`category`, `display_name`, `binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`, `measures`, `policies`) compares **equal** to the extended file's copy; the only extra key is `extended_policies`. The base copy has not been rewritten.

### rule_compute_equivalence

Swept sentence by sentence over all five policies, in both directions. Three defects found; they are recorded under `findings` as **F-1**, **F-2** and **F-3**. Everything else is lossless: every quantity, window, filter, tier, branch, cross-category read, acting base, cap/floor, rounding mode and rounding point in each `rule` has a verbatim `compute_basis` quotation and a restricted-expression implementation, and no `compute` binding introduces a basis the rule does not state.

Rounding conventions were checked individually and are faithful: `RND(x,1)` for "rounded to the nearest ten cents" (penalty relief), `RND(x,2)` for "rounded once to two decimal places" (arrears, TrOOP, counter), whole days with `MX(K('floor_days'), …)` for the approval term, and in every case the rule's stated rounding *point* ("the multiplication is carried out first and its product rounded once … and only that rounded product is then compared with the ceiling"; "no intermediate is rounded before that") matches the order of operations in `compute`.

### action_binding_and_uuids

Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). No policy's subject, base refs, tool docstring or terminal state admits a second business reading, and no confirmation, review or wait outside the policy is added by any docstring.

The five uuid8 tails are `e1c246c8`, `7dfec3b3`, `a40a5cef`, `dd13544d`, `eaef344a`. They are pairwise distinct, share no common prefix, are not adjacent or sequential in value, and show no sign of batch derivation from a common stem. Each is frozen with its tool in the one module.

Two docstring observations are recorded as **F-7** and **F-8**.

### prerequisite_graph

Three edges, all declared, over a graph of five nodes:

```
pdp_ext_premium_arrears_settlement --value_input(penalty_outstanding)--> pdp_ext_penalty_relief
pdp_ext_counter_cost_share --value_input(troop_on_record)------------> pdp_ext_troop_restatement
pdp_ext_counter_cost_share --state_gate(pdp_point_of_sale_cost_share.determination_on_record)--> pdp_ext_exception_approval_term
```

- `prerequisite` is filled in on every policy; `pdp_ext_penalty_relief`, `pdp_ext_troop_restatement` and `pdp_ext_exception_approval_term` carry `[]`.
- Every `problem` names another extended policy id in this file; none names a base policy and none names itself. The graph is a DAG (two disjoint trees, no back edge, no cross-task edge, hence no cycle at difficulty level).
- Every `policy_source` is verbatim locatable in the **blocked** policy's own `rule` — confirmed by string match against `rule` for all three edges.
- `form` is `state` on all three edges and no `fallback_reason` is present on any; this is correct, since `fallback_reason` must appear exactly on action-form edges.
- `kind` matches `gate` in each case: the two `value_input` edges name `penalty_outstanding` and `troop_on_record`, and both are real binding names in the blocked policy's own `compute`; the `state_gate` edge names `pdp_point_of_sale_cost_share.determination_on_record`, which **is** a real eligibility entry of kind `authorization` on the base policy `pdp_point_of_sale_cost_share` (condition: "Where the fill's formulary tier is one the tier enforces prior authorisation on, an approved coverage determination covering that product and still inside its approved through date is on record.").
- `resolved_by` is in each case the depended-on policy's own `target_tool`, and each genuinely moves the thing `effect` describes: `post_penalty_removal_e1c246c8` adds to `penalty_removed_total`; `restate_out_of_pocket_total_a40a5cef` is the only tool in the module that writes `pdp_enrollments.troop_accumulated`; `issue_exception_decision_dd13544d` is the only tool that creates an `approved` `pdp_coverage_determination_decision`.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears anywhere in the three `prerequisite` blocks.

One scope observation on edge 2 is recorded as **F-6**.

### prerequisite_sentences

Four-point test on each of the three edges.

**Edge 1 — `pdp_ext_premium_arrears_settlement` → `pdp_ext_penalty_relief`.**
Sentence: *"The amount the member is asked to settle is fixed only after every coverage month whose penalty the record no longer owes carries its removal entry on the premium account."*
(1) Ordering connective: "only after". (2) Form: state — "every coverage month whose penalty the record no longer owes carries its removal entry on the premium account" names a record-visible state in the words the premium ledger uses, with no performer, action or tool. (3) No tool name, policy id, snake_case token or row id. (4) Strength matches the declared `condition` exactly (both say: every penalty charge for a month no longer owed carries a matching removal entry).
Single write bringing the state about: `post_penalty_removal_e1c246c8` is the only tool in the module that creates a `pdp_premium_ledger` row with `event_type="pdp_penalty_removal"`. No second candidate, so the hop resolves uniquely.
Derivation in one reading: the sentence says the settlement waits on removal entries standing for months no longer owed → the reader looks for the policy whose own rule describes posting such an entry → `pdp_ext_penalty_relief`, whose rule says "the coverage months it covers are relieved together on one removal entry, which names the earliest penalty charge standing unrelieved on the account" → that policy's `target_tool` is the resolving action. No second reading.
The depended-on rule (`pdp_ext_penalty_relief`) does **not** restate this sentence; the blocked rule carries no second wording of the dependency and no other problem's tool name or id.

**Edge 2 — `pdp_ext_counter_cost_share` → `pdp_ext_troop_restatement`.**
Sentence: *"What the member pays at the counter is not fixed before the out-of-pocket total standing on the drug plan enrollment agrees with every fill the pharmacy record shows paid and every fill it shows backed out for the contract year."*
(1) "not fixed before". (2) State form, record-visible, no performer. (3) No tool/id/snake_case. (4) Scope is **narrower** than the declared `condition` — see **F-6**.
Single write: `restate_out_of_pocket_total_a40a5cef` is the only tool writing `pdp_enrollments.troop_accumulated`. Unique hop.

**Edge 3 — `pdp_ext_counter_cost_share` → `pdp_ext_exception_approval_term`.**
Sentence: *"What the member pays at the counter for a fill on a tier the plan enforces prior authorisation on is not fixed until an approved coverage determination for that product stands on the member's coverage determination record, good through a day not earlier than the fill date."*
(1) "not fixed until". (2) State form: "an approved coverage determination … stands on the member's coverage determination record, good through a day not earlier than the fill date" — a record-visible state in table words. (3) Clean of tool names and ids. (4) Exactly the strength of the `condition`, which repeats the approved-outcome and approved-through-date conjuncts.
Single write: `issue_exception_decision_dd13544d` is the only tool creating a determination row with `decision_outcome="approved"`. Unique hop.

**Cross-problem order elsewhere in the rules.** Every sentence of all five `rule` fields carrying an ordering or timing cue (`before`, `after`, `only after`, `until`, `not until`, `first`, `prior to`, `once`) was enumerated. Apart from the three prerequisite sentences above, every hit is intra-computation ("The multiplication is carried out first and its product rounded once…", "no intermediate is rounded before that", "a premium rate changed after the fact", "a charge raised in error", "relieved at once"). **No rule states a cross-problem order that grounds no declared edge**, and no task's tree rests on a cross-problem order stated only in a base rule.

**Docstring silence about sequence.** Four of the five docstrings are clean. One is not — see **F-7**.

### override_declarations

Sentence-by-sentence sweep of each extended policy against every entry in its `base_policy_refs`. Findings only; each affected task's file demonstrates the consequence against its own world.

**`pdp_ext_penalty_relief`** vs `pdp_premium_posting`, `pdp_late_enrollment_penalty`.
- `pdp_premium_posting` — "A credit adjustment and a penalty removal each name the single charge they relieve and the reason, and neither may exceed the amount of that charge." **Declared** in `overwrite` and replaced by the one-entry aggregate relief. Merged semantics unique.
- `pdp_premium_posting` — "Money the member pays is posted against the oldest unpaid coverage month first, and within a coverage month against the premium components before the penalty." Not hit by any `overwrite`; **inherited in full**. It is what fixes the `billing_period` argument of the settlement write.
- `pdp_premium_posting` — "An overpayment is refunded by the channel the money arrived on…" / "A member's statement that they have paid is a reason to look for the money…" Inherited; the second is restated compatibly in the extended rule ("the member's own recollection … is a reason to read the account rather than a figure to work from").
- `pdp_late_enrollment_penalty` — "the penalty is removed and every month of it credited back once CMS confirms the earlier coverage was creditable". **Declared** in `overwrite`.
- `pdp_late_enrollment_penalty` — "The count of months is CMS's, not the plan's: the plan bills what CMS supplies and never adds or removes a month on its own view of the member's history." **NOT declared, and extended handles the same quantity differently.** This is an undeclared override; recorded as **F-4**.
- `pdp_late_enrollment_penalty` — "the member's own statement that they had drug coverage starts that enquiry but never removes the penalty by itself." Inherited and compatibly restated ("The member's own account … opens the enquiry and never fixes any of these figures").
- `pdp_late_enrollment_penalty` — monthly penalty formula and the LIS / age-65 reset branches: extended's `published_monthly_penalty` implements the formula faithfully (`RND(P('national_base_beneficiary_premium') * P('late_enrollment_penalty_rate_percent') / 100 * F('late_enrollment_penalty_months'), 1)`); the LIS and age-65 branches are untouched and inherited.

**`pdp_ext_premium_arrears_settlement`** vs `pdp_premium_posting`, `pdp_premium_billing`, `pdp_premium_delinquency`, `pdp_late_enrollment_penalty`.
- `pdp_premium_posting` — "An overpayment is refunded by the channel the money arrived on and never held against a coverage month the plan has not yet billed." **Declared**; replaced by the advance-month clause.
- `pdp_premium_posting` — "No payment entry carrying the same remittance reference and the same amount is already posted on this enrollment." **Declared**; replaced by the plan-issued telephone payment reference.
- `pdp_premium_delinquency` — "A partial payment does not cure the delinquency and never restarts the clock." Inherited and compatibly restated in the extended rule. The grace-period length, the counting rule and the termination/reinstatement branches are untouched.
- `pdp_premium_billing` — premium split into basic and supplemental components, penalty billed as its own component, quarterly cadence: all inherited; the extended windows aggregate over `event_type` and never re-split a component.
- No undeclared conflict found for this policy.

**`pdp_ext_troop_restatement`** vs `pdp_coverage_stage_progression`, `pdp_transition_and_utilization_management`, `pdp_point_of_sale_cost_share`.
- `pdp_coverage_stage_progression` — "Only what the member or a qualifying third party actually paid counts toward the threshold: plan payments, premiums and the late enrollment penalty never count". **Declared**; replaced by the clause that adds the negotiated-price cap and the supplemental-card exclusion.
- `pdp_coverage_stage_progression` — "Reversing a fill takes its member payment back out of the accumulator and can return the member to an earlier stage; the stages are restated from the accumulator rather than kept as a separate fact." Inherited, and restated compatibly at the end of the extended rule.
- The **replacement clause itself** contradicts one of the extended policy's own ladder outcomes: recorded as **F-3**.

**`pdp_ext_exception_approval_term`** vs `pdp_coverage_determination_timeliness`, `pdp_point_of_sale_cost_share`, `pdp_transition_and_utilization_management`. `overwrite: []`, checked by the same sentence-by-sentence standard. The base's decision deadlines, hour/day counting rule, "a prescriber's request for expedition is always granted" and "An approval holds good until its approved through date" are all inherited and none is weakened: the extended policy fixes only the *length* of an approval run, a quantity the base nowhere fixes. The extended's closing sentence ("A request the prescriber has asked to have expedited is always expedited…") restates the base compatibly. **No undeclared override.**

**`pdp_ext_counter_cost_share`** vs `pdp_point_of_sale_cost_share`, `pdp_transition_and_utilization_management`, `pdp_coverage_stage_progression`.
- `pdp_point_of_sale_cost_share` — "the member never pays more than the negotiated price however the multiplier falls". **Declared**; replaced by the ceiling clause.
- `pdp_point_of_sale_cost_share` — tier/pharmacy-standing selection of the one-month figure and the extended-supply multiplier: inherited and implemented faithfully.
- `pdp_point_of_sale_cost_share` — insulin cap, zero-cost vaccines, LIS copay substitution, out-of-network footing: inherited untouched; none is reached on either task's world (`low_income_subsidy_level: none` on both customers).
- `pdp_coverage_stage_progression` — "A fill that straddles a stage boundary is split at the boundary, so the member pays the earlier stage's cost share only up to the distance remaining and the later stage's terms on the rest." Inherited; the extended `stage_boundary_split` ladder is a faithful proportional implementation.
- The declared replacement is nevertheless **not** what the factor ladder implements: recorded as **F-1** and **F-2**.

### factor_ladders

Structure only. Whether a factor bears weight is a fact about one world and lives in each task's `factor_weight`.

| policy | factors | `parameter` | `method` | multi-source tiers | `cross_difficulty` |
|---|---|---|---|---|---|
| `pdp_ext_penalty_relief` | 4 | 3 | 1 | `group_coverage_months_proved`, `relieved_month_window`, `monthly_penalty_basis_rule`, `relief_ceiling_rule` | `egwp` (1) |
| `pdp_ext_premium_arrears_settlement` | 6 | 3 | 3 | `charged_month_window`, `settled_payment_basis`, `credit_taken_off`, `penalty_standing_basis`, `penalty_share_asked`, `further_month_asked` | none |
| `pdp_ext_troop_restatement` | 4 | 2 | 2 | `gathered_fill_window`, `card_met_at_pharmacy`, `reversal_taken_back_out` | `allowance` (1) |
| `pdp_ext_exception_approval_term` | 6 | 4 | 2 | `term_counting_basis`, `standing_denial_allowance`, `quantity_limit_allowance` | none |
| `pdp_ext_counter_cost_share` | 6 | 3 | 3 | `one_month_figure`, `acting_price_basis`, `stage_boundary_split`, `counter_price_ceiling`, `deductible_still_to_be_met` | none |

Every policy declares between 4 and 6 factors with at least 2 `parameter` and at least 1 `method`. Every ladder has exactly three tiers, the fall-through counted. Per task: task 0 carries a multi-source factor (`group_coverage_months_proved`) and a `cross_difficulty` factor (`group_coverage_months_proved`, reading `egwp`); task 1 carries both in `card_met_at_pharmacy` (reading `allowance`).

- **Binding disjointness / `decides`:** every factor's `bindings` set is disjoint from every other factor's within its policy, and every `decides` names an *input* binding, never `result`. Confirmed for all 26 factors.
- **Tier disjointness as stated:** each ladder's two stated tiers are mutually exclusive by construction (each pair turns on a strict comparison or on complementary categorical values), and the fall-through takes the remainder.
- **No two tiers sharing a value or method, as stated:** holds for 25 of 26 factors. The one exception is recorded as **F-5**.
- **Every tier stated in the `rule`:** holds for 25 of 26 factors. `counter_price_ceiling`'s first tier is stated in `factors` and in `compute` but in **no sentence of the `rule`** — recorded as **F-1**.
- **Every tier implemented in `compute`:** holds for 25 of 26. `run_anchor`'s first tier is stated in the `rule` and in `factors` with one threshold and implemented in `compute` with another — recorded as **F-2**.
- **Label honesty:** each `method` tier selects a genuinely different algorithm (a window, an aggregation basis, a counting cycle, an anchor, a candidate order) and each `parameter` tier a number. Four factors sit on the boundary and are recorded as an observation, **F-9**.
- **Method tiers naming a rule the charter states:** every `method` tier's algorithm is one the charter's own prose states; none invents a computation rule from outside.
- **Baseline self-sufficiency:** each policy's `baseline.rule` is a subset of its `rule` sentences and yields a definite number from the records with no factor applied, and every factor's fall-through tier is the baseline — with one exception, **F-1**. Two policies' `baseline.params` do not name the figures the baseline method uses: **F-10**.

### findings

---

**F-1 — `SOURCE-POLICY RED` + `SOURCE-FACTOR RED`. `counter_price_ceiling`'s top tier exists in `compute` and `factors` but in no sentence of the rule, and its declared baseline contradicts the policy's own `baseline.rule`.**

*Symptom.* The ceiling ladder has three tiers in `factors` and three branches in `compute`, but the `rule` states the default ceiling **unconditionally** and then gives only two exceptions.

*Root cause.* The author converted an unconditional default plus two exceptions into a three-tier ladder, inventing a condition for the default and demoting one exception to the fall-through.

*Evidence.* `pdp.extended.yaml`, `pdp_ext_counter_cost_share`.
- `rule` states, in full, only these three ceiling sentences:
  - (a) "The member never pays more than the ceiling the fill is held to, and the ceiling is the plan's negotiated price recorded for the fill the pharmacy is holding." — no condition attached;
  - (b) "Where the member's fills standing paid at a pharmacy carrying preferred cost sharing are at least one and the pharmacy holding this fill carries standard cost sharing, the ceiling is instead the largest plan negotiated price standing on a fill the member has paid for.";
  - (c) "Where the member's fills standing paid at a pharmacy carrying preferred cost sharing are fewer than one, the ceiling is instead the plan negotiated price recorded on the member's latest fill standing paid."
- `factors[counter_price_ceiling].ladder[0].when` = "the member's fills standing paid at a pharmacy carrying preferred cost sharing are at least one **and the pharmacy holding this fill carries preferred cost sharing**". **No sentence of the `rule` states this condition.**
- `compute` implements `price_ceiling: price_used if (preferred_fill_count >= 1 and rejected_fill_network == 'preferred_retail') else (largest_paid_price if (preferred_fill_count >= 1 and rejected_fill_network == 'standard_retail') else latest_paid_price)` — the first branch binds `price_used`, not `rejected_fill_price`, although `compute_basis[price_ceiling]` quotes sentence (a), whose subject is "the fill the pharmacy is holding".
- `factors[counter_price_ceiling].baseline.price_ceiling = latest_paid_price`, i.e. outcome (c). But `baseline.rule` contains sentence (a) verbatim and neither (b) nor (c). A reader computing the ceiling from `baseline.rule` alone gets the held fill's negotiated price, not the latest paid fill's.

*Demonstrated consequence.* Two, both on task 1's world (`_masked_views/1.masked.json`):
1. *A gap in the rule.* For a member with `preferred_fill_count >= 1` whose holding pharmacy is `mail_order` (neither preferred nor standard retail), the rule gives sentence (a) — the held fill's negotiated price — while `compute` falls through to `latest_paid_price`. Two conclusions, same situation.
2. *A decoration factor behind a straw-man baseline.* What `baseline.rule` states for this input on task 1's world is `rejected_fill_price` = **786.00**. Substituting 786.00 as the ceiling and replaying everything else unchanged gives `RND(MN(473.98, 786.00), 2)` = **473.98** — the scored value, **unchanged**. The factor only appears to bear weight because its declared `baseline` is `latest_paid_price` = **36.00**, a figure the policy's own baseline rule never selects, which drags the result to 36.00. Under the honest baseline the factor is decoration.

*Affected artifact and location.* `pdp.extended.yaml` → `extended_policies[pdp_ext_counter_cost_share]` → `rule` (ceiling sentences), `compute[price_ceiling]`, `compute_basis[price_ceiling]`, `factors[counter_price_ceiling]` (`ladder[0].when`, `baseline`), `baseline.rule`. Bears on **task 1**.

---

**F-2 — `SOURCE-POLICY RED`. `run_anchor`'s first tier is stated with one threshold in the rule and implemented with another in compute.**

*Symptom.* The rule and the ladder both gate the "anchor to the latest paid fill" branch on the member having at least the settled-therapy number of paid fills; `compute` gates it on having at least **one**.

*Root cause.* The compute expression substitutes a presence test (`>= 1`) for the rule's threshold test (`>= K('settled_therapy_fill_count')`, i.e. 3).

*Evidence.* `pdp.extended.yaml`, `pdp_ext_exception_approval_term`.
- `rule`: "Where a fill stands paid on the pharmacy record **and the member's fills standing paid for the contract year are at least the number the plan treats as settled therapy**, the run is anchored instead to the day of the member's latest fill standing paid, and the days from that day to the handling date are taken off as already elapsed."
- `compute_basis[anchor_offset]` quotes that sentence **verbatim**, including the threshold.
- `factors[run_anchor].ladder[0].when` repeats it: "…and the member's fills standing paid for the contract year are at least the number the plan treats as settled therapy".
- `compute`: `anchor_offset: DAYS(latest_paid_fill_date, NOW) if (paid_fill_count >= 1 and latest_paid_fill_date != None) else (DAYS(latest_request_date, NOW) if (paid_fill_count < 1 and requests_on_record >= 1) else 0)`.
- `params.settled_therapy_fill_count: 3`.

*Demonstrated consequence.* For a member with 2 paid fills and an open request, the two passages reach different conclusions in the same situation. Under the rule: tier 1 fails (2 < 3), tier 2 fails ("no fill stands paid" is false), so the fall-through applies and `anchor_offset` = **0** — the run is anchored to the decision day. Under `compute`: `paid_fill_count >= 1` is true, so `anchor_offset` = `DAYS(latest_paid_fill_date, NOW)`, a positive number of days taken off the term. Two defensible approval terms differing by exactly that many days. (On task 1's own world `paid_fill_count` = 5, so both readings agree there and the scored value is not itself in dispute — see task 1's file.)

*Affected artifact and location.* `pdp.extended.yaml` → `extended_policies[pdp_ext_exception_approval_term]` → `compute[anchor_offset]` against `rule` / `compute_basis[anchor_offset]` / `factors[run_anchor].ladder[0]`. Bears on **task 1**.

---

**F-3 — `SOURCE-POLICY RED`. The TrOOP policy's own negotiated-price cap contradicts the second tier of its out-of-network ladder.**

*Symptom.* One sentence of the rule caps what an out-of-network fill contributes at the plan's negotiated price; another sentence of the same rule contributes the largest amount the member paid, which the seed itself shows can exceed that price.

*Root cause.* The clause that replaces the base's TrOOP-counting sentence adds a negotiated-price cap, but the out-of-network ladder was written without reference to it.

*Evidence.* `pdp.extended.yaml`, `pdp_ext_troop_restatement`, both sentences in the same `rule`:
- "Only what the member or a qualifying third party actually paid counts toward the out-of-pocket total, **and never more than the plan's negotiated price recorded for the fill**; plan payments, premiums, the late enrollment penalty and what a supplemental benefit card met at a pharmacy never count." (also the `overwrite.replaced_by` for `pdp_coverage_stage_progression`)
- "Where a fill dispensed by an out-of-network pharmacy stands on the pharmacy record and the member's fills standing paid are fewer than that number, **what counts from such a fill is worked out as the largest amount the member paid on one of them**."

*Demonstrated consequence.* The seed already carries exactly such a fill: `_masked_views/1.masked.json` → `pdp_pharmacy_claims.bfba1d7b-6561-4d0b-99f9-51d5f7534084`, `pharmacy_network_status: out_of_network`, `negotiated_price: "96.00"`, `member_paid_amount: "145.00"`. For a member holding that fill with fewer than 4 paid fills, the first sentence says at most **96.00** counts and the second says **145.00** counts — different conclusions, same situation, a 49.00 divergence in the restated total. (Task 1's member has 5 paid fills and so takes tier 1, where both readings give 96.00; the contradiction does not move task 1's scored value.)

*Affected artifact and location.* `pdp.extended.yaml` → `extended_policies[pdp_ext_troop_restatement]` → `rule`, `overwrite[0].replaced_by`, `compute[out_of_network_counted]`, `factors[out_of_network_counted_basis].ladder[1]`. Bears on **task 1**.

---

**F-4 — `SOURCE-POLICY RED`. Undeclared override: the extended penalty-relief ladder decides the relieved months from the plan's own reading of another product's record, which the base policy forbids and which no `overwrite` names.**

*Symptom.* Base fixes the month count as CMS's and forbids the plan from adding or removing a month on its own view of the member's history. The extended policy's `group_coverage_months_proved` ladder does exactly that, and `overwrite` names a different base sentence.

*Root cause.* The override is hidden inside an intermediate of the calculation chain (`months_proved_by_group`) rather than in a renamed parameter, so it was not noticed as a conflict when `overwrite` was written. The tell is that the ladder's own fall-through restores the base reading.

*Evidence.*
- Base, `blueprint/products/pdp.yaml` → `policies[pdp_late_enrollment_penalty].rule`: "The count of months is CMS's, not the plan's: **the plan bills what CMS supplies and never adds or removes a month on its own view of the member's history.**"
- Extended, `pdp_ext_penalty_relief.overwrite` names only two base sentences: `pdp_premium_posting`'s "A credit adjustment and a penalty removal each name the single charge they relieve…" and `pdp_late_enrollment_penalty`'s "the penalty is removed and every month of it credited back once CMS confirms the earlier coverage was creditable". **The sentence above is named by neither.**
- Extended `rule`: "Where the member's employer group retiree drug coverage ended when the group's own contract ended and the group premium record carries at least the floor of coverage months charged for that member, **the months proved are the coverage months that record carries.**" and "…the months proved are **the fixed allowance of months the plan credits without further enquiry**." (`params.group_election_months_proved: 6`)
- The same ladder's fall-through is `float(F('late_enrollment_penalty_months'))` — the CMS count — which is precisely what base requires. The two tiers above it depart from it.

*Demonstrated consequence.* On task 0's world (`_masked_views/0.masked.json`): CMS's count is `pdp_enrollments.de27f4c9….late_enrollment_penalty_months = "19"`; the plan's own reading of the EGWP premium record gives `XCOUNT('egwp','egwp_premium_ledger', event_type='egwp_premium_charge')` = **4** (rows for 2026-01 … 2026-04). Following the base sentence, `months_proved` = 19 → `months_relieved` = `MN(5, 19)` = 5 → `RND(7.40 × 5, 1)` = 37.00 → held to the ceiling 35.80 → relief = **35.80**. Following the extended ladder, `months_proved` = 4 → `months_relieved` = 4 → relief = **29.60**. Two defensible removal amounts, and because the removal feeds the settlement, two defensible settlement figures as well. Declaring an override makes an override legal; leaving it undeclared leaves the task with a second defensible answer.

*Affected artifact and location.* `pdp.extended.yaml` → `extended_policies[pdp_ext_penalty_relief]` → `overwrite` (missing entry), `rule` (the two `months proved` sentences), `compute[months_proved_by_group]`, `factors[group_coverage_months_proved]`. Bears on **task 0**; the consequence is demonstrated against task 0's world in `0.md`.

---

**F-5 — observation. Two tiers of `term_counting_basis` select the same counted term for the plan's maintenance and ordinary terms, so the ladder cannot be told apart by the score wherever it matters.**

*Symptom.* The 30-day-cycle and 90-day-cycle tiers are different algorithms that return the same number for the term values the charter actually issues.

*Evidence.* `pdp_ext_exception_approval_term`, `params`: `maintenance_term_days: 365`, `ordinary_term_days: 180`, `expedited_term_days: 90`. `compute[term_counted]` = `int(base_term_days/30)*30` (tier 1) or `int(base_term_days/90)*90` (tier 2).
- base 365 → tier 1 gives 360, tier 2 gives 360. Identical.
- base 180 → 180 and 180. Identical.
- base 90 → 90 and 90. Identical.

*Demonstrated consequence.* For every one of the three terms the policy can start from, the two stated tiers of this ladder select the same value. A reader who takes the wrong tier scores identically, so the `settled_therapy_fill_count` test this factor is built around discriminates nothing. It is not a red light under the four relationships: the factor still bears weight against its own baseline (`term_counted = base_term_days`, i.e. 365 vs 360), and the distinctness rule is stated over tiers *as written*, which do differ. Recorded so it is not lost.

*Affected artifact and location.* `pdp.extended.yaml` → `extended_policies[pdp_ext_exception_approval_term]` → `params`, `compute[term_counted]`, `factors[term_counting_basis]`. Bears on **task 1**.

---

**F-6 — observation. Edge 2's prerequisite sentence is narrower than its declared `condition`, and both are narrower than what the depended-on policy computes.**

*Evidence.* `pdp_ext_counter_cost_share.prerequisite[0]`:
- `policy_source`: "…the out-of-pocket total … agrees with **every fill the pharmacy record shows paid and every fill it shows backed out** for the contract year." — two terms.
- `condition`: "…equals what the pharmacy record shows the member has paid on fills standing paid for the contract year, net of what the reversals on that record take back out **and of what a supplemental benefit card met at a pharmacy**." — three terms.
- `pdp_ext_troop_restatement.compute[result]` carries a **fourth**: `+ out_of_network_counted`.

*Demonstrated consequence.* A reader who takes the prerequisite sentence at face value expects the restated total to be paid-less-reversed = 360.00 − 162.00 = **198.00** on task 1's world; the policy's own rule yields **204.00** (− 90.00 card, + 96.00 out-of-network). This is not a red light: check 6 puts the method in the depended-on policy's own rule, which does carry both missing terms in full, so the derivation still has one reading. The mismatch is between `policy_source` and `condition`, which should carry the same strength.

*Affected artifact and location.* `pdp.extended.yaml` → `extended_policies[pdp_ext_counter_cost_share].prerequisite[0]` (`policy_source` vs `condition`). Bears on **task 1**.

---

**F-7 — observation. `settle_counter_fill_eaef344a`'s argument description states another problem's write and its position in the sequence.**

*Evidence.* `task_tools.py`, `settle_counter_fill_eaef344a` docstring:
- body: "…tied to the held fill it replaces **and to the approval that allowed it**";
- `Args.pdp_determination_id`: "the reference number of the approval on the member's coverage determination record that allows this product to be dispensed, **read from the receipt of the approval when it is recorded**."

*Demonstrated consequence.* Check 3 requires that no docstring state an action's position in a sequence. "read from the receipt of the approval when it is recorded" tells the agent that an approval will be recorded in this same transaction and that its receipt is to be read afterwards — the prerequisite is thereby partly discoverable from the tool layer rather than from the policy surface. It is an observation, not a red light: the tool neither validates nor refuses on the prerequisite (the function body is a bare `ctx.create`), and the dependency is independently and fully discoverable from `pdp_ext_counter_cost_share`'s own prerequisite sentence, so no solution is gained or lost.

*Affected artifact and location.* `task_tools.py` → `settle_counter_fill_eaef344a` docstring. Bears on **task 1**.

---

**F-8 — observation. `post_penalty_removal_e1c246c8` claims a business effect on the enrollment that it does not perform, and one task's tier selection depends on the omission.**

*Evidence.* `task_tools.py`, `post_penalty_removal_e1c246c8`:
- docstring: "**The member's penalty receivable falls by the amount taken off**, the entry appears on their next premium statement as a credit…";
- body: a single `ctx.create("pdp_premium_ledger", …)`. `pdp_enrollments.penalty_balance_due` is never updated. (Contrast `restate_out_of_pocket_total_a40a5cef`, which does `ctx.update("pdp_enrollments", …, troop_accumulated=…)`.)
- `pdp_ext_premium_arrears_settlement.compute[penalty_outstanding]` reads `float(F('penalty_balance_due'))` in every branch's test and in its fall-through.

*Demonstrated consequence.* On task 0's world, after the removal posts, `penalty_balance_due` still reads "35.80" while `penalty_charged_total − penalty_removed_total` = 6.20, so tier 1 of `penalty_standing_basis` fires **because the receivable did not fall**. Had the tool done what its docstring says, `penalty_balance_due` would read 6.20, neither strict comparison would hold, and the fall-through would apply. The scored settlement figure is the same either way (110.40 — the fall-through would return 6.20 too), so this is an observation and not a red light; but the factor's weight rests on the gap between the tool's stated effect and its implementation, and an agent who trusts the docstring and then reads the enrollment sees a record that contradicts it.

*Affected artifact and location.* `task_tools.py` → `post_penalty_removal_e1c246c8` docstring vs body; `pdp.extended.yaml` → `extended_policies[pdp_ext_premium_arrears_settlement].compute[penalty_outstanding]`, `factors[penalty_standing_basis]`. Bears on **task 0**.

---

**F-9 — observation. Four factors labelled `parameter` tier a window or an aggregation rather than a number.**

*Evidence.* `relief_ceiling_rule` (`pdp_ext_penalty_relief`): sum since coverage began less removals / sum over six months less removals / the single latest charge. `credit_taken_off` (`pdp_ext_premium_arrears_settlement`): every credit / credits in the last six months / nothing. `reversal_taken_back_out` (`pdp_ext_troop_restatement`): every reversal / reversals in the last three months / nothing. `card_met_at_pharmacy` is borderline in the other direction but selects a figure and is sound as `parameter`.

*Demonstrated consequence.* None that bites: even reclassifying `relief_ceiling_rule` and `credit_taken_off` as `method`, `pdp_ext_penalty_relief` keeps 2 `parameter` + 2 `method` and `pdp_ext_premium_arrears_settlement` keeps 2 `parameter` + 4 `method`, so no policy falls below the 2-`parameter` / 1-`method` floor and no count changes. Recorded as an observation only.

*Affected artifact and location.* `pdp.extended.yaml` → the four `factors[].effect` labels named above.

---

**F-10 — observation. Two policies' `baseline.params` name figures the baseline method does not use.**

*Evidence.*
- `pdp_ext_premium_arrears_settlement.baseline.params` = `[monthly_plan_premium, premium_due_day_of_month, frequent_payer_count]`. Its `baseline.rule` says "What the account treats as already settled is **the latest premium payment posted on it**" (no count), "The settlement asks for no penalty" and "**The settlement asks for no further coverage month**" (no monthly premium, no due day). None of the three figures enters the baseline computation.
- `pdp_ext_troop_restatement.baseline.params` = `[long_history_fill_count, reversal_run_count, annual_deductible]`. Its `baseline.rule` gathers over the three-month window, takes nothing for the card, nothing for reversals and nothing for out-of-network. None of the three enters the baseline computation; `annual_deductible` is not mentioned in the baseline rule at all, and the other two are thresholds used only by tiers the baseline excludes.
- By contrast `pdp_ext_penalty_relief` (`national_base_beneficiary_premium`, `late_enrollment_penalty_rate_percent`, `penalty_rounding_basis`), `pdp_ext_exception_approval_term` (`ordinary_term_days`, `floor_days`) and `pdp_ext_counter_cost_share` (`tier_2_generic_copay_30`, `annual_deductible`) name figures their baselines do use.

*Demonstrated consequence.* The baselines remain self-sufficient — a reader computes a definite number from `baseline.rule` and the records without any factor — so this is not a red light under the four relationships. It is recorded because `baseline.params` is what the computation document is expected to render as "the standard method's default values", and in these two policies that list is inert: the figures printed play no part in the number the document produces.

*Affected artifact and location.* `pdp.extended.yaml` → `extended_policies[pdp_ext_premium_arrears_settlement].baseline.params`, `extended_policies[pdp_ext_troop_restatement].baseline.params`. Bears on **task 0** and **task 1** respectively.

---

**F-11 — observation. A seeded determination record breaches the base timeliness policy it was written under.**

*Evidence.* `_masked_views/1.masked.json`: request `9590de5c-401c-4c19-ad79-ad5b09f776a0`, `request_type: standard_coverage_determination`, `received_date: 2026-04-10`, `received_time: "09:05"`; decision `1f61dfff-e055-4324-9dfc-2c6b41772dcb`, `source_determination_id` pointing at it, `decision_date: 2026-04-13`, `decision_time: "15:40"`, `decision_outcome: denied`. The member's variant is Ridgecrest RxSecure Value (PDP), `coverage_determination_standard_hours = 72`. Base `pdp_coverage_determination_timeliness`: "Hours are counted as full 24-hour periods from the recorded receipt time, a decision given exactly on the deadline is in time"; the deadline was 2026-04-13 09:05, and the decision was given 6h35m late. The same base rule says "Where the plan does not decide by the deadline the request goes to the independent review entity automatically".

*Demonstrated consequence.* None on the scored value — the row is historical and `denied_decisions` counts it either way. Recorded because `standing_denial_allowance` reads its tier off a record the charter says should not exist in that form.

*Affected artifact and location.* `_masked_views/1.masked.json` → `pdp_coverage_determinations`; `pdp.extended.yaml` → `factors[standing_denial_allowance]`. Bears on **task 1**.

## closing_checklist

**The difficulty does NOT close.** Step 4's checklist is written out below for the record, but closing requires "policy self-consistency PASS + problem tree holds PASS + factors bear weight PASS + unique solution PASS" for every task, and two of the four relationships fail. Everything in this section was written **after** both tasks' `source_derivation_frozen` sections and both `source_gt_comparison` sections were complete on disk; the pre-reveal `## charter_global_frozen` section above has not been altered.

| Step 4 item | status |
|---|---|
| per-task audit files correspond one-to-one with the tasks; `_difficulty.md` sits alongside them | **OK** — `0.md`, `1.md`, `_difficulty.md` in `audits/policy_task/part_d_pharmacy_and_coverage_desk/` |
| old revisions traceable | **OK** — first revision of this difficulty; no prior audit exists to preserve |
| every comparison section carries a PASS | **NO** — `0.md` carries SOURCE-POLICY RED (T0-1); `1.md` carries SOURCE-POLICY RED and SOURCE-FACTOR RED (T1-1, with T1-2 and T1-3) |
| this difficulty's extended policies fully covered | **OK** — all five, `{penalty_relief, arrears}` ∪ `{troop, exception, counter}` |
| the M tasks' scopes pairwise disjoint, each spanning its whole problem tree | **OK** — no policy appears in both, and each scope is exactly root + prerequisites |
| task tools and GT closed | **OK** — five tools, each named by exactly one policy and called exactly once across the suite |
| each task tool uses an independently generated, frozen uuid8 | **OK** — `e1c246c8`, `7dfec3b3`, `a40a5cef`, `dd13544d`, `eaef344a`; distinct, no shared stem, not sequential |
| every problem tree has 1–3 prerequisite problems | **OK** — task 0: n = 1; task 1: n = 2 |
| at least max(n − 1, 1) `value_input` edges | **OK** — task 0: 1 of 1; task 1: 1 of 2 (floor is 1) |
| at least one problem resolved by an `owner=user` tool | **OK** — `authorize_arrears_payment_7dfec3b3` (task 0), `settle_counter_fill_eaef344a` (task 1) |
| no cycle, including across tasks | **OK** — three edges, two disjoint trees, no cross-task reference; the difficulty-level graph is a DAG |
| every computation declares a self-sufficient baseline | **OK for the number, with two qualifications** — all five baselines yield a definite figure (7.00 / 76.40 / 164.00 / 180 / 6.00), each different from gold; but `counter_price_ceiling`'s declared factor baseline contradicts its policy's `baseline.rule` (**F-1**), and two policies' `baseline.params` are inert (**F-10**) |
| 4–6 factors, 2 `parameter`, 1 `method` per computation | **OK as declared** — 4 / 6 / 4 / 6 / 6, each meeting the label floors. After striking out `counter_price_ceiling` (**F-1**) the counter computation retains 5 (2 `parameter`, 3 `method`), so no bound is breached even on the corrected count |
| per task ≥ 1 multi-source and ≥ 1 cross-difficulty factor | **OK** — task 0: `group_coverage_months_proved` (both, reading `egwp`); task 1: `card_met_at_pharmacy` (both, reading `allowance`) |
| every ladder ≥ 3 tiers, stated in full in its rule | **NO** — 25 of 26 hold; `counter_price_ceiling`'s first tier is in no sentence of the rule (**F-1**) and `run_anchor`'s first tier is stated with one threshold and implemented with another (**F-2**) |
| tiers distinct in outcome; conditions and outcomes ones the business actually holds | **NO** — `term_counting_basis`'s two stated tiers return the same counted term for every term the policy can issue (**F-5**) |
| every factor proved to bear weight against an honest baseline | **NO** — 25 of 26 bear weight; `counter_price_ceiling` does not, once its baseline is taken from `baseline.rule` (**F-1** / `1.md` T1-1) |
| the baseline alone gives a definite number different from gold | **OK** — 7.00 vs 29.60; 76.40 vs 110.40; 164.00 vs 204.00; 180 vs 267; 6.00 vs 473.98 |
| instantiation-stage gates re-run on the final form | **OK, all green** — re-run at close on unchanged artifacts: `check_extended` EXTENDED OK; `check_task_tools` TASK TOOL CONTRACT OK; `replay_tasks` REPLAY OK (0.json 11 acts / 32 closure, 1.json 14 acts / 23 closure, both matching); `check_solvability` SOLVABILITY OK; `check_compute` COMPUTE OK; `check_grounding` GROUNDING OK; `check_cross_fire` SCOPE OK. No artifact was edited by this audit. |

### post-reveal note on the strength of the evidence

The independent derivation reproduced **every** scored value, **every** baseline result, **every** per-factor sensitivity and **every** argument of all five gold writes, for both tasks — 5 expected values, 5 baseline results, 26 factor sensitivities and 17 write arguments, figure for figure and id for id, derived from the policy, the schema, the tool contracts and the raw world before any masked field was read. The red lights below are therefore not disagreements about the answer. They are defects in the *proof the artifacts submit*: in two places the policy as written admits a second answer that the gold reading happens not to take, and in one place a declared factor is shown to carry no weight once its baseline is read from the policy's own baseline rule.

Two of the revealed proof fields assert things about the artifacts that do not survive recomputation and are red-lighted with the relationship they support:
- `tasks/0.json` → `design_rationale`: **"Overrides declared, none undeclared: three entries in all."** False — the CMS-count sentence of `pdp_late_enrollment_penalty` is overridden by the `months_proved_by_group` ladder and named by no `overwrite` entry (**F-4**, demonstrated in `0.md` → T0-1).
- `tasks/1.json` → `computations[pdp_ext_counter_cost_share].factor_trace[5]`: **"the ceiling is the negotiated price of 786.00, which does not bite."** True as written, and it is the author's own record that the factor has no effect on the result; the factor was nonetheless counted toward the computation's declared factor set (**F-1**, demonstrated in `1.md` → T1-1).

### summary of verdicts

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
|---|---|---|---|---|
| 0 | **SOURCE-POLICY RED** (T0-1 / F-4) | PASS | PASS | **FAIL by consequence of T0-1** |
| 1 | **SOURCE-POLICY RED** (T1-1 / F-1; also F-2, F-3) | PASS | **SOURCE-FACTOR RED** (T1-1) | PASS |

Red lights: **F-1** (rule gap + straw-man baseline, task 1), **F-2** (threshold mismatch, charter), **F-3** (cap vs ladder, charter), **F-4** (undeclared override, task 0).
Observations: **F-5** … **F-11**, plus `0.md` T0-2, T0-3 and the per-task consequence notes.

### write-domain disclosure

This audit edited no artifact. One side effect is disclosed for completeness: **`replay_tasks.py` writes its task files back in place** (`skills/erl-task-instantiate/scripts/replay_tasks.py:303`, `open(tp, "w").write(...)`), rebuilding `db_closure` and `db_closure_matches_initial_state` from the replay. Running it as part of the Step-4 gate re-run therefore rewrote `tasks/part_d_pharmacy_and_coverage_desk/tasks/0.json` and `1.json`, which lie outside this audit's write domain.

The rewrite is **content-neutral and was verified to be so**: parsing both files before and after the re-run and comparing them with `json.dumps(..., sort_keys=True)` gives an **empty diff for both tasks**. The only byte-level difference is the key ordering inside `db_closure`, because the gate rebuilds that dict by iterating an unordered set. No field value changed, and the gate reported exactly the coordinator's snapshot figures both times (0.json: 11 acts, 32 closure, 32 init, match True; 1.json: 14 acts, 23 closure, 23 init, match True). The `pdp.extended.yaml` and `task_tools.py` hashes are unchanged from the brief (`395a18d5ba3507c7`, `d8da38d60b74418b`), re-verified after the re-run.

The gate's write-back is its own designed behaviour — the coordinator's snapshot run did the same thing — and is noted here only so that a later diff of the task files is not mistaken for an audit edit.

---

# revision_2

Re-audit round 2. Revision 1 above is left untouched.

## charter_global_frozen (revision_2)

- re-audit time: 2026-09-21, after the round-1 rework.
- auditor: same independent source-layer auditor.
- **This round is not blind and is not presented as one.** Round 1's reveal is already in this auditor's context, so revision 2 is a *verification* pass: every figure below was recomputed from the reworked artifacts before the round-2 GT fields were read, but the round-1 answers were known, and the round-2 values for four of the five computations are unchanged from round 1. No blindness is claimed.
- re-derivation trigger, per the carry-forward rule: **both shared inputs moved**, so the whole charter-global section is re-derived rather than carried forward.

| artifact | round 1 | round 2 | re-derived? |
|---|---|---|---|
| `pdp.extended.yaml` | `395a18d5ba3507c7` | `c6f4e077813cd9eb` | yes, in full |
| `task_tools.py` | `d8da38d60b74418b` | `fb6f31940de52a89` | yes, in full |
| `tasks/0.json` | — | `f79146a3107e99f0` | yes |
| `tasks/1.json` | — | `fbda45ddb369e9ea` | yes |
| `_masked_views/0.masked.json` | `1e7a3e7485b34dde` | `f3afa8daff0aea8d` | yes |
| `_masked_views/1.masked.json` | `1bb1077d3c06fc19` | `2cb5870a2ea9489f` | yes |

All six hashes recomputed on disk and matching the coordinator's brief. Gate snapshot supplied with the brief and re-confirmed: `check_extended`, `check_task_tools`, `replay_tasks` (0.json 33/33, 1.json 23/23), `check_solvability`, `check_compute` (0.json 2 comps / 10 factors / 1 xfac; 1.json 3 comps / 16 factors / 1 xfac), `check_grounding`, `check_cross_fire` — all OK. `check_traceability` still deferred to the render stage.

### disposition of every round-1 item

Verified against the artifacts, not against the reworker's account. The reworker's claims were supplied by item id only, with its reasoning and figures withheld.

| round-1 item | claim | verdict | evidence |
|---|---|---|---|
| **F-1 / T1-1** | closed | **PARTIALLY CLOSED — the decoration half is closed, the rule↔compute half survives.** New finding **R2-1** | see below |
| **F-2 / T1-2** | closed | **CLOSED** | `compute[anchor_offset]` tier 1 is now `latest_paid_fill_date != None and paid_fill_count >= K('settled_therapy_fill_count')`, matching the rule's "at least the number the plan treats as settled therapy" and `compute_basis[anchor_offset]`. Tier 2 remains `paid_fill_count < 1`, matching "no fill stands paid". For 1–2 paid fills both tiers now fail and the fall-through gives 0, which is exactly what the rule's fall-through states. No gap. |
| **F-3 / T1-3** | closed | **CLOSED** | The offending tier outcome "the largest amount the member paid on one of them" is gone from `rule`, `compute`, `compute_basis` and `factors`. Tier 2 is now "the plan negotiated price recorded on the latest of them", implemented as the new binding `out_of_network_latest_price` (`LATEST(... 'negotiated_price' ... pharmacy_network_status='out_of_network')`). Both tiers now yield a negotiated price, so the policy's cap "never more than the plan's negotiated price recorded for the fill" can no longer be contradicted by its own ladder. The binding `out_of_network_paid` is gone, with no stranded reference. |
| **F-4 / T0-1** | closed | **CLOSED** | A third `overwrite` entry now names the base sentence. `superseded_clause` = "The count of months is CMS's, not the plan's: the plan bills what CMS supplies and never adds or removes a month on its own view of the member's history." — verified **verbatim present in** `blueprint/products/pdp.yaml` → `policies[pdp_late_enrollment_penalty].rule`. `replaced_by` = "Where the plan's own records prove how many coverage months the member held creditable drug coverage for, the months relieved are taken from what those records carry rather than from the count of uncovered months the enrollment carries." — verified **verbatim present in** the extended `rule`. The rival reading is genuinely retired, not merely unquoted: the replacement says outright that the months come from the records "**rather than** from the count of uncovered months the enrollment carries", which is the 19 the base reading used. The ladder's fall-through still returns `float(F('late_enrollment_penalty_months'))`, and that is now consistent rather than contradictory — the replacement is conditional ("Where the plan's own records prove…"), so where they prove nothing the enrollment's count governs, as base requires. |
| **F-5** | addressed | **CLOSED** | `term_counted` tier 2 changed from ninety-day to **weekly** cycles (`int(base_term_days / 7) * 7`), and the change is carried through to the `rule` ("taken in whole weeks and rounded down to a whole week"), `compute_basis[term_counted]` and `factors[term_counting_basis].ladder[1]`. On the maintenance term the task uses, the three tiers now give **360 / 364 / 365** — all distinct. Residual, carried forward as an observation: for the ordinary (180) and expedited (90) terms, tier 1 and the fall-through still coincide numerically because both are divisible by 30; the *methods* differ, so the distinctness rule is met as stated. |
| **F-6 / T1-5** | addressed | **CLOSED** | The prerequisite sentence now reads "…agrees with what the pharmacy record shows the member has **borne** for the contract year", a general term, and the edge's `condition` now enumerates all four components ("once every fill standing paid, every fill backed out, what a supplemental benefit card met at a pharmacy and what counts from a fill dispensed by an out-of-network pharmacy have been taken into account"). Sentence and condition now carry the same scope, and both match what `pdp_ext_troop_restatement` computes. |
| **F-7 / T1-6** | addressed | **CLOSED** | `settle_counter_fill_eaef344a`'s `pdp_determination_id` description is now "the reference number of the approved coverage determination on the member's coverage determination record that covers this product, **read from the member's coverage determination records**". The sequencing phrase "read from the receipt of the approval when it is recorded" is gone, as is "tied to … the approval that allowed it" from the body. No docstring in the module now states another problem's write or its position in a sequence. |
| **F-8 / T0-4** | addressed | **CLOSED, and closed the right way round** | `post_penalty_removal_e1c246c8`'s docstring no longer claims "The member's penalty receivable falls by the amount taken off". It now states the opposite and matches the implementation: "…so that what the account has charged in penalty less what it has taken back off is the penalty the member still owes; **the running penalty figure carried on the enrollment record itself is not rewritten by this action**." The body is still a single `ctx.create` on `pdp_premium_ledger`. The arrears policy's `penalty_standing_basis` tier 1, which fires precisely because `penalty_balance_due` is not rewritten, is now honestly discoverable from the tool contract. |
| **F-9** | addressed | **CLOSED** | The four boundary labels were reclassified. `relief_ceiling_rule` → `method`; `credit_taken_off` → `method`; `penalty_standing_basis` → `method`; `reversal_taken_back_out` remains `parameter` but its ladder now selects between two totals rather than two windows. Per-policy label counts after the change: penalty_relief 2/2, arrears 2 `parameter` + 4 `method`, troop 2/2, exception 4/2, counter 3/3. Every policy still clears 4–6 factors with ≥2 `parameter` and ≥1 `method`. |
| **F-10 / T0-5 / T1-7** | addressed | **CLOSED** | `pdp_ext_premium_arrears_settlement.baseline.params` and `pdp_ext_troop_restatement.baseline.params` are now `[]`, and that is correct rather than evasive: both baseline paths were traced and neither calls `P()` or `K()` — arrears reduces to `RND(premium_charged_last_three − latest_premium_payment − 0 + 0 + 0, 2)` and TrOOP to `MX(0, RND(member_paid_last_three − 0 − 0 + 0, 2))`. The three policies whose baselines do use plan figures still name exactly those figures. |
| **F-11 / T1-8** | addressed | **CLOSED** | The seeded denial's `decision_time` moved from `"15:40"` to `"08:20"` on 2026-04-13. Against a receipt of 2026-04-10 09:05 and `coverage_determination_standard_hours` = 72 for this variant, the deadline was 2026-04-13 09:05, so the decision is now **in time**. The record no longer breaches base `pdp_coverage_determination_timeliness`, and `standing_denial_allowance` now takes its tier from a record the charter permits. |
| **T0-2** | addressed | **CLOSED** | Verified two ways. (1) The stamp no longer reproduces any intermediate: `pdp_enrollments.…premium_balance_due` is now **"61.40"** while the policy's `premium_due` computes to **66.00**. Checked against every binding of the settlement — 191.00, 114.60, 10.40, 66.00, 35.80, 6.20, 7.00, 38.20, 110.40 — 61.40 matches none. (2) The added row did not strand anything: the new credit is `2026-09-10, 4.60, billing_error_correction`, and the ladder was narrowed so tier 1 totals only rate-change credits (10.40) and tier 2 only error credits (4.60). The narrowing is carried through to `rule`, `compute_basis[credit_taken]` and `factors[credit_taken_off].ladder`, the old `premium_credited_all` / `premium_credited_last_six` bindings are gone with no leftover reference, and a new closing sentence — "A credit posted for any other reason is left on the account and is not taken off the settlement." — covers the fall-through. The added row does not touch `payments_on_record` (3), `premium_in_window` (191.00) or any penalty binding. It is a net improvement: tier 2 of `credit_taken_off` had no near-miss in round 1 and now has one. |
| **T0-3** | addressed | **CLOSED as far as it went** | The `billing_period` argument is still fixed by the inherited base sentence "Money the member pays is posted against the oldest unpaid coverage month first", and still derives to `"2026-08"`. This was an observation about a load-bearing inheritance, not a defect; it is unchanged and remains correct. |

### policy_conflict_scan (revision_2)

Re-run in full. Five policies, five distinct target tools, five distinct computed quantities, unchanged in that structure from revision 1. Base copy re-checked key by key against `blueprint/products/pdp.yaml`: `category`, `display_name`, `binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`, `measures`, `policies` all compare equal; the only extra key is `extended_policies`. Task scopes are unchanged and remain pairwise disjoint and jointly complete: task 0 `{pdp_ext_penalty_relief, pdp_ext_premium_arrears_settlement}`, task 1 `{pdp_ext_troop_restatement, pdp_ext_exception_approval_term, pdp_ext_counter_cost_share}`. Cross-category boundaries unchanged: `egwp` for penalty relief, `allowance` for TrOOP, none elsewhere.

### rule_compute_equivalence (revision_2)

Swept sentence by sentence over all five reworked policies. Two of round 1's three divergences (**F-2**, **F-3**) are closed and verified above. **One survives, and it is the one the rework was meant to close**: `price_ceiling` — recorded as **R2-1**.

All other reworked bindings were checked for the "declaration left behind by a fix" failure mode and are clean: the weekly-cycle change, the out-of-network-latest change, the credit narrowing, the override addition and the ceiling demotion each carry through to `rule`, `compute_basis` and `factors[].ladder` consistently.

### action_binding_and_uuids (revision_2)

Unchanged and still sound. Five uuid8 tails `e1c246c8`, `7dfec3b3`, `a40a5cef`, `dd13544d`, `eaef344a` — pairwise distinct, no shared stem, not sequential, one per tool. Each `(target_tool, computes)` pair is claimed by exactly one policy. No docstring now states an action's position in a sequence (F-7 closed).

### prerequisite_graph and prerequisite_sentences (revision_2)

Re-derived in full. The graph is structurally unchanged: three edges, two disjoint trees, acyclic.

For all three edges it was re-verified mechanically that `policy_source` is **verbatim present in the blocked policy's own `rule`** and **absent from the depended-on policy's rule**; that `form` is `state` on all three with no `fallback_reason` anywhere; that each `value_input` edge's `gate` (`penalty_outstanding`, `troop_on_record`) is a real binding name in the blocked policy's `compute`; and that the `state_gate`'s `pdp_point_of_sale_cost_share.determination_on_record` is still a real base eligibility of kind `authorization`. Edge 2's sentence and condition now carry matching scope (F-6 closed). The four-point test passes on all three.

### factor_ladders (revision_2)

| policy | factors | `parameter` | `method` | cross_difficulty |
|---|---|---|---|---|
| `pdp_ext_penalty_relief` | 4 | 2 | 2 | `egwp` |
| `pdp_ext_premium_arrears_settlement` | 6 | 2 | 4 | — |
| `pdp_ext_troop_restatement` | 4 | 2 | 2 | `allowance` |
| `pdp_ext_exception_approval_term` | 6 | 4 | 2 | — |
| `pdp_ext_counter_cost_share` | 6 | 3 | 3 | — |

Totals per task: 10 factors (task 0) and 16 (task 1), matching `check_compute`. Every ladder has three tiers; every tier is stated in its policy's `rule` and implemented in `compute` — **including, now, the ceiling's disappearance: with `counter_price_ceiling` struck, no ladder remains that is absent from the rule.** Bindings are disjoint within each policy and every `decides` names an input rather than `result`.

**The two new counter factors were checked for tier realism and for being a fresh instance of the defect they replaced.** `one_month_figure` was split into `formulary_tier_figure` (decides `tier_figure`) and `pharmacy_standing_addition` (decides `standing_differential`), joined by `one_month_share = tier_figure + standing_differential`.
- Outcome distinctness was checked **on every one of the six variants**, not only the one in play. `formulary_tier_figure` gives (preferred brand / preferred generic / generic) = 47/0/8, 44/0/6, 42/1/5, 40/2/4, 37/0/3, 33/0/2 — three distinct values on every variant. `pharmacy_standing_addition` gives (brand differential / generic differential / nothing) = 7/12/0, 7/10/0, 7/8/0, 7/6/0, 7/6/0, 7/5/0 — three distinct values on every variant. No collision anywhere.
- Both are genuine business conditions: a formulary tier decides a copay, and a standard-retail pharmacy adds the published differential over the preferred figure. Each tier's outcome is a figure the plan actually publishes.
- Neither is decoration: on task 1's world `formulary_tier_figure` under its baseline gives 429.61 and `pharmacy_standing_addition` gives 473.98, against a gold of 484.00. **The replacement factor is load-bearing, and the split is not a fresh instance of the F-1 defect.**

### cross-category reads at field level (coordinator's lead, tested)

The lead holds here, in a mild form. `check_extended` prints "cross-category reads declared exactly", but the declaration is complete for one policy and incomplete for the other:
- `pdp_ext_penalty_relief.cross_category[egwp].reads` = `['status', 'egwp_premium_ledger.event_type']`. Compute uses `CFIELD('egwp','status')` and `XCOUNT('egwp','egwp_premium_ledger', event_type='egwp_premium_charge')`. **Both the field and the filter field are declared.** Complete.
- `pdp_ext_troop_restatement.cross_category[allowance].reads` = `['status', 'otc_quarterly_sublimit', 'allowance_card_ledger.amount']`. Compute uses `CFIELD('allowance','status')`, `CPARAM('allowance','otc_quarterly_sublimit')` and `XSUM('allowance','allowance_card_ledger','amount', event_type='allowance_purchase', merchant_category='pharmacy_and_otc', settlement_status='settled')`. **The summed field is declared; the three filter fields are not.**

Recorded as observation **R2-3**. The gate passes because it checks the category, not the fields; the charter's own convention — set by the sibling policy, which does declare its filter field — is not followed here.

### findings (revision_2)

---

**R2-1 — `SOURCE-POLICY RED`, carried over from F-1 and NOT closed. The ceiling's rule↔compute divergence survived the rework and is now unconditional.**

*Symptom.* The rule, `compute_basis` and `baseline.rule` all say the ceiling is the negotiated price recorded for **the fill the pharmacy is holding**; `compute` binds it to **`price_used`**, a different quantity with its own three-tier ladder.

*Root cause.* Round 1's F-1 had two halves: a decoration factor, and a compute binding that did not implement the rule's ceiling sentence. The rework struck the factor — which closes the first half — but carried the wrong binding through unchanged, and by removing the conditional wrapper made it apply on every world rather than only on the first tier.

*Evidence (verbatim, reworked artifacts).* `pdp.extended.yaml` → `extended_policies[pdp_ext_counter_cost_share]`:
- `rule`: "The member never pays more than the plan's negotiated price recorded for **the fill the pharmacy is holding**, however the multiplier falls."
- `baseline.rule`: carries that same sentence verbatim, and separately "The price the cost share is taken from is the largest plan negotiated price standing on a fill the member has paid for in the contract year" — so even on the pure baseline reading the two are explicitly different quantities.
- `compute_basis[price_ceiling]`: quotes the ceiling sentence, whose subject is the held fill.
- `compute`: `- price_ceiling: price_used`.
- `compute`: `- price_used: rejected_fill_price if (rejected_fill_price > 0 and paid_fill_count >= K('settled_therapy_fill_count')) else (latest_paid_price if (...) else largest_paid_price)` — equal to the held fill's price only on its first tier.

*Demonstrated consequence.* Recomputed on a world reachable under this charter — the same member, but with two paid fills, both at the initial-coverage stage, so that `paid_fill_count` = 2 < `settled_therapy_fill_count` = 3 and `fills_at_deductible_stage` = 0:

| binding | value |
|---|---|
| `rejected_fill_price` (held fill) | 786.00 |
| `paid_fill_count` | 2 |
| `largest_paid_price` | 128.00 |
| `price_used` (fall-through tier) | 128.00 |
| `supply_share` | 153.00 |
| `member_share` (fall-through branch) | 153.00 |

- **Rule reading** — ceiling is the held fill's negotiated price, 786.00 → `RND(MN(153.00, 786.00), 2)` = **153.00**.
- **Compute reading** — `price_ceiling` = `price_used` = 128.00 → `RND(MN(153.00, 128.00), 2)` = **128.00**.

Two defensible answers in the same situation, differing by 25.00. The compute reading is also the business-wrong one: it caps what the member pays for the held fill at the negotiated price of an unrelated earlier fill. (On task 1's own world `price_used` = `rejected_fill_price` = 786.00, so the scored 484.00 is the same under either reading — the defect is in the charter, not in this task's number. Verified by substitution: forcing `price_ceiling := rejected_fill_price` on task 1's handling-time world still returns 484.00.)

*Aggravating evidence from the proof fields — a new instance of the class red-lighted in round 1.* `tasks/1.json` → `design_rationale` asserts, in justifying the closure: *"because the split gives member_share = d + s(p − d)/p, which is strictly below p whenever the cost share is below the price, **a ceiling at p can never bind on any world**."* That assertion does not survive recomputation, for three independent reasons:
1. Its own premise is conditional ("whenever the cost share is below the price") and its conclusion drops the condition. Where the cost share exceeds the price, `d + s(p − d)/p` exceeds `p`.
2. It reasons only about the boundary-split branch. `member_share` has two others, and in the fall-through branch `member_share` = `supply_share`, which is unrelated to `p` and can exceed it — as the table above shows (153.00 against 128.00).
3. Most directly, the ceiling in `compute` is not "a ceiling at p" at all; it is `price_used`. The sentence justifies demoting a quantity the compute does not use.
The reworker corrected two false override-count assertions of exactly this class and introduced a third while doing so.

*What IS closed.* The decoration half of F-1 is genuinely closed and is not restated as a defect: `counter_price_ceiling` is gone, the withdrawn override is correctly withdrawn (base's own ceiling sentence is restored verbatim in the rule and the `overwrite` now supersedes a different, genuinely superseded base clause), and all six remaining counter factors bear weight on task 1's world. The replacement factor is load-bearing and its ladder is distinct on every variant.

*Affected artifact and location.* `pdp.extended.yaml` → `extended_policies[pdp_ext_counter_cost_share]` → `compute[price_ceiling]` against `rule`, `compute_basis[price_ceiling]` and `baseline.rule`; `tasks/1.json` → `design_rationale` (the "can never bind on any world" assertion).

*Relation to previous revisions.* Round 1 **F-1 / T1-1**, partially closed. The `SOURCE-FACTOR` half is closed; the `SOURCE-POLICY` half is not.

---

**R2-2 — observation. A stranded input declaration left behind by the struck factor.**

*Symptom.* `pdp_ext_counter_cost_share.inputs.history` still declares a history read that no binding of the policy performs.

*Evidence.* The fourth entry is `{table: pdp_pharmacy_claims, aggregate: count, field: pdp_pharmacy_claim_id, within_months: null, filters: {event_type: pdp_pharmacy_claim_adjudication, claim_status: paid, pharmacy_network_status: preferred_retail}}`. That was `preferred_fill_count`, the sole input of the struck `counter_price_ceiling` factor. The reworked `compute` contains no `preferred_fill_count` binding and no `COUNT(... pharmacy_network_status='preferred_retail' ...)` call.

*Demonstrated consequence.* Each of the other 19 declared history inputs across the five policies was matched mechanically against an actual DSL call in its policy's `compute` (aggregate, table, field, filters and window all matching); **19 match, this one does not**. `inputs.history` is the policy's declaration of the records it reads, which the render and traceability stages use to decide what a document must make findable; this entry now promises a read the policy does not perform, so it would require a document to surface a count of preferred-retail paid fills that nothing consumes. No scored value is affected, so it is an observation rather than a red light.

*Confirms the coordinator's second lead*: this is precisely "a declaration left behind by a fix", and the struck factor is exactly the edit that stranded it.

*Affected artifact and location.* `pdp.extended.yaml` → `extended_policies[pdp_ext_counter_cost_share].inputs.history[3]`.

---

**R2-3 — observation. Cross-category reads are declared at field level for one policy and not the other.**

*Evidence and reasoning.* Set out under `### cross-category reads at field level` above. `pdp_ext_troop_restatement.cross_category[allowance].reads` declares the summed field `allowance_card_ledger.amount` but not the three fields the `XSUM` filters on (`event_type`, `merchant_category`, `settlement_status`), while the sibling `pdp_ext_penalty_relief` does declare its filter field.

*Demonstrated consequence.* On task 1's world, summing `amount` over the allowance ledger without the undeclared filters gives 438.00 (it would sweep in the three quarterly loads of 90.00) against the correct 168.00. The tier is unaffected here, since both exceed the 90.00 sublimit, so `card_met_amount` is 90.00 either way and no scored value moves. For a member with 50.00 of settled purchases against 270.00 of loads the two readings would give `card_met_amount` 90.00 and 50.00 — a 40.00 divergence in the restated total. The policy's own `rule` does state the discrimination in prose ("the pharmacy and over-the-counter purchases **settled** on its card"), so no reader of the rule is misled; only the machine-readable declaration is incomplete. Observation, not a red light.

*Affected artifact and location.* `pdp.extended.yaml` → `extended_policies[pdp_ext_troop_restatement].cross_category[0].reads`.

---

**R2-4 — observation, carried forward from F-5. `term_counting_basis`'s tier 1 and fall-through still coincide numerically on two of the three terms.**

With the weekly-cycle change, the three tiers give 360 / 364 / 365 on the maintenance term (the one this task takes) — distinct, so F-5's substance is closed. But on the ordinary term (180) they give 180 / 175 / 180 and on the expedited term (90) they give 90 / 84 / 90, because both are divisible by 30. The *methods* differ ("taken in whole thirty-day supply cycles" vs "counted as booked"), so the distinctness rule is satisfied as stated and this is not a red light; recorded so the residue is not lost.

## closing_checklist (revision_2)

**The difficulty still does NOT close**, on one red light rather than four.

| Step 4 item | status |
|---|---|
| per-task files one-to-one with tasks, `_difficulty.md` alongside | OK |
| old revisions traceable | OK — revision_1 preserved verbatim above; revision_2 appended |
| every comparison section carries a PASS | **NO** — `1.md` carries **R2-1** (SOURCE-POLICY RED). `0.md` now carries PASS on all four relationships |
| extended policies fully covered, scopes pairwise disjoint | OK — unchanged |
| task tools and GT closed; uuid8s independent and frozen | OK — unchanged |
| trees: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input`, ≥1 `owner=user` write, no cycle | OK — unchanged and re-verified; both trees still hold |
| self-sufficient baseline per computation | OK — all five give a definite figure (7.00 / 76.40 / 164.00 / 180 / 6.00), each different from gold, and `baseline.params` is now honest in all five |
| 4–6 factors, 2 `parameter`, 1 `method`; per task ≥1 multi-source, ≥1 cross-difficulty | OK — 4/6/4/6/6; task 0 and task 1 each carry one multi-source and one cross-difficulty factor, seeded |
| every ladder ≥3 tiers stated in full in its rule | **OK now** — the one ladder that was not (the ceiling) has been struck rather than restated |
| tiers distinct in outcome; conditions and outcomes ones the business holds | OK — including the two new counter ladders, checked on all six variants |
| every factor bears weight against an honest baseline | **OK — 26 of 26.** Round 1's single decoration factor is gone and its replacement is load-bearing |
| baseline alone gives a definite number different from gold | OK — 7.00 vs 29.60; 76.40 vs 110.40; 164.00 vs 204.00; 180 vs 267; 6.00 vs 484.00 |
| instantiation gates re-run on the final form | OK — coordinator's snapshot re-confirmed; not re-run by this audit, to avoid `replay_tasks.py`'s in-place write-back (see revision_1 `### write-domain disclosure`) |

### summary of verdicts (revision_2)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
|---|---|---|---|---|
| 0 | **PASS** (was SOURCE-POLICY RED) | **PASS** | **PASS** | **PASS** (was FAIL) |
| 1 | **SOURCE-POLICY RED** — R2-1 | **PASS** | **PASS** (was SOURCE-FACTOR RED) | **PASS** |

Round 1: 4 reds. Round 2: **1 red**, and it is the surviving half of one of them. Three of the four round-1 reds (F-2, F-3, F-4) are genuinely closed, as are all seven observations. Nothing that passed in round 1 has regressed: both problem trees still hold, every edge still bears weight, and no factor became decoration.

---

# revision_3

Re-audit round 3. Revisions 1 and 2 above are left untouched.

## charter_global_frozen (revision_3)

- re-audit time: 2026-09-21, after the round-2 rework. Auditor unchanged.
- **Verification, not a blind audit, and recorded as such.** This auditor has seen the GT of rounds 1 and 2. Every figure below was recomputed from the round-3 artifacts before the round-3 GT fields were read, but the answers were already known and none of them moved. No blindness is claimed.

| artifact | round 2 | round 3 | re-derived? |
|---|---|---|---|
| `pdp.extended.yaml` | `c6f4e077813cd9eb` | **`e3fc9ffc65094eef`** | yes, in full — the charter moved |
| `task_tools.py` | `fb6f31940de52a89` | `fb6f31940de52a89` (unchanged) | carried forward by hash |
| `_masked_views/0.masked.json` | `f3afa8daff0aea8d` | `f3afa8daff0aea8d` (unchanged) | world carried forward by hash |
| `_masked_views/1.masked.json` | `2cb5870a2ea9489f` | `2cb5870a2ea9489f` (unchanged) | world carried forward by hash |

All four recomputed on disk and matching the coordinator's brief. Per the carry-forward rule the charter-global section is re-derived in full because `pdp.extended.yaml` moved; the tool module and both worlds are byte-identical, so the conclusions that rest on them alone (uuid8 independence, tool bodies judging no prerequisite, persona need/authorisation/closure, seeded near-misses, cross-difficulty rows present) are carried forward by hash rather than re-derived.

**On the task-file hashes.** The coordinator's byte-instability caveat is accepted and matches this auditor's revision-1 disclosure: `replay_tasks.py` rebuilds `db_closure` from a set iteration, so it is semantically idempotent but byte-unstable. `replay_tasks.py` was **not** run by this audit in round 2 or round 3. The stable identity used here is the masked-view hash plus the charter hash.

### what actually changed in the charter

A diff of all five policies, round 2 against round 3, shows changes in exactly three of them and nothing else:

1. `pdp_ext_counter_cost_share` — the ceiling. `compute[price_ceiling]` changed from `price_used` to `rejected_fill_price if rejected_fill_price > 0 else price_used`, and the matching sentence was extended in `rule`, in `compute_basis[price_ceiling]` and in `baseline.rule` to "…however the multiplier falls; **where that fill carries no such price, the price the cost share is taken from serves as the ceiling instead**." Also `inputs.history[3]`'s filter changed from `pharmacy_network_status: preferred_retail` to `coverage_stage_at_fill: deductible`.
2. `pdp_ext_premium_arrears_settlement` — `inputs.history` gained an `adjustment_reason_code` filter on its credit-count entry and a second credit-count entry, one per reason code.
3. `pdp_ext_troop_restatement` — `cross_category[allowance].reads` gained `allowance_card_ledger.event_type`, `.merchant_category` and `.settlement_status`.

`pdp_ext_penalty_relief` and `pdp_ext_exception_approval_term` are byte-identical to round 2.

### disposition of every round-2 item

Verified against the artifacts. The reworker's claims were supplied by item id only.

---

**R2-1 — CLOSED. Verified on this auditor's own counter-example, re-run rather than accepted.**

The reworker's report that the two readings now agree was not taken on trust. The round-2 counter-example script was re-run unchanged against the round-3 charter — the same hypothetical world, built by the same code: Harold Deakins's record with the paid fills reduced to two, both moved to `coverage_stage_at_fill: initial_coverage`, so that `paid_fill_count` = 2 < `settled_therapy_fill_count` = 3 and `fills_at_deductible_stage` = 0.

| binding | round 2 | round 3 |
|---|---|---|
| `rejected_fill_price` (held fill) | 786.00 | 786.00 |
| `paid_fill_count` | 2 | 2 |
| `price_used` (fall-through tier) | 128.00 | 128.00 |
| `supply_share` | 153.00 | 153.00 |
| `member_share` | 153.00 | 153.00 |
| **`price_ceiling`** | **128.00** | **786.00** |
| **result, compute as written** | **128.00** | **153.00** |
| **result, rule reading (ceiling := held fill price)** | **153.00** | **153.00** |

The two readings that differed by 25.00 in round 2 now coincide at **153.00**. The divergence is closed at its root: `compute` now binds the ceiling to the held fill's own price, which is what `rule`, `compute_basis[price_ceiling]` and `baseline.rule` have said throughout.

**The new fall-back branch was tested for a second reading of its own, and does not open one.** A world was built in which the held fill carries no negotiated price (`negotiated_price` set empty on `fa59216c-…`, everything else unchanged): `rejected_fill_price` = 0.00, so the branch fires; `price_used` takes its own tier 2 (`rejected_fill_price <= 0` and 5 ≥ 3) and returns `latest_paid_price` = 36.00; `price_ceiling` = **36.00**. The rule says "where that fill carries no such price, **the price the cost share is taken from** serves as the ceiling instead", and "the price the cost share is taken from" is exactly `price_used`. Compute and rule name the same binding, and `price_used` is itself fully determined by its own three-tier ladder, which is stated in full in the rule. One reading, in both branches.

*One residual idiom, recorded and not red-lighted.* `rejected_fill_price` is `float(LATEST(...) or 0)`, so a held fill recording a negotiated price of exactly 0.00 would be treated as carrying no price, and the ceiling would fall back rather than cap at zero. This `or 0` coalescing is the charter's idiom throughout (it appears identically on `latest_penalty_charged`, `latest_premium_payment`, `rejected_fill_days`, `out_of_network_latest_price` and others) and a zero negotiated price is not a case this line of business produces — the plan pays the balance of the negotiated price, so a zero price would mean the pharmacy is owed nothing. Not a defect, noted for completeness.

**Leaving the ceiling override withdrawn is still right, now that the branch exists.** Checked explicitly, as the coordinator asked.
- Base `pdp_point_of_sale_cost_share` states: "the member never pays more than the negotiated price however the multiplier falls."
- Where the held fill carries a negotiated price, the extended ceiling is that same price. **Identical to base**, so nothing is overridden.
- Where the held fill carries none, base's clause has no referent — there is no negotiated price to cap at. The extended supplies a value where base is silent, which is gap-filling, not overriding.
- Moreover the value it supplies is not a new one. The surviving `overwrite` entry already declares that in exactly this circumstance "the cost share is taken from a price standing on another of the member's fills rather than from that fill". The ceiling sentence says the ceiling follows *that already-declared substituted price*. It is a consequence of a declared override, not a second undeclared one.
- Nor does it admit a rival "no cap at all" reading: the extended rule states the fall-back cap outright in the same sentence, so a reader has no gap to fill by inference.

**Proof-field correction verified.** `tasks/1.json` → `design_rationale` now carries an explicit retraction rather than a quiet deletion: "(The round-2 write-up justified striking it with the claim that 'a ceiling at p can never bind on any world'. That claim was **FALSE and is retracted here**: its premise was conditional while its conclusion was not, it reasoned only about the boundary-split branch and ignored the fall-through branch where member_share is supply_share and unrelated to the price, and the ceiling in compute was never p but price_used…)". All three of this audit's refutation counts are named and conceded. The surrounding account is now true: the factor was struck for the right reason (its declared baseline `latest_paid_price` was a figure `baseline.rule` never selects, and under the honest baseline of 786.00 the scored value was unchanged at 473.98).

---

**R2-2 — CLOSED, and independently re-swept under a stricter test than the one that found it.**

The reworker reports 21 of 21 declared inputs matching a real call, and reports finding a second stranded entry this audit had not seen. Both verified, and this audit's round-2 method is corrected below.

*Independent sweep, strict.* Every `inputs.history` entry of all five policies was parsed and matched against the DSL calls its own `compute` actually makes, requiring **exact equality of the filter set** and **exact equality of the window**, not containment: **21/21 match.** Zero stranded.

*This audit's round-2 sweep was too permissive, and that is why it missed the second entry.* The round-2 matcher asked whether every declared filter string appeared in some call's arguments — a subset test. Round 2's arrears entry declared `{event_type: pdp_premium_credit_adjustment}` with no reason code, while the only credit-counting calls were `COUNT(..., event_type='pdp_premium_credit_adjustment', adjustment_reason_code='retroactive_rate_change')` and the same with `billing_error_correction`. Under a subset test the declared entry matched the first of those; under the exact test it matches neither, because no call counts *all* credit adjustments. The entry was a genuine leftover of round 2's credit narrowing — the same edit that this audit did check, and passed. **The reworker found a real defect that this audit missed**, and the fix is right: the entry now carries `adjustment_reason_code: retroactive_rate_change` and a second entry carries `billing_error_correction`, one per call. The counter policy's entry likewise moved from the struck factor's `pharmacy_network_status: preferred_retail` to `coverage_stage_at_fill: deductible`, which matches `fills_at_deductible_stage`.

The coordinator's warning — that a sweep calibrated to a known defect can miss an unknown one — was well placed, and it was this audit's sweep that it applied to.

---

**R2-3 — CLOSED, checked at field level in both directions.**

`pdp_ext_troop_restatement.cross_category[allowance].reads` now lists `status`, `otc_quarterly_sublimit`, `allowance_card_ledger.amount`, `allowance_card_ledger.event_type`, `allowance_card_ledger.merchant_category`, `allowance_card_ledger.settlement_status`.

Both directions were tested mechanically, extracting every `CFIELD` / `CPARAM` / `X*` field and filter field from each policy's `compute` and comparing the two sets:

| policy / category | undeclared reads | declared but unused |
|---|---|---|
| `pdp_ext_penalty_relief` / `egwp` | none | none |
| `pdp_ext_troop_restatement` / `allowance` | none | none |

No read is performed that is not declared, and no read is declared that is not performed. The charter's convention is now uniform across both cross-category policies.

*Noted from the coordinator:* the field-level gap does not reproduce in the advantage difficulty, so it was a real defect here rather than a universal property of `check_extended`. That is consistent with what was found here — one of this difficulty's two cross-category policies had it and the other never did.

---

**R2-4 — the reworker declines to change the ladder. This audit rules that the refusal is correct, and closes the observation.**

The requirement is that no two tiers of a ladder, the fall-through included, select the same value **or method**. `term_counting_basis` is a `method` factor, and what its tiers select is a method. The three are:
1. "the term is taken in whole thirty-day supply cycles and rounded down to a whole cycle";
2. "the term is taken in whole weeks and rounded down to a whole week";
3. "the term is counted as booked".

These are three distinct algorithms, and the label is honest — each changes how the quantity is computed rather than substituting a number. The distinctness requirement is therefore met as stated.

The residual coincidence is arithmetic, not structural: 180 and 90 are both divisible by 30, so tier 1 and the fall-through return the same integer for the ordinary and expedited terms. No tier has been "written as two" — that is the shape the rule guards against, and it is not this. On the maintenance term, which is the term this task's computation actually starts from, the three tiers return **360 / 364 / 365**, all distinct, so the ladder discriminates where it is scored and the factor bears weight (272 against a gold of 267).

**R2-4 is closed.** It was recorded as an observation in revision 2 and is discharged here rather than carried forward.

### policy_conflict_scan (revision_3)

Re-run in full on the moved charter. Base copy re-checked key by key against `blueprint/products/pdp.yaml` — `category`, `display_name`, `binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`, `measures`, `policies` all compare equal, the only extra key being `extended_policies`. Five policies, five distinct target tools, five distinct computed quantities, no overlap of subject, trigger, time anchor or terminal state. Task scopes unchanged, pairwise disjoint and jointly complete.

### rule_compute_equivalence (revision_3)

Swept sentence by sentence over all five policies. **No divergence remains.** The ceiling — the last one, R2-1 — is closed and verified above. Additionally, every non-fall-through tier condition of all 26 factors was checked for verbatim presence in its own policy's `rule`: **0 missing**. Every `compute` branch corresponds to a rule sentence and every rule sentence to a branch.

### action_binding_and_uuids (revision_3)

Carried forward by hash: `task_tools.py` is byte-identical to round 2 (`fb6f31940de52a89`). Five uuid8 tails `e1c246c8`, `7dfec3b3`, `a40a5cef`, `dd13544d`, `eaef344a` — distinct, no shared stem, not sequential, one per tool. Each `(target_tool, computes)` pair claimed by exactly one policy; re-verified against the moved charter.

### prerequisite_graph and prerequisite_sentences (revision_3)

Re-derived. Three edges, unchanged in shape, acyclic. Mechanically re-verified for all three: `policy_source` verbatim present in the blocked policy's own `rule` (3/3), absent from the depended-on policy's rule (3/3), `form: state` with no `fallback_reason` (3/3), each `value_input` gate a real binding name in the blocked policy's `compute` (2/2), and the `state_gate` still pointing at the real base eligibility `pdp_point_of_sale_cost_share.determination_on_record`.

### factor_ladders (revision_3)

| policy | factors | `parameter` | `method` | cross_difficulty |
|---|---|---|---|---|
| `pdp_ext_penalty_relief` | 4 | 2 | 2 | `egwp` |
| `pdp_ext_premium_arrears_settlement` | 6 | 2 | 4 | — |
| `pdp_ext_troop_restatement` | 4 | 2 | 2 | `allowance` |
| `pdp_ext_exception_approval_term` | 6 | 4 | 2 | — |
| `pdp_ext_counter_cost_share` | 6 | 3 | 3 | — |

Unchanged from revision 2 and still within bounds everywhere: 4–6 factors, ≥2 `parameter`, ≥1 `method` per policy; 10 factors on task 0 and 16 on task 1, matching `check_compute`; one multi-source and one cross-difficulty factor per task, both seeded. Every ladder has three tiers, all stated in the rule and implemented in compute.

### findings (revision_3)

**No new finding.** Every round-2 item is closed: R2-1 and R2-2 by verified fix, R2-3 by verified fix in both directions, R2-4 by a ruling in the reworker's favour. No regression was found in anything that passed in revision 2.

One methodological correction is recorded against this audit rather than against the artifacts: **this audit's revision-2 `inputs.history` sweep used a subset test where an exact test was required, and consequently missed the stranded arrears credit-count entry that the reworker found.** The revision-3 sweep is exact and is the one whose 21/21 result is relied on above. Recording this is not optional: a sweep whose method is weaker than its claim is exactly the kind of proof this audit red-lights in the artifacts.

## closing_checklist (revision_3)

**The difficulty CLOSES.** All four relationships hold for both tasks.

| Step 4 item | status |
|---|---|
| per-task files one-to-one with tasks, `_difficulty.md` alongside | OK |
| old revisions traceable | OK — revisions 1 and 2 preserved verbatim; revision 3 appended |
| every comparison section carries a PASS | **OK** — `0.md` and `1.md` both PASS on all four relationships in revision 3 |
| extended policies fully covered; scopes pairwise disjoint, each spanning its whole tree | OK — task 0 `{penalty_relief, arrears}`, task 1 `{troop, exception, counter}` |
| task tools and GT closed; each uuid8 independently generated and frozen | OK — module byte-identical to round 2 |
| trees: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input`, ≥1 `owner=user` write, no cycle; difficulty-level graph still a DAG | OK — task 0 n=1/1 `value_input`; task 1 n=2/1 `value_input`; both carry an `owner=user` write; no cross-task edge |
| every computation declares a self-sufficient baseline, four to six factors (2 `parameter`, 1 `method`), per task ≥1 multi-source and ≥1 cross-difficulty | OK |
| every ladder ≥3 tiers stated in full in its rule; tiers distinct in outcome; conditions and outcomes ones the business holds | OK — 0 tier conditions missing from their rules; R2-4 ruled on and closed |
| every factor bears weight against an honest baseline | OK — **26 of 26**, recomputed this round |
| baseline alone gives a definite number different from gold | OK — 7.00 / 76.40 / 164.00 / 180 / 6.00 against 29.60 / 110.40 / 204.00 / 267 / 484.00 |
| instantiation gates re-run on the final form | OK — coordinator's snapshot accepted and cited; not re-run here, deliberately, because `replay_tasks.py` writes its task files back in place (revision-1 disclosure; confirmed by the coordinator as semantically idempotent but byte-unstable) |

### summary of verdicts (revision_3)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
|---|---|---|---|---|
| 0 | **PASS** | **PASS** | **PASS** (10/10) | **PASS** |
| 1 | **PASS** | **PASS** | **PASS** (16/16) | **PASS** |

Round 1: 4 reds, 7 observations. Round 2: 1 red, 3 observations. Round 3: **0 reds, 0 open observations.** No scored value moved this round — 29.60, 110.40, 204.00, 267 and 484.00 are all unchanged, as are all 26 factor sensitivities and all five baseline results.

**This difficulty passes the source-layer audit.**

---

# revision_4

Re-audit round 4, prompted by a KB-layer finding that traced to a frozen-base defect. Revisions 1–3 above are left untouched.

## charter_global_frozen (revision_4)

- re-audit time: 2026-09-21. Auditor unchanged.
- **Verification, not a blind audit, and recorded as such.** This auditor has seen this difficulty's GT in rounds 1–3. Every figure below was recomputed from the round-4 artifacts before the round-4 GT fields were read, but the answers for four of the five computations were already known and unmoved, and the fifth had been reported in the brief. No blindness is claimed.

| artifact | round 3 | round 4 | re-derived? |
|---|---|---|---|
| `pdp.extended.yaml` | `e3fc9ffc65094eef` | **`d0436e4d65dfe61e`** | yes — the charter moved |
| `task_tools.py` | `fb6f31940de52a89` | `fb6f31940de52a89` (unchanged) | carried forward by hash |
| `_masked_views/0.masked.json` | `f3afa8daff0aea8d` | `f3afa8daff0aea8d` (unchanged) | world carried forward by hash |
| `_masked_views/1.masked.json` | `2cb5870a2ea9489f` | `2cb5870a2ea9489f` (unchanged) | world carried forward by hash |
| `blueprint/products/pdp.yaml` | (not recorded) | `ea1fa7d73e43339f` | read-only; see below |

**Base integrity.** Base is frozen and was not to be edited. This audit cannot prove a negative from a hash it never recorded, so it checked the property that matters instead: the extended file's verbatim copy of the base section still compares **equal, key by key**, to `blueprint/products/pdp.yaml` — `category`, `display_name`, `binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`, `measures`, `policies`. The gloss the coordinator identified as the root cause is still present and unchanged at `blueprint/products/pdp.yaml:95`: `tier_3_preferred_brand_copay_30: Member copay for a 30-day tier 3 fill at a preferred retail pharmacy, in USD.` Base was routed around, not edited.

`replay_tasks.py` was again not run, per the standing byte-instability finding; the stable identity used here is the masked-view hashes plus the charter hash.

### what changed in the charter

A diff of all five policies, round 3 against round 4, shows changes in exactly two:

1. **`pdp_ext_counter_cost_share` — the extended-supply reformulation.** `one_month_share = tier_figure + standing_differential` is gone. In its place `supply_charge` multiplies `tier_figure` **alone**, and `fill_cost_share = supply_charge + standing_differential` applies the pharmacy standing **after** the multiplication. `member_share` now consumes `fill_cost_share`. The rule, `compute_basis`, `baseline.rule` and the `extended_supply_basis` ladder are all rewritten to match, and a second `overwrite` on `pdp_point_of_sale_cost_share` is added.
2. **`pdp_ext_premium_arrears_settlement` — the `billing_period` sentence tightened.** "…applied to the oldest coverage month the account still shows unsettled" becomes "…applied to the oldest coverage month for which the account still shows **a premium component** unsettled; a coverage month whose basic and supplemental premium components are both settled is not reopened by a late enrollment penalty still standing against it, because premium and penalty are relieved by different events and either may be owed without the other." `overwrite` stays at 2 entries.

`pdp_ext_penalty_relief`, `pdp_ext_troop_restatement` and `pdp_ext_exception_approval_term` are byte-identical to round 3.

---

### 1. Does the reformulation close the contradiction on every world, or only on the seeded fill?

**On every world. The fix is structural, and that was tested exhaustively rather than argued.**

The contradiction was between two things that both claim to say what the extended-supply multiplier acts on:
- base, `parameter_schema`: `mail_order_90_day_multiplier: Multiplier applied to **the 30-day preferred retail cost share** for a 90-day mail-order fill` — and `retail_90_day_multiplier` identically;
- the round-3 extended rule: the multiplier acted on "the one-month figure", which was `tier_figure + standing_differential` — i.e. for a standard-retail fill, the **standard** retail figure, not the preferred one.

The round-4 rule multiplies "the figure the formulary tier gives", implemented as `tier_figure`, whose three tiers are `P('tier_3_preferred_brand_copay_30')`, `P('tier_1_preferred_generic_copay_30')` and `P('tier_2_generic_copay_30')` — and all three of those parameters are glossed in base as "Member copay for a 30-day tier N fill **at a preferred retail pharmacy**" (`pdp.yaml:93`, `:94`, `:95`). So the multiplicand is, by construction, exactly the quantity the multiplier gloss names.

The structural property that makes this universal rather than incidental: **`tier_figure`'s expression does not reference `rejected_fill_network` at all** — verified mechanically. Only `standing_differential` depends on the pharmacy standing, and it now sits outside the multiplication. The multiplicand therefore cannot vary with the dispensing pharmacy on any world.

*Exhaustive test.* All 540 combinations of 6 variants × 6 formulary tiers × 5 pharmacy standings × 3 days-supply values were enumerated, and for every combination where a multiplier fires the multiplicand was compared against the 30-day preferred-retail cost share the base gloss names:

| formulation | multiplied cases diverging from the base gloss |
|---|---|
| round 3 (`tier_figure + standing_differential`) | **24** |
| round 4 (`tier_figure` alone) | **0** |

The 24 are exactly the standard-retail extended-supply fills on the two tiers that carry a standard-retail parameter — preferred brand and preferred generic — across all six variants (2 tiers × 2 day-lengths × 6 variants). Task 1's seeded fill (Value, tier 3, standard retail, 90 days) is one of those 24, so the KB auditor caught an instance of a class, and the reformulation removes the whole class rather than the instance. **A fix that only worked on the seeded world would have left 23 others; there are none.**

### 2. Is the new `overwrite` legal and honest?

**Yes, on all three counts.**

- `base_policy: pdp_point_of_sale_cost_share` — the policy **exists** in `blueprint/products/pdp.yaml` and **is in this policy's own `base_policy_refs`** lineage. Both checked mechanically.
- `superseded_clause: "mail order and ninety-day retail fills take the one-month figure multiplied by the tier's extended-supply multiplier"` — **verbatim present** in that base policy's `rule`. Checked by string containment against the base text, not by eye.
- `replaced_by: "The cost share for the fill is the supply charge the fill earns together with whatever the dispensing pharmacy's standing adds, and the multiplier never acts on what the pharmacy's standing adds."` — **verbatim present** in the extended `rule`.
- **And it is genuinely what the extended layer does**, which is the part a quotation check cannot establish: `compute[supply_charge]`'s multiplicand references `tier_figure` and does **not** contain `standing_differential` (checked on the expression text), and `compute[fill_cost_share]` is exactly `supply_charge + standing_differential`. The declaration describes the implementation.

The residual divergence from base is real and is now named: base multiplies "the one-month figure", the extended multiplies the tier figure and adds the standing afterwards. That is a genuine conflict over the quantity that gets scored, and it is declared sentence by sentence rather than hidden in an intermediate — which is precisely what round 1's F-4 found missing elsewhere.

### 3. Do all six counter factors still bear weight?

**Yes — 6 of 6, recomputed independently on the new world.** The reworker's figures were not taken on trust; each was reproduced by substituting that factor's declared `baseline` into the round-4 compute and replaying.

| factor | tier taken | result under its baseline | ≠ gold 477.32 |
|---|---|---|---|
| `formulary_tier_figure` | 1 (preferred brand) | 422.93 | yes |
| `pharmacy_standing_addition` | **1 (standard retail + preferred brand)** | 473.98 | yes |
| `extended_supply_basis` | **2 (>30 days, retail)** | 435.33 | yes |
| `acting_price_basis` | 1 | 128.00 | yes |
| `deductible_still_to_be_met` | 1 | 645.24 | yes |
| `stage_boundary_split` | 1 | 139.00 | yes |

Whole baseline **6.00**, definite and different from gold. Every figure matches the coordinator's report exactly.

**The specific risk the coordinator named did not materialise.** The worry was that moving what the multiplier acts on could drop a factor onto its fall-through and make it decorative — the class red-lighted in rounds 1 and 2, and the reason route 1 was rejected. Checked directly on the handling-time world: `standing_differential` = **7.00**, which is `pharmacy_standing_addition`'s **tier 1**, not its fall-through of nothing; and `supply_charge` = **132.00** = 44.00 × 3.0, which is `extended_supply_basis`'s **tier 2**, not its fall-through. Both factors remain off their fall-through, and each still moves the scored value.

Worth noting for the record: `pharmacy_standing_addition`'s baseline result is **473.98**, which is the round-1 and round-2 gold. That is arithmetic coincidence, not a regression — under its baseline the standing adds nothing, so `fill_cost_share` = 132.00, which is what the old formulation produced for this fill before the standing was folded in. The scored value is 477.32 and the factor's margin over its baseline is 3.34, small but real.

Hand-checked independently of the evaluator: `tier_figure` 44.00; `standing_differential` 51.00 − 44.00 = 7.00; `supply_charge` = RND(44.00 × 3.0, 2) = 132.00; `fill_cost_share` = 139.00; `deductible_left` = 615.00 − 204.00 = 411.00; `member_share` = 411.00 + RND(139.00 × 375 ÷ 786, 2) = 411.00 + 66.32 = **477.32**; ceiling 786.00, which does not bind.

### 4. Is the `billing_period` change genuinely a refinement?

**Yes — but this is the one judgment call of this round, so both sides are set out.**

*What moved.* Round 2 and round 3 carried "The money the member settles is applied to the oldest coverage month the account still shows unsettled." On task 0's world that sentence admits two readings: May's **premium** is settled by the May payment, but May still carries an unrelieved **penalty** charge of 7.40, so a reader taking "unsettled" to cover any outstanding component selects `2026-05`, while a reader taking it in the premium sense selects `2026-08`. Round 4's sentence rules the first reading out explicitly.

*The case that it is a refinement, which this audit accepts.*
- Base `pdp_premium_posting` says "Money the member pays is posted against the oldest unpaid coverage month first, and within a coverage month against the premium components before the penalty", with `params.posting_order_basis` restating it as "oldest unpaid billing_period first, and inside a month the basic and supplemental premium components before the late enrollment penalty". **Base orders components inside a month; it nowhere defines which months count as unpaid.** The term "unpaid coverage month" is used and not cashed out.
- The direction the extended picks is the one base's own billing rule points to. `pdp_premium_billing` states: "The late enrollment penalty is billed as its own component of the same coverage month, **never folded into the premium, because the two are relieved by different events and a member may owe one without the other.**" The extended sentence's stated reason — "because premium and penalty are relieved by different events and either may be owed without the other" — is a paraphrase of that base sentence. The refinement is grounded in base, not opposed to it.
- Nothing in base is weakened. Oldest-first still governs, and premium-before-penalty within a month still governs; neither is touched. The extended adds a determination where base is silent, which is what `overwrite: []` correctly reports.

*The case against, stated honestly.* Base's clause "within a coverage month against the premium components before the penalty" presupposes that a month can carry both, and a literal reader could infer that a month carrying only an outstanding penalty is still an "unpaid coverage month" — which would select `2026-05` and make the extended sentence a narrowing of base rather than a completion of it. On that reading the change would need declaring.

*Ruling.* Base uses an undefined term and supplies, in its own adjacent billing policy, the reason for resolving it the way the extended does. That is indeterminacy resolved, not a stated base conclusion replaced. **Refinement; `overwrite: []` is not a false declaration.** The refinement is itself unambiguous on the world: May, June and July premiums are each cleared by a 38.20 payment, August carries 38.20 charged against a 10.40 credit and so still shows a premium component unsettled, and August precedes September — one reading, `2026-08`, which is what gold carries.

*A correction against this audit's own record.* Revisions 2 and 3 each reported T0-3 as "unchanged — the `billing_period` argument is still pinned by the inherited base sentence". That was **imprecise from round 2 onward**: the extended rule had carried its own sentence ("…applied to the oldest coverage month the account still shows unsettled") since round 2, and this audit did not notice it had appeared, nor that it was two-way ambiguous. The ambiguity was caught downstream instead. Recorded here rather than quietly superseded.

### 5. Regression sweep

Every check that closed in rounds 2 and 3 was re-run against the round-4 charter.

| check | result |
|---|---|
| base copy verbatim against `blueprint/products/pdp.yaml` | **equal on all 10 keys** |
| declared `inputs.history` matching a real compute call, strict on filters **and** window | **21/21**, zero stranded |
| cross-category reads, both directions, at field level | `egwp` and `allowance`: **no undeclared read, no declared-unused read** |
| every non-fall-through ladder tier condition verbatim in its own policy's `rule` | **0 missing of 26 factors** |
| prerequisite sentences verbatim in the blocked rule, absent from the depended-on rule | **3/3 and 3/3** |
| `form: state` on every edge, `fallback_reason` absent | **3/3** |
| factor counts and labels | 4 / 6 / 4 / 6 / 6; per policy 2+2, 2+4, 2+2, 4+2, 3+3 `parameter`+`method` — all within 4–6 with ≥2 `parameter` and ≥1 `method` |
| draw counts | task 0: 2 computations, 10 factors, 1 cross-difficulty; task 1: 3, 16, 1 — matching the coordinator's `check_compute` line |
| task 0 figures | 29.60 / 110.40, baselines 7.00 / 76.40, all 10 sensitivities, edge weight 110.40 vs 140.00, `billing_period` `"2026-08"` — **all unmoved** |
| task 1 unmoved figures | 204.00 and 267, with all ten of their sensitivities and both baselines — **unmoved** |
| problem trees | both unchanged; task 0 n=1 with 1 `value_input`; task 1 n=2 with 1 `value_input` and 1 `state_gate`; both carry an `owner=user` write; graph still acyclic |
| overwrite counts | penalty_relief 3, arrears 2, troop 1, exception 0, counter **2** (was 1) — the increase is the declared reformulation |

Nothing regressed.

### findings (revision_4)

**No new defect, and no red light.** The four round-4 questions are answered: the reformulation closes the contradiction on every world (0 of 540 divergent, against 24 before), the new `overwrite` is legal and honest on quotation, lineage and substance, all six counter factors still bear weight with none on a fall-through, and the `billing_period` change is a genuine refinement of an undefined base term rather than an undeclared override.

One observation is recorded against **this audit** rather than against the artifacts: revisions 2 and 3 reported the `billing_period` argument as pinned only by base, having failed to notice that an extended sentence had appeared in round 2 and that it was two-way ambiguous. The defect was real and was caught by the KB layer instead. It is recorded for the same reason the revision-3 sweep correction was: a proof this audit issues is held to the standard it applies to the artifacts.

## closing_checklist (revision_4)

**The difficulty CLOSES at the source layer.** All four relationships hold for both tasks, on the round-4 artifacts.

| Step 4 item | status |
|---|---|
| per-task files one-to-one with tasks; `_difficulty.md` alongside | OK |
| old revisions traceable | OK — revisions 1, 2 and 3 preserved verbatim; revision 4 appended |
| every comparison section carries a PASS | **OK** — `0.md` and `1.md` both PASS on all four relationships |
| extended policies fully covered; scopes pairwise disjoint, each spanning its whole tree | OK — unchanged |
| task tools and GT closed; each uuid8 independently generated and frozen | OK — tool module byte-identical since round 2 |
| trees: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input`, ≥1 `owner=user` write, no cycle | OK — re-verified |
| self-sufficient baseline per computation; 4–6 factors, 2 `parameter`, 1 `method`; per task ≥1 multi-source, ≥1 cross-difficulty | OK |
| every ladder ≥3 tiers stated in full in its rule; tiers distinct in outcome | OK — 0 tier conditions missing |
| every factor bears weight against an honest baseline | **OK — 26 of 26**, recomputed on the round-4 charter |
| baseline alone gives a definite number different from gold | OK — 7.00 / 76.40 / 164.00 / 180 / 6.00 against 29.60 / 110.40 / 204.00 / 267 / **477.32** |
| every base/extended conflict declared | OK — 8 `overwrite` entries across the charter, each verbatim in base and in the extended rule, each describing what the compute does |
| instantiation gates re-run on the final form | OK — coordinator's snapshot accepted and cited, including `check_traceability`; not re-run here, deliberately, because `replay_tasks.py` writes its task files back in place |

### summary of verdicts (revision_4)

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
|---|---|---|---|---|
| 0 | **PASS** | **PASS** | **PASS** (10/10) | **PASS** |
| 1 | **PASS** | **PASS** | **PASS** (16/16) | **PASS** |

Round 1: 4 reds, 7 observations. Round 2: 1 red, 3 observations. Round 3: 0 reds. Round 4, after a KB-driven source change: **0 reds, 0 open observations against the artifacts.**

**This difficulty passes the source-layer audit on the round-4 artifacts.** The scored values it now stands on are 29.60 and 110.40 for task 0, and 204.00, 267 and 477.32 for task 1.
