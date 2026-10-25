# Policy-task audit — balloon_maturity_and_title / charter-global

## charter_global_frozen

- Freeze time: 2026-10-15T20:18Z (written before any task's GT was revealed; nothing in the sections above `## closing_checklist` comes from a revealed GT).
- Auditor: independent erl-task-policy-audit agent (round 1). It did not write these artifacts.
- Freeze hashes (sha256 prefix, recomputed by the auditor; they match the coordinator snapshot):
  - `tasks/balloon_maturity_and_title/balloon.extended.yaml` 684503b134710695
  - `tasks/balloon_maturity_and_title/task_tools.py` db364d3df00ce2aa
  - masked views `.audit_views/policy/balloon_maturity_and_title/0.json` 65a519e31aa69587 and `1.json` 7acd75e473b4b3be
- Fields read: the blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/balloon.yaml`, and one schema/field-meaning lookup in `products/retail.yaml`), the extended charter (base copy plus `extended_policies`), `task_tools.py`, the DSL sandbox `skills/erl-task-instantiate/scripts/check_compute.py` (to learn what `within_months`, `MONTHS`, `DAYS`, `CFIELD` and `LATEST` mean), and the masked views (`frozen_time`, `user_scenario`, `initial_state` only).
- Fields masked and not read before freeze: everything in tasks/*.json beyond the masked views (`evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`) and `tasks/balloon_maturity_and_title/worklog.md`. No recursive search covered `tasks/*/tasks/`.
- Entry conditions (Step 0): the gate snapshot came with the brief (`.audit_views/policy/balloon_maturity_and_title/snapshot_r1.txt`). check_extended, check_task_tools, replay --check, check_solvability, check_compute, check_grounding and check_cross_fire are all OK. The check_traceability misses are only the unlock tool-name provenance, which is expected before the KB is rendered. validate_scenario is INVALID only because `documents: 0` (pre-render). The masked views and their hashes were supplied. The inputs are complete.
- Base copy: the auditor parsed both files and compared `category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies`. The extended yaml's copy is identical to `blueprint/products/balloon.yaml`.

### policy_conflict_scan

The charter has seven extended policies:

| id | target_tool | computes | trigger | subject | prerequisite |
| --- | --- | --- | --- | --- | --- |
| balloon_ext_return_mileage_charge | bill_excess_mileage_charge_7a491561 (agent) | amount | state_due | balloon_return_charge | [] |
| balloon_ext_return_wear_charge | bill_excess_wear_charge_ce1b5dd4 (agent) | amount | state_due | balloon_return_charge | [] |
| balloon_ext_return_fee | bill_return_fee_2252d2f2 (agent) | amount | state_due | balloon_return_charge | [] |
| balloon_ext_return_balance_plan | pay_return_balance_installment_2f123e0a (user) | amount | on_request | balloon_payment | mileage, wear, fee (state, value_input) |
| balloon_ext_payoff_quote | issue_payoff_quote_72ecc9f3 (agent) | amount | on_request | balloon_payoff_quote | [] |
| balloon_ext_refinance_precondition_payment | pay_refinance_precondition_amount_08a17076 (user) | amount | on_request | balloon_payment | payoff_quote (state, value_input) |
| balloon_ext_balloon_refinance | complete_balloon_refinance_14b47e8c (agent) | refinance_monthly_payment | on_request | balloon_refinance, balloon_terms_modified | payoff_quote (state, value_input), precondition (action, value_input) |

- **Overlapping subjects.**
  - The three return charges share `balloon_return_charge`. Each fixes one fee_type through its own tool (`excess_mileage_charge`, `excess_wear_charge`, `return_fee`). None reads another's output, so they do not conflict.
  - The return-balance payment and the pre-refinance payment share `balloon_payment`. Their scopes are disjoint by contract status: the first is posted only on a `returned` contract, the second only before a refinance, which needs `active` (base refi_status).
- **Eligibility and status.**
  - The return-balance plan's override lets a payment post while the contract is `returned`.
  - The pre-refinance payment keeps the base payable statuses.
  - The refinance's override moves the base days-past-due test onto the held payment.
  - None of these overrides reaches the other policies.
- **Time anchors.** Every history window is "N calendar months ending on the billing/payment/quote/refinance date". The DSL implements this as `0 <= MONTHS(txn_date, NOW) < N` (check_compute.py `_within`). The quote, pre-refinance payment and refinance are all anchored to one handling date: the quote "dated on the payment date" / "dated on the refinance date". All of these anchors are compatible.
- **Terminal states.**
  - Mileage, wear and fee each add their amount to `fees_due_balance`.
  - The plan payment subtracts from it.
  - The pre-refinance payment leaves balances untouched.
  - The refinance re-amortizes and zeroes fees.
  - No two policies write the same field to conflicting values within one tree.
- **Cross-category read boundaries.** Reads touch only the status/date/days_past_due/disposition_fee of lease, retail and preowned holdings. The `cross_category` blocks name exactly the categories that compute calls (EXISTS/CFIELD).
- **Scope exclusivity.** The auditor derived the trees independently. {mileage, wear, fee, plan} form one tree (root: plan) and {quote, precondition, refinance} form another (root: refinance). The two sets are disjoint and together cover all seven policies. GT's charter_scope is compared per task after the reveal.

### rule_compute_equivalence

The auditor swept every compute binding against its `compute_basis` quotation and the rule, in both directions:

- **Mileage.** Each of the following has a verbatim rule sentence, and the rule promises nothing compute omits:
  - insp/sign-in odometer and gap → the "Mileage odometer reading" sentence
  - allowance proration/extension → "Mileage allowance basis", rounded to a whole mile
  - 24-month late count
  - tier ladders
  - lease/retail gaps
  - election lead
  - completed/active rate reductions
  - `MX(0, …)` and cent rounding
- **Wear.** Standing forgiveness, proration (rounded to the cent after multiplying), brand, tenure (`MONTHS/12 ≥ years` is the whole-month anniversary reading of "signed at least N years before"), on-time months (whole months from the late-charged installment's due date to the return date, or 9999 when there was never a late charge), share billed, and the "subtracted together … then the share billed" order all match.
- **Fee.** The waiver/lower-of/tier basis, early reduction, multi-line, payment-record and autopay ladders match, and so does the `MX(0, …)` at the end.
- **Plan.**
  - Return charges are the SUM of the three fee types.
  - Prior fees are `MX(0, fees_due − charges)`.
  - The balance-driven count uses `int()` floor, held between 2 and 4.
  - "The larger is used" is `MX(spread, R·minimum_share)`.
  - The order "collected prior part added, deferral taken off, upfront added" is followed.
  - The result is capped by `MX(0, …)` and by fees_due.
  - All of these match.
- **Quote.** Good-through days, per diem `/100/basis`, the inclusive day count (`DAYS(ipt, NOW) + gtd` equals ipt+1 through the good-through date), pre-maturity days capped at the maturity date, the post-rate ladder, courtesy days off post-maturity days floored at 0, and separate per-diem rounding all match.
- **Pre-refinance payment.** The quote dated NOW, `MX(0, Q − balloon)`, the percentage-point sum on balloon_amount rounded and then credits taken off with `MX(0, …)`, and the sum all match.
- **Refinance.**
  - Q minus SUM of payments dated NOW.
  - The five rate adjustments summed and the APR rounded to 2 dp.
  - The term schedule.
  - The level-payment formula.
  - All of these match.

Gaps (observations, no task consequence demonstrable):

- **G1 — existential rule, first-match compute (decoy-guard class).** The rule quantifies existentially ("a customer holding an active Kestrel lease whose lease_date falls within …", "the disposition_fee of that lease", "accounts showing days_past_due of 0 in two or more … lines", "a … retail contract, now paid_in_full or closed, signed at least …"). Compute reads `CFIELD(cat, field, status=…)`, which returns the **first** matching holding (check_compute.py `CFIELD` → `hs[0]`). The full list of members is:
  - mileage `lease_gap`, `retail_gap`
  - wear `wear_lease_gap`, `wear_retail_gap`, `tenure_years` (closed first, then paid_in_full)
  - fee `fee_lease_gap`, `fee_retail_gap`, `fee_preowned_gap`, and the `disposition_fee` read inside `fee_basis`
  - plan `lease_dpd`, `retail_dpd`
  - quote `current_lines` (3 CFIELD reads)
  - precondition `cp_current_lines` (3)
  - refinance `ri_current_lines` (3)

  A customer with two holdings of one category, one inside the window or current and one not, makes compute and rule disagree. Neither task's world has two holdings of one category (task 0: one lease, one retail; task 1: one retail, one preowned), so no task consequence follows.
- **G2 — boundary count in the refinance term schedule.** "less one further month for every month from term_long_months on" is implemented as `ri_months_in_service − 48 + 1`. At exactly 48 months a reader can also count 0 months "from 48 on", which gives a 1-month term difference. Compare the precondition age ladder's "beyond age_slope_start_months" (`− 22`, exclusive). No task sits at ≥ 48 months (task 1 is at 36), so this is an observation.
- **G3.** The pre-refinance standing tier reuses `min_down_payment_pct`. That is an origination parameter whose schema meaning is "percent of the selling price"; here it is a refinance down-payment percentage of balloon_amount. This is a semantic stretch only; the rule states it outright.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (seven distinct tools).
- No share tool writes `balloon_transactions` or `balloon_contracts`. The only shared writes are `verify_customer_identity` and `transfer_to_human_agent`. So each state the charter waits on is brought about by exactly one tool.
- **uuid8s:** 7a491561, ce1b5dd4, 2252d2f2, 2f123e0a, 72ecc9f3, 08a17076, 14b47e8c. They are distinct, share no common prefix or tail, and show no sequence or adjacency pattern. They are independently generated.
- **Tool bodies.** No tool reads a policy figure or checks status, eligibility or a prerequisite. Each one books the row and adjusts balances exactly as its docstring states. Docstrings carry format descriptions only and no example values, so there is no gold leak.
- **Observation O-T1 (check 3, docstring ordering words; consequence not demonstrable):**
  - `pay_refinance_precondition_amount_08a17076`'s docstring reads "the amount required **ahead of** refinancing the balloon … holds it on the contract **toward the refinance**".
  - `complete_balloon_refinance_14b47e8c`'s docstring reads "any funds held on the contract toward the refinance are applied by this booking".

  Both describe the sequence pre-refinance payment → refinance at the tool layer. The blocked rule's action-form sentence already names that action ("…until the customer has made the payment Kestrel requires before a balloon refinance"), so the docstrings make the hop no easier to find. Recorded as an observation.
- **Observation O-T2.** The refinance tool zeroes `fees_due_balance` without booking a `balloon_fee_payment` entry. Base balloon_payment_posting says "When a payment carries a fee portion, that portion is booked as a fee payment against fees due", and the precondition override says the held payment "is applied when the refinance is booked … then fees due". The terminal fee-payment row the base implies is absent. No scored parameter depends on it.

### prerequisite_graph

- `prerequisite` is filled in everywhere. The mileage, wear, fee and quote policies have `[]`.
- Edges: plan→{mileage, wear, fee}; precondition→quote; refinance→{quote, precondition}. Every `problem` is an extended policy id in this file, never base and never self. The graph is acyclic.
- Every `policy_source` is a verbatim sentence of that policy's own `rule` (checked by string search):
  - plan: "The return balance payment is fixed only after the excess mileage charge for the return stands billed on the contract." / "The return balance payment is not fixed until the excess wear charge for the return stands billed on the contract." / "Before the return balance payment is fixed, the return fee for the return must stand billed on the contract."
  - precondition: "The pre-refinance payment is not fixed until a payoff quote dated on the payment date stands on the contract."
  - refinance: "The refinance installment is fixed only after a payoff quote dated on the refinance date stands on the contract." / "The refinance installment is not fixed until the customer has made the payment Kestrel requires before a balloon refinance."
- `form` and `fallback_reason`: there is one action-form edge (refinance←precondition), and it carries a fallback_reason. Every other edge is state form.
- `kind`/`gate`: every edge is value_input, and each gate is a binding of the blocked policy's compute (`mileage_billed`, `wear_billed`, `fee_billed`, `cp_quote_amount`, `ri_quote_amount`, `paid_on_refinance_date`). Each `resolved_by` is the depended-on policy's target_tool, and that tool's effect (a new `balloon_return_charge` row of the named fee_type / a `balloon_payoff_quote` row dated today / a `balloon_payment` row dated today) is exactly what the binding's SUM/LATEST reads.
- `condition` wording matches the sentence's strength.
- **Finding C-P1 (SOURCE-POLICY RED, authoring-viewpoint text in `prerequisite`):** refinance edge `fallback_reason` reads "…every ordinary payment posting **in this difficulty** leave entries of the same kind…" and "The write that resolves this edge…". `prerequisite` is general charter text. "this difficulty" and "the write that resolves this edge" are authoring-viewpoint phrasing, not business language, and check 7 makes that a red light outright. Location: `balloon_ext_balloon_refinance.prerequisite[1].fallback_reason`. It bears on task 1 only as charter text, not on any scored value.

### prerequisite_sentences

Four-point test for each edge:

| edge | connective | waited-on (form) | no tool/id/snake_case | strength = condition | single writer |
| --- | --- | --- | --- | --- | --- |
| plan←mileage | "only after" | "the excess mileage charge for the return stands billed on the contract" (state; table words: return charge, excess mileage) | yes | yes | bill_excess_mileage_charge only |
| plan←wear | "not … until" | "the excess wear charge … stands billed" (state) | yes | yes | bill_excess_wear_charge only |
| plan←fee | "Before … must" | "the return fee … stand billed" (state) | yes | yes | bill_return_fee only |
| precondition←quote | "not … until" | "a payoff quote dated on the payment date stands on the contract" (state) | yes | yes | issue_payoff_quote only (no share tool books quotes) |
| refinance←quote | "only after" | "a payoff quote dated on the refinance date stands on the contract" (state) | yes | yes | issue_payoff_quote only |
| refinance←precondition | "not … until" | "the customer has made the payment Kestrel requires before a balloon refinance" (action) | yes | yes | pay_refinance_precondition_amount only |

Derivations, each with a single reading:

- **Plan edges.** "Return charge … excess mileage/wear/return fee … billed" leads to the policy whose rule "sets the excess mileage charge billed once a balloon vehicle has come back…", and likewise for wear and fee. Those are three distinct policies with distinct tools.
- **Quote edges.** "Payoff quote … stands on the contract" leads to the only rule that "sets the payoff amount on a customer payoff quote".
- **Action edge.** "The payment Kestrel requires before a balloon refinance" leads to the rule that "sets the payment a customer makes before a Kestrel Advantage balloon refinance is booked". That is a single reading.

Observations:

- **O-S1 (fallback unjustified).** A record-visible state would single the pre-refinance payment out. The tool writes a `balloon_payment` dated today with `interest_applied = principal_applied = fees_applied = 0.00` ("held on the contract with nothing yet applied"; this is the edge's own `condition`). The return-balance payment books `fees_applied = amount`, and base postings apply interest first. So "a payment dated the refinance date stands held on the contract with nothing yet applied" was available as a state-form wording.
- **O-S2 (second wording in the blocked rule).** The refinance rule's override sentence "…the days-past-due condition is met when the payment the customer made before the refinance, held on the contract, covers every amount due other than the balloon installment, since that payment is applied when the refinance is booked…" restates the same dependency a second time. It is consistent with the edge and no second reading results.
- **O-S3 (the depended-on rule names the dependent).** The precondition rule's declared override text says the payment "is held on the contract … and is applied when the refinance is booked". This states, in the depended-on policy, the same order as the declared edge. It grounds no new edge and no second order.
- **Base rules.** No base rule grounds a tree edge. Base balloon_refinancing "any other amount due must be paid separately before the refinance" is a cross-problem order in base. The extended refinance carries its own prerequisite sentence, so this is an observation only.
- No undeclared cross-problem order exists in any extended rule. The mileage, wear and fee rules mention "the return inspection on file" and the vehicle "has come back". Those are base events present in the seed, not extended problems.

### override_declarations

The auditor checked each extended policy sentence by sentence against its `base_policy_refs`.

**balloon_vehicle_return** (refs from mileage, wear, fee, plan):
- "Returning the vehicle is the customer's own act…": followed.
- Return eligibility, deadline and counting: followed (not touched).
- "On return the balloon balance is satisfied … every regular installment must already be paid": followed.
- "The return inspection records the odometer…" and "excess_miles is the inspection odometer less…": replaced, declared in mileage `overwrite[0]` (the superseded_clause is a verbatim base substring). The sign-in odometer tier deviates from "inspection odometer" and is covered by that declaration.
- "The excess wear charge is wear_assessed_amount less return_wear_waiver_cap…": declared in wear.
- "The return fee is return_option_fee … waived when the customer signs a new Kestrel retail contract or lease within return_fee_loyalty_days…": declared in fee. The replaced_by changes "signs a new" to "holds an active … dated within" and adds pre-owned, explicitly.
- "Return charges can be billed only while … returned" and the dispute-period sentences: followed.
- "…charges are due return_charges_due_days calendar days after billing…": declared in plan `overwrite[1]` for plan charges only. "The account closes when they are paid" and charge-off: kept.

**balloon_payment_posting** (plan, precondition):
- S1 payable statuses: declared by plan (returned allowed); followed by precondition (active).
- S2 cutoff: followed. Both tasks' frozen times are before 20:00 CT on a business day (Wed 2026-10-14 09:20 CT; Thu 2026-10-22 13:05 CT).
- S3 allocation order: declared by precondition (held, then interest→fees→principal at booking). Plan says "applied to fees due" without naming S3 (observation O-OV1). On a `returned` contract, principal_balance is 0.00 and nothing is past due, so S3's formula gives interest 0, installments_due 0 and fees_applied = min(fees_due, amount). That is the same result, so no consequence.
- S7 channel fee: phone_ivr_ach is 0.00 in every tier, which agrees with the tools.
- S9 certified funds: not relevant (both seeds have it empty).
- S10 fee-payment booking: see O-T2.

**balloon_reinstatement_and_redemption** (plan, precondition; shared subject `balloon_payment`): every sentence governs reinstatement/redemption after repossession. Nothing is touched, and both are followed.

**balloon_payoff_and_refunds** (quote):
- S1 status: followed.
- S2 good-through: declared.
- S3 per diem/payoff: declared. The base prose omits "/100" but the base formula has it, and the extended text matches the formula.
- S4 funds received: followed. The rest is about refunds and is not touched.

**balloon_refinancing** (precondition, refinance):
- S1 status, S2/S3/S4 windows, late-charge cap, S8 re-amortization effects and S9 "only once": followed.
- S5 days-past-due, S6 amount refinanced and S7 term/APR: each declared in refinance `overwrite`.
- The precondition's new down payment adds a payment requirement that no base sentence governs, so it is not an override.

There are no anonymous intermediate factors, 0/1 multipliers or dropped base branches. No author note calls base output a "wrong value".

### factor_ladders

Counts per policy (`parameter`/`method`):

| policy | factors |
| --- | --- |
| mileage | 6 (4/2) |
| wear | 6 (5/1) |
| fee | 5 (4/1) |
| plan | 5 (4/1) |
| quote | 5 (4/1) |
| precondition | 5 (4/1) |
| refinance | 6 (5/1) |

Structure:
- Every ladder has 3 tiers, pairwise disjoint as stated, each in the rule's prose and implemented in compute.
- Every `decides` is a binding, not `result`, and binding sets within a policy are disjoint.
- Every factor's fall-through equals its `baseline`. Each `baseline.rule` is made of sentences of the rule, uses the params it names and is self-sufficient.

Multi-source factors (conjunction over distinct records): mc_tolerance_miles, wc_standing_forgiveness, wc_share_billed, fc_payment_record, rp_plan_length, rp_prior_fee_share, rp_minimum_share, rp_relationship_deferral, qt_relationship_courtesy, cp_down_standing, cp_relationship_credit, ri_relationship_rate, ri_completed_loans.

`cross_difficulty`:
- lease: mc_return_to_brand, wc_return_to_brand, fc_fee_basis, fc_multi_line, rp_relationship_deferral
- retail: mc_rate_relationship, wc_tenure_credit, qt_relationship_courtesy, cp_relationship_credit, ri_relationship_rate
- preowned: ri_completed_loans

Method labels: mc_odometer_reading picks which reading enters the subtraction (min-of-two / sign-in / inspection). That is closer to an input selection than an algorithm, so it is recorded as observation O-L1. Every other method factor is honest (proration vs extension formula vs flat; waive / lower-of / tier fee; balance-driven count vs fixed count vs one payment; good-through anchor; sliding vs flat vs none add-on; sliding vs fixed-cut vs max term).

Realism and distinctness. **Finding C-F1 (SOURCE-FACTOR RED, unreal ladders: risk-inverted or dead tiers).** Listed as one class so one rework can close all members:

1. **wc_standing_forgiveness** (wear). Ladder: Tier 3/2/1/1+ with a clean record → `wear_forgiveness_preferred` = 500; fall-through (a returned payment, or fewer than 10 payments) → `return_wear_waiver_cap` for the tier. Variants: Tier 1 cap = 500.0 and Tier 1+ cap = 750.0.
   - A Tier 1 contract gets 500 on the preferred tier and 500 on the fall-through, so the two tiers select the same value.
   - A Tier 1+ contract gets 500 with a clean record and **750 with a returned payment**, so the delinquent customer is forgiven more.

   No lender publishes a "reward" for a clean record that is smaller than its penalty-tier default.
2. **rp_minimum_share** (plan). The preferred tier (Tier 2/1/1+, no late charge in 24 months, 0.20) can never change the result on any world:
   - Those contracts are on rp_plan_length's balance-driven tier (n ∈ [2,4], so spread ≥ 0.25·R > 0.20·R) or, with a returned payment, on the one-payment tier (spread = R). So `MX(spread, 0.20·R) = spread` always, and substituting the baseline 0 never changes the value.
   - The standard tier is also inert for Tier 4 (n = 2, so 0.50·R > 0.35·R).
   - The fall-through ("no minimum share") goes to the riskier records: Tier 3/4 with two or more late charges, Tier 5, and Tier 1/2/1+ with any late charge. Example: a Tier 3 contract with R = 1,200 and no returned payment pays ≥ 420.00 now with one late charge but 300.00 with three. That is an inverted risk treatment.
3. **mc_tolerance_miles** and **wc_share_billed** (same cross-tier inversion). "every other contract, including … a Tier 2, Tier 1 or Tier 1+ contract with any late charge in those months, has no tolerance miles" / "is billed the whole chargeable wear", while a Tier 3/4 contract with one late charge gets 500 miles / is billed 0.75. Example: a Tier 1+ contract with one late charge in 24 months is forgiven 0 miles while a Tier 4 contract with the same one late charge is forgiven 500. The same holds for share billed (1.00 vs 0.75). No lender gives its best-credit tier harsher lease-end treatment than its subprime tier for the same payment record.
4. **cp_down_standing** (precondition). The tier-2 condition "Tier 4 or Tier 5 **with at most two balloon late charges** in those months" contains a part that holds of every Tier 4/5 customer who reaches this write. The payment is made only before a refinance, and base balloon_refinancing (kept by the refinance override: "balloon_msr_late_charges_12m must still not exceed refinance_max_late_charges_12m for the tier") caps late charges at 1 (Tier 4) and 0 (Tier 5). The fall-through for Tier 4/5 with 3+ late charges (0 points, lighter than the 10/15 points the cleaner Tier 4/5 records carry) is inverted and also unreachable.

Each member's consequence is demonstrated above on a constructible world. Whether it costs a given task is decided in that task's file.

Other realism observations (no RED):
- **O-R1.** qt_post_maturity_rate charges refinance_apr (e.g. Tier 2: 7.99) on post-maturity quote days once a refinance election is on file, which is above the contract APR the fall-through uses (Tier 2 rate-sheet 7.24–7.99). Charging a rate the customer has not yet contracted for, before any refinance is booked, is unusual under a RISC. It is defensible only as a refinance effective from maturity, so it is recorded as an observation.
- **O-R2.** fc_early_return reduces the return fee for returning before maturity. That is a company incentive and plausible.

### findings

| id | verdict | where | tasks it bears on |
| --- | --- | --- | --- |
| C-F1 | SOURCE-FACTOR RED (unreal ladder class; four members above) | wear `factors[wc_standing_forgiveness]` + params/variants `return_wear_waiver_cap`; plan `factors[rp_minimum_share]`; mileage `factors[mc_tolerance_miles]`; wear `factors[wc_share_billed]`; precondition `factors[cp_down_standing]` | task 0 (wear, mileage and plan policies), task 1 (precondition). Per-task cost is in each task file. |
| C-P1 | SOURCE-POLICY RED (authoring-viewpoint phrasing inside `prerequisite`) | `balloon_ext_balloon_refinance.prerequisite[1].fallback_reason` | task 1 (charter text only) |
| G1 | observation (first-match CFIELD vs existential rule; full member list above) | 17 CFIELD reads across all seven policies | none on these worlds |
| G2, G3, O-T1, O-T2, O-S1, O-S2, O-S3, O-OV1, O-L1, O-R1, O-R2 | observations | as listed above | — |

## closing_checklist

Written after both reveals (2026-10-15T20:21:33Z onward). This section sits below the pre-reveal charter-global section, which stays unchanged.

- **Files.** One audit file per task (`0.md`, `1.md`) sits alongside this file. This is the first revision. Task 0's comparison is PASS. Task 1's comparison carries SOURCE-FACTOR RED T1-F1.
- **Coverage and scope.** The 7 extended policies are fully covered. GT charter_scope matches the auditor's independent split: task 0 = {mileage, wear, fee, plan}, task 1 = {quote, precondition, refinance}. The two are pairwise disjoint, and the task tools are closed over GT.
- **uuid8s.** Every uuid8 is independently generated (see action_binding_and_uuids).
- **Trees.**
  - Task 0: 3 prerequisite problems, 3 value_input edges (≥ 2), user write at the root.
  - Task 1: 2 prerequisite problems, 3 value_input edges (≥ 1), user write at the precondition.
  - The difficulty-wide graph is a DAG with no cross-task edges.
- **Factors.**
  - Every computation in both tasks has a self-sufficient baseline, 5–6 factors (≥ 2 parameter, ≥ 1 method), multi-source and cross-difficulty factors per task, and every factor bears weight on its task's world. Each whole-baseline fall-back is definite and differs from gold; all figures matched GT.
  - **Not closed:** charter-wide unreal ladders C-F1 (wc_standing_forgiveness Tier 1/1+, rp_minimum_share's inert preferred tier and inverted fall-through, the cross-tier late-charge inversion in mc_tolerance_miles / wc_share_billed, cp_down_standing's vacuous Tier 4/5 condition).
- **Prerequisite text.** **Not closed:** C-P1, authoring-viewpoint phrasing in a `prerequisite.fallback_reason`.
- **Seed.** **Not closed:** T1-F1, task 1's retail row has next_due_date inconsistent with its own payments_made_count / last_payment_date.
- **Gates.** The instantiation-stage gates were not re-run by the auditor (out of role). The coordinator snapshot r1 is cited as the entry condition. A re-run on the final form is due after rework.
- **Result.** The difficulty does **not** pass the source-layer audit in this revision. Policy self-consistency carries C-P1, factors carry C-F1 (charter) and T1-F1 (task 1); problem trees and unique solutions PASS for both tasks.

task0=PASS task1=SOURCE-FACTOR RED
charter=C-F1,C-P1

## revision_2

### charter_global_frozen (revision_2)

- **Written:** before reading the round-2 worklog closure section or any round-2 task GT field. Auditor: the same independent auditor.
- **Gating:** `tail -1 tasks/balloon_maturity_and_title/worklog.md` = `REWORK round 2: gates 7/7 green`.
- **Gate snapshot:** `.audit_views/policy/balloon_maturity_and_title/snapshot_r2.txt` (2026-10-15T20:41:22Z), produced by the coordinator script. check_extended, task_tools, replay --check, solvability, compute, grounding and cross_fire are OK. check_traceability shows only the unlock tool-name provenance miss (pre-render). validate_scenario is INVALID only on `documents: 0` (pre-render).
- **Hashes:** both shared inputs moved, so every charter-global section is re-derived in full below.

| file | round 1 | round 2 |
| --- | --- | --- |
| `balloon.extended.yaml` | 684503b134710695 | ac29468ae727c921 |
| `task_tools.py` | db364d3df00ce2aa | c39a38c81bb50a54 |
| view `0.json` | 65a519e31aa69587 | 0748c506fa63290b |
| view `1.json` | 7acd75e473b4b3be | cdbe395c8955132f |

- **Base copy:** still identical to `blueprint/products/balloon.yaml`.

### re-derived charter-global checks (revision_2)

**Mechanical sweep** (auditor's own script over the yaml), for all 7 policies:
- Every `compute_basis` quotation is a substring of its rule.
- Every `overwrite.superseded_clause` is a verbatim substring of the cited base rule, and every `replaced_by` sits in the extended rule.
- Every `baseline.rule` sentence is in the rule.
- Every `decides` is a compute binding.
- Every factor's fall-through equals its `baseline`.
- Every `policy_source` is verbatim in its own rule.

**policy_conflict_scan.** Subjects, statuses, anchors and terminal fields are as in round 1. No new conflict was introduced.

New scope clauses in the mileage, wear and fee rules (e.g. "of a customer who holds at most one active Kestrel lease and at most one active Kestrel new-vehicle retail contract … the excess mileage charge of any other customer stays under the base excess-mileage sentence"). Each sits inside that policy's declared `replaced_by`, so the base sentence still governs out-of-scope customers.
- Observation O2-1: compute implements only the in-scope branch. That is the accepted self-naming-scope pattern; both task worlds are in scope.
- Realism: limiting the override to customers with at most one holding per line is administrative, not a pricing tier.

**rule_compute_equivalence.**
- **G1 closed.** Every former first-match read is now either existential (`CFIELD(cat,'days_past_due', status='active', days_past_due=0) == 0` in quote, precondition and refinance; `EXISTS(..., days_past_due=0)` in plan) or behind a scope clause that excludes multi-holding customers (mileage, wear, fee).
- **G2 closed.** The term schedule now reads "one further month for each whole month in service at or beyond term_long_months, term_long_months itself counting as one", which matches `− 48 + 1`.
- **G3 closed.** The Tier 4/5 standing tier now carries its own `down_pct_subprime` 10.0 instead of the origination `min_down_payment_pct`.
- **New:** the ri_late_charge_addon tier-1 condition is now "two or more late charges OR a returned payment". The rule and compute agree (`ri_returned_window` added).

**action_binding_and_uuids.**
- Tools are unchanged in name and uuid8.
- O-T1 closed: the pre-refinance payment docstring now reads "an amount … held on the contract unapplied" and the refinance docstring no longer mentions funds "toward the refinance". A grep for ahead/toward/before/after/first finds nothing.
- O-T2 closed: the refinance tool now books one `balloon_fee_payment` for the fees standing, linked to the latest payment dated today. That is an effect only; it reads fees_due solely to size the entry and gates nothing.
- No tool judges a prerequisite.

**prerequisite_graph.**
- Edges: plan→{mileage, wear, fee} (value_input, state); precondition→quote (value_input, state); refinance→quote (**state_gate**, gate `balloon_transactions.event_type`, a `<table>.<field>` gate the instantiate contract allows); refinance→precondition (value_input, **state**, gate `paid_on_refinance_date`).
- The graph is acyclic. Every `policy_source` is verbatim.
- No action-form edge remains, so there is no `fallback_reason`.
- **C-P1 closed:** the phrase "in this difficulty" and the whole fallback_reason are gone.
- Observation O2-2: the quote→refinance `effect` says "this edge gates the refinance rather than moving its value". "This edge" refers to the declaration itself, not to a task, opening or world; that self-reference is the instance-viewpoint phrasing check 7 bans. Recorded as observation only. Round 1's RED rested on "in this difficulty", which tied general text to the benchmark partition.
- The effect text now states the cancellation the auditor noted as O-1.1, which is accurate.

**prerequisite_sentences.** New state-form sentence: "The refinance installment is not fixed until a payment dated on the refinance date stands held on the contract with nothing yet applied to it."
- It passes the four-point test: the connective is "not … until"; it names a record-visible state; it carries no tool, id or snake_case token; and its strength matches the condition (interest/principal/fees_applied all 0.00 on a payment dated that day).
- **Single writer.** Only `pay_refinance_precondition_amount_08a17076` books a `balloon_payment` with nothing applied. The return-balance tool books `fees_applied = amount`, and base postings apply interest first.
- **Single reading.** The only rule that says a payment "is held on the contract rather than applied" is the precondition rule.
- O-S1 is therefore closed.
- O-S2 and O-S3 remain as observations: the refinance dpd override still speaks of "a payment held on the contract … applied when the refinance is booked", and the precondition rule still says its payment "is applied when the refinance is booked". Both are consistent with the edge, and no second reading follows.

**override_declarations.**
- As in round 1, plus the scope clauses above, which are declared inside each `replaced_by`.
- O-OV1 closed: the plan's `replaced_by` now says the payment "is applied in payment_allocation_order, which on a returned contract carrying no principal and nothing past due places all of it on fees due". That keeps base S3, and the auditor's round-1 computation confirms it.

### factor_ladders (revision_2) and the C-F1 class

- **Member 1, wc_standing_forgiveness: CLOSED.** The ladder is now cap + 250 (Tier 3/2/1/1+ clean), cap + 150 (Tier 4/5 clean), or cap otherwise. Every tier strictly exceeds the fall-through within its own tier. Across tiers, clean customers get Tier 1+ 1,000 > Tier 1 750 > Tier 2/3 500 > Tier 4/5 150. No duplicate value and no inversion.
- **Member 2, rp_minimum_share: CLOSED.** The ladder is now risk-ordered: 0.50 (two or more late charges in 24 months, or a returned payment in 12), 0.35 (exactly one late charge and no returned payment), 0 (clean). The 0.50 tier binds for Tier 1–3 contracts with return charges ≥ 900 and no returned payment (n ≥ 3), so it is not dead. Observation O2-3: the "or a returned payment" disjunct can never bind. Such contracts are already on rp_plan_length's one-payment tier (spread = R ≥ 0.5·R). It is harmless and a weighed condition, not a RED.
- **Member 3, mc_tolerance_miles / wc_share_billed: CLOSED.** The preferred tier is now "Tier 2/1/1+ with at most one late charge" and the fall-through is "Tier 5 or two or more late charges". For any fixed late-charge record, treatment is monotone in credit tier: Tier 1+ with one late charge gets 1,000 miles / 0.50 billed, against Tier 4's 500 / 0.75.
- **Member 4, cp_down_standing: CLOSED.** The ladder is now Tier 4/5 → `down_pct_subprime` 10.0 (no vacuous late-charge clause); Tier 2/3 with at least one late charge → 7.5; Tier 1/1+, or a clean Tier 2/3 → 0. Every condition divides the refinance-eligible population and the outcomes are risk-ordered. cp_down_standing is no longer multi-source (its first tier reads only the tier). Each task's multi-source floor is checked in the task file.
- **Counts per policy** are unchanged (6/6/5/5/5/5/6) and each policy has ≥ 2 `parameter` and ≥ 1 `method`.
- **New multi-source factors:** rp_minimum_share and ri_late_charge_addon (late charge or returned payment).
- O-R1 (post-maturity days at refinance_apr after a refinance election), O-R2 and O-L1 remain observations.

### findings (revision_2)

| id | round-1 verdict | revision_2 |
| --- | --- | --- |
| C-F1 (4 members) | SOURCE-FACTOR RED | closed, all members (above) |
| C-P1 | SOURCE-POLICY RED | closed |
| G1, G2, G3, O-T1, O-T2, O-S1, O-OV1 | observations | closed |
| O-S2, O-S3, O-R1, O-R2, O-L1 | observations | remain observations |
| O2-1, O2-2, O2-3 | — | new observations |

No new charter-wide RED was found.

### closing_checklist (revision_2)

Written after the round-2 reveals.

- **Files.** One audit file per task plus this file. Revision 1 is preserved and revision_2 is appended.
- **Coverage and scope.**
  - All 7 policies are covered.
  - Scopes are disjoint: task 0 = {mileage, wear, fee, plan}; task 1 = {quote, precondition, refinance}. GT charter_scope is unchanged.
  - uuid8s are unchanged and independent.
- **Trees.**
  - Task 0: 3 prerequisite problems with 3 value_input edges.
  - Task 1: 2 prerequisite problems with 2 value_input edges plus 1 state_gate.
  - Each tree has a user write. The difficulty-wide graph is a DAG.
- **Factors.**
  - Every computation has a self-sufficient baseline and 5–6 factors with ≥ 2 parameter and ≥ 1 method.
  - Each task has at least one multi-source and one cross-difficulty factor.
  - Every ladder is risk-ordered with distinct tier outcomes.
  - Every factor bears weight on its world, and every whole-baseline fall-back is definite and differs from gold (figures equal GT).
- **Round-1 REDs closed:** C-F1 (all four members), C-P1, T1-F1.
- **Remaining observations** (no rework grounds): O-S2, O-S3, O-R1, O-R2, O-L1, O2-1, O2-2, O2-3, O2-1.1 (stale "multi-source" labels in task 1 `factor_trace`), O-0.1, O-0.2.
- **Gates.** Coordinator snapshot r2 is green apart from pre-render traceability/validate items. A re-run after KB render is due in the scenario pipeline.
- **Result.** The difficulty passes the source-layer audit at revision_2.

task0=PASS task1=PASS
charter=CLEAN
VERDICT revision_2: task0=PASS task1=PASS charter=CLEAN

## revision_3

### charter_global_frozen (revision_3)

- **Written:** before reading the worklog "REWORK round 3 closure" or any round-3 GT field. Auditor: the same independent auditor.
- **Gating:** `tail -1 worklog.md` = `REWORK round 3: gates 7/7 green`.
- **Gate snapshot:** `.audit_views/policy/balloon_maturity_and_title/snapshot_r3.txt` (2026-10-16T00:32:18Z). check_extended, task_tools, replay --check, solvability, compute, grounding and cross_fire are OK. check_traceability shows only the unlock tool-name provenance miss and validate_scenario fails only on `documents: 0`; both are expected before render.
- **Hashes:**
  - `balloon.extended.yaml` ac29468ae727c921 → **fc433afe864d999b** (changed, so every charter-global check is re-derived below).
  - `task_tools.py` c39a38c81bb50a54 (unchanged; the revision_2 tool conclusions carry forward on that hash).
  - Views `0.json` 0748c506fa63290b and `1.json` cdbe395c8955132f (both unchanged).
- **Base copy:** identical to `blueprint/products/balloon.yaml`.
- **Mechanical sweep** (auditor's script, XF point 5 and check 2):
  - Every `compute_basis` quotation is verbatim in its own rule (0 misses in all 7 policies).
  - Every `superseded_clause` is a verbatim base substring, and every `replaced_by` and `policy_source` sits in its own rule.
  - Every `baseline.rule` sentence is in the rule.
  - Only plain binding without a basis entry: the plan's `return_charges`, carried from round 1. Rule sentence "The return charges are the excess mileage charge, the excess wear charge and the return fee billed on the contract for the return." states it. Observation O3-1.

### XF_recipe.md, points 1–12, checked on every extended policy

| # | mileage | wear | fee | plan | quote | precondition | refinance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 assembly | ok (generic "every mileage forgiveness") | ok | ok | ok (effect classes: "the larger is used / collected part / amounts moved / amounts added") | ok | ok | ok |
| 2 non-commuting order | ok (replacements act on inputs, the subtraction on the derived difference) | **MEMBER** | **MEMBER** | ok (stated) | ok | ok (stated) | ok |
| 3 independence | ok | ok (proration's tiers read no factor; the product sits in plain `forgiveness_applied`) | ok | ok | ok | ok | ok |
| 4 ownership | ok | ok | ok | ok | ok | ok | ok |
| 5 basis quotes | ok | ok | ok | ok (O3-1) | ok | ok | ok |
| 6 ties | ok (inspection tie stated; the election tie is value-identical, since LATEST reads the txn_date itself) | ok (inspection and late-charge ties stated) | n/a (scoped single holdings) | n/a | ok (election tie stated) | ok (quote tie stated) | ok (quote tie stated) |
| 7 counting | ok (day/month/window convention sentence equals DAYS/MONTHS/_within) | ok (+ years = months/12) | ok | ok | ok | ok ("beyond" = −22) | ok (48 counts as one) |
| 8 branches both ways | ok (no inspection or multi-holding: outside rule and tool) | ok | ok | ok | ok | ok | ok |
| 9 base clauses | ok (restated) | ok (restated) | ok (restated) | ok (both restated) | **MEMBER** | ok (restated) | ok (see note) |
| 10 rounding | ok | ok | ok | ok | ok | ok | ok |
| 11 tools | unchanged hash; revision_2 sweep holds (no example values; no ordering words; docstring effects equal bodies) | | | | | | |
| 12 proof text | checked after the GT reveal (task files) | | | | | | |

**XF-2 members** (non-commuting adjustments to one quantity whose order no generic sentence fixes). Finding **C3-X2**:

1. **Wear (`balloon_ext_return_wear_charge`).**
   - Two changes act on the same quantity:
     - "Wear forgiveness by standing: … has its wear forgiveness raised to return_wear_waiver_cap for its tier plus wear_standing_bonus_preferred" is a replacement.
     - "Wear forgiveness proration: … the wear forgiveness is multiplied by the calendar days from contract_date to the return date over …" is a scaling.
   - The combination sentence fixes the order only between the two changes as a group and the later steps: "Changes to the wear forgiveness are made first; the wear forgiveness and every wear credit that applies are then subtracted together …".
   - Round 2's text ("The wear forgiveness, prorated where proration applies, and every wear credit …") anchored proration to the forgiveness as set. Round 3 removed that anchor, so this is a regression introduced by the hardening pass.
   - Second reading: prorate the tier cap first, then raise to cap + bonus. That loses the proration.
2. **Fee (`balloon_ext_return_fee`).**
   - "Return fee basis: … the return fee is waived and is zero; … the return fee is the lower of return_option_fee for the tier and the disposition_fee of that lease; otherwise the return fee is return_option_fee" is a replacement.
   - Each reduction, e.g. "the return fee is reduced by fee_early_reduction_short", is a subtraction.
   - The combination sentence "Every reduction that applies is subtracted from the return fee, which never falls below zero and is rounded to the cent." does not say the basis is set first. Round 1/2's "subtracted from the return fee basis" did; it was removed for XF-1 without a generic replacement-first wording.
   - Second reading: subtract the reductions from return_option_fee, then apply the basis replacement.

Each member's second-reading value on task 0's world is demonstrated in `0.md` revision_3.

**XF-9 member.** Finding **C3-X9**: quote (`balloon_ext_payoff_quote`) `overwrite[1].replaced_by` ends "every other payoff quote, which is issued outside this rule and its tool, keeps the base per diem and payoff amount."
- This defers to the very clause the overwrite retires instead of restating its still-in-force content ("the per diem is the principal_balance times apr divided by per_diem_day_basis, rounded to the cent, and the payoff amount is principal_balance plus fees_due_balance plus the per diem times balloon_msr_quote_interest_days").
- Out-of-scope quotes really exist: base quotes for refinance_lender, dealer_trade_in and insurance_total_loss purposes.
- The same policy's `overwrite[0]` restates its retired clause, as do the mileage, wear, fee, plan and precondition overwrites.

Note on refinance point 9: the three `replaced_by` say "for a balloon refinance booked under this rule, and only for such a refinance" with no out-of-scope restatement. Every balloon refinance is booked under this rule: one tool, base "only once per contract", and other refinance requests route to a human. So no still-in-force part of those clauses survives to restate, and this is not a member (observation O3-2).

### other re-derived checks (revision_3)

- **Factor ladders.**
  - rp_minimum_share is now "two or more late charges in 24 months → min_share_high; exactly one → min_share_standard; none → 0". The returned-payment disjunct is gone, so O2-3 is closed.
  - The ladder is risk-ordered and its 0.50 tier can bind (Tier 1–3, R ≥ 900, no returned payment).
  - It is now single-source; the task-level multi-source floor is checked per task.
  - All other ladders are as at revision_2: C-F1 members stay closed and outcomes are monotone.
  - Factor counts per policy are 6/6/5/5/5/5/6, with ≥ 2 parameter and ≥ 1 method each.
- **Prerequisite graph and sentences.**
  - The graph is unchanged from revision_2 (DAG; state forms; the single-writer derivations hold).
  - O2-2 is closed: the quote→refinance `effect` now reads "…so the quote enables the refinance installment without moving its value".
  - No authoring-viewpoint word remains in the extended section (grep for task/difficulty/opening/world/seed/gold/edge/agent: 0 hits).
- **O2-1 closed.** The mileage, wear and fee scope clauses now say out-of-scope customers are "outside this rule and its tool" and restate the base sentence (XF-8/9 satisfied).
- **Conventions.** Every policy now carries the day/month/window convention sentence, and it matches DAYS/MONTHS/`_within` exactly.

### findings (revision_3)

| id | verdict | where | consequence |
| --- | --- | --- | --- |
| C3-X2 | charter RED (XF-2; members: wear, fee) | wear rule combination sentence and its standing/proration tiers; fee rule combination sentence and its basis tier | task 0 second readings: see `0.md` revision_3 |
| C3-X9 | charter RED (XF-9; member: quote `overwrite[1]`) | `balloon_ext_payoff_quote.overwrite[1].replaced_by` and its rule copy | out-of-scope quotes are defined by deferral to a retired clause; task 1's customer quote is in scope, so its values are unaffected |
| O3-1, O3-2 | observations | plan `return_charges` basis entry; refinance scope note | none |

### reworker claims vs artifacts (revision_3)

| claim | status |
| --- | --- |
| O2-1, O2-2, O2-3, O2-1.1 | confirmed closed |
| XF table "point 2: P" for wear and fee | **not supported**; see C3-X2 |
| XF table "point 9: P" for quote | **not supported**; see C3-X9 |
| All other XF cells | confirmed |
| Scored values and sensitivities unchanged | confirmed against the GT and the auditor's recomputation |

### closing_checklist (revision_3)

- **Coverage and scope.** Files, coverage, scope, uuid8s, trees and factor floors are as at revision_2, re-checked on hash fc433afe864d999b.
- **Not closed:**
  - **C3-X2** (XF-2; members: wear combination sentence, standing raise vs proration; fee combination sentence, basis replacement vs reductions). It costs task 0 a second scored answer.
  - **C3-X9** (XF-9; member: quote `overwrite[1]` defers out-of-scope quotes to the retired per-diem/payoff clause instead of restating it).
- **Result.** The difficulty does not pass the source-layer audit at revision_3.

task0=SOURCE-TASK RED task1=PASS
charter=C3-X2,C3-X9
VERDICT revision_3: task0=SOURCE-TASK RED task1=PASS charter=C3-X2,C3-X9

## revision_4

### charter_global_frozen (revision_4)

- **Written:** before reading the worklog "REWORK round 4 closure" or any round-4 GT field.
- **Gating:** `REWORK round 4: gates 7/7 green`.
- **Gate snapshot:** `.audit_views/policy/balloon_maturity_and_title/snapshot_r4.txt` (2026-10-16T01:00:14Z).
  - check_extended, task_tools, replay --check, solvability, compute, grounding and cross_fire are OK.
  - check_traceability: only the unlock tool-name provenance miss.
  - validate_scenario: INVALID with `documents: 169`. Other products have rendered; for this difficulty only the expected pre-render "required document" items apply.
- **Hashes:** charter fc433afe864d999b → **1b10b43c551e9701** (changed). Tools c39a38c81bb50a54, views 0748c506fa63290b / cdbe395c8955132f (all unchanged, so revision_3 tool and world conclusions carry forward on those hashes).
- **What changed:** sentence, compute, factor, param and overwrite counts per policy are identical to revision_3 (16/21/6/13/1, 17/20/6/17/1, 10/14/5/13/1, 16/23/5/15/2, 15/17/5/11/2, 14/15/5/17/1, 19/19/6/17/3). Spot phrases of the unchanged policies are present verbatim. The edits are confined to the wear and fee combination sentences, the quote `overwrite[1]` and its rule copy, and the plan `return_charges` basis entry.
- **Mechanical sweep:** compute_basis verbatim, 0 misses in 7 policies. Every superseded_clause is a base substring; every replaced_by, policy_source and baseline sentence is in its own rule. The extended section has no authoring-viewpoint words.

### round-3 REDs

- **C3-X2 closed.**
  - Wear: "Replacements of the wear forgiveness are made first and proration of it second; the wear forgiveness and every wear credit that applies are then subtracted together from the wear_assessed_amount, the chargeable wear that remains never falls below zero, and any share of it that applies is taken last, rounded to the cent." The standing raise (replacement) now precedes the proration (scaling), which is the order compute implements (`RND(forgiveness * proration_share, 2)`). The proration-first reading is excluded. The sentence names adjustment classes (replacement, proration, credit, share), not a factor's quantity, so XF-1 holds.
  - Fee: "The basis of the return fee is set first and every reduction that applies is then subtracted from it; the return fee that remains never falls below zero and is rounded to the cent." The replacement now precedes the reductions, matching `RND(MX(0, fee_basis − …), 2)`. The reductions-first reading is excluded.
- **C3-X9 closed.** Quote `overwrite[1].replaced_by` now ends "…keeps the base per diem and payoff amount, by which the per diem is the principal_balance times apr divided by per_diem_day_basis, rounded to the cent, and the payoff amount is principal_balance plus fees_due_balance plus the per diem times balloon_msr_quote_interest_days." That restates the retired clause for out-of-scope quotes. The rule copy is verbatim.
- **O3-1 closed.** The plan's `return_charges` now carries the basis "The return charges are the excess mileage charge, the excess wear charge and the return fee billed on the contract for the return."

### XF_recipe.md points 1–12 on every policy (revision_4)

| policy | result |
| --- | --- |
| mileage, plan, quote, precondition, refinance | text unchanged except the quote overwrite (now passing point 9). The revision_3 point-by-point table holds. |
| wear | points 1, 2 (now stated), 3–11 pass |
| fee | points 1, 2 (now stated), 3–11 pass |
| all | point 11: tools unchanged (no example values, no ordering words, effects equal bodies). Point 12: checked after the reveal in the task files. |

O3-2 (refinance scope note) remains an observation.

### findings (revision_4)

No charter-wide RED as frozen. C3-X2, C3-X9 and O3-1 are closed.

### reworker claims vs artifacts (revision_4)

| claim | status |
| --- | --- |
| C3-X2 (wear, fee) | confirmed closed |
| C3-X2 class sweep | concurs with the auditor's revision_3 table: mileage, plan, quote, precondition and refinance already fix their order |
| C3-X9 | confirmed closed |
| Overwrite sweep (refinance needs none, O3-2) | concurs |
| O3-1 | confirmed closed |
| No compute edited | consistent with the unchanged scored values and sensitivities in GT and in the auditor's recomputation |

### closing_checklist (revision_4)

- **Coverage and scope.** Files, coverage, disjoint scopes, uuid8s, trees (DAG; value_input floors; user writes) and factor floors are as at revision_2/3, re-checked on charter 1b10b43c551e9701.
- **REDs.** Every RED from revisions 1–3 is closed: C-F1, C-P1, T1-F1, C3-X2, C3-X9, T0-R3-1.
- **Recipe.** XF_recipe points 1–12 pass on all 7 extended policies.
- **Remaining observations** (no rework grounds): O-S2, O-S3, O-R1, O-R2, O-L1, O3-2, O-0.1, O-0.2.
- **Result.** The difficulty passes the source-layer audit at revision_4.

task0=PASS task1=PASS
charter=CLEAN
VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

### charter_global_frozen (revision_5)

- **Written:** before reading the worklog "REWORK round 5 closure" or any round-5 GT field.
- **Gating:** `REWORK round 5: gates 8/8 green`.
- **Gate snapshot:** `.audit_views/policy/balloon_maturity_and_title/snapshot_r5.txt` (2026-10-16T09:32:54Z).
  - check_extended, task_tools, replay --check, solvability, compute, grounding and cross_fire are OK.
  - **check_traceability OK** (0.json 18/0, 1.json 15/0). The KB is now rendered.
  - validate_scenario: INVALID with `documents: 303`. The snapshot line does not itemise the errors. The KB audit file records DOCS OK and TRACEABILITY OK for this difficulty. The auditor did not run gates itself; this is recorded as the entry condition.
- **Hashes:**
  - charter 1b10b43c551e9701 → **86d56ce7529d0510**
  - view `0.json` 0748c506fa63290b → **20765664f620fa63**
  - view `1.json` cdbe395c8955132f and tools c39a38c81bb50a54 unchanged
- **Input this round:** SRC-1..SRC-4 from `audits/policy_kb/balloon_maturity_and_title/_difficulty.md` (KBVERDICT round 1: kb=CLEAN, src=SRC-1..4).
- **What changed:** sentence, compute, factor, param and overwrite counts are identical to revision_4 except the quote (15 → 16 sentences). Edits are confined to:
  - the quote (overwrite[1] restatement, post-maturity rate sentence, new split sentence, factor binding set)
  - the "one" → "one or more" wording in plan (prior-fee share, upfront amount) and precondition (returned payments)
  - task 0's persona timing line
- **Mechanical sweep:**
  - compute_basis verbatim: 0 misses in 7 policies; every compute binding has a basis entry.
  - Every superseded_clause is a base substring; every replaced_by, policy_source and baseline sentence is in its own rule.
  - Every `decides` is within its factor's bindings.
  - No authoring words in the extended section.

### SRC items

- **SRC-1: closed.** Quote `overwrite[1].replaced_by` (and its rule copy) now restates the out-of-scope per diem as the base *formula* computes it: "…keeps the base per diem and payoff amount as the base formula computes them, by which the per diem is principal_balance times apr divided by 100 divided by per_diem_day_basis…". That equals the base `formula.per_diem` (`round(principal_balance * apr / 100 / per_diem_day_basis, 2)`), so the 100× misreading of the base prose is no longer carried by the extended text. The base copy itself stays verbatim, as required; its prose/formula slip is a blueprint matter, not something this charter can rewrite.
- **SRC-2: closed.** All three members now read "one or more":
  - rp_prior_fee_share: "where one or more was assessed or posted in those months but none in the plan_recent_window_months…"
  - rp_upfront_amount: "…but one or more posted in the plan_long_window_months…"
  - cp_returned_payments: "…but one or more posted in the cp_long_window_months…"

  The factor ladders match. Compute (`>= 1` / non-zero tests) is unchanged. No other existential "one" remains in the extended rules: the fee record tier's "exactly one" and the refinance add-on's "exactly one" are intended exact counts that match compute `== 1`.
- **SRC-3: closed.**
  - The post-maturity daily rate now sits inside its factor: qt_post_maturity_rate decides `post_per_diem` (bindings election_option, election_lead, post_rate, post_per_diem). Its ladder is (a) refinance election ≥ 30 days ahead → "principal_balance times refinance_apr for the tier divided by 100 divided by per_diem_day_basis, rounded to the cent", (b) return election ≥ 30 days ahead → 0, (c) otherwise → the per diem, which equals baseline `per_diem`.
  - The day split is a plain binding stated once: "The quote interest days after maturity_date are those that fall after maturity_date; the other quote interest days fall on or before it." It is shared by the rate factor and the three courtesy factors (XF-3/4).
  - The assembly "each quote interest day that remains is charged at the daily rate that applies to it" names no factor quantity (XF-1).
  - The baseline (all days at the per diem) needs no post-maturity rate wording.
- **SRC-4: closed.** The task 0 persona now reads "A little over three years ago, in September 2023, you financed a Kestrel Corvalis…". That is consistent with contract_date 2023-09-11 and frozen_time 2026-10-14.
- **KB policy-side notes.** PN-1 and PN-2 are the same items as revision-1 observations O-S3 and O-S2, and stay observations. The held-row applied fields left at 0.00 after booking are record detail and stay an observation (O5-1). Booking balances embody the application, and no scored value or gate reads those fields after the refinance.

### XF_recipe.md points 1–12 on every policy (revision_5)

- **Quote, re-checked in full:**
  - 1: generic assembly.
  - 2: courtesy days off the post-maturity days, then each day at its rate.
  - 3: no factor reads another's binding; the shared split is plain.
  - 4: ownership as above.
  - 5: verbatim.
  - 6: election tie stated.
  - 7: convention sentence.
  - 8: every rate branch stated, including "otherwise the per diem".
  - 9: both overwrites restated.
  - 10: daily rates and payoff rounded as RND.
  - 11: tool unchanged.
- **Plan and precondition:** wording-only edits, points 1–11 as at revision_4.
- **Mileage, wear, fee, refinance:** unchanged, as at revision_4.
- **Point 12:** checked after the reveal in the task files.

### findings (revision_5)

No charter-wide RED as frozen. O5-1 is a new observation.

### reworker claims vs artifacts (revision_5)

| claim | status |
| --- | --- |
| SRC-1..SRC-4 | confirmed closed in the source |
| SRC-2 class sweep (the other "one" uses are exact or bounded counts matching compute) | concurs |
| No compute value changed | consistent with GT and the auditor's recomputation |
| validate_scenario "no error names balloon_maturity_and_title" | consistent with the KB audit's DOCS OK / TRACEABILITY OK; the auditor did not run gates |

### closing_checklist (revision_5)

- **Coverage and structure.** Files, coverage, disjoint scopes, uuid8s, trees and factor floors are as at revision_4, re-checked on charter 86d56ce7529d0510 and view 20765664f620fa63.
- **Items.** The KB auditor's SRC-1..SRC-4 are closed. Every RED from revisions 1–4 stays closed.
- **Recipe.** XF_recipe points 1–12 pass on all 7 policies.
- **Remaining observations:** O-S2, O-S3, O-R1, O-R2, O-L1, O3-2, O5-1, O-0.1, O-0.2.
- **Result.** The difficulty passes the source-layer audit at revision_5.

task0=PASS task1=PASS
charter=CLEAN
VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN
