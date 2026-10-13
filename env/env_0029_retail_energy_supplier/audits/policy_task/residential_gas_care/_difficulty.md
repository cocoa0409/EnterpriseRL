# Policy-task audit — residential_gas_care / charter-global

## charter_global_frozen

- Freeze time: 2026-10-04T16:20Z (round 1; file hash 384a61ff…d852 taken at 16:23:58Z, before any reveal). Auditor: independent policy-task auditor (did not author any artifact of this difficulty).
- Frozen inputs (sha256, re-verified by the auditor against `.audit_views/policy_task/residential_gas_care/HASHES.txt`):
  - `tasks/residential_gas_care/gas.extended.yaml` 4acba50abbdafc2230ed385e3f21f83592e37867da6e39ac825518d73b5e6123
  - `tasks/residential_gas_care/task_tools.py` 6489f6158b4a7e755685ac0faa0884a03e80150e6c3fdc8523767a6f8fd51ca1
- Permitted reads for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/gas.yaml` (plus the variant names of `power.yaml` / `protect.yaml` to check cross-category reads), the extended charter, `task_tools.py`, the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (read-only, to know what `SUM(... within_months=12 ...)`, `LATEST`, `CFIELD`, `XSUM`, `RND` evaluate to).
- Masked / not read when this section was written: every `tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), every worklog, any other audit view. Nothing in this section is derived from a revealed GT.

### Entry conditions (Step 0)

Gate snapshot supplied by the orchestrator (cited, not re-run): `check_extended.py` EXTENDED OK; `check_task_tools.py` TASK TOOL CONTRACT OK; `replay_tasks.py` REPLAY OK; `check_solvability.py` SOLVABILITY OK; `check_compute.py` COMPUTE OK; `check_grounding.py` GROUNDING OK; `check_cache_diff.py` CACHE-DIFF INFO; `check_cross_fire.py` SCOPE OK; `check_traceability.py` deferred (depends on the unrendered KB). Masked views and hashes present. Entry conditions satisfied; `check_traceability` remains open for the closing checklist.

Base-copy check: lines 1-1208 of `gas.extended.yaml` are byte-identical to `blueprint/products/gas.yaml` (diff shows only the trailing blank line before `extended_policies:`). The base section is verbatim.

### policy_conflict_scan

Six extended policies:

| id | subject | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| gas_ext_recontract_rate | gas_renew | accept_gas_recontract_offer_a9611340 (user) | contract_rate_usd_therm | [] |
| gas_ext_added_premise_rate | gas_enroll | enroll_gas_added_premise_5ded636b (agent) | contract_rate_usd_therm | -> gas_ext_recontract_rate (value_input, home_rate, state) |
| gas_ext_latest_bill_rebill_credit | gas_adjustment | post_gas_rebill_credit_0e7c2434 (agent) | credit_amount_usd | [] |
| gas_ext_signup_credit | gas_credit | post_gas_signup_credit_32aac0cb (agent) | credit_amount_usd | [] |
| gas_ext_renewal_loyalty_credit | gas_credit | post_gas_loyalty_credit_c1183f95 (agent) | credit_amount_usd | [] |
| gas_ext_renewal_rate | gas_renew | accept_gas_renewal_offer_6e431548 (user) | contract_rate_usd_therm | -> rebill, signup, loyalty (all value_input, ref_cost, state) |

Overlapping subjects:
- `gas_renew`: recontract ("has rolled over and who re-contracts within the post-expiry grace period") vs renewal_rate ("an agreement still in its term ... on or before the contract end date"). Disjoint by the record state (contract_end_date passed and plan_change_date recording a rollover vs not). No conflict.
- `gas_credit`: signup (line_type signup_credit, "still on the plan it was enrolled on") vs loyalty (renewal_loyalty_credit, "renewal that has already taken effect ... at least one energy line of the renewed term has already been billed"). Different line types and dedup keys. No conflict. Base `gas_renew` event trigger to `gas:gas_credit renewal_loyalty_credit` and base gas_renewal "posted on the first bill of the new term": the extended loyalty policy declares this sentence overwritten and states that the credit of a renewed term not yet billed "arrives with that term's first bill and is not settled by this policy"; renewal_rate's rule repeats "its own renewal loyalty credit arrives with the first bill of the renewed term". So neither user-owned renewal write obliges an immediate loyalty write. Consistent.
- `gas_adjustment`: extended rebill (only the latest energy line) vs base gas_billing_correction (any line). The extended policy narrows the object and declares its amount sentence overwritten. Base still governs other lines. See `override_declarations` for the undeclared part.
- `gas_enroll`: extended added premise (a customer holding a home agreement at the mailing-address premise) vs base enrollment pricing (price-offer rate). The rate sentence is declared overwritten. Eligibility (premise class, gas utility, state, assistance program, channel, one live agreement per premise, max 4) is inherited ("must satisfy the gas enrollment eligibility rules and the one-live-agreement-per-premise rule").
- Time anchors: recontract uses plan_change_date (rollover) to election date; renewal_rate uses acceptance date to contract_end_date. Each tool's own date fields are disjoint (recontract stamps today; renewal takes plan_change_date = end + 1).
- Cross-category reads: recontract reads power status/service_start_date (CFIELD); added premise reads power_billing energy lines (XSUM); renewal_rate reads power service_start_date; loyalty reads protect status/variant_name. All reads are of this customer's own holdings and ledger; none writes another category.

Scope exclusivity: the prerequisite graph has exactly two connected components, {added_premise -> recontract} and {renewal_rate -> rebill, signup, loyalty}. With M=2, the only partition into problem-tree scopes covering all six policies is task A = {gas_ext_added_premise_rate, gas_ext_recontract_rate}, task B = {gas_ext_renewal_rate, gas_ext_latest_bill_rebill_credit, gas_ext_signup_credit, gas_ext_renewal_loyalty_credit}. These are pairwise disjoint and jointly complete over `extended_policies`. Whether the two tasks claim exactly these is checked against `charter_scope` after the reveal (task files).

Observation (scope breadth): the blueprint claim lists event_types gas_rescind, gas_cancel, gas_cancel_withdraw, gas_plan_change and gas_etf_charge. No extended policy of this difficulty has any of them as a subject; they are covered only by base policies and by no task. This is a coverage observation about the claim, not a conflict.

### rule_compute_equivalence

Check 2 over all six policies. DSL semantics used: `SUM/COUNT(..., within_months=12, date_field='billing_period_start')` keeps rows with `0 <= MONTHS(d, NOW) < 12`. That matches "cycles starting later than the same calendar day twelve months before" (a cycle starting exactly twelve months before gives MONTHS = 12 and is excluded). `LATEST` takes the row with the greatest `date_field` value among this holding's rows. `CFIELD` takes the customer's first holding of that category. `RND` is Python `round` on binary floats.

gas_ext_recontract_rate:
- start_rate tiers, grace, commitment, peak, electricity, result: each has a verbatim compute_basis quote and a matching expression. `ini_ok`: `DAYS(ini_date, ini_end) <= 60 and >= 45` matches "no earlier than ... and no later than ...". `fin_ok`: `>= 30 and fin_date > ini_date` matches "no later than final_options_notice_latest_days ... and after the initial renewal notice". Final-rounding-once matches `RND(..., 4)` on the result only. Equivalent.
- Minor: `fin_ok` measures from the final notice's own `effective_date`, while the rule says "before that date" (the date the initial notice refers to). These are equal whenever both notices refer to the same end date. Observation only.

gas_ext_added_premise_rate:
- home_rate, home_usage12 (gas energy lines, 12-month window), base_rate (fixed AND >=900 -> x0.97 rounded to 4 places; fixed AND 500-899 -> minus 0.0100; else home rate), tenure, elec_spend (`XSUM power_billing amount_usd line_type='energy_charge'`, which excludes fee lines and credits as the rule says), align (0 when no end date), commit, result. Equivalent.

gas_ext_latest_bill_rebill_credit:
- `var_rate: LATEST('gas_notices','new_rate_usd_therm', date_field='effective_date', notice_type='variable_rate_change')` takes the notice with the latest effective date **overall**. The rule says "the most recent variable rate change notice on the agreement whose effective date is on or before the cycle's billing period start". The compute drops the "on or before the cycle start" filter. The two disagree whenever a variable notice with an effective date after the latest line's cycle start already stands. **Latent finding F-2** (below).
- `allowed_rate` reads `P('rate_type')` of the plan **now** in force. The rule says "the plan's pricing structure" for "the line's cycle". On an agreement whose latest line was billed under an earlier plan (for example a line billed in a fixed term on an agreement that has since rolled over), the two readings differ. Latent observation, part of F-1.
- `over_billed`, the three supplements, the `over_billed > 0` gate and the agent-limit comparison (stated in the rule, not computed; no scored value depends on it unless above 150.00) are equivalent.

gas_ext_signup_credit: plan_amount, online (web AND switch <= 30 -> x1.25; web AND > 30 -> +5.00; else unchanged), late, retention, lifetime usage, result. Equivalent.

gas_ext_renewal_loyalty_credit: tenure multiplier, late, term, protection (gas-related list vs any other active plan vs none), peak, result. Equivalent. Note that `CFIELD('protect', ...)` reads the customer's first protect plan, while the rule says "the customer's ... home protection plan" (singular). This is ambiguous only for a customer with several plans. Observation.

gas_ext_renewal_rate:
- start_rate (`MN(ini, fin)` when both on time and fin > ini; ini when ini on time and fin not; else fin), since (either span), early, heating, reduced, net_amount, ref_cost, share, cushioned, result. Equivalent on the stated branches.
- `ref_cost: ... if usage12 > 0 else F('contract_rate_usd_therm')`. The zero-usage fallback to the contract rate has no rule sentence, so the compute invents a basis. Latent observation (unreachable in any world with billed energy lines in the window).
- `net_amount` sums **every** line type in the window. The rule enumerates "energy charges, service fees, rebill credits, sign-up credits and renewal loyalty credits". The two differ only if an early-termination or thermostat-recovery line falls in the window of an agreement still renewing, which is unlikely. Observation.

Rounding: every rule says "rounded half up", and `RND` is Python banker's-style `round` on binary floats. The two differ on exact ties. The ties that could arise in this difficulty's worlds are checked per task. Charter-level observation.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy: six tools, six policies, no reuse.
- Tool docstrings: none names another tool, a policy id, or a position in a sequence. Every docstring ends its effect description with "Afterwards the ... appears/can see ...". That word describes the call's own visible effect, not an order relative to another problem. Observation only.
- Scope phrases in the docstrings ("an agreement that has already rolled over to month-to-month service"; "still in its current term"; "for a renewal that has taken effect") restate the policy's own object, not a procedure. No added confirmation, review or wait.
- uuid8 tails: a9611340, 5ded636b, 6e431548, 0e7c2434, 32aac0cb, c1183f95. All distinct, with no shared prefix, no sequential pattern and no copied-with-new-tail pair. PASS.
- Tool bodies (prerequisite judgement): `accept_gas_recontract_offer_a9611340` performs one `ctx.update` with `plan_change_date=ctx.now()[:10]`; `enroll_gas_added_premise_5ded636b` performs one `ctx.create` with status enrollment_pending and channel phone; `accept_gas_renewal_offer_6e431548` performs one `ctx.update`; the three `post_*` tools each perform one `ctx.create` of a negative `gas_billing` line. None reads a prerequisite state, refuses, errors or hints. The tool layer does not judge any prerequisite. PASS.

### prerequisite_graph

Check 7:
- `prerequisite` is present on all six policies (`[]` on four). Every `problem` names another extended policy id in this file, never a base policy and never itself. The graph has edges added_premise->recontract and renewal_rate->{rebill, signup, loyalty}. It is acyclic, with depth 1 in both components.
- `policy_source` is verbatim in the blocked policy's own `rule`: added_premise line 1423 = edge text; renewal_rate lines 2031, 2032, 2033 = the three edge texts. PASS.
- `form: state` on all four edges, with no `fallback_reason`. Consistent.
- `resolved_by` equals the depended-on policy's `target_tool` on all four edges.
- `kind: value_input`. `gate: home_rate` exists in added_premise compute (`home_rate: F('contract_rate_usd_therm')`). `gate: ref_cost` exists in renewal_rate compute. The effect claims are correct: the recontract rewrites contract_rate_usd_therm, variant (hence `P('rate_type')`), contract_end_date and plan_change_date, which feed home_rate, base_rate, align_disc and commit_bonus. Each credit adds a negative `gas_billing` row with a billing_period_start the agent supplies, which enters `net_amount` when inside the window.
- Condition vs sentence strength (observations, no consequence demonstrated):
  - added_premise edge: the sentence waits on "again carries a term in months and a contract end date". The `condition` adds "written by a re-contract within the post-expiry grace period", which is narrower than the sentence. Within this difficulty no other write can produce that state on a rolled-over agreement: renewal_rate's scope excludes rolled-over agreements, and there is no plan-change tool. So the narrowing selects nothing different.
  - loyalty edge: the sentence says "every renewal that has taken effect"; the `condition` names only "the renewed term recorded by the agreement's plan change date". On an agreement with one past renewal (or where only the latest is unpaid) these coincide.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field. PASS.

### prerequisite_sentences

Check 6, four-point test per edge:

1. added_premise <- recontract. "The household rate for an added premise is fixed only after the home agreement, once rolled over, again carries a term in months and a contract end date."
   - Connective "only after"; the waited-on thing is a record-visible state (`gas_agreements.term_months`, `contract_end_date`); no tool, id or snake_case. Its strength matches.
   - Writes that can bring the state about on a rolled-over agreement: only `accept_gas_recontract_offer_a9611340`. `accept_gas_renewal_offer_6e431548` also writes term and end date, but its policy is confined to "an agreement still in its term ... on or before the contract end date". Base gas_plan_change_terms (month-to-month to a term plan "always allowed") has no write tool in this difficulty or in `share_tools.py`.
   - Derivation: the home agreement shows term_months 0 and an empty contract_end_date after a rollover. Among the policies, recontract is the one whose rule says the customer "takes the plan offered in the final options notice, that plan's term in months ... and the new term starts on the election date". So the resolving action is the customer's re-contract. One reading. PASS.
2. renewal_rate <- rebill. "The renewal acceptance rate is fixed only after the energy line of the most recent bill, when it was billed above the rate the plan allows for its cycle, carries its rebill credit." State form: a rebill_credit row with source_billing_id = that line. The one write is `post_gas_rebill_credit_0e7c2434` (gas_ext_latest_bill_rebill_credit settles exactly "the energy line of the most recent bill ... when that line was billed above the rate the plan allows"). PASS.
3. renewal_rate <- signup. "The renewal acceptance rate is not fixed until the agreement carries the sign-up credit that its completed billing cycles earned under its plan." State form: a signup_credit row. The one write is `post_gas_signup_credit_32aac0cb`. PASS.
4. renewal_rate <- loyalty. "The renewal acceptance rate is not worked out before every renewal that has taken effect on the agreement carries its renewal loyalty credit." State form: a renewal_loyalty_credit row for the renewed term. The one write is `post_gas_loyalty_credit_c1183f95`. PASS.

The depended-on rules (recontract, rebill, signup, loyalty) do not restate any of these sentences and do not name the root. The root rules carry no second wording of any dependency.

Undeclared cross-problem order: none in the extended rules. Base rules with ordering connectives across problems: gas_etf "Gas termination fees are assessed only once the agreement is drop_pending or closed" (fee after cancellation). It grounds no edge of this difficulty and no task tree rests on it. Observation.

### override_declarations

Check 1, sentence by sentence against each `base_policy_refs` entry (findings only):

- gas_ext_recontract_rate vs gas_renewal:
  - s1 (accept offer, take offered plan, term and rate): declared.
  - s2 (active only), s3 (after rollover the new term starts on the election date), s4/s5 (grace and counting rule): followed.
  - s6 (loyalty credit on first bill of the new term): untouched and inherited. The extended loyalty policy defers an unbilled term.
  - s7 (late election / other plan = plan change): followed.
  - vs gas_expiry_notices: s5 (final notice governs) declared. Compliance windows restated identically.
  - vs gas_rollover_terms: no quantity in conflict.
  - Clean.
- gas_ext_added_premise_rate vs gas_enrollment_eligibility: s5 (offer-rate pricing and capped ceiling) declared. s1-s4 and s6 followed. vs gas_agg_multi_holding: followed. vs gas_renewal: no conflict. Clean.
- gas_ext_signup_credit vs gas_signup_credit: s1 declared. s2, s3, s4 (forfeit), s5 (plan changes/renewals/rollovers never earn) and s7 followed (scope "still on the plan it was enrolled on"). Clean.
- gas_ext_renewal_loyalty_credit vs gas_renewal: s6 declared. vs gas_signup_credit: s3 restated. Clean.
- gas_ext_renewal_rate vs gas_renewal: s1 declared. s2, s3, s6 and s7 followed. vs gas_expiry_notices: s5 declared. Clean.
- gas_ext_latest_bill_rebill_credit vs gas_billing_correction: s2 and s6 declared. s3/s4 lookback, s5 once-per-line and s7 no back-billing are inherited.
- gas_ext_latest_bill_rebill_credit vs gas_variable_rate (in its own `base_policy_refs`): **undeclared**. See F-1.

### factor_ladders

Per policy (label / decides / tiers / multi-source / cross_difficulty):

gas_ext_recontract_rate (5 factors: 1 method, 4 parameter; cross power):
- notice_protection / method / start_rate / 3 tiers (held rate | average of final and held, rounded to 4 places | final rate). Three different algorithms, so the label is honest. Tiers 1-2 are conjunctions over two distinct notice rows: multi-source. Fall-through = baseline `fin_rate`.
- prompt_return / parameter / grace_disc / <=10, 11-20, >20 days: all three are reachable inside a 30-day grace.
- commitment / parameter / PL36, PL24 or CO24, other.
- winter_peak / parameter / >=180, 120-179, <120.
- electricity_relationship / parameter / cross power / active AND >=1461 d, active AND 730-1460 d, else. Both conditions sit on one power-agreement row, so it is not multi-source.
- Distinct values in every ladder. All tiers are stated in the rule and implemented in compute. Fall-throughs are 0 or fin_rate, equal to `baseline`.

gas_ext_added_premise_rate (5 factors: 1 method, 4 parameter; cross power):
- household_form / method / base_rate / fixed AND >=900 therms -> x0.97 rounded to 4 places | fixed AND 500-899 -> minus 0.0100 | else home rate. Multiplication vs subtraction vs identity: an honest method. Conjunction over the agreement row and billing rows: multi-source.
- household_tenure / parameter / >=730, 365-729, <365.
- household_electricity / parameter / cross power (XSUM power_billing) / >=1200, 600-1199, <600 USD.
- term_alignment / parameter / >=540, 180-539, <180 or no end date.
- new_commitment / parameter / change <=30 d AND term >=24 | change <=30 d AND 0<term<24 | else.
- All reachable, distinct, stated and implemented.

gas_ext_latest_bill_rebill_credit (4 factors: 1 method, 3 parameter; no cross):
- allowed_rate_basis / method / allowed_rate / capped -> min(variable, contract) | variable -> variable | else contract. A minimum of two sources vs a single source: an honest method. Fall-through = baseline contract rate. Single-condition tiers, not multi-source.
- billing_error_supplement (>=20, 5-19.99, <5), carried_charge_supplement (>=21, 7-20, <7 days), repeat_error_supplement (>=2, 1, 0). Reachable and distinct.

gas_ext_signup_credit (4 factors: 1 method, 3 parameter; no cross):
- online_enrollment / method / web AND <=30 d -> x1.25 | web AND >30 d -> +5.00 | else unchanged. Multiply vs add vs identity: honest.
- late_posting (>=540, 180-539, <180; <180 reachable because a credit can post about 90 days after start), retention (>=30 d since plan change with term >=24 | with 0<term<24 | else, including no plan change date), lifetime_usage (>=1500, 750-1499, <750).

gas_ext_renewal_loyalty_credit (5 declared factors; cross protect):
- **loyalty_tenure / labelled method / tenure_amount / x2.0 | x1.5 | unchanged.** All three tiers are `plan_amount x m` with m in {2.0, 1.5, 1.0}: the same formula with a different number substituted. The `method` label is dishonest; this is a parameter factor (finding F-3a).
- **loyalty_tenure fall-through "<365 days from service start to the renewal's plan change date" is unreachable for any customer in this policy's scope** (finding F-3b). A renewal takes effect only when a term has run. The shortest term of any plan paying renewal_loyalty_credit_usd > 0 is 12 months (CV12, PL12, CO12). A term counted per gas_enrollment_processing / gas_renewal ends on "the day before the same calendar day term_months calendar months after" its start, and the renewed term starts the next day. So the renewal plan_change_date is at least 12 calendar months after service_start_date, which is >= 365 days, including the 29 Feb case (2024-02-29 start -> 2025-02-27 end -> 2025-02-28 renewal = 365 d). A re-contract after rollover is later still. The condition "at least loyal_tenure_mid_days" therefore holds for every customer who reaches this write, and the ladder has only two live tiers.
- **renewed_term / parameter / term_supp / >=700 | 360-699 | <360 days from the renewal's plan change date to its contract end date.** The fall-through <360 is unreachable (finding F-3c). Every renewed term is 12, 24 or 36 months, and a 12-month term spans 364 or 365 days (start day to "day before the same calendar day 12 months later"), always >= 360. The condition "at least term_mid_days" holds for every customer in scope. Two live tiers.
- loyalty_late_posting (>=270, 90-269, <90), home_protection (cross protect; active AND gas-related plan | active AND other | none), loyalty_winter_peak (>=170, 110-169, <110). Reachable and distinct.
- Surviving count after the tests: late_posting, home_protection and winter_peak are clean parameter factors. loyalty_tenure (mislabelled, plus a universal condition) and renewed_term (universal condition) are struck. That leaves 3 factors and 0 method, against the bounds of 4-6 factors with >=1 method. **SOURCE-FACTOR RED on the structure of this computation** (bears on whichever task claims gas_ext_renewal_loyalty_credit).

gas_ext_renewal_rate (6 factors: 2 method, 4 parameter; cross power):
- offer_choice / method / start_rate / min(ini, fin) | ini | fin: honest. Conjunction over two notice rows: multi-source.
- long_relationship / parameter / cross power / either span >=1826 | neither >=1826 AND either >=1096 | both below. A disjunction over the gas agreement row and the power agreement row: multi-source.
- early_acceptance (>=30, 15-29, <15).
- renewal_cushion / method / capped AND reduced > net cost -> subtract share x excess | fixed AND reduced > contract x 1.10 -> lower to that cap | else stands: honest. Conjunctions over the agreement row and billing rows.
- cushion_share / parameter / >=10, 6-9, <6 energy lines in 12 months. Observation: the share only matters on a capped plan (CV12, 12-month term), and an offer is accepted after a notice that is normally 30-60 days before the end. That leaves 9-12 lines in the ordinary case, so "<6" is reachable only through a badly early (non-compliant) notice. The charter admits such worlds, so this is not demonstrable as universal.
- heating_household (>=900, 500-899, <500).

Counts per policy: recontract 5 (1 method); added premise 5 (1 method); rebill 4 (1 method); signup 4 (1 method); loyalty 5 declared, 3 surviving (0 method) — RED; renewal_rate 6 (2 method).
- Per-component multi-source: {recontract, added premise} has notice_protection and household_form. {renewal_rate, rebill, signup, loyalty} has offer_choice, long_relationship and renewal_cushion.
- Per-component cross_difficulty: {recontract: power, added premise: power}; {renewal_rate: power, loyalty: protect}.

Realism of conditions and outcomes: no tier condition or outcome other than F-3b/F-3c was found that the line of business would not weigh or publish. The values are synthetic goodwill and retention amounts, but each is a plausible published treatment. No demonstrable defect beyond F-3.

### findings

- **F-1 — SOURCE-POLICY RED (charter-global; undeclared override; latent on both task worlds).**
  - Symptom: gas_ext_latest_bill_rebill_credit lists gas_variable_rate in `base_policy_refs` but replaces how that policy decides the allowed rate of a cycle without naming any of its sentences in `overwrite` (its two `overwrite` entries both target gas_billing_correction).
  - Evidence:
    - Base gas_variable_rate s1: "A month-to-month gas agreement is billed at contract_rate_usd_therm for its first intro_rate_cycles billing cycles and for any cycles held at the expiring rate under the gas rollover policy."
    - Base s2: "...until the first such notice applies, contract_rate_usd_therm continues."
    - Base s4: "...when it is issued later, the change applies only from the first cycle beginning on or after notice_date plus variable_rate_notice_days."
    - Extended rule: "on a month-to-month variable plan it is the variable rate in force for the cycle ... The variable rate in force for the cycle is the new rate of the most recent variable rate change notice on the agreement whose effective date is on or before the cycle's billing period start."
    - Not in `base_policy_refs` but equally replaced: gas_regulatory_passthrough s2, "the new rate applies to cycles beginning on or after the later of the stated effective date and notice_date plus regulatory_change_notice_days". The extended "on a fixed plan it is the contract rate" ignores a valid pass-through.
  - Demonstrated conflict (constructed situation): a capped-variable agreement whose latest cycle starts 2026-09-04, with a variable notice dated 2026-08-28 effective 2026-09-01 (4 days' notice < 10). Base s4: the change applies only from the first cycle starting on or after 2026-09-07, so cycle 2026-09-04 keeps the prior rate. Extended: the late notice is "in force". Two allowed rates give two credit amounts. Second situation: a Monthly Variable agreement in a held cycle after late expiry notices. Base: contract rate (held). Extended: the latest variable notice.
  - Affected artifact: `gas.extended.yaml` gas_ext_latest_bill_rebill_credit `overwrite` and `rule`. Bears on the task that claims the rebill policy. Its task file must show whether its world triggers the conflict.
  - Relation to previous revisions: first audit.
- **F-2 — SOURCE-POLICY RED (charter-global; rule/compute non-equivalence; latent on both task worlds).**
  - Symptom: `var_rate` in the rebill compute drops the rule's filter "whose effective date is on or before the cycle's billing period start" (compute = latest notice by effective_date, unfiltered).
  - Demonstrated conflict (constructed situation): latest line cycle 2026-09-04, notices effective 2026-09-01 (0.662) and 2026-10-01 (0.700). The rule gives 0.662 and the compute gives 0.700, so the scored credit differs from what the rule entails.
  - A related latent non-equivalence: `allowed_rate` reads the current plan's rate_type, not the plan in force for the line's cycle.
  - Affected: rebill `compute.var_rate` / `compute.allowed_rate`. Bears on the task claiming the rebill policy (demonstration in its file).
- **F-3 — SOURCE-FACTOR RED (charter-global structure of gas_ext_renewal_loyalty_credit).**
  - F-3a: loyalty_tenure is mislabelled `method`, because its tiers only change a multiplier.
  - F-3b: loyalty_tenure's fall-through (<365 days) is unreachable for every renewal.
  - F-3c: renewed_term's fall-through (<360 days) is unreachable for every renewed term.
  - Surviving factors: 3 (0 method), against the bounds of 4-6 with >=1 method. Evidence as quoted in `factor_ladders`.
  - Bears on the task that claims the loyalty policy.
- Observations (no consequence demonstrated):
  - O-1: banker's `RND` vs "half up". Ties checked per task.
  - O-2: the renewal_rate `ref_cost` zero-usage fallback has no rule sentence.
  - O-3: renewal_rate `net_amount` sums all line types, while the rule enumerates five.
  - O-4: `CFIELD` first-holding semantics for power/protect.
  - O-5: added-premise edge `condition` is narrower than its sentence; loyalty edge `condition` is narrower than "every renewal".
  - O-6: the "Afterwards" wording in the docstrings.
  - O-7: base gas_etf "only once" cross-problem order grounds no edge.
  - O-8: claimed event_types without any extended policy.
  - O-9: cushion_share's "<6" tier is reachable only via a badly early notice.

## closing_checklist

Written after both reveals (2026-10-04T16:26Z). This section is the only part of this file that draws on revealed GT. Everything above it was frozen at 384a61ff…d852 before any task JSON was opened.

- **Audit files.** `0.md` and `1.md` correspond one-to-one with tasks/0.json and tasks/1.json, and this file sits beside them. Round 1, so there are no older revisions. Each comparison section is on disk, but **not every comparison carries a PASS**: see the per-task verdicts.
- **Scope.**
  - `charter_scope`: task 0 = {gas_ext_recontract_rate, gas_ext_added_premise_rate}; task 1 = {gas_ext_latest_bill_rebill_credit, gas_ext_signup_credit, gas_ext_renewal_loyalty_credit, gas_ext_renewal_rate}.
  - The two scopes are pairwise disjoint and together cover all six extended policies. This matches the partition derived blind in § policy_conflict_scan.
  - The task tools are closed: each of the six tools is used by exactly one task's GT. The uuid8 tails are independent (§ action_binding_and_uuids).
- **Problem trees.**
  - Task 0: 1 prerequisite problem, with 1 value_input edge and 1 user-owned write (the re-contract).
  - Task 1: 3 prerequisite problems, with 3 value_input edges and 1 user-owned write (the renewal acceptance).
  - The difficulty-wide graph has no cycle.
  - Both trees hold on their worlds. Task 1's only chain defect is the proof-field figure T1-F3.
- **Factors. Not satisfied.**
  - F-3: gas_ext_renewal_loyalty_credit keeps only 3 real factors and 0 `method`.
  - T0-F1 and T1-F2: household_form and heating_household tiers coincide with the seeded premises.annual_therm_usage = 926.
  - All other factors bear weight against honest baselines, and each baseline gives a definite number different from gold.
- **Policy self-consistency at charter level. Not satisfied.**
  - F-1: gas_ext_latest_bill_rebill_credit carries an undeclared override of gas_variable_rate s1, s2 and s4, and of gas_regulatory_passthrough.
  - F-2: rebill `var_rate` compute drops the rule's "on or before the cycle start" filter.
  - Both are latent: neither task world triggers them.
- **Gate re-run on the final form.** Not done. The artifacts were not changed in this round, so the orchestrator's snapshot stands. check_traceability is still deferred.

**Difficulty verdict (round 1): NOT PASSED.**

| Where | Classes | Findings |
| --- | --- | --- |
| Charter-global | SOURCE-POLICY RED (latent) | F-1, F-2 |
| Charter-global | SOURCE-FACTOR RED | F-3 |
| Task 0 | SOURCE-FACTOR RED | T0-F1 |
| Task 1 | SOURCE-FACTOR RED | T1-F1, T1-F2 |
| Task 1 | SOURCE-CHAIN RED (proof field) | T1-F3 |

On the round's focus question, the independent blind derivation landed exactly on GT in both tasks: every write, owner, order, argument, expected value, factor-sensitivity figure and baseline_result matched. The one exception is a single counterfactual skip figure (0.8107 vs GT 0.8106; T1-F3).

## revision_2

### charter_global_frozen (revision 2)

- **Freeze:** 2026-10-04, written before either round-2 task JSON was opened. Auditor: the same independent auditor as round 1.
- **Inputs, re-verified against `.audit_views/.../HASHES.txt` ("# round 2"):**

  | File | Round 2 hash | Round 1 hash | Status |
  | --- | --- | --- | --- |
  | `gas.extended.yaml` | 25f6cfe75041d5e864fcca19d073f8c4cb36c4445b0cc13f21ce75809c7993ba | 4acba50a…6123 | changed, so every charter section below is re-derived |
  | `task_tools.py` | 6489f6158b4a7e755685ac0faa0884a03e80150e6c3fdc8523767a6f8fd51ca1 | same | unchanged, so § action_binding_and_uuids is carried forward by reference |
  | `blueprint/products/gas.yaml` | 4fdd1fd1…4234 | — | — |

  Lines 1-1208 of the extended charter are still byte-identical to it, so the base copy is verbatim.
- **Masked and unread at freeze:** both round-2 `tasks/*.json`, all worklogs, and every other audit view.
- **Entry conditions:** the orchestrator re-ran the gates after rework and cites EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE OK; CACHE-DIFF is INFO; traceability is deferred. The masked views were rebuilt and their hashes match.
- **Charter diff against round 1:**
  - **gas_ext_recontract_rate:** only the rounding in `start_rate` and `result` changed, from `RND` to `int(x·10⁴+0.5+1e-9)/10⁴`.
  - **gas_ext_added_premise_rate:**
    - the edge `condition` now reads "...again carries a term in months above zero and a non-empty contract end date";
    - the rounding is now `int`-based.
  - **gas_ext_latest_bill_rebill_credit:**
    - `base_policy_refs` now includes gas_regulatory_passthrough;
    - two new rule sentences restrict the scope and send out-of-scope lines to the base correction;
    - the variable-rate sentence is reworded;
    - `over_billed` and `result` use the `int`-based half-up rounding;
    - the `var_rate` compute is unchanged.
  - **gas_ext_signup_credit:** only the rounding changed.
  - **gas_ext_renewal_loyalty_credit:** rebuilt.
    - loyalty_tenure is now `parameter` on `tenure_mult`, with thresholds 1095/730 and a fall-through ×1.
    - loyalty_late_posting is now `method`: per-month accrual from 9 months, a flat 5.00 from 3 months, otherwise none.
    - renewed_term is removed and repeat_renewal is added.
    - home_protection is scoped to the agreement's premise.
    - The `overwrite` replaced_by is updated.
  - **gas_ext_renewal_rate:**
    - the net-cost sentence now says "whatever its kind (… or any other line that carries a billing period)" and adds a zero-usage clause;
    - the loyalty edge `condition` now reads "For every renewal … the latest one being …";
    - the rounding is now `int`-based.

### policy_conflict_scan (revision 2)

Re-run over the new text. The subjects, targets and tool owners are unchanged, so the round-1 scan of overlaps between policies still holds.

- **gas_adjustment, extended vs base:** the extended rebill policy now says outright where its scope ends: "A line outside that scope keeps the allowed rate the gas supply billing, variable rate, rollover and regulatory pass-through rules give it and is corrected under the base gas billing correction rule, without the supplements of this policy". The boundary between the two is therefore declared, not left implicit.
- **Scope partition:** the two components of the prerequisite graph are unchanged, so the partition into {added_premise, recontract} and {renewal_rate, rebill, signup, loyalty} still holds.

### rule_compute_equivalence (revision 2)

**Rounding (round-1 O-1): closed.** Every computation now rounds with `int(x·10ⁿ + 0.5 + 1e-9)/10ⁿ`. For the non-negative magnitudes involved this is half-up, matching "rounded half up". The 1e-9 guard absorbs binary representation error. Because the guard sits below 10⁻⁹ after scaling, it cannot create a false round-up at any precision the rules use.

**gas_ext_latest_bill_rebill_credit, `var_rate` (round-1 F-2): closed for the policy's declared scope.**
- The compute still takes the latest notice by effective date, unfiltered.
- The rule now applies the policy only when "the most recent variable rate change notice on the agreement took effect on or before that cycle's billing period start and was issued at least variable_rate_notice_days ... before its effective date".
- Inside that scope, the notice with the latest effective date has an effective date on or before the cycle start, so it is the notice in force for the cycle. The compute and the rule give the same value.
- The "current plan vs plan of the line's cycle" divergence is also closed: "the line's cycle began on or after the agreement's most recent plan change date, or its service start date when it has none, so that the plan in force today is the plan the line was billed under".
- Residual observation **O-R2-4**: "most recent" is ordered by issue in the rule but by effective date in the compute. The two differ only if notices were issued out of effective-date order. That is contrived, and no world has it.

**gas_ext_latest_bill_rebill_credit, `over_billed` (new observation O-R2-3).** `over_billed = MX(0, lt_amount − int(…)/100)` no longer rounds the difference. An over-billed amount that is exactly 5.00 or 20.00 in decimal can evaluate a hair below the threshold in binary (for example 4.999999999). Its tier would then fall a step, while the rule's "error_mid_usd or more" keeps it. This is latent; see the per-task check.

**gas_ext_renewal_rate, net cost (round-1 O-3): closed.** The rule now names every line kind, and the compute's unfiltered `SUM` matches it.

**gas_ext_renewal_rate, zero-usage fallback (round-1 O-2): closed.** The rule now states "when no energy line falls in that window, the net supply cost per therm is the contract rate", which matches the compute's `else F('contract_rate_usd_therm')`.

**gas_ext_renewal_loyalty_credit, rebuilt:**
- `tenure_mult` with thresholds 1095/730 and else 1; `tenure_amount = plan_amount × tenure_mult`.
- `late_months = MONTHS(plan_change_date, NOW)` matches "whole calendar months".
- `late_supp`: ≥9 months gives months × 2.00; 3–8 months gives 5.00; otherwise 0.
- `prior_loyalty = COUNT(renewal_loyalty_credit)`. The rule says "already standing on the agreement for earlier renewals". Within the policy's scope ("no renewal loyalty credit stands on the agreement for that term"), every standing credit belongs to an earlier renewal, so the two are equivalent.
- `prot_*` = `CFIELD('protect', …, premise_id=F('premise_id'))` matches "at the agreement's premise".
- `result` is rounded half-up.
- Every tier of every ladder is stated in the rule and implemented in the compute.

**Unchanged policies:** recontract, added_premise and signup apart from rounding. Round-1 equivalence is confirmed on the re-read text.

**`CFIELD('power', …)` (round-1 O-4): closed for protect only.**
- The protect read is now premise-scoped.
- The power read in recontract and renewal_rate is still "the customer's first electricity agreement", while the rule says "the customer's ... residential electricity agreement" in the singular. Residual observation; neither world has two power agreements.

### action_binding_and_uuids (revision 2)

`task_tools.py` is unchanged (6489f615…51ca1), so the round-1 section is carried forward by reference. The six tools and their uuid8 tails are claimed as before, by one policy each. No tool judges a prerequisite. The "Afterwards" wording (O-6) remains, as the reworker stated.

### prerequisite_graph (revision 2)

Re-checked:

- The same four edges, all value_input and state-form.
- `policy_source` is verbatim in each blocked rule: added_premise rule line 1423, and renewal_rate rule lines 2035-2037.
- The graph is acyclic.
- `resolved_by` equals the target tool in each case.
- The gate bindings (`home_rate`, `ref_cost`) are still present.

**Edge conditions (round-1 O-5): closed.**
- added_premise: "again carries a term in months above zero and a non-empty contract end date". This now has the sentence's strength, with no provenance clause added.
- loyalty: "For every renewal that has taken effect … the latest one being the renewed term recorded by the plan change date". This now matches "every renewal" in the sentence.

**New observation O-R2-2.**
- The sentence and the condition now require a loyalty credit for *every* past renewal.
- gas_ext_renewal_loyalty_credit settles only the renewal "where the agreement's plan change date records the start of the renewed term".
- If an earlier renewal had lost its credit, no write of this difficulty could bring the waited-on state about. The edge would then be unresolvable from this charter: base gas_renewal s6 is overwritten.
- This is latent, and it depends on the world.

### prerequisite_sentences (revision 2)

- **Prerequisite sentences:** the four are unchanged. The round-1 four-point tests and single-write derivations still hold.
- **New rule text, cross-problem ordering:** none is introduced.
  - Rebill: "A line outside that scope ... is corrected under the base gas billing correction rule" routes the policy's own object. It is not an ordering between problems.
  - Loyalty: the new sentences, including "as they are for a customer renewing for the first time out of a twelve-month term", carry no ordering connective toward another problem.
- **Depended-on rules:** none restates a root sentence.

### override_declarations (revision 2)

**gas_ext_latest_bill_rebill_credit vs gas_variable_rate and gas_regulatory_passthrough (round-1 F-1): closed.** The test is whether any sentence of those base policies still reaches a different allowed rate than the extended rule inside the extended scope.
- **Base s1 (intro and held cycles):** excluded from scope ("past the plan's introductory cycles and is not a cycle held at the expiring rate after a late-notice rollover").
- **Base s2 ("until the first such notice applies, contract_rate continues"):** in scope, a notice that is timely and already effective always exists, so this branch cannot arise.
- **Base s4 (late-notice deferral):** in scope, the most recent notice is timely and in force, so base and extended both give its rate.
- **Base s5 (ceiling):** the extended capped tier takes the same minimum.
- **gas_regulatory_passthrough:** in scope, no pass-through notice stands, so the fixed-plan allowed rate equals the contract rate under both.
- **Lines outside scope:** sent back to the base rules explicitly.
- **Conclusion:** no base sentence is overridden inside the scope, so nothing remains to declare. The two round-1 constructed situations (a late notice, and a held cycle on a Monthly Variable agreement) now fall outside the extended scope. The base rule alone governs them.

**New observation O-R2-1 (no demonstrated consequence).**
- The scope condition on the most recent variable notice is not limited to variable plans: "...when the most recent variable rate change notice on the agreement took effect on or before ..." carries no prefix restricting it to such plans.
- Read literally, an agreement that has only ever been fixed, with no variable notice, is outside this policy and is corrected under the base rule.
- The fixed-plan tier (the fall-through and baseline of allowed_rate_basis) is therefore reachable only by fixed agreements that carry an earlier variable-notice history, for example after a plan change from a variable plan. It stays reachable, so this is not a ladder defect. It is a narrower scope than the tier's wording ("otherwise (a fixed plan)") suggests.

**gas_ext_renewal_loyalty_credit vs gas_renewal s6:** still declared, and the `replaced_by` now names the repeat-renewal supplement in place of the term supplement.

**All other policies:** unchanged from round 1 and clean.

### factor_ladders (revision 2)

**gas_ext_renewal_loyalty_credit, rebuilt (round-1 F-3): closed.**

| factor | label | ladder | assessment |
| --- | --- | --- | --- |
| loyalty_tenure | parameter, on `tenure_mult` | ≥1095 d → ×2.0; 730–1094 → ×1.5; else ×1 | Honest: a multiplier value. |
| loyalty_late_posting | method | ≥9 whole months → 2.00 × months; 3–8 → flat 5.00; else none | Honest: linear accrual vs constant vs none. |
| repeat_renewal | parameter | ≥2 earlier loyalty credits → 10.00; 1 → 5.00; 0 → 0 | — |
| home_protection | parameter, cross protect, premise-scoped | unchanged | — |
| loyalty_winter_peak | parameter | unchanged | — |

Reachability of every tier, including each fall-through:

- **loyalty_tenure:**
  - The first renewal out of a 12-month term (365/366 d) falls through.
  - The second 12-month renewal, or the first out of a 24-month term (≈730), is mid.
  - The third 12-month renewal, or the first out of a 36-month term (≈1095), is long.
  - The round-1 F-3b universality is gone.
- **loyalty_late_posting:** the policy settles once ≥1 energy line of the term has been billed, which is about 1 month in, so "<3 months" is reachable.
- **repeat_renewal:** "none" is the first renewal.
- **home_protection:** "no plan at the premise" is reachable.
- **winter_peak:** "<110" is reachable.

No two tiers of any ladder select the same value or method. Counts: 5 factors (4 parameter, 1 method), 1 cross_difficulty (protect). The structure is within bounds.

**Other policies:** factors unchanged.
- recontract: 5 factors (1 method), cross power, multi-source.
- added_premise: 5 factors (1 method), cross power, multi-source.
- rebill: 4 factors (1 method). Their reachability needs re-reading under the new scope:
  - Capped tier: reachable.
  - Month-to-month tier: reachable past intro and held cycles.
  - Fixed tier: reachable only with an earlier variable-notice history (O-R2-1).
- signup: 4 factors (1 method).
- renewal_rate: 6 factors (2 method), cross power, multi-source.

Per-component floors (multi-source and cross_difficulty) hold as in round 1.

### findings (revision 2, pre-reveal)

**Round-1 charter-global REDs:**

| Finding | Status | Evidence |
| --- | --- | --- |
| F-1 (undeclared override) | **closed** | § override_declarations (revision 2) |
| F-2 (var_rate compute vs rule) | **closed within the declared scope** | § rule_compute_equivalence (revision 2) |
| F-3 (loyalty ladders) | **closed** | § factor_ladders (revision 2) |

**Round-1 observations:**

| Observation | Status |
| --- | --- |
| O-1, O-2, O-3, O-5 | closed |
| O-4 | closed for protect; the power first-holding read remains |
| O-6, O-7, O-8, O-9 | unchanged, as the reworker stated |

**New charter-global observations (no consequence demonstrated at charter level; per-task checks in the task files):**
- **O-R2-1:** the rebill scope is narrower than the fixed-plan tier wording.
- **O-R2-2:** the "every renewal" loyalty prerequisite is unresolvable if an earlier renewal lacks its credit.
- **O-R2-3:** the rebill `over_billed` amount is unrounded at the 5.00 and 20.00 thresholds.
- **O-R2-4:** "most recent notice" is ordered by issue date in the rule but by effective date in the compute.

**No new charter-global RED.**

### closing_checklist (revision 2)

Written after both round-2 reveals at 2026-10-04T17:47Z. Everything above in revision_2 was frozen at d0dc7367…cea5 before the reveals.

- **Files.**
  - `0.md` and `1.md` each carry an appended `## revision_2`; the round-1 text is untouched.
  - Both revision-2 comparisons are PASS.
- **Scope.**
  - charter_scope: task 0 {recontract, added_premise}; task 1 {rebill, signup, loyalty, renewal_rate}.
  - The two scopes are disjoint and together cover all six extended policies.
  - The six tools are closed, with independent uuid8 tails (tools file unchanged).
- **Trees.**
  - Task 0: 1 prerequisite, 1 value_input edge, 1 user write.
  - Task 1: 3 prerequisites, 3 value_input edges, 1 user write.
  - The graph is acyclic, the topological order matches the GT order, and every edge bears weight on its world.
- **Factors.**
  - Every computation has a self-sufficient baseline giving a definite number that differs from gold.
  - Factor counts per computation:

    | computation | factors | method factors |
    | --- | --- | --- |
    | recontract | 5 | 1 |
    | added premise | 5 | 1 |
    | rebill | 4 | 1 |
    | signup | 4 | 1 |
    | loyalty | 5 | 1 |
    | renewal | 6 | 2 |

  - Every ladder has at least three reachable, distinct tiers, all stated in its rule.
  - Each task has at least one multi-source factor and at least one cross-difficulty factor, and the cross-difficulty rows are seeded.
  - Every factor bears weight against an honest baseline.
  - No seeded field agrees with a factor tier: annual_therm_usage is now 868 (task 0) and 874 (task 1) against window totals of 926.
- **Policy self-consistency.** F-1 and F-2 are closed (rebill scope with base fallback). No undeclared override remains.
- **Round-1 REDs.**
  - F-1, F-2, F-3 / T1-F1, T0-F1, T1-F2 and T1-F3 are all closed, with evidence in their sections.
  - O-1, O-2, O-3 and O-5 are closed in the charter. O-5's task-0 proof copy is stale; see the observation below.
  - O-4 is closed for protect.
  - O-6 to O-9 are unchanged.
- **New this round. Observations only; no RED.**
  - O-R2-1: rebill scope is narrower than the fixed-plan tier wording.
  - O-R2-2: the "every renewal" loyalty prerequisite cannot be settled if an earlier renewal lacks its credit. Not triggered in task 1.
  - O-R2-3: rebill `over_billed` is unrounded at the 5.00 and 20.00 thresholds. Not triggered: the amount is 5.68.
  - O-R2-4: notice ordering by issue date in the rule vs by effective date in the compute.
  - O-T0-R2: tasks/0.json `prerequisite_closure.edges[0].condition` still carries the round-1 provenance clause that the charter's condition dropped. The clause is true on that world, so this is not a RED.
- **Gates.** The orchestrator's post-rework snapshot is cited as is (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK). check_traceability is still deferred until the KB is published, so it is open for the KB stage, not this audit.

**Difficulty verdict, revision 2: PASS** (source-layer: policy self-consistency, problem tree, factor weight and unique solution all PASS for both tasks). Open observations are listed above for the KB stage and later rounds.
