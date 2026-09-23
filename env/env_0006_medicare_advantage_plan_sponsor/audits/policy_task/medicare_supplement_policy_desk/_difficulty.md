# Policy-task audit — medicare_supplement_policy_desk / charter-global

## charter_global_frozen

| item | value |
| --- | --- |
| `medigap.extended.yaml` | sha256[:16] = `ff66c1f9a56e6aa9` |
| `task_tools.py` | sha256[:16] = `11d4619938c51ac9` |
| freeze time | 2026-09-21T13:59:45Z (written before any task's GT was revealed) |
| auditor | independent policy-task auditor (erl-task-policy-audit), single pass over M=2 |
| permitted | `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/*.yaml`, this difficulty's `medigap.extended.yaml` and `task_tools.py`, `erlbench/`, and the two masked views |
| explicitly masked | `evaluation_criteria`, `computations` (expected, factor_trace, factor_sensitivity, baseline_result, step/arg), `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`; `env/.../worklog.md` was left unread |
| contamination | none. No scored value, gold parameter or intermediate reached this file or either task file before that task's freeze. No recursive grep was run with `tasks/*.json` in the match domain. |

Entry conditions (Step 0) are met and are cited, not re-run: the coordinator supplied the actual output lines of `check_extended`, `check_task_tools`, `replay_tasks`, `check_solvability`, `check_compute`, `check_grounding` and `check_cross_fire`, all green; the two masked views are on disk and their sha256[:16] (`24f623ed4dfca1fe`, `ed75098b8a5f6c96`) were re-verified against the brief and match. `check_traceability` cannot run before the render step and `check_cache_diff` is informational; both are correctly out of scope here.

### policy_conflict_scan

The base section of `medigap.extended.yaml` was compared key by key against `blueprint/products/medigap.yaml`: **verbatim identical** on all ten base keys (`accounts`, `binding`, `category`, `display_name`, `events`, `lifecycle`, `measures`, `parameter_schema`, `policies`, `variants`); the only added key is `extended_policies`. The base copy has not been rewritten.

Eleven base policies and five extended policies were scanned for overlapping subjects, triggers, eligibility, time anchors, action parameters, terminal states and cross-category read boundaries.

| subject / quantity | base owner | extended owner(s) | compatible? |
| --- | --- | --- | --- |
| `medigap_premium_refund` | `medigap_premium_billing_and_posting` | `medigap_ext_dual_coverage_premium_return` | yes — base's refund sentence is scoped to *termination* ("Premium already paid for cover beyond a termination date is returned on the tier's unearned premium basis"); the extended policy fires on an in-force policy (`policy_end_date` empty) for an inception overlap. Disjoint situations. |
| `medigap_premium_payment` | `medigap_premium_billing_and_posting` | `medigap_ext_premium_account_settlement` | yes on posting order and dedup; **no** on the discount stack — see finding CG-1 |
| premium construction | `medigap_premium_rating` | `medigap_ext_premium_account_settlement` | **no** — see findings CG-1 and CG-2 |
| `medigap_claim_adjustment` | `medigap_claim_adjustment_and_recovery` | `medigap_ext_uncovered_day_line_restatement`, `medigap_ext_uncovered_day_direct_repayment` | split cleanly by who received the money (base: "Money the supplement overpaid a provider is recovered from that provider and never from the policyholder, unless the policyholder was paid directly"); restatement takes the automatic-crossover lines, repayment the member-submitted ones. **Per-line granularity diverges** — see finding CG-3 |
| `medigap_claim_crossover_processed` | `medigap_benefit_payment` | `medigap_ext_crossover_benefit_settlement` | yes — the one conflicting sentence (the high-deductible basis) is **declared** in `overwrite` |
| Medicare Advantage exclusivity | `medigap_exclusivity_with_medicare_advantage` | read as `cross_category` branch by policies 1 and 3 | yes — read-only, no write claimed |

Cross-category read boundaries: exactly two extended policies declare `cross_category`, both against `advantage`, both `as: branch`, reading `coverage_end_date` (policies 1 and 3) and additionally `specialist_copay` (policy 3). No extended policy writes into another category. This matches the `cross-cat=2` the EXTENDED gate reports.

**Task scope exclusivity and completeness.** The `prerequisite` graph partitions the five extended policies into exactly two connected components:

- component A: `medigap_ext_premium_account_settlement` → `medigap_ext_dual_coverage_premium_return`
- component B: `medigap_ext_crossover_benefit_settlement` → `medigap_ext_uncovered_day_direct_repayment` → `medigap_ext_uncovered_day_line_restatement`

The two components are disjoint and together cover all five policies. The two masked worlds match them one-to-one (task 0 seeds only `medigap_premium_ledger` event rows; task 1 seeds only `medigap_claim_crossovers` event rows), so the M=2 claimed scopes are pairwise disjoint and jointly complete. No policy is claimed twice and none is orphaned.

### rule_compute_equivalence

Check 2 was run over every binding of all five extended policies: each `compute` name carries a `compute_basis` entry, and every `compute_basis` value is a verbatim sentence of that policy's own `rule`. The sweep back — rule sentence by rule sentence — found every quantity, window, filter, tier, branch, cross-category read, acting base, cap/floor and rounding point implemented, **with two exceptions**, both recorded as findings CG-4 and CG-5 below.

Rounding discipline is uniform and correct across all five policies: each `result` binding rounds once at the end (`RND(..., 2)`) and clamps with `MX(0.0, ...)` exactly where the rule says "nothing is returned / nothing is payable / nothing is restated / never less than nothing"; policy 4 additionally carries the rule's "never more than what reached her" as `MN(reached_the_policyholder, ...)`.

Interval counting is consistent: every `within_months=n` window means `0 <= MONTHS(row_date, NOW) < n` (`skills/erl-task-instantiate/scripts/check_compute.py:271-278`), and every "since the policy took effect" window is written `months_since_effective + 1`, which is the correct closed-on-the-effective-month form.

Two lesser notes, neither a red light:

- `medigap_ext_uncovered_day_line_restatement.compute.outside_cover_liability_span` is written `A if F('policy_end_date') == '' else (B if F('policy_end_date') != '' else 0.0)`. The trailing `else 0.0` is unreachable: the two guards are exhaustive. Dead branch, no semantic effect.
- `medigap_ext_uncovered_day_line_restatement.compute.distinct_claims_outside_cover` counts rows with `line_sequence=1` as a proxy for "distinct Medicare claims". The rule's basis is "Where the lines outside cover belong to one Medicare claim". The proxy is faithful for every line shape the schema permits (a claim contributes exactly one `line_sequence=1` row), so this is an implementation choice rather than an invented basis.

### action_binding_and_uuids

Each `(target_tool, computes)` pair is claimed by exactly one policy; no pair repeats:

| policy | target_tool | computes | owner |
| --- | --- | --- | --- |
| `medigap_ext_dual_coverage_premium_return` | `post_overlap_premium_return_c83152d2` | `return_amount` | agent |
| `medigap_ext_premium_account_settlement` | `remit_supplement_settlement_23b5df61` | `settlement_amount` | **user** |
| `medigap_ext_uncovered_day_line_restatement` | `book_precoverage_restatement_aba9484f` | `liability_restated` | agent |
| `medigap_ext_uncovered_day_direct_repayment` | `repay_direct_benefit_f162ba18` | `repayment_amount` | **user** |
| `medigap_ext_crossover_benefit_settlement` | `settle_crossover_benefit_9f3dc765` | `supplement_payment_amount` | agent |

uuid8s: `c83152d2`, `23b5df61`, `aba9484f`, `f162ba18`, `9f3dc765`. All five are distinct, share no common prefix, are not sequential or adjacent in value, and none is another's tail rewritten. Each is frozen with its tool (it appears in the function name, in the policy's `target_tool` and nowhere else). PASS.

No docstring states an action's position in a sequence, names another tool, or carries an ordering word about another problem. The three phrases that read like ordering — "The call has completed when the confirmation naming the new account entry comes back", "You can see the payment on the account as soon as the confirmation naming it comes back", "once the money is back" — all describe the completion of *that same call*, which is the required completion sentence, not a cross-problem order.

Each function body was read: all five are a single `ctx.create` or `ctx.update` followed by a confirmation string. **No tool validates a prerequisite, refuses a call, raises, or emits a hint.** No tool aggregates history or works out an amount. PASS on the "tool layer judges no prerequisite" requirement for the whole difficulty.

One observation (OBS-A, no consequence): `book_precoverage_restatement_aba9484f` and `repay_direct_benefit_f162ba18` both promise in their docstrings that "the year's deductible accumulator falls by that amount", and `medigap_policies.deductible_accumulated` is declared in `db_schema.json` as "identically the sum of the deductible_accrual account deltas". Neither function writes that field — both only `ctx.create` a `medigap_claim_crossovers` row. The declared effect is therefore realised only as a ledger aggregate, and the stored field goes stale the moment either tool is called. This does not create a second scored answer, because `medigap_ext_crossover_benefit_settlement.rule` pins the quantity to the event rows in terms ("What counts toward that deductible is **measured from the claim record**"), which excludes the holding field.

### prerequisite_graph

Check 7 over the whole graph. Every extended policy has `prerequisite` filled in (`[]` on policies 1 and 3). Three edges are declared, all `kind: value_input`, all `form: state`, none carrying `fallback_reason` (correct — `fallback_reason` is required exactly on action-form edges, and there are none).

| blocked policy | → problem | gate | resolved_by | gate is a real binding of the blocked policy's compute | resolved_by == the depended-on policy's target_tool |
| --- | --- | --- | --- | --- | --- |
| `medigap_ext_premium_account_settlement` | `medigap_ext_dual_coverage_premium_return` | `returns_credited` | `post_overlap_premium_return_c83152d2` | yes | yes |
| `medigap_ext_uncovered_day_direct_repayment` | `medigap_ext_uncovered_day_line_restatement` | `recovered_from_others` | `book_precoverage_restatement_aba9484f` | yes | yes |
| `medigap_ext_crossover_benefit_settlement` | `medigap_ext_uncovered_day_direct_repayment` | `counted_toward_deductible` | `repay_direct_benefit_f162ba18` | yes | yes |

Every `problem` points at another extended policy id in this file; none points at a base policy or at itself. The graph is two disjoint chains (A: 2→1; B: 5→4→3) and is **acyclic**; no cross-task reference creates a cycle. Each edge's `kind` is `value_input` and each `gate` names a binding that genuinely enters that policy's arithmetic — `returns_credited` is subtracted in policy 2's `result`, `recovered_from_others` in policy 4's, `counted_toward_deductible` feeds `deductible_remaining` in policy 5's. Each `resolved_by` genuinely changes that binding's value (demonstrated per task in `0.md` / `1.md` under `problem_chain`). No `condition` is strengthened or weakened relative to the sentence it comes from, and no authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears anywhere in the three `prerequisite` blocks. PASS.

### prerequisite_sentences

Check 6, four-point test on each of the three edges. Each `policy_source` was confirmed **verbatim locatable in the blocked policy's own `rule`** and **absent from the depended-on policy's rule** (both checked mechanically).

**Edge 2 → 1.** "The amount a policyholder must pay to bring the account up to date is not fixed before the premium account carries the return owed on premium charged for months in which other Medicare coverage was still in force."
(1) ordering connective: "not fixed **before**". (2) what it waits on is a record-visible state — *the premium account carries a return entry of a named kind* — with no action, performer or tool. State form, as declared. (3) names no tool, policy id, snake_case token or row id. (4) strength matches `condition` exactly. **The one write that brings the state about:** `post_overlap_premium_return_c83152d2` is the only write in this difficulty that creates a `medigap_premium_ledger` row with `event_type='medigap_premium_refund'`; `remit_supplement_settlement_23b5df61` creates a `medigap_premium_payment`, and the other three write to `medigap_claim_crossovers`. Unique. Derivation: the sentence says the settlement waits on a return standing for the overlap months → the reader searches the charter for the policy whose result is a return of premium for months of dual coverage → `medigap_ext_dual_coverage_premium_return`, whose own rule opens "A Medicare Supplement policy pays nothing for any day on which a Medicare Advantage enrollment of the same member is still in force… and is returned to them as a correction of the rate charged" → its `target_tool`. One reading.

**Edge 4 → 3.** "What the policyholder is asked to send back is fixed only after the claim record carries the entry taking back what the supplement paid on the lines that fall outside cover **and reached someone other than her**."
(1) "only after". (2) record-visible state. (3) no tool/id/token. (4) matches `condition`. **Uniqueness of the resolving write is carried by the qualifier**: two writes of this difficulty put an adjustment on the claim record — `book_precoverage_restatement_aba9484f` (`claim_status='adjusted'`) and `repay_direct_benefit_f162ba18` (`claim_status='recovered'`). The clause "reached someone other than her" singles out the first, since the second is by construction the money that reached *her*. One reading, and the disambiguation is done by business words rather than by a tool name — this is the state form working as intended.

**Edge 5 → 4.** "What the supplement pays on a line waiting on it is fixed only after the claim record carries the entry recording the money the policyholder has sent back on the lines the supplement paid her for days the policy did not cover."
(1) "only after". (2) record-visible state. (3) clean. (4) matches. **Unique write:** the mirror qualifier "the money the policyholder has sent back" picks out `repay_direct_benefit_f162ba18` against the restatement. One reading.

No rule carries a second wording of its own dependency, another problem's id, or a tool name. An ordering-cue sweep (`before | after | only after | only once | until | not until | first | prior to | then | once`) over all five extended rules, with the three declared prerequisite sentences excluded, returned 22 hits — **every one of them intra-computational** ("That monthly premium is **then** multiplied…", "The line settled is **first** identified", "rounded to the cent **once** at the end", "falls **before** the day the policy took effect", "pays nothing **until** the liability… reaches the tier's high deductible"). None states an order between two problems. **No undeclared cross-problem order exists in any extended rule**, and no task's tree rests on a base rule sentence that states a cross-problem order. PASS.

### override_declarations

Check 1's finding half, run sentence by sentence over every `base_policy_refs` entry of all five extended policies. Four of the five declare `overwrite: []`; `medigap_ext_crossover_benefit_settlement` declares one override.

The one **declared** override is well formed: it names `medigap_benefit_payment`, quotes the superseded clause verbatim ("On a high-deductible plan letter the supplement pays nothing until the policyholder's own payments for the calendar year reach the high deductible, and from that point it pays as the standard plan letter would") and gives the replacement ("…until the liability the policyholder's paid lines record over the twelve months to date reaches the tier's high deductible…"). The merged semantics are unique: after replacement there is exactly one basis for the high deductible — the recorded liability of paid lines over the twelve months to date — and `compute.counted_toward_deductible` implements that and nothing else. PASS on this one.

Base provisions **inherited in full and not weakened** (checked, no finding): the `policy_open_for_posting` and `payment_not_already_posted` eligibilities of `medigap_premium_billing_and_posting`; `original_line_on_record` and `adjustment_not_already_posted` of `medigap_claim_adjustment_and_recovery`; `policy_in_force_on_service_date` and `medicare_determination_on_record` of `medigap_benefit_payment`; `no_medicare_advantage_in_force` of `medigap_exclusivity_with_medicare_advantage`; the filing-window sentence ("A line more than the tier's filing window old is not reopened"), the assignment/excess-charge sentence, the benefit-not-in-plan sentence, the out-of-pocket-limit sentence and the pre-existing-condition sentence of `medigap_benefit_payment`; and the oldest-unpaid-period posting sentence of `medigap_premium_billing_and_posting`.

Three divergences were found. They are stated here once; what each costs a particular task is demonstrated in that task's file.

### factor_ladders

Structure only. Whether a factor bears weight is a fact about one world and lives in `0.md` / `1.md` under `factor_weight`.

| policy | factors | method | parameter | ladder tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| `medigap_ext_dual_coverage_premium_return` | 4 | 2 | 2 | 3,3,3,3 | `coverage_overlap_months` | `advantage` |
| `medigap_ext_premium_account_settlement` | 6 | 3 | 3 | 3,3,3,3,3,3 | `arrears_reach`, `payment_method_reduction` | — |
| `medigap_ext_uncovered_day_line_restatement` | 6 | 3 | 3 | 3,3,3,3,3,3 | `other_coverage_retention` | `advantage` |
| `medigap_ext_uncovered_day_direct_repayment` | 4 | 2 | 2 | 3,3,3,3 | `what_reached_her` | — |
| `medigap_ext_crossover_benefit_settlement` | 5 | 2 | 3 | 3,3,3,3,3 | `travel_deductible_taken`, `settled_line_selection` | — |

Every policy is inside the 4–6 bound with at least 2 `parameter` and at least 1 `method`; every ladder has exactly three pairwise-disjoint tiers with the fall-through counted. Within each policy the factors' `bindings` sets are **disjoint** (checked mechanically, no shared binding), every `decides` names an input binding and never `result`, and every `decides` is a member of its own factor's `bindings`.

Per task, over the task's own computations: component A carries 10 factors with `coverage_overlap_months` as its multi-source factor and its cross-difficulty factor (`advantage`); component B carries 15 factors with `other_coverage_retention` as a multi-source and the cross-difficulty factor (`advantage`). Both floors met.

Every tier of every ladder was checked against the policy's `rule`: each tier's condition and its value-or-method is a sentence of the prose, and each is a branch of the `decides` binding. **One ladder fails this in the compute direction — finding CG-5.** Every other ladder's three prose tiers map one-to-one onto three distinct compute branches, and the fall-through branch is textually the declared `baseline` expression.

Tier-outcome distinctness was checked mechanically by unparsing each `decides` binding into its branch expressions and comparing them pairwise. **24 of the 25 ladders have three pairwise-distinct outcome expressions. `retention_spread` has two identical ones — finding CG-5.**

Effect labels are honest with one borderline case recorded as an observation:

- `method` tiers that genuinely change the algorithm: `coverage_overlap_months` (which months are counted at all), `opening_month_valuation` (whole charge vs charge ÷ months of cover vs charged-since-start ÷ months in force), `age_rating_basis` (flat vs issue-age step vs attained-age increase), `current_period_valuation` (posted amount vs rate-built amount vs posted less returned), `arrears_reach` (which window), `outside_cover_span` (which comparison fixes the line set), `restated_liability_source` (recorded liability vs what the supplement paid), `retention_spread` (per line vs per claim), `what_reached_her`, `overpayment_measure` (whole payment vs excess over the supported share), `settled_line_selection` (which line, and whether liabilities are combined), `deductible_counting_basis` (which take-backs are netted). All genuine.
- `parameter` tiers that substitute a figure into a fixed formula: `returned_rate_components`, `money_already_given_back`, `credit_for_money_received`, `policy_fee_due_with_settlement`, `lines_restated_here`, `other_coverage_retention`, `already_taken_back_offset`, `recovered_elsewhere`, `balance_credited_to_her`, `settlement_base`, `covered_benefit_share`, `travel_deductible_taken`. All genuine.
- OBS-B (observation, no consequence): `payment_method_reduction` is labelled `parameter`, but its first tier computes `RND(rated_monthly_premium * P('annual_payment_discount_percent') / 100, 2)` — a proportion of the premium — while its second returns the flat constant `P('electronic_funds_transfer_discount')`. That is arguably a change of algorithm rather than of a number. It is recorded as an observation because reclassifying it to `method` leaves `medigap_ext_premium_account_settlement` at 4 `method` / 2 `parameter`, still inside every declared bound, so no count is violated and no scored value moves.

Every `method` tier names a computation rule the charter states: the three rating bases come from `medigap_premium_rating`'s own prose, the high-deductible basis from the declared `overwrite`, and the rest from the extended policy's own `rule`.

Every tier's condition was judged against what a Medicare Supplement line of business actually weighs for that quantity, and each part of each compound condition on its own. All 75 tier conditions are business-real (billing cadence, rating method, age at issue, payment channel, whether a settling payment stands in the year, whether the opening charge covered several months, whether a line crossed over automatically or was member-submitted, whether a Medicare determination is on the line, whether the benefit is foreign-travel or skilled-nursing, whether an adjustment already stands) and none holds of every customer who reaches its write. Every tier's outcome, the fall-throughs included, is a treatment such a plan would publish — **with one qualification recorded as OBS-C** and one recorded as OBS-D.

- OBS-C (observation): four of the five policies' whole-baseline fall-backs collapse to `$0.00` on any world, because their first-listed factor's baseline zeroes a multiplicand (`overlap_months: '0'`, `outside_cover_liability_span: '0.0'` / `restated_liability_measure: '0.0'`, `reached_the_policyholder: '0.0'`). Each is a faithful restatement of the policy's own standard method ("The standard method counts no month as run together", "The standard method finds no line outside cover", "The standard method treats nothing as having reached the policyholder") and each gives a *definite* number that differs from gold, so the letter of the baseline requirement is met. But a computation document whose baseline answer is "nothing is returned / nothing is restated / nothing is asked of her" gives a reader a degenerate rather than an informative wrong answer. Only `medigap_ext_crossover_benefit_settlement` has a non-degenerate baseline (it lands on a real figure). No consequence is demonstrable, so this is an observation.
- OBS-D (observation): `money_already_given_back`'s first tier reads "Where **a return** has already been paid on the policy's premium account, the amount already returned is deducted from this return", and `compute.already_returned_on_account` implements it as `SUM(..., event_type='medigap_premium_refund')` with no window and no reason filter. Rule and compute agree exactly, so this is not a check-2 failure. The business point is that an unrelated refund — a duplicate-payment return, say — is then netted against a rate-correction return, which is not what "Money the plan has already given back is never given back twice" is about. A reader who narrows the sentence to overlap-related returns computes a different figure. The sentence as written is unambiguous on its face, so this is recorded as an observation on tier realism rather than a red light; task 0's file records that its world does take this tier.

### findings

**CG-1 — undeclared override: the household discount is dropped. SOURCE-POLICY RED.**
*Symptom.* Two clauses of the merged charter fix the same quantity — the monthly premium a supplement settlement is built on — and reach different figures for a policyholder who holds a household discount.
*Root cause.* `medigap_ext_premium_account_settlement` lists `medigap_premium_rating` in `base_policy_refs` and declares `overwrite: []`, but its reduction ladder never produces the household discount.
*Evidence.* Base, `blueprint/products/medigap.yaml`, `medigap_premium_rating.rule`: "The household discount and the annual payment discount **stack: both are taken**, one after the other, on the premium after the rating factors and before the policy fee." Extended, `medigap.extended.yaml`, `medigap_ext_premium_account_settlement.rule`: "A reduction is then taken from the monthly premium for the way the policyholder pays. The standard method takes no reduction from that monthly premium. Where a payment covering twelve months of cover stands… the reduction is the tier's annual payment discount… Where no payment covering twelve months of cover stands… the reduction is the tier's flat electronic funds transfer reduction…" — an if/elif that yields **at most one** reduction and never the household one. `compute.monthly_premium_reduction` confirms it: the household branch does not exist. `medigap_policies.household_discount_applied` is a seeded enum whose values include `household_discount` and `household_and_annual_discount` (`blueprint/db_schema.json`), and `household_discount_percent` is a live tier parameter on every variant (5 on Plans A/B/K, 7 on D/N, 12 on G and High Deductible G).
*Demonstrated consequence.* Same situation — a Plan N policyholder with `household_discount_applied = 'household_and_annual_discount'` and a twelve-month payment on the account. Base: the 7 % household discount and the 4 % annual payment discount are both taken on the rated premium. Extended: only the 4 % annual payment discount is taken. On a rated monthly premium of 152.94 the two readings differ by 10.71 per month, and at a quarterly cadence by 32.13 on the settlement. This is the disguised form the check names a **dropped branch**: base declares a branch that extended's selector never produces.
*Affected artifact and location.* `env/env_0006_medicare_advantage_plan_sponsor/tasks/medicare_supplement_policy_desk/medigap.extended.yaml`, `medigap_ext_premium_account_settlement` — `overwrite` (empty), `rule` (the reduction paragraph), `compute.monthly_premium_reduction`, factor `payment_method_reduction`.
*Bears on.* Task 0 (component A). Task 0's file records why the consequence does not reach its scored value.
*Relation to previous revisions.* First revision; no prior audit exists for this difficulty.

**CG-2 — undeclared divergence: attained-age rating made simple rather than compounding. Observation.**
*Symptom.* Base and extended describe the attained-age premium differently for a policy in force two years or more.
*Root cause.* Same undeclared `overwrite: []` on `medigap_premium_rating`.
*Evidence.* Base: "on an attained-age tier it rises by the attained-age increase **at each policy anniversary**." Extended `compute.age_rated_monthly_premium`: `RND(P('base_monthly_premium_age_65') * (1 + P('attained_age_annual_increase_percent') / 100 * int(months_in_force / 12)), 2)` — simple, not compounded.
*Demonstrated consequence.* For Plan A (`base_monthly_premium_age_65` 112.4, `attained_age_annual_increase_percent` 3.4) in force three years, base's per-anniversary reading gives 112.4 × 1.034³ = 124.26 and extended gives 112.4 × (1 + 0.102) = 123.86 — a 0.40 gap. Recorded as an **observation** rather than a red light because "rises by the increase at each anniversary" does not unambiguously mandate compounding; the simple reading is a defensible reading of the same base sentence.
*Affected artifact and location.* As CG-1, `compute.age_rated_monthly_premium` and factor `age_rating_basis`.
*Bears on.* Neither task — both seeded policies are issue-age rated (Plan N and High Deductible Plan G both carry `rating_method: issue_age`).

**CG-3 — undeclared divergence: a restatement aggregated across lines. Observation.**
*Symptom.* Base fixes the granularity of a claim adjustment at one line per entry; the extended restatement computes one figure across every line that falls outside cover and books it with a single call.
*Root cause.* `medigap_ext_uncovered_day_line_restatement` lists `medigap_claim_adjustment_and_recovery` in `base_policy_refs` with `overwrite: []`, while its arithmetic is an aggregate.
*Evidence.* Base: "**Each line is adjusted on its own reference**: a Medicare claim covering several services is never adjusted as one, because the lines may be settled differently." Extended `compute`: `outside_cover_liability_span` sums `member_responsibility` across all outside-cover automatic-crossover lines, and `retention_applied` explicitly multiplies the retention by `auto_outside_cover_lines`, i.e. spreads one figure over several lines. The tool `book_precoverage_restatement_aba9484f` takes a single `source_claim_id` described as "the reference number of the **single** processed crossover line this restatement applies to" and its docstring says "One call restates **one named line**" — so one call carries the aggregate of several.
*Demonstrated consequence.* Recorded as an **observation**, not a red light, because on task 1's world — the only world in this difficulty where the policy fires — the two granularities converge exactly. Task 1's file gives the arithmetic that makes them converge and the seed rows that produce it.
*Affected artifact and location.* `medigap_ext_uncovered_day_line_restatement` — `overwrite`, `compute.outside_cover_liability_span`, `compute.retention_applied`; `task_tools.py`, `book_precoverage_restatement_aba9484f`.
*Bears on.* Task 1 (component B).

**CG-4 — rule/compute non-equivalence: "the credit standing from that overpayment" implemented as the whole payment. SOURCE-POLICY RED.**
*Symptom.* Two policies promise to set a *credit* against a figure and implement it as the *entire payment that produced the credit*.
*Root cause.* The `balance_effect='overpayment'` filter selects the ledger row, but the row's `amount` is the whole payment, not the excess over the period's balance. `medigap_premium_ledger` carries no separate excess field, so the compute has no binding for the quantity the rule names.
*Evidence.* `medigap_ext_dual_coverage_premium_return.rule`: "Where no return has yet been paid on the policy's premium account and a payment stands on it that exceeded the balance of the billing period it was applied to, **the credit standing from that overpayment** is deducted from this return." `compute.overpayment_credit_on_account`: `SUM('medigap_premium_ledger','amount', event_type='medigap_premium_payment', balance_effect='overpayment')`. The same pair recurs in `medigap_ext_premium_account_settlement`: rule "…the credit standing from that overpayment is credited together with the payments that settled a billing period in full", `compute.overpayment_credit_in_window`: `SUM(..., balance_effect='overpayment')`.
*Demonstrated consequence.* On task 0's own seed the two readings are far apart. Ledger row `c17fa1f4` is a payment of **480.00** with `balance_effect='overpayment'`, applied to billing period 2025-06 whose charges total 452.82 + 20.00 = **472.82**. The rule's "credit standing from that overpayment" is 480.00 − 472.82 = **7.18**; the compute yields **480.00**. In the situation the tier describes — no return yet paid on the account — the return would be reduced by 480.00 under the compute and by 7.18 under the rule, a gap of 472.82 on a return whose premium component is 152.61, i.e. the compute reading returns nothing at all while the rule reading returns 145.43. Two defensible answers.
*Affected artifact and location.* `medigap.extended.yaml`: `medigap_ext_dual_coverage_premium_return.compute.overpayment_credit_on_account` with `compute_basis.overpayment_credit_on_account`, factor `money_already_given_back` tier 2; `medigap_ext_premium_account_settlement.compute.overpayment_credit_in_window` with `compute_basis.overpayment_credit_in_window`, factor `credit_for_money_received` tier 2.
*Bears on.* Task 0 (component A), whose world contains the overpaying row. Task 0's file records why its scored value does not move.

**CG-5 — rule/compute non-equivalence: the retention ladder's fall-through is not the standard method, and two of its tiers are one tier written twice. SOURCE-POLICY RED.**
*Symptom.* A three-tier ladder is stated in the prose with three distinct outcomes and implemented with only two; the branch that answers the prose's "standard method" computes something the standard method says is not computed at all.
*Root cause.* The `else` branch of `retention_applied` was written as a copy of the first branch instead of as the baseline.
*Evidence.* `medigap_ext_uncovered_day_line_restatement.rule`: "What is left with the policyholder falls across the lines outside cover. **The standard method does not apply it at all.** Where more than one line falls outside cover and each was a visit of its own, what is left with the policyholder falls on each of those lines separately. Where the lines outside cover belong to one Medicare claim, what is left with the policyholder falls once on that claim." The declared factor baseline is `retention_applied: '0.0'`, and `baseline.rule` repeats "The standard method does not apply it at all." But `compute.retention_applied` is
`RND(retained_by_policyholder * auto_outside_cover_lines, 2) if (auto_outside_cover_lines > 1 and distinct_claims_outside_cover == auto_outside_cover_lines) else (RND(retained_by_policyholder * MX(1, distinct_claims_outside_cover), 2) if (auto_outside_cover_lines > 1 and distinct_claims_outside_cover < auto_outside_cover_lines) else RND(retained_by_policyholder * auto_outside_cover_lines, 2))`
— the first branch and the `else` branch are the **identical expression** `RND(retained_by_policyholder * auto_outside_cover_lines, 2)`. This is the only one of the difficulty's 25 ladders whose branch expressions are not pairwise distinct, and the only one whose `else` branch is not its declared `baseline`.
*Demonstrated consequence.* Take the situation the fall-through describes: exactly one automatic-crossover line falls outside cover, it was a visit of its own, and the retention is the Advantage tier's 40.00 specialist copay. The rule's standard method gives `retention_applied = 0.00`; the compute's `else` branch gives `RND(40.00 × 1, 2) = 40.00`. The restatement then differs by 40.00 between the two faces of the same policy. Separately, and independently of any world, the ladder's first tier and its fall-through select the same method, so one tier has been written as two.
*Affected artifact and location.* `medigap.extended.yaml`, `medigap_ext_uncovered_day_line_restatement` — `compute.retention_applied`, `compute_basis.retention_applied`, `baseline.rule`, factor `retention_spread` (`ladder` tier 3 and `baseline`).
*Bears on.* Task 1 (component B). Task 1's file records that its world takes tier 1 in both faces, so its scored value does not move.

**OBS-A** — tool docstrings promise a deductible-accumulator effect the code does not perform (see `action_binding_and_uuids`). Bears on task 1.
**OBS-B** — `payment_method_reduction` labelled `parameter` while its tiers arguably change the algorithm (see `factor_ladders`). Bears on task 0.
**OBS-C** — four of five baselines collapse to $0.00 (see `factor_ladders`). Bears on both tasks.
**OBS-D** — `money_already_given_back` nets any refund, including an unrelated one (see `factor_ladders`). Bears on task 0.
**OBS-E** — `medigap_exclusivity_with_medicare_advantage` states the plan's practice as "the supplement is dated to begin **the day** the Medicare Advantage coverage ends", while `medigap_ext_uncovered_day_line_restatement`'s first retention tier keys on the enrollment being "in force up to **the day before** this policy took effect" (`compute`: `days_between_other_coverage_and_cover == 1`). Task 1's seed follows the extended reading (coverage ends 2026-02-28, policy effective 2026-03-01) and task 0's follows neither (coverage ends 2025-06-30, policy effective 2025-06-01, a month of genuine overlap, which is what makes task 0's return policy fire at all). No scored value turns on the discrepancy in either task; recorded so that a rework does not read the base sentence as a constraint the seeds violate.
**OBS-F** — the two `owner=user` tools require arguments the customer cannot hold before acting: `remit_supplement_settlement_23b5df61.medigap_premium_entry_id` ("read from the entries on that policy's premium account") and `repay_direct_benefit_f162ba18`'s `source_claim_id`, `medicare_claim_number`, `date_of_service` and `liability_credited` are all plan-internal references or derived figures, and each persona undertakes to repeat back only "the figure you have just been given" / "exactly the amount you have been given". The hand-over therefore presupposes the representative dictating several row references to the customer. No second answer follows, so this is an observation.

## closing_checklist

Written **after** both tasks' reveals, and therefore below the charter-global section, which remains pre-reveal by construction and was not edited after the reveal.

**Audit files.** `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`; `_difficulty.md` sits alongside them in `env/env_0006_medicare_advantage_plan_sponsor/audits/policy_task/medicare_supplement_policy_desk/`. This is revision 1 — no prior revision exists, so nothing has been overwritten; any re-audit must append under `## revision_2` and leave this text untouched. Both `source_gt_comparison` sections carry a PASS on all four relationships.

**Coverage, scopes and closure.** The five extended policies are fully covered by the two tasks and the two `charter_scope` blocks are pairwise disjoint and jointly complete — task 0 claims `{medigap_ext_dual_coverage_premium_return, medigap_ext_premium_account_settlement}`, task 1 claims `{medigap_ext_uncovered_day_line_restatement, medigap_ext_uncovered_day_direct_repayment, medigap_ext_crossover_benefit_settlement}`, and each scope spans that task's whole problem tree, root and prerequisites together. The five task tools partition the same way. Task tools and GT are closed: every tool a task's `evaluation_criteria` calls is in its `charter_scope`, and every policy in scope produces exactly one write. Each `uuid8` — `c83152d2`, `23b5df61`, `aba9484f`, `f162ba18`, `9f3dc765` — is independently generated, frozen with its tool, unreused and not batch-derived.

**Problem trees.** Task 0: one prerequisite problem, one `value_input` edge (floor max(n−1,1) = 1), one problem resolved by an `owner=user` tool (`remit_supplement_settlement_23b5df61`), no cycle. Task 1: two prerequisite problems, two `value_input` edges (floor 1), one problem resolved by an `owner=user` tool (`repay_direct_benefit_f162ba18`), no cycle. Every edge was shown to bear weight by an independent skip-and-replay run: 675.64 → 530.21 on task 0; 802.00 → 668.00 and 7 170.00 → 6 658.00 on task 1. The `prerequisite` edges of the whole difficulty together form a directed acyclic graph — two disjoint chains, 2→1 and 5→4→3 — and no cross-task reference creates a cycle.

**Computations and factors.** Five computations, each with a self-sufficient `baseline` whose sentences are all in its `rule`, whose default keys match `baseline.params`, and which yields a definite number differing from gold on its own world (0.00, 0.00, 0.00, 0.00 and 9 400.00 respectively — see OBS-C on the four degenerate ones). Twenty-five declared factors, four to six per computation, at least two `parameter` and one `method` each; every ladder has three pairwise-disjoint tiers stated in full in its own `rule`; each task carries at least one multi-source factor and at least one cross-difficulty factor reading seeded `advantage` rows. **All twenty-five were proved to bear weight** against an honest baseline by the auditor's own substitution-and-recompute runs, and every one of the twenty-five `baseline_result` figures and `tier_taken` strings matched `computations[].factor_sensitivity` value for value. Two exceptions to "tiers distinct in outcome" and "every tier implemented in compute" are recorded as CG-5.

**Gates re-run on the final form** (from the repository root, 2026-09-21):

```
check_extended     EXTENDED OK            (extended_policies=5, cross-cat=2, task_tools=5, tasks=2)
check_task_tools   TASK TOOL CONTRACT OK  (5 tools)
replay_tasks       REPLAY OK              (0.json 10 acts, 1.json 12 acts; det, nonvac, 0 errs, closures match)
check_solvability  SOLVABILITY OK
check_compute      COMPUTE OK             (branches=41.00, steps=11.00, history_rows_max=26, branches_max=51)
check_grounding    GROUNDING OK
check_cross_fire   SCOPE OK               (2 tasks, policies=5, hard-fails=0)
```

Identical to the snapshot supplied with the brief. `check_traceability` remains out of scope until the render step publishes the KB; `check_cache_diff` is informational.

**Difficulty verdict.** Policy self-consistency **RED at the charter level** (CG-1, CG-4, CG-5), **PASS for each of the two tasks** — every charter-global red light was shown, on that task's own world and scored solution, not to give it a second defensible answer, and in two cases (CG-4, CG-5) the margin is a single seeded row. Problem tree holds **PASS** for both tasks. Factors bear weight **PASS** for both tasks, 25 of 25. Unique solution **PASS** for both tasks.

Because the four relationships must hold together, this difficulty **does not yet pass the source-layer audit**: the three charter-global `SOURCE-POLICY RED` findings stand against `medigap.extended.yaml` and are reported for rework. No artifact was edited by this audit, and no fix is designed here.

---

# revision_2

Re-audit round 2. **Revision 1 above is unedited.** This round is not blind: I have already seen this difficulty's GT, so nothing below is presented as an independent blind derivation. The question this round answers is narrower and different — whether each round-1 RED is genuinely closed rather than reworded, whether the rework introduced any new defect, and whether anything that passed in round 1 has regressed.

## charter_global_frozen (revision 2)

| item | round 1 | round 2 | treatment |
| --- | --- | --- | --- |
| `medigap.extended.yaml` | `ff66c1f9a56e6aa9` | **`9b11c3e10388e3a6`** | **CHANGED → charter-global section re-derived in full** |
| `task_tools.py` | `11d4619938c51ac9` | `11d4619938c51ac9` | unchanged |
| `_masked_views/0.masked.json` | `24f623ed4dfca1fe` | `24f623ed4dfca1fe` | unchanged (byte-identical world) |
| `_masked_views/1.masked.json` | `ed75098b8a5f6c96` | `ed75098b8a5f6c96` | unchanged (byte-identical world) |
| `tasks/0.json` | — | `eccd03eaa560b98b` | changed |
| `tasks/1.json` | — | `821b8ec129c3aac6` | changed |

All six re-verified on disk against the brief; all six match. Re-audit time 2026-09-21T14:41Z.

**Carry-forward rule applied.** The charter moved, so every charter-global section that reads it — `policy_conflict_scan`, `rule_compute_equivalence`, `prerequisite_graph`, `prerequisite_sentences`, `override_declarations`, `factor_ladders` — is re-derived below rather than carried. `action_binding_and_uuids` reads the charter's `target_tool`/`computes` pairs **and** `task_tools.py`; the tool module is unchanged by hash and the five `(target_tool, computes)` pairs are unchanged, so that section's tool-side conclusions (uuid8 independence, docstring silence about sequence, no tool judging a prerequisite, OBS-A) are **carried forward by reference on the hash `11d4619938c51ac9`**, and only its charter-side half was re-checked (unchanged: five policies, five distinct pairs).

The reworker's claims were read as a list of item ids only and were not used as evidence; every conclusion below is from the artifacts.

## re-derived charter-global scan (revision 2)

**Base section** re-diffed key by key against `blueprint/products/medigap.yaml`: still **verbatim identical** on all ten base keys, with `extended_policies` the only addition. The base copy has not been rewritten.

**Shape unchanged**: five extended policies, same ids, same `trigger`/`subject`/`computes`/`target_tool`, factor counts 4/6/6/4/5, prerequisites 0/1/0/1/1, one declared `overwrite` (on `medigap_ext_crossover_benefit_settlement`, unchanged and still well formed). Cross-category declarations unchanged: `advantage` `['coverage_end_date']` on policy 1 and `['coverage_end_date','specialist_copay']` on policy 3.

**`rule_compute_equivalence` re-run** over all five policies: every `compute` binding has a `compute_basis` entry, every `compute_basis` sentence is verbatim in that policy's own `rule`, and no `compute_basis` names a binding that no longer exists (22 bindings on policy 2 alone, all clean). Both round-1 exceptions are gone — see CG-4 and CG-5 below. **No new exception was found.**

**`prerequisite_graph` and `prerequisite_sentences` re-run**: the three edges are unchanged in every field (`problem`, `kind: value_input`, `form: state`, `gate`, `condition`, `resolved_by`), each `policy_source` is still verbatim locatable in the blocked policy's own `rule` and still absent from the depended-on rule, each `gate` is still a live binding of the blocked policy's compute, and the graph is still two disjoint acyclic chains. The rework did not disturb any prerequisite sentence. An ordering-cue sweep over the five reworked rules again found every hit intra-computational; **no new cross-problem order was introduced** — in particular the new household sentences ("That monthly premium is **then** multiplied…", "A reduction is **then** taken…") are ordinary calculation sequencing inside one policy.

**Lead 1 tested and does not apply here.** I checked cross-category reads at **field** level, not category level, by extracting every `CFIELD`/`CPARAM`/`X*` call from all five computes and comparing the field sets against each policy's declared `reads`:

| policy | category | declared `reads` | fields actually read | verdict |
| --- | --- | --- | --- | --- |
| `medigap_ext_dual_coverage_premium_return` | advantage | `coverage_end_date` | `coverage_end_date` | exact |
| `medigap_ext_uncovered_day_line_restatement` | advantage | `coverage_end_date`, `specialist_copay` | `coverage_end_date`, `specialist_copay` | exact |

No undeclared field is read and no declared field goes unread. The gap the lead describes is real in the gate but this difficulty does not exhibit it, before or after the rework.

**Lead 2 tested across all five policies.** I swept for declarations left behind by the fix — `compute_basis` pointing at a renamed or deleted binding, `baseline.rule` sentences no longer in the `rule`, `baseline.params` out of step with the baseline's `P()` keys, factor `bindings`/`decides` naming a binding that no longer exists, ladder tiers not tracking a changed rule sentence, and `prerequisite.gate` orphaned. **The sweep is clean**, and the two places most at risk were carried through correctly:

- `medigap_ext_premium_account_settlement.baseline.params` gained `household_discount_percent` (now `['base_monthly_premium_age_65','area_rate_factor','tobacco_rate_factor','household_discount_percent','policy_fee_annual']`) and `baseline.rule` gained the household sentence, so the baseline remains a complete standard method whose default keys are the ones it names. This is exactly the trap the lead describes and it was avoided.
- The five ladders whose prose the fixes touched all track the new wording: `payment_method_reduction` tier 1 now reads "taken on **the monthly premium the household discount leaves**", `current_period_valuation` tier 1 now reads "valued at **the monthly premium the household discount leaves**, less the reduction", `credit_for_money_received` tier 2 and `money_already_given_back` tier 2 both carry the renamed quantity, and all three `retention_spread` tiers carry their new text.

One imprecision was surfaced by running the tier check byte-wise this round, and it is **pre-existing, not a regression** — see OBS-G.

## findings (revision 2)

### CG-1 — **CLOSED**

Closed by restoring the dropped branch, not by declaring an override, and on this evidence that is the right call: base's clause is something the settlement policy should *produce*, so `overwrite: []` is now true rather than false.

The rule now carries a household step between the rating factors and the payment reduction, and a sentence fixing how the two compose: "Where the plan holds the policy as taking the household discount, the tier's household discount is then taken from that monthly premium; where it does not, the monthly premium stands as rated." and "A reduction is then taken for the way the policyholder pays **from the monthly premium the household discount leaves**, so that the household discount and the reduction for the way they pay are taken **one after the other and are never combined into a single rate**." The preceding sentence was amended from "before any reduction is taken" to "before any **discount** is taken". A new binding implements it:

```
household_adjusted_monthly_premium = RND(rated_monthly_premium * (100 - P('household_discount_percent')) / 100, 2)
    if (F('household_discount_applied') == 'household_discount'
        or F('household_discount_applied') == 'household_and_annual_discount')
    else rated_monthly_premium
```

Checked against base `medigap_premium_rating`: "The household discount and the annual payment discount **stack: both are taken, one after the other, on the premium after the rating factors and before the policy fee**." Extended now takes the household discount **after** `rated_monthly_premium` (which is where the area and tobacco factors are applied) and **before** `fee_instalment` is added, and takes the annual payment discount on what the household discount leaves. Ordering and composition both match the base sentence. The base clause is produced, not superseded.

**Reachability, ordering and composition verified independently of the seed.** Driving `household_discount_applied` through all four schema enum values on task 0's world:

| `household_discount_applied` | `rated` | `household_adjusted` | reduction | settlement |
| --- | --- | --- | --- | --- |
| `none` | 152.94 | 152.94 | 2.00 | **530.21** |
| `household_discount` | 152.94 | **142.23** | 2.00 | 498.08 |
| `household_and_annual_discount` | 152.94 | **142.23** | 2.00 | 498.08 |
| `annual_payment_discount` | 152.94 | 152.94 | 2.00 | **530.21** |

The branch is genuinely reachable (two of four enum values fire it, and `142.23 = RND(152.94 × 93/100, 2)` is the tier's 7 % household discount for Plan N), and it correctly does **not** fire on `annual_payment_discount`, which names a different discount. The "never combined into a single rate" sentence is load-bearing rather than decorative: where both apply, taking them one after the other gives `142.23 − RND(142.23 × 4/100, 2) = 136.54`, while combining them into one 11 % rate would give `152.94 × 0.89 = 136.12` — a 0.42 difference the sentence rules out.

**No figure round 1 verified was moved**: task 0's seed carries `household_discount_applied = "none"`, the branch falls to `rated_monthly_premium`, and the settlement stays 530.21 with all six factor `baseline_result` figures unchanged (verified below).

One consequence worth recording rather than objecting to: the household discount is now a **baseline step**, not a declared factor. That is the only structurally available choice — policy 2 already carries six factors, the maximum — and it is faithful to base, which treats the household discount as part of the standard build rather than as a tiered variation. `baseline.params` and `baseline.rule` were both updated to match, so the baseline still computes a definite number with no factor applied.

### CG-4 — **CLOSED**

Closed by renaming the quantity in both rules to one the ledger actually carries. `medigap_premium_ledger` holds no excess-over-balance field, so "the credit standing from that overpayment" was a quantity no record could supply; both rules now name an account-level difference instead, and both computes implement exactly that difference.

| | policy 1 | policy 2 |
| --- | --- | --- |
| rule now says | "…**the money received on it exceeds the premium charged on it**, **the amount by which the money received exceeds the premium charged** is deducted from this return." | "…**the money received within that span exceeds the charges posted within it**, the payments that settled a billing period in full are credited together with **the amount by which the money received within the span exceeds the charges posted within it**." |
| compute now is | `MX(0.0, RND(SUM(payments) − SUM(charges), 2))` | `MX(0.0, RND(SUM(payments within window) − arrears_charges, 2))` |
| `compute_basis` | the same sentence, verbatim | the same sentence, verbatim |
| ladder tier 2 | "the amount by which the money received exceeds the premium charged" | "…together with the amount by which the money received within the span exceeds the charges posted within it" |

Rule, `compute_basis`, ladder and compute now name one quantity, and that quantity is a difference of two sums the ledger really holds (`amount` filtered by `event_type`), with no invented field.

**Verified in the exact region where the round-1 defect lived, not merely on the seed.** The round-1 finding was that the seeded refund `586aaae6` masked the defect by making tier 1 fire. I built the probe world that removes that refund and raises the June-2025 payment from 480.00 to 700.00, so tier 2 must fire:

- money received across the account = 2 308.46; premium charged = 2 304.10; **the rule's quantity = 4.36**
- the reworked compute returns `overpayment_credit_on_account = 4.36`, `return_offset = **4.36**` — agreeing with the rule
- the **round-1** compute (`SUM(amount, balance_effect='overpayment')`) would have returned **700.00** on the same world

So the fix changes behaviour precisely where the defect was and lands on the rule's figure. The correspondence is now exact over the whole domain rather than on this seed: `MX(0.0, payments − charges)` is positive exactly when the rule's condition "the money received exceeds the premium charged" is true and equals the amount the rule names; when the condition is false the guard `> 0` fails and the ladder falls through to the rule's "nothing is deducted". There is no world in which the two faces diverge.

A naming remnant, recorded and not charged: the binding is still called `overpayment_credit_on_account` / `overpayment_credit_in_window` although it now measures an account-level surplus rather than a flagged overpayment. Binding names are not normative and the `compute_basis` is correct, so this is cosmetic.

### CG-5 — **CLOSED**, and the same-class lesser note with it

The fall-through was set to the factor's declared baseline and the middle tier's guard widened:

```
retention_applied = RND(retained * auto_outside_cover_lines, 2)  if (auto_outside_cover_lines > 1 and distinct_claims_outside_cover == auto_outside_cover_lines)
               else RND(retained * MX(1, distinct_claims_outside_cover), 2) if auto_outside_cover_lines > 0
               else 0.0
```

The `else` branch is now `0.0`, which **is** the factor's declared `baseline` (`retention_applied: '0.0'`), and the rule's fall-through sentence was amended to explain the guard: "The standard method does not apply it at all, **no line falling outside cover**." The middle tier's prose was widened to match: "Where lines fall outside cover and belong to one Medicare claim, what is left with the policyholder falls once on **each such claim**."

The round-1 defect had two halves and both are gone: the three branch expressions are now pairwise distinct, and the fall-through is the declared baseline. Re-running the mechanical distinctness check across **all 25 ladders** of the difficulty: **0 failures** — every ladder has exactly three branches, no two branch expressions coincide, and every fall-through branch is textually its declared `baseline`.

**Verified over the whole (lines, claims) domain, not on the seed.** Evaluating the rule's three prose tiers and the reworked compute at every reachable combination with `retained = 40.00`:

| lines | claims | rule | compute | agree |
| --- | --- | --- | --- | --- |
| 0 | 0 | 0.00 | 0.00 | yes |
| 1 | 1 | 40.00 | 40.00 | yes |
| 2 | 1 | 40.00 | 40.00 | yes |
| 2 | 2 | 80.00 | 80.00 | yes |
| 3 | 1 | 40.00 | 40.00 | yes |
| 3 | 2 | 80.00 | 80.00 | yes |
| 3 | 3 | 120.00 | 120.00 | yes |
| 4 | 1…4 | 40 / 80 / 120 / 160 | same | yes |

Zero disagreements, and five distinct outcomes are reachable. **Widening the guard did not strand the tier above it**: tier 1 is tested first and still fires on its own region (lines > 1 with claims equal to lines).

**A correction to my own round-1 report, made rather than left standing.** Revision 1 demonstrated CG-5 partly by asserting that with one line outside cover "the rule's standard method gives 0.00 while the compute's `else` branch gives 40.00". That half was weaker than I stated: the round-1 **rule** prose for the middle tier read "Where the lines outside cover belong to one Medicare claim, what is left with the policyholder falls once on that claim", with no "more than one line" qualifier, so a careful reader would already have routed the one-line case through that tier to 40.00 and agreed with the compute. The column "compute r1" in the table above confirms it — the round-1 compute agrees with the rule at every grid point. **The structural half of CG-5 stands unaffected and was the real defect**: the ladder's first branch and its `else` branch were the identical expression, and the `else` branch was not the factor's declared `baseline`, so "every factor's fall-through tier is that baseline" failed on the artifact's own terms. That half is now closed. I record the correction because a red light turns on whether an assertion is true, and one of mine was overstated.

**The lesser note is closed too.** `outside_cover_liability_span`'s first guard was tightened from `F('policy_end_date') == ''` to `F('policy_end_date') == '' and auto_paid_liability_all > auto_paid_liability_in_cover`, which makes the previously unreachable trailing `else 0.0` reachable:

| situation | result | |
| --- | --- | --- |
| in force, some liability outside cover | 996.00 | tier 1 |
| in force, **no** liability outside cover | **0.00** | the branch that was dead in round 1 |
| ended and put back in force | 448.00 | tier 2 |

The fall-through is the declared `baseline` (`'0.0'`) and matches the rule's "The standard method finds no line outside cover, the policy having been in force for every day its paid lines fall on."

### New observation introduced by the CG-5 fix

**OBS-H — `retention_spread`'s first tier is now behaviourally redundant. Observation.**
*Symptom.* Widening the middle tier's guard from `lines > 1 and claims < lines` to `lines > 0` made it subsume the first tier's region with an identical value.
*Evidence.* Where tier 1 fires, `claims == lines`, so tier 2's formula `RND(retained × MX(1, claims), 2)` equals tier 1's `RND(retained × lines, 2)`. Deleting tier 1 outright and re-evaluating every grid point above changes **no outcome anywhere** (verified over the full domain).
*Why it is an observation and not a repeat of CG-5.* The two are different in kind. CG-5 was a rule/compute non-equivalence — the `else` branch contradicted the declared baseline and the prose's standard method. Here the fall-through is correct, the three outcomes are distinct across the domain, and the two prose tiers state genuinely different treatments: "falls on each of those lines separately" is per line and "falls once on each such claim" is per claim. They coincide only when lines and claims stand in bijection, which is a fact about the world rather than a duplication in the drafting, and both sentences are ones a plan would publish. What can be demonstrated is only that the first tier never changes an outcome, which is weaker than "one tier written as two". Recorded so a rework can decide whether the first tier earns its place.
*Bears on.* Task 1, where lines = 2 and claims = 2 put the customer on tier 1; tier 2 would give the same 80.00, so the scored 766.00 is unaffected either way.

### Carried forward from revision 1, re-checked against the reworked charter

| item | status in round 2 |
| --- | --- |
| **CG-2** (attained-age made simple rather than compounding, undeclared) | **still present** — `age_rated_monthly_premium`'s attained-age branch is unchanged. Still an observation; still bears on neither task, both being issue-age rated. |
| **CG-3** (restatement aggregated across lines against base's "Each line is adjusted on its own reference") | **still present** — `outside_cover_liability_span` and `retention_applied` still aggregate, and the tool still takes one `source_claim_id`. Still an observation; still converges on task 1's world. |
| **OBS-A** (tools promise a deductible-accumulator effect they never write) | **still present** — `task_tools.py` is unchanged by hash. |
| **OBS-B** (`payment_method_reduction` labelled `parameter` while its tiers arguably change the algorithm) | **still present**, and unchanged in substance: tier 1 is now a proportion of the household-adjusted premium, tier 2 still a flat constant. |
| **OBS-C** (four of five baselines collapse to $0.00) | **still present** — the five whole-baseline fall-backs are still 0.00 / 0.00 / 0.00 / 0.00 / 9 400.00. Adding the household step to policy 2's baseline did not change its degenerate value on task 0. |
| **OBS-D** (`money_already_given_back` tier 1 nets any refund, including an unrelated one) | **still present** — tier 1's wording is unchanged; only tier 2 was reworked. |
| **OBS-E** (base exclusivity says "the day" MA coverage ends, extended keys on "the day before") | **still present**, unchanged. |
| **OBS-F** (`owner=user` tools need arguments the customer cannot hold) | **still present** — `task_tools.py` unchanged. |

**OBS-G — a task-file `tier_taken` string is a truncated paraphrase of its ladder tier. Pre-existing observation, not a regression.**
Running the tier check byte-wise this round (revision 1 matched them semantically) surfaced one mismatch out of 25: `tasks/0.json`, `computations[1].factor_sensitivity`, `payment_method_reduction` records `tier_taken` as "the premium is drawn by bank transfer and at least two payments that settled a billing period in full stand within the twelve months to date", dropping the ladder tier's leading conjunct "no payment covering twelve months of cover stands on the account". **This string is byte-identical to the one round 1's GT carried**, so the rework did not introduce it and nothing regressed. No consequence: it is still unambiguously tier 2, the only tier mentioning bank transfer, and the recorded `baseline_result` 536.21 is correct for it. Recorded for completeness and explicitly not charged against the rework.

## closing_checklist (revision 2)

**Regression check — the main risk this round, since every per-task relationship passed in round 1.** I re-ran my own independent evaluation of all five computations on the two byte-identical worlds and compared every figure against the ones revision 1 verified:

- **5 of 5 gold values unchanged**: 145.43, 530.21, 766.00, 668.00, 6 658.00.
- **25 of 25 factor `baseline_result` figures unchanged**, and every one of the 25 factors still **bears weight** (no substitution reproduced its policy's gold value).
- **5 of 5 whole-baseline fall-backs unchanged**: 0.00, 0.00, 0.00, 0.00, 9 400.00.
- **Total deviations from round 1: 0.**
- **Both problem trees unchanged**: same roots, same edges, same `kind`/`gate`/`form`, same `resolution_order`; and every load-bearing figure in both `prerequisite_closure` blocks (675.64; 802.00, 2 144.00, 726.00, 7 170.00, 7 896.00, 1 632.00, 1 238.00) still present and still matching my own runs.
- **All 16 scored tool arguments byte-identical to round 1** across both tasks, including owners and order.
- **Scopes unchanged and still pairwise disjoint and jointly complete**; the five `(target_tool, computes)` pairs and the five uuid8s are unchanged.

**Gates re-run by me on the reworked form** (not taken from the brief):

```
check_extended     EXTENDED OK            (extended_policies=5, cross-cat=2, task_tools=5, tasks=2)
check_task_tools   TASK TOOL CONTRACT OK  (5 tools)
replay_tasks       REPLAY OK              (0.json 10 acts, 1.json 12 acts; det, nonvac, 0 errs, closures 17/17 and 13/13 match)
check_solvability  SOLVABILITY OK
check_compute      COMPUTE OK             (branches=42.50, steps=11.00, history_rows_max=26, branches_max=51)
check_grounding    GROUNDING OK
check_cross_fire   SCOPE OK               (2 tasks, policies=5, hard-fails=0)
```

Matching the brief's snapshot. The one gate figure that moved — suite mean branches 41.00 → 42.50 — is accounted for exactly by the single branching binding CG-1's fix added to policy 2, which corroborates that the restored household branch is a real branch rather than prose. `check_traceability` remains deferred to the render step.

**Difficulty verdict, revision 2.** All three round-1 `SOURCE-POLICY RED` findings are **genuinely closed**, each verified in the region of its own domain where the defect lived rather than on the seed that masked it, and the same-class lesser note with them. The rework introduced **no new red light**; it introduced one observation (OBS-H) and left a cosmetic naming remnant. Nothing regressed: every figure, tree, argument, owner, order and scope that revision 1 verified is unchanged.

Policy self-consistency **PASS** at the charter level and for both tasks. Problem tree holds **PASS** for both tasks. Factors bear weight **PASS** for both tasks, 25 of 25. Unique solution **PASS** for both tasks.

**This difficulty now passes the source-layer audit.** Eight observations stand (CG-2, CG-3, OBS-A through OBS-H), none of which carries a demonstrated consequence for either task's scored solution, and none of which is grounds for rework. No artifact was edited by this audit and no fix was designed here.

## provenance addendum (revision 2) — the task files moved during this audit

Recorded because it is a fact about the evidence this audit rests on, and the hash table at the top of `revision_2` records the brief's values, which are no longer what is on disk.

**What happened.** At the start of this round I re-verified all six hashes against the brief and all six matched, including `tasks/0.json = eccd03eaa560b98b` and `tasks/1.json = 821b8ec129c3aac6`. On the closing boundary check the same two files hashed **`4a19852b8a51e6b3`** and **`70b8beb5fae23e5c`**. Their mtime is **2026-09-21 14:33:23 UTC**, i.e. after the brief was issued and while this audit was in progress. `medigap.extended.yaml` (mtime 14:23:11) hashed `9b11c3e10388e3a6` at the start of the round and still does, so the charter was stable throughout; `task_tools.py` (mtime 13:25:26) is untouched. I did not write to `tasks/` — my write domain is the audit directory alone, and `git status` over `blueprint/`, `tasks/`, `skills/` and `erlbench/` shows no modification attributable to this session.

**What I did about it.** I re-ran the whole task-file comparison against the **current** bytes rather than reporting on the superseded ones. The result is that the rewrite is **non-material to every conclusion in `revision_2`**:

| checked against the current `tasks/*.json` | result |
| --- | --- |
| `computations[].expected` | 145.43, 530.21 / 766.0, 668.0, 6658.0 — unchanged |
| `computations[].baseline_result` | 0.0, 0.0 / 0.0, 0.0, 9400.0 — unchanged |
| all 25 `factor_sensitivity` `baseline_result` figures | unchanged |
| all 16 scored tool arguments across the five writes | byte-identical to round 1 |
| `charter_scope` on both tasks | unchanged and still disjoint |
| `prerequisite_closure.resolution_order` on both tasks | unchanged |
| step owners on both tasks | unchanged (one `user` write per task, in the same position) |
| OBS-G's `tier_taken` string | unchanged |
| **material differences** | **0** |

**The critical check — the worlds did not move.** I reconstructed each masked view from the current task files and compared field by field: `frozen_time`, `user_scenario` and `initial_state` in `tasks/0.json` and `tasks/1.json` are **identical** to `_masked_views/0.masked.json` and `1.masked.json`, which still hash to `24f623ed4dfca1fe` and `ed75098b8a5f6c96`. The masked views are therefore not stale, and every world-based figure in `revision_2` — the five gold values, the 25 factor substitutions, the load-bearing runs, the CG-1/CG-4/CG-5 probes — was computed on the world the current task files still carry.

**Conclusion.** The 14:33 rewrite touched only non-scored prose (the `design_rationale`, `objective`/`necessity` and `argument_uniqueness_tracing` narration are the only fields left once the invariants above are held fixed). `revision_2`'s verdicts stand on the current artifacts. The coordinator should note that the brief's `tasks/*.json` hashes are superseded by `4a19852b8a51e6b3` and `70b8beb5fae23e5c`, and that a fourth artifact moving mid-audit is worth tracing to whichever process wrote it, since an audit that had *not* re-checked would have signed off on bytes that no longer existed.

**Update — the rewriting is ongoing, not a one-off.** On a further check `tasks/0.json` and `tasks/1.json` had changed a **third** time, to `6207640fd7958af7` and `b8f921d7cce23f42`, mtime **14:39:09 UTC**. Three distinct hashes for `tasks/0.json` were observed inside this one audit:

| observed at | `tasks/0.json` | `tasks/1.json` |
| --- | --- | --- |
| round-2 brief / audit start | `eccd03eaa560b98b` | `821b8ec129c3aac6` |
| 14:33:23 | `4a19852b8a51e6b3` | `70b8beb5fae23e5c` |
| 14:39:09 | `6207640fd7958af7` | `b8f921d7cce23f42` |

`medigap.extended.yaml` (`9b11c3e10388e3a6`) and `task_tools.py` (`11d4619938c51ac9`) held steady across all three observations, so whatever is writing is touching the task files only.

I re-checked the invariants against the 14:39 revision as well. **Zero material differences again**: both worlds still byte-identical to their masked views; `expected` still 145.43 / 530.21 and 766.0 / 668.0 / 6658.0; all five `baseline_result` values and all 25 `factor_sensitivity` figures unchanged; the five scored write amounts unchanged; one `owner=user` write per task. All seven gates re-run green on these bytes.

**What this does and does not license.** The verdicts in `revision_2` rest on the charter, the tool module and the two worlds, all three of which were stable throughout and are pinned by hashes that have not moved. Those verdicts stand. What cannot be asserted is a hash-pinned sign-off on `tasks/*.json`: any statement of the form "task file X, hash H, is audited" has a shelf life of minutes here. A consumer of this report should re-check the two task-file hashes before relying on them, and the coordinator should trace which process is rewriting them — a re-audit that verified once at the top and signed off at the bottom would have certified bytes that no longer existed, which is precisely the failure this addendum exists to prevent.
