# Policy-task audit — flood_coverage_and_mortgagee_billing / charter-global

Round 1 (revision_1). Scenario `env/env_0024_homeowners_insurance_carrier`, category `flood`, M=2.

## charter_global_frozen

- Freeze time: 2026-09-24T23:41Z (written before any task's GT was revealed; nothing in this section is derived from a revealed GT).
- Auditor: independent policy-task auditor (Claude, erl-task-policy-audit), not the instantiating agent.
- Frozen inputs (sha256 verified at audit start against the orchestrator's view-construction hashes):
  - `tasks/flood_coverage_and_mortgagee_billing/flood.extended.yaml` = `9cce2f1cd155c47e4c5736376b6d24ecea6c1e36717523a81612a149a79601a4` (matches)
  - `tasks/flood_coverage_and_mortgagee_billing/task_tools.py` = `6d61732d7f9dbeb1f0f692b728ab9ca0998a541c66affb941a0e02a6162f523d` (matches)
- Fields read: `blueprint/blueprint.yaml` (the difficulty entry), `blueprint/products/flood.yaml`, `blueprint/share_tools.py` (flood/home/umbrella finders, identity, handoff), light greps of `products/home.yaml` / `products/umbrella.yaml` (lifecycle states, event type names), the extended charter in full, `task_tools.py` in full, and the two masked views (`frozen_time`, `user_scenario`, `initial_state` only).
- Fields masked and unread at the time this section was written: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`, the difficulty `worklog.md`, the scenario `worklog.md`.
- Base-copy check: `diff <(head -997 flood.extended.yaml) blueprint/products/flood.yaml` differs only by one trailing blank line; the base section is a verbatim copy.
- Entry conditions (Step 0): the gate snapshot came with the brief. check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and check_cross_fire all exit 0; check_traceability is deferred until the KB is published. Masked views and their hashes came with the brief (`0.view.json` 54173a5f…, `1.view.json` 892c52af…, both recomputed and matching). The input is complete.
- DSL semantics note: the auditor did not read the compute interpreter (it is under `skills/`, which is outside the read domain). Where a figure depends on DSL semantics, it is taken from the rule's prose: `DAYS(a,b)` = calendar days from a to b; `MONTHS(a,b)` = whole calendar months elapsed; `within_months=N` = the N months ending at the handling-time clock.

### policy_conflict_scan

The six extended policies sit on two disjoint subjects:

| policy | subject / computes | target_tool (owner) | base refs |
| --- | --- | --- | --- |
| flood_ext_renewal_indication | flood_renewal_offered / indicated_renewal_premium | record_flood_renewal_offer_81f1ff73 (agent) | premium_rating, renewal, agg_companion_discount |
| flood_ext_renewal_term | flood_policy_renewed / term_premium | renew_flood_policy_8cc307a9 (agent) | premium_rating, renewal, agg_companion_discount |
| flood_ext_renewal_payment | flood_payment_received / amount | pay_flood_renewal_premium_ad8d78a5 (user) | billing_and_mortgagee, renewal |
| flood_ext_increase_premium | flood_additional_premium / amount | bill_flood_increase_premium_f099355d (agent) | billing_and_mortgagee, premium_rating, waiting_period |
| flood_ext_cancellation_credit | flood_policy_cancelled + flood_return_premium / credit_amount | sign_flood_cancellation_83daa4cf (user) | cancellation |
| flood_ext_cancellation_refund | flood_refund_issued / amount | issue_flood_refund_b526defb (agent) | billing_and_mortgagee, cancellation |

- Overlapping subjects: none. Every event is claimed by exactly one extended policy.
- Two extended policies overwrite the **same** base sentence (flood_premium_rating S5, "At renewal the indicated premium is rated on … and the renewal term premium is the smaller of …"). renewal_indication replaces it with the rated-building-amount sentence and renewal_term replaces it with the renewal-credit sentence. That sentence governs two quantities, the indicated premium and the capped renewal term premium, and each extended policy replaces only the half it computes, so the merged semantics stay unique: indication → indicated premium, term → smaller-of + credits. **Observation** (O-G1): the split is implicit, because neither `overwrite` entry says which half of the sentence it takes.
- Triggers/eligibility/time anchors: renewal_grace (base) gates flood_policy_renewed; it is inherited and consistent with renewal_term and renewal_payment. accepted_reason (base) gates flood_policy_cancelled; it is inherited by cancellation_credit. billable_status (base) gates flood_premium_billed, which renew_flood_policy posts; the policy is in force on the renewal world.
- Cross-category read boundaries: every read is declared in `cross_category` and reached by a shared finder (`find_home_policies`, `find_umbrella_policies`, `find_umbrella_underlying`, `find_dwelling_policies`). No undeclared category is read.
- Terminal states: renewal chain → policy with a new term, a new premium and fee charge, and an insured payment. Cancellation chain → an additional-premium charge, the policy cancelled with a return-premium credit, and a refund. No two policies write conflicting terminal values on one field. (See O-G6 and O-G7 on account-level residues.)
- Scope across M=2 (from the trees derived blind in the task files): task 0 = {renewal_indication, renewal_term, renewal_payment}, task 1 = {increase_premium, cancellation_credit, cancellation_refund}. They are pairwise disjoint and jointly complete over the six extended policies. (This is confirmed against `charter_scope` in each task's comparison section.)
- **Observation** (O-G2): the difficulty's name and claimed event types include `flood_policy_bound`, `flood_endorsement_added`, `flood_coverage_updated`, `flood_mortgagee_changed`, `flood_mortgagee_invoice` and `flood_zone_updated`, but no extended policy targets any of them. No task involves a mortgagee, although "mortgagee billing" is in the difficulty's name. This is not a failure of any of the four relationships.

### rule_compute_equivalence

Check 2, policy by policy. Each tier named by `factors[].ladder` is a sentence of the rule and a branch of its `decides` binding, and the reverse also holds; no ladder tier exists in only one face. Findings are listed below. None of them bears on a task world, so all are **observations** unless marked otherwise.

- **renewal_indication**
  - `rated_building_amount` adds the guard `F('building_replacement_cost') > 0`, which is not in the rule ("when the building limit on file exceeds the building replacement cost on file"). Invented guard, inert on both worlds (O-G3a).
  - `era_home_same_address`, `home_year_built`, `home_same_address` and `home_months_in_force` use `CFIELD('home', …, status='in_force')` with no property-address filter, then compare the returned address. With two in-force HomeGuard policies, the row picked may not be the same-address one the rule names ("the customer's HomeGuard policy in force at the same property address"). Inert on task 0, which has one HomeGuard (O-G3b).
  - `elevation_claim_payments` is textually identical to `claim_payments_lookback`. It is a duplicate binding that keeps factor bindings disjoint (O-G3c).
  - Everything else is quoted verbatim in `compute_basis`: the zone rate, the newly-mapped window, the VE surcharge, the loss-load windows (36/120 months back from the renewal offer date = NOW), the elevation half-credit, the pre-FIRM/modern era, the companion tenure, multiplicative chaining, one rounding at the end, and the minimum.
- **renewal_term**
  - `tenure_months_for_cap` duplicates `months_continuously_insured` (O-G3c).
  - The claim-count windows are anchored at NOW; the rule says "before the renewal date". The renewal date could be read as the new term's start. That reading is inert on task 0 (see the task file) (O-G3d).
  - `umbrella_schedules_home` counts `umbrella_underlying_scheduled` rows only and ignores `umbrella_underlying_removed`. The rule says "has scheduled as underlying", present perfect. Inert on task 0, which has no removal rows (O-G3e).
  - Smaller-of, cap rounding, additive credits, a single reduction and final rounding are all quoted verbatim.
- **renewal_payment**
  - `pif_premium_charged` duplicates `new_term_premium` (O-G3c).
  - `earlier_balance` = all charges − all credits − new-term premium − new-term fee, quoted to "The balance left on the premium account from earlier terms".
  - The branch expressions of `balance_entering`: tier 1 → `earlier_balance`, tier 2 → `earlier_balance`, fall-through → `0` (see factor_ladders F-G2).
- **increase_premium**
  - `annual_change`, `attach_date`, `request_date`, `band_new_limit` and `itv_new_limit` all filter `change_code='building_increase'`. The rule speaks of "a limit increase", which includes a contents increase (O-G3f). `band_new_limit` and `itv_new_limit` are duplicates (O-G3c).
  - The mitigation window has no anchor in the rule ("within the mitigation window months"). The compute anchors it at NOW. The request-date reading is inert on task 1 (O-G3g).
  - `home_here_live_on_request` checks only `closed_date` > request date. It ignores the HomeGuard status (e.g. expired) and whether the HomeGuard was already bound on that date (O-G3h).
- **cancellation_credit**
  - The base flood_cancellation S4 clamp ("never before the effective date and never more than cancel_backdate_max_days before the date the signed request is received") is not overwritten, so it is inherited. The extended rule restates only "the date of the reason", and `cancel_date` = the request's `requested_effective_date` with no clamp. Rule+inherited base ≠ compute whenever the clamp binds. Inert on task 1: the reason date is 11 days before receipt, after the term's effective date (O-G3i).
  - `addl_attach` = the LATEST additional-premium effective_date and is applied to the SUM of all additional premium in the window. With two increases, both are returned on one attach date (O-G3j).
  - `claim_deduction` for a damage payment = premium_credit×(1−retention)+fee_returned, which drives the result to 0 and matches "no credit and no fee return are due".
- **cancellation_refund**
  - `request_received_on` = the request's `created_at`. The rule says "the date the signed cancellation request was received". See the task 1 file for the reading this admits on a pending-signature request.
  - `delay_days` uses `closed_date` as the cancellation date, which the sign tool writes. `home_owed_here` has no status filter, which matches the rule ("the customer's HomeGuard policy at the same property address shows an amount owed").
- Pattern across all six policies (O-G4): each rule carries the baseline sentence for a quantity ("The rated building amount is the building limit on file", "The earned share of the increase is the calendar days …", "the policy fee is not returned") and then the tiered sentence for the same quantity. A reader reconciles the two only by treating the tiered sentence as the more specific one. This is the framework's baseline-in-rule contract, so it is not a red light.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (six distinct tools, six distinct policies).
- Docstrings: none names another tool, and none carries a sequence word (before/after/first/then-as-order). "The policy then shows …" / "the premium account then shows …" describe the write's own result, not an order between writes. The tools add no confirmation, review or wait.
- Tool bodies (task_tools.py L35-38, L71-91, L117-128, L153-163, L193-208, L237-247) check no eligibility, prerequisite or amount. Each lands its write with the values handed in (module docstring L3-4: "None of them checks eligibility, ordering or amounts").
- uuid8: `81f1ff73`, `8cc307a9`, `ad8d78a5`, `f099355d`, `83daa4cf`, `b526defb`. There is no shared prefix, no shared tail and no sequence pattern, so they are independently generated. PASS.
- **Observation** (O-G5): blueprint.yaml L78 says "payments … are agent actions on a verified caller", while `pay_flood_renewal_premium_ad8d78a5` is `owner="user"`. This is a surface disagreement between blueprint prose and the tool contract. The charter's own event model does not fix an owner for flood_payment_received.

### prerequisite_graph

| blocked policy | problem | kind | gate binding (exists?) | form | resolved_by = problem's target_tool? |
| --- | --- | --- | --- | --- | --- |
| renewal_indication | [] | — | — | — | — |
| renewal_term | renewal_indication | value_input | `indicated` (yes, L1280) | state | record_flood_renewal_offer_81f1ff73 (yes) |
| renewal_payment | renewal_term | value_input | `new_term_premium` (yes, L1460) | state | renew_flood_policy_8cc307a9 (yes) |
| increase_premium | [] | — | — | — | — |
| cancellation_credit | increase_premium | value_input | `addl_billed` (yes, L1831) | state | bill_flood_increase_premium_f099355d (yes) |
| cancellation_refund | cancellation_credit | value_input | `credits_posted` (yes, L2007) | state | sign_flood_cancellation_83daa4cf (yes) |

- Every policy fills in `prerequisite`. Every `problem` is an extended id of this file, never a base id and never itself. The graph is two disjoint chains, indication→term→payment and increase→credit→refund, and is acyclic.
- Every `policy_source` is verbatim in that blocked policy's own `rule` (L1251, L1432, L1798, L1978). There is no `fallback_reason`, and none is needed because every edge is in the state form.
- Each `resolved_by` genuinely makes its `effect` hold. record_flood_renewal_offer writes `indicated_renewal_premium`. renew_flood_policy posts a `flood_premium_billed` with `term_effective_date` = the new effective date, which also becomes the policy's `effective_date`. bill_flood_increase_premium posts `flood_additional_premium` with `source_endorsement_id`. sign_flood_cancellation posts `flood_return_premium` with change_reason cancellation and marks the request completed.
- `condition` vs sentence (observations):
  - payment ← term: the condition adds "together with the policy fee for that term", which the sentence ("carries the premium charge for the new term") does not state. It is slightly strengthened but inert, because the same write posts both (O-G6a).
  - refund ← credit: the condition adds "the policy's cancellation request is no longer pending signature". It is strengthened but inert, because the same write does both (O-G6b).
  - credit ← increase: the condition covers endorsements "with premium_direction additional", while the sentence covers "every limit increase recorded on the policy". The condition is narrower than the sentence; a premium_direction-none increase would, by the sentence, block the credit forever. Inert on task 1, whose only increase is `additional` (O-G6c).
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite` field.

### prerequisite_sentences

Four-point test on each edge:

1. **term ← indication**: "The renewal term premium is fixed only after the indicated premium for the upcoming term stands on the policy."
   - It joins this policy's result to what it waits on with "only after".
   - The state is record-visible: `flood_policies.indicated_renewal_premium`, surfaced by `find_flood_policies` as "any indicated renewal premium".
   - It names no tool, id or snake_case token. Its strength matches the condition.
   - Exactly one write of this difficulty brings the state about: record_flood_renewal_offer (renew_flood_policy clears it).
   - Derivation: the sentence plus a policy record with an empty indicated premium plus the indication rule ("The indicated renewal premium is worked out on the renewal offer date …") leads, in one reading, to recording the renewal offer. PASS.
2. **payment ← term**: "A renewal payment is not taken until the premium account carries the premium charge for the new term."
   - "not until"; record-visible state (`flood_billing` premium_billed for the new term); no names.
   - Exactly one write posts a `flood_premium_billed`: renew_flood_policy. bill_flood_increase_premium posts `flood_additional_premium`, which is a different event.
   - Derivation: the sentence plus a premium account with no charge for the term after the expiring one plus the term rule leads, in one reading, to renewing the policy. PASS.
3. **credit ← increase**: "The cancellation credit is worked out only after the premium account carries an additional-premium charge for every limit increase recorded on the policy."
   - "only after"; record-visible (a `flood_additional_premium` with `source_endorsement_id`, filterable by `find_flood_billing(source_endorsement_id=…)`).
   - Exactly one write: bill_flood_increase_premium. Single reading. PASS (see O-G6c on scope).
4. **refund ← credit**: "No refund is paid out until the premium account carries the cancellation credit for the policy's signed cancellation."
   - "until"; record-visible (`flood_return_premium`, change_reason cancellation).
   - Exactly one write: sign_flood_cancellation. Single reading. PASS.

- No depended-on rule restates its dependent's sentence. No rule carries a second wording of an edge, a tool name or another problem's id.
- Undeclared cross-problem orders: a sweep of all six extended rules finds no ordering sentence besides the four above. Time windows such as "before the renewal offer date", "before the cancellation is processed" and "attaches after the renewal offer date" relate records to a clock, not problems to each other.
- Base rules: the only base sentence with a cross-activity order is flood_billing S3 ("A renewal is billed or invoiced renewal_offer_lead_days before expiration"). That is a clock relation and grounds no edge.
- PASS.

### override_declarations

Findings only. Each is a sentence-by-sentence sweep against every `base_policy_refs` entry.

- **renewal_indication**
  - vs flood_premium_rating:
    - S1 (building premium) is overwritten, declared.
    - S2 (contents premium) is followed verbatim.
    - S3 (annual premium, companion, rounding, minimum, fee) is overwritten, declared. Loss load, era adjustment and elevation are all named in the replacement, so there is no anonymous intermediate factor.
    - S4 (midterm limit change) is outside this subject. The rule's increased-limit tier rates a *future-attaching* increase at renewal, which is compatible with S4.
    - S5 is overwritten for the indicated-premium half (O-G1).
  - vs flood_renewal: S1–S3 (grace) and S5 (repetitive loss) are inherited and not touched. S4 ("Limit decreases and deductible changes … take effect only at renewal") is compatible.
  - vs flood_agg_companion_discount:
    - S1 is overwritten, declared. The eligible lines narrow from Home/Condo/Rent/LandlordGuard to Home/LandlordGuard, "live" narrows to "in force", and a tenure tier is added.
    - S2 ("One companion policy is enough and the discount never stacks") is followed: the long-tenure extra rewards one companion's tenure and does not stack two companions.
    - S3 (before fee and cap) is followed.
- **renewal_term**
  - vs rating S5: overwritten for the smaller-of/cap half, declared.
  - vs rating S3 (minimum annual premium): the minimum was re-declared by the indication's overwrite as applying "only to that final figure" of the indicated premium. After credits, the renewal term premium therefore carries no floor. The consequence exists only where credits push it under the tier minimum; see the task 0 file.
  - vs flood_renewal and flood_agg_companion_discount: no conflict.
- **renewal_payment** (`overwrite: []`)
  - vs flood_billing_and_mortgagee:
    - S1 and S2 are N/A to this subject.
    - S3 (renewal billed and due on expiration) is followed.
    - S4 (oldest-charge-first; confirmation numbers) is followed, and the rule cites oldest-first as its reason for adding a balance owed.
    - S5 (refund only on a credit ≥ refund_minimum, to the last payer) does not conflict. Netting an insured's credit into a payment is not a refund, and a third party's credit "is refunded to its payer instead", which is consistent with S5.
    - S6 is N/A.
  - vs flood_renewal: no conflict.
  - No base sentence fixes the amount of a renewal payment, so the pay-in-full discount, late-renewal charge and member dividend override nothing. The undeclared-override test passes. See O-G7 for the account-level residue this leaves.
- **increase_premium**
  - vs rating S4: overwritten, declared. The min_premium_change clause is carried into the extended rule.
  - vs rating S3: the increase companion discount multiplies the *recorded* annual premium change. Whether that stacks with S3's companion discount turns on whether the recorded change already embeds a discount; see the task 1 file.
  - vs flood_waiting_period S8 (midterm waiting days, attach date) and vs billing: followed.
- **cancellation_credit**
  - vs flood_cancellation:
    - S1–S3 (accepted, signed reasons) are inherited.
    - S4 (date of reason, clamped) is inherited but not implemented (O-G3i).
    - S5 (credit basis; the fee is never returned) is overwritten, declared. The partial fee return on a sale, the additional-premium return and the backdating retention all modify the quantity S5 governed, so the declaration covers them although the `replaced_by` text names only the day count.
    - S6 (claim paid → fully earned) is overwritten, declared.
    - S7 (nonpayment) is N/A.
- **cancellation_refund**
  - vs billing S5: overwritten, declared. The extended rule's first sentence restates the payer and minimum.
  - vs S4 (oldest-first) and vs flood_cancellation: no conflict.
- **Result: no undeclared override found.**

### factor_ladders

Per policy: factors with effect label, ladder tier count, distinctness, multi-source tiers, and whether each tier is stated in the rule and implemented in compute.

- **renewal_indication**: 6 factors, 1 method and 5 parameter. Every tier is stated in the rule (L1053–L1058) and implemented in compute.
  - `rated_building_amount_rule` (method; RC / future increased limit / limit on file): 3 distinct tiers. The label is accepted because the tiers choose the acting base from different records, not a charter constant (O-G8a: borderline).
  - `newly_mapped_building_rate` (parameter; 1.45 / VE×(1+extra) / zone rate): on the Contents Only, Essential and Standard tiers `zones_rated_extra_pct`=0 and VE is not in `zones_accepted`, so the VE tier equals the fall-through for a VE building and is unreachable anyway (O-G8b). Distinct for Plus, Premier and High Value.
  - `flood_loss_load` (15/5/0) is distinct.
  - `elevation_credit_after_claims` (pct / pct×0.5 / 0) collapses to 0/0/0 on Contents Only and Essential (`elevation_credit_pct`=0) (O-G8c). Distinct on Standard and above.
  - `construction_era_adjustment` (+10/−5/0) is distinct and cross_difficulty home.
  - `companion_discount_tenure` (tier+3 / tier / 0) is distinct, multi-source (HomeGuard record × tenure date; disjunct with LandlordGuard) and cross_difficulty home.
- **renewal_term**: 5 factors, declared as 1 method and 4 parameter.
  - `renewal_cap_tenure` (parameter; 8 / 12 / tier cap) is multi-source (tenure × counted claims). On Premier the tier cap is 12, which equals the tenured tier (two tiers, one value). On High Value the tier cap is 10, so a tenured claim-free customer is capped at 12, *above* the default, and the loyalty tier penalises loyalty (O-G8d). Distinct on Contents Only, Essential and Standard (18/15).
  - **`cap_claim_window` (declared method): the three tiers are `COUNT('flood_claims', within_months=K('loyal_window_months'|'tenured_window_months'|'loss_lookback_months'), date_field='entry_date', event_type='flood_claim_payment')` (L1283–L1285). That is the same counting algorithm with a different window constant substituted. By the skill's test, a tier that only substitutes a number into the same formula is a `parameter`. The method label is dishonest → F-G1.**
  - `prompt_payment_credit` (2/1/0) is multi-source (returned-payment window × last payment vs last due).
  - `claim_free_credit` (4/2/0).
  - `umbrella_account_credit` (3/1/0) is multi-source (umbrella status × underlying ledger × HomeGuard number) and cross_difficulty umbrella.
- **renewal_payment**: 4 factors, declared as 1 method and 3 parameter.
  - **`earlier_balance_treatment` (method): tier 1 (balance owed) → `earlier_balance`, tier 2 (credit + last payer insured) → `earlier_balance`, fall-through → `0` (L1466). Tiers 1 and 2 select the same method: carry the signed earlier balance into the payment. Adding a positive balance and "netting" a negative one is one signed addition. The ladder has two distinct outcomes, not three → F-G2.**
  - `pay_in_full_discount` (3/1/0), `late_renewal_charge` (25/10/0) and `member_dividend_lines` (4/2/0, cross_difficulty home+umbrella existence) are distinct.
- **increase_premium**: 6 factors, 1 method and 5 parameter. All ladders are distinct.
  - `increase_earned_share_method` (months/12 / full / days/term) is a genuine method.
  - `increase_companion_discount` is multi-source (HomeGuard × request date × tenure) and cross_difficulty home.
  - Layer, anti-selection, insurance-to-value and mitigation are parameters. Mitigation is multi-source (loss-avoidance × damage payments).
- **cancellation_credit**: 5 factors, 2 method and 3 parameter. All distinct.
  - `unearned_day_count` (method) is multi-source (request reason × HomeGuard closed_date) and cross_difficulty home.
  - `increase_premium_return` (method; full / share / none).
  - `window_claim_deduction` (parameter; whole / loss-avoidance amount / 0), `sale_fee_return` (0.5/0.25/0), `backdating_retention` (5/2/0).
- **cancellation_refund**: 4 factors, 2 method and 2 parameter. All distinct.
  - `credit_offset_order` (method) is cross_difficulty home+umbrella.
  - `refund_interest_rate` (6/3/0).
  - `refund_interest_anchor` (method) is cross_difficulty home.
  - `refund_method_charge` (2.5/1/0).
- Real-business sanity: every condition divides the customers who reach the write, and none restates the policy's scope. Observations only (O-G8e):
  - the refund "payment-method charge" (keeping 2.5% of a refund because the premium was paid by card);
  - the cancellation "backdating retention";
  - the High Value/Premier cap-tier inversion (O-G8d).
  None is demonstrated against a task world as a treatment no business would publish.
- Baselines:
  - Every `baseline.rule` is a sentence subset of its `rule` and its `params` are named keys.
  - Every factor's fall-through equals its `baseline` binding. Exception: `cap_claim_window` (baseline `claims_lookback_window`) and `refund_interest_anchor` (baseline `DAYS(closed_date, NOW)`) decide inputs that their policy's `baseline.rule` never mentions. The term baseline has no claim count, and the refund baseline has no interest. Their "baseline" is the rule's fall-through tier rather than anything `baseline.rule` states (O-G8f). These are not straw men.
- Counts that survive the tests:
  - renewal_term: 5 parameter-effect factors and **0 honest method** (F-G1).
  - renewal_payment: 3 factors and **0 method** once `earlier_balance_treatment` is struck (F-G2).
  - The other four policies meet the 4–6 / 2 parameter / 1 method bounds.

### findings

- **F-G1 — SOURCE-FACTOR RED (structure; bears on task 0)**
  - Symptom: renewal_term's only `method` factor, `cap_claim_window`, changes nothing but a window constant.
  - Root cause: the ladder's tiers are one COUNT expression with K('loyal_window_months'=36) / K('tenured_window_months'=60) / K('loss_lookback_months'=120) substituted (flood.extended.yaml L1283–L1286, L1342–L1356).
  - Evidence: the three compute branches differ only in the `within_months` argument.
  - Consequence: relabelled honestly as `parameter`, the renewal_term computation has 0 method factors, below the required 1. The demonstration against task 0's world is in `0.md`.
  - Affected: flood.extended.yaml `flood_ext_renewal_term.factors[cap_claim_window]`.
- **F-G2 — SOURCE-FACTOR RED (structure; bears on task 0)**
  - Symptom: renewal_payment's only `method` factor, `earlier_balance_treatment`, has two tiers that select the same method.
  - Root cause: `balance_entering: "earlier_balance if earlier_balance > 0 else (earlier_balance if (earlier_balance < 0 and last_payer == 'insured') else 0)"` (L1466). Tiers 1 and 2 both return `earlier_balance`.
  - Evidence: the rule sentence L1433 ("a balance owed is added in full … a credit balance is deducted …") is one signed addition of the earlier balance.
  - Consequence: the ladder has 2 distinct outcomes (<3 tiers), so the factor does not count. renewal_payment is then left with 3 factors (<4) and 0 method. The demonstration is in `0.md`.
  - Affected: `flood_ext_renewal_payment.factors[earlier_balance_treatment]`, compute `balance_entering`.
- Observations O-G1…O-G8 above. Each is inert on both task worlds unless a task file demonstrates otherwise.
- **O-G7 (account residue, charter-level)**
  - renewal_payment's pay-in-full discount, member dividend and late-renewal charge enter the payment figure, but no entry of the premium account records them. After the scored payment the account therefore does not settle to zero.
  - cancellation_refund's "applied to other Larkspur balances" offset is likewise recorded by no tool of this difficulty (no write posts it to the HomeGuard account or the flood account).
  - Figures are demonstrated in each task file. Neither residue creates a second scored answer, so both are observations.

## closing_checklist

Written after both reveals (2026-09-24T23:41Z onward). Everything above this heading was frozen before any reveal (pre-reveal sha256 `746f37c8…`) and has not been edited since.

**Status: NOT CLOSED.** Step 4 requires all four relationships PASS for every task. They do not:

| task | policy self-consistency | problem tree | factors | unique solution | blind = GT? |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS (O-0-1) | **SOURCE-FACTOR RED** (R-0-1 = F-G1, R-0-2 = F-G2, R-0-3) | PASS | yes, every write and parameter |
| 1 | PASS | PASS (O-1-1, O-1-2) | PASS | **SOURCE-TASK RED** (R-1-1, R-1-2) | yes under reading A; reading B changes the refund |

- Audit files: `_difficulty.md`, `0.md` and `1.md` correspond one-to-one with tasks 0 and 1. This is revision 1, with no older revision.
- Coverage and scope, confirmed against `charter_scope`:
  - task 0 = {renewal_indication, renewal_term, renewal_payment}; task 1 = {increase_premium, cancellation_credit, cancellation_refund}.
  - The scopes are pairwise disjoint and cover all six extended policies. The task tools are disjoint.
  - uuid8s are independent (action_binding_and_uuids).
- Problem trees:
  - Each has 2 prerequisite problems and 2 declared value_input edges (≥1 needed). Task 0's second edge carries weight only as a gate (O-0-1).
  - Each has one owner=user problem (task 0 payment; task 1 signature).
  - The whole-difficulty graph is two disjoint chains and acyclic.
- Factors:
  - All six baselines are self-sufficient and give definite numbers that differ from gold (868.80, 290.17, 303.43, 110.94, 593.60, 201.52).
  - Every declared factor bears weight on its own task's world.
  - Structural failures: F-G1 (renewal_term has no honest method factor) and F-G2 (renewal_payment's method ladder has two outcomes, which leaves 3 factors and 0 method).
- Instantiation-stage gates: not re-run by the auditor, per the brief. The snapshot supplied with the brief (7 gates exit 0; check_traceability deferred) is cited as the entry condition. A machine green light does not overturn the manual findings above: check_compute accepted the `cap_claim_window` method label and the `earlier_balance_treatment` ladder.

## revision_2

### charter_global_frozen (revision_2)

- Freeze time: 2026-09-24T23:57Z. Same auditor as revision_1. This section was written before any round-2 GT was revealed and holds nothing derived from a round-2 reveal.
- Inputs, re-hashed at audit start and matching the orchestrator's round-2 hashes:
  - `flood.extended.yaml` = `a477bad150bb45098707c26cdd2a554bbdec92cf2443e534acc6a38d8c7bc4a5`: **changed** (revision_1 was `9cce2f1c…`).
  - `task_tools.py` = `6d61732d…`: unchanged.
- The charter changed, so every charter-global section below is **re-derived in full**, not carried forward.
- The base copy is still verbatim: `diff <(head -997 …) products/flood.yaml` shows only the trailing blank line.
- Entry conditions: a round-2 gate snapshot came with the brief (7 gates green; traceability deferred). The masked views were rebuilt: `0.view.json` `54173a5f…` is unchanged and `1.view.json` `8770f41a…` changed. Input complete.
- contamination_disclosure (applies to all round-2 files):
  - The auditor read both tasks' revision_1 GT in round 1. So round-2 derivations are **not blind** where the round-1 GT was visible: the task 0 indication, and every task 1 value whose rule did not change.
  - They **are** blind where the rule or seed changed and no GT has been seen: the task 0 renewal term and renewal payment, and the task 1 interest-day reading.
  - No `tasks/*.json` was opened in round 2 before the freeze below. No worklog was read. The round-1 `_difficulty.md` text above is untouched.

### policy_conflict_scan (revision_2)

- Subjects, target tools and base refs are unchanged from revision_1's table. Each `(target_tool, computes)` pair still belongs to exactly one policy, and no subject overlaps.
- rating S5 is now split explicitly:
  - renewal_indication supersedes "At renewal the indicated premium is rated on the zone, elevation and limits on file on the renewal offer date".
  - renewal_term supersedes "the renewal term premium is the smaller of that indicated premium and the expiring term_premium increased by renewal_rate_cap_pct, rounded half-up to the cent."
  - Both are verbatim substrings of base S5 (L864) and they do not overlap. **O-G1 closed.**
- Cross-category reads are all declared. New are the term's HomeGuard `original_effective_date` read (the tenure start) and the umbrella `umbrella_underlying.event_type` read (removed rows). Both are reachable through `find_home_policies` / `find_umbrella_underlying`.
- Scope: the six policies still split into two disjoint chains (re-confirmed in the task files).
- O-G2 (the mortgagee claim is uncovered) is kept, and the rework says so.

### rule_compute_equivalence (revision_2)

- **renewal_indication**
  - The `building_replacement_cost > 0` guard is removed. **O-G3a closed.**
  - The HomeGuard CFIELDs now filter `property_address=F('property_address')`, so O-G3b is closed for HomeGuard. The LandlordGuard read `dwelling_same_address: CFIELD('dwelling', 'property_address', status='in_force') == F('property_address')` still takes one in-force dwelling unfiltered by address. **O-G3b therefore stays open for the dwelling line** (inert: no dwelling policy on either world).
  - `elevation_claim_payments` still duplicates `claim_payments_lookback`. O-G3c is kept.
- **renewal_term**, re-derived:
  - The tenure start is L1251 ↔ `anchor_*`/`tenure_months`. It is measured "in whole calendar months to the date the renewal is recorded" (= NOW), which closes **O-G3d**.
  - Tier 1: an in-force HomeGuard at the address with an earlier `original_effective_date` AND no payment in the loss lookback (`anchor_claims_lookback == 0`).
  - Tier 2: a payment in the lookback → LATEST payment `entry_date`.
  - Tier 3: the flood `original_effective_date`.
  - The cap is the tier cap − 7 / − 3 / 0 (L1252 ↔ `cap_pct`), with a 60-month claim window anchored at the date the renewal is recorded.
  - Scheduled minus removed rows for the umbrella ↔ "lists, and has not since removed". **O-G3e closed.**
  - The `tenure_months_for_cap` duplicate is gone.
- **renewal_payment**, re-derived:
  - The earlier balance is now in the baseline sentence L1432, with the third-party carve-out in L1433. `balance_entering` = `earlier_balance if (earlier_balance >= 0 or last_payer == 'insured') else 0` is equivalent.
  - The late charge is per day × all days past the term start when > 15, flat 10 for 1–15 days, and 0 otherwise (L1436 ↔ `late_charge`).
    - **N-G3 (observation)**: "each of those calendar days" could be read as only the days beyond the threshold. That reading makes the charge fall from 10.00 at 15 days to 1.25 at 16 days, a non-monotone schedule no business would publish. The all-days reading, which the ladder text "multiplied by the days passed" states, is the only coherent one. No second answer.
  - Electronic credit (L1438 ↔ `electronic_*`): the compute counts only EFT/card vs `check` and ignores `mortgagee_check`, while the rule says "all made by EFT or card". **N-G5 (observation)**: inert where no mortgagee payment is in the window.
  - `pif_premium_charged` still duplicates `new_term_premium` (O-G3c).
- **increase_premium**
  - The companion "in force on the request date" is now defined as "bound on or before that date and not cancelled or expired by it". The compute checks `bound_date <= request_date` and (`status == 'in_force'` or `closed_date > request_date`). **O-G3h closed.**
  - **N-G6 (observation)**: a HomeGuard that is still `pending_cancellation`/`pending_nonrenewal` (not closed) at handling time fails the compute test although the rule counts it. Inert on task 1, whose HomeGuard is cancelled with a closed date after the request.
  - The mitigation window is anchored "before the date the charge is posted" (= NOW). **O-G3g closed.**
  - The building-only filter is kept (O-G3f).
- **cancellation_credit**
  - "the date the cancellation request was received, as recorded on the request whether or not it had been signed by then" (L1809, L1813) ↔ `request_received` = `created_at`.
  - The base S4 clamp is still not implemented (O-G3i kept). **N-G2 (observation)**: the merged policy now has two anchors named "received". The inherited base S4 clamp still speaks of "the date the **signed** request is received", while the extended rule defines "received, as recorded … whether or not … signed". This is inert wherever the clamp does not bind.
  - O-G3j is kept.
- **cancellation_refund**
  - The offset is now "held back … the held-back amount staying on this premium account for that balance" (L1989). The account residue left after the refund is now what the rule states. This partly closes O-G7/O-1-3 for the held-back amount.
  - The payment-method charge "kept from the refund" also stays on the account as a credit that no entry records. That residue remains (O-G7 kept).
  - Interest days use the "as recorded on the request whether or not it had been signed by then" date ↔ `request_received_on` = `created_at`. The R-1-1 ambiguity is removed at the rule level; see the task 1 file.
- Pattern O-G4 (baseline sentence plus tiered sentence) is kept by design.

### action_binding_and_uuids (revision_2)

The tool module is unchanged (`6d61732d…`). Revision_1's conclusion holds: six distinct tools, one per policy, independent uuid8s, docstrings that name no other tool or order, and bodies that check nothing. O-G5 is kept.

### prerequisite_graph (revision_2)

| blocked | problem | kind | gate | form | policy_source verbatim in own rule? |
| --- | --- | --- | --- | --- | --- |
| renewal_term | renewal_indication | **state_gate** (was value_input) | `flood_policies.indicated_renewal_premium` | state | yes, L1250 |
| renewal_payment | renewal_term | value_input | `new_term_premium` (exists, L1462) | state | yes, L1434 |
| cancellation_credit | increase_premium | value_input | `addl_billed` (exists, L1841) | state | yes, L1808 (reworded "… with additional premium due") |
| cancellation_refund | cancellation_credit | value_input | `credits_posted` (exists, L2017) | state | yes, L1988 |

- The graph is still two acyclic chains. Every `resolved_by` is the depended-on policy's target tool.
- term ← indication is re-declared `state_gate`, and its `effect` now says outright that "where the capped premium is the smaller figure the indicated premium's exact value does not move the result". This is honest (**O-0-1 closed** at the charter level).
  - **N-G4 (observation)**: the `gate` names a record field, not an eligibility id. Extended policies carry no `eligibility` block, so no eligibility id exists to point at.
- Each chain now has 1 value_input edge for n = 2 prerequisite problems, which meets the floor max(n−1,1) = 1.
- Conditions:
  - payment ← term no longer adds the policy fee. **O-G6a closed.**
  - refund ← credit no longer adds "not pending signature". **O-G6b closed.**
  - credit ← increase: the sentence now reads "every limit increase recorded on the policy with additional premium due", matching the condition's `premium_direction additional`. **O-G6c closed.**
- **N-G1 — SOURCE-POLICY RED (pre-existing since revision_1; missed by the revision_1 audit; bears on task 0)**
  - Symptom: the payment ← term edge's `effect` reads "The binding new_term_premium changes from zero (no charge for the new term) to the renewal term premium charged by the renewal …" (L1450–L1451).
  - Root cause: the binding is `new_term_premium: SUM('flood_billing', 'amount', event_type='flood_premium_billed', term_effective_date=F('effective_date'))` (L1462). Before the renewal, `F('effective_date')` is the *expiring* term's start, and that term's premium charge is on the account.
  - Evidence: on task 0's opening world, `effective_date` = 2025-09-03, and `flood_billing.2d7adc7c…` (term_effective_date 2025-09-03) makes the binding equal the expiring charge, not zero.
    - The edge's `condition` has the same flaw. "a flood_premium_billed entry whose term_effective_date equals the policy's current effective_date" is literally **true** on that opening world. Only its parenthetical "(the new term)" makes it false.
  - Consequence: two passages of the structured policy give different pre-resolution values of the same binding: zero by `effect`, the expiring term's charge by `compute`. The policy sentence the agent reads (L1434, "the premium charge for the new term") is unaffected, and no scored value changes. The per-task demonstration is in `0.md`.
  - Affected: `flood_ext_renewal_payment.prerequisite[0].effect` and `.condition`.

### prerequisite_sentences (revision_2)

Four-point test re-run:

1. **term ← indication**: L1250 is unchanged. PASS (single write: record_flood_renewal_offer).
2. **payment ← term**: L1434 is unchanged. PASS (single write: renew_flood_policy).
3. **credit ← increase**: "… for every limit increase recorded on the policy with additional premium due." It has "only after", a record-visible state (an endorsement with `premium_direction` additional plus a `flood_additional_premium` whose `source_endorsement_id` is it), no names, and a strength that now matches the condition. The single write is bill_flood_increase_premium. PASS.
4. **refund ← credit**: L1988 is unchanged. PASS.

- No other ordering sentence appears in any extended rule. The new tenure, late and electronic sentences relate records to clocks only. No depended-on rule restates its dependent's sentence.

### override_declarations (revision_2)

- **renewal_indication**: unchanged from revision_1, except that the S5 split is now explicit (O-G1 closed).
- **renewal_term**
  - It supersedes only the smaller-of/cap half of S5, declared.
  - The cap percentage is now "the tier's renewal rate cap percentage less a reduction". This handles the quantity that clause governed, so it is covered by that declaration.
  - The minimum floor on the term premium after credits is unchanged from revision_1 (absent). Its consequence is checked per task.
- **renewal_payment** (`overwrite: []`): no base sentence fixes the payment amount. The balance, the per-day late charge and the electronic credit override nothing. PASS.
- **increase_premium**: unchanged.
- **cancellation_credit**: S5 and S6 are superseded, declared. S4 is inherited (see N-G2).
- **cancellation_refund**: billing S5 is superseded, declared.
- **No undeclared override found.**

### factor_ladders (revision_2)

- **renewal_indication**: unchanged, 6 factors (1 method, 5 parameter). O-G8a/b/c are kept, as revision_1 described.
- **renewal_term**: 5 factors, 1 method and 4 parameter.
  - `renewal_cap_tenure` (parameter; tier cap −7 / −3 / tier cap) is multi-source (counted tenure × 60-month claim window). It is now distinct on every variant: Contents Only/Essential 11/15/18, Standard/Plus 8/12/15, Premier 5/9/12, High Value 3/7/10. The High Value/Premier inversion is gone. **O-G8d closed.**
  - `cap_tenure_start` (**method**; start = HomeGuard original effective / last paid claim / flood original effective) replaces `cap_claim_window`.
    - The tiers pick the start date from three different records, not a charter constant, so it is a genuine method (the same class as `refund_interest_anchor`).
    - Tier 1 is multi-source (HomeGuard × claim ledger) and cross_difficulty home. Tier 2 reads the claim ledger. The tiers are disjoint by the lookback-payment condition, and each is stated in L1251 and implemented in `tenure_months`.
    - Its baseline (the flood policy's original effective date) is the fall-through tier, which `baseline.rule` does not state (the O-G8f pattern; kept).
    - **F-G1 closed structurally.**
  - `prompt_payment_credit`, `claim_free_credit` and `umbrella_account_credit` are unchanged. The umbrella credit is now net of removals.
- **renewal_payment**: 4 factors, 1 method and 3 parameter.
  - `earlier_balance_treatment` is removed. The balance is now in the baseline for every payer, less the third-party carve-out, and is no longer a factor. **F-G2 closed structurally.**
  - `late_renewal_charge` (**method**; per-day accrual × days / one flat amount / none): the per-day tier changes the algorithm (linear in days) against a constant. That is honest. It is distinct and stated in L1436.
  - `pay_in_full_discount` (3/1/0), `member_dividend_lines` (4/2/0, cross_difficulty home+umbrella) and `electronic_payment_credit` (parameter 1.5/0.5/0; multi-source: EFT/card × check) are distinct.
  - The baseline rule is self-sufficient: premium + fee + balance.
- **increase_premium, cancellation_credit, cancellation_refund**: structure unchanged from revision_1. The ladder wording now anchors on "as recorded on the request". Counts are 6 (1M/5P), 5 (2M/3P) and 4 (2M/2P).
- O-G8e (refund card charge, backdating retention) is kept as an observation.
- Counts: every policy is within 4–6 factors, ≥2 parameter and ≥1 method, with no mislabelled or collapsed ladder found.

### findings (revision_2, pre-reveal)

| round-1 item | status after re-derivation (charter level) |
| --- | --- |
| F-G1 / R-0-1 | **closed** structurally (cap_tenure_start is an honest method; weight shown in 0.md) |
| F-G2 / R-0-2 | **closed** structurally (collapsed ladder removed; late_renewal_charge is an honest method; 4 factors) |
| R-0-3, R-1-2 | GT-side proof text; checked after reveal in the task files |
| R-1-1 | rule wording now excludes the signed-date reading; confirmed per task in 1.md |
| O-G1, O-G3a, O-G3d, O-G3e, O-G3g, O-G3h, O-G6a, O-G6b, O-G6c, O-G8d | closed |
| O-G3b | **partly open** (the dwelling CFIELD is unfiltered by address; inert) |
| O-0-1 | closed at the charter level (state_gate with an honest effect) |
| O-G7 | partly closed (refund hold-back now stated); the payment residue and the kept method charge remain |
| kept, as stated by the rework | O-G2, O-G3c, O-G3f, O-G3i, O-G3j, O-G4, O-G5, O-G8a/b/c/e/f |

- New: **N-G1 SOURCE-POLICY RED** (see prerequisite_graph). N-G2…N-G6 are observations.

## closing_checklist (revision_2)

Written after the round-2 reveals. Everything in § revision_2 above this heading was frozen before them (sha256 `e96ec0ae…`).

**Status: NOT CLOSED.**

| task | policy self-consistency | problem tree | factors | unique solution | blind = GT? |
| --- | --- | --- | --- | --- | --- |
| 0 | **SOURCE-POLICY RED** (N-G1) | PASS | PASS | scored solution PASS; **SOURCE-TASK RED** on proof text (R2-0-1) | yes, every write and parameter |
| 1 | PASS | PASS | PASS | PASS | yes, every write and parameter |

**Round-1 RED closure:**

| round-1 RED | status |
| --- | --- |
| F-G1 / R-0-1 | closed |
| F-G2 / R-0-2 | closed |
| R-0-3 | closed |
| R-1-1 | closed |
| R-1-2 | closed |

**Round-1 observations the rework claimed closed:**
- Verified closed: O-G1, O-G3a, O-G3d, O-G3e, O-G3g, O-G3h, O-G6a, O-G6b, O-G6c, O-G8d, O-0-1, O-1-2, O-1-4.
- **Not fully closed:**
  - O-G3b: the dwelling CFIELD is still unfiltered by address.
  - O-0-3: the new near-miss does not move a tier.

**Kept, as the rework stated:** O-G2, O-G3c, O-G3f, O-G3i, O-G3j, O-G4, O-G5, O-G7 (partly closed for the refund hold-back), O-G8a/b/c/e/f, O-1-1.

**New in round 2:**
- **N-G1**, SOURCE-POLICY RED: the payment ← term edge's `effect`/`condition` contradict `compute` on the pre-renewal value. The flaw was present since revision_1 and the revision_1 audit missed it.
- **R2-0-1**, SOURCE-TASK RED: a stale figure in task 0's `design_rationale`.
- Observations: N-G2 (two "received" anchors between base S4 and the extended rule), N-G3 (late-charge "those calendar days"; the second reading is incoherent), N-G4 (a state_gate `gate` names a field), N-G5 (electronic credit ignores mortgagee_check), N-G6 (increase-companion compute excludes pending HomeGuard states), N-1-1 (stale sentence quotations in task 1).

**Other checks:**
- Coverage and scope: disjoint and complete. The trees each have 2 prerequisites, ≥1 value_input edge and one user write, and are acyclic. Every factor bears weight against an honest baseline, and no baseline gives gold.
- Instantiation gates: the round-2 snapshot from the brief is cited, 7 green, traceability deferred. The auditor did not re-run them.

## revision_3

### charter_global_frozen (revision_3)

- Freeze time: 2026-09-25T00:05Z. Same auditor. Written before any round-3 GT reveal; nothing here is derived from a round-3 reveal.
- Inputs, re-hashed and matching the orchestrator's round-3 hashes:
  - `flood.extended.yaml` = `3a59c3210c4828d898549bddc28aa199448979260df69faa8a2b70de1d079ed9`: **changed** (revision_2 was `a477bad1…`).
  - `task_tools.py` = `6d61732d…`: unchanged.
- The base copy is still verbatim (trailing blank line only). Each charter-global section is re-derived below.
- Method: no copy of the revision_2 charter was kept on disk, so the change set was not established by a file diff. It was established by:
  - reading every line the round-2 findings and observations named;
  - a structural dump (params, overwrite clauses, prerequisite edges, factor ids, labels, cross_difficulty and baseline params of all six policies), which is identical to revision_2;
  - re-reading the full rule and compute text of the renewal_term, cancellation_refund and renewal_indication policies, and the full rule text of the other three, against my revision_2 reading.
- A copy of this charter is kept in the auditor scratchpad (`audit_r3/charter_r3.yaml`) for any later round's diff.
- Entry conditions: the round-3 gate snapshot came with the brief (7 green; traceability deferred). The views were rebuilt: `0.view.json` `58a15704…` (changed) and `1.view.json` `8770f41a…` (unchanged).
- contamination_disclosure: the auditor saw round-1 and round-2 GT for both tasks. Round-3 derivations are blind only where the rule or seed changed since round 2, which here means the task 0 electronic-payment credit and the payment amount. No `tasks/*.json` was opened in round 3 before the freeze.

### change set found (revision_2 → revision_3)

1. `flood_ext_renewal_payment.prerequisite[0].condition` now reads: "The policy's effective_date is the start of the new term (the expiring term's expiration date) and flood_billing carries a flood_premium_billed entry whose term_effective_date is that date; while the policy still shows the expiring term, the only premium charge matching its effective_date is the expiring term's own charge, which is not a charge for the new term."
2. `flood_ext_renewal_payment.prerequisite[0].effect` now reads: "Before the renewal the binding new_term_premium reads the premium charged for the term the policy's effective_date names, which is the expiring term's own charge (already billed and paid); the renewal moves effective_date to the new term's start date and posts that term's charge …".
3. renewal_indication `dwelling_same_address` now filters `property_address=F('property_address')`.
4. renewal_payment late-charge wording (rule, compute_basis, ladder): "the charge is the late daily charge multiplied by every calendar day from the new term's start date to the payment date". The compute is unchanged.
5. renewal_payment electronic credit: the rule, basis and ladder now say "the named insured's own premium payments". The compute adds `payer='insured'` to both counts.
6. increase_premium `home_here_live_on_request` now also accepts status `pending_cancellation` / `pending_nonrenewal`.
- No other rule, compute, param, factor, prerequisite or overwrite text was found changed.

### policy_conflict_scan / override_declarations (revision_3)

- Changes 1–6 touch no subject, trigger, target tool, overwrite clause or cross-category boundary.
- Revision_2's conclusions are re-affirmed on the revision_3 text:
  - no overlapping subjects;
  - the S5 split is explicit;
  - no undeclared override;
  - scopes are disjoint and complete.
- Kept as before: O-G2.
- N-G2 is kept as an observation. Base S4's clamp still anchors on "the date the signed request is received", while the extended rules use "received, as recorded on the request whether or not it had been signed by then". This is inert wherever the 30-day clamp does not bind.

### rule_compute_equivalence (revision_3)

- **Change 3**: `dwelling_same_address` now matches "a LandlordGuard policy of the customer is in force at the same property address". **O-G3b closed.**
- **Change 4**: the rule now says "every calendar day from the new term's start date to the payment date", which matches the compute `K('late_daily_charge') * days_past_term_start`. The excess-days reading no longer has a textual basis. **N-G3 closed.**
- **Change 5**:
  - The rule restricts all three tiers to "the named insured's own premium payments", and the compute counts `payer='insured'` payments by eft/card against check.
  - A mortgagee's `mortgagee_check` is now outside the counted set by the rule's own words.
  - An insured's payment by a method other than eft/card/check (only `none`, which the payment tool describes as "a real payment never uses") is not counted by the compute. Under the rule it would make "all made by EFT or card" false.
  - That is a residual gap, and it is inert: no such row exists.
  - **N-G5 closed.**
- **Change 6**: the rule says "bound on or before that date and not cancelled or expired by it". The compute now accepts in_force, pending_cancellation and pending_nonrenewal, or a closed date after the request. That is equivalent for every lifecycle state in the home charter (bound/in_force/pending_*/cancelled/expired). One edge remains: a HomeGuard still `bound` (not yet effective) on the request date fails the status test although the rule's "bound on or before that date" admits it. Inert: no such row. **N-G6 closed** (residual noted).
- The O-G3c duplicates, O-G3f, O-G3i and O-G3j are kept, as the rework stated.

### action_binding_and_uuids (revision_3)

The tool module is unchanged. Revision_1's conclusion holds. O-G5 is kept.

### prerequisite_graph / prerequisite_sentences (revision_3)

- The edges, kinds, gates, policy_sources and resolved_by are identical to revision_2. The graph is two acyclic chains. Every policy_source is verbatim in its own rule. All four sentences pass the four-point test with a single resolving write each.
- **N-G1**, payment ← term, re-tested against the new text:
  - The condition now requires the policy's effective_date to be the new term's start (the expiring term's expiration date) *and* a premium charge for that date. On any pre-renewal policy the first clause is false: effective_date is the expiring term's start. The literal condition is therefore unmet at the opening, and it agrees with the sentence "the premium charge for the new term".
  - The effect now states that the binding reads the expiring term's own charge before the renewal. That agrees with `compute` `new_term_premium` (L1462).
  - The two passages no longer disagree. **N-G1 closed.**
- N-G4 is kept as an observation: the state_gate `gate` names a record field, and extended policies carry no eligibility id.

### factor_ladders (revision_3)

- Structure is identical to revision_2: 6/5/4/6/5/4 factors, ≥2 parameter and ≥1 method each, with the same labels and cross_difficulty.
- `electronic_payment_credit` is now restricted to the named insured's own payments. Its tiers (1.5 / 0.5 / 0) stay distinct, and the condition divides insureds who reach the payment by their payment history, which is a real split.
- `late_renewal_charge` is unchanged in outcome.
- Kept as before: O-G8a/b/c/e/f.

### findings (revision_3, pre-reveal)

| round-2 item | status (charter level) |
| --- | --- |
| N-G1 (SOURCE-POLICY RED) | **closed** (condition and effect now agree with compute) |
| R2-0-1 (SOURCE-TASK RED, proof text) | GT-side; checked after reveal in 0.md |
| O-G3b | closed |
| N-G3 | closed |
| N-G5 | closed (residual inert gap on a `none` method) |
| N-G6 | closed (residual inert gap on a still-`bound` HomeGuard) |
| O-0-3 | seed-side; judged in 0.md |
| N-1-1 | GT-side; checked after reveal in 1.md |
| N-G2, N-G4 | kept as observations (rework answered; no consequence on either world) |
| O-G2, O-G3c, O-G3f, O-G3i, O-G3j, O-G4, O-G5, O-G7, O-G8a/b/c/e/f, O-1-1 | kept |

- No new charter-level defect was found.

## closing_checklist (revision_3)

Written after the round-3 reveals. Everything in § revision_3 above this heading was frozen before them (sha256 `a7e2d7e3…`).

**Status: CLOSED.** Every task passes all four relationships:

| task | policy self-consistency | problem tree | factors | unique solution | blind = GT? |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | yes (the payment was re-derived blind under the new seed) |
| 1 | PASS | PASS | PASS | PASS | yes (regression check) |

**RED history:**

| RED | raised | closed |
| --- | --- | --- |
| F-G1 / R-0-1 | revision_1 | revision_2 |
| F-G2 / R-0-2 | revision_1 | revision_2 |
| R-0-3 | revision_1 | revision_2 |
| R-1-1 | revision_1 | revision_2 |
| R-1-2 | revision_1 | revision_2 |
| N-G1 | revision_2 | revision_3 |
| R2-0-1 | revision_2 | revision_3 |

**Step 4 checklist:**
- **Audit files**: `_difficulty.md`, `0.md` and `1.md` map one-to-one onto the tasks. Revisions 1–3 are appended and no earlier text was edited. Every comparison section carries a PASS at revision_3.
- **Coverage and scope**: all six extended policies are covered; task 0 = renewal indication/term/payment and task 1 = increase/credit/refund. The scopes are pairwise disjoint over the whole tree. Task tools are closed, each with an independent frozen uuid8.
- **Trees**: each has 2 prerequisite problems, 1–2 value_input edges (floor 1) and one owner=user write. The difficulty graph is two acyclic chains.
- **Factors**: every computation has a self-sufficient baseline that gives a definite number different from gold, and 4–6 factors with ≥2 parameter and ≥1 method. Each task has ≥1 multi-source and ≥1 cross-difficulty factor (home, umbrella). Every ladder has three distinct tiers stated in its rule, and every factor bears weight on its task's world.
- **Instantiation gates**: the round-3 snapshot from the brief is cited (7 green; traceability deferred until the KB is published). The auditor did not re-run them, per the brief.

**Observations carried** (none is a red light):
- Charter: O-G2, O-G3c, O-G3f, O-G3i, O-G3j, O-G4, O-G5, O-G7 (payment-adjustment residue and refund card-charge residue, neither acted on by any rule), O-G8a/b/c/e/f.
- New in rounds 2–3: N-G2, N-G4.
- Residual inert gaps from the N-G5 and N-G6 fixes.
- Task-level: O-0-2 and O-1-1.

- Correction note: the revision_3 frozen section says a charter copy is kept at `audit_r3/charter_r3.yaml` in the auditor scratchpad. That copy was removed at the end of the audit, under the brief's rule to remove the auditor's own temp files. A later round should diff against sha256 `3a59c3210c4828d898549bddc28aa199448979260df69faa8a2b70de1d079ed9` using another retained source.
