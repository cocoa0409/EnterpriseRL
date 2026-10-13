# Policy-task audit — comfort_club_membership_care / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (Claude agent run by the erl-task-policy-audit skill). It did not write any of the audited artifacts.
- Freeze time: 2026-10-05T15:47Z (UTC). This section was written before any task's GT was revealed, and nothing in it comes from a revealed GT.
- Frozen inputs (sha256, checked against `/tmp/erl37/views/comfort_club_membership_care/charter.sha256`, which matched):
  - `tasks/comfort_club_membership_care/plan.extended.yaml` `e9e5cd250658d75463d4cdff0a8e4a0c08a3d7f3e9ed81790ac9453cc70e9203`
  - `tasks/comfort_club_membership_care/task_tools.py` `60a3229fca6c0b7a1d9a389f71eda281f513f44f2d0051c260b917440cf652b8`
  - masked views `task_0.masked.json` `26a132d2…ccece` and `task_1.masked.json` `7e2cf218…2bd4`
- Permitted reads: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/plan.yaml`, plus `service.yaml` (only the `labor_multiplier` lines), `warranty.yaml` and `install.yaml` (grep for field names); the extended charter; `task_tools.py`; the masked views (`frozen_time`, `user_scenario`, `initial_state`); and `erlbench/` together with the gate script DSL (`skills/erl-task-instantiate/scripts/check_compute.py`, read for the semantics of MONTHS, DAYS, SUM/COUNT/XSUM/XCOUNT/XLATEST/XMAX, CFIELD and `within_months`).
- Masked and unread at freeze: everything in `tasks/*.json` other than the three permitted fields (`evaluation_criteria`, `computations`, `db_closure`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`). `env/env_0037_residential_hvac_company/worklog.md` was also left unread.
- Entry conditions (Step 0): the coordinator supplied the gate snapshot at `/tmp/erl37/gates/comfort_club_membership_care.snapshot.txt` with its actual output lines: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (0.json 16 acts, 1.json 19 acts, match True), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK. check_traceability is deferred until KB publication. Masked views and hashes were supplied. Input complete.
- Base copy: every top-level key of `products/plan.yaml` (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies) is structurally identical in `plan.extended.yaml` (yaml-parsed equality). The only added key is `extended_policies`, which holds 6 policies.

### policy_conflict_scan

The extended policies are:

| id | trigger | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| plan_ext_covered_repair_draw | state_due | post_covered_repair_draw_a854dec6 (agent) | draw_amount | [] |
| plan_ext_cancellation_settlement | on_request | confirm_agreement_cancellation_08dfa488 (user) | proration_credit | -> covered_repair_draw (value_input, state) |
| plan_ext_reinstatement_fee | on_request | reinstate_lapsed_agreement_6e8e1b28 (agent) | reinstatement_fee | [] |
| plan_ext_reinstated_rate_lock | on_request | set_reinstated_rate_lock_0c66ac3f (agent) | locked_annual_rate | -> reinstatement_fee (state_gate, state) |
| plan_ext_missed_visit_fee | state_due | post_missed_visit_fee_325d3ccb (agent) | fee_amount | -> reinstatement_fee (state_gate, state) |
| plan_ext_reinstated_term_dues | on_request | pay_reinstated_term_dues_c2f743bd (user) | term_dues | -> reinstatement_fee (value_input, state); -> rate_lock (value_input, action); -> missed_visit_fee (value_input, state) |

- Overlapping subjects: plan_ext_reinstated_term_dues and plan_ext_reinstated_rate_lock both settle a figure the base names `locked_annual_rate` / the first-system rate of the reinstated term. They are compatible. The rate lock writes `locked_annual_rate`, and the term-dues price-lock rule reads the locked rate on file. Only one policy writes each quantity.
- plan_ext_reinstatement_fee and plan_ext_reinstated_rate_lock both overwrite the same base sentence of plan_reinstatement ("A reinstated agreement loses its price lock: …"), each with a different replaced_by. The two replacements are compatible: one defers the locked rate and dues to "the policies that settle them", and the other settles the locked rate. No contradiction.
- Triggers and eligibility:
  - The draw and the cancellation both require an active agreement (base `draw_on_active_agreement`). Cancellation makes the agreement cancelled, so base order and extended order agree.
  - The reinstatement chain (fee, lock, missed fee, dues) all operates inside base `within_renewal_grace`.
  - The missed-fee rule's gate ("not posted until … back in active status") is compatible with base `forfeiting_tier`.
- Time anchors: each policy uses "the date of handling" consistently. In the rate-lock and term-dues computes, "days since lapse" is `DAYS(F('term_start'), NOW) + 1`, which equals the rule's "calendar days from the lapsed term's last day" only after the reinstatement write has moved term_start (see O-8).
- Cross-category read boundaries:
  - draw reads service (lines, call class) and warranty (tier)
  - cancellation reads install (member credit) and service (member repair discounts)
  - reinstatement fee reads install (member credit date) and warranty (tier)
  - rate lock reads install (registration years) and warranty (tier)
  - term dues reads install (installed date), service (repair totals) and warranty (purchase channel)

  All reads are declared in `cross_category`, and the gate reports cross-cat=5.
- Claimed scopes: the prerequisite graph has two weakly connected components, {covered_repair_draw, cancellation_settlement} and {reinstatement_fee, rate_lock, missed_visit_fee, reinstated_term_dues}. The two tasks' worlds instantiate exactly these, each from its user-tool root (task 0: cancellation; task 1: term dues). As derived pre-reveal, the components are mutually exclusive and jointly complete over the 6 extended policies. The declared `charter_scope` is checked after reveal in each task file.

### rule_compute_equivalence

For all six policies, every `compute_basis` quotation was checked verbatim against the policy's own `rule` after whitespace normalisation, and all are present. Every sentence of each `baseline.rule` is a sentence of its `rule`. Every ladder tier named in `factors[].ladder` is stated in the rule and is a branch of the `decides` binding. Every branch of the binding is a tier the rule states.

Sweep back (rule sentences with no compute counterpart, or compute bases the rule does not state):

- plan_ext_covered_repair_draw:
  - The rule scopes the draw to "a completed service call … on an enrolled system", to "the repair lines of that call", "the member refrigerant allowance already posted on the call", "any protection contract coverage already posted on the call", "thermostat replacement and condensate pump replacement are never covered", and "A draw is posted only for a call booked no earlier than the tier's covered-repair waiting period after the agreement's first covered-repair grant".
  - The compute implements none of these per-call or per-task restrictions. `draw_parts_billed` / `draw_labor_billed` / `draw_refrigerant_*` / `draw_warranty_paid` are `XSUM` over every `service_lines` row of the customer posted within one month. `draw_call_class` is `CFIELD('service','variant_name',status='completed')`, which takes the first completed call. No `task_code` exclusion exists for thermostat or condensate-pump lines, and no waiting-period test exists.
  - These are rule promises with no compute counterpart (O-1). Whether either task's world exercises them is decided in that task's file. Pre-reveal reading of task 0's world: its thermostat call (2026-09-03) falls outside the one-month window, so this world does not exercise the gap.
- plan_ext_cancellation_settlement: "posted since the current term began" (term dues billed, member repair discounts) is implemented as a whole-month window `within_months = MONTHS(term_start, NOW) + 1`. That window also admits rows posted before term_start inside the same month span (O-2). Every other quantity, tier and rounding has a basis quote.
- plan_ext_reinstatement_fee: all bindings are quoted. "rounded up to the next whole dollar" is implemented as `-(-(x)//30)`, and "held … when it lapsed" reads `F('consecutive_terms')` at the opening (pre-reinstatement), which is correct.
- plan_ext_reinstated_rate_lock: all bindings are quoted. The result has a cap ("never above") and no floor, consistent with the rule.
- plan_ext_missed_visit_fee: the rule says "The fee is worked out for the most recent forfeited visit that carries no fee". The compute's `miss_late_cancel_date` / `miss_no_show_date` are LATEST over all forfeits, so it does not filter "carries no fee" (O-3).
- plan_ext_reinstated_term_dues:
  - "most recently closed Harbison installation" is `CFIELD('install','installed_date',status='closed')`, which returns the first closed project rather than the most recent (O-4).
  - The `compute_basis` of `result` quotes "The term dues are the discounted dues for the whole term.", which is the baseline sentence. The bound value is the gap-rule outcome. This is wording only.
- Rounding: `RND` in the gate DSL is Python `round` on binary floats, while every rule says "half up" (O-5). Whether a tie occurs on a scored path is checked per task.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: there are 6 distinct tools and 6 distinct computes, and each pair is claimed by exactly one policy.
- uuid8s: a854dec6, 08dfa488, 6e8e1b28, 0c66ac3f, 325d3ccb, c2f743bd. They share no common prefix, suffix or sequence, are not adjacent values, and none is reused.
- Docstrings: none names another tool, a policy id or a sequence position. "after" occurs only as a date description ("starts the day after the lapsed term's last day"), and "once" only in a return-value description ("the benefit left in the term once the draw is posted").
  - Two tools name their object by state: `set_reinstated_rate_lock_0c66ac3f` ("a reinstated Comfort Club agreement") and `pay_reinstated_term_dues_c2f743bd` ("their reinstated Comfort Club term"). This is not an ordering word, but the object naming already presumes the reinstated state (O-9).
- Function bodies: none of the six tools validates a status, an eligibility or a prerequisite, and none refuses or hints. Each performs a write unconditionally (`ctx.find`, `ctx.create`, `ctx.update` only).
- Tool effects versus inherited base:
  - `reinstate_lapsed_agreement_6e8e1b28` moves dates, status, consecutive_terms and the fee. It posts no visit grant and no coverage grant for the new term. Base plan_reinstatement still says "Reinstatement returns the agreement to active and renews it exactly as an automatic renewal would", and base plan_renewal says that renewal grants "the new term's visits and covered-repair benefit". The extended rule overwrites only the price-lock/dues and fee sentences (O-6).
  - `confirm_agreement_cancellation_08dfa488` has no cancellation-fee parameter, while base "a cancellation_fee of cancellation_fee_usd is charged where it is above 0.00" is inherited (O-14; latent for tiers whose fee is 0.00).

### prerequisite_graph

Check 7:

- Every policy fills `prerequisite`. Draw and reinstatement fee are `[]`.
- Every `problem` points at another extended policy id in this file, never at a base policy or itself.
- Edges: cancellation->draw; rate_lock->reinstatement_fee; missed_visit_fee->reinstatement_fee; term_dues->{reinstatement_fee, rate_lock, missed_visit_fee}. The graph is acyclic, and the difficulty-wide graph is the union of two DAGs.
- Each `policy_source` is found verbatim in that policy's own `rule` (script check, whitespace-normalised, 6/6 True).
- `form`: five edges are `state` and one is `action` (term_dues->rate_lock), and only that edge carries `fallback_reason`.
- `kind` / `gate`:
  - value_input gates `settle_coverage_drawn`, `due_gap_days`, `due_first_rate` and `due_loyalty_pct` are real compute bindings of the blocked policy.
  - state_gate gates `plan_agreements.status` (rate lock, missed fee) point at the status field that the base `within_renewal_grace` and the lifecycle `lapsed -> active` transition govern.
- `resolved_by` is in every case the depended-on policy's `target_tool`, and the function body makes the stated state hold:
  - reinstate sets status=active, term_start=old term_end+1 and consecutive_terms+1
  - the draw creates a `plan_coverage_draw` entry with term_start=current term
  - the missed fee creates a `missed_appointment_fee` charge
  - the rate lock writes `locked_annual_rate`
- `condition` versus sentence strength:
  - rate_lock->reinstatement_fee's condition adds "with the consecutive term count raised by one", and term_dues->reinstatement_fee's condition adds "its term end one day before the same date twelve months later". Both are consequences of the same single write, so no second reading results (O-7).
  - Other conditions match their sentences.
- `effect` assertions:
  - term_dues->reinstatement_fee says "so the days since lapse fall within the grace period", and rate_lock->reinstatement_fee says "so the days since lapse are counted from the reinstated term". Both are true of the compute (`DAYS(F('term_start'),NOW)+1`). They are not true of the rule, which defines the days since lapse from "the lapsed term's last day", a date readable at the opening (O-8).
  - The weight of these edges is judged per task on other grounds (term end, consecutive count and status move with the write).
- No authoring-viewpoint phrasing ("in this task", "at the opening") occurs in any `prerequisite` field.

### prerequisite_sentences

Check 6, edge by edge:

1. **cancellation -> draw (state).** "The cancellation credit is fixed only after every completed service call on an enrolled system with repair lines posted since the current term began carries its covered-repair draw on the agreement."
   - Ordering connective: "only after".
   - The waited-on state is record-visible: a `plan_coverage_draw` service entry naming the call (`find_plan_service_entries(ticket_id=…)`).
   - No tool name, policy id or snake_case token. The strength matches the condition: "every completed member service call … whose repair lines were posted in the current term".
   - Exactly one write of this difficulty creates a coverage-draw entry: `post_covered_repair_draw_a854dec6`.
   - Derivation: the sentence plus the records (calls completed with repair lines since term_start, versus draw entries naming them) plus the draw rule ("A covered-repair draw settles a completed service call … posted as one draw for the call naming the call …") lead to one reading: post the draw for each such call. The draw rule does not restate the sentence.
2. **rate_lock -> reinstatement_fee (state).** "The locked rate for a reinstated term is set only once the agreement shows active status with a current term that began the day after the lapsed term ended."
   - Connective: "only once". The state is record-visible (status, term_start). Only `reinstate_lapsed_agreement_6e8e1b28` sets lapsed->active with such a term_start. One reading. The reinstatement rule does not restate it.
3. **missed_visit_fee -> reinstatement_fee (state).** "A missed-appointment fee for a visit forfeited in a lapsed term is not posted until the agreement is back in active status with its reinstated term on record."
   - Connective: "not … until". The state is record-visible. One write brings it about. One reading.
   - The scope is "a visit forfeited in a lapsed term". The edge condition does not narrow this further, and a fee for a forfeit in a non-lapsed term is not gated, which is consistent with the sentence.
4. **term_dues -> reinstatement_fee (state).** "The dues of a reinstated term are fixed only after the agreement shows active status with a term starting the day after the lapsed term ended." Connective: "only after". Record-visible state, one write, one reading.
5. **term_dues -> rate_lock (action, fallback).** "The dues of a reinstated term are not billed until the price lock for that term has been decided."
   - Connective: "not … until". It names the depended-on action in business words, with no tool or id.
   - Fallback test: the rate-lock write changes only `plan_agreements.locked_annual_rate`, and the agreement carried a figure in that field before. The schema has no dated or term-tagged lock record (`plan_agreements` fields listed in db_schema.json), so no record-visible state singles out that the decision was made. **The fallback is justified.**
6. **term_dues -> missed_visit_fee (state).** "The dues of a reinstated term are not fixed until the dues ledger carries a missed-visit fee for every visit forfeited in the lapsed term."
   - Connective: "not … until". The state is record-visible: a `missed_appointment_fee` charge per forfeit of the lapsed term.
   - The only tool creating such a charge is `post_missed_visit_fee_325d3ccb`. One reading. The missed-fee rule does not restate it.

Other checks:

- Undeclared cross-problem orders in extended rules: none.
  - "fees standing on the agreement are billed separately" (term dues) states no order.
  - "the locked rate and the dues of the reinstated term are decided by the policies that settle them" (reinstatement fee) states no order.
- Base sentences stating a cross-problem order:
  - plan_evt_repair_coverage "Covered-repair benefit is drawn only while the agreement status is active." implies draw-before-cancellation.
  - plan_cancellation_refund "A cancellation proration credit is posted only to an agreement whose status is cancelled."

  The task 0 tree does not rest on either alone, because the extended cancellation rule carries its own prerequisite sentence. Observation (O-10).

### override_declarations

Check 1, sentence by sentence against each `base_policy_refs` entry (finding half only; consequences are demonstrated in the task files):

**plan_ext_covered_repair_draw** (refs plan_evt_repair_coverage, plan_evt_tuneup_allowance):

- Declared:
  - "diagnostic fees, … refrigerant, … never covered" -> refrigerant at the coverage rate.
  - "The draw for one service call is the lowest of the remaining covered amount of its covered lines, … allocated to the covered lines in invoice order and posted as one draw per line it pays." -> lowest of the call's covered amount, the cap and the remaining benefit; one draw per call.
- **Undeclared:**
  - Base sentence: "The member repair discount is applied to the line first; when a protection contract claim pays part of the same line, that warranty coverage is applied next, and the plan covers what remains."
  - Extended does not let "the plan cover what remains". It values labor at a daytime rate (divides by 1.25 or 1.5), multiplies the discounted sum by a covered share (0.6, 0.85 or 1.0), adds refrigerant, subtracts warranty coverage, and **subtracts a member deductible (0, 25 or 50)**.
  - This is the "anonymous intermediate factor" form: the base measure `plan_msr_ticket_covered_repair_net` (repair lines less member discount and warranty credits) is the "what remains" figure. No `overwrite` entry names this sentence or the base formula `draw: min(plan_msr_ticket_covered_repair_net, …)`.
  - -> **CG-1**.
- Followed (inherited, compatible):
  - grant per term
  - grant only to pending/active
  - "drawn only while … active"
  - waiting period
  - flood/fire/freeze and not-enrolled exclusions
  - expiry
  - plan_evt_tuneup_allowance as a whole (read only)

**plan_ext_cancellation_settlement** (refs plan_cancellation_refund, plan_evt_tuneup_allowance, plan_evt_repair_coverage):

- Declared:
  - the full-refund credit sentence -> the new credit composition
  - the outside-window credit sentence -> unused-months refundable dues
- Followed:
  - member-confirmed cancellation; effective on the confirmation date
  - full-refund window counted from term_start as day 0, inclusive
  - the credit is never negative
  - a credit is posted only to a cancelled agreement
  - monthly agreements earn no credit
  - expiry of remaining visits and benefit (agreement_closed)
  - refund_payout of a negative balance
  - "a cancellation_fee of cancellation_fee_usd is charged where it is above 0.00" (inherited unchanged; O-14 concerns the tool)
- The extended refund-basis middle tier (days/365 for a long-standing member with notice within 60 days) deviates from base "Outside the window … unused full months". That base sentence is named in the overwrite, and the extended baseline-plus-ladder states the tiers. Declared.

**plan_ext_reinstatement_fee** (refs plan_reinstatement, plan_evt_missed_appointment):

- Declared: the fee sentence and the price-lock sentence.
- Followed: grace counting; closure at grace end; "returns the agreement to active … new term starting the day after the old term_end … consecutive_terms continues".
- Not carried out by the tool: "renews it exactly as an automatic renewal would" also implies the new term's visit and coverage grants (base plan_renewal), and neither the extended rule nor the tool does this (O-6).
- plan_evt_missed_appointment is read only (forfeits).

**plan_ext_reinstated_rate_lock** (refs plan_dues_pricing, plan_renewal, plan_reinstatement, plan_tier_changes):

- Declared: the price-lock sentence of plan_reinstatement.
- plan_dues_pricing's automatic-renewal clause "the first-system rate for the new term is the lower of the agreement's locked_annual_rate and the current annual_dues_first_system_usd" concerns the rate billed, not the rate written as locked. It reaches reinstatement only through "renews it exactly as an automatic renewal would". It is compatible with the rate-lock write: that write sets a locked rate, and the term-dues policy decides the billed rate.
- plan_tier_changes: no overlap.

**plan_ext_missed_visit_fee** (refs plan_enrollment_eligibility, plan_dues_pricing, plan_billing_collections, plan_evt_missed_appointment, plan_reinstatement, plan_cancellation_refund, plan_tier_changes, plan_evt_add_system):

- Declared: "a missed_appointment_fee of missed_appointment_fee_usd is charged".
- Other refs: no sentence of theirs governs the fee amount.
- The events-section trigger `plan_tuneup_visit -> plan_dues_charge(missed_appointment_fee)` (fee at forfeit time) is structural and not a policy sentence (O-13).

**plan_ext_reinstated_term_dues** (refs plan_billing_collections, plan_dues_pricing, plan_reinstatement):

- Declared: the plan_dues_pricing loyalty sentence -> combined discount percentage.
- **Undeclared (CG-2):**
  - (a) plan_dues_pricing "Annual dues for a term are annual_dues_first_system_usd plus annual_dues_additional_system_usd for each enrolled system beyond the first, billed once in advance as annual_dues for the first term or renewal_dues for later terms, with billing_period equal to the month of term_start." Extended multiplies the additional-system rate by an **additional-system share** (0.6, 0.8 or 1) and, by the **gap rule**, bills only months/12 or days/365 of the term rather than the term's dues once in advance.
  - (b) plan_dues_pricing "… and additional systems are billed at the current catalogue rate." This is the automatic-renewal clause, reaching reinstatement through plan_reinstatement's "renews it exactly as an automatic renewal would". Extended bills them at 0.6 or 0.8 of catalogue.
  - (c) The same automatic-renewal clause "the first-system rate for the new term is the lower of the agreement's locked_annual_rate and the current annual_dues_first_system_usd". Extended's price-lock tier 2 gives the **average** of locked and current for agreements under 5 consecutive terms. This conflict is latent where the agreement holds 5 or more terms (tier 1 then gives the locked rate, which equals the lower of the two).
  - None of (a) to (c) is named in the policy's `overwrite`. The policy's own `base_policy_refs` include plan_dues_pricing, and its only overwrite on that policy is the loyalty sentence, so by its own declaration the other plan_dues_pricing sentences are inherited.
- Followed: plan_billing_collections (payment recording). The order of payment application ("oldest unpaid charge first") is not balance-affecting under the tool's netting (O-15).

### factor_ladders

Structure only. Weight is assessed per task.

| policy | factors (effect) | P / M | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- |
| covered_repair_draw | after_hours_labor_valuation (method*), maintenance_covered_share (param), loyal_member_call_cap (param), sealed_system_refrigerant_rate (param), protection_holder_deductible (param) | 4 / 1* | call_cap (terms x draws), refrigerant_rate (task lines x terms) | service (labor, refrigerant), warranty (deductible) |
| cancellation_settlement | notice_refund_basis (method), long_tenure_visit_rate (param), claim_history_coverage_rate (param), install_credit_recapture (param), member_discount_recapture (param) | 4 / 1 | notice basis tier 2 (request date x terms), visit_rate (enrolled date x visit count), coverage_rate (terms x draws) | install, service |
| reinstatement_fee | lapse_length_fee (method), tenure_fee_share (param), forfeited_visit_surcharge (param), installation_customer_courtesy (param), protection_holder_courtesy (param) | 4 / 1 | tenure share (terms x ledger) | install, warranty |
| reinstated_rate_lock | lock_retention (method), maintenance_lock_surcharge (param), registration_lock_credit (param), protection_lock_credit (param) | 3 / 1 | retention (lapse days x lock on file x terms) | install, warranty |
| missed_visit_fee | repeat_miss_fee (param), tenure_fee_cap (param), attendance_reduction (param), forfeit_treatment (method) | 3 / 1 | forfeit_treatment (forfeit entry x terms) | none |
| reinstated_term_dues | price_lock_application (method), new_installation_share (param), appointment_loyalty (param), trouble_free_discount (param), protection_bundle_discount (param), lapse_gap_proration (method) | 4 / 2 | price lock, loyalty (terms x ledger), gap | install, service, warranty |

Every ladder has three pairwise-disjoint tiers as stated. Every fall-through equals the factor's `baseline` binding, and every `decides` is an input, never `result`. Bindings are disjoint across factors within each policy.

Label honesty:

- **after_hours_labor_valuation is mislabelled (CG-3).**
  - Its three tiers are "divided by the overnight and holiday labor multiplier (1.5)", "divided by the evening and weekend labor multiplier (1.25)" and "taken as billed" (division by 1).
  - That is one formula, `labor / m`, with a different number substituted. The divisors are exactly the service charter's class `labor_multiplier` values (service.yaml: Standard 1.0, Same-Day 1.0, Evening 1.25, Weekend 1.25, Overnight 1.5, Holiday 1.5).
  - The rounding step is a no-op at m=1 on cent-valued lines.
  - Under the skill's test ("a factor labelled method whose tiers only substitute a different number into the same formula (a rate, a fee, a threshold)") it is a `parameter`.
  - Struck as a method, the draw computation has 5 parameter factors and **0 method factors**, below the bound of 1 method per computation.
- The other method factors change the algorithm:
  - notice basis: full / days÷365 / months÷12
  - lapse fee: none / flat / ceil(fee × days÷30)
  - retention: keep / interpolate half-way / current
  - price lock: locked / average / current
  - gap: months÷12 / days÷365 / whole
  - forfeit treatment: floor(x/2) / ceil(3x/4) / x, where the rounding direction changes with the factor. This one is borderline and recorded as an observation.

Ladder reality:

- **Vacuous condition parts (CG-4).** These hold for every customer who reaches the write:
  - "within its renewal grace period" in lock_retention tier 2, price_lock_application tiers 1 and 2, and lapse_gap_proration tiers 1 and 2. Every agreement reaching the rate-lock or term-dues write was "reinstated within its renewal grace period" (each rule's scope sentence, and base `within_renewal_grace`).
  - "with a locked rate on file" in lock_retention tiers 1 and 2, on a policy scoped to "a tier that carries a price lock". Base enrollment, renewal and tier-change all write a nonzero `locked_annual_rate` on such tiers.
- **Same value across tiers, or tiers no business would publish, on some tier variants (CG-5):**
  - repeat_miss_fee: on Comfort Club Basic and Silver, `missed_appointment_fee_usd` = 35.0 = `fee_second_miss` 35.0, so tier 2 and the fall-through select the same value.
  - lapse_length_fee: on Platinum, Platinum Plus and Total Home, `reinstatement_fee_usd` = 0.0, so all three tiers select 0.
  - loyal_member_call_cap: on Comfort Club Total Home, `covered_repair_per_incident_cap_usd` = 1500, so the "long-standing" (1000) and "steady-member" (875) loyalty tiers *lower* the cap of the most loyal members below the ordinary member's. This is a treatment no business would publish as a loyalty reward.
  - On the tier variants the two tasks use (Platinum Plus, Gold) these ladders are distinct and monotone.
- Business realism observations (no demonstrable "no business would" claim, O-11):
  - A manufacturer parts registration and a protection contract lower a membership's locked rate.
  - A free 2-Year Workmanship Warranty lowers the plan deductible.

Counts per policy (after striking CG-3), against 4–6 factors, at least 2 `parameter` and at least 1 `method`:

- draw 5 factors (5 P / **0 M**: fails)
- cancellation 5 (4/1)
- reinstatement fee 5 (4/1)
- rate lock 4 (3/1)
- missed fee 4 (3/1)
- term dues 6 (4/2)

Per task, both components carry multi-source and cross-difficulty factors (draw+cancellation: service/warranty/install; reinstatement chain: install/service/warranty).

### findings

- **CG-1 — SOURCE-POLICY RED (undeclared override).** Bears on task 0.
  - Symptom: base plan_evt_repair_coverage says "the plan covers what remains" after the member discount and warranty. Extended plan_ext_covered_repair_draw inserts a labor revaluation, a covered-share multiplier and a member deductible into that same quantity.
  - Root cause: the overwrite list names only the "never covered" sentence and the "draw … lowest of …" sentence.
  - Evidence: plan.extended.yaml lines 1384–1385 (base) versus 1580–1585 and 1590–1598, 1607–1609 (extended); overwrite entries at 1540–1556.
  - Consequence: demonstrated against task 0's world in `0.md`.
- **CG-2 — SOURCE-POLICY RED (undeclared overrides).** Bears on task 1.
  - Symptom: plan_ext_reinstated_term_dues prorates the reinstated term's dues (gap rule) and discounts additional systems (additional-system share), and its price-lock tier 2 averages locked and current rates. Inherited plan_dues_pricing says annual dues for a term are first-system plus full catalogue additional rates, billed once in advance, and at an automatic renewal the first-system rate is the lower of locked and current.
  - Root cause: the term-dues overwrite names only the loyalty sentence.
  - Evidence: plan.extended.yaml 950–952, 958–960 (base) versus 2563–2567, 2570–2592 (extended), 2528–2535 (overwrite).
  - Consequence: demonstrated in `1.md`.
- **CG-3 — SOURCE-FACTOR RED (mislabelled method).** Bears on task 0.
  - Symptom and root cause: after_hours_labor_valuation's tiers substitute divisors 1.5, 1.25 and 1 into one formula. Struck, the draw computation has no method factor.
  - Evidence: lines 1659–1672, 1629; service.yaml `labor_multiplier` lines 98/159/219/278/337/393.
- **CG-4 — SOURCE-FACTOR RED (vacuous condition parts).** Bears on task 1.
  - Symptom: "within its renewal grace period" and "with a locked rate on file" restate the scope of the rate-lock and term-dues policies inside tiers of lock_retention, price_lock_application and lapse_gap_proration.
  - Evidence: lines 2233–2234, 2240–2244, 2304–2306 (rate lock) and 2558, 2570–2574, 2586–2592, 2689–2691, 2764–2766 (term dues).
- **CG-5 — SOURCE-FACTOR RED (unreal ladders on some tier variants; latent on both tasks' worlds).**
  - repeat_miss_fee tier 2 equals the fall-through on Basic/Silver (35 = 35).
  - lapse_length_fee all tiers equal 0 on Platinum and above.
  - loyal_member_call_cap's loyalty tiers lower the cap below the fall-through on Total Home (1000 and 875 < 1500).
  - Evidence: variants table (plan.extended.yaml 113–465) against params at 1567–1570, 2387–2388 and 2045–2046.
  - Neither task's tier variant (Platinum Plus, Gold) exhibits the collapse or inversion.
- Observations (no consequence demonstrable on any task world; each task file checks whether its world exercises them):
  - O-1: draw compute omits per-call scoping, the enrolled-system test, the thermostat and condensate-pump exclusion and the waiting period. It also aggregates across calls and picks the first completed call.
  - O-2: cancellation "since the term began" is implemented as a whole-month window.
  - O-3: missed fee's "most recent forfeit that carries no fee" is not filtered.
  - O-4: CFIELD takes the first closed install, not the most recent.
  - O-5: RND uses banker's rounding on binary floats against the rules' "half up".
  - O-6: the reinstate tool omits the new term's visit and coverage grants that base "renews it exactly as an automatic renewal would" implies.
  - O-7: conditions are slightly stronger than their sentences (same write).
  - O-8: edge `effect` text describes compute mechanics ("days since lapse fall within grace") that the rule does not share.
  - O-9: tool names and docstrings presume the "reinstated" state.
  - O-10: base sentences imply draw-before-cancellation.
  - O-11: business-realism doubts on registration/protection credits on a locked rate and on the workmanship-warranty deductible.
  - O-12: forfeit_treatment's method status is borderline.
  - O-13: the events-section missed-fee trigger fires at forfeit time.
  - O-14: the cancellation tool has no fee parameter while base charges a cancellation fee on Basic/Silver.
  - O-15: payment application order versus tool netting.

## closing_checklist

Written 2026-10-05T15:53Z (UTC), after both tasks' derivations were frozen (`0.md`, `1.md`) and their GT revealed and compared. Nothing above this heading was edited after the reveal; the pre-reveal sha256 of this file was 4f4ccdaa…a430.

**The difficulty does not close.** Not every relationship passes for both tasks.

| task | SOURCE-POLICY | SOURCE-CHAIN | SOURCE-FACTOR | SOURCE-TASK |
| --- | --- | --- | --- | --- |
| 0 | RED (CG-1) | PASS | RED (CG-3) | PASS |
| 1 | RED (CG-2) | PASS | RED (CG-4) | PASS |

Step 4 items, as they stand:

- Task files: `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`, with `_difficulty.md` alongside. This is the first revision; no older revision exists. Not every comparison section carries a PASS.
- Coverage and scope:
  - All 6 extended policies are covered: task 0 holds {covered_repair_draw, cancellation_settlement} and task 1 holds {reinstatement_fee, reinstated_rate_lock, missed_visit_fee, reinstated_term_dues}.
  - The scopes are pairwise disjoint over whole trees. The revealed `charter_scope` equals the frozen components.
  - Task tools and GT are closed (6 tools, each used by exactly one task).
  - The uuid8s are independent and frozen.
- Trees:
  - Task 0 has 1 prerequisite problem and 1 value_input edge; task 1 has 3 prerequisite problems and 3 value_input edges.
  - Each tree has an owner=user root and no cycle, and the difficulty-wide prerequisite graph is a DAG (two components).
  - PASS.
- Factors:
  - Every factor of every computation bears weight against its baseline on its task's world. Every all-baseline fall-back is definite and ≠ gold (750.00, 0.00, 25.00, 249.00, 25.00, 418.00).
  - But CG-3 leaves the draw computation without an honest `method` factor, CG-4 places task 1's customer on tiers carrying vacuous condition parts, and CG-5 records ladders that collapse or invert on tier variants these worlds do not use.
  - Not PASS.
- Gates: the coordinator's snapshot (`/tmp/erl37/gates/comfort_club_membership_care.snapshot.txt`, all green) was taken on the same artifacts the audit froze. `plan.extended.yaml` and `task_tools.py` are byte-identical to the hashes in `charter.sha256`, re-checked at close. Re-running the gates on a final form is moot while the difficulty does not close. check_traceability remains deferred to KB publication.

Inputs to carry forward on any re-audit:

- `plan.extended.yaml` e9e5cd25…9203
- `task_tools.py` 60a3229f…52b8

If both are unchanged, the charter-global sections above carry forward by reference.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: same independent auditor as revision 1. Freeze time: 2026-10-05T16:52Z (UTC). This section was written before any revision-2 GT was revealed.
- Inputs (sha256), checked against `/tmp/erl37/views_r2/comfort_club_membership_care/charter.sha256` (match):
  - `plan.extended.yaml` `583050e8377b249c421bb284a17f0a34e7a5cff708e98cba9f2183d72d9f35e5`. Changed from revision 1 (`e9e5cd25…`).
  - `task_tools.py` `3712982638452f4c216bb264b30237f0d5ed465a3cdae5b4cc983de55d332507`. Changed from revision 1 (`60a3229f…`).
  - masked views `task_0.masked.json` `26a132d2…ccece` and `task_1.masked.json` `7e2cf218…2bd4`. Byte-identical to revision 1, so frozen_time, user_scenario and initial_state did not move.
- **Both shared inputs changed, so every charter-global section is re-derived in full below.** Nothing from revision 1 is carried forward by reference.
- Base copy: the yaml-parsed equality of every base key with `blueprint/products/plan.yaml` still holds. `blueprint/` file mtimes predate revision 1, so the blueprint is untouched.
- Gate snapshot (revision 2, coordinator-run): `/tmp/erl37/gates/comfort_club_membership_care.r2.snapshot.txt`. All seven gates are OK (EXTENDED, TASK TOOL CONTRACT, REPLAY 16/19 acts match, SOLVABILITY, COMPUTE, GROUNDING, SCOPE), plus CACHE-DIFF INFO. The input is complete.
- contamination_disclosure (charter-global): the auditor read revision 1's GT fields of `tasks/0.json` and `tasks/1.json` during the revision-1 reveal. That knowledge is of an older revision. The revision-2 derivation below was recomputed mechanically from the revision-2 charter and the unchanged masked seeds. It is disclosed so a reader can weigh it.
- Masked and unread before freeze: the revision-2 `tasks/*.json` GT fields and the worklogs.

### policy_conflict_scan (revision 2)

- Policies, targets, owners, computes and the prerequisite graph are unchanged in shape: 6 policies and the same two components. There is still one writer per quantity.
- Changes since revision 1:
  - Draw: three named overwrites (adds the "plan covers what remains" sentence). New scope "On a tier that includes covered repairs". Thermostat and condensate-pump lines are excluded in compute. The labor divisor is now a parameter factor, and the maintained-repair method factor replaces the covered share. The per-call cap is now additive (+250 / +125). Rounding is half up.
  - Cancellation: a cancellation-fee sentence was added, and the tool gained a `cancellation_fee` argument. The term-dues-billed and discount windows are now stated in the rule as the whole-month window the compute uses.
  - Reinstatement fee:
    - It now overwrites base "Reinstatement … renews it exactly as an automatic renewal would …". The replacement grants the new term the lapsed term's visit and coverage grants, and the tool now writes those grants.
    - A fee-free tier is scoped out ("On a tier whose reinstatement fee is 0.00 no reinstatement fee is charged and the fee rules below do not apply").
  - Rate lock: days since lapse are defined from "the day before the agreement's current term start". The retention tiers no longer carry "within its renewal grace period" or "with a locked rate on file".
  - Missed fee: the repeat-miss fee is additive (+10 / +25). The fee is "worked out when the most recent forfeited visit on record is one that carries no fee".
  - Term dues:
    - Five plan_dues_pricing sentences and the plan_reinstatement price-lock sentence are now named in `overwrite`.
    - The price lock is keyed on enrolment months (≥ 60) instead of term count plus grace. The share is keyed on the most recent contract signing (install_ledger contract_price), and the gap tiers drop "within its renewal grace period".
    - The days since lapse are named "the reinstatement gap".
  - Tools: the pay and rate-lock docstrings now say "current term" instead of "reinstated".
- Overlap: base plan_reinstatement's price-lock sentence is now overwritten by three policies (reinstatement fee: "leaves the locked rate on file … decided by the policies that settle them"; rate lock: locked-rate formula; term dues: price lock rule). The replacements settle disjoint quantities (fee and entries, locked rate, first-system rate) and do not contradict one another.
- Scopes: the two components are unchanged, mutually exclusive and jointly complete.

### rule_compute_equivalence (revision 2)

Mechanical checks:

- All `compute_basis` quotes are verbatim in their rule.
- All `baseline.rule` sentences are in the rule.
- All overwrite `superseded_clause` texts are verbatim in their base policy, and all `replaced_by` texts are in the extended rule (script check, 6/6 policies; every overwrite True/True).
- Every ladder tier is stated in the rule and branches the `decides` binding, and the converse holds.

Sweep back:

- Draw:
  - The thermostat and condensate-pump exclusion is now implemented (`draw_parts_billed` / `draw_labor_billed` subtract those task codes).
  - Rounding is half up (`int(x*100+0.5+1e-9)/100`).
  - Still aggregated across every call of the customer in the one-month window, and `CFIELD(... status='completed')` still takes the first completed call. The rule's "of that call" scoping and the waiting-period gate have no compute counterpart (the waiting period is now explicitly "decides whether a call is drawn on, not how much"). O-1 is partly closed; the residue is an observation.
- Cancellation:
  - The rule's term-dues and discount windows now state the whole-month window the compute uses. O-2 is closed as a divergence; the wording is the rule's own definition.
  - The cancellation fee is in the rule and the tool, but it is **not** a compute binding: `proration_credit` is the computed argument, and the fee argument is set by the rule's sentence. Acceptable; it is a rule-stated fixed value.
- Reinstatement fee: the `result` now returns 0 when `reinstatement_fee_usd` is 0, matching the new scope sentence. Equivalent.
- Rate lock: `lock_lapse_days = DAYS(term_start, NOW) + 1` now matches the rule's "lapsed term's last day, which is the day before the agreement's current term start". Retention tiers match. Equivalent.
- Missed fee: the rule now says the fee is "worked out when the most recent forfeited visit on record is one that carries no fee, and the forfeit treatment reads that most recent forfeited visit", which matches the LATEST-over-all-forfeits compute. O-3 is closed as a divergence. The residue is N-2 below.
- Term dues:
  - The share reads `XLATEST(install_ledger.contract_price.posted_date)` for "most recently signed Harbison installation contract". That is the most recent contract, so O-4 is closed.
  - The `result` basis now quotes "and the amount billed follows the gap rule".
  - **N-3 (new, latent, introduced in this revision).** `due_first_rate` lost revision 1's `F('locked_annual_rate') > 0` guard.
    - On a tier without a price lock (Comfort Club Basic, `price_lock_on_renewal: false`), base writes `locked_annual_rate` 0.00 ("else 0.00", plan_enroll/plan_renew fields). The compute then takes tier 1 (0.00 < 149.00 and enrolled ≥ 60 months, or tier 2's average) and bills a first-system rate of 0.00 or 74.50.
    - The rule says "when the agreement carries a locked rate below …". An agreement carrying no locked rate falls to "otherwise it is the current rate".
    - Rule and compute diverge for every Basic reinstatement. Neither task's world is on Basic (task 1 is Gold), so this is an observation, not demonstrated on a scored world.
- Rounding everywhere is now half up (O-5 closed).

### action_binding_and_uuids (revision 2)

- Tool names and uuid8s are unchanged and independent (a854dec6, 08dfa488, 6e8e1b28, 0c66ac3f, 325d3ccb, c2f743bd). Each `(target_tool, computes)` pair is still claimed once.
- Function bodies validate nothing and refuse nothing.
- `reinstate_lapsed_agreement_6e8e1b28` now copies the lapsed term's `plan_visit_grant` and `plan_coverage_grant` rows with reasons new_term, renewal_term or additional_system into the new term (reason renewal_term) and sets `visits_remaining` and `repair_coverage_remaining`. This matches the new replaced_by "grants the new term the same maintenance visits and covered-repair benefit that the lapsed term was granted at its start and for systems added during it". O-6 is closed.
- `confirm_agreement_cancellation_08dfa488` gained `cancellation_fee` (charge posted when > 0), so O-14 is closed.
- The `set_reinstated_rate_lock_0c66ac3f` and `pay_reinstated_term_dues_c2f743bd` docstrings now describe "the current term" and no longer presume a reinstated state, so O-9 is closed. The function names still carry the word "reinstated". That is a name, not an ordering word.
- No docstring carries an ordering word or another tool's name.
- O-15 (payment application order versus netting): the pay tool's body and docstring do not visibly differ from revision 1 on this point. The observation stands as non-scoring.

### prerequisite_graph (revision 2)

- Edges, kinds, gates, forms and `resolved_by` are unchanged. The graph is acyclic, and every `policy_source` is verbatim in its own rule (script check).
- `condition` texts:
  - rate_lock->reinstatement: "The agreement's status is active and its current term start is the day after the lapsed term's last day."
  - term_dues->reinstatement: "The agreement is active and its current term starts the day after the lapsed term's last day."
  - term_dues->rate_lock: "…is the rate decided for the reinstated term."

  They now match their sentences' strength, so O-7 is closed.
- `effect` texts now describe the rule's own definitions ("the date the days since lapse are counted back to", "the reinstatement gap is counted back to the lapsed term's last day"), which the revision-2 rules state. O-8 is closed.
- `fallback_reason` (term_dues->rate_lock) is unchanged, and still justified: no dated lock record exists.

### prerequisite_sentences (revision 2)

- All six sentences are textually unchanged and pass the four-point test as in revision 1. One write per state-form edge, and one reading each.
- New wording in other sentences carries no undeclared cross-problem order:
  - draw scope "On a tier that includes covered repairs"
  - the cancellation fee sentence
  - the reinstatement grant sentence
  - the missed-fee "worked out when …" sentence
  - term dues' "the amount billed follows the gap rule"
- O-10 is unchanged. The reworker states "no change". It remains an observation.

### override_declarations (revision 2)

- **CG-1 (draw) — closed.** The base sentence "The member repair discount is applied to the line first; when a protection contract claim pays part of the same line, that warranty coverage is applied next, and the plan covers what remains." is now named (`superseded_clause` verbatim in base). Its replacement, "…the plan covering that covered amount and not simply what remains of the lines.", is in the rule.
  - The remaining base sentences of plan_evt_repair_coverage are either named (never covered; draw per call) or followed (grant; open/active gates; waiting period; exclusions; expiry).
  - The fragment "Covered lines are the repair_parts and repair_labor lines of a service call on an enrolled system" is followed (extended narrows by the thermostat and condensate-pump exclusion, which base also states).
- **CG-2 (term dues) — closed for the sentences named in revision 1.** The `overwrite` now names:
  - "Annual dues for a term are annual_dues_first_system_usd plus annual_dues_additional_system_usd for each enrolled system beyond the first"
  - "billed once in advance as annual_dues … with billing_period equal to the month of term_start"
  - "the first-system rate for the new term is the lower of …"
  - "and additional systems are billed at the current catalogue rate"
  - and the plan_reinstatement price-lock sentence.

  All of these are verbatim in base. The plan_reinstatement "renews it exactly as an automatic renewal would" sentence is now named by the reinstatement-fee policy.
- **N-1 (new; scope of the replacements, latent).** Several named base sentences are general dues-pricing sentences for *every* annually billed agreement: first-term annual dues, automatic-renewal first-system rate, catalogue rate for additional systems at renewal. Their replacements are written for a reinstated term only: gross dues with the additional-system share, a "Price lock rule" keyed on enrolment months, "dues of an annually billed agreement reinstated within its renewal grace period".
  - Once rendered together, the KB has no remaining base statement of the first-term annual dues or of the automatic-renewal first-system rate for agreements that were never lapsed. Read literally, the replacement price-lock rule would also bill an ordinary automatic renewal of a member enrolled fewer than 60 months at the average of locked and current instead of the lower of the two.
  - No task of this difficulty scores an ordinary enrolment or renewal. Task 0's renewal charge is already posted and is read, not computed. So no consequence is demonstrable on either world. Observation.
- Cancellation: the new fee sentence follows base "a cancellation_fee of cancellation_fee_usd is charged where it is above 0.00" outside the window. Compatible.
- Missed fee: the additive repeat fee replaces a named sentence. Compatible.

### factor_ladders (revision 2)

| policy | factors (effect) | P / M | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- |
| covered_repair_draw | after_hours_labor_divisor (param), maintenance_coverage_basis (method), loyal_member_call_cap (param), sealed_system_refrigerant_rate (param), protection_holder_deductible (param) | 4 / 1 | call cap (terms x draws), refrigerant (task lines x terms) | service, warranty |
| cancellation_settlement | unchanged from revision 1 | 4 / 1 | notice tier 2, visit rate, coverage rate | install, service |
| reinstatement_fee | unchanged factors; fee-free tiers scoped out | 4 / 1 | tenure share | install, warranty |
| reinstated_rate_lock | lock_retention (method; tiers: ≤ keep days / > keep days & ≥ halfway terms / otherwise) and 3 params | 3 / 1 | retention (lapse days x terms) | install, warranty |
| missed_visit_fee | repeat_miss_fee (now additive), tenure cap, attendance, forfeit_treatment (method) | 3 / 1 | forfeit treatment | none |
| reinstated_term_dues | price_lock_application (method; locked < current x enrolment months), new_installation_share, loyalty, trouble-free, bundle, lapse_gap_proration (method; gap days x terms) | 4 / 2 | price lock, loyalty, gap | install, service, warranty |

- **CG-3 — closed.**
  - after_hours_labor_divisor is now honestly a `parameter` (divisor 1.5 / 1.25 / 1.0).
  - The draw's method factor is now maintenance_coverage_basis. Its tiers are:
    - parts only, net of discount (the labor drops out of the base)
    - discounted repair amount less the tune-up retail value
    - discounted repair amount as it stands

    Tier 1 changes which lines enter the computation, which is a genuine change of algorithm and not a substituted number. The draw computation has 4 P / 1 M.
- **CG-4 — closed.**
  - lock_retention: the tiers now read "no more than the keep days" / "more than the keep days and at least the halfway term count".
  - price_lock_application: the tiers now read "locked rate below current and enrolled ≥ / < lock tenure months".
  - lapse_gap_proration: the tiers now read "gap > full-gap days and ≥ gap terms" / "gap > partial-gap days".
  - None of these restates "within its renewal grace period", and none includes "with a locked rate on file". Each remaining part divides the customers who reach the write.
- **CG-5 — closed.** By tier variant:
  - loyal_member_call_cap is now the tier cap plus 250 or plus 125: Platinum Plus 1000 / 875 / 750, Total Home 1750 / 1625 / 1500. Monotone on both covered-repair tiers.
  - repeat_miss_fee is now the tier fee plus 25 or plus 10: Basic and Silver 60 / 45 / 35, Gold 50 / 35 / 25. Distinct on every forfeiting tier. Tiers that do not forfeit are outside the rule's scope.
  - lapse_length_fee: tiers whose fee is 0.00 are now outside the fee rules. On fee tiers (25.00) the tiers give 0, 25, or 25 × days/30 rounded up, which are distinct.
- Business realism, carried from revision 1 (O-11 unchanged, reworker states "no change"). New ladder judged: maintenance_coverage_basis (no tune-up in 12 months: parts only; one: less one tune-up's retail value; two or more: full). This is a maintenance-requirement treatment a service-plan business does publish. No objection.
- O-12 (forfeit_treatment method status): unchanged, observation.
- O-13 (events trigger at forfeit time): unchanged, observation.

### findings (revision 2)

- CG-1, CG-2, CG-3, CG-4 and CG-5 are all **closed** (see the sections above).
- O-2, O-3, O-4, O-5, O-6, O-7, O-8, O-9 and O-14 are closed.
- O-1 is partly closed (thermostat and condensate-pump exclusion now implemented). The per-call aggregation and the first-completed-call read remain an observation.
- O-15 shows no visible change and remains a non-scoring observation.
- O-10, O-11, O-12 and O-13 are unchanged, as the reworker states. They remain observations.
- **New observations, latent on both worlds:**
  - **N-1:** general dues-pricing sentences are replaced by reinstatement-scoped text.
  - **N-2:** the missed-fee rule now computes a fee only "when the most recent forfeited visit on record is one that carries no fee". So an older fee-less forfeit sitting behind a fee-carrying later forfeit would never get a fee, while the term-dues prerequisite demands "a missed-visit fee for every visit forfeited in the lapsed term". That state would be unresolvable. Task 1's world has its fee-less forfeit as the most recent, so it is not exercised.
  - **N-3:** the term-dues price-lock compute lost its locked-rate > 0 guard, so it diverges from the rule on Basic (no price lock). Task 1 is Gold, so it is not exercised.
- No revision-2 charter-global finding is a demonstrated RED. Per-task consequences are judged in `0.md` and `1.md` under `revision_2`.

## closing_checklist (revision 2)

Written 2026-10-05T16:56Z (UTC), after both revision-2 task derivations were frozen and then compared with the revision-2 GT. The revision-2 charter-global section above was written before the reveal (pre-reveal sha256 of this file: a584684e…623). The revision-1 text and revision-1 closing checklist above are untouched.

| task | SOURCE-POLICY | SOURCE-CHAIN | SOURCE-FACTOR | SOURCE-TASK |
| --- | --- | --- | --- | --- |
| 0 | PASS (CG-1 closed) | PASS | PASS (CG-3 closed) | PASS |
| 1 | PASS (CG-2 closed) | PASS | PASS (CG-4 closed) | PASS |

Step 4 items:

- **Task files:** `0.md` and `1.md` map one-to-one to `tasks/0.json` and `tasks/1.json`, with `_difficulty.md` alongside. Revision 1 is preserved verbatim, and revision 2 is appended under `## revision_2`. Every revision-2 comparison section carries PASS on all four relationships.
- **Coverage and scope:** all 6 extended policies are covered. The scopes are pairwise disjoint over whole trees: task 0 holds {draw, cancellation}, task 1 holds {reinstatement fee, rate lock, missed fee, term dues}. The revealed `charter_scope` equals the frozen components. Task tools and GT are closed. The uuid8s are independent and frozen, and unchanged since revision 1.
- **Trees:** task 0 has 1 prerequisite and 1 value_input edge; task 1 has 3 prerequisites and 3 value_input edges. Each has an owner=user root and no cycle, and the difficulty-wide graph is a DAG.
- **Factors:**
  - draw 4 P / 1 M; cancellation 4/1; reinstatement fee 4/1; rate lock 3/1; missed fee 3/1; term dues 4/2.
  - Each task has multi-source and cross-difficulty factors.
  - Every ladder has 3 distinct tiers on every tier variant in scope.
  - Every factor bears weight on its world against an honest baseline, and every all-baseline fall-back is definite and differs from gold.
- **Gates:** the coordinator re-ran the full instantiation gate block on this final form (`/tmp/erl37/gates/comfort_club_membership_care.r2.snapshot.txt`, all 7 OK, CACHE-DIFF INFO). The `plan.extended.yaml` (583050e8…) and `task_tools.py` (37129826…) hashes audited here equal the ones in `views_r2/charter.sha256`. check_traceability remains deferred to KB publication.

**Result: the difficulty passes the source-layer audit at revision 2.** Every round-1 RED (CG-1 to CG-5) is closed, and nothing regressed on either scored world.

Observations carried forward (non-scoring, no consequence demonstrable on either world):

- **N-1:** general dues-pricing sentences are replaced by reinstatement-scoped text, which leaves ordinary enrolment and renewal semantics unstated.
- **N-2:** the missed-fee "most recent forfeit carries no fee" trigger against the term-dues "every forfeit in the lapsed term" prerequisite.
- **N-3:** the term-dues price-lock compute lost its locked-rate > 0 guard, so it diverges from the rule on Comfort Club Basic. This was introduced in revision 2.
- O-1 residue, O-10, O-11, O-12, O-13, O-15.
- R2-a and R2-b: GT proof prose in task 1.
