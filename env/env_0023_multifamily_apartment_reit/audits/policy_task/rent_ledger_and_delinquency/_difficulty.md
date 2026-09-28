# Policy-task audit — rent_ledger_and_delinquency / charter-global

## charter_global_frozen

- Frozen: 2026-09-24T18:06Z, round 1, auditor: independent policy-task audit agent (not an author of these artifacts).
- Inputs and hashes:
  - `tasks/rent_ledger_and_delinquency/lease.extended.yaml` sha256 `e9eb3a3f4cb21d091a0f0545c5f3455995439bd8eeb8644ecd3722c0f709e7ee` (read in full)
  - `tasks/rent_ledger_and_delinquency/task_tools.py` sha256 `d4cc8e875d2d890240aa9f168e8dc1c0e5b79438ce76d5057ad98d3ac00c8085` (read in full)
  - `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/lease.yaml` (base copy compared)
  - The DSL used by `compute` is taken from `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`, `MONTHS`, `DAYS`, `within_months` = `0 <= MONTHS(date, NOW) < N`).
- Fields permitted: the above, plus each task's `frozen_time`, `user_scenario` and `initial_state` read only from the coordinator's masked views (`r1/0.json` sha256 `9f2f6718…bcae8`, `r1/1.json` sha256 `ba56c474…b8657`).
- Fields masked (not read before this file and both task derivations were frozen): `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`. No other audit directory, worklog or scratchpad file was read.
- Entry conditions (Step 0): the brief supplied the gate snapshot. check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and check_cross_fire all returned rc=0. check_traceability is deferred to the render stage. The masked views came with hashes, and the recomputed hashes matched. The replay excerpt shows only the `1.json` line. That is a formatting gap in the brief, not a failed gate, and it is recorded here as an observation. Entry conditions: met.
- Nothing in this file comes from a revealed GT. Everything below comes from the charter, the schema and the tool contracts. It was written after both per-task derivations were computed but before either task JSON was opened.

### policy_conflict_scan

The base section is a verbatim copy of `blueprint/products/lease.yaml`. `diff <(head -1583 lease.extended.yaml) products/lease.yaml` reports only one trailing blank line.

The five extended policies, each with its subject, target tool and trigger:

| id | subject | target_tool (owner) | trigger | prerequisite |
|---|---|---|---|---|
| A `lease_ext_employer_discount_credit` | lease_charge_credit (preferred_employer_discount) | `post_employer_discount_credit_34aaf7ea` (agent) | state_due | [] |
| B `lease_ext_rent_catch_up_payment` | lease_payment | `make_rent_catch_up_payment_381e22a2` (user) | on_request | A (value_input, gate `rent_credits`) |
| C `lease_ext_courtesy_waiver_amount` | lease_charge_credit (late_fee_waiver) | `grant_courtesy_late_fee_waiver_1c994f24` (agent) | on_request | B (value_input, gate `last_pay`) |
| D `lease_ext_late_fee_review_reversal` | lease_charge_credit (charge_reversal) | `post_late_fee_review_reversal_dc9bc174` (agent) | state_due | [] |
| E `lease_ext_payment_plan_terms` | lease_payment (plan signature) | `sign_payment_plan_b63c5de9` (user) | on_request | D (value_input, gate `balance`) |

- **Overlapping subjects.** A, C and D all write `lease_charge_credit`, but each writes a different `charge_code` and a different `source_charge_id` (A uses the base rent line; C and D both use the initial late fee line). C (late_fee_waiver) and D (charge_reversal) can both land on the same initial late fee line. The base `waive_once` dedup ("A charge is waived or reversed at most once.", duplicate_filters `[late_fee_waiver, charge_reversal]`) would then block the second write. The two policies never meet in one tree here: C belongs to the A→B→C tree and D to the D→E tree. In each task world the other policy either has nothing to write (D on task 0 computes a 0.00 reversal, see `0.md`) or is on_request and was not requested (C on task 1). The collision is latent and recorded as observation O-6.
- **Triggers and time anchors.** Every policy is evaluated at the handling date, NOW = frozen date. Every "last N months" is anchored to the handling date ("dated after the same day of the month N months before the handling date"), which matches `within_months`.
- **Cross-category read boundaries.** A reads term (`term_rent_changes`), parking and storage. B reads term. C reads term (`lease_terms` current) and utility. D reads term. E reads term. Every read is declared in `cross_category` and `inputs.cross_category`. None of them writes another category.
- **Terminal states.** No policy changes a lease status. E sets `request_status` from submitted to signed. None conflicts with the lifecycle.
- **Mutual exclusivity of task scopes.** The prerequisite graph has exactly two connected components, {A,B,C} and {D,E}. Two tasks can therefore claim them disjointly and cover all five policies together. The gate snapshot says the same ("all policies are covered across the suite with disjoint scopes"). The actual `charter_scope` values are masked and are compared after the reveal in the task files.
- **Conflict found between an extended policy and base: undeclared override in E.** See F-1.
- **Base late fee posting after D's overwrites: the merged meaning is ambiguous.** See O-1.

### rule_compute_equivalence

I checked every binding of every policy against its `compute_basis` quotation and swept back through the rule sentence by sentence.

- **A.** `period` (latest base_rent billing_period) matches "the period worked out is the latest billing period that carries a base rent line". `rent_line`, `rate` (floor-plan pct plus four steps), `discount` (RND once) and `credit_taken` all match their rule text: three quarters rounded down via `int(RND(x*100,6))/100`, half via RND, otherwise the whole discount. `result` returns 0 for a lease not enrolled or a period with a concession. All four step ladders match the prose thresholds (≥3 / 1–2 / 0 renewals; ≥10 / 6–9 drafts; ≥48 / 36–47 months; parking+storage / parking only / other).
  - Gap (O-2): the rule says "A credit already posted for a billing period is never re-rated" and that a credit is owed only for a period "whose base rent line carries no preferred_employer_discount credit". `compute` has no binding that returns 0 when the latest period already carries a credit. This is an empty promise at the compute layer. In both task worlds the latest base-rent period carries no discount credit at the opening, so there is no consequence.
- **B.**
  - `late_period`, `rent_line`, `rent_credits`, `rent_net`, `fees`, `late_net`, `rent_open`, `fees_open`, `late_open`, `fee_carry`, `late_carry`, `next_window`, `next_carry` and `result` each correspond to a quoted sentence.
  - `to_rent` and `to_fees` implement all three application orders and the CO branch of the charter order.
  - `days_before_next = days_in − DAYS(due, NOW)` is the number of days to the next due date, the day after the period's last day, which matches "one of the ten days before".
  - Deviation (O-3): the rule defines `paid` as payments in the month "less any of them returned", meaning returns of those payments. `compute` instead subtracts every return dated in the window. Neither task has a return, so there is no consequence.
- **C.**
  - `covered` implements all three tiers. The middle tier values each of the first five daily lines at `daily_sum/daily_count`, the average posted daily line, for the rule's words "each at the period's daily late fee amount". O-4 records that this phrase can be read two ways, and `0.md` shows which world it bears on.
  - The `weekday` offset uses reference 2024-01-01, a Monday, so Saturday gives 5 → 2 and Sunday gives 6 → 1. Both roll to Monday, as the rule says.
  - `lateness_share` thresholds are >20 / 11–20 / ≤10. `term_bonus` is ≥13 / 10–12 / shorter. `household_bonus` requires ≥12 payments and splits on balance = 0 versus > 0. `share` is `MN(1,…)`. All match the rule.
  - `ret_date` takes only the LATEST ach_autopay return (O-3b). An earlier in-period return followed by a later out-of-period return would be missed. Neither world has an autopay return.
- **D.**
  - `first_late = clock_offset + base_grace + grace_extra + 1` matches "the day after the last review grace day … counted as calendar days after the day the … clock starts".
  - `accrual_end` has the plan branch (`created_at` on or after the due date, status submitted), then the notice branch (notice for the period), then the handling date.
  - `daily_lines` is clamped to 0..late_fee_daily_max_days. `initial_allowed` applies only when accrual end ≥ first late day. `period_cap` has the TX and CO branches. `result` is floored at 0.
  - `lookback` and `earlier_late` follow the rule.
  - Every binding is quoted and no sentence is left unimplemented.
- **E.** `balance`, `left_out` (≤ plan grace → rent + fees; ≤ fee_window_days → fees; otherwise 0), `plan_arrears`, `base_pct`, `size_loading` (>1, >0.5), `term_loading` (≤120, ≤240), `tenure_credit`, `plan_pct` (floored at 0), `upfront`, `spread` and `result` (ceiling to the cent, plus upfront) all match the rule. The other figures the rule fixes (installment count, installment amount, first installment date) are not `compute` bindings. They are arguments of the same write, derived from rule prose, and are handled in `1.md`.
- **Rounding.** The rule's "rounded half up" is implemented with Python `round` on floats. On both task worlds no scored intermediate lands on an exact half-cent (checked: 143.55, 107.6625→107.66, 130.50, 118.80, 544.25). There is no consequence.
- **Rule style, observation O-5.** Every extended rule first states its baseline sentence ("The review percentage is the floor plan's late_fee_initial_pct."; "Nothing is paid up front."; "The period's payments are applied in the charter order…") and later a factor sentence that replaces it for the non-fall-through tiers. Read literally, each such pair is two absolute statements about one quantity. The specific sentence always names its conditions and keeps the baseline as its "any other" fall-through, so a reader resolves the pair specific-over-general into one reading. The pattern is the framework's design (the baseline must be in the rule), and no second defensible value results in either world.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: (post_employer_discount_credit_34aaf7ea, amount), (make_rent_catch_up_payment_381e22a2, amount), (grant_courtesy_late_fee_waiver_1c994f24, amount), (post_late_fee_review_reversal_dc9bc174, amount), (sign_payment_plan_b63c5de9, down_payment_amount). Each is claimed exactly once.
- uuid8s: `34aaf7ea`, `381e22a2`, `1c994f24`, `dc9bc174`, `b63c5de9`. They are pairwise distinct, share no common prefix or suffix, are not sequential and are not re-tailed copies. They look independently generated.
- Tool bodies: each performs one `ctx.create` or `ctx.update` and returns a receipt. None reads history, judges eligibility, checks a prerequisite, errors or refuses on business grounds. The prerequisite check is therefore never moved into the tool layer.
- Docstrings: no tool names another tool, a sequence position or an ordering instruction. "The balance due after it/after the payment" and "installments after the down payment" describe a quantity, not an order of actions. No docstring adds a confirmation, review or wait that the policies lack.
- The payment tool's `payment_method` docstring gives exact meanings, including "ach_autopay — … never a payment made by hand".
- Observation O-7: E's rule says "the down payment is paid by the resident as a plan payment carrying the plan's reference". The only payment tool in the difficulty is B's `make_rent_catch_up_payment_381e22a2`, whose docstring is about catching up rent that is behind and which accepts a `plan_request_id`. If a task scored the down payment through that tool, B's claimed tool would carry E's quantity. `1.md` checks whether task 1 does this.

### prerequisite_graph

- `prerequisite` is filled in on all five policies ([] on A and D). Edges: A→B, B→C, D→E. Every `problem` is an extended policy id in this file. No edge points at a base policy or at itself. The graph is acyclic, with two components.
- `policy_source` is found verbatim, modulo YAML line folding, in the blocked policy's own `rule`:
  - B: "The catch-up amount for a late billing period is not fixed until that period's base rent line carries the preferred employer discount credit owed on a lease enrolled in the preferred employer program." This is rule sentence 2 of B.
  - C: "A courtesy waiver on a billing period is granted only after the ledger shows a catch-up payment for that period, received on or after its first late day, in the full catch-up amount." This is rule sentence 4 of C. The same sentence is also C's second `overwrite.replaced_by`, which is consistent.
  - E: "The figures of a payment plan are fixed only after the most recent late billing period's late fees stand at the amount the late fee review allows, any excess carrying its charge reversal credit on that period's initial late fee line." This is rule sentence 2 of E.
- `form: state` on all three edges. No `fallback_reason` is present, which is correct because none is required.
- `condition` against each sentence:
  - B's condition ("… base_rent line is the source_charge_id of a preferred_employer_discount credit posted for that billing_period") matches the sentence's strength.
  - C's condition ("A lease_payment dated on or after the late billing period's first late day, in the catch-up amount of that period") matches.
  - E's condition ("late fee lines … less the charge_reversal credit … equal the late fees the late fee review allows") matches.
  - None is strengthened or weakened.
- `resolved_by` equals the depended-on policy's `target_tool` in all three cases. Each write produces the state in its `effect`: A creates the preferred_employer_discount credit, B creates a lease_payment dated today, and D creates the charge_reversal on the initial line.
- `kind: value_input`, and each gate is a real binding of the blocked compute: `rent_credits` in B, `last_pay` in C, `balance` in E.
- No authoring-viewpoint wording appears anywhere in `prerequisite`.

### prerequisite_sentences

Four-point test:

| edge | ordering connective | waited-on state (record-visible, no actor or tool) | no tool / id / snake_case | strength = condition |
|---|---|---|---|---|
| A→B | "not fixed until" | base rent line carries a preferred employer discount credit (`lease_charges.charge_code` + `source_charge_id`) | yes | yes |
| B→C | "granted only after" | ledger shows a payment for the period, on/after its first late day, in the full catch-up amount | yes ("catch-up payment" is a term B's own rule defines, not an id) | yes |
| D→E | "fixed only after" | the period's late fees stand at the reviewed amount, excess carried by a charge reversal credit on the initial line | yes | yes |

- **Exactly one write per state.**
  - A→B: only A writes a `preferred_employer_discount` line.
  - B→C: only B creates a `lease_payment`. E's sign tool writes no payment.
  - D→E: only D writes a `charge_reversal`. C's waiver writes `late_fee_waiver`, which the sentence ("its charge reversal credit") excludes.
- **Derivation, each edge has one reading.**
  - B→C. C's rule names a "catch-up payment". The only rule that defines one is B ("A catch-up payment is the resident's own one-time lease payment that brings the most recent late billing period … current, and its amount is the catch-up amount …"). The resolving action is B's user payment.
  - A→B. B's rule waits on the period's base rent line carrying the "preferred employer discount credit owed". The only rule that works out that credit is A, so the resolving action is A's agent credit.
  - D→E. E's rule waits on "the amount the late fee review allows" and "its charge reversal credit on that period's initial late fee line". The only rule defining the late fee review is D, so the resolving action is D's agent reversal.
- **No second wording, tool name or other policy id in any rule.** The depended-on rules (A, B, D) do not restate the blocked sentence.
- **Cross-problem orders stated in rules that ground no declared edge.** None found. D's accrual-end sentence reads `request_status submitted` on the plan request, which E's write flips to `signed`. That is a reverse value dependency (signing first would change D's value), but the declared D→E edge pins the order to D first, so there is one order and one terminal state. The dependency is recorded, with its numeric consequence, in `1.md`.
- **Base-rule orders.** The base rules contain sequencing sentences, for example lease_delinquency_and_default "The default is cured … when … the resident signs a payment plan and pays its down payment". None of them grounds an edge of either tree.

### override_declarations

This is the sentence-by-sentence sweep over `base_policy_refs` for each extended policy.

- **A** (refs: credits_and_waivers, rent_posting).
  - The preferred_employer discount sentence ("receives each month a preferred_employer_discount of preferred_employer_discount_pct times the monthly_rent in force, rounded half up") is declared superseded. The rate steps and the late share change the same quantity and sit inside the superseded sentence.
  - Followed without change: concession/discount no-stack, first full billing period, "Five credits exist … and no other", one credit per period.
  - rent_posting is followed.
  - Undeclared conflict: none.
- **B** (refs: payment_acceptance, payment_plan).
  - The state allocation-order sentence is declared superseded. The "charter order" B keeps for other leases (recurring fees, then late fees, then rent; CO rent first) agrees with base `allocation_order_default [non_rent, rent]` plus "oldest charge_date first".
  - Certified-funds and after-notice acceptance limits are inherited and do not apply in either world.
  - payment_plan: "Payments of a plan carry its plan_request_id" is inherited. A catch-up payment is not a plan payment.
  - Undeclared conflict: none.
- **C** (refs: credits_and_waivers, late_fee).
  - Two base clauses are declared superseded: "credits every late fee line … in full, one credit per late fee line", and "that the late rent of that period has been paid in full".
  - All other courtesy conditions are inherited explicitly: tenure ≥ courtesy_waiver_min_tenure_months, lease_msr_courtesy_waivers_12m < limit, autopay if required, lease_msr_returned_payments_12m = 0, not eviction_filed, and waive_once.
  - late_fee: "first late day" is used as defined there. See O-1.
  - Undeclared conflict: none.
- **D** (refs: credits_and_waivers, late_fee).
  - Six supersessions are declared: charge_reversal definition, effective grace, grace counting, initial late fee amount, daily accrual, and the CO cap.
  - Company cap and TX cap, observation O-8: base says "late_fee_cap_pct_of_rent times monthly_rent" and "tx_cap_pct_of_rent times monthly_rent". D says "times the period's base rent line". This is a change of base, not declared except for CO. It gives the same number whenever the base rent line equals the monthly_rent in force, which is true in both worlds (1980 = 1980, 2640 = 2640). No consequence.
- **E** (refs: payment_acceptance, payment_plan).
  - Two supersessions are declared: arrears "on the day it is drawn up" replaced by "on the day the resident signs", and "down payment at least payment_plan_min_down_pct" replaced by plan pct × spread + upfront.
  - Undeclared, see **F-1**: base lease_payment_plan says "the first due payment_plan_installment_interval_days calendar days after the plan is drawn up". E's rule says "the first due payment_plan_installment_interval_days calendar days after the day of signing". Neither `overwrite` entry names the base sentence. Entry 1's replaced_by ("the figures of a plan request drawn up earlier are worked out again on that day") re-computes the figures on the signing day but does not redefine the date the plan was drawn up, which is a record (`created_at`).
  - Inherited and followed: max arrears multiple, per-12-month cap, defaulted-within-365 refusal, signature requirement, good-standing rules, "at most payment_plan_max_installments".

### factor_ladders

Counts per policy (P = parameter, M = method):

| policy | factors | P | M | multi-source factors | cross_difficulty |
|---|---|---|---|---|---|
| A | renewal_step, autopay_step, tenure_step, household_bundle_step, late_period_share | 4 | 1 | household_bundle_step (parking × storage) | renewal_step → term (XCOUNT); household_bundle_step → parking (EXISTS) |
| B | application_order, recurring_fee_carry, late_fee_carry, next_month_window | 2 | 2 | application_order (lease_payments returns × term_rent_changes) | application_order → term (XCOUNT) |
| C | covered_lines, lateness_share, lateness_clock_start, term_bonus, household_bonus | 3 | 2 | household_bonus (utility_bills × utility_accounts); lateness_clock_start tier 2 (return rows × due-date weekday) | term_bonus → term (CFIELD); household_bonus → utility (XCOUNT + CFIELD) |
| D | review_grace_extension, review_clock_start, accrual_end, term_daily_relief, review_percentage, review_look_back | 3 | 3 | review_percentage (lease_charges × lease_payments) | term_daily_relief → term (CFIELD); review_look_back → term (XCOUNT) |
| E | plan_arrears_window, plan_history_percentage, arrears_size_loading, term_end_loading, tenure_credit, upfront_charges | 4 | 2 | upfront_charges (lease_payments × lease_charges) | term_end_loading → term (CFIELD) |

- **Bounds.** Every policy has 4–6 factors, at least 2 P and at least 1 M. Every ladder has three tiers that are disjoint as stated, and the fall-through is always the baseline value or method (checked against each `baseline` entry). Every tier appears in its rule in prose (condition and value or method) and in its `decides` binding.
- **Bindings.** The `bindings` sets are disjoint within each policy. No `decides` is `result`.
- **Label honesty.** Every M factor changes how the quantity is computed:
  - application order;
  - accrual window;
  - covered-line selection;
  - clock anchor;
  - look-back window;
  - composition of the arrears;
  - up-front split;
  - next-month inclusion window;
  - late share (a different algorithm: floor ×0.75 versus half-up ×0.5).

  Every P factor substitutes a number. Every M tier names a rule the charter itself states.
- **Tiers with the same value or method, found per floor plan or per state:**
  - **F-2 (latent SOURCE-FACTOR, affects no task in this bundle).** E `plan_history_percentage`: tier 2 selects `pct_defaulted_plan` = 0.50 and the fall-through selects `P('payment_plan_min_down_pct')`, which is 0.5 for Studio Residence and One-Bedroom Residence (`variants[*].parameters.payment_plan_min_down_pct`, lines 136 and 196). On those two floor plans the two tiers select the same value. Task 1 is a Two-Bedroom (0.4), where the three tiers are distinct (0.30 / 0.50 / 0.40).
  - **F-3 (latent SOURCE-FACTOR, affects no task in this bundle).** B `application_order`: in a CO community the fall-through "charter order" is "rent first, then … recurring fees, then … late fees" (rule and compute `MN(paid, rent_net) if F('community_state') == 'CO'`). That is the same method as tier 1 ("rent first, then its recurring fees, then its late fees"). For CO leases, tiers 1 and 3 are one tier written twice. Task 0 is AZ, where the three methods are distinct.
- **Realism of conditions and outcomes.** These tiers are loyalty and hardship relief for tenure, renewals, autopay record, bundled add-ons, clean payment record, household utility record, a weekend due date rolled to Monday, a returned draft restarting the clock, fees stopping once a plan is requested or a notice served, the current month left out while not yet past due, and higher down payments for bigger arrears, near term-end or after a defaulted plan. Each is a consideration a residential landlord's collections or resident-relations desk plausibly weighs. None of the conditions holds for every customer who reaches its write. The fall-through outcomes are the base charter's own treatments (full discount rate, base late fee schedule, whole waiver, min_down_pct, all fees carried). No tier outcome is one a landlord would not publish. No tier is read off a stamp field: every tier rests on aggregates of charge, payment, term, utility, parking or storage rows, or on date spans.
- **Categories the cross-difficulty factors read:** term (A, B, C, D, E), parking (A), storage (A, with parking), utility (C).

### findings

- **F-1 — SOURCE-POLICY RED (charter-global finding; the consequence is demonstrated in `1.md`).**
  - Symptom: E's first installment date conflicts with inherited base text.
  - Root cause: undeclared override of lease_payment_plan's "the first due payment_plan_installment_interval_days calendar days after the plan is drawn up" by E's "the first due payment_plan_installment_interval_days calendar days after the day of signing".
  - Evidence: `lease.extended.yaml` lines 1482–1485 (base) against lines 2563–2565 (E). E's `overwrite` (lines 2516–2529) names only the arrears and down-payment clauses.
  - Bears on: task 1, where the request was drawn up on 2026-03-12 and is signed on 2026-04-03.
  - Affected: E `overwrite` / E `rule`.
- **F-2 — latent SOURCE-FACTOR (ladder tiers identical on Studio and One-Bedroom).** Bears on no task in this bundle. Affected: E `factors.plan_history_percentage`, `params.pct_defaulted_plan` against the variants' `payment_plan_min_down_pct`.
- **F-3 — latent SOURCE-FACTOR (ladder tiers identical in CO).** Bears on no task in this bundle. Affected: B `factors.application_order`.
- **O-1 — observation.** D's `overwrite` declares as superseded the base late-fee **posting** sentences (effective grace, grace counting, the initial late fee amount, daily accrual, the CO cap), but its `replaced_by` sentences define only the **review** quantities. After the merge it is not stated what governs posting of `lease_late_fee` lines, or what "the effective grace period … defined by the late fee rule" now means for the delinquency-notice rule and for C's "first late day". The two seeds show both readings: task 0's March 2026 late fee lines follow D's review values (95 / 10 per day / first on 03-08), and task 1's follow base (132 / 12 per day / first on 03-07). No scored value in either task differs between the readings (demonstrated per task). Recorded as an observation.
- **O-2 — observation.** A's compute does not enforce "never re-rated / owed only when no credit". No consequence in either world.
- **O-3 — observation.** B's `paid` subtracts every return in the window rather than returns of those payments. O-3b: C's and D's `ret_date` look only at the latest autopay return. No returns exist in either world.
- **O-4 — observation.** C's rule "each at the period's daily late fee amount" admits a floor-plan-rate reading. It bears only on a world whose posted daily lines differ from the floor plan's `late_fee_daily_amount`. Demonstrated in `0.md`.
- **O-5 — observation.** Each rule states a baseline sentence and then a conditional replacement for the same quantity. Specific-over-general gives one reading.
- **O-6 — observation.** C and D can target the same initial late fee line under `waive_once`. Latent in this bundle.
- **O-7 — observation.** E's down payment has no dedicated tool. Checked in `1.md`.
- **O-8 — observation.** D's company and TX cap base changed from monthly_rent to the base rent line without being declared. The numbers are identical in both worlds.
- **O-9 — observation.** The brief's replay excerpt shows only the `1.json` line.

## closing_checklist

Written after both reveals. Everything above this heading was written before any reveal and is unchanged.

- **Files.** `_difficulty.md`, `0.md` and `1.md` exist, one per task (M = 2). This is the first revision, so there are no older revisions. Comparison sections: task 0 **PASS**; task 1 **SOURCE-POLICY RED** (F-1). **The difficulty does not close**: the checklist requires every comparison to carry PASS.
- **Scope.** GT `charter_scope`: task 0 = {A, B, C} with its three tools; task 1 = {D, E} with its two tools. The scopes are pairwise disjoint, cover all five extended policies and all five task tools together, and each scope spans its whole tree. The uuid8s are independent (§action_binding_and_uuids).
- **Trees.** Task 0 has 2 prerequisite problems and 2 value_input edges; task 1 has 1 and 1. Each tree has an `owner=user` write (B; E). The whole prerequisite graph {A→B→C, D→E} is acyclic, and no task references across trees.
- **Factors.** Every computation declares a baseline that suffices on its own and 4–6 factors, each with ≥ 2 P and ≥ 1 M. Each task has ≥ 1 multi-source and ≥ 1 cross-difficulty factor. Every factor bears weight against an honest baseline, and every whole-baseline number is definite and differs from gold: 99.00 / 3446.34 / 195.00 for task 0, 0.00 / 1781.12 for task 1.
  - Latent ladder defects F-2 (E, Studio and One-Bedroom) and F-3 (B, CO) affect no task in this bundle.
- **Gates.** The instantiation-stage gates were not re-run by this auditor; per Step 0 the auditor only cites them. The brief's snapshot (all rc = 0) is the last known run. A re-run on the final form belongs to the round that fixes F-1.
- **Open RED:** F-1 (E's undeclared first-installment override), which bears on task 1.

## revision_2

### charter_global_frozen (revision 2)

- Frozen: 2026-09-24, round 2, before any round-2 task JSON was opened.
- Hashes:
  - `lease.extended.yaml` sha256 `ab71b7ef12024f8d8e6061aa10ee0d61dbb1c21e5aaecffc52c8c11ec0bfdb76`. Changed from round 1 (`e9eb3a3f…`), so every charter-global section below was re-derived by re-reading the whole extended section (lines 1584–2804).
  - `task_tools.py` sha256 `d4cc8e87…8c085`. Unchanged, so §action_binding_and_uuids and the tool-body conclusions are carried forward from round 1 on that hash.
  - Base section: `diff` against `blueprint/products/lease.yaml` still shows only one trailing blank line, so the base copy is still verbatim.
- Round-2 masked views `r2/0.json` and `r2/1.json` hash identical to round 1 (`9f2f6718…`, `ba56c474…`).
- Fields masked until revision-2 freeze: the same list as round 1.
- Round-1 text above is untouched.

### what changed in the extended charter (found by re-reading, not taken from the reworker)

| policy | change | round-1 item |
|---|---|---|
| A | new binding `credit_on_period`, and `result` returns 0 when the period already carries a discount credit; compute_basis quotes "A credit already posted for a billing period is never re-rated" | O-2 |
| B | tier 1 of `application_order` becomes "rent first, then its late fees, then its recurring fees" in the rule, in `overwrite.replaced_by`, in the ladder and in compute (`to_fees = MN(MX(0, paid − to_rent − late_net), fees)`) | F-3 |
| B | the `paid` wording becomes "less the returned payments dated in that month" in the rule, the baseline rule and compute_basis | O-3 |
| C | new sentence: "When that initial late fee line already carries a charge_reversal credit, the courtesy waiver credit is posted instead against the period's earliest daily late fee line that carries no credit, a charge being waived or reversed at most once." | O-6 |
| C | "each at the average amount of the daily late fee lines posted for the period" | O-4 |
| C, D | the clock wording becomes "when the latest ach_autopay payment return on the lease is dated within the period", matching compute | O-3b |
| D | new sentences: "Late fee lines post on the late fee review schedule this rule sets out … the review grace days and the first late day of the review are the effective grace period and the first late day that every other rule of this charter reads. The late fee review reversal credits a period whose lines were posted on any other schedule." | O-1 |
| D | new `overwrite` entry declaring the company and TX cap clause superseded | O-8 |
| E | new `overwrite` entry: superseded "the first due payment_plan_installment_interval_days calendar days after the plan is drawn up", replaced by "… after the day of signing, not after the day the request was drawn up …"; the rule carries the same wording | F-1 |
| E | `pct_completed_plan` / `pct_defaulted_plan` (0.30 / 0.50) replaced by `completed_plan_credit` / `defaulted_plan_loading` (0.10 / 0.10), each relative to the floor plan's `payment_plan_min_down_pct`, in the rule, compute and ladder | F-2 |
| E | new sentence: "Signing records the figures only; paying the down payment is the resident's own later act, as a plan payment carrying the plan's reference, and is not part of signing." | O-7 |

Nothing else in the extended section moved:
- `prerequisite` blocks, `policy_source` sentences, target tools, `computes`, factor ids, labels, `decides`, `bindings` and baselines are unchanged.
- Other params and cross_category declarations are unchanged.

### policy_conflict_scan (revision 2)

- The subjects, write targets, triggers, time anchors, cross-category reads and terminal states are as in round 1. None of the edits moves a subject, a tool or a trigger.
- The graph is still {A→B→C, D→E}, so disjoint claims that together cover all five policies remain possible.
- New overlaps introduced by the edits:
  - **D's new "posting schedule" sentence** makes D the author of the lease_late_fee posting schedule and of the effective grace period and first late day "that every other rule of this charter reads". Base `lease_delinquency_and_default` carries its own counting sentence: "Grace days are counted as calendar days starting the day after the rent due date, without skipping weekends or holidays, so the first late day is the day after the last grace day." Its time eligibility `notice_after_grace` counts from the rent due date plus the effective grace period. D's review clock instead starts on the following Monday for a weekend due date, or on a returned-draft date, and adds tenure days. D's `base_policy_refs` and `overwrite` name only `lease_evt_credits_and_waivers` and `lease_evt_late_fee`. So the notice rule's own counting sentence is displaced by a sentence that no `overwrite` names. Neither task has a delinquency-notice write or a notice in its world, so no scored value in this bundle can be shown to move. Recorded as **R2-O1** (latent undeclared override of `lease_delinquency_and_default`).
  - **C's new target clause** reads D's state (a charge_reversal on the initial line). In a world where D is owed with a positive amount and a courtesy waiver is requested, D-then-C is fully specified. C-then-D is not: D's rule still posts on "the period's initial late fee line", which would then carry a late_fee_waiver, and `waive_once` forbids a second credit, while D's rule has no symmetric fallback. The C/D order is fixed by no declared edge. The two trees never meet in this bundle: task 0's D is 0.00 and task 1 has no waiver request. Recorded as **R2-O2** (replaces O-6).
- Round-1 F-1: closed at the charter level (see §override_declarations).

### rule_compute_equivalence (revision 2)

I re-checked every binding against its `compute_basis` quotation and swept back through each rule.

- **A.**
  - `credit_on_period` is quoted and implemented. O-2 is closed.
  - A re-run of A after its own credit is posted returns 0.00 on task 0's world, which I checked.
- **B.**
  - `to_rent` and `to_fees` for tier 1 implement rent → late → fees. For paid ≥ rent_net + late_net, `to_late` = late_net and `to_fees` = the remainder capped at fees. For paid < rent_net + late_net, `to_fees` = 0 and `to_late` = the remainder. All branches were checked.
  - `paid` now matches its sentence. O-3 is closed.
  - `compute_basis.to_fees` still quotes the charter-order sentence, which is accurate for tiers 2 and 3. Tier 1 of `to_fees` is covered by the `to_rent` quote.
- **C.**
  - `covered` uses `daily_sum/daily_count`, which is now what the sentence says. O-4 is closed.
  - `ret_date` is the LATEST autopay return, which is now what the sentence says. O-3b is closed.
  - The new target-line clause governs `source_charge_id`, which is an argument and not a compute binding. No compute binding is required for it.
- **D.**
  - The posting-schedule sentence restates the review's own quantities as the posting schedule and adds no new quantity to the reversal compute.
  - The reversal definition is unchanged. The equivalence of round 1 holds.
- **E.**
  - `base_pct = P(min_down) − K(completed_plan_credit)` / `+ K(defaulted_plan_loading)` / `P(min_down)` matches the new sentence.
  - The first-installment and "signing records the figures only" sentences govern arguments and the scope of the write, not compute.
- **O-5** (a baseline sentence followed by a conditional replacement for the same quantity) remains. It is by design and resolves to one reading, so it stays an observation.

### action_binding_and_uuids (revision 2)

Carried forward. The `task_tools.py` hash is unchanged, and each extended policy keeps the same `target_tool` and `computes`. The pairs are still claimed once each.

### prerequisite_graph and prerequisite_sentences (revision 2)

- The `prerequisite` blocks and the three `policy_source` sentences are unchanged, and each is still verbatim in its own rule (re-located at yaml lines 1810–1812, 2035–2037 and 2569–2570).
- Round-1 conclusions carry forward: acyclic, state form, four-point test passed, one resolving write per state.
- New in revision 2:
  - D's posting sentence and C's target clause state no ordering connective between problems. Their order implications are covered under R2-O1 and R2-O2.
  - E's new sentence "paying the down payment is the resident's own later act … and is not part of signing" places a write after E. That write is outside the tree and outside any declared edge. It is phrased as a statement of scope, not as a dependency of E's result, so it grounds no edge and conflicts with none.

### override_declarations (revision 2)

- **F-1 closed.** E's `overwrite` now names "the first due payment_plan_installment_interval_days calendar days after the plan is drawn up". That text is a verbatim substring of base `lease_payment_plan` at lines 1484–1485. The replacement is "…after the day of signing, not after the day the request was drawn up…", so the merged meaning is unique.
- **O-8 closed.** D's `overwrite` now names the company and TX cap clause.
- **New (R2-O1).** D's posting-schedule sentence reaches beyond `lease_evt_late_fee` into `lease_delinquency_and_default`'s own grace-counting sentence, which no `overwrite` names. No consequence in this bundle.
- Every other sentence-by-sentence conclusion from round 1 is unchanged.

### factor_ladders (revision 2)

- **F-2 closed.** `plan_history_percentage` tiers are min_down − 0.10, min_down + 0.10 and min_down. They are distinct on every floor plan (Studio/One-Bed 0.40/0.60/0.50; Den/Two/Three 0.30/0.50/0.40; Penthouse 0.23/0.43/0.33).
- **F-3 closed.** `application_order` methods are rent → late → fees (tier 1), fees → rent → late (tier 2), and fees → late → rent, or rent → fees → late in CO (tier 3). They are pairwise distinct in every state.
- Counts, labels, bindings and cross-difficulty declarations are unchanged from round 1 (A 5, B 4, C 5, D 6, E 6; P/M, multi-source and cross-difficulty as tabled in round 1).
- Realism: the new tier-1 order (rent, then late fees, then recurring fees) and the relative plan-history adjustments are treatments a landlord's collections desk plausibly publishes.

### findings (revision 2)

| item | round-1 class | revision-2 status | evidence |
|---|---|---|---|
| F-1 | SOURCE-POLICY RED | **closed** | E `overwrite[1]`, verbatim base clause |
| F-2 | latent SOURCE-FACTOR | **closed** | relative credit and loading; tiers distinct on all floor plans |
| F-3 | latent SOURCE-FACTOR | **closed** | tier 1 now rent → late → fees |
| O-1 | observation | addressed: D now defines the posting schedule; residual R2-O1 | D rule sentence 2 |
| O-2 | observation | closed | A `credit_on_period` |
| O-3 / O-3b | observation | closed (wording aligned to compute) | B `paid`; C/D clock wording |
| O-4 | observation | closed | C "average amount of the daily late fee lines posted" |
| O-5 | observation | unchanged (by design) | — |
| O-6 | observation | superseded by R2-O2 (half-specified) | C new clause |
| O-7 | observation | addressed (signing excludes the down payment) | E new sentence |
| O-8 | observation | closed | D `overwrite[4]` |
| O-9 | observation | this round's replay line again shows only `1.json`; unchanged | brief |
| **R2-O1** | new, observation (latent) | D's posting sentence displaces `lease_delinquency_and_default`'s grace-counting sentence without an `overwrite` | yaml line 2299 against base line 1319 |
| **R2-O2** | new, observation (latent) | C/D order unspecified when both are owed on one period | yaml line 2034 against D rule "posted as one charge_reversal credit whose source_charge_id is the period's initial late fee line" |

No new charter-global RED: R2-O1 and R2-O2 have no demonstrable consequence on either task world, which is shown per task below.

### closing_checklist (revision 2)

Written after the revision-2 reveals. Everything above is untouched.

- **Files.** `_difficulty.md`, `0.md` and `1.md` exist, one per task. Round-1 text is preserved, and `## revision_2` is appended in each file. Revision-2 comparisons: task 0 **PASS**, task 1 **PASS**.
- **Scope.** Task 0 = {A, B, C} with its three tools; task 1 = {D, E} with its two tools. The scopes are disjoint and together cover all five extended policies and all five task tools. The uuid8s are independent (carried forward; `task_tools.py` hash unchanged).
- **Trees.** Task 0 has 2 prerequisite problems and 2 value_input edges, with user write B. Task 1 has 1 prerequisite problem and 1 value_input edge, with user write E. The graph {A→B→C, D→E} is acyclic.
- **Factors.** Every computation has a baseline that works on its own and 4–6 factors (≥ 2 P, ≥ 1 M). Every task has ≥ 1 multi-source and ≥ 1 cross-difficulty factor. The tiers are distinct on every floor plan and in every state (F-2 and F-3 closed). Every factor bears weight, and every whole-baseline number differs from gold (99.00 / 3446.34 / 195.00; 0.00 / 1781.12).
- **Round-1 RED.** F-1 / T1-R1 is closed.
- **New in revision 2.** Two latent observations remain open, with no consequence in either task:
  - R2-O1: D's posting sentence displaces `lease_delinquency_and_default`'s own grace counting without an `overwrite`.
  - R2-O2: the C/D order is unspecified when both are owed on one period.
- **Gates.** The coordinator re-ran the gates on the final form (brief: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE OK; traceability deferred to render). This auditor cites that run and did not re-run the gates.
- **The difficulty passes the source-layer audit.**
