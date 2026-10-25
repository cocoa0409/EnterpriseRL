# Policy-task audit — managed_services_agreements / charter-global

## revision_1

## charter_global_frozen
- Frozen: 2026-10-18T01:56Z, before any task GT was revealed. Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiator.
- Hashes (sha256, re-checked on disk at audit start):
  - `tasks/managed_services_agreements/managed.extended.yaml` 0bfa3fef2a3430f62ee9186ced0675c73b2997d9bd62c3b4f74df1d26ece6550
  - `tasks/managed_services_agreements/task_tools.py` 819877d3171b886111db471eff75c17e54668ba11156dcf9dded9b82c5bf7010
  - `.audit_views/policy/managed_services_agreements/r1/0.view.json` 45b71b815b865eb1512252d11dcdeaef169ec344552286ff190bbcd73652064b
  - `.audit_views/policy/managed_services_agreements/r1/1.view.json` 8b96702a11cbfc1a7523b8efe6234a445de30383ddcb0f21ccac4882f85b2770
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/managed.yaml` (plus `security.yaml`, `backup.yaml`, `licensing.yaml` variant parameters and pricing rules, for the cross-product reads and the XF-D20 seed check), the extended charter, `task_tools.py`, `audits/render_source/XF_recipe.md`, and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (to learn what `MONTHS`, `COUNT(within_months=…)`, `LATEST`, `CFIELD`, `CPARAM`, `XSUM` and `RND` actually do; it holds no GT).
- Masked and not read: `tasks/*.json`, `plan.md`, `worklog.md` of this difficulty, and every `_masked_keys` field of the views (`charter_scope, computations, db_closure, db_closure_matches_initial_state, design_rationale, evaluation_criteria, prerequisite_closure, required_documents, solvability_contract`). No recursive grep was run over `tasks/`.
- Entry conditions: the coordinator's gate snapshot (2026-10-18T01:39:54, replay with `--check`) is attached and all seven gates are rc=0. `check_traceability` is deferred until the KB is published, so it is not part of this snapshot (noted, not counted as missing input). The masked views came with hashes, and those hashes match. Input complete.

### policy_conflict_scan
- The base section of the extended charter is a verbatim copy of `blueprint/products/managed.yaml`: every top-level key compares equal, and the textual diff is only the appended `extended_policies` banner.
- The eight extended policies split into two disjoint problem trees. They are read off the `prerequisite` graph; `charter_scope` is masked.
  - Tree A, root `managed_ext_signed_exit_fee` (an `owner=user` signature). Prerequisites: `managed_ext_reinstatement_charge` (state_gate), `managed_ext_auto_renewal_rate` (value_input) and `managed_ext_current_month_fee` (value_input). `managed_ext_current_month_fee` itself depends on `managed_ext_auto_renewal_rate` (value_input).
  - Tree B, root `managed_ext_essentials_upgrade_rate` (an `owner=user` signature). Prerequisite: `managed_ext_first_late_fee` (value_input), which depends on `managed_ext_after_hours_remote_labor` and `managed_ext_onsite_visit_labor` (both value_input).
  - The two trees cover all 8 policies and share no node, so the scopes are pairwise disjoint and jointly complete. Confirmation against `charter_scope` waits for the reveal.
- Overlapping subjects:
  - `managed_billable_labor` is claimed by both labor policies. They write through different tools, and their scopes differ by labor class. The sibling overwrites, however, do not scope each other correctly (finding C-4).
  - `managed_notice_given` / `managed_early_termination_fee` (exit) and `managed_tier_changed` (upgrade) both overwrite clauses of `managed_client_signed_changes`. The upgrade overwrite's `replaced_by` keeps the early termination notice under the pending-request regime, which matches the exit tool. Compatible.
  - `managed_late_fee` (first late fee) and `managed_reinstated` (reinstatement) each overwrite a different clause of `managed_late_fee_and_suspension`. No overlap.
- Status gates:
  - Exit: "only once the agreement's status is active".
  - Renewal: base, active or suspended.
  - Monthly fee: base, active, suspended or notice_given.
  - Upgrade: base `tier_change_active`, active only.
  - Late fee: no status gate, in base or extended.
  - Together these allow every order the two trees need. No status conflict.
- Time anchors: every extended month window is "a month window of N months ending today", and every extended rule carries the same "whole month" sentence. This is consistent with the DSL `MONTHS` (a month counts only once the later day-of-month is at least the earlier one) and with `_within` (`0 <= MONTHS(d, today) < N`).
- Cross-category reads:
  - security: `CFIELD`/`CPARAM` on status active, plus `XSUM` over `security_endpoint_changes`.
  - backup: `CFIELD`/`CPARAM` on status active.
  - licensing: `CFIELD` on status active plus variant.
  - Security and backup allow at most one open holding per client (`max_per_customer: 1`), so first-match is safe. Licensing allows any number of subscriptions of one plan (`licensing_agg_multi_holding`, `max_per_customer: null`), so first-match is not safe (finding C-6).

### rule_compute_equivalence
- Mechanical sweep, scratch script:
  - Every `compute_basis` quote of all 8 policies is verbatim in its own rule (XF-B9). No miss.
  - Every `baseline.rule` sentence is in the rule.
  - Every `replaced_by` is carried verbatim in the rule.
  - Every `policy_source` is verbatim in the rule.
- Reverse sweep, by hand. Every tier named in `factors[].ladder` is a rule sentence and a branch of its `decides` binding, and every branch is a stated tier. Points checked one by one:
  - Rounding placement (XF-B10) matches in all 8:
    - fee: `RND(RND(seat_amount*(1-p)) + servers*fee)`, i.e. "reduced once … rounded …; the server management fee is added last".
    - onsite: `RND(RND(labor) + trip)`.
    - late fee: `MX(RND(banded*(1-c)), minimum)`.
    - upgrade: `RND(built)`, where `built_rate` is RND'd inside the phased and ratio tiers.
    - renewal: `MN(RND(selected*(1+net)), cap)`.
    - reinstatement and exit: a single RND.
  - Absent-record branches (XF-B13) are stated and implemented:
    - exit: no pending request gives months 0.
    - labor: no ticket gives 0.
    - reinstatement: no payment, or a payment before `suspended_date`, gives 9999.
    - renewal: an empty `suspended_date`.
    - cross reads: None gives fall-through.
  - Month-end convention (XF-B12): the rule's "whole month" sentence is the DSL `MONTHS`. Month-end anchors are consistent with base `term_end_date` (the day before the anniversary).
  - DSL rounding: `RND` is Python `round` on binary floats, not half up. The rules say "rounded half up". No exact binary tie arises in either world, so this is an observation (O-3).
  - Same-day ties (XF-B11):
    - The two labor policies state "never stamps two resolutions of one agreement with the same minute".
    - The exit policy's `LATEST('managed_service_requests', …, date_field='created_at')` has no tie rule for two pending requests registered at the same minute. This is a member of XF-B11 (finding C-6).

### action_binding_and_uuids
- `(target_tool, computes)` pairs are all distinct: 8 policies, 8 tools. Each tool is claimed once.
- Owners:
  - `sign_early_termination_notice_6477ae2a` and `sign_tier_upgrade_933f385b` are `owner="user"`.
  - The other six are `owner="agent"`.
  - This matches the base `managed_client_signed_changes` as overwritten.
- uuid8s: 69c0d348, 19cc11da, be1b3a76, 6477ae2a, c0dca9e8, c7936621, 96a9eef8, 933f385b. None is reused or shares a prefix, and there is no sequential or adjacent pattern.
- Docstrings:
  - No tool's docstring names another tool, states a sequence position, or carries an ordering word. The only hits on "first"/"after" are descriptive: "the first day of the renewal term", "remote after-hours".
  - No concrete example values (XF-D19). Formats only ("INV- followed by 6 digits", "SB- followed by 7 digits").
  - The tier-enum descriptions in `sign_tier_upgrade_933f385b` agree with the variant parameters: Standard adds vendor management, onsite hours and SAT; Professional adds a dedicated account manager; Enterprise adds a TAM.
- No body validates a prerequisite: none reads a status, payment, renewal or ledger state before writing. Two docstring/body points:
  - `sign_tier_upgrade_933f385b` writes `variant_name` and `seat_rate_usd` at signature, even though the amendment takes effect on the first of next month (O-5).
  - `post_monthly_fee_19cc11da` dates the invoice today rather than on `monthly_invoice_day` (O-4).

### prerequisite_graph
- Every extended policy has `prerequisite` filled in (`[]` for renewal, reinstatement and both labor policies). Every `problem` is an extended policy id of this file, none is self-referencing, and none is a base id.
- The graph is acyclic: renewal → fee → exit; renewal → exit; reinstatement → exit; after-hours → late fee; onsite → late fee; late fee → upgrade.
- Every edge is `form: state`, with no `fallback_reason`, which is consistent.
- Every `policy_source` is verbatim in the blocked rule.
- `resolved_by` equals the depended-on policy's `target_tool` on all 7 edges.
- `gate` bindings exist in the blocked compute: `seat_amount`, `months_charged`, `basis_rule`, `unpaid_balance` ×2, `standing_pct`. The state_gate `managed_agreements.status` is a real eligibility gate.
- `condition` against sentence:
  - The fee and exit/renewal conditions append "the renewal term having been recorded with its renewal seat_rate_usd and contracted_seats" / "term dates, term_months and renewal seat_rate_usd". The sentence names only the term end date. This is a mild strengthening. Only `record_renewal_term_69c0d348` moves `term_end_date`, so the strengthening is equivalent in this difficulty (O-1).
  - `effect` of the exit/fee edge: "Once the current month's fee is posted, three monthly fees stand in the recent window, so the exit billing-basis rule selects the average of those three fees". This asserts a world outcome in charter text: the average tier also needs covered seats above the floor (O-2).

### prerequisite_sentences
All 7 edges pass the four-point test: an ordering connective, a record-visible state named in table words, no tool, policy id, snake_case token or row id, and scope equal to the condition. Each sentence below is followed by the one write that brings its state about.
- Fee ← renewal: "The monthly fee of a service month is fixed only after the agreement's current term covers the first day of that service month, its term end date falling on or after that day."
  - Only `record_renewal_term_69c0d348` moves `managed_agreements.term_end_date`.
  - The renewal rule does not restate the sentence.
- Exit ← reinstatement: "An early termination notice is recorded only once the agreement's status is active."
  - In this difficulty, only `record_reinstatement_be1b3a76` sets status active. Withdrawal and go-live have no tool here.
- Exit ← renewal: "The early termination fee is fixed only after the agreement carries the term in force on the day the notice is signed, its term end date falling on or after that day."
  - Only the renewal write.
- Exit ← fee: "The early termination fee is not worked out until the ledger carries the monthly fee of every service month begun before the notice is signed."
  - Only `post_monthly_fee_19cc11da` creates `managed_monthly_fee` rows.
  - Read literally, it also covers the go-live month, which base bills by the baseline proration and never by a monthly fee. Base excludes that reading ("The first service month after go-live is billed by the baseline proration charge"), so there is no defensible second reading (O-1).
- Late fee ← after-hours: "The late fee on an invoice is fixed only after that invoice carries the remote after-hours labor charge of every ticket resolved in the calendar month before its posting whose remote after-hours labor is settled by invoice."
  - Only `post_remote_after_hours_labor_c0dca9e8`.
- Late fee ← onsite: "The late fee on an invoice is not worked out until that invoice carries the onsite visit charge of every ticket resolved in the calendar month before its posting whose onsite visit labor is settled by invoice."
  - Only `post_onsite_visit_labor_c7936621`.
- Upgrade ← late fee: "The upgraded seat rate is fixed only after the ledger carries the late fee owed on the first day of the current month for every invoice then past its grace period."
  - Only `post_late_fee_96a9eef8`.

Further checks:
- No rule carries a second wording, a tool name or another problem's id for any dependency.
- No undeclared cross-problem order appears in an extended rule. Reinstatement's "once every invoice past its due date has been paid in full" points at the base payment policy, which is not in this difficulty.
- The late-fee pair of sentences is well-formed, but the business order they impose is not a real one (finding C-2).

### override_declarations
Sentence by sentence against each `base_policy_refs` entry:
- `managed_ext_auto_renewal_rate` vs `managed_renewal_and_uplift`:
  - The uplift/list clause is overwritten and scoped to auto-renewals. The base content is restated for signed renewals (XF-C16 ok).
  - Term start, `term_months`, `contracted_seats = max(seat_count, min_seats)` and `renewal_count` are restated identically.
  - "a 12-month renewal term carries no term discount on any tier" agrees with every variant (12-month discount 0, or no 12-month key).
  - No undeclared departure.
- `managed_ext_current_month_fee` vs `managed_monthly_fee_calc`:
  - The amount sentence is overwritten and scoped.
  - The base's "seat_count as it stood at the end of the last day of the previous month" becomes "seat_count", which is equal within the scope (no seat change since the 1st).
  - Proration of first months, status gate and post-termination months are inherited.
  - No undeclared departure.
- `managed_ext_reinstatement_charge` vs `managed_late_fee_and_suspension`: the fee clause is overwritten "for every such reinstatement" (base has no other case). The paid-up gate is inherited and restated. OK.
- `managed_ext_signed_exit_fee` vs `managed_early_termination_and_exit`:
  - The fee clause is overwritten for every signed early termination fee. Base charges notices only on e-signature, so this is global and adequately named.
  - Undeclared departure: base "Its termination_effective_date is the later of the date the client asks for and the notice_received_date plus notice_days calendar days" is not overwritten. The extended rule sets "the request's effective date as termination_effective_date" (finding C-5).
  - The months count changes from calendar service months to term months. This is inside the overwritten clause, so it is declared.
- `managed_ext_after_hours_remote_labor` / `managed_ext_onsite_visit_labor` vs `managed_billable_labor_rates`:
  - The amount sentence is overwritten by both siblings.
  - Each sibling's out-of-scope clause over-claims the other's case (finding C-4).
  - The onsite schedule applies its same-day minimum and its trip charge without the base's partial-inclusion carve-out, "only the excess is billable and the onsite minimum does not apply to that excess", which is not overwritten (finding C-5, second member).
- `managed_ext_first_late_fee` vs `managed_late_fee_and_suspension`:
  - The amount sentence, including the measure reference, is overwritten and scoped. The ledger-wide balance replaces the per-invoice measure inside the scope.
  - The first-of-month assessment timing and grace are inherited.
  - The in-scope assertion "no other invoice and no late fee standing unpaid" does not cover an unapplied credit balance (O-6).
- `managed_ext_essentials_upgrade_rate` vs `managed_tier_change` and `managed_client_signed_changes`: both overwrites are scoped to Essentials→Standard. The effective-date, min_seats, status and no-proration clauses are inherited. OK.

### factor_ladders
Counts per policy (structure only):

| policy | factors | parameter | method | multi-source factor(s) | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| auto_renewal_rate | 6 | 5 | 1 (price_protection_rule) | first_renewal_uplift_schedule (renewal_count AND term span, one record) | none |
| current_month_fee | 6 | 5 | 1 (frontline_seat_rule) | sentinel_bundle_credit (subscription term AND endpoint ledger) | security ×2, licensing ×2, backup |
| reinstatement_charge | 4 | 3 | 1 (environment_revalidation_rule) | first_suspension_relief (reinstatement fees AND payments) | security |
| signed_exit_fee | 6 | 5 | 1 (exit_billing_basis_rule) | exit_billing_basis_rule (fee rows AND seat ledger) | security, backup |
| after_hours_remote_labor | 6 | 5 | 1 (after_hours_callout_rule) | remote_scope_courtesy (scope AND category, one row) | security |
| onsite_visit_labor | 4 | 3 | 1 (onsite_dispatch_rule) | none distinct-record | none |
| first_late_fee | 5 | 4 | 1 (balance_band_rule) | payment_record_rate, relationship_courtesy | security (+backup) |
| essentials_upgrade_rate | 6 | 5 | 1 (upgrade_pricing_rule) | upgrade_pricing_rule (one record) | security |

- Every ladder has 3 tiers, including the fall-through, and every fall-through equals the factor's `baseline`. `decides` is never `result`. Binding sets are disjoint: no binding is shared by two factors (mechanical check).
- XF-A1 independence (mechanical transitive check): no factor binding reaches another factor's binding.
- XF-A7: no factor id is a substring of any tool name.
- Labels are honest. Method tiers change formula shape (max vs plus vs none, flat vs per-seat, average vs rate×seats, banded vs whole). Parameter tiers swap a number.
- Per tree (task):
  - Tree A has multi-source factors (sentinel_bundle_credit, first_suspension_relief, exit_billing_basis_rule) and cross-difficulty factors (security, licensing, backup).
  - Tree B has multi-source factors (payment_record_rate, relationship_courtesy) and cross-difficulty factors (security, backup).
- Unreal ladders (finding C-1): `loyalty_remote_rate` and `onsite_loyalty_rate` use absolute dollar rates on charters that are not tier-scoped. On ClearPath Standard and above they coincide with, or exceed, the fall-through tier.
- Realism of the remaining tiers, judged against a per-seat MSA:
  - Renewal uplift schedule, price protection, volume, credits, payment standing and intensity: real.
  - Fee bundle credits, frontline (F3) pricing and per-server charge: real.
  - Reinstatement: re-validation, first-offence relief and cure speed are real.
  - Exit: tenure, notice lead and retention credits are real.
  - Labor day multipliers, call-out minimums, dispatch minimums and shared trip: real.
  - Late-fee bands, minimum and courtesies: plausible as the company's own schedule.
  - Upgrade: phasing, term, volume, training overlap and out-of-scope conversion: real.
  - Weaker, recorded as observation O-7: "SOC overlap" (10/5 % off after-hours remote labor when the client holds Sentinel, keyed on threat hunting), "monitoring continuity" (Sentinel tier lowers a ClearPath reinstatement fee) and the after-hours frequency discount (more invoiced after-hours tickets give a cheaper rate). No demonstration that no MSP publishes these, so they are not RED.

### findings
Charter-global. Every task file cites these by id.

**C-1 SOURCE-FACTOR RED: loyalty-rate ladders select the fall-through value, or a surcharge, on reachable tiers (XF-A6 / unreal ladder).**
- Symptom:
  - `loyalty_remote_rate` tiers: `loyalty_long_rate_usd: 145.0`, `loyalty_mid_rate_usd: 150.0`, fall-through `P('remote_hourly_rate_usd')`.
  - `onsite_loyalty_rate` tiers: `onsite_loyalty_long_rate_usd: 160.0`, `onsite_loyalty_mid_rate_usd: 168.0`, fall-through `P('onsite_hourly_rate_usd')`.
  - Neither policy is scoped to a tier.
- Evidence:
  - `remote_hourly_rate_usd` by tier: Monitor 165, Essentials 155, Standard 150, Professional 145.
  - `onsite_hourly_rate_usd`: Standard 170, Professional 160, Premier 155, Enterprise 150.
  - Remote after-hours invoice labor is reachable on Monitor, Essentials, Standard and Professional (non-P1). Onsite invoice labor is reachable on every tier, beyond the included hours.
- Demonstrated consequence:
  - Standard, 12–23 months live: the "loyalty" mid tier gives 150 = the fall-through 150.
  - Professional: the long tier 145 = the fall-through 145, and the mid tier 150 is a surcharge above the standard rate.
  - Onsite on Professional: long 160 = fall-through, mid 168 is a surcharge.
  - Onsite on Premier and Enterprise: both "loyalty" rates (160/168 vs 155/150) exceed the standard rate.
  - Two tiers of one ladder select the same value. A loyalty discount that raises the price is not a treatment any MSP publishes.
- Affected: `managed.extended.yaml` → `managed_ext_after_hours_remote_labor` (params, rule "The loyalty labor rate…", compute `hourly_rate`) and `managed_ext_onsite_visit_labor` (params, rule "The onsite loyalty rate…", compute `onsite_rate`).
- Task effect: none on task 1, an Essentials agreement (155/175 > tiers). This is a charter-level RED.

**C-2 SOURCE-CHAIN RED (realism of the prerequisite order): late fees are assessed on labor charges added to an invoice after its due date.**
- Symptom: the late-fee rule's two prerequisite sentences require that "that invoice carries the remote after-hours labor charge / onsite visit charge of every ticket resolved in the calendar month before its posting" before its late fee is fixed. Its unpaid balance is "every charge on the agreement's billing ledger less every payment…".
- Base facts:
  - The labor tools post onto a named past invoice, dated today (`post_remote_after_hours_labor_c0dca9e8`, `post_onsite_visit_labor_c7936621`: `invoice_number=invoice_number, posted_date=ctx.now()[:10]`).
  - Base assesses late fees "On the first day of each calendar month" on "the invoice's unpaid balance on the assessment day … as of the end of the day before the assessment day" (`managed_msr_invoice_unpaid_balance`).
  - The domain order stated in the blueprint is "a fee is invoiced before it can be paid or waived".
- Root cause: the edge is built so that the charges are invoiced after the invoice is past due and past its assessment day, and then immediately carry a late fee. No MSP charges a late fee on a line the client was never billed for by the due date.
- Consequence: demonstrated on task 1 (see `1.md` `findings`).
- Affected: rule sentences and `prerequisite[0..1]` of `managed_ext_first_late_fee`.

**C-3 RED (XF-A3): assembly sentences name the factor quantities instead of a generic combination statement.** Every member:
- current_month_fee: "The seat amount is first worked out under the frontline seat rule; the percentage credits are then added together … the server management fee is added last."
- reinstatement_charge: "The fee built under the re-validation rule is first multiplied by the first-suspension relief share; the two reductions are then added into one percentage…"
- signed_exit_fee: "The fee is the exit-fee percentage of the monthly basis times the months charged; the reductions are added into one percentage…"
- after_hours_remote_labor: "The billed minutes divided by 60 are multiplied by the hourly rate and by the day multiplier; the three reductions are added into one percentage…"
- onsite_visit_labor: "The billed minutes divided by 60 are multiplied by the hourly rate, that labor is reduced once by the visit courtesy … and the trip charge is added last."
- first_late_fee: "The amount from the balance band rule is first reduced once by the two courtesies added together …; the late-fee minimum is then applied…"
- essentials_upgrade_rate: "The discounts are added into one percentage and the rate built under the upgrade pricing rule is reduced once by it…"
- auto_renewal_rate is the only generic one ("The adjustments are combined into one net percentage…"). Even it refers to "the renewal rate selected above".

No scored effect demonstrated, so this is charter-level. Order is fixed in each, so XF-A4 is satisfied.

**C-4 SOURCE-POLICY RED (XF-C17): the sibling labor overwrites claim each other's whole labor class while each policy scopes only the most recent ticket.**
- The after-hours `replaced_by` says "onsite business-hours visit labor follows its own visit schedule". That covers all onsite business-hours labor.
- The onsite policy scopes itself to "the agreement's most recently resolved ticket whose labor class is onsite business-hours … and only for that visit", and leaves "every other labor amount … under the base rule". The onsite `replaced_by` mirrors this, so after-hours labor is over-claimed in the same way.
- Consequence: two unbilled onsite visits, the older being X. The after-hours overwrite prices X by the visit schedule (dispatch minimum, shared trip, loyalty rate, courtesy). The onsite overwrite prices X by the base rule (minutes/60 × `onsite_hourly_rate_usd` + `onsite_trip_charge_usd`). Two different amounts.
- No effect in task 1: each class has exactly one unbilled ticket, and it is the most recent.

**C-5 SOURCE-POLICY RED (XF-C18): undeclared departures from in-force base sentences.**
- (a) Exit:
  - Base, not overwritten: "Its termination_effective_date is the later of the date the client asks for and the notice_received_date plus notice_days calendar days".
  - Extended: "puts the notice on the agreement with … the signing date as notice_received_date and the request's effective date as termination_effective_date". `months_charged`, `lead_days` and the retention days all read the request's date.
  - Consequence: a request registered with requested date = registration + notice_days, and signed k > 0 days later. Base gives signing + notice_days, while extended gives the request's date, so `months_charged` and the notice-lead tier can differ.
  - No effect in task 0: Dec 31 is later than Oct 8 + 60.
- (b) Onsite:
  - Base, not overwritten: "when a visit's minutes exceed the included onsite minutes remaining for the month, only the excess is billable and the onsite minimum does not apply to that excess".
  - The extended dispatch rule bills `max(recorded, same_day_minimum_minutes)` with no excess carve-out.
  - Consequence: on Standard or above, a same-day partially-included visit gives the excess under base and max(excess, 120) under extended.
  - No effect in task 1 (Essentials, 0 included hours).

**C-6 SOURCE-POLICY RED (XF-B11/B14): first-match reads with no tie or multiplicity rule.**
- (a) `managed_ext_current_month_fee` reads "the license_qty of the client's active Microsoft 365 F3 subscription" / "… Business Premium subscription" through `CFIELD(...)`, which returns the first match. Licensing explicitly allows several subscriptions of one plan ("the same plan on different terms or billing frequencies").
  - Consequence: a client with an annual and a monthly active F3 has two readings. One subscription's qty, compute's arbitrary first, or their sum can each select a different frontline tier.
- (b) `managed_ext_signed_exit_fee`: "the most recently registered one is the notice signed" has no tie rule for two pending requests with one `created_at` minute.
- No effect on either task world (one active F3, one Premium, one pending request in task 0).

**Observations** (no consequence demonstrated):
- O-1: Edge conditions are slightly stronger than the sentences (the fee and exit renewal edges). The exit/fee sentence's literal "every service month begun", read with the go-live month, is resolved by base.
- O-2: The exit/fee edge `effect` asserts a world-specific outcome ("three monthly fees stand … selects the average").
- O-3: `RND` is Python banker's-on-float, while the rules say "half up". No binary tie arises in either world.
- O-4: `post_monthly_fee_19cc11da` dates a late-posted fee today, while rule and overwrite say "invoiced in advance on monthly_invoice_day". The due date then runs from the actual posting.
- O-5: `sign_tier_upgrade_933f385b` sets `variant_name` and `seat_rate_usd` at signature for an upgrade effective the 1st of next month. Base: "takes effect on the first day of the calendar month after the signature".
- O-6: The late-fee in-scope identity ("every charge on the agreement's billing ledger less every payment…") is false when the agreement carries an unapplied credit balance (base `managed_payment_application`).
- O-7: Realism weaknesses in SOC-overlap, monitoring-continuity and after-hours-frequency tiers (see `factor_ladders`).
- O-8: `XSUM` over `security_endpoint_changes` reads every one of the client's Sentinel holdings, including a closed prior subscription. The rule says "the client's Sentinel ledger", so the reading is literal, but not probed.

## closing_checklist
Written after both reveals (2026-10-18T01:59:43Z onward). Nothing above this heading was changed after the reveal, except the freeze-time line of the task files.

The difficulty is **not closable in revision_1**:
- The per-task audit files `0.md` and `1.md` correspond one-to-one with the tasks, with `_difficulty.md` alongside. This is the first revision.
- Comparison sections: task 0 has gold equal to the blind derivation, with RED T0-F1/F2/F3. Task 1 has gold equal to the blind derivation, with RED T1-F1/F2/F3. Neither comparison is a PASS.
- Coverage and scope:
  - Scopes are disjoint and jointly complete. `charter_scope` 0 = {reinstatement, renewal, fee, exit} and 1 = {after-hours, onsite, late fee, upgrade}, matching the graph-derived trees.
  - Task tools and GT are closed: each task tool appears in exactly one `charter_scope`.
  - uuid8s are independent.
- Trees: each has 3 prerequisite problems, 3 value_input edges and a user-owned root, with no cycle. The difficulty-wide graph is a DAG.
- Factors:
  - Counts, labels, baselines and per-world weight PASS on both tasks.
  - The ladder-realism RED C-1 is open.
  - The near-miss RED T0-F2 and the proof-text REDs T0-F3 and T1-F3 are open.
- Charter REDs C-1..C-6 are open.
- Gate re-run on the final form: not performed. Per Step 0 the auditor does not run gates. The coordinator snapshot of 2026-10-18T01:39:54 (all rc=0) is the latest, with `check_traceability` deferred.

VERDICT revision_1: task0=RED T0-F1,T0-F2,T0-F3 task1=RED T1-F1,T1-F2,T1-F3 charter=C-1,C-2,C-3,C-4,C-5,C-6

## revision_2

## charter_global_frozen (revision_2)
- Frozen 2026-10-18T06:09Z, before any r2 GT or the round-2 claims were read.
- Entry gate: the last line of `worklog.md` is exactly `REWORK round 2: gates 7/7 green`.
- Coordinator snapshot, executed `/tmp/erl0069_coord/snapshot.sh managed_services_agreements 2` @ 2026-10-18T06:02:21:
  - check_extended rc=0 EXTENDED OK
  - check_task_tools rc=0 TASK TOOL CONTRACT OK
  - replay_tasks rc=0 REPLAY OK
  - check_solvability rc=0 SOLVABILITY OK
  - check_compute rc=0 COMPUTE OK
  - check_grounding rc=0 GROUNDING OK
  - check_cross_fire rc=0 SCOPE OK
- Views and hashes:
  - r2/0.view.json 76920f7d5f7dc96c4c6df921ade58405699126ddbdea57de6325532d3d184ed4
  - r2/1.view.json a1a7f4e23eb648b8c0adf4a8ebcc8019bbd4b05aea17e8c4765569a6f8b5b2a9
  - managed.extended.yaml 35516d1c44057c037d9ccf552babe8a73facb67716b68cd2cc2b6e7097b77adf (changed, so every charter-global section is re-derived below)
  - task_tools.py 819877d3…7010 (unchanged, so `action_binding_and_uuids` carries forward by reference to revision_1)
- XF_recipe.md re-read (md5 7ba3ca86…), including the new points 23–26.

### re-derived sections (summary of checks)
- Base section is still verbatim.
- Mechanical sweep over all 8 policies:
  - Every `compute_basis` quote, `baseline.rule` sentence, `replaced_by` and `policy_source` is verbatim in its rule.
  - No factor reaches another factor's binding (A1). No factor id is a substring of a tool name (A7). No shared bindings.
  - No plain (non-result) binding reads a factor-owned binding (XF-26). Every policy now assembles in `result`.
  - Every factor sentence names the quantity it modifies ("… of/on the renewal rate / monthly fee / reinstatement fee / early termination fee / after-hours remote amount / onsite visit labor / late fee / upgraded rate").
- Counts: renewal 6 (5p/1m), fee 6, reinstatement 4, exit 6, after-hours 6, onsite 4, late fee 5, upgrade 6.
- Prerequisite graph:
  - renewal → fee (gate `result`, now that `seat_amount` is inlined).
  - {reinstatement (state_gate), renewal, fee} → exit.
  - {late fee, after-hours, onsite} → upgrade (value_input on `standing_pct` / `conversion_pct`).
  - The late fee has no prerequisite now. Acyclic, all state form, every `resolved_by` = `target_tool`.
  - Each state sentence is brought about by exactly one tool. The new upgrade sentences ("… carries the remote after-hours labor charge / onsite visit charge of every ticket resolved before the current month …") pass the four-point test.
- XF-24 trigger rule. Events written by the tools: `managed_renewed`, `managed_monthly_fee`, `managed_reinstated` + `managed_reinstatement_fee`, `managed_notice_given` + `managed_early_termination_fee`, `managed_billable_labor` ×2, `managed_late_fee`, `managed_tier_changed`. Base triggers: `managed_reinstated` → managed:reinstatement_fee and `managed_notice_given` → managed:early_termination_fee, both the same category. No crossing. PASS.
- XF-23 all-pairs method-shape tables:

| factor | tier pairs |
| --- | --- |
| price_protection_rule | uplifted RND(cur×(1+u)) vs held cur: **same input, constant multiplier → FAIL**. lower-of vs either: adds list input + min → pass |
| frontline_seat_rule | half-rate (adds F3 input) / out+flat (adds F3 + tariff) / flat: pass |
| environment_revalidation_rule | +per-seat (adds seat_count) / +flat (tariff) / alone: pass |
| exit_billing_basis_rule | avg of fee sum / rate×ledger seats / rate×floor (distinct fields): pass |
| after_hours_callout_rule | max (conditional pick) / +tariff / recorded: pass |
| onsite_dispatch_rule | max (conditional pick) / +tariff / recorded: pass |
| balance_band_rule | capped piecewise / piecewise / whole: pass |
| upgrade_pricing_rule | phased (adds std) / list-ratio (adds 124/89 tariff) / std: pass |

- Round-1 charter items:
  - C-2: closed (late-fee edges removed; late fee counts only the invoice's own lines).
  - C-3: closed (all 8 assembly sentences generic: "The schedules of this paragraph change the standard … in one fixed order: a value or a method a schedule selects replaces the standard one first; the percentage … then …; flat charges / the minimum / the cap … last").
  - C-4: closed (each sibling `replaced_by` names exactly the other's case: "most recently resolved onsite business-hours ticket … when that visit is wholly billable" and "most recently resolved remote after-hours ticket").
  - C-5(a): closed (exit scope requires exactly one pending request whose date is at least notice_days after signing; every other ETF stays under base).
  - C-5(b): closed (a partly included visit stays under base).
  - C-6: closed (fee scope requires at most one active F3 and at most one active Business Premium; exit scope requires exactly one pending request).
  - C-1: the two loyalty ladders are now percent discounts (5 / 2.5 % off), so the tier rates are no longer coincident. But other class members remain (C-1r below).

### findings (revision_2, charter)
**C-1r SOURCE-FACTOR RED (unreal ladder: absolute values on ladders not limited to a tier).** All remaining members, including two I missed in revision_1 that were present then:
- (a) `managed_ext_onsite_visit_labor.shared_trip_schedule`: tiers 0 / `trip_shared_usd` 47.50 / fall-through `P('onsite_trip_charge_usd')`. On ClearPath Professional, Premier and Enterprise `onsite_trip_charge_usd` = 0.0. A single visit is charged 0, while two visits in six months are charged 47.50, a surcharge for visit frequency. The 3-or-more tier (0) equals the fall-through (0). Onsite invoice-route labor is reachable on those tiers beyond their included hours.
- (b) `managed_ext_reinstatement_charge.environment_revalidation_rule`: a suspension of 30 days or more costs fee + 2.50 × seat_count, and one of 15–29 days costs fee + 150. For any agreement under 60 seats, the longer suspension is charged a smaller re-validation fee. Example: 46 seats → +115 against +150. Non-monotone in the very quantity the rule says drives re-validation.
- (c) `managed_ext_current_month_fee.frontline_seat_rule` tier 3: 1–9 F3 users are taken out of the billed seats and replaced by one flat 95.00. Seats removed: Monitor 1–2 F3 seats are 38.50–77.00, Essentials 1 seat is 89.00. On those tiers the "frontline" treatment costs more than billing the seats.

**C-7 RED (XF-23 method shape).** `managed_ext_auto_renewal_rate.price_protection_rule`: tier 2 "the uplifted renewal rate, with no list comparison", `RND(seat_rate_usd × (1 + uplift_pct/100))`, and tier 3 "held at the expiring seat_rate_usd", `seat_rate_usd`, are the same input up to a constant multiplier. The tier-3 hold also makes `first_renewal_uplift_schedule` inert. This is the only member across the 8 method factors.

**Observations carried forward:**
- O-3 (`RND` is Python round, not half-up; no tie arises in either r2 world).
- O-4 (late-posted monthly fee is dated today).
- O-5 (the upgrade tool writes tier and rate at signature).
- O-7 (SOC-overlap, monitoring-continuity and after-hours-frequency realism).
- O-1, O-2, O-6, O-8 unchanged where the text is unchanged.

## closing_checklist (revision_2)
Written after the r2 reveal at 2026-10-18T06:09:47Z.
- One audit file per task, with revision_1 preserved verbatim above every revision_2 section.
- Scopes are disjoint and complete: {reinstatement, renewal, fee, exit} and {after-hours, onsite, late fee, upgrade}.
- Tool uuid8s unchanged and independent.
- Trees:
  - task 0: 3 prerequisites with 3 value_input edges (+1 state_gate), user-owned root.
  - task 1: 3 prerequisites with 3 value_input edges, user-owned root.
  - Difficulty-wide graph is a DAG.
- Factor counts, labels, baselines and per-world weight PASS on both tasks. Near-misses are present in all 8 computations.
- The cross-category trigger rule (XF-24) and complete ledgers (XF-25) PASS. The only unbilled or unposted items in either world are the declared prerequisites.
- Gates: the coordinator snapshot of round 2 shows 7/7 rc=0.
- **Not closable**: charter REDs C-1r(a,b,c) and C-7 are open.
- Note for the coordinator: C-1r(b) and C-1r(c) were present unchanged in revision_1 and missed by that audit. They are not regressions from the rework. C-1r(a) is the same class as round-1 C-1 and was also present in revision_1.

VERDICT revision_2: task0=PASS task1=PASS charter=C-1r,C-7

## revision_3

## charter_global_frozen (revision_3)
- Entry gate: the worklog's last line is exactly `REWORK round 3: gates 7/7 green`.
- Executed `/tmp/erl0069_coord/snapshot.sh managed_services_agreements 3` @ 2026-10-18T07:56:30. All 7 gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Hashes:
  - r3/0.view.json 76920f7d…84ed4 and r3/1.view.json a1a7f4e2…b2a9. Both are **identical to r2**, so the worlds are unchanged.
  - managed.extended.yaml 9b08f245936b457838ce29ab07c458d4bf03e43b395eda880bbb7fc2b63c2c9e (changed, so every charter-global section is re-derived).
  - task_tools.py 819877d3…7010 (unchanged).
  - XF_recipe.md md5 7ba3ca86… (unchanged).
- The worklog's "round 3 claims" list was read before this section, as instructed. It carries no task values beyond those already known from revision_2.

### exhaustive pass, every XF point × every policy (revision_3)
| point | result |
| --- | --- |
| A1 / A2 / A7 / XF-26 (mechanical) | Clean on all 8. No factor reaches another factor's binding. No factor id is a substring of a tool name. No shared bindings. No plain non-result binding reads a factor-owned binding. Every factor sentence names its result quantity. |
| A3 / A4 | Each of the 8 rules has exactly one generic "The schedules of this paragraph change the standard … in one fixed order …" sentence, and the non-commuting order is fixed. |
| A5 | No "as another policy figures it" phrasing. Every cross-policy dependency is a state-form sentence. |
| A6 / XF-23 | Re-run below. All method pairs pass. Partial coincidences (not across the whole domain): frontline tier 3 = tier 1 when seat_rate × F3 ≤ 95; price-protection tier 3 = tier 1 when uplift ≤ 2 %. |
| B8 rule == compute | Hand-checked every changed sentence: day multiplier = tier multiplier + 0.25 / + 0.5; call-out P1 = max(m, 60) + 15; dispatch same-day = max(m + 30, 120); trip = RND(50 % × trip charge); frontline flat = min(95, removed seats × rate); server 50 / 60; re-validation fee + 150 + 2.50 × seats; renewal loyalty tier = lowest of (uplifted, list, expiring × 1.02); upgrade renewal-term tier = cur + gap × MONTHS(term_start, today)/term_months. Every one equals compute. |
| B9 / B10 | Every `compute_basis` quote is verbatim. Rounding placement is stated for each new RND (trip, loyalty tier, term-spread tier). |
| B11 / B12 / B13 / B14 | Ties: ticket resolutions are stated unique per minute, and the exit request is scoped to exactly one. Month counts use whole months. Absent records have explicit tiers. Decoys are excluded by status, class or window. |
| B15 | **Member, C-8 below.** |
| C16 / C17 / C18 | Scoped `replaced_by` on all 8. The siblings now name each other's exact case, including "on a tier whose onsite_trip_charge_usd is above zero". No undeclared base departure beyond C-8. |
| D19 / XF-24 | Tools are unchanged, so revision_2 carries forward. Each docstring gives formats only, and no written event triggers into another category. |
| D20 / XF-25 | Seeds are unchanged since revision_2 (same view hashes). The cross ledgers reproduce every balance and count. Every historical priced row still equals the r3 formulas: Sat 1.5 + 0.25 = 1.75; Sun 2.0; next-day 60 + 30 = 90; frontline min(95, 8 × 121.52) = 95; 3 servers × 60. |
| D21 | See the C-1r class sweep. O-7 is kept as an observation and ruled not RED: multi-product and volume labor discounts are a published MSP practice. |
| D22 | Proof-text sweep of both task JSONs: every date or amount not in the seed is derived and correct (2026-12-07, 2027-08-01, 0.25, 1.03, 95.00, 150.00, 102.24, 315.00, skip-run figures). No stale method wording. |

XF-23 all-pairs (revision_3):
- price_protection: uplifted vs lowest-of-three (adds list + ceiling cap); uplifted vs lower-of (adds list + min); lowest-of-three vs lower-of (adds the tariff ceiling `loyalty_ceiling_pct`). Pass. **C-7 closed.**
- upgrade_pricing: phased constant share vs term-spread (adds term_start / today) vs standard. Pass.
- revalidation: adds seat_count. Pass.
- frontline, exit basis, call-out, dispatch, band: pass as in revision_2.

### C-1r class sweep: ladder monotonicity and relative outcome, every ladder of every policy
- Closed: (a) trip is now 50 % of the tier's charge and the onsite schedule is scoped to trip > 0; (b) re-validation 30+ days ≥ 15–29 days; (c) frontline flat never above the removed seats.
- Rework-found members are fixed: day multiplier, call-out, dispatch, server fee, upgrade ratio.
- Checked and clean: renewal (uplift ≤ cap; suspended ≥ standard ≥ loyalty; growth / SLA / standing / intensity ordered); Sentinel, Continuum and CSP credits; reinstatement relief, cure and monitoring; exit tenure, retention, SLA and notice-lead; after-hours tenure, courtesy, SOC and frequency (direction only); onsite trip, tenure and courtesy; late-fee rate, minimum, band (continuous at 1,000 and 5,000), courtesies; upgrade commitment, standing, training and conversion.

### findings (revision_3, charter)
**C-1r(d) SOURCE-FACTOR RED (introduced by this rework).** `managed_ext_essentials_upgrade_rate.upgrade_pricing_rule` tier 2-of-3, "renewal term … step-up spread over the term": rate = cur + (std − cur) × MONTHS(term_start_date, today)/term_months.
- In the first month of a renewal term the elapsed whole months are 0, so the Standard rate equals the client's current Essentials rate. Example: 85.44 → 85.44, before discounts.
- An upgrade to a higher tier at the lower tier's price is not a treatment an MSP publishes.
- The step-up also rises through the term: month 6 gives 102.24, month 11 gives 116.24.
- Reachable on any renewed Essentials agreement with ≥ 24 months live.

**C-1r(e) SOURCE-FACTOR RED (present since revision_1, missed then).** `managed_ext_current_month_fee.frontline_seat_rule` inverts the per-user price at the group threshold.
- 9 F3 users cost min(95, 9 × rate) = 95.00 in total (10.56 each).
- 10 users cost 10 × rate × 50 %: 192.50 on Monitor, 445.00 Essentials, 620.00 Standard, 1,180.00 Enterprise.
- The larger group gets the worse per-user price, and adding the 10th user raises the charge by up to 1,085.

**C-1r(f) SOURCE-FACTOR RED (present since revision_1; same class as the server fee the rework fixed).** All-units volume tiers lower the total when a seat is added:
- `managed_ext_current_month_fee.seat_volume_price_break`, 74→75 seats: 74 × r × 0.98 = 72.52r > 75 × r × 0.96 = 72.00r. On Standard at 124.00: 8,992.48 vs 8,928.00.
- `managed_ext_essentials_upgrade_rate.upgrade_volume_discount`, 49→50 seats: 49 × 0.98 = 48.02 > 50 × 0.96 = 48.00 (× rate).

**C-8 SOURCE-POLICY RED (XF-B15 / undeclared departure; present since revision_2).** `managed_ext_first_late_fee` defines the invoice's own lines as "the charges posted on the agreement's billing ledger in the month window two months before today (dated at least two and fewer than three whole months before today), which are its own lines".
- The scope excludes payments, credits and memos and other invoices of the month. It does not exclude a line added to the invoice after its posting day but before its due date.
- Second reading: an Aug-1 invoice with a labor line posted 2026-08-20.
  - Base measure on the 2026-10-01 assessment day: fee + labor.
  - Extended on 2026-10-14: fee only (MONTHS(08-20, 10-14) = 1).
  - Extended on 2026-10-25: fee + labor.
- The same fee therefore depends on which day of the assessment month it is posted. "Which are its own lines" is false for that record.
- No effect in task 1: INV-013814 carries only its fee.

**Observations carried forward:** O-3, O-4, O-5, O-7 (ruled not RED, above). The "covered seat" wording in the renewal intensity sentence is equal to `seat_count` whenever the seat ledger is complete (XF-25), so it is not RED.

## closing_checklist (revision_3)
- Both tasks PASS on all four relationships, against unchanged worlds and identical gold.
- Gates: 7/7 rc=0 at round 3.
- Every round-2 RED is closed: C-1r(a, b, c) and C-7. No task value regressed.
- Not closable. Charter REDs open:
  - C-1r(d): new in this round, introduced by the rework.
  - C-1r(e) and C-1r(f): present since revision_1 and missed by revisions 1 and 2.
  - C-8: present since revision_2 and missed then.
- This pass covered every XF point and the full C-1r class over all 8 policies and both seeds, and lists every member found.

VERDICT revision_3: task0=PASS task1=PASS charter=C-1r(d),C-1r(e),C-1r(f),C-8

## revision_4

## charter_global_frozen (revision_4)
- Entry gate: the worklog's last line is exactly `REWORK round 4: gates 7/7 green`.
- Executed `/tmp/erl0069_coord/snapshot.sh managed_services_agreements 4` @ 2026-10-18T09:13:02. All 7 gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Hashes:
  - r4/0.view.json 07b83edd657b55e0f5551fc7520599bb158ef7ba081b443290bdf184f0f53f41
  - r4/1.view.json 7aa441e3a4f10bcf5f19113513a159cc3dfb4b24a354fc63fc80f0ab3062598d
  - managed.extended.yaml fe103bfa75da9fd4bdfc89b63430bb8275adf9318b0a7f7ea34d9ed0daeb64e9 (changed)
  - task_tools.py 819877d3…7010 (unchanged)
- contamination_disclosure: the "round 4 claims" list, read as instructed before any derivation, states this round's task values. Neither task is blind this round. Every figure below was recomputed independently with the gate DSL on the r4 views and the r4 charter.
- What changed:
  - Charter: renewal growth, fee volume, fee frontline, upgrade volume, the upgrade renewal-term tier, and the late-fee balance/scope.
  - Task 0 seed: 52 managed_billing amounts repriced: monthly fees, SLA credits, late fees, payments.
  - Task 1 seed: unchanged except `frozen_time` 2026-10-14 → 2026-10-01 14:20 EDT. No seeded row is dated after 2026-10-01.

### closure verification
- **C-1r(d): closed.** The renewal-term upgrade tier is min(cur + (Standard list − own list), standard × (1 − 3 %)). It is always above cur (+35.00) and below standard. XF-23 against both other tiers passes: it adds a list-difference input and a min.
- **C-1r(e): closed.** The frontline charge is graduated (11.50 each to 9 users, then 50 % of rate each), monotone in users with no cliff, and never above billing those seats. Remaining note, an observation not a RED: the marginal price for users 10+ (0.5 × rate) is above the first nine's 11.50. This is read as a published first-nine allowance rather than an inversion.
- **C-1r(f): closed.** Fee volume, upgrade volume and renewal seat-growth are graduated. Band-boundary probe of every reworked ladder:
  - The marginal seat cost is rate × (1 − other % − band %) > 0 at every boundary: 24/25 and 49/50 (upgrade), 39/40 and 74/75 (fee), mid/high growth seats (renewal).
  - The frontline charge rises at every user, including 9→10.
- **C-8: closed.** The balance is now the invoice's lines as they stood at the end of the day before the assessment day. The scope requires assessment and posting on the 1st, so no window proxy remains.

### re-checks of the changed text and regressions (all 8 policies)
- Mechanical sweep is clean on all 8: B9, replaced_by, policy_source, A1, A7, XF-26. Each assembly sentence is still single and generic.
- Rule == compute was hand-checked for every changed sentence. One mismatch: C-9 below.
- XF-23: every method pair still passes (frontline tiers: graduated vs per-user vs flat; upgrade tiers: phased vs capped list-difference vs standard).
- Seeds:
  - Task 0: every repriced historical fee equals the r4 schedule. Example, 2024-11: 32 × 121.52 + 8 × 11.50 = 3,980.64; less 5.05 % = 3,779.62; + 180 = 3,959.62.
  - Every task-0 invoice is fully settled.
  - Base late fees equal 1.5 % of the late-fee-free balance: 66.87, 36.87, 70.07.
  - SLA credits = 2 % of the repriced month fees: 86.92 and 91.39.
  - Cross ledgers are unchanged.
- Near-misses are still present in all 8 computations. Task 1 at 2026-10-01: the 2025-04-01 late fee counts for neither the late-fee rate nor the upgrade standing discount.

### findings (revision_4, charter)
**C-9 SOURCE-POLICY RED (B8 rule ≠ compute; introduced by this rework).** `managed_ext_current_month_fee.seat_volume_price_break`:
- Rule: "reads the billed seats, the covered seats on the seat ledger … or the minimum-commitment floor if that is greater: … each covered seat from the volume_mid_seats-th … earns …, and the earned percentages are summed and divided by the covered seats".
- Compute counts and divides by `MX(covered_seats, floor_seats)`.
- When the floor exceeds covered seats and is ≥ 40, the two readings differ. Example: contracted 80 on Standard → floor 68, covered 60. Compute (68 − 39) × 2/68 = 0.853 %; the "covered seats" reading (60 − 39) × 2/60 = 0.700 %.
- No effect on task 0: covered 46 > floor 40.

**C-10 SOURCE-POLICY RED (XF-C18 undeclared departure; introduced by this rework).**
- `managed_ext_first_late_fee` now measures "every charge on the agreement's billing ledger less every payment, service credit and credit memo …". Its compute adds `managed_late_fee` to the charges. The scope now admits any monthly late fee on the agreement's only unpaid invoice, not just the first.
- The base sentence that directly follows the superseded clause stays in force and is not overwritten: "late fees are not themselves assessed late fees". The base measure also excludes late fees from both sides.
- Second reading, using task-0-like rows: the only unpaid invoice carries last month's unpaid late fee of 66.87.
  - Base balance excludes the 66.87.
  - Extended balance includes it, so a late fee is assessed on a late fee.
- No effect on task 1: INV-013814 carries no earlier late fee.

**Observations carried forward:** O-3, O-4, O-5, O-7, plus the frontline first-nine allowance note above. Upgrade relative tiers: the renewal-term client's capped rate (≈ standard − 3 %) is above the initial-term phased rate. The same ordering has held since revision_1 and is read as a first-term phase-in offer, so it is an observation.

## closing_checklist (revision_4)
- Task 0 and task 1 PASS: gold equals the independent recomputation figure for figure (below).
- Gates: 7/7 rc=0 at round 4.
- Round-3 REDs C-1r(d, e, f) and C-8 are closed.
- Not closable: C-9 and C-10, both new in the round-4 rework text.

VERDICT revision_4: task0=PASS task1=PASS charter=C-9,C-10

## revision_5

## charter_global_frozen (revision_5)
- Entry gate: the worklog's last line is exactly `REWORK round 5: gates 7/7 green`.
- Executed `/tmp/erl0069_coord/snapshot.sh managed_services_agreements 5` @ 2026-10-18T09:50:09. All 7 gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Hashes:
  - r5/0.view.json 07b83edd…3f41 and r5/1.view.json 7aa441e3…598d. Both are identical to r4, so the worlds are unchanged.
  - managed.extended.yaml 46c1626b028e4829c74c3bff6cf1961f4363e98828b4c18e4876162ba3229dfb (changed)
  - task_tools.py 819877d3…7010 (unchanged)
- contamination_disclosure: the "round 5 claims" list states the task values, and the r4 GT is already known. Not blind. Every value was recomputed independently with the gate DSL.

### closure verification and changed-text checks
- **C-9: closed.** The rule reads "the billed seats for the break, which are the covered seats on the seat ledger … or the minimum-commitment floor, whichever is greater … divided by the billed seats". This equals compute `MX(covered_seats, floor_seats)`.
- The sweep's wording fixes are correct and equal compute:
  - intensity: "per seat of seat_count".
  - re-validation: "every seat of seat_count".
- Mechanical sweep is clean on all 8: B9, replaced_by, policy_source, A1, A7, XF-26.
- No other policy text changed in substance. The task values recompute unchanged.
- **C-10: partly closed.**
  - The rule now states "late fees are not themselves assessed late fees". Compute subtracts the late fees on the invoice carrying the agreement's most recent late fee, when that invoice is still unpaid. A prior unpaid late fee on the assessed invoice itself is now excluded.
  - A remaining member is below (C-10r).

### findings (revision_5, charter)
**C-10r SOURCE-POLICY RED (rule ≠ compute ≠ base, for an unpaid late fee on another invoice).**
- The balance is computed ledger-wide: all charges, including late fees, less all settlements, less only the late fees of the one invoice carrying the most recent late fee. The rule justifies this with "(the late fees of settled invoices net out against the payments that settled them)".
- That holds only if the payment covered the late fee. Take an invoice B whose principal was paid in full while its earlier late fee was left unpaid.
  - B has no unpaid balance under the base measure, which excludes late fees from both sides, so A remains "the agreement's only invoice with an unpaid balance" and the fee is in scope.
  - The most recent late fee sits on the assessed invoice A, so B's late fee is never subtracted.
- Probe on the task-1 world, with a hypothetical unpaid 25.00 late fee on INV-013756 and a prior 32.49 late fee on INV-013814:
  - compute `invoice_charges` = 2,190.90 (2,165.90 + B's 25.00), against 2,165.90 under the base measure and the rule's own "late fees are not themselves assessed late fees".
  - Fee 13.16, assessed partly on another invoice's late fee.
- The alternative reading treats B as an invoice "with an unpaid balance", which puts the fee out of scope and under the base rule. Either way the extended number is not entailed.
- No effect on task 1 (no unpaid late fee anywhere).

## closing_checklist (revision_5)
- Task 0 and task 1 PASS. Gold equals the independent recomputation for every write, expected value, baseline and per-factor substitution (unchanged from revision_4).
- Gates: 7/7 rc=0.
- C-9 is closed.
- Not closable: C-10r.

VERDICT revision_5: task0=PASS task1=PASS charter=C-10r

## revision_6

## charter_global_frozen (revision_6)
- Entry gate: the worklog's last line is exactly `REWORK round 6: gates 7/7 green`.
- Executed `/tmp/erl0069_coord/snapshot.sh managed_services_agreements 6` @ 2026-10-18T10:21:09. All 7 gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Hashes:
  - r6/0.view.json 07b83edd…3f41 and r6/1.view.json 7aa441e3…598d. Both are identical to r4/r5, so the worlds are unchanged.
  - managed.extended.yaml 36f72258dfe8b5d8aac6c458da26b638a67cafaac07cd75d1911790285dfcd86 (changed)
  - task_tools.py 819877d3…7010 (unchanged)
- Not blind (values known from earlier rounds and the claims list). Every value was recomputed with the gate DSL.

### C-10r closure: judging the scoped route
The coordinator's route keyed the assessed invoice's own lines by exact invoice id; the reworker found it inexpressible in the DSL and scoped the policy instead. Judged against the criteria (rule words == compute in every in-scope case; out-of-scope handling stated):
- **Scope (self-naming overwrite):** "the agreement's only invoice with any amount unpaid at the end of the day before the assessment day, its late fees included, so that every other invoice is settled in full together with any late fee it carries, no other invoice having been assessed a late fee on the day of that invoice's most recent late fee". Out-of-scope handling is stated: "every other late fee remains under the base rule, late_fee_pct_monthly percent of the invoice's unpaid balance …".
- **In-scope equality, case by case:**
  - (i) First assessment on A: every other invoice nets to zero, including its late fees and their payments. The most-recent-late-fee invoice is settled, so nothing is subtracted. Ledger-wide = A's own non-late-fee lines less A's settlements = the rule's own-balance definition.
  - (ii) A already carries late fees: A stays unpaid, so it is assessed every 1st and its latest late fee is the agreement's most recent. A same-day tie with another invoice is excluded by scope. Its late fees are subtracted, giving equality.
  - (iii) The revision_5 counter-case, B with principal paid and late fee unpaid: B now has "an amount unpaid, its late fees included", so the fee is out of scope and under the base rule. The rule states this.
- Payments count in full against the lines in both base and extended.
- The route follows the accepted XF-15 pattern: scope the policy, by a self-naming overwrite, to the case compute prices exactly, and restate the base for the rest.
- **C-10r: closed.**
- Residual, observation O-6 (carried since revision_1, not RED): the ledger identity would break only if a payment row carried more than the amount applied to its invoice. Probe: +100.00 on settled INV-013843 gives 2,065.90 against the own balance 2,165.90. Base `managed_payment` records "amount_usd: Amount applied", and the excess "stays on the agreement as a credit balance", so that row is not a state the charter produces.

### regressions
- Mechanical sweep is clean on all 8: B9, replaced_by, policy_source, XF-26.
- Every task value, all-baseline and per-factor substitution recomputes unchanged and equals the r6 `tasks/*.json`:
  - task 0: 140.00 / 124.82 / 4,686.16 / 15,656.52.
  - task 1: 308.55 / 362.50 / 8.71 / 95.44.
- No other policy result moved.

## closing_checklist (revision_6)
- Both tasks PASS on all four relationships. Gold equals the independent recomputation.
- Gates: 7/7 rc=0.
- Every RED across revisions 1–5 is closed.
- Open observations only: O-3, O-4, O-5, O-6, O-7, the frontline first-nine allowance, and the upgrade first-term phase-in ordering.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

## charter_global_frozen (revision_7)
- Entry gate: the worklog's last line is exactly `REWORK round 7: gates 7/7 green`.
- Executed `/tmp/erl0069_coord/snapshot.sh managed_services_agreements 7` @ 2026-10-18T11:32:25. All 7 gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Hashes:
  - r7/0.view.json 07b83edd…3f41 and r7/1.view.json 7aa441e3…598d. Both are identical to r4–r6, so the worlds are unchanged.
  - managed.extended.yaml aea970a2703356046b2e0c2a28aa7c3bd5e728753fea18779cf2dbc489749890 (changed)
  - task_tools.py 819877d3…7010 (unchanged)
- Read in full: `audits/render_source/managed_services_agreements/render_r1.md` (renderer findings 1–6), then the "round 7 claims".
- Not blind; all values recomputed.
- Auditor's note on the earlier rounds:
  - Findings 2–6 are XF-C16 members (out-of-scope restatement incomplete) that revisions 1–6 missed. I checked that each `replaced_by` was scoped, but did not check that its out-of-scope tail carried every in-force element of the retired clause.
  - Finding 1 is a rule-vs-compute mismatch at small inputs that revision_4/5 recorded only as the "first-nine allowance" observation.
  - Both checks were run exhaustively this round.

### closure of renderer findings 1–6
- **1: closed.** Top tier: per-user fee count = min(min(F3, billed), 9), and further seats = max(treated − 9, 0).
  - I built an independent rule implementation and ran a differential test against compute: rates 38.5 / 89 / 124 / 236 × billed 4–29 × F3 0–34. 0 mismatches, covering tiers 1–3 and the case F3 ≥ 10 > billed.
  - Renderer case (billed 8, F3 12, rate 40.00): 92.00 before credits.
- **2–6: closed.** Each out-of-scope `replaced_by` tail now restates its retired clause in full:
  - renewal: rounding and "in which case the lower rate applies";
  - tier change: "or none if there is no such term";
  - registration: request type, target tier, computed effective date;
  - monthly fee: "invoiced in advance on monthly_invoice_day of that month";
  - exit: "invoiced on the date the notice takes effect on the agreement".

### class sweeps (all members listed now)
- **replaced_by tails (XF-C16), all 9 overwrites.** Word-level diff of every retired clause against its `replaced_by`. The only words missing are inflection or connective variants ("falls"→"falling", "equals"/"each"/"it"/"registers"/"applies" recast). No in-force element is dropped in renewal, monthly fee, reinstatement, exit, after-hours, onsite, late fee, tier change or registration. **No remaining member.**
- **rule-vs-compute at small or edge inputs, all 8 policies.** Checked every min/max cap, negative-term guard, divisor, absent-record branch and count-equality test:
  - frontline (differential, above);
  - volume and growth graduated divisors (≥ 25 / ≥ 40 / ≥ the mid seat);
  - exit months (floor 0) and absent request (0);
  - retention days for absent holdings (−1 → 0);
  - after-hours absent ticket (0) and frequency 0/1;
  - onsite visits 0/1;
  - reinstatement no payment (9999);
  - late-fee band continuity;
  - upgrade tier-3 cap;
  - CSP / F3 active-with-0 licenses (same outcome as no subscription).
  - **One member found: C-11 below.**
- Mechanical sweep is clean: B9, replaced_by, XF-26.

### findings (revision_7, charter)
**C-11 SOURCE-POLICY RED (rule ≠ compute at an edge count; present since revision_1).** `managed_ext_signed_exit_fee.exit_billing_basis_rule`:
- Rule: "when three monthly fees were posted in that window and the covered seats exceed the floor, the basis is the average of those three monthly fees; when fewer than three were posted …; otherwise the basis is seat_rate_usd times the floor seats".
- Compute: `basis_rule = 2 if recent_fee_count >= 3 …`, basis `recent_fee_sum / 3`.
- The 3-month window ending today can hold four monthly fees. The extended current-month fee policy posts a late current-month fee on the day it is posted, as task 0 itself does on 2026-10-08. A month-M fee posted on a day-of-month after today's lies inside the window: MONTHS(07-09, 10-08) = 2.
- Probe, the task-0 world with the July fee posted 2026-07-09 instead of 07-01:

| reading | count | basis | result |
| --- | --- | --- | --- |
| compute | 4 → tier 2 | 18,282.51 / 3 = 6,094.17, the sum of four fees over three | 20,704.94 |
| rule | 4 is neither "three" nor "fewer than three", so the "otherwise" tier applies | seat_rate × floor | 16,963.04 |

- A reader computing a plain "average" of the window's fees gets a third value.
- No effect on task 0's world: exactly 3 fees.

## closing_checklist (revision_7)
- Both tasks PASS. Gold equals the independent recomputation (unchanged since revision_4) in every write, expected value, baseline and per-factor substitution.
- Gates: 7/7 rc=0.
- Renderer findings 1–6 are closed.
- Not closable: C-11.

VERDICT revision_7: task0=PASS task1=PASS charter=C-11

## revision_8

## charter_global_frozen (revision_8)
- Entry gate: the worklog's last line is exactly `REWORK round 8: gates 7/7 green`.
- Executed `/tmp/erl0069_coord/snapshot.sh managed_services_agreements 8` @ 2026-10-18T11:51:27. All 7 gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Hashes:
  - r8/0.view.json 07b83edd…3f41 and r8/1.view.json 7aa441e3…598d. Both are identical to r4–r7, so the worlds are unchanged.
  - managed.extended.yaml 1a19b120e61f8a8832ba366180ff6e4199a899f22f29c190b978c779fdccb1cb (changed)
  - task_tools.py 819877d3…7010 (unchanged)
- The "round 8 claims" were read. Not blind; all values recomputed.

### C-11 closure
- Rule: "when three or more monthly fees were posted in that window and the covered seats exceed the floor, the basis is the average of the monthly fees posted in that window, their sum divided by their number; when fewer than three …; otherwise …".
- Compute: `basis_rule = 2 if recent_fee_count >= 3 …`, basis `recent_fee_sum / recent_fee_count`. The ladder text is the same. The divisor is ≥ 3 whenever it is used.
- Probe (task-0 world, July fee posted 2026-07-09): count 4, sum 18,282.51.
  - compute 15,528.71
  - independent rule reading (the average of four, × 0.50 × 9 × 0.755) 15,528.71
  - Equal.
- Two fees (skip-fee world) → the fewer-than-three tier, 19,507.49.
- XF-23: the average-of-window tier versus rate × covered seats and rate × floor seats still adds a distinct input. Pass.
- **C-11: closed.**

### regressions
- Mechanical sweep is clean on all 8: B9, replaced_by, policy_source, XF-26.
- Count-tier words re-checked against their operators in all 8 policies (renewal, reinstatement, exit, after-hours, onsite, late fee, upgrade): no mismatch.
- Every value, all-baseline and per-factor substitution recomputes unchanged and equals the r8 `tasks/*.json`:
  - task 0: 140.00 / 124.82 / 4,686.16 / 15,656.52.
  - task 1: 308.55 / 362.50 / 8.71 / 95.44.

## closing_checklist (revision_8)
- Both tasks PASS on all four relationships.
- Gates: 7/7 rc=0.
- Every RED across revisions 1–7, including renderer findings 1–6 and C-11, is closed.
- Open observations only: O-3, O-4, O-5, O-6, O-7, and the upgrade first-term phase-in ordering.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN

## revision_9

## charter_global_frozen (revision_9)
- Entry gate: the worklog's last line is exactly `REWORK round 9: gates 7/7 green`.
- Executed `/tmp/erl0069_coord/snapshot.sh managed_services_agreements 9` @ 2026-10-18T17:48:47. All 7 gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Hashes:
  - r9/0.view.json 2c778540cbfe58bdd3032018089c661a23c910fbb443d2587fea23b3b7bf67c3
  - r9/1.view.json f23ee3e1aa23a4e4790f6a26b60bd4ce4f5a75201485c951428826a5e6369fce
  - managed.extended.yaml 1a19b120…cb1cb and task_tools.py 819877d3…7010, both **unchanged** (seed-only round confirmed). The charter-global sections of revision_8 carry forward by reference.
- Read, as directed:
  - `audits/policy_kb/managed_services_agreements/_difficulty.md` revision_2 (S1–S5);
  - the "round 9 claims";
  - the published owning-product docs: `docs/licensing` (administration fee invoicing / amount / schedule / coverage share / volume / commitment-term / Continuum-bundle / security-baseline upkeep / part-month / standing rules; whole-subscription cancellation, cancellation refund, prompt-cancellation basis, order-reversal, seat-change reversal, license-change fee, Continuum deprovisioning);
  - blueprint `security.yaml` (`security_ir_hours_ledger`, variant IR and identity-threat-detection parameters);
  - `backup.yaml` (ordering, entry gate, monthly fee).
- Not blind (values known); all values recomputed.

### r8 → r9 seed diff
Only the rows below changed; the managed rows, `frozen_time` and scenarios are identical.
- Task 0:
  - security_ir_ledger +2 (forfeit 10.00 for contract year 2025-09-01; grant 10.00 for 2026-09-01).
  - licensing_billing +2 admin fees (76.80 Premium, 14.00 F3, posted 2026-10-01 for 2026-09), with the matching `balance_due_usd`.
  - Refund 68fa7332 44.80 → 48.00.
  - The 3.20 payment a6b4ed36 removed.
- Task 1:
  - backup_device_changes +2 workstations (CDA-WS-PRINC01, CDA-WS-CAD02, 2024-06-15).
  - protected_count 1 → 3.
  - 55 backup fee and payment amounts 75.05 → 96.91; balance 96.91.

### exhaustive check of every re-seeded row against its owning product's published rules
| item | check | result |
| --- | --- | --- |
| S2 IR ledger | MDR Advanced `ir_hours_included_annual` 10, `ir_rollover_pct` 0. "At activation and on each anniversary … granted …; at a contract year's end unused hours up to rollover% … the rest are forfeited." The ledger now runs grant 2024 / forfeit 2024 / grant 2025 / forfeit 2025 / grant 2026, the same pattern for every year; balance 10.00. | **closed** |
| S3 Continuum Backup Plus | Entry gate `min_protected_items` 3, met by 1 server + 2 workstations at order. Onboarding max(95 × 1, 250) = 250 (per contracted server). Fee = 75.05 × max(1, ceil(1 × 80 %)) + 10.93 × 2 = 96.91, devices counted at the end of the previous month (effective 2024-06-15, so July 2024 onward). Storage overage 0. All 27 paid; the October fee is open, so the balance is 96.91. | **closed** |
| S4 admin fees 2026-09 | Coverage is read on the posting day, 2026-10-01; ClearPath is suspended then, so "any other agreement — no reduction". Plan fee 1.50. Volume: Premium 48 licenses → ×90 %; F3 8 → none. Term: both P1Y, 365 days → none. Continuum protects no M365 users → no bundle. Upkeep: both plans are baseline-marked and MDR Advanced has identity threat detection → +0.25. Part-month: neither subscription is new or suspended. Premium (1.50 × 0.9 + 0.25) × 48 = 76.80; F3 (1.50 + 0.25) × 8 = 14.00. Earlier months correctly carry no fee: ClearPath was active on every earlier posting day, including 2026-09-01, before the 09-14 suspension. | **closed** |
| S5 cancelled F3 refund | Whole-subscription cancellation, P1M. Window opened 2026-06-10, cancelled 2026-06-12 (≤ 3 days), so prompt case A: 9.60 × 5 = 48.00, within the 48.00 cycle charge. The refund is credited to the cycle's own invoice INV-018165. No deductions: ClearPath Standard was active and covers M365 administration, so no order-reversal, seat-change or license-change charge; Continuum has no M365 users, so no deprovisioning; no admin fee was billed. Ledger: charge 48.00, refund 48.00, net 0 = balance. | **closed** |

- Not in this round's list: S1, the base lifecycle text about reinstatement. It sits in the verbatim base copy of `blueprint/products/managed.yaml`, so this difficulty cannot change it. I carry it as a blueprint-level observation, not a RED of this charter.
- No managed factor reads any re-seeded field: fee and exit read license_qty, status, term_end and variant; the late fee reads status. Scored values cannot move.

### moved values and proof text
- Every task value, all-baseline and per-factor substitution recomputes unchanged and equals the r9 `tasks/*.json`:
  - task 0: 140.00 / 124.82 / 4,686.16 / 15,656.52.
  - task 1: 308.55 / 362.50 / 8.71 / 95.44.
- Proof-text sweep of both task JSONs finds no stale 44.80, 3.20, "protected_count 1" or 75.05-as-fee. The only hit is the correct "75.05 + 2 x 10.93 = 96.91" in task 1's revision-9 note.

## closing_checklist (revision_9)
- Both tasks PASS.
- Gates: 7/7 rc=0.
- Charter and tools unchanged.
- KB-audit source items S2–S5 are closed.
- No new defect and no regression.

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN
