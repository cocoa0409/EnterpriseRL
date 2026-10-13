# Policy-task audit — community_rules_and_site_care_charges / charter-global

## charter_global_frozen

- Frozen: 2026-10-09T00:18Z (round 1), written before any task's GT was revealed; nothing in this section derives from a task JSON.
- Auditor: independent policy-task auditor (did not author the bundle).
- Inputs and their sha256 (re-verified against HASHES.txt before reading):
  - `tasks/community_rules_and_site_care_charges/rules.extended.yaml` 4b5ae608f1478d2f40e876c04aa7d0819a15138be0b10513613d6d634d047b18
  - `tasks/community_rules_and_site_care_charges/task_tools.py` 334a09d97b2a6e87d2b9a8aa3a6308a92e0d0cdc059b0d6dc52643b6634278cd
  - `blueprint/products/rules.yaml`, `blueprint/products/lease.yaml` (variant names, `lease_payment_return`, restriction), `blueprint/share_tools.py`, `blueprint/db_schema.json`, the blueprint `difficulties:` entry.
  - DSL semantics read from `skills/erl-task-instantiate/scripts/check_compute.py` (`MONTHS`, `DAYS`, `_within`, `LATEST`, `CFIELD`, `XCOUNT`, `RND`).
- Permitted: charter, tool module, blueprint, the masked views (`frozen_time`, `user_scenario`, `initial_state`).
- Masked until all M derivations are frozen: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`.
- Entry conditions (Step 0): gate snapshot supplied (`.audit_views/policy_task/community_rules_and_site_care_charges/GATES.txt`, eight gates rc=0; traceability deferred to render); masked views supplied with hashes (view hashes match). Entry complete.
- Base-copy check: every top-level key of `products/rules.yaml` (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies) compares equal to the extended file's copy; the only extra key is `extended_policies`. Base copy verbatim.

### policy_conflict_scan

Six extended policies: `rules_ext_vehicle_permit_fee` (agent, `post_vehicle_permit_fee_c6960799`), `rules_ext_pet_registration_fee` (agent, `post_pet_registration_fee_a0279ba6`), `rules_ext_past_due_payment` (user, `pay_site_care_past_due_0b8b512f`), `rules_ext_self_help_charge` (agent, `post_self_help_charge_892a63af`), `rules_ext_repeat_violation_charge` (agent, `post_repeat_violation_charge_7b5daab9`), `rules_ext_reinstatement_payment` (user, `pay_plan_reinstatement_3e360d67`).

- Subjects: the four agent policies each own one ledger event type, disjoint. The two user policies share subject `rules_payment` but have distinct triggers: past-due "A resident who asks to pay the past-due part of the rules and site-care statement"; reinstatement "A resident whose plan services are suspended pays the reinstatement payment". **Overlap**: neither rule excludes the other's case — a suspended resident who asks to pay "the past-due part" meets both triggers, and the two compute different amounts (window-limited past-due vs whole balance with advances). Recorded as observation O-1 (consequence only on a world with a suspended record whose customer asks for the past-due part; see task files).
- Time anchors: vehicle fee dated the plan fee due day of the billed month; pet fee the registration date (first year) or January 1; self-help the cure work date; repeat charge the notice date; payments `ctx.now()`. Every factor window is anchored on "the handling date". No two policies anchor the same quantity differently.
- Terminal states: each write adds one ledger row and moves `rules_balance`. Reinstatement rule says "plan services resume on the day it is received"; neither payment tool changes `rules_site_plans.status` (function bodies: `ctx.update(... rules_balance=balance)` only). Base lifecycle marks that transition `by: system`. Observation O-2.
- Cross-category reads: every policy reads only the lease holding/ledger (`CFIELD('lease', ...)`, `XCOUNT('lease','lease_ledger', ...)`), all reachable through `find_lease_holdings` / `find_lease_ledger`. `CFIELD` takes the first lease of the customer; a relocating customer with two leases (allowed by `rules_agg_multi_holding`) would make the read ambiguous — no task world has two leases (observation O-3).
- Scope partition implied by the prerequisite graph: {past_due -> vehicle, pet} and {reinstatement -> self_help, repeat; repeat -> self_help}. Two disjoint trees covering all six policies; with M=2 this is the only partition into two trees. Exclusivity/completeness of the tasks' declared `charter_scope` is checked after reveal (task files).

### rule_compute_equivalence

Swept every compute binding of the six policies against `compute_basis` and back against the `rule` sentences.

- vehicle: allowance ladder, permits floor at zero, community rate ladder, further-permit pricing (single: `rate + (n-1)*rate*2`; multi: `rate + (n-1)*ceil(rate*1.5)` — matches "that further-permit price rounded up to the next whole dollar"), parking-notice surcharge per permit, autopay+tenure courtesy, "added together first, the courtesy then taken once from that sum ... rounded half up". Two-way equivalent.
- pet: household rate (pets >= max_pets x section), conduct count (12 m), sanitation (fertilization / mowing-only x plan fee within 1 m), history credit (count of all pet fees, no window — matches "already on the plan record's statement"), incident recency (days from latest pets notice), subtotal floor 0, tenure courtesy (half floor / 0.75 ceil / as is), final half-up. Equivalent.
- past-due: statement balance (five charge types less payments and waivers), standard/long windows sum charge types only, window ladder, floor 0, carry-over, registration carry, plan-fee advance, "subtracted first ... never less than zero ... advance then added". Equivalent. (`compute_basis.charges_dated_long_window` quotes the ladder sentence — present in rule.)
- self-help: notice = latest violation notice, work date = latest `cured_by_community` outcome, visit rate by class, lot factor (lawn/snow x lot class), market factor, overgrowth (days deadline->work: >14 two visits; 4..14 1.5 visits ceil; else one), edging, contractor cost half-up, admin recurrence, admin courtesy, result. Equivalent. `compute_basis.scaled_visit_cost` quotes only the lot sentence though the binding also multiplies by the market factor (the market sentence is quoted on `contract_market_factor`); no invented basis (observation O-4).
- repeat: class/sequence of latest notice, schedule 2 -> second, >=3 -> third_plus, 1 -> 0, permitted communities (Saguaro Vista, Bluebonnet Ridge, Cedar Hollow — equals base `repeat_charges_permitted`), class weight, cure-cost count (12 m), lapse (deadline -> latest cure outcome), recurrence (2 m / 4 m counts of same class), `weighted_repeat_sum` zero when not permitted / sequence 1, tenure cap, courtesy, half-up. Equivalent to the extended rule — but see O-5 for the inherited base sentence on withdrawn notices.
- reinstatement: balance, lapse advance (months since latest plan fee), returned advance (returns or certified-funds), self-help deferral (3 m; full / half floor / none), repeat deferral (3 m; 1.0/0.25/0), tolerance, result. Equivalent. `compute_basis.plan_fee_advance_amount` quotes only the lapse sentence although the binding adds `returned_advance_months` (returned sentence quoted on its own binding) — observation O-4.
- Rounding: rules say "rounded half up to the cent"; `RND` is Python `round(float(x), 2)` (binary float, half-even at exact ties). No value of either task's derivation has a third decimal, so no consequence (observation O-6).
- Every factor's ladder tiers appear as rule sentences and as branches of the `decides` binding; no tier lives only in compute.

### action_binding_and_uuids

- `(target_tool, computes)`: six distinct pairs, each claimed by exactly one policy.
- Docstrings: none names another tool, a sequence position or an ordering word; the only ordering-like token is "once" in each Returns block ("balance ... once the charge is on it"), describing the same call's own effect. No added confirmation/review step.
- No tool validates eligibility, ownership, timing or a prerequisite: every body does `find` plan -> `create` ledger row -> `update rules_balance` -> return receipt; no branch refuses or hints.
- uuid8s: c6960799, a0279ba6, 0b8b512f, 892a63af, 7b5daab9, 3e360d67 — pairwise distinct, no shared prefix/suffix, no sequence pattern. Pass.

### prerequisite_graph

- `prerequisite` filled on all six (`[]` on vehicle, pet, self-help).
- Edges: past_due -> vehicle (value_input, gate `statement_balance`); past_due -> pet (value_input, gate `registration_carry`); repeat -> self_help (value_input, gate `cure_cost_addon`); reinstatement -> self_help (value_input, `reinstatement_balance`); reinstatement -> repeat (value_input, `reinstatement_balance`). All targets are extended ids of this file, none self, none base. Acyclic (self_help and vehicle/pet are sinks).
- Every `policy_source` is verbatim in its own policy's `rule` (string containment checked mechanically on whitespace-normalised text).
- `form: state` on all five, no `fallback_reason` — consistent.
- `condition` restates each sentence at the same strength (closed sets named by kind: "every month in which ...", "every registered pet in every registration year", "each community cure", "every repeat notice in a community permitting repeat charges"; the reinstatement->repeat condition adds "with its outcome recorded", which is the repeat rule's own assessment trigger, not a strengthening).
- `resolved_by` equals the depended-on policy's `target_tool` in all five; each named gate is a real binding of the dependent's compute and is moved by the resolving write (statement sums, pet-fee window sum, self-help count, reinstatement sums).
- No authoring-viewpoint phrasing in the `prerequisite` text.

### prerequisite_sentences

Four-point test per edge:

1. past_due -> vehicle: "The past-due amount is worked out only after the statement carries a vehicle permit fee for every month in which the site's registered vehicles exceeded its permit-free allowance." Connective "only after"; waited-on state = statement carries a permit fee per over-allowance month (record-visible on `rules_ledger`); no tool/id/snake token; scope "every month". Exactly one write of the difficulty creates a `rules_vehicle_permit_fee` row: `post_vehicle_permit_fee_c6960799` (the vehicle policy's rule: "The monthly vehicle permit fee ... is charged for each month in which the site carries more registered vehicles than its permit-free allowance"). Single reading. Note: the set of months is bounded only by the statement history the reader sees — see O-7.
2. past_due -> pet: "The past-due amount is not worked out until the statement carries a registration-year fee for every registered pet in every registration year it has been registered." "not ... until"; state on `rules_ledger`; one writer `post_pet_registration_fee_a0279ba6` (pet rule: "A registration-year fee is charged for each registered pet for each calendar registration year"). Single reading, subject to O-7 (first registration year not on any record).
3. repeat -> self_help: "The repeat-violation charge on a notice is fixed only once each community cure on the plan record has its self-help charge posted." "only once"; state = each `cured_by_community` outcome has a `rules_self_help_charge` row; one writer `post_self_help_charge_892a63af` (self-help rule: "A self-help charge is posted for a violation notice the community cured itself"). Single reading.
4. reinstatement -> self_help: "A reinstatement payment is quoted only after every violation notice that the community cured itself carries its self-help charge on the statement." Same writer; single reading.
5. reinstatement -> repeat: "A reinstatement payment is not quoted until every repeat notice in a community permitting repeat charges carries its repeat-violation charge on the statement." One writer `post_repeat_violation_charge_7b5daab9`. Single reading.

- No depended-on rule restates the sentence (vehicle, pet, self-help rules carry no payment language; the repeat rule does not mention reinstatement).
- No rule carries a second wording of a dependency, a tool name or another policy id.
- Cross-problem orders stated in rules without a declared edge: none. The repeat rule's "assessed once the repeat notice has its outcome recorded" and the self-help rule's dependence on a recorded cure outcome refer to base events (`rules_cure_confirmation`) that no extended policy writes; they are eligibility timing, not undeclared edges.
- Base sentences stating cross-problem order: `rules_service_suspension_terms` "Plan services resume on the day every past-due plan fee is paid" (overwritten by reinstatement); none grounds an edge.

### override_declarations

Sentence by sentence against each `base_policy_refs` entry:

- vehicle vs `rules_vehicle_terms`: s1 "up to vehicles_included ... without a fee" — overwritten (declared); "no more than max_vehicles in all" and registration/licensing — inherited and followed. s2 (fee per vehicle beyond vehicles_included) — overwritten (declared). s3 (RV/boat) — not touched. vs `rules_violation_process`: read only (notice class counts); no conflict.
- pet vs `rules_pet_terms`: s1 (registration window, max_pets, weight) inherited; s2 (state gate on registrations) n/a to the fee; s3 fee clause overwritten (declared) while its dating and "never prorated/refunded" clauses are restated verbatim in the extended rule; s4 assistance animals inherited (no assistance animal in either world). vs `rules_violation_process`, `rules_plan_terms`: read only.
- past-due vs `rules_charge_billing`: s1 "due charge_due_days calendar days after posting" overwritten (declared); "applied to the oldest charge first" restated in the rule; appeal/waiver sentences n/a. vs `rules_agg_charge_attribution`: "a payment is applied only to the record whose statement it names" restated.
- self-help vs `rules_self_help_terms`: s1 (class list, resident responsibility) inherited; s2-s3 (after deadline, counting) inherited; s4 charge formula overwritten (declared); s5 (withdrawn / resident-cured never charged) inherited. vs `rules_violation_process` (responsibility under the plan; suspended -> resident) inherited.
- repeat vs `rules_repeat_violation_terms`: s1 (permitted community, second-or-later after a cured/charged earlier notice) inherited; s2 schedule overwritten (declared); s3 "No repeat charge is posted for a notice withdrawn as the community's responsibility, and withdrawn notices are not counted." — inherited, **but the extended recurrence addition counts "the notices of the same rule class served within recent calendar months" and its compute (`class_notices_fast_window`, `class_notices_slow_window`) filters no outcome**, so a withdrawn notice inside the 2-/4-month window is counted by compute and excluded by the inherited base sentence. Not declared. Finding F-3 (observation: no world in this bundle places a withdrawn notice inside those windows — see task 1). s4 n/a.
- reinstatement vs `rules_service_suspension_terms`: s1 (suspension threshold, "while suspended, no plan fee is charged") inherited — the plan-fee advances are prepayments, not charges; s2 resume condition overwritten (declared); s3 n/a. vs `rules_charge_billing` / `rules_agg_charge_attribution`: oldest-first and record attribution inherited; reinstatement counts every charge regardless of due date, which follows from the overwritten resume condition.
- No anonymous intermediate, 0/1 multiplier or dropped base branch found beyond F-3; the repeat `weighted_repeat_sum ... if permitted_schedule_charge > 0 else 0` zeroes the additions only where base itself posts no repeat charge (sequence 1 / non-permitting community), consistent with base s1.

### factor_ladders

Per policy (P = parameter, M = method; MS = multi-source across distinct records; XD = cross_difficulty):

| policy | factors | P | M | MS | XD |
| --- | --- | --- | --- | --- | --- |
| vehicle | household_allowance (P), community_permit_rate (P), further_permit_pricing (M), parking_notice_surcharge (P), autopay_tenure_courtesy (P) | 4 | 1 | further_permit_pricing (permits from `rules_site_plans` x section from lease) | lease x4 |
| pet | household_pet_rate (P), pet_conduct_surcharge (P), lawn_crew_sanitation (P), registration_history_credit (P), pet_incident_recency (P), registration_tenure_courtesy (M) | 5 | 1 | household_pet_rate (plan pets x lease section); lawn_crew_sanitation (variant param x plan-fee rows); registration_tenure_courtesy (lease move-in x lease_ledger) | lease x2 |
| past-due | past_due_window (M), carryover_allowance (P), registration_fee_carry (P), returned_payment_advance (P) | 3 | 1 | past_due_window tier 2 (lease tenure x lease_ledger); registration_fee_carry (plan pets x lease tenure) | lease x3 (registration_fee_carry reads lease tenure but is labelled `cross_difficulty: null` — O-8) |
| self-help | lot_size_scaling (P), contract_market_scaling (P), overgrowth_billing (M), edging_addition (P), administration_fee_recurrence (P), administration_fee_courtesy (P) | 5 | 1 | lot_size_scaling (notice class x lease lot); edging_addition (variant param x plan-fee rows); administration_fee_courtesy (lease x lease_ledger) | lease x3 |
| repeat | rule_class_weighting (P), cure_cost_addition (P), cure_lapse_addition (P), class_recurrence_addition (P), tenure_cap (P), repeat_charge_tenure_courtesy (M) | 5 | 1 | repeat_charge_tenure_courtesy (lease x lease_ledger) | lease x2 |
| reinstatement | lapse_advance (P), returned_payment_reinstatement_advance (P), upkeep_deferral (M), repeat_charge_deferral (P), balance_tolerance (P) | 4 | 1 | returned advance (lease_ledger OR lease restriction); upkeep_deferral (lease x lease_ledger) | lease x4 |

- Counts 4-6 per policy, >=2 P and >=1 M on paper; every `decides` is an input binding (none is `result`); binding sets disjoint within each policy.
- Every ladder has three stated tiers; every fall-through equals the policy `baseline` for that input (vehicles_included; extra_vehicle_permit_fee_monthly; permits x rate; 0; 0 / pet_registration_fee_annual; 0; 0; 0; 0; subtotal / standard window; 0; 0; 0 / 1; 1; one visit; 0; plan's self_help_admin_fee; 0 / 1; 0; 0; 0; uncapped; capped sum / 0; 0; 0; 0; 0). No two tiers of one ladder share a value or method.
- Each `baseline.rule` is a subset of its `rule` sentences and yields a definite number on the records (vehicle: (vehicles - vehicles_included)+ x 15.00; pet: 25.00; past-due: balance less charges in the 1-month window; self-help: visit rate + plan admin fee; repeat: schedule charge; reinstatement: balance).
- Method labels: every M factor varies a multiplier together with a rounding step (pet/repeat courtesy: half floor / 0.75 ceil / identity; overgrowth: x2 / x1.5 ceil / x1; upkeep_deferral: full / half floor / none; past_due_window: no hold-back / 2-month / 1-month window). The rounding-direction change and the no-hold-back tier are accepted as algorithm changes; past_due_window tiers 2 vs 3 differ only by a window length and `repeat_charge_deferral` (P: 1.0/0.25/0) is the same shape as `upkeep_deferral` (M) minus the floor — label boundary recorded as observation O-9.
- **F-1 (SOURCE-FACTOR RED, charter-global): `further_permit_pricing` has a tier no lawful record can reach.** Its second tier is "two or more permits are charged and the home on the site is multi-section". On a multi-section site the allowance ladder gives `vehicles_included + 1` (>= large_household_adults adults) or `vehicles_included`; base gives `vehicles_included: 2` and `max_vehicles: 3` on all six variants and base `rules_vehicle_terms` (inherited) says "no more than max_vehicles in all". So permits on a multi-section site are at most 3 - 2 = 1, and the tier's condition is unsatisfiable for any record that obeys the inherited cap. The ladder therefore has two live tiers, below the three-tier floor; it is also the vehicle computation's only `method` factor, so on striking it the vehicle computation has 0 qualifying method factors. Bears on task 0 (vehicle computation).
- F-2 (observation): `household_allowance` tier 2 (>= 3 adults, multi-section, allowance 3) can never produce a posted fee for a lawful record (<= 3 vehicles), so it decides only whether a fee is due at all, never the amount of a scored write.
- Business realism of tier conditions/outcomes: no tier condition was found that holds for every customer reaching its write by definition; `edging_addition` tier 1 ("plan includes trimming but no plan fee in the last month") is close to that for lawn cures on trimming plans (a lawn cure is chargeable on a mowing plan only while services are suspended, i.e. after plan fees stop), but a plan fee can still fall inside the 1-month window when suspension starts just after a due day, so the tier is not universal (observation O-10).

### findings

- **F-1 SOURCE-FACTOR RED** — symptom: the vehicle computation's only method factor has an unreachable tier. Root cause: tier condition multi-section + >=2 permits contradicts base `vehicles_included: 2`, `max_vehicles: 3` and the extended allowance ladder. Evidence: `rules.extended.yaml` vehicle `factors[further_permit_pricing].ladder[1]`; base variants `vehicles_included: 2`, `max_vehicles: 3`; base `rules_vehicle_terms` "no more than max_vehicles in all". Consequence: ladder with two live tiers; vehicle computation left without a qualifying method factor. Affected: `rules_ext_vehicle_permit_fee` factors/rule sentence "When two or more permits are charged ... on a multi-section home site ...". Bears on: task 0.
- F-2 observation (household_allowance tier 2 never scores). Task 0.
- F-3 observation — undeclared divergence between inherited base "withdrawn notices are not counted" and the extended recurrence count; consequence not demonstrable in this bundle. Task 1 file confirms.
- O-1 observation — past-due / reinstatement trigger overlap for a suspended resident. Tasks 0 and 1 judge their own worlds.
- O-2 observation — payment tools do not effect the "plan services resume" transition.
- O-3 observation — `CFIELD('lease', ...)` first-lease read for a two-lease customer.
- O-4 observation — two `compute_basis` quotations cite only one of the two sentences their binding implements.
- O-5 = F-3.
- O-6 observation — `RND` vs "half up".
- O-7 observation — the past-due prerequisite sentences quantify over "every month" / "every registration year it has been registered", which the records bound only through the statement history shown; task 0 demonstrates what this costs there.
- O-8 observation — `registration_fee_carry` labelled `cross_difficulty: null` while reading lease tenure.
- O-9 observation — method/parameter label boundary.
- O-10 observation — edging tier 1 near-universal for trimming plans.

## closing_checklist

Written after both reveals (2026-10-09T09:22Z+); placed below the pre-reveal charter-global section, which was not edited.

- Per-task files: `0.md`, `1.md` correspond one-to-one with tasks 0 and 1; `_difficulty.md` alongside; round 1, no older revision.
- Coverage and exclusivity: task 0 `charter_scope` = {vehicle, pet, past_due} with their three tools; task 1 = {self_help, repeat, reinstatement} with their three tools. Pairwise disjoint, jointly complete over the six extended policies; matches the partition derived pre-reveal from the prerequisite graph. uuid8s independent (§ action_binding_and_uuids).
- Trees: task 0 — 2 prerequisite problems, 2 value_input edges, user root; task 1 — 2 prerequisite problems, 3 value_input edges, user root; the difficulty-wide graph is acyclic.
- Factors: every declared factor bears weight against an honest baseline in both worlds, and each baseline alone gives a definite number different from gold (figures in the task files) — **but** the factors relationship fails: F-1 (charter-global unreachable tier in `further_permit_pricing`, demonstrated in task 0), T0-1 (task 0 seed stamp equal to the scored permit fee) and T1-1 (task 1 seed stamp equal to the scored contractor cost).
- Gates: not re-run by the auditor (Step 0: auditor cites the coordinator's snapshot; all eight rc=0).

Difficulty result: **does not pass the source-layer audit.** Task 0 SOURCE-FACTOR RED; task 1 SOURCE-FACTOR RED. Policy self-consistency, problem tree and unique solution PASS in both tasks; observations listed in each file.

## revision_2

### charter_global_frozen (revision 2)

- Frozen: 2026-10-09 (round 2), written before any round-2 task JSON was opened; built from the charter, tool module and blueprint only.
- Inputs: `rules.extended.yaml` sha256 3d51da5110b7e812e1c5cefa0c65cec09156d266b12bbdead3ae15692e64f33a (**changed** from 4b5ae608…) -> every charter-global section is re-derived below; `task_tools.py` 334a09d97b2a6e87d2b9a8aa3a6308a92e0d0cdc059b0d6dc52643b6634278cd (unchanged) -> `action_binding_and_uuids` carried forward by reference to round 1 on that hash. Gate snapshot: GATES.txt, eight gates rc=0 (traceability deferred). Views re-hashed and match the brief (0: af161449…, 1: 5aba73e1…).
- Round-1 sections above are left untouched.
- Base copy: still equal key-for-key to `products/rules.yaml`; only `extended_policies` added.

### What changed in the charter (found by re-reading every extended policy, not from the reworker's list)

- vehicle: `further_permit_pricing` re-stated — params `single_section_further_multiplier`/`multi_section_further_multiplier` replaced by `further_permit_multiplier: 2` and `double_driveway_share: 0.5`; rule sentence now "The permits are priced by how the site holds the extra vehicles: when two or more permits are charged, the first permit is charged the permit rate and each further permit further_permit_multiplier times the permit rate; when exactly one permit is charged on a multi-section home site, whose double-width driveway holds the extra vehicle on the site, that permit is charged double_driveway_share of the permit rate, rounded up to the next whole dollar; otherwise each permit is charged the permit rate."; compute and ladder updated to match.
- pet: `history_credit_long_count` 8 -> 6, `history_credit_mid_count` 4 -> 3 (sentences unchanged, they name the params).
- past-due: trigger sentence now "A resident whose plan record is enrolled and who asks to pay the past-due part …"; `registration_fee_carry.cross_difficulty` now `lease`.
- self-help: new sentence "The scaled visit cost is the contract visit rate times the lot-size scale and times the contract market scale." quoted as `compute_basis.scaled_visit_cost`.
- repeat: recurrence addition re-stated — "A recurrence addition is made by the cure outcomes recorded on the plan record as cured by the resident or cured by the community within recent calendar months ending on the handling date, the notice's own outcome included and a withdrawn notice never counted: …"; compute bindings `resolved_outcomes_fast_window` / `resolved_outcomes_slow_window` count `rules_cure_confirmation` rows with `cure_outcome` in {cured_by_resident, cured_by_community}; factor renamed `cure_recurrence_addition`; `inputs.history` updated.
- reinstatement: resume clause (rule and `overwrite.replaced_by`) now "… the community's system resumes plan services on the day it is received …"; new sentence "The plan-fee advance is the plan fee in force times the lapse advance months and the returned-payment advance months added together." quoted as `compute_basis.plan_fee_advance_amount`.
- Unchanged: prerequisite fields and sentences of all six policies, targets, `(target_tool, computes)` pairs, all other ladders and baselines.

### policy_conflict_scan (revision 2)

- O-1 closed: the past-due trigger now requires an enrolled record and the reinstatement trigger a suspended one; the two user policies are exclusive on `rules_site_plans.status`.
- O-2 closed as an observation: the rule now attributes the resumption to "the community's system", consistent with the base lifecycle `by: system`; the payment tool leaving `status` unchanged no longer contradicts a desk action.
- O-3 unchanged (first-lease `CFIELD` read; no two-lease world).
- Scope partition implied by the unchanged prerequisite graph: same two disjoint trees covering all six policies.

### rule_compute_equivalence (revision 2)

- Mechanical check: every `compute_basis` quotation of all six policies is a verbatim substring of its own `rule` (whitespace-normalised) — 0 misses.
- vehicle `permit_charge`: `(rate + (n-1)*rate*2) if n >= 2 else (ceil(rate*0.5) if n == 1 and multi_section else n*rate)` — matches the new sentence in both directions.
- repeat recurrence: compute counts cured_by_resident + cured_by_community outcomes in the 2-/4-month windows, which is exactly "cure outcomes … cured by the resident or cured by the community …, a withdrawn notice never counted"; the rule no longer limits the count to the notice's class and compute does not either.
- O-4 closed: the self-help scaled-visit and reinstatement plan-fee-advance bindings now each quote a sentence that states the whole binding.
- O-6 unchanged (`RND` vs half-up; checked again on the round-2 figures below — none has a third decimal).

### prerequisite_graph and prerequisite_sentences (revision 2)

Unchanged fields and sentences (five state-form value_input edges; each `policy_source` verbatim in its own rule; one writer per waited-on state; no depended-on rule restates a sentence; no undeclared cross-problem order). The new sentences added this round (past-due trigger, self-help scaled-cost, repeat recurrence, reinstatement advance and resume clause) state no cross-problem order. Round-1 conclusions stand.

### override_declarations (revision 2)

- F-3 closed: base `rules_repeat_violation_terms` s3 "withdrawn notices are not counted" is now honoured by the recurrence count (withdrawn outcomes excluded by rule and compute). No other base sentence is touched differently from round 1.
- reinstatement `overwrite.replaced_by` equals the revised rule sentence verbatim; vehicle overwrites unchanged and still cover the re-stated pricing (the base fee sentence is superseded wholesale).
- No new undeclared override found in the changed sentences: the past-due "enrolled" scope narrows the policy's own trigger and contradicts no base sentence.

### factor_ladders (revision 2)

- F-1 closed: `further_permit_pricing` tiers — (1) two or more permits, reachable by a one-adult single-section household with 3 vehicles (allowance 1 -> 2 permits); (2) exactly one permit on a multi-section site, reachable by an ordinary multi-section household with 3 vehicles (allowance 2); (3) otherwise (one permit on single-section, or none). All three reachable under `max_vehicles 3`; outcomes distinct (escalating formula / half rate rounded up to the dollar / flat rate); method label honest (tier 1 is a different formula, tier 2 adds a rounding step); fall-through = baseline `permits_due * permit_rate`. Tier 2 is multi-source (plan record permits x lease section).
- `cure_recurrence_addition`: three disjoint tiers on two windows, fall-through 0 = baseline; condition (recent resolved violations) is one the line of business weighs for a repeat-violation charge; not universal (the 2-/4-month windows need two resolved outcomes close together).
- Counts: vehicle 4 P + 1 M (5); pet 5 P + 1 M; past-due 3 P + 1 M; self-help 5 P + 1 M; repeat 5 P + 1 M; reinstatement 4 P + 1 M. All within 4-6 with >= 2 P and >= 1 M; every policy now has a factor that survives the three-tier test as its method.
- O-8 closed (`registration_fee_carry` now labelled lease). F-2, O-9, O-10 unchanged and remain observations.

### findings (revision 2, charter-global)

- F-1: **closed** (no live-tier shortfall remains).
- F-3 / O-5: closed.
- O-1, O-2, O-4, O-8: closed.
- F-2, O-3, O-6, O-9, O-10: unchanged observations.
- New charter-global defects: none found.

### closing_checklist (revision 2)

Written after both round-2 reveals (2026-10-09T10:25Z); the revision-2 charter-global sections above were frozen before them and are not edited.

- Per-task files `0.md`, `1.md` each carry `## revision_2` with a frozen derivation and a comparison section ending in PASS; round-1 text preserved above in every file.
- Coverage and exclusivity: task 0 `charter_scope` {vehicle, pet, past_due} + their tools; task 1 {self_help, repeat, reinstatement} + their tools; pairwise disjoint, jointly complete; uuid8s independent (tool module unchanged).
- Trees: task 0 — 2 prerequisite problems, 2 value_input edges, user root; task 1 — 2 prerequisite problems, 3 value_input edges, user root; whole-difficulty graph acyclic.
- Factors: every computation declares a self-sufficient baseline and 4-6 factors (>= 2 P, 1 M), every ladder three reachable tiers stated in its rule with distinct outcomes; every factor bears weight on its task's world against an honest baseline; every baseline alone gives a definite number different from gold; each task has multi-source and cross-difficulty factors with seeded lease rows; no seeded stamp equals a scored value (round-1 T0-1, T1-1 closed).
- Round-1 RED closure: F-1/T0-2 closed, T0-1 closed, T1-1 closed. Observations claimed changed (F-3/O-5, T0-3, T0-4/O-7, T0-5, T0-6/T1-4, T1-2/O-2, T1-3, O-1, O-4, O-8) verified closed in the artifacts; F-2, O-3, O-6, O-9, O-10 unchanged and remain observations; new observations T0-7, T0-8 only.
- Gates: coordinator's round-2 snapshot, eight gates rc=0 (traceability deferred to render); not re-run by the auditor.

Difficulty result (revision 2): **passes the source-layer audit** — task 0 PASS, task 1 PASS.
