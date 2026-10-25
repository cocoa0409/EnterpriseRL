# Policy-task audit — financing_payments_and_hardship / charter-global

## charter_global_frozen
- Frozen: 2026-10-13T13:17Z (written before any task's GT was revealed; nothing below derives from a revealed GT field).
- Auditor: independent erl-task-policy-audit agent (did not author the artifacts).
- Artifact hashes (verified equal to the coordinator's brief):
  - `finance.extended.yaml` e580dc715a9bc4ab3539647fb60b936a1cf5318a4fcbeb640e13e438233c815e
  - `task_tools.py` e9d0c11114277c84afd3ed7b513dfa807060ca7c2c19f8fe7105214723126fc9
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/{finance,window,warranty,service}.yaml` (parameter lookups only), the extended charter, `task_tools.py`, and the compute DSL primitives in `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`, `MONTHS`, `DAYS`, `_within`; read for semantics only).
- Masked / unread: every `tasks/*.json`; the masked views were used only for the per-task files. No recursive search touched `tasks/` or `.audit_views/`.
- Base copy: lines 1-1384 of the extended charter equal `blueprint/products/finance.yaml` byte for byte except one trailing blank line, and `yaml.safe_load` of both base sections is identical. The base section is verbatim.
- Entry conditions (step 0): the gate snapshot, masked views and hashes came with the brief. Every gate is green except `check_traceability` (unlock tool-name provenance needs the published KB, which is deferred to step 3) and the expected "required document not found" errors from validate_scenario. The input is complete.

### policy_conflict_scan
Extended policies (6), their write tools and what they compute:
| id | target_tool (owner) | computes | prerequisite edges |
|---|---|---|---|
| P1 finance_ext_late_fee_assessment | post_finance_late_fee_832dc831 (agent) | amount of a late_fee | [] |
| P2 finance_ext_hardship_request_months | submit_finance_hardship_request_30b3e3a9 (user) | requested_months | [] |
| P3 finance_ext_hardship_deferral_grant | post_finance_hardship_deferral_5a1cdd93 (agent) | deferral_months | P2 (value_input `months_asked`, state), P1 (value_input `late_adj`, state) |
| P4 finance_ext_period_interest | post_finance_period_interest_067abc59 (agent) | amount of monthly_interest | P5 (value_input `balance_carried`, state) |
| P5 finance_ext_phone_payment_fee | post_finance_phone_fee_cbbb3871 (agent) | amount of a phone_payment_fee | [] |
| P6 finance_ext_catch_up_payment | submit_finance_portal_payment_b662a17f (user) | amount of a portal scheduled_payment | P4 (value_input `periods_due`, state) |

- Overlapping subjects. P1 and P5 both write `finance_fee_assessed`, but with different fee kinds, tools and computed amounts, so they do not collide. P2 and P3 both list `finance_payment_deferred`: P2 writes the intake row (`finance_hardship_requests`) and P3 writes the deferral. P1 and P3 meet on one subject, the late fee on a period that a deferral covers. See finding CG-1: this is a genuine conflict.
- Time anchors. Every write is dated on the handling day except P5's fee, which is dated on the named payment's posting date ("on the payment's posting date"; tool param `posting_date`). P5's "in the twelve months before the fee" is evaluated in compute from the handling date, not the fee's date (observation CG-O6).
- Cross-category read boundaries. Reads are limited to the window/door contract fields (contract_price, discount_program, status, payment_method), warranty_claims (claim_status, component, discovery_date) and service_plans.status. No policy writes another category.
- Claimed scopes. The prerequisite graph has exactly two connected components, {P1,P2,P3} and {P4,P5,P6}, which together cover all six extended policies and do not overlap. Which task claims which component is confirmed per task after reveal. Of the event types the blueprint claims for this difficulty, `finance_fee_reversed`, `finance_due_day_change_logged`, `finance_due_day_changed`, `finance_autopay_changed` and `finance_cancelled` are not the subject of any extended policy. This is an observation only, because joint completeness is measured against the extended policies.

### rule_compute_equivalence
- Every `compute_basis` quotation appears verbatim in its policy's `rule` (scripted check, whitespace-normalised: 0 misses in all 6 policies). Every `baseline.rule` sentence appears in its `rule`, every `overwrite.replaced_by` appears verbatim in its `rule`, and every `superseded_clause` appears verbatim in the cited base rule.
- Each factor's ladder tiers are stated in the rule prose (condition and value/method) and are implemented by the `decides` binding. No tier exists only in `compute`.
- Sweep back (compute → rule). Compute invents a basis or drops a rule clause in these places:
  1. **P6 `schedule_reach`** = `... else MN(periods_due, payments_covered + 1)`. The rule (and `baseline.rule`) says "every other account is brought to the scheduled balance after the payments covered plus one", with no cap at the periods fallen due. They diverge whenever payments_behind = 0, or when payments covered exceed the periods due. See finding CG-2.
  2. **`careline_active = EXISTS('service', status='active')`** in P1, P2, P4, P5 and P6. The rule says "an active CareLine service plan", but `service_plans.variant_name` also holds `On-Call Service Account`, which is not a CareLine plan (blueprint background; service.yaml variants). An active On-Call account satisfies the compute but not the rule. See finding CG-3.
  3. **P5 `named_payment` = `LATEST(... payment_channel='phone_agent')`**. The rule says "the most recent payment taken through a phone agent that does not yet carry its fee". When the latest phone payment already carries its fee and an earlier one does not, compute names the wrong payment. See finding CG-4.
  4. **P6 `fee_relief` = `MN(fee_pool, RND(fee_pool * shares, 2))`** rounds the relief on its own. The rule rounds only the scheduled balance and the final payment ("the catch-up payment is ... rounded to the cent"). This can differ by one cent only at an exact half-cent tie (`RND` is Python `round`), so it is recorded as an observation (CG-O4).
- Rounding sentences. P1: "only the final result is rounded to the cent" — compute `RND(combined_fee * shares, 2)`, and the share figure is rounded separately as the rule states ✓. P4: "Only the interest is rounded to the cent" ✓. P5: "only the final fee is rounded to the cent" ✓, with the small/large share figures "rounded to the cent" ✓. `RND` is Python `round()` (banker's rounding on float ties), while the base `amount_rounding` is `cent_half_up`. Ties have to be checked per task.
- Window semantics. `within_months=N` means `0 <= MONTHS(date, NOW) < N`, using a calendar-month difference with a day adjustment. This matches "in the N months before" as stated.

### action_binding_and_uuids
- (target_tool, computes) pairs are unique across the six policies ✓. Each base event type maps to exactly one write tool in this difficulty.
- uuid8 tails: 832dc831, 30b3e3a9, 5a1cdd93, 067abc59, cbbb3871, b662a17f. They are pairwise unrelated, with no shared prefix, sequence or adjacency ✓.
- No factor id is a substring of any tool name (scripted) ✓.
- Docstrings carry no concrete example value (formats only: YYYY-MM, YYYY-MM-DD, "2 decimal places") ✓. No docstring names another tool or states a position in a sequence, except one soft reference: the deferral tool's `finance_hardship_request_id` is "as returned by the hardship request lookup or by the filing of the request". That names the other problem's action in plain words, but it is not a tool name or an ordering word (observation CG-O5).
- Tool bodies validate no prerequisite: every body does one `ctx.create` (plus `ctx.update` of request_status for the deferral) with no guard, no error path and no hint ✓. No docstring claims an effect the body lacks ("shows on ... next statement" is descriptive and harmless).

### prerequisite_graph
- `prerequisite` is filled on all six (`[]` on P1, P2, P5). Edges: P3→P2, P3→P1, P4→P5, P6→P4. Every target is an extended policy id, none points at itself, and the graph is acyclic (two chains).
- Each `policy_source` is verbatim in its own (blocked) policy's rule ✓. Every `form` is `state`, so no `fallback_reason` is required ✓. Each `gate` names a binding that exists in that policy's compute (`months_asked`, `late_adj`, `balance_carried`, `periods_due`) ✓. Each `kind: value_input` names a binding that is a real input of the result ✓.
- `resolved_by` equals the depended-on policy's `target_tool` in all four edges ✓. Each `condition` restates its sentence's state without strengthening it ✓. No "in this task / at the opening" authoring phrasing appears ✓.

### prerequisite_sentences
| blocked | sentence (verbatim) | connective | state (record words) | the one write that brings it about |
|---|---|---|---|---|
| P3 | "The months granted are fixed only after the account carries a submitted hardship request from the borrower stating the months asked for." | only after | a `finance_hardship_requests` row with request_status submitted and requested_months | the borrower's hardship filing (P2's rule: "files the hardship request themselves, stating the reason and the months"). No other write creates a submitted request ✓ |
| P3 | "A deferral is not granted until the account carries the late fee owed for every statement period whose scheduled payment stayed unpaid past its grace period." | not until | a late-fee entry naming each period unpaid past grace | the late-fee posting (P1's rule: "posted as a late-fee entry naming that statement period") ✓ |
| P4 | "Monthly interest for a statement period is figured only after the account carries the phone payment fee owed for every payment taken through a phone agent." | only after | a phone-payment-fee entry naming each phone_agent payment | the phone fee posting (P5's rule: "charged once per payment ... naming that payment") ✓ |
| P6 | "A catch-up payment is not figured until the account carries a monthly-interest entry for every statement period whose due date has passed." | not until | a monthly-interest entry per period whose due date has passed | the interest posting (P4's rule: "posted once for each statement period whose due date has passed, as a monthly-interest entry naming that period") ✓ |

All four sentences name no tool, policy id, snake_case token or row id ✓. None is restated in the depended-on rule ✓. Each is written at the strength of its `condition` ✓. No extended rule states a cross-problem order beyond these four, except the inherited base sentence carried in P1's rule, "No late fee applies to a period covered by an approved hardship deferral". It is not an order, but it bears on the P3→P1 edge (CG-1). No base sentence grounds any edge.

### override_declarations
Sentence-by-sentence verdicts against each `base_policy_refs` entry:
- **P1 vs finance_late_fees**: S1 (one fee per period after grace) followed. S2 (assess only after grace) followed. S3 (counting rule) followed. S4 (amount = lower of fee and share, rounded) **replaced and declared**. S5 (hardship exclusion) followed and restated. S6 (courtesy waiver) and S7 (error reversal) kept by the replaced_by. S8 (reversed once) kept. **vs finance_payments**: allocation, cutoff and phone-fee sentences are untouched by P1. **vs finance_returned_payments**: "A returned payment does not count as paid" is followed (payments covered are net of returns). No undeclared override.
- **P2 vs finance_hardship**: S1 (borrower's own request) followed. S2/S3 (seasoning, counting) kept. S4 ("In addition the plan must offer ... lifetime maximum") **replaced and declared**: plan-offer and days-past-due are kept, and the per-deferral and lifetime caps on the months asked are replaced by the offer. Scope is named ("For a hardship request the borrower files, and only for such a request"); this covers every request, because base makes every request the borrower's own. S5 (end of term, interest, promo) not touched. S6 (decline) handed to P3.
- **P3 vs finance_hardship**: S6 ("A request that fails any condition is declined") **replaced and declared**, with scope named. The P2 and P3 overwrites retire different clauses of the same base policy, and each defers the other's half by name ("remain with the hardship request rules" / "remain with the hardship deferral rules"), so they do not collide. Merged semantics: the months granted (brought-forward plus forward months) are capped by nothing except P3's own "never exceed the months asked" on the forward part. The base lifetime cap survives only as a cap on the months asked, through P2. This is declared ("even where they differ from the months asked"), so it is not an undeclared override. The realism of granting more than the plan's per-deferral maximum is an observation (CG-O7).
- **P4 vs finance_interest**: S1-S2 (period-start balance, autopay at period start, non-negative) **replaced and declared** for non-promotional plans only, keeping "never makes the rate negative". The zero-APR and deferred-interest sentences remain for promotional plans ✓.
- **P5 vs finance_payments**: the phone-fee sentence is **replaced and declared**. It keeps once-per-payment, the posting date, naming the payment and the free channels, and the hardship waiver sentence is restated ✓.
- **P6 vs finance_payments / finance_agg_combined_exposure** (`overwrite: []`): allocation order is followed and restated. The free-portal sentence is followed. "Money beyond the scheduled payment reduces principal" does not govern the scored quantity: the catch-up repays amounts already fallen due. The "never split across accounts" and account-selection rules are untouched. No conflict in any sentence ✓.
- There are no anonymous intermediate factors, 0/1 multipliers or dropped base branches. The only base/extended clash on a scored outcome is CG-1, and it is a clash between a *retained* base sentence and an extended prerequisite, not an undeclared override.

### factor_ladders
Counts per computation (`parameter` / `method`; every ladder has 3 tiers including the fall-through; no two tiers of any ladder select the same value or method; `decides` is never `result`; binding sets are disjoint within each policy (scripted)):
| policy | factors | param | method | multi-source factor(s) | genuine cross-difficulty factor(s) (category is a difficulty) |
|---|---|---|---|---|---|
| P1 | 6 | 5 | 1 (arrears_combination: max / share-only / min) | arrears_combination tier 2 (behind ∧ late history ∧ return history); household_relationship tier 2 | project_size_share (window), program_courtesy (window), pending_claim_relief (warranty) |
| P2 | 5 | 4 | 1 (deferred_month_count: exclude disaster months / 36-month lookback / all) | storm_damage_extension (glass ∧/∨ frame claims), household_relationship_months (door ∧/∨ CareLine) | storm_damage_extension (warranty) |
| P3 | 4 | 3 | 1 (arrears_brought_forward: all behind / oldest only / none) | arrears_brought_forward (arrears ∧ request reason), returned_payment_record tier 2 (no returns ∧ autopay) | none (cross_category: []) |
| P4 | 6 | 5 | 1 (posting_timing_basis: actual/365, actual/360, monthly) | payment_standing_rate (autopay ∧ returns ∧ tenure) | program_rate_courtesy (window), claim_rate_relief (warranty) |
| P5 | 4 | 3 | 1 (payment_size_basis: min with share / max with share / flat) | agent_reliance_tier (autopay ∧ phone count) | program_phone_share (window) |
| P6 | 5 | 4 | 1 (arrears_reach: periods due / covered / covered+1) | arrears_reach tier 2 (one behind ∧ autopay) | program_fee_relief (window), claim_fee_relief (warranty) |

- Every computation is within 4-6 factors, has at least 2 `parameter` and at least 1 `method` ✓. P3 has no cross-category factor of its own. That is allowed: the cross-difficulty requirement is per task, and P3 can only appear with P1/P2.
- Label honesty. P1, P2, P4 and P5's method factors change the operator, aggregation or day-count convention ✓. P3 `arrears_brought_forward` and P6 `arrears_reach` select *which set of periods* enters the computation (all past-due periods vs the oldest only vs none; all fallen-due periods vs covered vs covered+1). These are integers fed into one formula, but each comes from a different counting rule over different records, not from a published constant. I accept them as `method` (observation CG-O8 records the weak point).
- **`cross_difficulty` labels**: `household_relationship` (P1) and `household_relationship_months` (P2) are labelled `door`, and `household_rate_courtesy` (P4), `household_phone_share` (P5) and `household_fee_relief` (P6) are labelled `service`. Neither door nor service is a difficulty of this scenario (blueprint difficulties: window, order, install, warranty, finance), so these five labels are wrong. Every policy except P3 still carries a genuine window or warranty factor, so whether the cross-difficulty floor is met is decided per task (CG-O1).
- Fall-through = baseline. In every factor, the fall-through tier is the factor's `baseline` and is what `baseline.rule` states for that input ✓. One exception is P6 `arrears_reach`: its baseline carries the `MN(periods_due, …)` cap that `baseline.rule` lacks (CG-2).
- Every `baseline.rule` is self-sufficient for a definite number: P1 lower of plan fee and plan share; P2 lower of per-deferral max and lifetime max less all deferred months; P3 the months asked; P4 balance × (APR − autopay discount)/12; P5 the plan phone fee flat; P6 balance less scheduled balance after covered+1.
- **Realism of ladders** (judged against consumer home-improvement financing practice; findings CG-5 and CG-O2/O3):
  - Plausible lender practice: tenure/standing counts (late fees standing, returns, on-time entries, payments covered), repeat-late fee schedules, project-size fee shares, autopay/loyalty rate reductions, actual/360 for legacy-dated contracts versus actual/365 for long periods, natural-disaster months excluded from lifetime caps, bringing arrears into a deferral, the military/first-responder/senior courtesy that a captive lender extends to programs the contract was sold under, and relationship goodwill for repeat household business (door contract, CareLine).
  - **Not plausible**: P4 `claim_rate_relief` cuts the *interest rate* of a closed-end plan published as "Fixed-Rate" by 2.00 or 1.00 APR points for any period in which the customer has a warranty claim awaiting a decision (CG-5). Under the base charter the rate moves only with autopay. No consumer lender reprices a fixed-rate installment loan month by month on the status of a product warranty claim, and the "any other claim" tier extends this to claims for screens, hardware or accidental breakage, which do not touch the financed obligation at all.
  - Doubtful but not demonstrable as unreal (observations): P4 `arrears_rate_margin` and the returned-payment premium of `payment_standing_rate`, which are penalty margins on a "Fixed-Rate" plan; the "any other claim awaiting a decision" tiers of P1 `pending_claim_relief` and P6 `claim_fee_relief`, which give fee goodwill for a claim unrelated to the financed work; P2 `storm_damage_extension`, which reads glass and frame warranty claims as storm evidence without looking at the request's reason; and P2 `household_relationship_months`, which adds hardship months for repeat business. In P3 `arrears_brought_forward`, the "at most two payments behind" conjunct is nearly implied by the base 59-days-past-due eligibility gate, but it is not universal, so it is not struck (CG-O7).

### findings
**CG-1 — SOURCE-POLICY RED (bears on task 0).**
- **Symptom.** P3 makes the deferral wait for a late fee on every period unpaid past grace, and then brings those same unpaid periods into the deferral. The retained hardship exclusion says no late fee applies to a period covered by an approved hardship deferral.
- **Root cause.** The P3→P1 prerequisite sentence and P3's `arrears_brought_forward` method were added on top of a base clause that P1 keeps in force. Neither policy says whether a late fee posted on a period that the deferral then covers stands or falls.
- **Evidence.** The following passages were quoted verbatim:
  - P3 rule: "A deferral is not granted until the account carries the late fee owed for every statement period whose scheduled payment stayed unpaid past its grace period."
  - P3 rule: "an account at most two payments behind whose request cites a natural disaster or medical hardship brings every payment behind into the deferral ... the deferral starts with the oldest payment brought in"
  - P1 rule, restating base finance_late_fees: "No late fee applies to a period covered by an approved hardship deferral".
  - The P3 edge `effect`: "The newly posted late-fee entry raises the late fees standing ... which can move the late-fee adjustment of the forward months."
- **Consequence.** The consequence is demonstrated in `0.md` against task 0's world. Under reading A, the late fee is posted, stands, and the deferral is shortened by it. Under reading B, the period's late fee is not "owed" because the deferral being granted covers it, so no fee is posted and the deferral is longer. These give two terminal states. On realism grounds, hardship deferral programs waive late charges on the periods they defer rather than assessing a new one as a precondition.
- **Affected.** finance.extended.yaml P3 `rule`/`prerequisite[1]`, P1 `rule` (last sentence).

**CG-2 — SOURCE-POLICY RED (charter-level; no consequence on either task's world, see 1.md).**
- **Evidence.** P6 compute: `schedule_reach: "... else MN(periods_due, payments_covered + 1)"`, with `factors[arrears_reach].baseline` equal to the same expression. The rule and `baseline.rule` say: "every other account is brought to the scheduled balance after the payments covered plus one" / "less the scheduled balance after the scheduled payments already covered plus one".
- **Demonstration.** Take an account with no payment behind and not on autopay (covered = periods due = n). The rule targets the scheduled balance after n+1; the compute targets the one after n. The two catch-up figures differ by one scheduled payment's worth of principal.
- **Affected.** P6 `compute.schedule_reach`, `factors[0].baseline`.

**CG-3 — SOURCE-POLICY RED (charter-level; no consequence on either task's world).**
- **Evidence.** `careline_active: "EXISTS('service', status='active')"` appears in P1, P2, P4, P5 and P6. Every rule says "an active CareLine service plan". `db_schema.service_plans.variant_name` includes `On-Call Service Account`.
- **Demonstration.** For a customer whose only service holding is an active On-Call Service Account, the rule leaves the share or adjustment untouched, but compute applies the CareLine tier, for example 0.95 on P1's late fee and +1 month on P2.
- **Affected.** The `careline_active` binding in all five policies.

**CG-4 — SOURCE-POLICY RED (charter-level; no consequence on task 1's world).**
- **Evidence.** P5 compute: `named_payment: "LATEST('finance_transactions', 'amount', date_field='txn_date', event_type='finance_payment_posted', payment_channel='phone_agent')"`. P5 rule: "The payment named is the most recent payment taken through a phone agent that does not yet carry its fee."
- **Demonstration.** Take a world where the latest phone payment already carries its fee and an earlier one does not. The rule names the earlier payment, whose amount decides the size tier; compute uses the later one.
- **Affected.** P5 `compute.named_payment`.

**CG-5 — SOURCE-FACTOR RED (unreal ladder; bears on task 1, which takes the workmanship tier).**
- **Evidence.** P4 `claim_rate_relief`. The ladder subtracts `workmanship_claim_relief` 0.02 or `open_claim_relief` 0.01 from the annual rate whenever a warranty claim is `submitted`. The plan is published as "Ridgeline Fixed-Rate 120/60" / "Low-Payment 144", and base finance_interest lets the rate move only with autopay.
- **Why it is unreal.** The condition (a pending product-warranty claim) is not one a consumer installment lender weighs when it sets the periodic interest rate on a fixed-rate loan, and the outcome (a temporary 1-2 point APR cut for as long as the claim waits) is not a treatment any such lender publishes.
- **Consequence.** The consequence is demonstrated in `1.md`.

**CG-O1 (observation).** Five factors carry `cross_difficulty: door|service`, which are not difficulties. Each task's genuine window/warranty factors are checked in its own file.
**CG-O2 (observation, realism).** P4 penalty margins on a "Fixed-Rate" plan: `arrears_rate_margin` +0.5/+2.0 points, and the returned-payment premium +1.0 point in `payment_standing_rate`.
**CG-O3 (observation, realism).** The "any other claim awaiting a decision" tiers of P1 (×0.75) and P6 (20 % fee relief), the household-relationship tiers in all policies, and the P2 storm extension, which ignores the request's reason.
**CG-O4 (observation).** P6's relief is rounded separately (tie-only, one cent).
**CG-O5 (observation).** The deferral tool's docstring says "or by the filing of the request".
**CG-O6 (observation).** P5's "twelve months before the fee" is anchored to the handling date in compute, while the fee is dated on the payment's posting date.
**CG-O7 (observation).** P3 grants brought-forward months on top of the asked months, which can exceed the plan's per-deferral and lifetime maxima. The "at most two payments behind" conjunct is nearly implied by the 59-day eligibility gate.
**CG-O8 (observation).** The `method` claim of P3 `arrears_brought_forward` and P6 `arrears_reach` rests on selecting different period sets, not on a different operator.

## closing_checklist
Written after both reveals (2026-10-13T13:22Z). The charter-global sections above were frozen earlier and have not been edited since.
- Per-task files `0.md` and `1.md` correspond one-to-one with tasks/0.json and tasks/1.json, and this file sits alongside them. This is the first revision; there is no older revision.
- Comparison results:
  - Task 0: SOURCE-POLICY RED (CG-1 / T0-F1) and SOURCE-FACTOR RED (T0-F2). Problem tree PASS. Unique solution PASS under reading A.
  - Task 1: SOURCE-FACTOR RED (CG-5 / T1-F1 and T1-F2). Policy self-consistency (task level), problem tree and unique solution PASS.
- Coverage: the six extended policies are covered as task 0 = {P1,P2,P3} and task 1 = {P5,P4,P6}. The two scopes are pairwise disjoint and each spans its whole problem tree ✓.
- Task tools and GT are closed ✓, and each uuid8 is independent ✓.
- Problem trees:
  - Task 0 has 2 prerequisite problems, both edges value_input, with user write P2.
  - Task 1 has 2 prerequisite problems, both edges value_input, with user write P6 at the root.
  - The difficulty-wide graph is acyclic ✓.
- Computations: each has 4-6 factors (≥2 parameter, ≥1 method). Each task has a multi-source factor and a genuine (window/warranty) cross-difficulty factor ✓. Every factor bears weight, and every all-baseline figure is definite and ≠ gold ✓. The exceptions are the RED items listed below.
- **The difficulty does NOT pass the source-layer audit.** Open items:
  - CG-1 (P3 late-fee prerequisite vs the retained hardship late-fee exclusion; bears on task 0).
  - CG-2 / CG-3 / CG-4 (charter-level rule/compute gaps in P6 schedule_reach, the careline_active binding, and P5 named_payment; no consequence on the current worlds).
  - CG-5 (P4 claim-based APR relief; bears on task 1).
  - T0-F2 / T1-F2 (claims seeded as awaiting a decision long after their plans' decision windows).
- Gate re-run on the final form: not performed. This difficulty is not at a passing final form, and the brief's gate snapshot (all green except deferred traceability) is the latest on record.

## revision_2

### charter_global_frozen (revision_2)
- Frozen: on disk by 2026-10-13T15:23Z. Written before any round-2 task GT was revealed, and built from the charter, schema and tool module only.
- Hashes, verified against the coordinator's brief:
  - `finance.extended.yaml`: **c75d90ab…db94110b**. This changed from round 1, so every charter-global section below is re-derived in full.
  - `task_tools.py`: e9d0c111…7126fc9, unchanged. The tool-contract conclusions of round 1 (§ action_binding_and_uuids: uuid8s, docstrings, no prerequisite validation in the bodies, no concrete examples) carry forward on that hash.
- Base section: lines 1-1384 are still byte-identical to `blueprint/products/finance.yaml`.
- Entry conditions: the coordinator's 15:05 UTC gate snapshot is all green except TRACEABILITY (6 unlock tool-name misses, deferred to step 3). The rebuilt masked views (fa9bd444…, bac1404c…) were verified.
- Prior context, disclosed: this auditor revealed the round-1 GT of both tasks during revision 1. Both worlds were regenerated, so the round-2 derivations below were done fresh on the new views. No round-2 task JSON was opened before the freeze.

### policy_conflict_scan (r2)
| id | target_tool (owner) | prerequisite edges (all state form, value_input) |
|---|---|---|
| P1 late_fee_assessment | post_finance_late_fee (agent) | [] |
| P2 hardship_request_months | submit_finance_hardship_request (user) | [] |
| P3 hardship_deferral_grant | post_finance_hardship_deferral (agent) | P2 (`months_asked`), **P4** (`arrears_adj`) |
| P4 period_interest | post_finance_period_interest (agent) | **[]** |
| P5 phone_payment_fee | post_finance_phone_fee (agent) | [] |
| P6 catch_up_payment | submit_finance_portal_payment (user) | **P1** (`balance_on_account`), **P5** (`fee_pool`) |

- The graph is acyclic. Its two components, {P2,P3,P4} and {P1,P5,P6}, cover all six policies and are disjoint.
- **CG-1 is closed.** P3 no longer waits on a late fee, and no longer brings past-due periods into the deferral. Its new rule says: "Scheduled payments whose due date has already passed stay due: a deferral never covers such a period, and those payments keep their own grace periods and late fee rules." The retained base sentence "No late fee applies to a period covered by an approved hardship deferral" therefore never meets a late fee on a deferred period. The P1 and P3 subjects no longer collide.
- No other overlapping subject, time anchor or terminal state conflicts.

### rule_compute_equivalence (r2)
- Scripted check: every `compute_basis` quote appears verbatim in its rule, except the four `result` bases (P1, P4, P5, P6). Each of those concatenates two sentences that are each verbatim but not adjacent in the rule (the result sentence plus the rounding-mode sentence). This is an observation (R2-O1) and not a gap.
- Every `baseline.rule` sentence, `replaced_by` and `policy_source` is verbatim. Every `superseded_clause` is verbatim in its base rule.
- **CG-2 is closed.** The P6 rule and `baseline.rule` now say "after the scheduled payments already covered plus one, but never beyond the scheduled payments that have fallen due". This matches `MN(periods_due, payments_covered + 1)`.
- **CG-3 is closed.** `careline_active` now ORs `EXISTS('service', status='active', variant_name=…)` over the five CareLine variants. Every rule adds: "A CareLine service plan here means a CareLine Basic, Plus, Premier, Premier 3-Year or Estate plan in active status; an On-Call Service Account is not a CareLine plan."
- **CG-4 is closed.** The P5 rule now says "The payment named is the most recent payment taken through a phone agent", which equals compute `LATEST(... payment_channel='phone_agent')`. Residual (observation R2-O3): with the old "does not yet carry its fee" guard gone, a world where the latest phone payment already carries its fee and an earlier one does not would leave P6's phone-fee prerequisite unresolvable through P5. Neither task's world has that shape.
- **CG-O4 is closed.** P6's rule now says "the relief is that sum times the fee pool, rounded to the cent and never more than the fee pool", matching `MN(fee_pool, RND(...,2))`.
- **Rounding mode (R2-O2, observation).** Every extended rule now says "an exact half cent going to the even cent". Two problems remain, and both matter only at exact half-cent ties:
  - The base variant parameter `amount_rounding: cent_half_up` ("Rounding of every computed amount") still stands, and no `overwrite` names it.
  - `RND` is Python `round()` on binary floats, which is not decimal half-even at every tie. For example, `round(2.675, 2)` is 2.67, while half-even would give 2.68.
  - No gold computation in either round-2 world lands on a tie (see the task files), so there is no consequence.
- New tiers checked both ways:
  - P1 `tenure_share` (36/24 payments covered; 0.90/0.95).
  - P4 `project_rate` (≥45,000 → −0.0025; <15,000 → +0.0025).
  - P6 `record_relief` (0/1/≥2 returns in 12 months).
  - P3's whole compute: record window, record_adj 12/6, returns_adj, arrears_adj, and result clamped to [0, months asked].
  - Each tier is a sentence of the rule and a branch of the binding, and the reverse holds too.

### prerequisite_graph and prerequisite_sentences (r2)
| blocked | sentence (verbatim) | connective | the one write that brings the state about |
|---|---|---|---|
| P3 | "The months granted are fixed only after the account carries a submitted hardship request from the borrower stating the months asked for." | only after | the borrower's filing (P2) |
| P3 | "A deferral is not granted until the account carries a monthly-interest entry for every statement period whose due date has passed." | not until | the monthly-interest posting (P4, "posted once for each statement period whose due date has passed, as a monthly-interest entry naming that period"). No other tool of this difficulty writes interest. |
| P6 | "A catch-up payment is fixed only after the account carries the late fee owed for every statement period whose scheduled payment stayed unpaid past its grace period." | only after | the late-fee posting (P1) |
| P6 | "A catch-up payment is not figured until the account carries the phone payment fee owed for every payment taken through a phone agent." | not until | the phone-fee posting (P5) |

- All four sentences are state form, name no tool, id or token, and are not restated in the depended-on rule.
- `gate` names a real binding in each case: `months_asked`, `arrears_adj`, `balance_on_account`, `fee_pool`. `resolved_by` equals the depended-on policy's target_tool.
- Realism holds. A lender brings interest accrual current before restructuring, and quotes a cure amount only after the fees owed are booked.
- No undeclared cross-problem order appears in any rule.

### override_declarations (r2)
The declared overwrites are unchanged from round 1: P1 replaces the late-fee amount sentence, P2 the "In addition…" limits, P3 the decline sentence, P4 the period-start balance/rate sentences, and P5 the phone-fee sentence. P6 has `overwrite: []`.
- P3's new sentence on past-due periods does not conflict with any base finance_hardship sentence. Base says only that "Deferred payments move to the end of the term".
- P6's added cap ("never beyond the scheduled payments that have fallen due") does not conflict with base finance_payments.
- No undeclared override on a scored quantity. The rounding-mode parameter is noted in R2-O2.

### factor_ladders (r2)
| policy | factors | param | method (as labelled) | genuine cross-difficulty | multi-source |
|---|---|---|---|---|---|
| P1 | 6 | 5 | arrears_combination (max / share only / min) | project_size_share, program_courtesy (window) | arrears_combination tier 2; household_relationship tier 2 |
| P2 | 5 | 4 | deferred_month_count | storm_damage_extension (warranty) | storm_damage_extension; household_relationship_months |
| P3 | 4 | 3 | **record_window_anchor** | none | returned_payment_record tier 2 (no returns ∧ autopay) |
| P4 | 6 | 5 | posting_timing_basis (actual/365, actual/360, monthly) | program_rate_courtesy, project_size_rate (window) | payment_standing_rate |
| P5 | 4 | 3 | payment_size_basis (min with share / max with share / flat) | program_phone_share (window) | agent_reliance_tier |
| P6 | 5 | 4 | **arrears_reach** | program_fee_relief (window) | arrears_reach tier 2 (one behind ∧ autopay) |

- **CG-5 is closed.** No factor in P1, P4 or P6 reads warranty claims any more. The only warranty read left is P2's storm extension, which counts claims by component and discovery date, not by claim status.
- **CG-O1 is closed.** The household factors now carry `cross_difficulty: null`. Every remaining `window`/`warranty` label names a real difficulty.
- New tiers judged against home-improvement lending practice:
  - Tenure courtesy on late fees: plausible goodwill.
  - Origination pricing by project size, "fixed when the loan was made": plausible risk-based pricing.
  - Clean-record and single-return relief on the catch-up fee pool: plausible.
  - Record window measured from the end of the last deferral: plausible.
  - Arrears at grant reducing the deferral: plausible.
  - Remaining realism observations (CG-O2 penalty margins on "Fixed-Rate" plans; household-relationship factors; storm extension) are carried forward as observations, with the same judgement as round 1.
- **Method labels, judged on their merits as the coordinator asked. This revises round-1 CG-O8.** The test from the skill: a `method` tier must change how its quantity is computed, not "only substitute a different number into the same formula".
  - P1, P4 and P5 change operators or day-count conventions ✓.
  - P2 `deferred_month_count` changes the aggregation itself ✓. Tier 1 subtracts a second aggregate taken from a different table (the months asked on approved natural-disaster `finance_hardship_requests`).
  - **P3 `record_window_anchor` decides `record_window_months`**, which is the `within_months` argument of an unchanged count (`COUNT(scheduled_payment) − COUNT(returned)` over the last N months). Its three tiers yield the integers MONTHS(last grant)−months covered, MONTHS(funded)+1, and the constant 12. That is a lookback-window parameter.
  - **P6 `arrears_reach` decides `schedule_reach`**, the integer n of an unchanged closed form, balance − S(n) − relief. Its tiers yield n = periods due, covered, or min(periods due, covered+1).
  - Both therefore only substitute a number into the same formula, and both are `parameter` by the skill's definition. P3 and P6 are left with **no genuine `method` factor** (finding R2-CG-6).
- Every fall-through equals its factor's baseline and its `baseline.rule`. Every `baseline.rule` yields a definite number.

### findings (r2)
- CG-1, CG-2, CG-3, CG-4 and CG-5 are **closed** (shown above). CG-O1 and CG-O4 are **closed**. CG-O2, CG-O3 (household and storm parts), CG-O5 and CG-O7 carry forward as observations unchanged.
- **R2-CG-6 — SOURCE-FACTOR RED (charter; bears on task 0 through P3 and on task 1 through P6).** Each of P3 and P6 declares exactly one `method` factor, and on its merits that factor is a parameter (see factor_ladders). Each computation therefore has 0 genuine `method` factors, against the floor of 1. This is a revised ruling for P6, which round 1 accepted (CG-O8). P3's factor is new in this revision. Affected: `factors[record_window_anchor]` (P3) and `factors[arrears_reach]` (P6).
- R2-O1 (observation): the four `result` compute_basis entries quote two non-adjacent rule sentences.
- R2-O2 (observation): the extended half-even rounding sentence sits next to the base `amount_rounding: cent_half_up`, and Python `round()` is not decimal half-even at every tie. Tie-only.
- R2-O3 (observation): P5 names the latest phone payment even if it already carries a fee (see CG-4 residual).
- R2-O4 (observation): P3 counts "payments behind" from posted monthly-interest entries. On a world whose interest posting lags its due date, the borrower's relief therefore depends on the lender's own posting. This is by design and stated in the rule; it is what makes the P3→P4 edge bear weight.

### closing_checklist (r2)
- **Reveal.** Written after both round-2 reveals at 2026-10-13T15:23Z. The r2 charter-global sections above were frozen before the reveal and have not been edited since. Revision 1 text is untouched.
- **Files.** `0.md` and `1.md` each carry `## revision_2` with a frozen derivation, a GT comparison (every figure equal to gold) and findings.

**Round-1 RED status.**

| RED | status |
|---|---|
| CG-1 / T0-F1 | closed |
| CG-2 | closed |
| CG-3 | closed |
| CG-4 | closed |
| CG-5 / T1-F1 | closed |
| T0-F2 | closed |
| T1-F2 | closed |

**Round-1 observation status.** CG-O1, CG-O4, T0-O1 and T1-O1 are closed. CG-O2, CG-O3 (household/storm), CG-O5, CG-O6 and CG-O7 remain as observations.

**Regressions.** None.

**Structure checks.**
- Scopes: the two scopes are disjoint and together complete.
- Trees: each tree has 2 prerequisites, both value_input, one user write each, and the graph is acyclic.
- Factors: every factor bears weight, and every all-baseline result is definite and differs from gold.
- Cross-difficulty floors: met. Task 0 has warranty and window factors; task 1 has window factors.

**New / revised RED.** R2-CG-6 (SOURCE-FACTOR). The only `method` factor of P3 (`record_window_anchor`) and of P6 (`arrears_reach`) selects a number — a lookback length, or a schedule index — that feeds an unchanged formula. Judged on its merits, each is a `parameter`, so P3 and P6 each fall below the floor of one `method` factor. For P6 this revises round-1 CG-O8, at the coordinator's request.

**Verdict.** The difficulty does **not** yet pass the source-layer audit; R2-CG-6 is the only open RED. I did not re-run the gates: this is not a passing final form, and the coordinator's 15:05 UTC snapshot is the latest on record.

## revision_3

### charter_global_frozen (revision_3)
- Frozen on disk before any round-3 task GT was read.
- Hashes, verified:
  - `finance.extended.yaml` **1af42ceb…48c8cb7399**. It changed, so every charter-global section below is re-derived.
  - `task_tools.py` e9d0c111…7126fc9. Unchanged, so the tool-contract conclusions (uuid8s, silent bodies, docstrings) carry forward on this hash.
- Base lines 1-1384 are still byte-identical to the blueprint copy.
- Gate snapshot (17:25 UTC) is all green except TRACEABILITY (unlock tool names, deferred).
- Views verified:
  - 0.view f9890e30…: changed.
  - 1.view bac1404c…: unchanged from round 2.
- Prior context: the auditor has seen round-1 and round-2 GT for both tasks. Gold changed this round, and every figure below was recomputed on the round-3 charter.

### policy_conflict_scan / prerequisite_graph (r3)
- Edges:
  - P3 → P2: value_input, `months_asked`, state.
  - P3 → P4: **state_gate**, gate `finance_transactions.interest_kind` (a field path, allowed by the reference spec), state.
  - P6 → P1: value_input, `fee_pool`, state.
  - P6 → P5: value_input, `fee_pool`, state.
- The graph is acyclic, with components {P2,P3,P4} and {P1,P5,P6}. They are disjoint and cover all six policies.
- Each component has 2 prerequisites, of which at least 1 is value_input ✓.
- Every `policy_source` is verbatim in its blocked rule ✓, and every value_input gate is a real binding ✓.
- The P6 phone sentence now reads "A catch-up payment is not figured until the most recent payment taken through a phone agent carries its phone payment fee". This matches P5's naming ("The payment named is the most recent payment taken through a phone agent"), so exactly one write resolves it ✓.
- P3 no longer has an arrears adjustment, so the interest posting changes no P3 value; it gates the grant ("A deferral is not granted until …"). The edge's weight is the eligibility flip, as `state_gate` defines it ✓.
- No overlapping-subject or terminal-state conflict. P3 still never covers a past-due period, so CG-1 stays closed ✓.

### rule_compute_equivalence (r3)
- Scripted check: every `compute_basis` quote, `baseline.rule` sentence, `replaced_by`, `superseded_clause` and `policy_source` is verbatim. The four `result` bases are now contiguous (**R2-O1 closed**).
- **Rounding (R2-O2 closed).** Every rule says "Every amount this policy rounds to the cent goes to the nearest cent, and an exact half cent rounds up." This agrees with base `amount_rounding: cent_half_up`. Compute now rounds with `int(x*100 + 0.5 + 1e-06)/100`, which is half-up for the non-negative amounts it is applied to. The P6 result can go negative inside the expression but is clamped by `MX(0, …)`, so a truncation-toward-zero artefact cannot surface. Example: P1's program baseline 15 × 0.9 × 0.95 = 12.825 now gives 12.83 ✓.
- **P5 (R2-O3 and CG-O6 closed).**
  - The rule names the latest phone payment and adds "when that payment already carries its phone payment fee, nothing more is charged". Compute implements it with `0 if latest_fee_source == named_payment_id`, where the latest phone-fee entry by date is compared with the latest phone payment.
  - "The twelve months are counted back from the day the fee is entered on the account" matches compute, which anchors at the handling date.
- **P3 new compute.**
  - `extra_payments`, `returned_window` and `measured_record` (three tiers) match the rule's "How the payment record is measured …" sentence tier by tier.
  - `record_adj` (≥16 → +1, <6 → −2, else 0) and `returns_adj` (≥2 → −2, 1 → −1, 0 with autopay → +1, else 0) match the rule.
  - `result = MX(0, MN(asked, asked + adj))` matches "never more than the months asked nor below zero".
- **P6 new compute.**
  - `paid_net` and `unpaid_installments = MX(0, periods_due × sched − paid_net)` match "the scheduled monthly payment times the statement periods fallen due less the scheduled-payment money already paid net of returned payments".
  - `catch_up_figure` follows the three arrears tiers. `result` applies "the figure so worked out less the relief, rounded to the cent and never below zero" ✓.
- No compute basis is invented and no rule clause is unimplemented.

### override_declarations (r3)
Overwrites are unchanged from round 2.
- P3's revised record sentences replace nothing in base finance_hardship.
- P6's new arrears paths ("the unpaid part of the scheduled payments …", "the fee pool alone") apply allocation and cure-amount logic that base finance_payments does not govern, so `overwrite: []` still holds sentence by sentence.
- No undeclared override.

### factor_ladders (r3)
| policy | factors | parameter | method | method shape (merits) |
|---|---|---|---|---|
| P1 | 6 | 5 | arrears_combination | max / share only / min operators ✓ |
| P2 | 5 | 4 | deferred_month_count | tier 1 subtracts a second aggregate from another table; tier 2 is a windowed sum ✓ |
| P3 | 4 | 3 | **record_measure** | money measure ⌊(sched + extra − returned)/payment⌋ vs count of autopay draws − returns vs count of scheduled entries − returns: three different aggregations ✓ |
| P4 | 6 | 5 | posting_timing_basis | actual/365, actual/360 and monthly formulas ✓ |
| P5 | 4 | 3 | payment_size_basis | min with share / max with share / flat ✓ |
| P6 | 5 | 4 | **arrears_amount_basis** | unpaid installments + fee pool, vs fee pool alone, vs balance − scheduled balance: three different formulas ✓ |

- **R2-CG-6 closed.**
  - `record_window_anchor` is now labelled `parameter`, which matches its window-length nature.
  - `arrears_reach` is gone. `schedule_reach` is now a fixed `MN(periods_due, covered+1)` binding inside the third path.
  - Each computation has exactly one genuine `method` and at least 2 `parameter` ✓.
- **Realism of the new tiers.**
  - P6 tier 1, past-due installments plus fees, is the standard cure amount.
  - P6 tier 2 (autopay with one behind pays fees only, and the draw collects the installment) is plausible.
  - P3's measure by money where extra principal was paid, or by autopay draws, is plausible.
  - P3 returns (−2/−1/+1) and a thin record (−2) are plausible.
- Fall-throughs equal the baselines, and every `baseline.rule` gives a definite number ✓.
- Genuine cross-difficulty factors: P1 project size and program; P2 storm; P4 program and project size; P5 program; P6 program.

### findings (r3)
- **R2-CG-6 closed.**
- R2-O1, R2-O2, R2-O3 and CG-O6 are closed.
- R2-O4 is closed for P3, which now uses interest entries only as a gate. In P1, P4 and P6, payments behind are still counted from posted interest entries, as the rules state. Both worlds post interest through the due date before the counts are read, so there is no consequence.
- CG-O7 is closed: P3 no longer brings periods forward, and grants never exceed the months asked.
- Remaining observations, unchanged:
  - CG-O2: penalty margins on "Fixed-Rate" plans.
  - CG-O3: household-relationship tiers and the storm extension.
  - CG-O5: the deferral docstring.
- **No new charter-level defect.**

### closing_checklist (r3)
Written after both round-3 reveals (2026-10-13T16:09Z). The r3 charter section above was frozen before them. Revisions 1 and 2 are untouched.

**Per-task results**
- `0.md` and `1.md` each carry `## revision_3`.
- In both, the frozen derivation matches GT on every write, figure and sensitivity.
- Both end in PASS on all four relationships.

**Status of earlier REDs**
| round | REDs | status |
|---|---|---|
| 1 | CG-1, CG-2, CG-3, CG-4, CG-5, T0-F2, T1-F2 | all closed |
| 2 | R2-CG-6 | closed |

- No regression.
- No new defect.

**Closing conditions**
| check | result |
|---|---|
| Coverage | the six extended policies are fully covered, and the two scopes are disjoint ✓ |
| Task tools / GT | closed; independently generated, frozen uuid8s ✓ |
| Problem trees | each has 2 prerequisite problems and ≥1 value_input edge (task 0: 1 value_input + 1 state_gate; task 1: 2 value_input) ✓ |
| User write | each tree has one ✓ |
| Difficulty-wide DAG | holds ✓ |
| Computations | every one has 4-6 factors, ≥2 `parameter` and exactly 1 genuine `method` ✓ |
| Per task | at least one multi-source factor and one genuine cross-difficulty factor, each reading seeded rows ✓ |
| Factor weight | every factor bears weight against an honest baseline ✓ |
| All-baseline results | definite and ≠ gold ✓ |

**Realism observations (not grounds for rework)**
- CG-O2: penalty margins on Fixed-Rate plans.
- CG-O3: household-relationship tiers and the storm extension.
- CG-O5: the deferral tool's docstring wording.

**Gates on the final form:** the coordinator's 17:25 UTC run on this exact charter (1af42ceb…) and tool module (e9d0c111…). EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING and SCOPE are all OK. TRACEABILITY is NOT OK only for the 6 unlock tool-name misses that the published KB will resolve, which is deferred to the doc stage.

**The difficulty passes the source-layer policy-task audit at revision_3.**

## revision_4

### charter_global_frozen (revision_4)
- **Freeze.** Frozen on disk before any round-4 task GT was read.
- **Hashes (verified).**
  - `finance.extended.yaml` **2ae3afa9…478473c3**. Changed, so the charter-global sections are re-derived below against the round-3 copy.
  - `task_tools.py` e9d0c111…. Unchanged.
  - Views f9890e30… / bac1404c…. Unchanged since round 3.
- **Base copy.** Still byte-identical to the blueprint.
- **Gate snapshot (coordinator, post-rework).** All OK, including TRACEABILITY.
- **Additional input read in full.** `audits/render_source/financing_payments_and_hardship/finance_round1.md` (F1–F5), as the brief directs. It carries no scored values.
- **Auditor's own miss.** F1–F5 were found by the renderer against the round-3 charter (1af42ceb…), which this audit passed at revision_3. None of them was recorded by me:
  - F2 overlaps round-1 observation CG-O7 ("can exceed the plan's per-deferral and lifetime maxima"). At revision_3 I marked CG-O7 closed because grants no longer exceed the months asked, but I did not check the months asked against the offer or the lifetime maximum. That closure was premature.
  - F1, F3, F4 and F5 are undefined branches or rule/compute gaps. My round-3 sweeps checked them on the task worlds only and did not catch them at charter level.

### What changed (r3 → r4, scripted word-level diff of every policy field)
**Rules and overwrites.**
- P1, P2, P3 and P6 now scope themselves in rule (P1/P2/P3 also in `overwrite`) to "an account whose plan carries no promotion (a fixed-rate or low-payment plan)". Promotional-plan accounts are routed back to the base rules. P4 was already scoped. P5 is unscoped, because it does not depend on interest entries.
- P1, P4 and P6 add: "An account paid ahead of its schedule counts as no scheduled payments behind." This states the `MX(0, …)` clamp already present in compute.
- P2 adds:
  - "the offer is never more than the lifetime room and never below zero"
  - "The months asked on a request filed under this policy never exceed the hardship offer: a borrower who wants more is told the offer, and the request is filed for the offer."
  - The tenure ladder's short-tenure tier now uses its own parameter, `short_tenure_cut`.
- P3 rule and `baseline.rule` now say:
  - "The months granted start from the months asked on the request, and the deferral covers as many consecutive statement periods as the months granted, starting with the first statement period whose due date has not yet passed."
  - "When the span so counted is zero months or less, no payment falls inside the window and the measured record is zero."
- P4's 360-day branch now reads "the days since the previous monthly-interest entry, or since the funded date where there is none, over 360".

**Compute, params and factor ladders** (P2 only; all other compute is unchanged).
- params: `tenure_extension` 1 → 2, and `short_tenure_cut` 1 is added.
- `tenure_ext` uses `0 - K('short_tenure_cut')`.
- `result` = `MX(0, MN(lifetime_room, lower_figure + history_adj + relationship_adj))`.
- The `tenure_room` factor ladder is updated to match.

### Verification of F1–F5
**F1 — closed.**
- Every policy whose counts rest on monthly-interest entries is now confined to non-promotional plans in its own rule (and in its overwrite where it overrides base): P1, P2, P3, P4 and P6.
- On a Zero-Interest Equal Pay 24 or same-as-cash account:
  - The P3 interest gate does not apply; base finance_hardship governs.
  - P1, P6 and P4 fall back to base.
- The parenthetical "(a fixed-rate or low-payment plan)" matches the variants with `promo_type: none` (Fixed-Rate 60/120, Low-Payment 144) ✓.
- Residual (observation R4-O1): P6 routes promotional accounts to "the base payment rules", but base finance_payments states no catch-up figure, only allocation. Base delinquency ("brought current") is the nearest definition. Neither task is on a promotional plan.

**F2 — closed.**
- The offer is capped at the lifetime room in both rule and compute (`MN(lifetime_room, …)`). Requests are filed at most at the offer (rule). The grant never exceeds the months asked (P3).
- Grant ≤ asked ≤ offer ≤ lifetime room. The as-written lifetime overrun no longer exists.
- The submit tool still accepts any count. That is a tool-contract latitude, not a policy gap, because the rule fixes the filed figure.

**F3 — closed.** The rule now defines a window of zero or less (record = 0). Compute agrees:
- `_within` with N ≤ 0 counts nothing, so both the money measure and the count measure give 0.
- The thin-record tier (< 6 → −2) then applies, as the rule's ladder states.

**F4 — closed.** The 360-day branch names the funded-date fallback, matching `accrual_days`.

**F5 — closed.** The coverage sentence now ties coverage to the months granted. `baseline.rule` still gives a definite figure (the months asked, unadjusted).

### Re-derived charter-global checks (r4)
- **Scripted verbatim checks.** All six policies are clean: compute_basis, baseline sentences, replaced_by, superseded_clause and policy_source.
- **Prerequisite graph.** Unchanged and acyclic:
  - P3←P2 value_input; P3←P4 state_gate.
  - P6←P1 and P6←P5 value_input on `fee_pool`.
- **Methods.** Unchanged: P1 arrears_combination, P2 deferred_month_count, P3 record_measure, P4 posting_timing_basis, P5 payment_size_basis, P6 arrears_amount_basis. Each is genuine, as judged at r3.
- **Factor counts.** All within 4-6, with at least 2 `parameter` and at least 1 `method` each.
- **P2 tenure ladder.** The tiers are +2 / −1 / 0, all distinct. The changed values are drawn from the charter's params ✓.
- **Realism.**
  - Two extra months of lifetime hardship room for a borrower who has kept 36+ payments covered is plausible.
  - So is a one-month cut below 12 payments.
  - Capping the offer at the lifetime room restores normal lender practice.
- **Override declarations.** The new scoping clauses narrow the declared overrides without leaving a base sentence undeclared. No new conflict was found.
- **Rounding.** Half-up in rule and compute, unchanged from r3 ✓.

### findings (r4)
- **Closed:**
  - F1, F2, F3, F4, F5.
  - Every earlier closure (rounds 1-3) still holds; no regression.
- **New observation:**
  - R4-O1: the P6 promotional-plan route points at base payment rules that state no catch-up figure. No task world exercises it.
- **Carried observations:** CG-O2, CG-O3 and CG-O5.
- **New RED:** none.

### closing_checklist (r4)
Written after both round-4 reveals. The revision_4 charter section above was frozen before the reveals, and revisions 1–3 are untouched.

**Item status**
- Render-source F1–F5: closed (verified above).
- Every RED and observation closure from rounds 1–3: still holds. No regression, no new RED.
- Previously premature closure: CG-O7, now genuinely closed via F2.

**Closing checklist**
- **Per-task results.** Both tasks' frozen derivations equal GT on every write, figure and sensitivity.
- **Scope.** The scopes are disjoint and together complete.
- **Trees.** Each tree has 2 prerequisites, at least 1 value_input edge and one user write. The DAG holds.
- **Factors.** Every computation has 4–6 factors with exactly one genuine `method`. Every factor bears weight. Every all-baseline result is definite and differs from gold.
- **Cross-difficulty and multi-source floors.** Met in each task.
- **Gates on the final form.** The coordinator's post-rework run on 2ae3afa9… / e9d0c111… is all OK, including TRACEABILITY.

**Open observations (realism; not grounds for rework)**
- CG-O2: penalty margins on Fixed-Rate plans.
- CG-O3: the household-relationship tiers and the storm extension.
- CG-O5: the deferral docstring wording.
- R4-O1: P6's promotional-plan route points at base payment rules.

**The difficulty passes the source-layer policy-task audit at revision_4.**
- revision_4 verdict: task 0 PASS
- revision_4 verdict: task 1 PASS

## revision_5

### entry (r5): views and gates run by this auditor (2026-10-14, repo root)
- **Views.** Ran `.venv/bin/python /tmp/erl0060_coord/views.py financing_payments_and_hardship` (execute only). It printed:
  - `f9890e30887174891d44734ee41adaa29b5b19e435e30317c73a79c48467dd58 …/0.view.json`
  - `bac1404c4943684ccb36a123330b1fa4432d50223def7f91b313ffb454def0d3 …/1.view.json`
  - `b152d680a19f9e63e7fd56c385d68246684a5cd84eaf050a859ce7a06ce4bdbf finance.extended.yaml`
  - `e9d0c11114277c84afd3ed7b513dfa807060ca7c2c19f8fe7105214723126fc9 task_tools.py`

  The views keep only frozen_time, user_scenario and initial_state. Both worlds are unchanged since round 3. The tools are unchanged. The charter changed (2ae3afa9… → b152d680…).
- **Gate block.** Run with `DIFF=env/env_0060_window_replacement_company/tasks/financing_payments_and_hardship`, each script from `skills/erl-task-instantiate/scripts/`. Only the summary lines were read, to keep GT out of the blind derivation. Logs are in `/tmp/audit_d5_0060/gates_r5/`. Every gate exited 0.

  | gate | summary line |
  |---|---|
  | check_extended | "[PASS] compatible charter; … every prerequisite is stated by a prerequisite sentence; every task calls a customer's own tool; all policies are covered across the suite with disjoint scopes" / "EXTENDED OK" |
  | check_task_tools | "[PASS] complete business effects, Args coverage, four-way parameter typing, and success returns" / "TASK TOOL CONTRACT OK" |
  | replay_tasks --check | "1.json 13 True True 0 107 107 True" / "REPLAY OK" |
  | check_solvability | "SOLVABILITY OK" |
  | check_compute | "COMPUTE OK" |
  | check_grounding | "GROUNDING OK" |
  | check_traceability | "0.json 21 0 True", "1.json 16 0 True" / "TRACEABILITY OK" (0 misses) |
  | check_cross_fire | "[PASS] policy ownership, trigger declarations, and task scopes are structurally consistent …" / "SCOPE OK" |

  No gate is red, so the audit proceeds.
- **Source-side items read.** Only the source-side finding lines S1–S4 were read: `audits/policy_kb/financing_payments_and_hardship/0.md` ll. 82-83 and 1.md ll. 67-69. The derivation and GT sections of those files were not read.
  - S1: P6's promotional route has no figure.
  - S2: the base `parameter_schema` attributes `interest_basis` and `late_fee_cap_pct_of_payment` contradict the extensions.
  - S3: P3's nested window and measure factors have no baseline home.
  - S4: the P6 fee-pool floor exists in compute only.

### charter_global (r5, re-derived from the r4 → r5 diff)
- **Base.** The base section is still byte-identical to the blueprint. Only `extended_policies` changed.
- **Changes.**
  - **S2 adjudication sentences added to the rules of P1, P2, P3, P4 and P5.** Each states that the plan attribute describes the base rule and that this policy governs its own accounts:
    - P1: "the late fee may exceed the stated share"
    - P2: per-request cap and lifetime room
    - P3: "the months granted are bounded by the months asked, which the hardship request rules bound by the hardship offer"
    - P4: balance on the posting day and the annual rate
    - P5: "the flat fee is its standard amount"
  - **P6.**
    - Promotional route (S1): "No catch-up figure is quoted for an account on a promotional plan: such an account is brought current only by paying its scheduled payments as they are shown on the account, each applied first to fees, then to interest, then to principal, under the base payment rules, and a borrower on such a plan who asks for a single catch-up figure is referred to a representative."
    - Floor (S4): "(a pool below zero counts as zero)". This is now in the rule and in `compute_basis.fee_pool`.
  - **P3 (S3).**
    - The record adjustment is now part of the standard method, and `baseline.rule` states it in full: "a record of sixteen or more adds two months, a record under six takes two months away … The payment record is the scheduled-payment entries posted in the twelve months before the grant less the payments returned unpaid in those twelve months."
    - So `record_window_anchor` (fall-through: 12 months) and `record_measure` (fall-through: count of scheduled entries less returns) now have their baselines stated in the computation's own baseline. The factor `payment_record_months` is removed.
    - New factor `standing_late_record` (parameter): late fees standing in 6 months, where ≥3 → −2, exactly 2 → −1, fewer → 0.
    - New params: `record_step` 2, `late_heavy` 3, `late_two` 2.
    - The rule adds "The request answered is the most recent hardship request on the account whose status is submitted", which matches `LATEST(... request_status='submitted')`.
- **Scripted checks.**
  - All six policies are clean on every check: compute_basis verbatim with no missing key, baseline sentences, replaced_by, superseded_clause, policy_source, and no duplicate bindings.
  - The prerequisite graph is unchanged: P3←P2 value_input, P3←P4 state_gate, P6←P1/P5 value_input. It is acyclic.
  - Factor counts:

    | policy | parameter | method | method factor |
    |---|---|---|---|
    | P1 | 5 | 1 | |
    | P2 | 4 | 1 | |
    | P3 | 3 | 1 | record_measure |
    | P4 | 5 | 1 | |
    | P5 | 3 | 1 | |
    | P6 | 4 | 1 | |

    Every ladder has ≥3 distinct tiers. P3's `returned_payment_record` has 4 tiers: −2/−1/+1/0.
- **Realism.**
  - Standing late fees reducing hardship relief is plausible.
  - Two months for a strong payment record is plausible.
  - Referring a promotional-plan catch-up request to a representative is plausible.
- **Overrides.** The S2 sentences adjudicate parameter-schema descriptions, not base policy rule sentences, so no `overwrite` entry is required. No base rule sentence is newly contradicted.
- **Status of S1–S4.** All four are **closed** at charter level (above). R4-O1 is closed by S1. No new charter defect found.

### closing_checklist (r5)
Written after both round-5 reveals (2026-10-14). The r5 charter section above was frozen before the reveals; revisions 1–4 are untouched.

**Gates and views**
- I ran the full gate block myself on b152d680… / e9d0c111…. All gates are OK, including TRACEABILITY with 0 misses.
- I rebuilt the views mechanically and recorded their hashes.

**Item status**
- S1, S2, S3 and S4 are closed. R4-O1 is closed via S1.
- Every closure from rounds 1–4 still holds.
- No regression and no new defect.
- No scored value moved in either task: task 0 = 73.30 / 4 / 3; task 1 = 11.54 / 8.72 / 464.78. The only declared figure change is the set of P3 sensitivities, after the factor redesign.

**Closing checklist**
- Scopes: disjoint and complete.
- Problem trees: each has 2 prerequisites, at least one value_input edge and one user write; the DAG holds.
- Computations: every one has 4–6 factors with exactly one genuine `method`, and every factor bears weight against an honest baseline.
- All-baseline results: definite and different from gold.
- Cross-difficulty and multi-source floors: met in each task.

**Observations only (realism; not grounds for rework)**
- CG-O2: penalty margins on Fixed-Rate plans.
- CG-O3: household-relationship tiers and the storm extension.
- CG-O5: deferral docstring wording.

revision_5 verdict: task0=PASS task1=PASS
charter=CLEAN
