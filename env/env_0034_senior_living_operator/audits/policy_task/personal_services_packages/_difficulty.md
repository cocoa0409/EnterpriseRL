# Policy-task audit — personal_services_packages / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (round 1), not the instantiating agent.
- Freeze time: 2026-10-05T09:04Z (wall clock), written before any task GT was revealed.
- Inputs and hashes (read from the masked view directory `env/env_0034_senior_living_operator/audits/_views/policy_task/personal_services_packages/`, hashes re-computed and matching `MANIFEST.sha256.txt`):
  - `services.extended.yaml` 85691583a97db40283a234339c0acd6698a310ec87533f3ce9768e9a68e995e9
  - `task_tools.py` 94951f4a98172802e533f6d721a8b705aca9a73c4d337d3c6ec5a63a4dfb94b0
  - `blueprint/products/services.yaml` 60310eb167f63ac9e0e72137796eecfb21cb7ed3a0439b3f45426895c405043a
- Also read: `blueprint/blueprint.yaml` (difficulty entry), `blueprint/share_tools.py`, `blueprint/products/entrance.yaml` (contract_type per variant only).
- Masked and unread while this section was written: `tasks/personal_services_packages/tasks/*.json` (all of evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), the difficulty worklog, any earlier audit.
- Entry conditions (Step 0): the brief carries the gate snapshot (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred to render), the masked views and their hashes. Complete; cited, not re-run.

Base copy: lines 1-1287 of `services.extended.yaml` are byte-identical to `blueprint/products/services.yaml` (`diff` shows only the appended extended_policies banner). PASS.

### policy_conflict_scan

Four extended policies, four distinct writes:

| policy | trigger | subject | target_tool (owner) | computes |
| --- | --- | --- | --- | --- |
| services_ext_short_visit_credit | state_due | services_credit | post_services_visit_credit_5ef485c2 (agent) | amount |
| services_ext_suspension_months | on_request | services_suspend | sign_services_suspension_89d6021d (user) | suspended_months |
| services_ext_missed_visit_hours | state_due | services_hours_draw | post_services_order_hours_8d682fe6 (agent) | hours |
| services_ext_package_fit | on_request | services_package_change_request | sign_services_package_change_2a41e92a (user) | target_variant_name |

- Overlapping subjects: none between extended policies. short_visit_credit (services_credit) shares the event with base services_disputes_and_corrections and services_cancellation_and_end (residency_end_proration); the extended policy is restricted to service_dispute credits on delivered-visit hourly charges, residency_end_proration is untouched. missed_visit_hours shares services_hours_draw with base services_hours_and_billing (delivered draws) and services_late_cancellation; it is restricted to late_cancellation / no_show draw bases.
- Triggers: two state_due desk corrections (credit, missed hours), two on_request signed requests. A state_due policy fires on any world where its state holds, so each task world must be checked for stray state_due obligations (done per task).
- Eligibility / time anchors: suspension notice (base, inherited), dispute window (base, inherited), package-change cutoff and commitment (base, inherited), active-status gates (base, inherited). No extended policy relaxes one.
- Cross-category reads: assisted (absence fields, status) by credit and suspension; entrance (status, contract_type) by credit and missed hours; independent (variant_name, occupancy_type, second_occupant_name) by package_fit. All reads are branches, none writes another category.
- Terminal states: credit lowers account_balance; hours draw lowers hours_available (or charge raises balance); suspension writes suspension_start/end dates; package change writes pending_variant_name/pending_change_date. No two policies write the same field.
- Scope partition: the natural pairing by prerequisite edges is {suspension_months <- short_visit_credit} and {package_fit <- missed_visit_hours}; these are disjoint and jointly cover the four extended policies. Whether the tasks claim exactly that is checked at reveal.

No conflict found.

### rule_compute_equivalence

services_ext_short_visit_credit
- visit_ref / charged_amount / visit_month: LATEST hourly charge with draw_basis service_delivered by posting_date <-> "corrections are made one charge at a time beginning with the most recently posted hourly charge for a delivered visit"; "carrying the billing month of the charge". Equivalent.
- booked_hours / delivered_minutes / visit_date / visit_service from the charge's own order <-> "those recorded on that charge's own service order". Equivalent.
- billed_minutes three branches <-> the "When the charge is re-rated ..." sentence. Equivalent.
- floor_hours / base_hours <-> "never counted below companion_visit_minimum_hours for a companion visit or below minimum_visit_hours". Equivalent.
- is_holiday hard-codes 2025-2027 dates; spot-checked: Memorial Day 2025-05-26 / 2026-05-25 / 2027-05-31, Labor Day 2025-09-01 / 2026-09-07 / 2027-09-06, Thanksgiving 2025-11-27 / 2026-11-26 / 2027-11-25 — correct for the named calendar. weekday_index anchors 2026-01-03 (a Saturday), %7 in {0,1} = Sat/Sun. Equivalent within 2025-2027.
- relief_factor <-> the illness relief sentence (0..3 days short, >3..7 long, else 1). Equivalent.
- billable_hours rounded once after surcharge and multiplier <-> "rounded to two decimal places half up once the surcharge and any multiplier have been applied, and never earlier". Equivalent.
- covering_hours (expired month_end in visit month; else restored in visit month; else drawn) <-> covering sentence. Equivalent.
- overage_rate (occupied EFA lifecare / fee_for_service / else) <-> overage sentence. Equivalent.
- prior_disputes COUNT service_dispute credits within 12 months by posting_date; goodwill 25 / 10 / 0 <-> goodwill sentence. Equivalent.
- result = RND(MN(charged, charged - rerated + goodwill), 2) <-> "first worked out ... goodwill then added ... capped at the posted hourly charge and rounded". Equivalent.
- Sweep back: no rule sentence lacks an implementation except the eligibility halves already carried by base (dispute window) and the first-sentence selection condition "that the visit record shows was billed on more time than the visit supports", which compute does not test (it takes the latest delivered-visit hourly charge unconditionally). Observation O-1 below.

services_ext_suspension_months
- absence_extra, tenure_extra, standing_deduction, counted_prior, result: each bound to its own rule sentence verbatim. Equivalent.
- past_due: compute subtracts `P('monthly_package_fee')` (the package's tariff) where the rule subtracts "the package fee charged in advance for the current month" (a ledger row). Identical whenever the current month's fee has been charged at tariff; diverges in a month with no fee row (e.g. a suspended month or a package_change month). Observation O-2.
- prior_in_medical_absence: al_start <= prior_start and (no return or return >= prior_end) <-> "lay within a hospital or rehabilitation absence". Equivalent.
- first_suspended_month is fixed by the rule's first sentence and not by compute (not a computes field). Acceptable.

services_ext_missed_visit_hours
- band_hours (no_show; notice_days <= 1; else 0) <-> band sentence. Equivalent.
- basis_hours, pattern_multiplier (counts draws and hourly charges, both draw bases, 6 months), entrance_reduction, result order. Equivalent.
- rebook_multiplier: compute reads the LATEST same-service booking; the rule is existential ("where the resident booked the same service again no more than rebook_quick_days days after the missed visit date"). If an in-window rebooking is followed by a later booking of the same service, compute falls through to 1 while the rule gives 0.25 / 0.5. Observation O-3 (not demonstrable on either task world; checked per task).

services_ext_package_fit
- fee_months / change_months / current_fee_months / divisor <-> divisor sentence, except tier 2's causal clause "because the plan was suspended", which compute does not test (any shortfall of fees without a change takes tier 2, e.g. a plan that started inside the review months). Observation O-4 (checked per task).
- delivered_hours, late_hours, late_entries, counted_late, average_use, latest_month_hours, trend_adjustment, home_headroom, required_hours, result ladder (<=0 PAYG, <=4, <=8 or assisted -> Companion, <=12, <=20, else Concierge). Equivalent.
- Window convention: every history read uses `within_months=K('review_months')` / `within_months=1`, bound to "with a posting date within the review_months whole months before the request" and "within the last whole month before the request". The rule does not say whether a posting dated exactly review_months months before the request date is inside the window, nor whether "whole months" means rolling months back from the request date or whole calendar months. The charter elsewhere states its boundaries explicitly (dispute window "posting date being day 0 ... last day is in time"; suspension "ended fewer than window_months whole months"). Finding F-2 below; its consequence is task-specific (task 1).

### action_binding_and_uuids

- (target_tool, computes) pairs are unique: (post_services_visit_credit_5ef485c2, amount), (sign_services_suspension_89d6021d, suspended_months), (post_services_order_hours_8d682fe6, hours), (sign_services_package_change_2a41e92a, target_variant_name). PASS.
- Docstrings: none names another tool, none states a sequence position; no "before/after/first" ordering across actions ("the suspension takes hold on its start date", "any change already scheduled is replaced by this one" are intra-tool effects). The hours tool's event_type enum lists other ledger entry kinds by event name, not by tool. PASS.
- Function bodies: none validates a policy condition, refuses or hints; each writes what it is passed (`ctx.update` / `ctx.create`, balance and hours arithmetic only). PASS.
- uuid8: 89d6021d, 5ef485c2, 2a41e92a, 8d682fe6 — pairwise distinct, no common prefix or sequential pattern. PASS.

### prerequisite_graph

- prerequisite filled on all four: short_visit_credit `[]`, missed_visit_hours `[]`, suspension_months -> services_ext_short_visit_credit, package_fit -> services_ext_missed_visit_hours. Both problems are extended policy ids of this file, neither self, no base id. Graph: two disjoint edges, acyclic. PASS.
- policy_source verbatim in own rule: suspension edge sentence is rule line 4 of services_ext_suspension_months; package_fit edge sentence is rule line 4 of services_ext_package_fit. PASS.
- form `state` on both, no fallback_reason. PASS.
- kind value_input; gate `past_due` exists in suspension compute, gate `late_hours` exists in package_fit compute. PASS.
- resolved_by = depended-on target_tool on both. Effect: a credit row enters `ledger_reductions` -> past_due -> standing_deduction; a late/no-show hours row enters late_hours / late_entries -> counted_late. Genuine data paths. PASS.
- condition vs sentence: suspension condition "fewer delivered minutes than the time billed" vs sentence "billed on more time than was delivered" — same scope. package_fit condition names "no_show, or a resident cancellation received on the visit's day or the day before, within the review window" vs sentence "every service order recorded in the review months as a late cancellation or a no-show" — same scope once "late cancellation" is read through the extended band sentence (the base 24-hour definition is superseded). No authoring-viewpoint phrasing. PASS.

### prerequisite_sentences

Edge A (services_ext_suspension_months <- services_ext_short_visit_credit)
- Sentence: "The number of months a suspension may run is fixed only after every hourly charge on the plan that its visit record shows billed on more time than was delivered carries a service dispute credit referencing it."
- Four-point test: ordering connective "only after"; waited-on object is a record-visible state (hourly charge row carrying a services_credit service_dispute row whose source_entry_id is that charge); no tool, policy id, snake_case token or row id; strength matches the condition (all such charges, closed set by kind). PASS.
- Single writer: the only write in this difficulty creating a services_credit row is post_services_visit_credit_5ef485c2. PASS.
- Derivation a reader performs: sentence -> find unpaired over-billed hourly charges in the ledger/orders -> the policy whose rule says such a charge "is corrected ... posted as one service dispute credit referencing that hourly charge" is services_ext_short_visit_credit -> its write. One reading.
- Depended-on rule does not restate the sentence; no second wording elsewhere. PASS.

Edge B (services_ext_package_fit <- services_ext_missed_visit_hours)
- Sentence: "The package that fits the resident's use is not chosen until every service order recorded in the review months as a late cancellation or a no-show carries its hours entry for that cancellation on the plan's ledger."
- Four-point test: connective "not ... until"; state is record-visible (an hours draw / hourly charge row with that order_reference and draw basis); no tool name / id / snake_case; strength matches. PASS.
- Single writer: post_services_order_hours_8d682fe6 is the only write creating hours entries with a draw_basis. PASS.
- Derivation: sentence -> list cancellation rows in the review window, keep those whose band is non-zero, find which lack an hours row -> services_ext_missed_visit_hours "Hours owed for a service order that was cancelled late or missed are posted by the desk" -> its write. One reading. The window used to decide "in the review months" inherits the boundary question of F-2.
- No undeclared cross-problem order in any rule; no base sentence grounds an edge. PASS.

### override_declarations

services_ext_short_visit_credit (refs: services_cancellation_and_end, services_disputes_and_corrections, services_hours_and_billing)
- hours_and_billing s1 "Services listed ..." followed; s2 rounding/minimum superseded (declared); s3 surcharge sentence restated equivalently in the extended rule; s4 "drawn from services_msr_hours_available" superseded (declared) and "the rest are charged at hourly_rate_beyond_allotment" superseded (declared); a la carte sentence untouched; s6 one-draw dedup inherited.
- disputes_and_corrections s1 window inherited (desk-initiated within the same window, compatible); s2 counting inherited; s3 "credited as service_dispute referencing that charge" declared superseded although the extended rule re-states the same posting form ("posted as one service dispute credit referencing that hourly charge") — merged meaning unique; s4 cap and once-per-reason inherited and honoured by the cap; s5 "A draw or charge that matches the delivered minutes, the rounding and the surcharge rules is not an error" declared superseded.
- cancellation_and_end: no sentence touched (residency_end_proration unaffected).
- Observation O-5: three overwrite entries pair a superseded clause with a replaced_by text that governs a different quantity (s5 -> illness relief multiplier; s3 -> goodwill; missed_visit's no-show sentence -> order-of-operations sentence). The declarations still name every base sentence that the extended rule contradicts, so no undeclared override results.

services_ext_suspension_months (ref: services_suspension): quota sentence superseded (declared); absence, notice, counting, no-fee, resume sentences inherited and compatible. PASS.

services_ext_missed_visit_hours (refs: services_hours_and_billing, services_late_cancellation): late-cancellation definition and no-show draw superseded (declared); surcharge exclusion restated; hospital-absence exemption, cancel-once and one-draw dedup inherited. The base minimum_visit_hours / billing increment apply to "Delivered time of an hourly service" and do not govern missed-visit hours, so a fractional result below minimum_visit_hours is not an undeclared override. PASS.

services_ext_package_fit (ref: services_package_change, overwrite []): cutoff, single pending change, commitment, change-date effects, assisted ceiling, active-only — all restated or inherited; nothing contradicted. PASS.

No undeclared override found.

### factor_ladders

| policy | factor | label | decides | tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| short_visit_credit | delivered_time_billing | method | billed_minutes | 3 (floor / booked / ceil) | booked row vs completion row | - |
| | date_surcharge | parameter | surcharge_pct | 3 (holiday / weekend / 0) | no | - |
| | illness_relief | parameter | relief_factor | 3 (0.5 / 0.8 / 1) | AL absence + visit date | assisted |
| | covering_hours_rule | method | covering_hours | 3 (draw+expired / draw+restored / draw) | ledger rows | - |
| | entrance_overage_rate | parameter | overage_rate | 3 (rate-4 / rate-2 / rate) | one EFA record | entrance |
| | dispute_goodwill | parameter | goodwill | 3 (25 / 10 / 0) | ledger count | - |
| suspension_months | medical_absence_extension | parameter | absence_extra | 3 (2 / 1 / 0) | AL record only | assisted |
| | time_in_force_extension | parameter | tenure_extra | 3 (2 / 1 / 0) | plan only | - |
| | account_standing_deduction | parameter | standing_deduction | 3 (2 / 1 / 0) | ledger rows | - |
| | previous_suspension_count | method | counted_prior | 3 (none / half floor / full-or-none) | plan suspension + AL absence | assisted |
| missed_visit_hours | missed_visit_band | parameter | band_hours | 3 (no_show / late / 0) | cancel row | - |
| | missed_visit_basis | method | basis_hours | 3 (booked / band x share / band) | order + tier param | - |
| | cancellation_pattern | parameter | pattern_multiplier | 3 (1.25 / 0.5 / 1) | ledger count | - |
| | rebooking_relief | parameter | rebook_multiplier | 3 (0.25 / 0.5 / 1) | missed order + later booking | - |
| | entrance_hours_reduction | parameter | entrance_reduction | 3 (0.20 / 0.10 / 0) | one EFA record | entrance |
| package_fit | review_divisor | method | divisor | 3 (current-tier fee count / fee count / 3) | ledger rows | - |
| | missed_visit_use | parameter | counted_late | 3 (full / half / 0) | ledger rows | - |
| | home_headroom | parameter | home_headroom | 3 (1.5 / 1.0 / 0) | IL record only | independent |
| | use_trend | parameter | trend_adjustment | 3 (+2 / -1 / 0) | ledger rows | - |

- Counts per computation: credit 6 (4 parameter, 2 method); suspension 4 (3 parameter, 1 method as labelled); missed hours 5 (4 parameter, 1 method); package fit 4 (3 parameter, 1 method). Within 4-6.
- Every factor's `decides` is an input binding, not `result`; binding sets are pairwise disjoint within each policy; each ladder has three tiers, pairwise disjoint as stated, every tier stated in the rule (condition and value/method) and implemented in the `decides` binding; no tier lives only in compute; fall-through = baseline on all 19.
- No two tiers of one ladder select the same value or method.
- Cross-difficulty reads: assisted (credit, suspension), entrance (credit, missed hours), independent (package fit).
- Label honesty: see finding F-1 (previous_suspension_count).
- Realism: see observations O-6 (illness_relief) and O-7 (missed_visit_band fall-through lies outside the write's scope).

### findings

F-1 — SOURCE-FACTOR RED (bears on task 0, the task whose tree contains services_ext_suspension_months)
- Symptom: factor `previous_suspension_count` is labelled `method` but its three tiers substitute a share into one formula.
- Root cause: tiers "none of its months is counted", "half of its months are counted, rounded down to a whole month", "its months are counted in full if it ended fewer than window_months whole months before the request, and not at all if it ended earlier" are all `counted_prior = floor(prior_months x s)` with s = 0, 0.5, and 1 (or 0 past the window). Same input, same operation, a different number — the parameter shape the skill names ("tiers only substitute a different number into the same formula").
- Evidence: `services.extended.yaml` services_ext_suspension_months.factors[3] and compute `counted_prior: "0 if prior_in_medical_absence else (int(prior_months // 2) if (...) else (prior_months if months_since_prior_end < K('window_months') else 0))"`.
- Consequence: counted honestly, the suspension computation has 4 parameter factors and 0 method factors, below the "at least 1 method" bound for that computation.
- Affected: services_ext_suspension_months.factors (label), and every task whose tree includes the suspension computation.

F-2 — window boundary of the review months is not fixed by the rule (consequence demonstrated per task; bears on task 1)
- Symptom: "with a posting date within the review_months whole months before the request" and "within the last whole month before the request" leave open (a) whether a posting dated exactly review_months months before the request date is inside, and (b) rolling months vs whole calendar months.
- Evidence: services_ext_package_fit rule sentences 2 and 7; compute `within_months=K('review_months')`, `within_months=1`. Contrast the charter's explicit conventions elsewhere (dispute window day-0/inclusive; suspension "fewer than window_months whole months").
- Consequence: charter-global it is an under-specification only; whether it yields two answers depends on whether a scored row sits on the boundary — see `task_1.md`.

Observations (no consequence demonstrable on the charter alone)
- O-1 short_visit_credit compute does not test the "billed on more time than the visit supports" selection condition; it re-rates the latest delivered-visit hourly charge whatever it shows.
- O-2 suspension past_due subtracts the tariff fee, not the ledger's current-month fee row.
- O-3 missed_visit rebooking uses LATEST same-service booking where the rule is existential.
- O-4 package_fit divisor tier 2 does not test "because the plan was suspended".
- O-5 overwrite entries whose replaced_by governs a different quantity than the superseded clause (no undeclared override results).
- O-6 illness_relief: a hospital or rehabilitation absence that begins up to 7 days after a fully delivered visit scales that visit's billable hours by 0.5 / 0.8. Re-rating an over-billed visit is about what was delivered; a later admission does not change it. Contestable as compassionate relief, so recorded as a realism doubt rather than a red light.
- O-7 missed_visit_band: its fall-through (cancellation received on an earlier day -> 0 band hours) is an order for which the policy's own first sentence posts nothing, so no order that reaches this write can sit on the fall-through tier; the factor bears weight by the policy's scope rather than by the customer's records. The baseline rule "The standard band hours of a cancelled order are nothing" consequently zeroes the quantity this business (base no_show_hours_charged / late_cancel_hours_charged) publishes for a missed visit.

## closing_checklist

Written after both reveals (2026-10-05T09:07:29Z); nothing above this heading was changed after the reveal.

- Audit files: `_difficulty.md`, `task_0.md`, `task_1.md` — one per task, first revision, no older revision to preserve.
- Scope: task 0 claims {services_ext_suspension_months, services_ext_short_visit_credit} with tools {sign_services_suspension_89d6021d, post_services_visit_credit_5ef485c2}; task 1 claims {services_ext_package_fit, services_ext_missed_visit_hours} with tools {sign_services_package_change_2a41e92a, post_services_order_hours_8d682fe6}. Pairwise disjoint, jointly cover all four extended policies and all four task tools — matches the pre-reveal expectation in § policy_conflict_scan.
- Trees: each has 1 prerequisite problem, 1 value_input edge, an owner=user root write, no cycle; the difficulty graph is two disjoint edges, acyclic.
- Factors: 4-6 per computation as declared, every ladder 3 tiers stated in its rule; all 19 factors bear weight on their task's world under GT's reading; fall-back numbers definite and different from gold (task 0: 55.00 and 0; task 1: 0.00 and Essentials). Open: F-1 (suspension computation has no honest method factor).
- Unique solution: task 0 PASS (blind = GT); task 1 SOURCE-TASK RED (F-2 window boundary: Comfort vs Companion).
- Difficulty status: NOT CLOSED — task 0 SOURCE-FACTOR RED, task 1 SOURCE-TASK RED. The instantiation-stage gate re-run belongs to the close-out on the final form and is not performed in this round (gate snapshot of the brief is the one cited in § charter_global_frozen).

## revision_2

### charter_global_frozen (revision 2)

- Auditor: same independent auditor, round 2 re-audit. Written before either task's round-2 GT was read (reveal recorded in the task files).
- Inputs (masked views rebuilt by the coordinator, hashes re-computed and matching `MANIFEST.sha256.txt`):
  - `services.extended.yaml` 6102277bf8e0f54c74f5ff919e1fb7dd372d6e38cb0207f324e49cecc7c56f87 — CHANGED from round 1 (85691583…), so every charter-global section is re-derived below rather than carried forward.
  - `task_tools.py` 94951f4a98172802e533f6d721a8b705aca9a73c4d337d3c6ec5a63a4dfb94b0 — unchanged; § action_binding_and_uuids of round 1 is carried forward by reference on that hash (the four (target_tool, computes) pairs are also unchanged in the charter).
  - `task_0.view.json` 26690d98… unchanged; `task_1.view.json` 3ee065a9… changed.
- Base copy: lines 1-1287 still byte-identical to `blueprint/products/services.yaml` (diff empty). PASS.
- Gate snapshot (coordinator, after rework): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred. Cited, not re-run.
- contamination_disclosure (charter level): the auditor read the round-1 GT of both tasks (task 0: credit 87.50, 3 months; task 1: 0.27 h, Comfort) and the brief states that task 1's scored values changed. Round-2 derivations below are computed from the new charter and views; the round-1 GT is known and is disclosed, not concealed.

Changes found in the extended charter (read in full, compared with the round-1 text quoted in this file and the task files):
- short_visit_credit: illness_relief tiers now require "the visit ended short of its booked time" (compute `visit_cut_short`); new sentences "A charge whose re-rated charge is not below the posted hourly charge was not billed on more time than the visit supports and is credited nothing" (compute `result ... if rerated_charge < charged_amount else 0`) and "The dispute look-back is counted from each credit's posting date to the date of the correction, a whole month elapsing on the same day of each later month"; overwrite replaced_by for the illness sentence updated to match.
- suspension_months: new param recent_window_months 6; counting sentence rewritten ("only the months that ended fewer than window_months whole months before the request are counted ... a whole month elapsing on the same day of each later month"); past_due now subtracts "the package fee charged on the ledger in advance for the current month (nothing where no fee was charged for the current month)" (compute `current_fee_date` / `current_fee`); previous_suspension_count ladder now: left out / look-back shortened to recent_window_months / look-back window_months, compute `MX(0, MN(prior_months, W - months_since_prior_end))`.
- missed_visit_hours: band ladder now no_show / day-before (late_cancel_hours_charged x day_before_share 0.5) / same-day (late_cancel_hours_charged); new scope sentence "A cancellation received two or more calendar days before the visit owes no hours and is not posted"; baseline band is now late_cancel_hours_charged; repeat_multiplier 1.25 -> 1.2, rebook_week_multiplier 0.5 -> 0.6; rebooking rule now "read from the most recent booking of the same service"; pattern look-back counting sentence added.
- package_fit: new window sentence "a posting falls within them when fewer than review_months whole months have elapsed from its posting date to the request date ... a posting dated on the same day of the month review_months months before the request is outside and one dated the next day is inside; the last whole month before the request is counted the same way with one month"; divisor tier 2 now "as when the plan was suspended for a month" (illustrative, no longer causal).

### policy_conflict_scan (revision 2)
Same four policies, subjects, triggers, tools and terminal fields as round 1; no new overlap. The new missed-visit scope sentence (two or more days' notice owes nothing) agrees with base services_late_cancellation's free timely cancellation. No conflict.

### rule_compute_equivalence (revision 2)
- credit: `visit_cut_short` <-> "Where the visit ended short of its booked time"; `result` zero branch <-> "credited nothing"; prior_disputes window <-> new look-back sentence. Equivalent. Round-1 O-1 closed (selection condition now has both a rule sentence and an implementation).
- suspension: `current_fee` <-> ledger-fee sentence; equivalent on any world where the latest fee row is the current month's. Edge (observation O-8, new): compute takes the latest fee row posted fewer than one whole month before the request, not the row whose billing_period is the current month, so a fee posted mid-previous-month (e.g. a package_change fee dated the 15th) would be read as the current month's fee early the next month. Not reachable on task 0 (latest fee b0bd66a8 posted 2026-10-01, billing_period 2026-10). Round-1 O-2 closed on its own terms.
- suspension counted_prior <-> the rewritten three-method sentence: equivalent.
- missed hours: band, scope, rebooking ("most recent booking") equivalent; round-1 O-3 closed (rule now states LATEST).
- package fit: window sentence now fixes the `within_months` convention (strictly fewer than N whole months, same-day boundary outside); divisor tier 2 text now matches compute's count-only test; round-1 O-4 closed.
- No rule sentence without implementation, no compute binding without basis.

### action_binding_and_uuids (revision 2)
Carried forward from round 1 by hash (task_tools.py 94951f4a… unchanged; target_tool/computes pairs unchanged). PASS.

### prerequisite_graph and prerequisite_sentences (revision 2)
Both edges unchanged verbatim (policy_source, condition, form, gate, resolved_by). Gates past_due and late_hours still exist in compute. Edge B's waited-on set ("recorded in the review months as a late cancellation") now reads through the new band ladder (day-before and same-day cancellations owe hours; two or more days' notice owes none), which matches the edge's condition text. Edge B's "in the review months" now has a stated boundary. PASS for both.

### override_declarations (revision 2)
- credit: the replaced_by for "A draw or charge that matches ... is not an error" now carries the cut-short condition; no new base sentence contradicted. PASS.
- suspension: unchanged declaration (quota sentence). The rewritten counting reproduces the base's rolling-window idea for tier 3 and shortens it for tier 2; both are covered by the declared supersession. PASS.
- missed hours: replaced_by of the late-cancellation sentence updated to the new band ladder; the base 24-hour definition stays declared superseded. PASS.
- package fit: overwrite [] still holds; the window sentence adds a convention base never stated. PASS.
- O-5 (replaced_by texts governing a different quantity) unchanged, as the reworker states; remains an observation.

### factor_ladders (revision 2)
Factor set, labels and counts unchanged (credit 6: 4 parameter / 2 method; suspension 4: 3 / 1; missed hours 5: 4 / 1; package fit 4: 3 / 1). Changes:
- illness_relief: both non-fall-through tiers now conjoin a cut-short visit (booked row vs completion row) with an AL absence starting 0-3 / 4-7 days after — now a coherent "illness cut the visit short" relief. Round-1 O-6 closed.
- missed_visit_band: tiers 1.0 / 0.25 / 0.5 for Premier (no_show / day-before / same-day); fall-through (same-day cancellation) is inside the write's scope and equals the baseline late_cancel_hours_charged, which is the base charter's published late-cancellation hours. Round-1 O-7 closed. Observation O-9 (new): on the Concierge package late_cancel_hours_charged is 0.0, so the day-before and same-day tiers both select 0 there; on every other package they differ.
- previous_suspension_count: see F-1 status below.

### findings (revision 2)

F-1 — NOT closed (SOURCE-FACTOR RED persists in a new form; bears on task 0)
- Round-1 defect: tiers were one formula floor(prior_months x s) with s in {0, 0.5, 1}.
- Round-2 text: tier 1 "the suspension is left out of the count altogether"; tier 2 "the look-back shortens to recent_window_months: only its months that ended fewer than recent_window_months whole months before the request are counted"; tier 3 "its months that ended fewer than window_months whole months before the request are counted".
- Evidence: compute `counted_prior: "0 if prior_in_medical_absence else (MX(0, MN(prior_months, K('recent_window_months') - months_since_prior_end)) if (...) else MX(0, MN(prior_months, K('window_months') - months_since_prior_end)))"`. Tiers 2 and 3 are the same expression with a different window constant (6 vs 12); tier 1 is the same expression with any window not exceeding the elapsed months (W = 0 gives MX(0, MN(prior, -m)) = 0).
- Consequence: tiers 2 and 3 select the same method — "count the suspension's months that fall inside a look-back window" — differing only by a number (a threshold), which is the parameter shape; the ladder therefore has two tiers selecting one method, and counted honestly the suspension computation still has no `method` factor (3 parameter + 1 parameter-in-substance). The share has been renamed a look-back window; the defect stands under a new name.
- Affected: services_ext_suspension_months.factors[previous_suspension_count] and compute counted_prior.

F-2 — closed at charter level. The package-fit rule now states the window boundary in prose (strictly fewer than review_months whole months; the same-day posting is outside, the next day inside; same convention for the last whole month). Whether the task world still admits a second reading is checked in `task_1.md` revision_2.

Observations: O-1, O-2, O-3, O-4, O-6, O-7 closed (above); O-5 unchanged; O-8 and O-9 new (above), neither demonstrable on a task world.

### closing_checklist (revision 2)

Written after the round-2 reveals (2026-10-05T10:04:39Z); the revision_2 charter-global sections above were written before them.
- Audit files: `_difficulty.md`, `task_0.md`, `task_1.md`, each with the round-1 text untouched and a `revision_2` appended.
- Scope: task 0 {suspension_months, short_visit_credit}, task 1 {package_fit, missed_visit_hours}; tools as in round 1; disjoint and jointly complete — unchanged.
- Trees: each one prerequisite, one value_input edge, owner=user root, acyclic; edges unmet at the opening and load-bearing (task 0: 3 vs 2 months; task 1: Comfort vs Companion).
- Factors: all 19 bear weight on their task worlds against honest baselines; fall-backs definite and different from gold (task 0: 55.00 and 0; task 1: 0.50 and Essentials). Open: F-1 (suspension computation has no honest method factor).
- Unique solution: task 0 PASS, task 1 PASS (F-2 closed).
- Round-1 items: F-2 closed; O-1, O-2, O-3, O-4, O-6, O-7 closed; O-5 unchanged (observation); task-0 obs 3 and task-1 obs 2, 4, 5 closed; F-1 NOT closed. New observations O-8, O-9 (not demonstrable on either world).
- Difficulty status: NOT CLOSED — task 0 SOURCE-FACTOR RED (F-1). Gate re-run on the final form deferred to close-out.

## revision_3

### charter_global_frozen (revision 3)

- Round-3 re-audit by the same auditor; written before either task's round-3 GT was read.
- Inputs (rebuilt views, hashes re-computed and matching the manifest): `services.extended.yaml` b202a9e51957d7695879cf2df41c2a8c15b9b058a197f10ebf61e2ff1329c104 (CHANGED from 6102277b…, so the charter-global sections are re-derived); `task_tools.py` 94951f4a… (unchanged — action_binding_and_uuids carried forward by hash); `task_0.view.json` 26690d98… and `task_1.view.json` 3ee065a9… (both unchanged).
- Base copy lines 1-1287 still byte-identical to `blueprint/products/services.yaml`. PASS.
- Gate snapshot (coordinator, after round-3 rework): all green, traceability deferred. Cited.
- contamination_disclosure: the auditor has read the round-1 and round-2 GT of both tasks (task 0: 87.50 / 3; task 1 round 2: 0.34 h / Comfort). Disclosed; round-3 values are recomputed from the round-3 charter.

Changes found (the three other policies were checked against the round-2 text: params, the round-2 sentences and every compute line are as in round 2; the only edits are in services_ext_suspension_months):
- Factor previous_suspension_count removed; counted_prior is now a plain baseline binding `MX(0, MN(prior_months, K('window_months') - months_since_prior_end))` with its rule sentence "Of the plan's most recent recorded suspension, only the months that ended fewer than window_months whole months before the request are counted ..."; params recent_end_months / recent_window_months removed; the AL absence_start_date read removed.
- New method factor time_in_force_count (decides months_in_force): came from a Larkspur IL residency with a move-in date on record -> whole months since that move-in; otherwise with a recorded suspension -> whole months since the plan's effective date less the suspension's months; otherwise -> whole months since the effective date. New baseline sentence "The months counted toward time in force are, as the standard, the whole months since the plan's effective date." New cross-category read: assisted admission_source, independent move_in_date.
- time_in_force_extension now keyed on "the months counted toward time in force".
- Past-due wording: "less the package fee charged on the ledger on the first day of the current month (nothing where no fee was charged for the current month)" (O-8).

### policy_conflict_scan (revision 3)
No new subject, trigger, tool or terminal field. The new IL read is a branch read of another category, no write. No conflict.

### rule_compute_equivalence (revision 3)
- months_in_force / time_in_force_count: three branches <-> the three-method sentence; equivalent. tenure_extra <-> the rewritten extension sentence; equivalent.
- counted_prior <-> the baseline counting sentence; equivalent.
- current_fee: compute still takes the latest fee row posted fewer than one whole month before the request and does not test that it was posted on the first day of the month; the rule now says "charged on the ledger on the first day of the current month". Because package fees in this charter post on the first of a month (monthly cycle and package-change dates are both first-of-month), no world in this charter reaches a divergence; O-8 is retained as an observation in the narrower form "the day-of-month condition is stated but not tested".
- Observation O-10 (new in round 3): compute_basis.past_due still quotes "less the package fee charged on the ledger in advance for the current month", which is no longer a substring of the rule after the O-8 rewording. Same meaning on every reachable world; quote-trace defect only.
- Observation O-11 (present since round 2, missed by the round-2 audit): compute_basis.al_absence_reason and compute_basis.medical_absence of services_ext_short_visit_credit quote "Where the resident's assisted living residency records a hospital or rehabilitation absence", which stopped being a substring of the rule when round 2 prefixed "Where the visit ended short of its booked time and"; package_fit compute_basis.latest_month_hours joins two verbatim fragments with ";". No semantic divergence.
- Observation O-12 (new): time_in_force_extension lists `months_since_effective` among its bindings although its decided binding tenure_extra reads months_in_force; months_since_effective is an input of time_in_force_count's branches. Binding sets remain disjoint and substitution of either factor's baseline is unaffected.

### action_binding_and_uuids (revision 3)
Carried forward by hash. PASS.

### prerequisite_graph / prerequisite_sentences (revision 3)
Both edges unchanged verbatim; gate past_due still in compute. PASS.

### override_declarations (revision 3)
Suspension overwrite unchanged and still covers the rolling-12 quota sentence; the time-in-force method touches no base sentence (base services_suspension has no tenure clause). PASS.

### factor_ladders (revision 3)
- Suspension: medical_absence_extension (parameter, assisted), time_in_force_count (method, independent + assisted), time_in_force_extension (parameter), account_standing_deduction (parameter): 4 factors, 3 parameter, 1 method.
- time_in_force_count label: tier 1 measures from a different record's date (the earlier IL move-in), tier 2 subtracts a different quantity (the suspension's months), tier 3 is the plain count — the tiers change which records the quantity is computed from and how, not a constant substituted into one formula. Honest `method`. Tiers distinct; tier 1 and tier 2 are conjunctions over distinct records (AL admission_source + IL move-in; AL admission_source + plan suspension) — multi-source. Fall-through = baseline sentence. Realism: carrying years as a Larkspur IL resident into tenure, and excluding months on hold, are both treatments a senior living operator plausibly publishes.
- Other three policies: unchanged from revision 2.

### findings (revision 3)
- F-1 — CLOSED. The mislabelled factor is gone (no tier ladder remains on counted_prior), and its replacement time_in_force_count is an honest method factor; the suspension computation has 1 honest method factor. Consequence on task 0 checked in `task_0.md` revision_3.
- F-2 — remains closed (package_fit text unchanged since round 2).
- O-5 unchanged; O-8 narrowed (above); O-9 unchanged (Concierge late_cancel_hours_charged 0.0 — reworker answered, no change; still not reachable on either task world); O-10, O-11, O-12 new observations, none with a demonstrable consequence.

### closing_checklist (revision 3)

Written after the round-3 reveals (2026-10-05T10:28:55Z).
- Audit files `_difficulty.md`, `task_0.md`, `task_1.md` correspond one-to-one to the difficulty and its two tasks; revisions 1 and 2 untouched, revision_3 appended; every comparison section of revision 3 carries PASS.
- Coverage and scope: the four extended policies are covered; task 0 {services_ext_suspension_months, services_ext_short_visit_credit}, task 1 {services_ext_package_fit, services_ext_missed_visit_hours}; pairwise disjoint over whole trees; task tools closed over GT; uuid8s 89d6021d / 5ef485c2 / 2a41e92a / 8d682fe6 independent and unchanged.
- Trees: each has 1 prerequisite problem, 1 value_input edge (>= max(n-1,1)), an owner=user root write, no cycle; the difficulty-wide graph is two disjoint edges, acyclic.
- Factors: credit 6 (4 parameter / 2 method), suspension 4 (3 / 1), missed hours 5 (4 / 1), package fit 4 (3 / 1); every ladder 3 tiers stated in its rule, tiers distinct (O-9: Concierge-only coincidence, not reached), conditions and outcomes ones the business holds; each task has multi-source and cross-difficulty factors with seeded rows (task 0: assisted, independent, entrance; task 1: entrance, independent); every factor bears weight against an honest baseline; fall-backs definite and different from gold (task 0: 55.00 and 0; task 1: 0.50 and Essentials).
- Unique solution: task 0 and task 1 blind derivations equal GT.
- Instantiation-stage gates on the final form: coordinator's round-3 snapshot — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability deferred until the KB is published (cited, not re-run by the auditor).
- Open observations (no demonstrable consequence, not grounds for rework): O-5, O-8 (narrowed), O-9, O-10, O-11, O-12.
- Difficulty status: PASSES the source-layer audit (policy self-consistency, problem tree, factors, unique solution all PASS for both tasks), subject to the deferred traceability gate.

## revision_4

### charter_global_frozen (revision 4)

- Round-4 re-audit by the same auditor; this section and both task derivations below were written before reading the round-4 task JSONs. The two KB-audit directories the brief names (`audits/policy_kb/personal_services_packages/`, `audits/runtime_context/personal_services_packages/`) were also read only after this freeze; the item-by-item closure check of B1, B2, B3, E1, N1-N8 is appended further below.
- Inputs (hashes re-computed, matching the manifest): `services.extended.yaml` d73f83125dcd2005853f383b46076da1f8ca97fba7d86fb439f1de01843bfa34 (CHANGED — every charter-global section re-derived); `task_tools.py` 94951f4a… (unchanged — action_binding_and_uuids carried forward by hash); `task_0.view.json` 26690d98…, `task_1.view.json` 3ee065a9… (both unchanged).
- Base copy lines 1-1287 byte-identical to `blueprint/products/services.yaml`. PASS.
- Gate snapshot (coordinator, round 4): all green including TRACEABILITY OK (against the not-yet-re-rendered KB). Cited.
- contamination_disclosure: round-1..3 GT of both tasks known (task 0: 87.50 / 3; task 1: 0.34 / Comfort); the brief says task 0's scored value changed. Recomputed from the round-4 charter.

Changes found (all four policies read in full):
- short_visit_credit: the three overwrite entries against services_hours_and_billing are withdrawn; the remaining declarations are (a) base disputes "A draw or charge that matches the delivered minutes, the rounding and the surcharge rules is not an error." now replaced by a scope sentence "A charge re-rated under this rule is corrected on the re-rated figure even where it matches ... those rules stay in force for every first posting, and the re-rating rules here apply only to working out a correction" (also added to the rule), and (b) the goodwill entry (unchanged, O-5). Entrance tiers now name the plans: lifecare "(the LifeCare Declining Balance Plan or the LifeCare 90% Refundable Plan)", fee-for-service "(any LifeChoice plan)". compute unchanged.
- suspension_months: restructured. Result sentence and overwrite replaced_by now "one total: the package's max_suspension_months_per_12m, which is the starting allowance and not a ceiling, plus the months added for the plan's time in force, less the months counted for the plan's most recent recorded suspension; ... the floor being applied once to the final number". Time-in-force tiers (loyalty 48/24 -> +2/+1, from the effective date) moved into the baseline; time_in_force_extension is no longer a factor. New parameter factor previous_suspension_share (0 within a medical absence / older_suspension_share 0.5 where it ended >= older_suspension_months 3 whole months before / 1), applied to window_counted = MN(prior_months, window_months - months_since_prior_end) and rounded down. Absence months "added to the total", past-due months "deducted from the total". compute_basis.past_due now verbatim (O-10 fixed).
- missed_visit_hours: scope sentence extended "lateness is read in calendar days, so the package's late_cancel_notice_hours plays no part under this rule"; entrance tiers name the plans. compute unchanged.
- package_fit: first sentence adds "where the required hours exceed every allotment an independent living resident is fitted to the Personal Services Concierge Package" (compute's final else); last-whole-month window now stated inside the trend sentence. compute unchanged.

### policy_conflict_scan (revision 4)
No new subject, trigger, tool or terminal field. No conflict.

### rule_compute_equivalence (revision 4)
- Suspension: max_base, absence_extra, months_in_force (three methods), tenure_extra (baseline tiers applied to months_in_force), past_due, window_counted, prior_share, counted_prior = int(window_counted x share) <-> "taken at one of three shares ... at older_suspension_share, rounded down to a whole month", result with a single floor — all equivalent. Every compute_basis quote is a verbatim substring of the rule; every baseline sentence is in the rule.
- Credit: compute unchanged; equivalent. O-11 persists: compute_basis.al_absence_reason / medical_absence still quote "Where the resident's assisted living residency records a hospital or rehabilitation absence", not a substring of the rule (which reads "...and the resident's assisted living residency records..."). Quote-trace only.
- Missed hours, package fit: compute unchanged; the new Concierge sentence matches compute's final branch; latest_month_hours quote now a single verbatim fragment (O-11's package-fit half fixed).
- O-8: rule says "charged on the ledger on the first day of the current month", compute tests "latest fee posted < 1 whole month before"; unreachable divergence (fees post on the 1st). Retained as observation.
- O-12 withdrawn by construction (time_in_force_extension no longer exists; tenure tiers are a baseline binding).

### action_binding_and_uuids (revision 4)
Carried forward by hash. PASS.

### prerequisite_graph / prerequisite_sentences (revision 4)
Both edges verbatim unchanged; gate past_due still in suspension compute (now feeding standing_deduction inside "the total"); gate late_hours in package-fit compute. PASS.

### override_declarations (revision 4)
- Credit: with the three services_hours_and_billing entries withdrawn, the base rounding / "drawn from services_msr_hours_available" / "charged at hourly_rate_beyond_allotment" sentences are no longer superseded. The extended rule now confines its re-rating rules to "working out a correction" and keeps the base rules "in force for every first posting". The scored quantity (the credit amount) is not a first posting; base services_hours_and_billing governs draws and hourly charges, and the only base sentence that decided what counts as an error in a charge (disputes s5) is declared superseded by the scope sentence. Swept sentence by sentence: hours_and_billing s1-s6 now govern postings only and do not determine the credit; disputes s1, s2, s4 inherited and honoured; s3 middle clause declared (goodwill). No undeclared override. PASS.
- Suspension: the quota sentence remains declared superseded; its replaced_by now matches the rule's total sentence verbatim. PASS.
- Missed hours: unchanged declarations; the new "late_cancel_notice_hours plays no part" clause restates the already-declared supersession of the base 24-hour definition. PASS.
- Package fit: overwrite [] still holds. PASS.

### factor_ladders (revision 4)
- Credit 6 (4 parameter / 2 method), missed hours 5 (4 / 1), package fit 4 (3 / 1): unchanged.
- Suspension 4: medical_absence_extension (parameter, assisted), time_in_force_count (method, independent; tiers measure from another record's date, subtract the suspension's months, or plain count — honest method), account_standing_deduction (parameter), previous_suspension_share (parameter, assisted; values 0 / 0.5 / 1 distinct, honestly labelled a share — the shape round 1 objected to as a `method` is now declared as a `parameter`). 3 parameter, 1 method. Multi-source: time_in_force_count (AL admission_source + IL move-in; AL source + plan suspension), previous_suspension_share tier 1 (plan suspension + AL absence). Realism: halving an older suspension's months and ignoring a suspension taken during a hospital stay are plausible published treatments.
- Baseline self-sufficiency (suspension): baseline rule = first-month sentence + one-total sentence + tenure tiers from the effective date + window counting in full + whole-month convention -> a definite number on any world.

### findings (revision 4, charter-global)
- No new RED at charter level.
- Observations carried: O-5, O-8, O-9, O-11 (credit half only). Closed this round: O-10, O-12, O-11's package-fit half.

### kb_traced_items (revision 4, read after the freeze)

Source: `audits/policy_kb/personal_services_packages/task_0.md` and `task_1.md` (bijection verdicts, dependency_form, policy-side notes), read at 2026-10-05T11:35Z after the revision_4 derivations were on disk.

| item | what the KB audit traced to the source | round-4 source | status |
| --- | --- | --- | --- |
| B1 / N1 | suspension baseline.rule floored the partial `max - counted` while the rule floored only the total | baseline and rule both say "one total ... the floor being applied once to the final number of months and never to a part of it"; absence months "added to the total", past-due months "deducted from the total"; compute `MX(0, max + absence + tenure - deduction - counted)` | closed |
| B2 / E1 / N2 | baseline atom "The months counted toward time in force are, as the standard, ..." consumed only by a factor, its wording signalling a variant | "as the standard" gone from rule and baseline; tenure tiers ("Time in force adds ... where the whole months since the plan's effective date are ...") are now consumed by the baseline computation itself; time_in_force_extension replaced by previous_suspension_share | closed |
| B3 / N6 | package-fit baseline.rule carried "the last whole month ... counted the same way with one month", consumed only by use_trend | clause removed from baseline.rule; last-month window now stated inside the trend sentence | closed |
| N3 | max_suspension_months_per_12m description reads as a cap | base description cannot change (verbatim base copy); the rule and the declared replacement now say "the starting allowance and not a ceiling" | closed at the policy layer |
| N4 | credit overwrites retired services_hours_and_billing's draw/overage clauses for every delivered visit | the three hours_and_billing entries withdrawn; new scope sentence keeps those rules "in force for every first posting" and confines re-rating to a correction; declared against disputes s5. Sweep in § override_declarations (revision 4): no undeclared override | closed |
| N5 | contract type is a variant parameter, plan-to-type mapping only cross-corpus | lifecare tier names "the LifeCare Declining Balance Plan or the LifeCare 90% Refundable Plan", fee-for-service tier "any LifeChoice plan" (matches `products/entrance.yaml` contract_type of all six variants) in both credit and missed-hours rules | closed |
| N7 | fit rule silent above the largest allotment | sentence "where the required hours exceed every allotment an independent living resident is fitted to the Personal Services Concierge Package" (= compute's final branch) | closed |
| N8 | late_cancel_notice_hours description outlives the hour-based lateness rule | rule: "lateness is read in calendar days, so the package's late_cancel_notice_hours plays no part under this rule" (base description unchangeable) | closed at the policy layer |

Policy-layer criteria after the rework: factor counts 6 / 4 / 5 / 4 within bounds, each computation with >= 2 parameter and >= 1 method; baselines self-sufficient and every baseline sentence in its rule; trees and unique solutions re-derived per task (both PASS).

### closing_checklist (revision 4)

Written after the round-4 reveals (2026-10-05T11:35:29Z).
- Files: `_difficulty.md`, `task_0.md`, `task_1.md`; revisions 1-3 untouched, revision_4 appended; every revision-4 comparison carries PASS.
- Coverage/scope: four extended policies covered; task 0 {suspension_months, short_visit_credit}, task 1 {package_fit, missed_visit_hours}; disjoint, complete; tools closed over GT; uuid8s unchanged and independent.
- Trees: one prerequisite and one value_input edge each, owner=user root writes, acyclic difficulty graph; edges unmet at opening and load-bearing (task 0: 4 vs 3; task 1: Comfort vs Companion).
- Factors: credit 6 (4/2), suspension 4 (3/1), missed hours 5 (4/1), package fit 4 (3/1); ladders of three distinct tiers stated in their rules; multi-source and cross-difficulty factors per task with seeded rows (task 0: assisted, independent, entrance; task 1: entrance, independent); all 19 bear weight; fall-backs definite and different from gold (task 0: 55.00 and 1; task 1: 0.50 and Essentials).
- Unique solution: both blind derivations equal GT.
- Gates on the final form: coordinator's round-4 snapshot, all OK including TRACEABILITY OK (against the not-yet-re-rendered KB). Cited, not re-run.
- Open observations (no demonstrable consequence): O-5, O-8, O-9, O-11 (credit half: compute_basis.al_absence_reason / medical_absence quote "Where the resident's ..." not verbatim in the rule).
- Difficulty status: PASSES the source-layer audit.
