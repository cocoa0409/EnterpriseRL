# Policy-task audit — primary_care_assignment / charter-global

## charter_global_frozen

- Freeze time: 2026-09-24T17:05Z (written before any task's GT was revealed; nothing in this section is derived from a revealed GT field).
- Auditor: erl-task-policy-audit sub-agent (independent of the instantiating agent; round 1).
- Frozen inputs (sha256):
  - `tasks/primary_care_assignment/pcp.extended.yaml` 54cdea2438f183adaea98c7d66c27bbc74d4f860b09997485f439b0b9cbe9766 (matches the brief)
  - `tasks/primary_care_assignment/task_tools.py` 65d36829ec2c3662abfffedd54326b58e901ae6ed9b30ff0c4d33a77f90ff6bc (matches the brief)
  - `blueprint/products/pcp.yaml` 549a6e8d9468863cbf51b838525015ded0489ebf5ed85f5e65f01902b0ada555
  - `blueprint/db_schema.json` 122531ba911ae79a19800dc19f574b45a1b39fb5961d1acbb91463e0f49fc8f1
  - `blueprint/share_tools.py` a569fd6edf967b4f057313f1cb4d912f94c2c7bdf2c7ca2a119408ff54b40f75
  - `blueprint/blueprint.yaml` 9813a99607dd0254831d69f1b117dae5c02e9fca1cb8d55ca12a68d71249c70e
- Fields permitted: the four blueprint files above, the extended charter, `task_tools.py`, the compute-DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py::build_env` (the runtime meaning of SUM/COUNT/LATEST/XCOUNT/CFIELD/MONTHS used by the charter), and the coordinator's masked views (frozen_time, user_scenario, initial_state only).
- Fields masked and not read: every task JSON under `tasks/primary_care_assignment/tasks/`, `worklog.md` (difficulty and scenario level), `__pycache__`, `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, closure fields. No recursive search was run over `env/` or `tasks/`.
- Entry conditions (Step 0): gate snapshot supplied (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0; check_traceability deferred until KB publication); masked views supplied with hashes, re-hashed by the auditor and matching (0.json 3995e097…b376b, 1.json 43711a7f…a2b). Entry conditions met.

DSL semantics relied on (from `check_compute.py::build_env`): `SUM/COUNT/MAX/LATEST('pcp_events'|'pcp_visits', …)` are scoped to the single target holding (`pcp_assignment_id = HID`); `P(x)` is the parameter of the target holding's practice type; `X*` aggregates read the customer's rows of another category; `within_months=W` keeps a row when `0 <= MONTHS(date, NOW) < W`, where `MONTHS` counts whole months and subtracts one when the day-of-month of NOW is below that of the date (so the anniversary date W months back is excluded); `CFIELD` returns the first matching holding.

### policy_conflict_scan

Structured policy = the verbatim base section (lines 1–1428, byte-identical to `blueprint/products/pcp.yaml`; `diff` empty) + five extended policies, all with `base_policy_refs: [pcp_referrals]`, `overwrite: []`, `subject: [pcp_referral_issue]`, `computes: referral_visits`:

| Policy | target_tool (owner) | prerequisite |
| --- | --- | --- |
| pcp_ext_referral_carryover | carry_over_referral_de0684af (agent) | [] |
| pcp_ext_standing_referral | issue_standing_referral_d300bbad (agent) | carryover (value_input, state) |
| pcp_ext_continuity_of_care | elect_continuity_of_care_ec21b6d4 (user) | standing (value_input, state) |
| pcp_ext_specialist_referral | issue_specialist_referral_96d4855f (agent) | [] |
| pcp_ext_second_opinion | request_second_opinion_76735634 (user) | specialist_referral (value_input, state) |

Overlap scan (subject, trigger, eligibility, time anchors, action parameters, terminal states, cross-category read boundary):

- All five write a `pcp_referral_issue` row on the member's active assignment; the base eligibility `referral_from_active_pcp` ("A referral is issued only on an assignment in active status.") is inherited by all five and weakened by none (every rule names the active/current assignment).
- Row-level interaction: every tool except the standing one writes `referral_type="single"` (`task_tools.py` lines 53, 141, 183, 227). So a carried referral, a specialist referral, a continuity election and a second-opinion entry are all "single referrals the current assignment carries" to any later reader. Readers of that set: standing (`carried_specialist` = LATEST single, `carried_open_visits` = SUM single to that NPI) and second opinion (`treating_visits` = SUM single to the requesting provider). A continuity election or a second-opinion entry written before a standing referral would therefore become the "most recent single referral" and name the PCP or the second-opinion doctor as the standing specialist. No gold order in this charter's graph puts either user write before a standing write, so this is recorded as observation O-G8, not a conflict.
- Cross-category reads are declared per policy in `cross_category` and every `CFIELD/EXISTS/X*` in compute reads only a declared category and field (checked by hand against each `cross_category.reads` list; the auth read `requesting_provider_npi` and the ride read `destination_npi` are both declared).
- Base-vs-extended conflict on the continuity window: see finding **G-1** (SOURCE-POLICY RED).
- Scope exclusivity / completeness: the prerequisite graph has exactly two weakly connected components, {carryover → standing → continuity} and {specialist_referral → second_opinion}. With M=2 and each task's scope spanning its whole tree, the only exclusive and complete cover is one component per task. Confirmed against the masked personas only at the level "task 0 asks for continuity with a leaving PCP, task 1 asks for a second opinion"; the declared `charter_scope` is masked and is compared in the closing checklist, not here.
- Difficulty claim vs charter subject: the blueprint claims `event_types [pcp_assign, pcp_end, pcp_change_log, pcp_location_update]` for this difficulty, while every extended policy's subject is `pcp_referral_issue`, an event type no difficulty in `blueprint.yaml` claims. Recorded as observation **O-G6**.

### rule_compute_equivalence

Every `compute_basis` value was checked mechanically: every sentence of every basis quotation is a verbatim substring of that policy's `rule`, every compute binding has a basis entry, and every sentence of each `baseline.rule` is a verbatim substring of the `rule` (script output: no misses for all five policies). Sweep back sentence by sentence:

- **carryover**: windows (recent 3 / middle 6 / standard 12 months), filters (paid, specialist_visit, provider_npi = referred specialist), the age ladder, bridge, relationship count (referrals the earlier assignment issued to that specialist in 12 months, the carried referral included, as the rule says "the referrals the earlier assignment issued to the referred specialist"), travel legs (completed, outbound, destination NPI, appointment date in 6 months), order (floor at 0, add, then MN with ceiling) — all implemented. Gap: the rule's scope sentence says "A single referral that one of the member's earlier primary care assignments issued … is carried", but `carried_specialist/visits/issue_date` are `LATEST(... event_type='pcp_referral_issue')` with no `referral_type='single'` filter, matching only the second sentence "The referral carried is the most recent referral that the earlier assignment issued". The two sentences diverge when the earlier assignment's most recent referral is a standing one. Observation **O-G3** (world-dependent; checked in 0.md).
- **standing**: allowance tier, monitoring (event_type rx_fill = "paid" fill, formulary specialty, 3 months), post-hospital (12 months), travel (XMAX, no window, "on record"), lab (3 months), alignment (renewal_due → DAYS/validity; active and MONTHS<12 → MONTHS/12; else 1), order (sum → align → floor → cap → deduct, floor 0) — implemented. Rounding: `aligned_total: int(allowance_total * eligibility_share)` truncates the float product without the `RND(…, 6)` guard the specialist-referral policy uses; with share = m/12 a product that is exactly an integer in real arithmetic can land just below it in floating point (e.g. 24 * (7/12)). Observation **O-G11** (world-dependent; checked in 0.md).
- **continuity**: window ladder, rate ladder, `ceil(rate*window/90)` via `(x + 89)//90`, co-management, emergency follow-up, order (round up → minus reduction plus follow-up → floor 1 / ceiling) — implemented.
- **specialist_referral**: core ladder (≥2 paid specialist claims in 12 months; Elective Inpatient and Surgical request in submitted/pended_info/approved), review, travel, medication (specialty → 2, else preferred_brand/non_preferred → 1), emergency (6 months), alignment, floor via `int(RND(x,6))`, ceiling — implemented.
- **second_opinion**: requesting provider (CFIELD on the Elective Inpatient and Surgical authorization, first match, no status filter), review method ladder, imaging (lab_xray paid, 3 months), controlled fills (CII+CIII+CIV, rx_fill, 3 months), mobility (active ride benefit level), sum then ceiling — implemented. The rule says "for controlled pain medicine, counted as … fills of a Schedule II, III or IV controlled substance": the counting clause is explicit and the compute follows it; a Schedule IV fill that is not a pain medicine is a potential second reading, observation **O-G12** (world-dependent; checked in 1.md).

Every tier named in every `factors[].ladder` is a sentence of the rule and a branch of its `decides` binding, and every branch of each `decides` binding is a tier the rule states (checked factor by factor; see factor_ladders). No compute binding invents a basis; no rule sentence is left unimplemented except the eligibility phrases "still within its validity" (carryover) and "a member in active treatment" (continuity), which are act/refuse gates and not quantities.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: five distinct target tools, each claimed by exactly one policy; `computes` is `referral_visits` for all five but the pair is unique.
- uuid8 tails: de0684af, d300bbad, ec21b6d4, 96d4855f, 76735634 — no shared prefix, no sequential or adjacent values, no copy-with-changed-tail; consistent with independent generation.
- Docstrings: none states a position in a sequence or carries before/after/first/then as a sequencing word (grep: only line 110 "after the provider's network exit date", which describes when the elected visits fall, not the order of tool calls). Two docstrings point at share lookups in business words ("as shown by the PCP assignment lookup", "the earlier assignment's referral entry in the PCP history lookup") — observation **O-G7**; no other hidden tool is named.
- Function bodies: each tool computes nothing, checks no status, validity, eligibility or prerequisite, and writes exactly one `pcp_events` row with the passed values (lines 45–57, 86–100, 131–144, 173–187, 217–230). The tool layer never judges a prerequisite.
- Owners: carryover, standing, specialist referral = agent; continuity election and second opinion = user. Each tree's root is an `owner=user` tool.

### prerequisite_graph

- `prerequisite` present on all five policies (`[]` on carryover and specialist_referral).
- Edges: standing → carryover; continuity → standing; second_opinion → specialist_referral. Every `problem` is an extended policy id of this file, none is a base policy, none is self. Graph acyclic (two chains).
- `policy_source` verbatim in the blocked policy's own `rule`: True for all three (script check).
- `form: state` on all three; no `fallback_reason` present, as required.
- `gate` bindings exist in the blocked compute: `carried_open_visits` (standing), `comanagement_reduction` (continuity), `treating_visits` (second_opinion); `kind: value_input` matches a real binding in each.
- `resolved_by` equals the depended-on policy's `target_tool` in all three.
- `condition` strength vs sentence: standing edge — sentence "every single referral that an earlier assignment of the member issued and that is still within its validity is carried on the current assignment under its original referral number" ↔ condition "every pcp_referral_issue row (referral_type single) on an ended earlier assignment whose issue date is within that practice type's referral validity days … a row with the same referral_number exists on the active assignment" — same scope. Continuity edge — sentence conditional on "at least the frequent-use count of paid specialist-visit claims in the recent-use window" ↔ condition "at least four paid specialist_visit claims in the last six months" (K values 4 and 6) — same. Second-opinion edge — sentence "a single referral, dated on or after the assignment's effective date, to the specialist whose recommendation is being reviewed" ↔ condition names the requesting_provider_npi of the Elective Inpatient and Surgical request — this narrows "the specialist whose recommendation is being reviewed" to the surgical case, which the next rule sentence itself does ("Where the recommendation under review is a surgery, the specialist … is the requesting provider"); not a strengthening.
- `effect` statements are world assertions (e.g. "the carried single referral becomes the most recent single referral on the current assignment", "the continuity visits fall by one"); they are verified per task.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field.

### prerequisite_sentences

Four-point test per edge:

1. **standing ← carryover** — "The visits of a standing referral are fixed only after every single referral that an earlier assignment of the member issued and that is still within its validity is carried on the current assignment under its original referral number." Connective "only after" joins the standing result to the waited-on state; state form, named in record words (single referral, earlier assignment, validity, referral number) with no tool, performer or policy id; strength = condition. Unique resolving write: the only tool that puts an earlier referral's own referral number on the current assignment is `carry_over_referral` (the standing, specialist and second-opinion tools mint a new `RF-YYMM-NNNNN` number from the date and a hash; the continuity tool likewise). Derivation a reader performs: sentence → find every single referral on an ended assignment still within validity → check the current assignment for its number → the carryover rule ("A single referral that one of the member's earlier primary care assignments issued, and that is still within its validity, is carried onto the member's current active assignment under its original referral number") is the one policy whose write produces that state. Single reading. Caveat: the sentence requires *every* such referral to be carried, while the carryover rule fixes the visits only of "the most recent referral that the earlier assignment issued" — a world with two unexpired single referrals on the earlier assignment would leave the second without a defined carried value. Observation **O-G4** (world-dependent; checked in 0.md).
2. **continuity ← standing** — "For a member with at least the frequent-use count of paid specialist-visit claims in the recent-use window, the visits of a continuity-of-care referral are not fixed until the active assignment carries a standing referral." Connective "not … until"; state form ("the active assignment carries a standing referral"); no tool/id; conditional scope stated. Unique resolving write: only `issue_standing_referral` writes `referral_type="standing"`. The standing rule ("it is written on the member's active assignment where the practice type allows standing referrals") is found by the reader as the only policy producing a standing referral. Single reading. Caveat: for a member on a practice type whose `standing_referral_allowed` is false (Standard, Pediatric, OB/GYN, FQHC Home), the waited-on state can never be brought about, so the continuity visits can never be fixed for a frequent-use member on those practice types. Observation **O-G5** (not demonstrable on either world unless the task's practice type disallows standing; checked in 0.md).
3. **second_opinion ← specialist_referral** — "A second-opinion referral is recorded only after the current assignment carries a single referral, dated on or after the assignment's effective date, to the specialist whose recommendation is being reviewed." Connective "only after"; state form; no tool/id. Unique resolving write: a single referral dated on or after the current effective date to a named specialist can come from `issue_specialist_referral` (dated today). The carryover tool writes the original issue date, which precedes the current effective date whenever the earlier assignment ended before the current one began, so it cannot satisfy "dated on or after"; the continuity and second-opinion tools also write "single" rows dated today, but to the leaving PCP and to the member's chosen second-opinion doctor respectively, never to the specialist under review in a coherent reading. Single reading.

No blocked rule carries a second wording, a tool name or another policy id for its dependency; no depended-on rule restates the sentence. No rule states a cross-problem order that grounds no declared edge (swept all five rules and the base `pcp_referrals` / `pcp_provider_exit` rules; the base "A referral is issued only on an assignment in active status" is a state gate, not a cross-problem order).

### override_declarations

Base sentences of `pcp_referrals` (the only `base_policy_refs` entry of all five):

- B1 "Where referral_required_for_specialist is true, an in-network specialist visit needs a referral from the active PCP;" — followed by all five (each writes on the active assignment).
- B2 "a referral is valid for referral_validity_days from its issue date and covers up to referral_max_visits, or standing_referral_max_visits for a standing referral where standing referrals are allowed." — followed: carryover MN with the issuing practice type's `referral_max_visits`; standing MN with `standing_referral_max_visits` and restricted to practice types that allow it; continuity, specialist referral and second opinion MN with `referral_max_visits`; carryover keeps the original issue date (validity unchanged).
- B3 "Services listed in self_referral_services never need a referral, and a referral never replaces a prior authorization where one is required." — not touched by any extended policy.
- B4 "A referral is issued only on an assignment in active status." — followed by all five.
- B5 "A referral issued by a PCP whose assignment has since ended stays valid until its own expiry." — followed by carryover ("so that it keeps its own expiry").

`overwrite: []` is correct as against `pcp_referrals`. Anonymous intermediate / 0-1 multiplier / dropped branch: none found against `pcp_referrals` (the eligibility-alignment share is an extended-side quantity with no base counterpart; B2 only sets a ceiling).

**Undeclared override outside `base_policy_refs`**: `pcp_ext_continuity_of_care` governs the length of the continuity-of-care period after a provider's network exit, which base `pcp_provider_exit` fixes: "A member in active treatment may keep seeing the exiting provider for continuity_of_care_days after the exit date". The extended rule replaces that period with a ladder ("a member whose plan membership is in the Prairie Ridge ABD Care or Prairie Ridge Dual Complete category and who had at least the active-treatment count of visits … receives the extended continuity window [135 days]; a member who meets exactly one … the intermediate continuity window [105 days]; a member who meets neither receives the practice type's continuity-of-care days"). `pcp_provider_exit` is not cited in `base_policy_refs` and no `overwrite` names the sentence. See finding **G-1**; the consequence is demonstrated in 0.md.

### factor_ladders

Per policy (effect label; decides; tiers; outcomes distinct?; stated in rule; label honest?):

**pcp_ext_referral_carryover** (baseline: recorded − used in 12-month window, floor 0, ceiling of the issuing practice type)
- used_visit_window — labelled `method`; decides `used_visits`; 3 tiers (age < 3 months → claims in 3 months; 3 ≤ age < 6 → claims in 6 months; else → claims in 12 months); fall-through = baseline (`used_standard`). Tiers are disjoint and stated in the rule. **Label dishonest**: the three bindings `used_recent/used_middle/used_standard` are the identical `XCOUNT('plan','plan_claims', …, service_category='specialist_visit', adjudication_status='paid', provider_npi=carried_specialist)` differing only in `within_months=K(…)` (3/6/12); the tiers substitute a different number (a window length) into the same count. Finding **G-2**.
- complex_needs_bridge — `parameter`; bridge_visits 2/1/0; multi-source (plan membership category AND auth Home Health approval — distinct records); cross_difficulty plan (the auth read is also another difficulty's). Stated in rule; distinct outcomes.
- specialist_relationship — `parameter`; relationship 2/1/0 on count ≥3 / =2 / <2; single-source (pcp_events); cross_difficulty none. Note the carried referral itself is always in its own count, so the count is ≥1 for every member who reaches this write; the tiers ≥3/=2/<2 still divide members.
- specialist_travel — `parameter`; travel 2/1/0 on ≥4 / 1–3 / 0 outbound completed legs to the specialist in 6 months; single-source (ride_trips); cross_difficulty ride.
- Counts as labelled: 4 factors, 3 parameter, 1 method; **after G-2, 0 honest method factors** (below the bound of 1).

**pcp_ext_standing_referral** (baseline: standard allowance 12, cap, deduct carried visits, floor 0)
- standing_allowance_tier — `parameter`; ceiling / 18 / 12; multi-source (plan_claims count AND plan membership category — distinct records); cross plan.
- specialty_monitoring — `parameter`; 4/2/0 on ≥3 / 1–2 / 0 specialty fills in 3 months; cross rx.
- eligibility_alignment — `method`; DAYS-to-renewal/validity vs whole-months-to-renewal/12 vs unaligned — genuinely different formulas; honest. Tier 2 is a conjunction over one record (status and renewal date of the same membership), not multi-source.
- post_hospital — `parameter`; 4/2/0; cross plan.
- travel_distance — `parameter`; 4/2/0 on ≥30 / ≥15 / shorter-or-none miles (XMAX, no window); cross ride.
- laboratory_review — `parameter`; 4/2/0 on ≥3 / 1–2 / 0 lab-xray claims in 3 months; cross plan.
- Counts: 6 factors; 5 parameter, 1 method; ≥1 multi-source; cross plan/rx/ride.

**pcp_ext_continuity_of_care** (baseline: window = continuity_of_care_days, standard rate 2, ceil(rate*window/90), floor 1, ceiling)
- continuity_window — `parameter`; 135/105/P(continuity_of_care_days); multi-source (plan category AND pcp_visits count); cross plan. Conflicts with base `pcp_provider_exit` (G-1).
- continuity_rate — `method`; tier 1 derives the rate from the history (visits in the last quarter), tiers 2/3 fixed 1 / 2; at least one tier changes the algorithm; honest. Observation **O-G13**: the ladder is non-monotone — a member with no visit in the half-year gets the standard rate 2 while a member with one or two visits gets the maintenance rate 1 — defensible as "default when there is no cadence to read", so not red.
- co_management — `parameter`; reduction 2/1/0; multi-source (standing referral on pcp_events AND specialty fill on rx_fills); cross rx.
- emergency_followup — `parameter`; 2/1/0; cross plan.
- Counts: 4 factors; 3 parameter, 1 method; multi-source ≥1; cross plan/rx.

**pcp_ext_specialist_referral** (baseline: standard 4 visits, ceiling)
- core_visits — `parameter`; 8/6/4; multi-source (plan claims AND auth request); cross auth.
- result_review — `parameter`; 2/1/0; multi-source (two different auth holdings); cross auth.
- travel_distance — `parameter`; 2/1/0; cross ride.
- medication_review — `parameter`; 2/1/0 (specialty / brand-or-non-preferred / else); cross rx.
- emergency_followup — `parameter`; 2/1/0; cross plan.
- eligibility_alignment — `method`; honest (as in standing).
- Counts: 6 factors; 5 parameter, 1 method; multi-source ≥1; cross auth/ride/rx/plan.

**pcp_ext_second_opinion** (baseline: consultation 1 visit, ceiling)
- recommendation_review — `method`; pending → treating visits // 4; approved → flat 1; else 0; honest (tier 1 is a derived quantity). Single-source condition (the auth request status).
- imaging_review — `parameter`; 2/1/0; cross plan.
- controlled_medication — `parameter`; 2/1/0; cross rx.
- mobility_level — `parameter`; 2/1/0 by active ride level; the disjunctions are over values of one record, not multi-source.
- Counts: 4 factors; 3 parameter, 1 method; **no multi-source factor in this policy** (the task-level multi-source bound must come from the other computation of the same task; observation **O-G14**).

All fall-through tiers equal their policy's baseline value. No two tiers of any ladder select the same value or method. Every `baseline.rule` is self-sufficient and wholly quoted in its rule. Business realism: every condition is a customer attribute a Medicaid MCO would plausibly weigh (eligibility category, specialist use, authorizations, fills, claims, travel); the "add visits for X" allowances are synthetic but not straw men, and every fall-through is the plan's ordinary treatment. Whether each factor bears weight and each baseline gives a definite wrong number is per task (`factor_weight` in each task file).

### findings

- **G-1 — SOURCE-POLICY RED (undeclared override), bears on task 0.**
  - Symptom: two clauses of the structured policy fix the continuity-of-care period after a provider's network exit differently.
  - Root cause: `pcp_ext_continuity_of_care` replaces the continuity period with a 135/105/90-day ladder but cites only `pcp_referrals` in `base_policy_refs` and declares `overwrite: []`; base `pcp_provider_exit` is not named.
  - Evidence: base `pcp_provider_exit.rule` (pcp.extended.yaml line 1167): "A member in active treatment may keep seeing the exiting provider for continuity_of_care_days after the exit date"; extended rule (line 1942): "The continuity window depends on the member's eligibility category and recent treatment: … receives the extended continuity window; … the intermediate continuity window; … the practice type's continuity-of-care days." with `extended_window_days: 135`, `intermediate_window_days: 105`; `base_policy_refs: [pcp_referrals]`, `overwrite: []` (lines 1916–1918).
  - Consequence: demonstrated on task 0's world in `0.md` (the base reading's window gives a different scored visit count whenever the member is on the extended or intermediate tier).
  - Affected: `pcp.extended.yaml` → `pcp_ext_continuity_of_care.base_policy_refs/overwrite/rule`, base `pcp_provider_exit.rule`.
- **G-2 — SOURCE-FACTOR RED (mislabelled effect; method bound unmet), bears on task 0.**
  - Symptom: the only `method` factor of `pcp_ext_referral_carryover` changes a number, not an algorithm.
  - Root cause: `used_visit_window` selects among three bindings that are the same XCOUNT with `within_months` = 3, 6 or 12.
  - Evidence: compute lines 1485–1488 (`used_recent/used_middle/used_standard` identical except `within_months=K('recent_window_months'|'middle_window_months'|'standard_window_months')`); factor block lines 1517–1540 (`effect: method`).
  - Consequence: counting only honest labels, the carryover computation has 3 parameter factors and 0 method factors, below the bound "at least 1 `method`" for that computation. Structural; applies to every task that scores a carryover.
  - Affected: `pcp.extended.yaml` → `pcp_ext_referral_carryover.factors[used_visit_window]`.
- Observations (not grounds for rework unless a task file demonstrates a consequence): O-G3 (carryover scope sentence says "single", compute reads latest referral of any type), O-G4 (standing prerequisite requires every unexpired single referral carried; carryover fixes visits only for the most recent one), O-G5 (continuity edge unsatisfiable on practice types without standing referrals), **O-G6 (difficulty claim `[pcp_assign, pcp_end, pcp_change_log, pcp_location_update]` vs every extended subject `pcp_referral_issue`; the difficulty summary's change/withdraw/move writes are exercised by no task tool)**, O-G7 (docstrings point at "the PCP assignment lookup" / "PCP history lookup"), O-G8 (continuity and second-opinion entries stored as `referral_type single`), O-G11 (standing `int()` without RND guard), O-G12 (Schedule IV non-pain fill as second reading of "controlled pain medicine"), O-G13 (continuity_rate non-monotone), O-G14 (second opinion has no multi-source factor). Also: continuity eligibility "a member in active treatment" is undefined in records (O-G15); "the last quarter / the last half-year" can be read as calendar periods while compute uses trailing whole months (O-G9); window boundary convention (anniversary day excluded) is not stated in any rule (O-G10). Each world-dependent one is checked in the task files.

## closing_checklist

Written after both reveals (2026-09-24T17:08Z). Everything above this heading was written before any reveal: file mtime 17:03:09Z, first read of `tasks/*.json` at 17:07:09Z. Its "17:05Z" freeze label was an estimate; see the `timestamp_correction` section of each task file.

**The difficulty is not closed: task 0 is SOURCE-POLICY RED (G-1) and SOURCE-FACTOR RED (G-2); task 1 PASS.** Step 4's items as they stand now:

- Per-task files: `0.md` and `1.md` match the two tasks one-to-one, with `_difficulty.md` alongside them. This is the first revision. Comparison verdicts: 0 RED, 1 PASS.
- Coverage and scope: revealed `charter_scope` is task 0 = {pcp_ext_referral_carryover, pcp_ext_standing_referral, pcp_ext_continuity_of_care} and task 1 = {pcp_ext_specialist_referral, pcp_ext_second_opinion}. That covers all five extended policies. The two scopes are pairwise disjoint, and each scope is exactly one component of the prerequisite graph. Task tools and GT are closed (every gold write uses its own scope's tool). The uuid8s were generated independently (see § action_binding_and_uuids).
- Trees:
  - Task 0 has n=2 prerequisites and 2 value_input edges; its user write is the continuity election.
  - Task 1 has n=1 prerequisite and 1 value_input edge; its user write is the second opinion.
  - Both are acyclic, and the difficulty-wide graph is a DAG.
- Factors: every factor bears weight against an honest baseline on its task's world, and every whole-baseline number is definite and differs from gold:
  - carryover 0 vs 5
  - standing 7 vs 13
  - continuity 2 vs 4
  - specialist referral 4 vs 8
  - second opinion 1 vs 7

  **Exception: carryover has no honestly labelled method factor (G-2).**
- Gates: the instantiation gates were not re-run by this audit. They are re-run only when the difficulty closes, and it has not closed. The coordinator's pre-audit snapshot is cited in § charter_global_frozen.
- Findings that bear on a rework, re-stated from above without being re-derived:
  - G-1 (SOURCE-POLICY RED, task 0)
  - G-2 (SOURCE-FACTOR RED, task 0)
- Observations: O-G3 through O-G15 above.
  - None was demonstrated on either world except O-G9. O-G9 gives a calendar-quarter reading of 1 for task 0's continuity visits; it is recorded as an observation only.
  - O-G6 is an observation of scenario-level weight. The difficulty's claimed event types `[pcp_assign, pcp_end, pcp_change_log, pcp_location_update]` are written by no task tool in this difficulty. Every extended policy's subject is `pcp_referral_issue`, which no difficulty in `blueprint.yaml` claims.

## revision_2

### charter_global_frozen (revision_2)

- Re-audit started 2026-09-24T17:09Z by the tool clock; this section was written at about 17:14Z. Same auditor as round 1. The derivation is not blind: round-1 GT was revealed, and this round checks closure item by item.
- Both shared inputs changed, so every charter-global check was re-derived rather than carried forward:
  - `pcp.extended.yaml`: 54cdea24… → **385121a4ed65e556eafcfd55fe7e19d875da087ba327a27c50c58076e926ae48**
  - `task_tools.py`: 65d36829… → **e8e62f1109f893795131e56f59a9298767d57d4e705e982bc4f621c09224c568**
  - Both match the round-2 brief.
- Unchanged:
  - `blueprint/products/pcp.yaml` 549a6e8d…
  - `blueprint.yaml` 9813a996…
  - `db_schema.json` 122531ba…
  - `share_tools.py` a569fd6e…
- The masked views are byte-identical to round 1 (3995e097…, 43711a7f…); re-hashed by the auditor.
- Gate snapshot supplied in `scratchpad/brief_pcp_r2.md`: all 7 gates rc=0 (check_traceability deferred). Entry conditions are met.
- Not read: `worklog.md` and `__pycache__`. No recursive search was run.
- Read after the charter re-derivation, for comparison only:
  - the revealed task JSONs' `evaluation_criteria`
  - `computations`
  - `charter_scope`
  - `design_rationale` (a keyword scan)

### re-derived charter-global checks

- **Base section**: lines 1–1427 are still byte-identical to `blueprint/products/pcp.yaml`. The only difference is one blank separator line before `extended_policies`.
- **rule_compute_equivalence** (mechanical re-run on the new file):
  - For all five policies, every `compute_basis` sentence is verbatim in its rule and every compute binding has a basis.
  - Every `baseline.rule` sentence is verbatim in its rule, and every `overwrite[].replaced_by` sentence is verbatim in its rule.
  - Hand sweep of the changed parts:
    - carryover `carried_*` now filter `referral_type='single'`, matching "the most recent single referral that the earlier assignment issued" (O-G3 closed).
    - carryover `travel_visits` is `(outbound_legs // 2) if legs >= 4 else (1 if legs >= 1 else 0)`, matching "for a member with four or more such legs … one visit for every two legs, rounded down; … one to three legs … flat one-visit …; … no leg … no travel visit".
    - standing `aligned_total` is `int(RND(x, 6))` (O-G11 closed).
    - Every rule now carries the window-convention sentence "a record is inside a window of a given number of months when fewer than that number of whole months separate its date from the handling date, so a record dated exactly that number of months back is outside it". That is exactly `0 <= MONTHS(d, NOW) < W` (O-G10 closed).
    - The continuity rule states that "The last quarter and the last half-year are trailing periods of three and six whole months … not calendar quarters or halves" (O-G9 closed).
- **action_binding_and_uuids**:
  - Tool names and uuid8 tails are unchanged.
  - Function bodies are unchanged: one `ctx.create` each and no validation.
  - Docstrings now say "as it appears on the member's primary care assignment record" and "in the member's referral history" instead of naming the lookups (O-G7 closed).
  - No sequencing word was added.
- **prerequisite_graph / prerequisite_sentences**:
  - All three edges are unchanged: same `policy_source`, which is still verbatim in the blocked rule, same gate, kind, form, condition and resolved_by.
  - The graph is still acyclic, and the single-reading derivations of round 1 still hold.
  - The new definition sentence in the continuity rule ("A member is in active treatment with the exiting provider when the member had at least one visit with that provider in the last half-year.") states no cross-problem order.
- **override_declarations**:
  - carryover, standing, specialist referral and second opinion: `pcp_referrals` only, `overwrite: []`. The round-1 sentence-by-sentence conclusions stand, because their rules changed only by the window-convention sentence and the carryover "single" / travel wording, none of which touches B1–B5.
  - continuity: `base_policy_refs: [pcp_referrals, pcp_provider_exit]` with one overwrite entry:
    - `superseded_clause` "A member in active treatment may keep seeing the exiting provider for continuity_of_care_days after the exit date" is verbatim in base `pcp_provider_exit` (whitespace-normalised match).
    - `replaced_by` is two sentences, both verbatim in the rule, including "… the period after the exit date during which the member may keep seeing the exiting provider is the continuity window set out here, in place of a fixed continuity-of-care period for every member in active treatment."
    - After replacement the merged semantics for the window are unique. **G-1 closed.**
  - Sentence sweep of the rest of `pcp_provider_exit`: the notice-timing sentence is untouched, and so is the reassignment-at-exit sentence. The retained clause "and a pregnant member through the postpartum period where continuity_of_care_pregnancy_through_postpartum is true" still fixes a period for pregnant members alongside the extended window ladder, which the declaration names only for "every member in active treatment". This is observation **O-R2-1**: it is not demonstrable, because neither world holds a pregnant member (task 0 is Prairie Ridge ABD Care and task 1 is Prairie Ridge Expansion Adult; `design_rationale` also states the pregnancy clause "stay[s] in force").
  - The new definition of "in active treatment" specifies a base term that was undefined. It narrows nothing the base fixed. Observation only (O-R2-2).
- **factor_ladders** (changed policies only; the rest are unchanged from round 1):
  - carryover:
    - `used_visit_window` is now labelled `parameter`, and its tiers are the look-back lengths 3, 6 and 12 months. The label is honest.
    - `specialist_travel` is now labelled `method`:
      - tier 1 derives the visits from the leg count (legs // 2);
      - tier 2 is flat 1;
      - tier 3 is 0 (the fall-through, equal to the baseline).
    - Its outcomes are distinct: at least 2 on tier 1, 1 on tier 2, 0 on tier 3. At least one tier changes the algorithm, so the label is honest.
    - Counts: 4 factors, 3 parameter and 1 method. **G-2 closed.**
  - continuity: the four factors and their ladders are unchanged. But the new active-treatment eligibility sentence makes the `continuity_rate` fall-through unreachable (new finding **G-3**, below).

### findings (revision_2)

- **G-1 — CLOSED.**
  - Evidence: the declared override above.
  - The base 90-day reading is now superseded by name, so on task 0's world the continuity visits have the single value 4 (see `0.md` § revision_2).
- **G-2 — CLOSED.**
  - Evidence: the new labels.
  - `specialist_travel` (method) bears weight on task 0: baseline 4 vs gold 5.
- **G-3 — SOURCE-FACTOR RED (new; introduced by the rework for O-G15); bears on task 0.**
  - Symptom: `pcp_ext_continuity_of_care.factors[continuity_rate]` has a fall-through tier that no member who reaches the continuity write can be on. The ladder therefore divides eligible members into only two tiers, and the policy's baseline method is a treatment the plan gives no eligible member.
  - Root cause: the rework added the eligibility definition "A member is in active treatment with the exiting provider when the member had at least one visit with that provider in the last half-year." The rule opens "a member in active treatment may elect …", so only members with at least one visit in the last half-year reach this write. The rate ladder's fall-through is "a member with no visit in the last half-year is set at the standard continuity rate" (`continuity_rate: … else K('standard_rate')`, where `visits_last_half_year` is the same six-month count of visits with the assigned, i.e. the exiting, provider).
  - Evidence:
    - `pcp.extended.yaml` continuity `rule`, sentences 2 and 9;
    - compute `visits_last_half_year: COUNT('pcp_visits', within_months=K('half_year_months'), …)` and `continuity_rate: visits_last_quarter if visits_last_half_year >= K('active_treatment_visits') else (K('maintenance_rate') if visits_last_half_year >= 1 else K('standard_rate'))`;
    - `factors[continuity_rate].ladder[2]` "otherwise (no visit in the last half-year) — use the standard continuity rate";
    - `baseline.rule` "the member is expected to see the provider at the standard continuity rate".
  - Demonstrated consequence:
    - The eligibility sentence and the fall-through condition are contradictory, so tier 3 is empty for every member who reaches this write.
    - The "one visit, or more" half of tier 2's condition holds of every such member, so it restates the policy's scope.
    - The live ladder is therefore two tiers (at least 3 visits → cadence; 1–2 visits → maintenance rate 1), below the three-tier bound.
    - The baseline's "standard continuity rate" is the treatment of a member the policy does not serve: the straw-man baseline in the form the skill names ("a default no such business applies to its ordinary customer").
    - This is structural and independent of the world. On task 0's world the factor still moves the score (2 vs 4), which does not cure the ladder.
  - Affected: `pcp.extended.yaml` → `pcp_ext_continuity_of_care.rule` (active-treatment sentence vs rate-ladder sentence), `.factors[continuity_rate]`, `.baseline.rule`.
- Observations status:
  - Closed: O-G3, O-G7, O-G9, O-G10, O-G11 and O-G15. O-G15's definition is the cause of G-3.
  - Moot: O-G13 (the non-monotone fall-through is now unreachable; superseded by G-3).
  - Unchanged: O-G4, O-G5, O-G8, O-G12, O-G14 and O-T1-1.
  - Not addressed (the blueprint is frozen): O-G6.
  - New observations: O-R2-1 (retained pregnancy clause) and O-R2-2 (definition added to a base term).

### closing_checklist (revision_2)

The difficulty is not closed: task 0 is SOURCE-FACTOR RED (G-3) and task 1 is PASS.

- Scopes (revealed `charter_scope`, unchanged) are still disjoint and complete.
- The trees and the DAG are unchanged.
- Every factor bears weight on its world. The round-2 recomputation of every expected value, factor baseline and whole baseline equals round 1 and GT; the figures are in each task file.
- The gates were not re-run by the auditor, because the difficulty has not closed.

## revision_3

### charter_global_frozen (revision_3)

- Time: 2026-09-24T17:16Z–17:20Z by the tool clock. Same auditor. This round is not blind: it checks closure item by item, looks for regressions and new defects.
- Inputs:
  - `pcp.extended.yaml` changed: 385121a4… → **9cd886ab5789f479eeb402cbb4dc2a472317b4ada503a38517a020b3b10672b2** (matches the brief).
  - `task_tools.py` unchanged since round 2: e8e62f11… (re-hashed).
  - Blueprint files unchanged.
  - Masked views unchanged: 3995e097… and 43711a7f… (re-hashed).
- Gate snapshot in `scratchpad/brief_pcp_r3.md`: all 7 gates rc=0 (check_traceability deferred).
- Not read: `worklog.md` and `__pycache__`. No recursive search was run.
- Because the extended charter's hash changed, the charter-global checks were re-derived: the mechanical sweep, a policy-by-policy diff against the round-2 dump, and a hand review of the diff.

### re-derived charter-global checks

- **Diff vs round 2.** The only textual change among the dumped policies (standing, continuity, specialist referral, second opinion: refs, overwrite, rule, params, prerequisite, compute, factors, baseline) is the `pcp_ext_continuity_of_care.rule`. It changed in two places:
  - The active-treatment sentence now reads: "A member is in active treatment with the exiting provider when the member had at least one visit with that provider in the last year; the visits in the last half-year then set the continuity rate as described below, and a member whose visits all fall earlier than the last half-year is still in active treatment."
  - The closing sentence now defines "the last year" as well: "The last quarter, the last half-year and the last year are trailing periods of three, six and twelve whole months … not calendar quarters, halves or years".
  - Carryover was spot-checked and is unchanged from round 2: the params, `referral_type='single'` in `carried_*`, the travel `legs // 2` method sentence, and the labels.
  - `task_tools.py` is byte-identical to round 2.
- **Base section:** lines 1–1427 are still byte-identical to `blueprint/products/pcp.yaml`.
- **rule_compute_equivalence:** the mechanical re-run passes for all five policies. Every basis sentence is verbatim in its rule, every binding has a basis, every baseline sentence is in the rule, and every `overwrite.replaced_by` sentence is in the rule. The new sentence is an eligibility gate, not a computed quantity, so it needs no compute binding.
- **action_binding_and_uuids:** unchanged from revision_2 (same module).
- **prerequisite_graph / prerequisite_sentences:** all three edges are unchanged and every `policy_source` is still verbatim in its rule. The new sentence's "then" orders two parts of the same policy's rule (eligibility, then rate); it states no cross-problem order.
- **override_declarations:** unchanged from revision_2, and G-1 stays closed. The declared superseded clause and its replacement are intact. "In active treatment" is still a definition added to a base term that was undefined (O-R2-2).
- **factor_ladders:** `continuity_rate` is re-examined below. All other ladders are unchanged from revision_2.

### findings (revision_3)

- **G-3 — CLOSED.**
  - Eligibility is now "at least one visit with that provider in the last year (trailing 12 whole months)". The rule also says explicitly that a member whose visits all fall before the last half-year is still in active treatment.
  - The three rate tiers are therefore all live for eligible members, pairwise disjoint and distinct in outcome:
    - at least 3 visits in the last 6 months → cadence rate (visits in the last quarter);
    - 1–2 visits in the last 6 months → maintenance rate 1;
    - 0 visits in the last 6 months but at least 1 in the last 12 → standard rate 2. This fall-through equals the baseline.
  - The baseline is again a treatment the policy gives a real set of eligible members.
  - The window convention makes the boundary exact: a visit dated exactly 6 whole months back is outside the half-year and inside the year.
- **G-1, G-2 — still closed** (evidence as in revision_2; the relevant text is unchanged).
- **No new red.**
  - O-G13 revives as an observation: the rate ladder is non-monotone. An eligible member with no visit in the half-year gets rate 2, above the 1 given to a member with one or two recent visits. It is defensible as the default when there is no recent cadence to read, as judged in round 1.
  - Trivial wording note in `tasks/0.json` `design_rationale` §14: "(visits only 7-12 months back)". Under the stated convention the fall-through set also includes a visit dated 6 whole months back to the day. This is a domain description, not a claim about the task's world, and changes no scored value.
- Observations carried: O-R2-1, O-R2-2, O-G4, O-G5, O-G6 (blueprint frozen), O-G8, O-G12, O-G13, O-G14, O-T1-1. Closed items stay closed: O-G3, O-G7, O-G9, O-G10, O-G11, O-G15 (now without the side effect that caused G-3).

## closing_checklist (revision_3)

Written after both tasks were compared in revision_3 and both PASS.

- **Report files:** `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`, with `_difficulty.md` alongside. Old revisions are preserved: round-1 text, `revision_2` and `revision_3` are all appended and none rewritten. The latest comparison verdict is PASS for both tasks.
- **Coverage and scope:** the five extended policies are fully covered. The scopes are disjoint and each spans a whole tree:
  - task 0 = {carryover, standing, continuity}
  - task 1 = {specialist referral, second opinion}

  Task tools and GT are closed, since every gold write uses a tool of its own scope. The five uuid8s are independently generated and frozen, unchanged since round 1.
- **Problem trees:**
  - task 0: 2 prerequisite problems, 2 value_input edges, and the continuity election as the customer's own write;
  - task 1: 1 prerequisite problem, 1 value_input edge, and the second opinion as the customer's own write.

  Each tree is acyclic, and the difficulty-wide graph has two chains with no cross-task edge.
- **Factor counts:**

  | computation | factors | parameter | method | whole baseline vs gold |
  | --- | --- | --- | --- | --- |
  | carryover | 4 | 3 | 1 | 0 vs 5 |
  | standing | 6 | 5 | 1 | 7 vs 13 |
  | continuity | 4 | 3 | 1 | 2 vs 4 |
  | specialist referral | 6 | 5 | 1 | 4 vs 8 |
  | second opinion | 4 | 3 | 1 | 1 vs 7 |

  Per task there is at least 1 multi-source factor and at least 1 cross-difficulty factor, and the cross-difficulty rows are seeded.
- **Factor checks:** every ladder has at least three live, pairwise-disjoint tiers that are distinct in outcome and stated in full in its rule. Every factor bears weight against an honest baseline on its task's world; the round-3 recomputation matches GT `factor_sensitivity` figure for figure.
- **Gates on the final form:** the coordinator's round-3 snapshot was run after the rework on exactly these hashes (extended 9cd886ab…, tools e8e62f11…): check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and check_cross_fire all rc=0. check_traceability is deferred to KB publication.
- **Result:** the difficulty passes the source-layer policy-task audit. Standing observations, O-G6 above all, are recorded above for the owners of the scenario-level checks.
