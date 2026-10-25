# Policy-task audit — prepaid_service_hours / charter-global

## revision_1

## charter_global_frozen
- Frozen: 2026-10-18T01:57:08Z (on-disk mtime), auditor: erl-task-policy-audit (independent of the instantiator). Written before any task GT was revealed; nothing below is derived from a revealed GT.
- Hashes (re-computed, identical to the coordinator brief): `timebank.extended.yaml` 7b89751b8c84398f91643c3e7415003626cb20536fa8c288f2c07bde000926ff, `task_tools.py` e975d606f97e5e912995e083175da4caf2a476f715d6778a8382b5eba2034423, `0.view.json` d4db23dc…ed1c, `1.view.json` e3491bda…82ed.
- Read: `blueprint/` (blueprint.yaml, db_schema.json, products/{timebank,managed,security,hardware,project}.yaml), the extended charter, `task_tools.py`, the two masked views (frozen_time, user_scenario, initial_state), `audits/render_source/XF_recipe.md`, and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (lines 224-395 only: MONTHS/DAYS/SUM/COUNT/LATEST/CFIELD/CPARAM/XLATEST semantics) to fix the meaning of compute expressions.
- Masked/unread until the freeze: `tasks/prepaid_service_hours/tasks/*.json`, `plan.md`, `worklog.md`, every masked key (`evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`). No search was run with those paths in its domain.
- Entry conditions: gate snapshot supplied (7 gates rc=0, check_traceability deferred), masked views with hashes supplied. Complete.

### policy_conflict_scan
- Policies: base 9 (verbatim: `diff` of extended lines 1-927 against `blueprint/products/timebank.yaml` is empty) + extended 7: P1 `timebank_ext_repeat_order_quote` (user tool `sign_repeat_block_order_5562f94d`), P2 `timebank_ext_visit_travel_entry`, P3 `timebank_ext_visit_draw_correction`, P4 `timebank_ext_remote_session_draw`, P5 `timebank_ext_install_visit_draw`, P6 `timebank_ext_project_time_draw`, P7 `timebank_ext_extension_quote` (user tool `sign_block_extension_cebc1113`).
- Prerequisite graph: P1 -> {P2, P3}; P7 -> {P4, P5, P6}. Two disjoint trees covering all 7 extended policies; the natural scope split (task 0 = {P1,P2,P3}, task 1 = {P7,P4,P5,P6}) is mutually exclusive and jointly complete (to be confirmed against `charter_scope` after the reveal).
- Overlapping subjects: P2, P4, P5, P6 all write `timebank_hours_drawn`; distinguished by work_type (travel / remote_support / onsite_support / project_work) and by sibling-excluding `replaced_by` texts (P4 names install + project + travel; P5 names remote + project + travel; P6 names remote + install). P3 alone writes `timebank_draw_reversed`.
- Shared selector: P2, P3 and P5 all select "the onsite ticket most recently resolved by the service desk to the prepaid-block route" (identical XLATEST pair on labor_class onsite_business_hours / onsite_after_hours). P5's tool therefore draws any latest onsite visit, not only installations (see F-C4).
- Overlapping trigger worlds (state_due policies firing on the other tree's world) are probed per task; see F-B3 and the task files.
- Cross-category read boundaries: managed (agreement status/tier/go-live/seats/renewals/params; managed_tickets), security (subscription tier), hardware (delivered order), project (engagement, work logs). All reads are customer-scoped by the DSL.

### rule_compute_equivalence
- Mechanical sweep (scratch script, normalised whitespace): every `compute_basis` quotation of all 7 policies is verbatim in its own rule; every `baseline.rule` sentence is in its rule; every `replaced_by` is in its rule. No binding belongs to two factors; no factor binding reaches another factor's binding (transitive read walk) — XF A.1/A.2 clean. No factor id is a substring of a tool name (XF A.7 clean).
- DSL facts used: `within_months=N` keeps rows with 0 <= MONTHS(date, today) < N, which is exactly "dated after the same day N months earlier" (P1 12, P6 1, P7 3, P7 project count 1) — matches. MONTHS subtracts one when the day-of-month is not reached — matches P1's "a month being complete only once the same day of the month is reached". SUM/COUNT/LATEST are scoped to the target block. LATEST/XLATEST break ties by first row met (strict >). CFIELD returns the first matching holding. `RND` is Python `round` (binary half-even), not half-up (observation O-1).
- Defects found (details in findings): F-B1 (P3 trigger in minutes vs compute in hours), F-B2 (multi-record words, single-record compute: P1/P7 prerequisite sentences and P2/P3/P4/P5/P6 selectors), F-B3 (selectors have no "not yet drawn" test), F-B4 (same-date ties unstated: P2, P3, P6), F-B5 (absent/decoy payment records: P1, P7), F-C4 (P5 rule vs compute for non-installation visits).

### action_binding_and_uuids
- 7 `(target_tool, computes)` pairs, each claimed by exactly one policy. Tool bodies (task_tools.py) perform the write only; none reads a status, checks a prerequisite, errors or hints (module docstring and bodies confirm). Docstrings carry formats only (no example values), name no other tool, and carry no sequencing word about other actions ("before it is passed" refers to rounding the argument).
- uuid8s: 5562f94d, 8d0122c7, 4cdbf60f, 4c084c45, 14ae60a8, e9603a55, cebc1113 — pairwise distinct, no shared prefix beyond a 2-char coincidence (4c), no sequence pattern. PASS.

### prerequisite_graph
- Every extended policy has `prerequisite` filled (P2-P6 `[]`). Problems point at extended ids of this file, none at itself or a base policy; graph acyclic.
- All five edges: `form: state`, no `fallback_reason` (correct for state form); `kind: value_input`; `gate` names a real compute binding (P1 `net_drawn_share`, P7 `ext_balance`); `resolved_by` equals the depended-on policy's `target_tool`; each `policy_source` verbatim in the blocked rule (mechanical sweep). `effect` texts are true of the tool bodies (travel/draw lowers balance and raises hours drawn; reversal raises hours reversed). No authoring-viewpoint phrasing.
- `condition` strength: P1 edge 2 condition ("worked_minutes exceed the billable minutes its ticket's ClearPath resolution leaves for that visit") matches the sentence; but the sentences quantify over "every" visit/session/line while each resolving policy figures only one record — F-B2.

### prerequisite_sentences
- P1 <- P2: "The repeat-order price is fixed only after the current block's hours ledger carries a travel entry for every onsite visit drawn on it, dated the same day and booked to the same ticket as that visit, wherever the block's size draws travel hours for a visit." Connective "only after"; record state (ledger travel entry, same date + ticket); no tool/id/snake_case. Unique writer: only `post_visit_travel_entry_8d0122c7` creates work_type travel. Derivation: sentence -> look for a policy whose rule writes a travel entry -> P2 ("Each onsite visit additionally draws a separate travel entry, dated the visit's date and booked to the visit's ticket") -> its tool. Single reading for one missing visit.
- P1 <- P3: "The repeat-order price is not fixed until the current block's hours ledger carries a reversal against every visit draw whose recorded minutes exceed what its ticket's resolution substantiates." Connective "not until"; record state (reversal pointing at the draw); unique writer: only `post_visit_draw_correction_4cdbf60f` creates timebank_draw_reversed. The qualifier borrows P3's own quantity ("the minutes the ticket substantiates for that visit"), which P3 defines only for the latest visit (F-B2).
- P7 <- P4/P5/P6: "fixed only after … a draw for every remote session …", "not worked out until … a draw for every installation visit …", "Before the extension fee is worked out, … must carry a draw for every line of project time …". Connectives present; record states; unique writers (only P4/P5/P6 tools create remote_support / onsite_support / project_work draws). Note P5's tool also draws non-installation onsite visits, but the P7 sentence is scoped to installation visits, so the writer is still unique for the waited-on state.
- No rule states a cross-problem order that grounds no edge; the depended-on rules do not restate the sentences. Base `timebank_low_balance_and_replenish` and others carry no cross-problem order used by a tree.
- Observation O-2: the "every …" quantifier vs single-record resolvers (F-B2) is the only dependency-form issue.

### override_declarations
Sentence-by-sentence against `base_policy_refs` (finding half only):
- P1 (agg_multi_holding, ordering_and_pricing, low_balance_and_replenish, billing_and_entitlements): price sentence overwritten and scoped ("and only for such an order … every other block order remains …", restating the base rule) — XF C.16 clean. Signed-order-form, large-block ClearPath gate, invoicing/due sentence, auto-replenish (no order form -> not a repeat order), card/late-fee/hold sentences: followed. CLEAN.
- P2 (agg_draw_order, draw_conversion): flat travel sentence overwritten (including its business-hours band). The replacement retires the flat figure for every travel entry, but the rule figures only one visit (F-B2).
- P3 (draw_disputes, draw_conversion), `overwrite: []`: dispute window, once-per-draw, cap at draw hours, block-status and depleted->active sentences inherited and not contradicted. **Undeclared**: the corrected figure departs from draw_conversion's "Worked minutes are the recorded minutes rounded up to billing_increment_minutes and never less than … minimum_draw_minutes_onsite for an onsite visit" (no onsite minimum) and from "Converted block hours equal worked minutes divided by 60, times the resource ratio …" where the ratio is the level of who worked (schema `timebank_hours_ledger.resource_level`: "the level of the person who performed the work"), replaced by ticket category / P1 reprioritisation; and the baseline drops ratio and band multiplier altogether — F-C1.
- P4, P5, P6 (agg_draw_order, draw_conversion): minutes sentence overwritten by P4, P5 (siblings name each other and project/travel — XF C.17 clean); conversion sentence overwritten by P4, P5, P6 (siblings name each other — clean). **Undeclared** in all three: the base time-band sentence "The time band is holiday on weekends and observed holidays, emergency for work dispatched outside business hours at the client's request to restore a down system, after_hours for other work outside business_hours_start to business_hours_end on business days …; only one band applies to a session, in that order of precedence" is replaced by each policy's own band schedule and "The draw is recorded in the band …" sentence (weekday observed holidays dropped; emergency redefined as P1+phone+ClearPath after-hours class in P4 and absent in P5/P6; after-hours taken from the ClearPath labor_class, i.e. ClearPath coverage hours, not TimeBank business hours) — F-C2. P6 additionally imposes a weekend 240-minute floor and uses unrounded logged minutes while the base minutes sentence still governs project lines (P4/P5 `replaced_by`: "a project time line … keep their own minutes rules"; P6 overwrites only the conversion sentence) — F-C3.
- P5: its own rule/replaced_by promises "any other onsite visit keeps the standard conversion of worked minutes divided by 60 times the resource ratio of the person who worked it times the band multiplier", yet its compute prices a non-installation visit at technician_ratio and under the installation band schedule — F-C4.
- P7 (rollover_and_extension): fee sentence overwritten for every extension (explicitly universal), rolled-out restriction restated; extension_allowed, extension_months, max_extensions_per_block, signed-by-expiry inherited. CLEAN. (Observation O-3: base gives no month-end convention for "extended by extension_months".)

### factor_ladders
Counts (declared / surviving the tests below):
| Policy | declared (param/method) | struck | surviving | multi-source | cross_difficulty |
|---|---|---|---|---|---|
| P1 | 5 (4/1) | — | 5 (4/1) | prompt_payer_tier, tenure_scale | tenure_scale, seat_volume_tier (managed) |
| P2 | 4 (3/1) | shared_day_split (mislabelled; tier 2 unreal), trip_parity_tier (tier 2 = fall-through on 40/80 sizes) | 2 (2/0) | dispatch_band_rate | dispatch_band_rate, trip_parity_tier (managed) |
| P3 | 4 (2/2) | sessions_offset (one method written as three), escalation_level_ratio (unreal condition, undeclared) | 2 (1/1) | — | service_recovery (managed) |
| P4 | 5 (4/1) | remote_clearpath_rate (tier 1 unreachable) | 4 (3/1) | remote_band_pricing, remote_floor_minutes | remote_floor_minutes, remote_level_ratio (managed) |
| P5 | 5 (4/1) | install_rush_rate (tier 2 unreal) | 4 (3/1) | install_rush_rate (struck), install_clearpath_rate | install_unit_minutes, install_lead_ratio (hardware), install_clearpath_rate (managed) |
| P6 | 5 (4/1) | — | 5 (4/1) | project_window_pricing | window/level/class/discount (project) |
| P7 | 6 (5/1) | — | 6 (5/1) | payment_standing_points, engagement_commitment_rate | clearpath_loyalty_rate (managed), engagement_commitment_rate (project) |
- Every ladder has >= 3 tiers stated in its rule with condition and value/method, each a branch of its `decides` binding and vice versa (rule/compute two-way check per tier: clean). Every fall-through equals the policy baseline for that input; every `baseline` value equals what `baseline.rule` states (P2 trip = onsite_trip_hours; P4/P5/P6 technician ratio, multiplier 1; P7 extension_fee_pct, hourly_rate_usd; P1 zero added percent).
- Tier-pairwise tables (XF A.6): distinct on reachable domains except P2 trip_parity_tier tier 2 vs fall-through on 40/80-hour blocks (all of ClearPath trip charges 85/95 ÷ 150/142 exceed onsite_trip_hours 0.5, so MN(...) = 0.5 = fall-through), P3 sessions_offset (tiers coincide everywhere), P4 remote_clearpath_rate tier 1 (unreachable). Observations (genuine shape change present, but some tier pairs differ only by a constant): P1 tenure_scale (flat vs none), P4 remote_band_pricing (weekend/after-hours/business all uniform multipliers), P5 install_unit_minutes (staged vs standard per-unit), P6 project_window_pricing (after-hours vs business) — O-4.
- Realism (XF D.21), struck: P2 shared_day_split tier 2, P3 escalation_level_ratio, P5 install_rush_rate tier 2. Observations: P3 service_recovery (SLA-credit uplift on a billing correction with no breach; quarter-hour round-up only for non-credit tiers), P7 clearpath_loyalty_rate (fee halved), P6 project_class_rate, P5 install_lead_ratio (>= 25 laptops drawn at architect ratio) — O-5.

### findings
Charter-global REDs (each names the tasks whose files carry the demonstration):
- **F-A1 SOURCE-FACTOR RED (XF A.6) — P2 `shared_day_split` mislabelled `method`.** Tiers: "the day's one trip is divided equally among those draws" (×1/n), "two trips" (×2), "one trip" (×1); compute `trip_share` = 1/n | 2 | 1 multiplied into `RND(trip_basis * dispatch_mult * trip_share * return_share, 2)`. Every tier substitutes a multiplier into the same product; no tier changes the formula's shape. Struck as a method -> P2 has 0 method factors (< 1). Bears on task 0.
- **F-A2 SOURCE-FACTOR RED (XF A.6) — P3 `sessions_offset` is one method written as three.** Tier 1 "billable minutes less the minutes of every other draw of the ticket, visits and remote sessions alike, never below zero"; tier 2 "billable minutes less the minutes of those earlier visits"; tier 3 "the whole of the billable minutes". Because the figured visit is the latest-dated visit, tier 1's method evaluated where tier 2 applies (no remote draws) is tier 2's method, and where tier 3 applies (no other draws) is billable − 0 = tier 3's method; compute `MX(0, T − (onsite_all − m) − remote_all)` reproduces all three branches. Bears on task 0.
- **F-A3 SOURCE-FACTOR RED (XF A.6) — P2 `trip_parity_tier` tier 2 coincides with the fall-through on the 40- and 80-hour sizes.** `MN(P('onsite_trip_hours'), RND(cp_trip_charge / P('hourly_rate_usd'), 2))` with ClearPath onsite_trip_charge_usd ∈ {95, 95, 85} (Monitor/Essentials/Standard) and hourly_rate_usd 150 / 142 gives 0.63/0.57 and 0.67/0.60, all capped to onsite_trip_hours 0.5 = the fall-through value. Charter-level; task 0 (20-hour block) is unaffected in value.
- **F-A4 SOURCE-FACTOR RED (XF A.6 / D.20) — P4 `remote_clearpath_rate` tier 1 unreachable.** Tier 1 needs "an after-hours session AND … ClearPath Premier or ClearPath Enterprise". managed.yaml: Premier/Enterprise `coverage_days: Mon-Sun`, `coverage_start 00:00`, `coverage_end 24:00`, `observed_holidays_excluded: false`, and `managed_billable_labor_rates`: "labor is after-hours when it is performed outside coverage hours" — the owning charter never produces `remote_after_hours` for those tiers. The ladder has two reachable tiers. Bears on task 1 (tier 2 taken).
- **F-A5 SOURCE-FACTOR RED (XF D.21) — P2 `shared_day_split` tier 2 is not a real treatment.** "when the visit is the only onsite draw of its date and its ticket was resolved on a later calendar day than the visit's date, it carries two trips, one for each day on site": a later resolution date is not evidence of a second day on site (the ledger shows a single onsite draw that date; a second day on site is its own onsite draw with its own travel entry). Charter-level (not taken in task 0).
- **F-A6 SOURCE-FACTOR RED (XF D.21 + C.18) — P3 `escalation_level_ratio` values a recorded visit by ticket category / reprioritisation, not by who worked.** The draw being corrected carries `resource_level` ("the level of the person who performed the work"), and base conversion multiplies by that level's ratio; the ladder ("security_concern -> architect_ratio; reprioritized to P1 -> senior_engineer_ratio") is a condition no MSP weighs once the worker's level is on the record. Bears on task 0 (tier 2 taken; equals the recorded senior_engineer here, so no value effect).
- **F-A7 SOURCE-FACTOR RED (XF D.21) — P5 `install_rush_rate` tier 2.** "an installation visit for a rush order resolved later, by rush_late_rate" (1.05) surcharges an installation that was not expedited, for a rush option the hardware charter already bills (`rush_fee_usd` in `quote_total_usd`). Charter-level (task 1 takes tier 1).
- **F-B1 SOURCE-POLICY RED (XF B.8) — P3 trigger vs compute.** Rule: "A visit draw whose recorded minutes exceed what its ticket's resolution substantiates is a mistaken draw"; compute has no minutes test and restores `MX(0, fix_hours − fix_corrected)` whenever the recorded hours exceed the re-priced figure. Where the recorded minutes do not exceed the substantiated minutes but the re-pricing (technician ratio / ticket-category level, ClearPath-class band) is lower than the recorded pricing, the rule says "no correction" and compute gives a positive restore. Bears on task 1 (demonstrated there).
- **F-B2 SOURCE-POLICY RED (XF B.15 / C.16) — multi-record words, single-record compute.** Members: P1 both prerequisite sentences ("a travel entry for every onsite visit", "a reversal against every visit draw …"), P7 all three ("every remote session", "every installation visit", "every line of project time"); P2 overwrite retires the flat travel figure for every travel entry while the rule figures only "the latest-dated onsite draw of the ticket that the service desk most recently resolved …"; P3 "A visit draw whose recorded minutes exceed … is a mistaken draw" vs "The visit draw a correction is figured for is the latest-dated visit draw …"; P4/P5/P6 retire the base conversion for every remote session / installation visit / project line but draw only the most recent one. Where two records are pending, the waited-on state cannot be produced by the policy surface and the base rule for the other record is retired. Bears on task 0 (second reading on the earlier SB-2306631 visit) and task 1 (single pending record each, no effect).
- **F-B3 SOURCE-POLICY RED (XF B.14) — selectors have no "not yet drawn" test.** P4 "The remote session drawn is the one on the client's ticket that the service desk most recently resolved …", P5 likewise, P6 "the client's most recently dated project time line whose billing route is the prepaid block"; none excludes a session/visit/line already on the ledger. On task 0's opening world the P4 compute returns 0.75 for SB-2291047 (drawn 2026-09-23) and P5 returns 4.88 for SB-2306631 (drawn). Charter-level (no gold effect under the careful reading; see task files).
- **F-B4 SOURCE-POLICY RED (XF B.11) — same-date ties unstated.** P2/P3 "latest-dated onsite draw of the ticket" (two visits on one date of one ticket), P6 "most recently dated project time line" (project logs are "per person level, band and day", so several lines per date is normal; `pj_sow`, `pj_minutes`, time_band and resource_level are separate XLATESTs on `work_date=pj_date`). No tie rule in either rule. Charter-level (no ties in either world).
- **F-B5 SOURCE-POLICY RED (XF B.13 / B.14) — payment records.** P1 payment schedule has no tier for an unpaid block invoice with no late fee (reachable for signature-activated 160/320 blocks) — compute gives `prompt_partial_pct`, the rule's tier 2 says "paid on a later day"; P1 `same_day_paid_n` counts any payment dated the order date (a partial same-day payment counts as "paid on the day it was posted"); P7 `ext_payment_date` is the latest payment of any invoice on the block, not of the block invoice the rule names. Charter-level (single full payment in both worlds).
- **F-C1 SOURCE-POLICY RED (XF C.18) — P3 undeclared departure from base conversion; straw-man baseline.** See override_declarations. Baseline "the corrected figure … substantiated minutes, rounded up …, divided by 60" with `fix_band_rate`/`fix_ratio` baselines of 1 is not the standard conversion any reader of `timebank_draw_conversion` applies (band multiplier and resource ratio always apply, onsite minimum applies). Bears on task 0 (demonstrated there).
- **F-C2 SOURCE-POLICY RED (XF C.18) — base time-band sentence overridden without declaration in P4, P5, P6.** Charter-level (task 1's three sessions are on non-holiday weekdays and their ClearPath class agrees with TimeBank hours, so no value effect).
- **F-C3 SOURCE-POLICY RED (XF C.18) — P6 minutes floor and rounding undeclared.** Charter-level (task 1's line is a weekday 180-minute line, a multiple of 15).
- **F-C4 SOURCE-POLICY RED (XF B.8) — P5 contradicts its own replaced_by for non-installation visits.** Charter-level (task 1's visit is an installation visit); also makes P5's tool a second general onsite-visit writer.

Observations: O-1 `RND` is Python round, not half-up (no scored value in either world sits on an exact half; baseline-only cases 5.175, 5.625 do); O-2 dependency quantifier (folded into F-B2); O-3 extension month-end convention absent in base; O-4 partial-constant method tiers; O-5 realism notes above; O-6 P4 records `resource_level` from ticket category although the ledger field means "the level of the person who performed the work".

## closing_checklist
Written after both reveals (2026-10-18T02:01Z). The difficulty does **not** close: two of the four relationships fail in both tasks.
- Per-task files 0.md / 1.md correspond one-to-one with tasks 0 and 1; each carries a frozen derivation written before any reveal and an appended `source_gt_comparison`. Both comparisons match GT figure for figure (every write, every argument, every factor_sensitivity and baseline_result, every edge_load_bearing value); neither carries an overall PASS because of the REDs below.
- Coverage/scope: charter_scope task 0 = {P3, P2, P1}, task 1 = {P4, P5, P6, P7} — pairwise disjoint, jointly the 7 extended policies; task tools closed; uuid8s independent (action_binding_and_uuids). PASS.
- Trees: task 0 n=2, 2 value_input; task 1 n=3, 3 value_input; each root is an owner=user write; whole-difficulty graph acyclic; every edge false at the opening and load-bearing. PASS.
- Factors: FAIL — task 0: P2 has 0 surviving method factors (F-A1), P3 has 2 surviving factors (F-A2, F-A6), P1 seat_volume_tier reads unsupported seat_count (XF D.20); task 1: F-A4, F-A7, seeded rate_discount_pct and renewal_count contradict their owning charters (XF D.20), supporting ledgers absent (PLAUSIBLE).
- Policy self-consistency: FAIL — F-B1 demonstrated on task 1 (322.72 vs 328.49), F-C1 demonstrated on task 0 (baseline vs trigger), F-B2 PLAUSIBLE on task 0 (2938.80 vs 3002.00), plus charter-level members F-A3, F-A5, F-B3, F-B4, F-B5, F-C2, F-C3, F-C4 (XF recipe classes: every member listed in `findings` above).
- Unique solution on the derived reading: identical to GT in both tasks.
- Instantiation gates were not re-run by the auditor (coordinator-owned); the brief's snapshot (all rc=0) stands for revision_1.

VERDICT revision_1: task0=RED[0.1,0.2,0.3,0.4,0.5] task1=RED[1.1,1.2,1.3,1.4,1.5,1.6,1.7] charter=F-A1,F-A2,F-A3,F-A4,F-A5,F-A6,F-A7,F-B1,F-B2,F-B3,F-B4,F-B5,F-C1,F-C2,F-C3,F-C4

## revision_2

### charter_global_frozen (revision_2)
- Gate: last line of `tasks/prepaid_service_hours/worklog.md` is exactly `REWORK round 2: gates 7/7 green` — passed. Reworker claims read from the "round 2 claims" block just above it (worklog lines 70-102).
- Snapshot (executed `/tmp/erl0069_coord/snapshot.sh prepaid_service_hours 2`, output @ 2026-10-18T05:06:19): check_extended rc=0 EXTENDED OK · check_task_tools rc=0 TASK TOOL CONTRACT OK · replay_tasks rc=0 REPLAY OK · check_solvability rc=0 SOLVABILITY OK · check_compute rc=0 COMPUTE OK · check_grounding rc=0 GROUNDING OK · check_cross_fire rc=0 SCOPE OK. Views: `r2/0.view.json` sha256=854f410aa6df9bd0a7812a7e17c344000ec1eea364b83996c052976a2b7c5cef, `r2/1.view.json` sha256=c375ee78760a3a2c0c5d3c4920143adca1a567d1ca0e7594f68637565fc65c63; `timebank.extended.yaml` sha256=9b007d19d97674fc6e0f90d466f115bc130c9d88ad806fd7b412c28928e58040; `task_tools.py` sha256=e155386ef0ffbd8a8fef1b7c4a9e8613adf5782b8e26a7bc622d3c0eb31f603a.
- Both shared hashes changed since revision_1 (7b89751b… -> 9b007d19…, e975d606… -> e155386e…), so every charter-global section below is re-derived in full, not carried forward. Written before either task's round-2 GT was opened.
- contamination_disclosure: not blind. Revision_1 revealed the round-1 GT, and the claims block names a few world facts and tiers (seat ledger 30+2+1+1, rush tier 1.15 on task 1, the service-visit draw yielding 0 for SB-2310275 on task 1). Every figure below was recomputed from the r2 views with the scratch evaluator.

### structure (revision_2)
- Base section is still verbatim (`diff` of lines 1-927 against `blueprint/products/timebank.yaml` is empty). There are 7 extended policies. `timebank_ext_visit_draw_correction` and its tool were removed. New: **P3s `timebank_ext_service_visit_draw`** with tool `post_service_visit_draw_abd20ee9` (agent). P1 dropped its Sentinel schedule and added a lead schedule. P4 dropped the Sentinel share and added a call-out factor. P6 dropped the class rate and added a minutes factor.
- Graph: P1 -> {P2, P3s}; P2 -> P3s; P7 -> {P4, P5, P6}. Acyclic, and every edge is state form and value_input (gates net_drawn_share, tv_day_n, ext_balance). Each `policy_source` is verbatim in its blocked rule and each `resolved_by` equals the depended-on target_tool (mechanical sweep).
- Mechanical sweep: every compute_basis quote is verbatim in its own rule (B.9), and compute_basis keys equal the compute bindings. Every baseline sentence and every replaced_by is in its rule. No factor reaches another factor's binding (A.1/A.2). No plain binding reads a factor-owned binding (XF 26, first clause). No factor id is a substring of a tool name (A.7). Factor counts: P1 5 (1 method), P2 4 (1), P3s 4 (1), P4 5 (1), P5 5 (1), P6 5 (1), P7 6 (1).
- Tools (XF 3 / 19 / 24): 7 tools, each `(target_tool, computes)` claimed once. uuid8s 5562f94d, 8d0122c7, abd20ee9, 4c084c45, 14ae60a8, e9603a55, cebc1113 are distinct. No body checks state. Docstrings carry formats only and no sequencing words. Events written: timebank_block_ordered (holding create), timebank_block_invoice, timebank_hours_drawn, timebank_block_extended (holding update), timebank_extension_fee. Their base triggers are timebank:timebank_block_invoice, [], [], timebank:timebank_extension_fee, [] — none crosses into another category (XF 24 PASS).

### round-1 RED closure (charter)
| id | status | evidence |
|---|---|---|
| F-A1 | closed | P2 `trip_value_basis` (method): zero / charge ÷ hourly_rate_usd / onsite_trip_hours. The all-pairs XF23 table passes: tier 2 adds two inputs and a division; tier 3 adds a tariff parameter that is non-zero on 10-80 sizes. The share factors are now labelled parameter. |
| F-A2, F-A6, F-B1, F-C1 | closed (policy removed) | The correction policy and its tool are gone. P3s draws new visits; its level schedule sets the level of a new draw ("The draw records that level"), the same pattern accepted for P4 (O-6). P3s overwrites the minutes, conversion and band sentences, each scoped and naming its siblings. |
| F-A3 | closed | Trip value is uncapped: 85/150 = 0.57 and 95/142 = 0.67 differ from onsite_trip_hours 0.5. |
| F-A4 | closed | P4/P3s ClearPath tiers are Professional, then Standard/Essentials/Monitor. Their coverage (Mon-Fri 07-19 or 08-17/18) produces after-hours classes. The rule states that Premier/Enterprise never do. |
| F-A5 | closed as worded | The "two trips" tier is removed. **New defect in the same ladder: N-1.** |
| F-A7 | closed | Rush tiers: same day 1.25, one to two days 1.15, else 1. |
| F-B2 | closed | All prerequisite and selector sentences are single-record ("the client's ticket most recently resolved …", "the client's most recently dated line …"). **Remaining member: N-3.** |
| F-B3 | closed | Not-yet-drawn tests: P2 tv_travel_n, P3s sv_done, P4 rs_done, P5 in_done, P6 pj_done. Probes: on both worlds, after the gold writes, every draw policy returns 0. |
| F-B4 | closed (residual observation) | Ties are stated and implemented: after-hours beats business-hours at the same minute; XMAX minutes within a class and minute; most minutes on a P6 date. Residual: equal minutes at the same minute in the same class (O-7). |
| F-B5 | closed | P1 and P7 match payments on the block invoice's invoice_number (pay_applied / ext_paid_sum) and state the partial and unpaid tiers. |
| F-C2, F-C3 | closed | Band, minutes and conversion overwrites in P3s, P4, P5 and P6 quote the base sentences verbatim, are scoped ("and only for …") and name every sibling. The weekday-holiday departure is declared. |
| F-C4 | closed | P5 handles installation visits only (result 0 when `not in_is_install`). P3s handles service visits only. |

### new and remaining findings (revision_2, charter)
- **N-1 SOURCE-FACTOR RED (XF D.21 / B.8) — P2 `shared_day_share` does not share one trip.** Rule: "when the block's ledger carries three or more onsite-support draws dated the visit's date, the visits share one trip and this one carries third_share of it; when it carries exactly two, half_share of it; when the visit's draw is the only one that date, the whole trip". Visits are drawn one at a time, so the first visit of a date has already taken the whole trip when the second arrives. The day's trips then add to 1 + 0.5 (two visits) or 1 + 0.5 + 0.33 (three); with four visits, 4 × 0.33 = 1.32. Neither sum is "one trip". If the visits were really separate trips, halving the later one has no basis either. No MSP bills a shared trip this way. Demonstrated on task 0's world (see 0.md). Struck, P2 keeps 3 factors (< 4).
- **N-2 SOURCE-POLICY RED (XF B.14) — single-holding first-match reads with no decoy rule.** Members:
  - P2 `tv_delivered`, P3s `sv_delivered`, P5 `hw_type`/`hw_delivered`/quantity/rush all read `CFIELD('hardware', …, status='delivered')`. The rules say "the client's hardware order whose status is delivered". With two delivered orders, the compute takes the first row met and the rule names no choice.
  - P7 `ext_pj_model` reads `CFIELD('project', 'pricing_model', status='in_progress')`, but the rule reads "a client with a time-and-materials engagement in progress". With a fixed-fee and a T&M engagement both in progress, a first-met fixed-fee row sends the compute to "any other client" (1), while the rule gives 0.9 or 0.95.
  - Charter-level: each world seeds one delivered order and one in-progress engagement.
- **N-3 SOURCE-POLICY RED (XF B.15 / B.13) — P6: a second line of the same SOW and date can never be drawn.** Rule: "where several such lines carry that date, the one logging the most minutes …; when … the block's ledger already carries a project-work draw for that statement of work dated that date, no project line is figured". Project logs are "per person level, band and day" (project.yaml `project_tm_billing`), so several lines per SOW and date is a normal state. After the first is drawn, the second matches the "already carries" test and stays undrawn, and the base conversion is retired for it. Charter-level: task 1 has one line per date.
- **N-4 SOURCE-POLICY RED (XF 26, third clause; wording only) — factor sentences that do not name the quantity they modify.** "a weekday service visit … is multiplied by …" (P3s band, ClearPath rate); "a remote session … is multiplied by …" (P4 band, ClearPath rate); "an installation visit … is multiplied by …" (P5 band, ClearPath rate, rush); "a line … is multiplied by …" (P6 band, discount, volume). Each names the visit/session/line rather than its block hours. Only the rule's assembly sentence names the hours. No value effect.
- **N-5 (task-level, task 0) SOURCE-FACTOR RED (PLAUSIBLE, XF D.20/25):** the current block has no signed order-form intake row (`timebank_orders` absent), while task 1 seeds one for its block. See 0.md.
- Observations: O-1 (Python round, not half-up) stands; no scored value sits on a half. O-7: residual equal-minute ties. O-8: P2 "under the same tie rules as the service-visit rule" names another policy's rule but restates the rule in full (A.5 not engaged). O-5 realism notes stand (P7 loyalty 0.5; P3s/P4 level set from the ticket category for new draws).
- Round-1 miss, now closed: the round-1 project original_value_usd 42000 was below the Advanced Project minimum of 50000. Revision_1 did not catch it. It is now 64000, within 50000-149999.99.

### closing_checklist (revision_2)
- Reveal at 2026-10-18T05:13:55Z, after all revision_2 derivations were on disk. Both comparisons match GT figure for figure: every write argument, every factor_sensitivity and baseline_result, and every edge. The only discrepancy is two customer_id values the auditor carried over from round 1; GT is correct.
- Scope: task 0 = {P3s, P2, P1}, task 1 = {P4, P5, P6, P7}. Disjoint, and together they cover the 7 policies. Trees: task 0 n=2 with 3 value_input edges; task 1 n=3 with 3. Each root is the customer's own write. The whole graph is acyclic.
- Round-1 REDs: every id F-A1..F-C4, 0.1-0.5 and 1.1-1.7 is closed (table above, task files). Nothing that passed in round 1 has regressed in value or tree. New in revision_2: N-1 (shared-day trip, same ladder as old F-A5), N-2, N-3, N-4 (charter); task 0 R2-0.2 (order form, PLAUSIBLE), R2-0.3 (stale proof text).
- Remaining class members, listed in full: B.14 first-match — P2 tv_delivered, P3s sv_delivered, P5 hw_type/hw_delivered/quantity/rush_requested, P7 ext_pj_model. B.15 — P6 pj_done blocks a second same-SOW same-date line. XF 26 wording — P3s band and ClearPath rate; P4 band and ClearPath rate; P5 band, ClearPath rate and rush; P6 band, discount and volume. D.21 — P2 shared_day_share.
- Gates were not re-run by the auditor; the coordinator snapshot @ 2026-10-18T05:06:19 (7/7 rc=0) stands for revision_2.

VERDICT revision_2: task0=RED[R2-0.1,R2-0.2,R2-0.3] task1=PASS charter=N-1,N-2,N-3,N-4

## revision_3

### charter_global_frozen (revision_3)
- Gate: worklog last line is exactly `REWORK round 3: gates 7/7 green`. The claims are the "round 3 claims" block (worklog line 143 onward).
- Snapshot: I executed `/tmp/erl0069_coord/snapshot.sh prepaid_service_hours 3`; output at 2026-10-18T07:01:56. All seven gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Hashes:
  - `r3/0.view.json` df9676d77f3d79d347b51a6520e2b4c71a7cdb7026bb8ac445f0ded5c128ab19
  - `r3/1.view.json` c375ee78760a3a2c0c5d3c4920143adca1a567d1ca0e7594f68637565fc65c63 (unchanged from r2)
  - `timebank.extended.yaml` 96c14842b34d035ed1b7de2e8c9a65c34e5609ea43ed707363444a0a9d2eb438 (changed)
  - `task_tools.py` e155386ef0ffbd8a8fef1b7c4a9e8613adf5782b8e26a7bc622d3c0eb31f603a (unchanged)
- Re-derivation: the extended charter changed, so every charter section is re-derived. The tool module is unchanged, so the revision_2 tool/uuid/XF-24 conclusions carry forward on hash e155386e…. Not blind (the earlier GT and the claims block were read before this section).
- Base section is still verbatim.

### re-derived checks (revision_3)
- Mechanical sweep, all 7 policies: compute_basis quotes are verbatim in their own rule (B.9); compute_basis keys equal the bindings; prerequisite sources are verbatim; every gate is a real binding; resolved_by equals the depended-on target_tool; baseline sentences and replaced_by texts are in the rule.
- Factor structure: no factor reads another factor's binding (A.1); no plain binding reads a factor-owned binding (XF 26); no factor id appears in a tool name (A.7). Counts: P1 5, P2 4, P3s 4, P4 5, P5 5, P6 5, P7 6, each with one method factor.
- Graph: unchanged and acyclic. The P2 -> P3s edge now gates on `tv_ticket_n`; the new visit draw raises it from 1 to 2, which moves return_leg_share, so the edge carries a real value.
- XF 26 wording sweep: every multiplier/ratio sentence in P2-P6 now names the hours it modifies (no hits).
- XF 23: the method factors are unchanged (PASS). P2 `month_trip_cap` is a parameter with values 0 / 0.5 / 1, all distinct.

### round-2 RED closure (charter)
| id | status | evidence |
|---|---|---|
| N-1 | closed | shared_day_share removed. Replaced by `month_trip_cap`: 4+ travel entries in the month -> ×0, 2-3 -> ×0.5, else ×1. A monthly cap with a taper is a treatment a real MSP publishes. Rule = compute (`tv_month_trips` uses within_months=1 = "entries dated after the same day of the previous month"). |
| N-2 | closed | Hardware is the latest delivered_date among delivered orders; on the same date, the order with the most units (XMAX quantity), whose type and rush flag are read (P2, P3s, P5; stated in each rule). P7 counts in-progress T&M engagements (XCOUNT). ClearPath first-match is safe because managed.yaml `managed_agg_multi_holding` says "A client organisation holds at most one ClearPath agreement at a time". |
| N-3 | closed | P6's done test is keyed on SOW + date + level + the recorded band. Every overwrite of P3s, P4, P5, P6 (and P2's) is scoped to "the visit / session / line this rule figures", and other records keep the base rules, so no record is left unpriced. The P7 project sentence names SOW, date and level. |
| N-4 | closed | Wording sweep clean. |

### new findings (revision_3, charter)
- **N-6 SOURCE-POLICY RED (XF C.16 / D.21): the travel scoping gives one trip two prices.** P2's replaced_by says "the travel of an installation visit, and of any other visit this rule does not figure, keeps the flat onsite_trip_hours at the business hours band". P2 figures only a visit dated on its ticket's resolution date. So an earlier visit on a ticket that is still open now draws the flat onsite_trip_hours (1.0 h on a 20-hour block), while the same trip on the resolved visit draws the ClearPath trip price (85/158 = 0.54 h). The trip-value schedule says the block bears "the agreement's own trip price", but only for one visit per ticket. Task 0's own seed contradicts this scoping: travel row 926ed7c7 is a visit P2 cannot figure, yet it is priced 0.54 (see 0.md).
- **Observations:**
  - O-7 (residual exact ties: same minute, class and minutes; same delivery date and units; same P6 date and minutes) stands.
  - O-9: P7's project sentence does not mention the band that its condition carries ("in the time_band the project rule records"); the draw "of that line" implies it.
  - O-1 (Python round) stands; no scored value sits on a half.

### closing_checklist (revision_3)
- Reveal at 2026-10-18T07:05:01Z, after every revision_3 section was on disk. Both tasks match GT on every write, factor figure and edge.
- Round-2 REDs: N-1, N-2, N-3 and N-4 are closed. Task 0's R2-0.1, R2-0.2 and R2-0.3 are closed. Task 1 has not regressed.
- Remaining XF class members, listed in full:
  - C.16/D.21 travel scoping, N-6 — P2's replaced_by is the only member. P3s, P4, P5 and P6 are not members. Their schedules read the ticket's resolution (class, priority, channel) or the line's own log, which do not exist for an unresolved or unselected record, so base conversion is the only pricing available for those records. P2's trip value reads only the ClearPath trip charge, which is available for every visit, so the flat-versus-agreement split has no basis.
  - D.20 seed: task 0's row 926ed7c7 (R3-0.1). No other seeded draw in either world is unfigured: each is dated on its own ticket's resolution date or is the latest line of its date.
- Observations (not REDs): O-1, O-7, O-9.
- Gates were not re-run by the auditor. The coordinator's snapshot at 07:01:56 (7/7 rc=0) stands.

VERDICT revision_3: task0=RED[R3-0.1] task1=PASS charter=N-6

## revision_4

### charter_global_frozen (revision_4)
- **Gate.** The worklog's last line is exactly `REWORK round 4: gates 7/7 green`. The reworker's claims are the "round 4 claims" block just above it.
- **Snapshot.** I executed `/tmp/erl0069_coord/snapshot.sh prepaid_service_hours 4`; output timestamped 2026-10-18T08:01:46. All seven gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- **Hashes.**
  - `r4/0.view.json` df9676d77f3d79d347b51a6520e2b4c71a7cdb7026bb8ac445f0ded5c128ab19 — same as r3.
  - `r4/1.view.json` c375ee78760a3a2c0c5d3c4920143adca1a567d1ca0e7594f68637565fc65c63 — same as r3.
  - `timebank.extended.yaml` 96cea9aed6ffd1111a40465adb2df66799518c64c2275b763a15e37830c912b7 — changed.
  - `task_tools.py` e155386ef0ffbd8a8fef1b7c4a9e8613adf5782b8e26a7bc622d3c0eb31f603a — unchanged; tool, uuid8 and XF 24 conclusions carry forward on this hash.
- **Scope of this pass.** The charter changed, so all charter-global checks are re-derived. As the brief asked, this is one exhaustive pass of XF 1-26 over all 7 policies and both seeds. Not blind. Written before round-4 GT was opened.

### exhaustive XF pass (revision_4)
| point | result | members / evidence |
|---|---|---|
| A.1/A.2/26a (factor independence, plain reads) | PASS | Mechanical walk: no factor reaches another factor's binding; no plain binding reads a factor binding. |
| A.3/A.4 (assembly, order) | PASS | P1 sums percentages once. P3s and P4 state replace -> floor -> weighting -> multiply. P2, P5 and P6 say "no order between the multipliers" (all multiplicative). P6 minutes come first. P7 states its order. |
| A.5 | PASS (O-10) | P1/P7 sentences say "where that visit is a service / installation visit". That is a record class whose test lives in the depended-on rule, which check 6 allows. No quantity is defined "as another policy figures it". |
| A.6/23 (method shape, all pairs) | PASS | P1 tenure (scaled+cap / tariff / none); P2 trip value (zero / charge÷rate / tariff); P3s and P4 call-out (min-split / max-floor / keep); P5 unit minutes (qty×rate / max(two inputs) / basis); P6 minutes (max-floor / ceil-60 / keep); P7 valuation (÷(purchased+rolled) / ÷purchased / tariff). |
| A.7 | PASS | No factor id is a substring of a tool name. |
| B.8 (rule == compute) | PASS for every policy | P2 selector rule matches compute (`tv_top_*`, `tv_use_other` when exactly two draws). |
| B.9 | PASS | All quotes verbatim; basis keys equal the bindings. |
| B.10 / B.12 | PASS | One RND per result where stated; MONTHS/DAYS conventions are stated. O-1 stands: no scored value sits on a half. |
| B.11 (ties) | **RED N-8** | Every second-level tie is unstated (see N-8). |
| B.13 | PASS | Absent records stated: no onsite draw, no ClearPath, no hardware, no line, unpaid invoice. |
| B.14 | PASS | Hardware = latest delivered_date, then most units; ClearPath is single by managed.yaml; P7 uses XCOUNT; P6 SOW is the business key; payments are matched by invoice number. |
| B.15 / "every X, one priced" | **RED N-7** | P2. |
| C.16/C.17/C.18 | PASS on declaration | All overwrites quote base verbatim and are scoped; siblings named. P2 now covers "every onsite visit … service visits and installation visits alike". |
| **One object, two prices across a scoped overwrite (N-6 class)** | **RED N-6 (members P3s, P4, P5, P6)** | Correction of revision_3, which wrongly excluded these members. P2 is closed. |
| D.19 | PASS | Unchanged tools; formats only. |
| D.20 seeds | PASS | Both worlds. Task 0 travel rows ce7a1dbc, 926ed7c7 and df89b1f0 each reproduce 0.54 under the r4 P2 rule at their posting date (trip 85/158; band business_hours ×1; month count < 2; first visit of the ticket). Every seeded remote/onsite/project draw is the record its rule figured at its date. |
| D.21 realism | PASS | Monthly trip cap with taper; trip at the agreement's price; dispatch read from the visit's own recorded band. |
| D.22 | checked after the reveal (task files) | — |
| 24 | PASS | Unchanged tool module. |
| 25 | PASS | Ledgers: managed seats and fees, block order forms, block invoices and payments, hardware and project billing. |
| 26b/26c | PASS | Every multiplier sentence names the hours or fee. |

### findings (revision_4, charter)
- **R3 closure.** N-6 is closed as worded for P2: one rule now prices every onsite visit's travel, keyed on the visit's own draw. A two-visit probe gives 0.54 for an open ticket and 0.54 for a resolved one.
- **N-6 SOURCE-POLICY RED (class re-scoped; members P3s, P4, P5, P6).** Each policy prices "the visit / session / line this rule figures" under its schedules, while "any other service visit / remote session / installation visit / project time line included, keeps the standard conversion … and the standard time-band precedence". Which regime a given record gets depends on posting order or on a sibling record, not on the record itself.
  - P6 (probe on task 1's world): add a 120-minute senior_engineer business-hours line to SOW-337412 on 2026-10-15. As the line P6 figures it draws 120/60 × 1.25 × 0.95 (discount) × 0.95 (volume) = 2.26 h. Because the 165-minute architect line logs more minutes that date, it is "any other project time line" and draws base 120/60 × 1.25 = 2.50 h.
  - P4: if a second remote resolution lands before SB-2311409 is drawn, SB-2311409 loses the call-out floor and split, the ClearPath 0.9 rate and the ticket-category level, and falls to base conversion: 45 min, the base emergency band at 1.75, the ratio of the person who worked (not on the ticket record). For example, 1.31 h at technician, against 2.36 h.
  - P3s and P5: the same mechanism with two onsite resolutions before either is drawn.
  - Revision_3 recorded these as non-members, arguing that base is the only pricing for records the resolution does not yet describe. That holds for an unresolved record. It does not hold for a resolved record that a later resolution pushes out of "this rule figures". The exclusion was wrong.
  - Charter-level: in both worlds every seeded draw was the figured record at its date.
- **N-7 SOURCE-POLICY RED (XF B.15) — P2 leaves some visits' travel with no rule at all.** The overwrite retires the flat charge for "every onsite visit", but the selector reaches only the latest onsite date: the most-minutes draw, then "exactly one other". Probes on task 0's world after the gold writes:
  - a third onsite draw dated 2026-10-14 -> P2 returns 0 (selector stays on SB-2306631);
  - an onsite draw dated 2026-10-12 without travel -> 0;
  - two equal-minute draws on one date: the first is figured (0.27), the second never is (selector returns the same ticket).
  - Each such visit's travel is neither figured nor flat.
- **N-8 SOURCE-POLICY RED (XF B.11, residual ties; promoted from O-7 so that nothing pre-existing resurfaces).** Rules state a first-level tie-break, but no rule states what happens when that tie-break also ties:
  - P3s/P4/P5: same minute, same class and the same billable minutes.
  - P5/P2/P3s: two delivered orders on the same date with the same units.
  - P6: two lines on the latest date with the same minutes.
  - P2: two draws on the latest date with the same minutes (also in N-7).
  - Compute takes the first row met. Charter-level.
- **Observations.** O-1 stands. O-9 is closed (the P7 sentence now names the band). O-10 is the A.5 note above. The P2 -> P3s condition text still describes "the client's latest onsite resolution" although P2 now reads draws only; it names the same record, so no second reading.

### closing_checklist (revision_4)
- **Reveal.** At 08:04:40Z, after every revision_4 section was on disk. Both tasks match GT figure for figure, and no proof text is stale.
- **Round-3 REDs.**
  - R3-0.1: closed.
  - N-6: closed for P2. Still RED as a class, now listed in full with members P3s, P4, P5 and P6 — revision_3 wrongly excluded them.
- **Complete member list of every open class:**
  - N-6, one object priced two ways across a scoped overwrite: P3s, P4, P5, P6. No other member — P1 (repeat order vs other orders) and P7 (every extension) price distinct objects or a single object once.
  - N-7, retired base rule but some records unreachable (B.15): P2 only. P3s/P4/P5/P6 retain base for unreached records, so they are not members.
  - N-8, residual ties (B.11): P2, P3s, P4, P5, P6, as listed in the findings above.
  - Every other XF point PASSES on every policy and on both seeds.
- **Tasks.** task0 PASS, task1 PASS. All three open items are charter-level, with no effect on either task's world or gold.
- **Gates.** I did not re-run them; the coordinator's snapshot at 08:01:46 (7/7 rc=0) stands.

VERDICT revision_4: task0=PASS task1=PASS charter=N-6,N-7,N-8

## revision_5

### charter_global_frozen (revision_5)
- Gate: worklog last line is exactly `REWORK round 5: gates 7/7 green`. Claims: the "round 5 claims" block.
- Snapshot: I executed `/tmp/erl0069_coord/snapshot.sh prepaid_service_hours 5`, output @ 2026-10-18T09:17:18. All seven gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Hashes (views and charter changed; tools unchanged):
  - `r5/0.view.json` 1c135496d87bbce7842b2a662c175afc32a792ea6cc862304d31f89ef3720c69
  - `r5/1.view.json` 235209c8662d7728f5de49ab4b2c7735c2436f8ad209590286972aff4b7a9837
  - `timebank.extended.yaml` 592ffa25a073d3642aac2ae694137a81ea2905f6daf4c4b6640fd0cb5b73cb51
  - `task_tools.py` e155386e…603a (unchanged; tool, uuid and XF 24 conclusions carry forward)
- Scope: per the brief, this checks what changed plus regressions. The round-4 pass was exhaustive.
- contamination_disclosure: not blind. The claims block states the round-5 gold figures (task 0 2.82 / 1.55 / 2938.80; task 1 2.36 / 6.47 / 5.08 / 316.23). All figures below were recomputed independently from the r5 views.
- World deltas, r4 -> r5:
  - task 0: SB-2306631 is now opened 2026-10-13 18:40 with billable 75; its 2026-10-07 visit draw (362da00a) and travel (926ed7c7) are removed. Added remote ticket SB-2303384 with a 1.50 h draw (2026-10-01). SB-2309118 is opened 2026-10-12.
  - task 1: project log of 2026-09-14 is 255 min; three project draws re-priced (5.75 / 6.49 / 7.90).
  - Personas unchanged.

### changed-policy checks (revision_5)
- Mechanical sweep (B.9, A.1/A.2, A.7, XF 26, prerequisite sources/gates/resolved_by): clean on all 7 policies. Factor counts 5/4/4/5/5/5/6, each with one method factor.
- P2 changes:
  - The return-leg and month-cap factors are replaced by `travel_level_ratio` ("travel time being drawn at the rate of the person who travels") and `dispatch_lead_rate` (same-day dispatch 1.25, next-day 1.15). Both are real treatments with distinct values.
  - Tie chain: date -> minutes -> higher ticket number, backed by P3s/P5's "A ticket's onsite labor is drawn once …".
- P3s / P4 / P5:
  - "Every service visit / remote session / installation visit is priced by the schedules below from its own ticket's records alone". The figured-record residues are gone; base is kept only for other kinds of draw.
  - "A ticket's … labor is drawn once, when the service desk resolves the ticket" agrees with managed.yaml (managed_ticket_resolved triggers timebank:timebank_hours_drawn). With it, the single-record selector always meets the only pending record of a producible world.
  - Tie chains end in the ticket number (one resolved row per ticket) and, for the hardware order, in quote_number.
- P6:
  - Scope is now "a line … whose statement of work, date and level carry no other block-routed line". Lines that share all three keep the base rules.
  - The volume factor is replaced by `project_class_rate` (Major/Strategic 0.9, Standard/Advanced 0.95).
  - Tie chain: date -> minutes -> SOW -> level.
- Seeds re-derived under the r5 rules, each at its posting date: travel ce7a1dbc and df89b1f0 -> 0.54 = seeded; project draws 5.75 / 6.49 / 7.90 / 6.77 / 5.64 = seeded.

### round-4 RED closure (revision_5)
| id | status | evidence |
|---|---|---|
| N-6 | closed for P3s, P4, P5 | Each record is priced from its own ticket's records. A record's regime no longer depends on posting order. |
| N-6 | **open for P6 (N-6b)** | See findings. |
| N-7 | closed for P3s, P4, P5 | "drawn once, when the service desk resolves the ticket" makes a second pending record a non-producible state. |
| N-7 | **open for P2 and P6 (N-7b)** | See findings. |
| N-8 | closed | Every tie chain ends in a business key: ticket number, quote_number, SOW + level. |

### findings (revision_5, charter)
- **N-6b SOURCE-FACTOR RED (D.21; one object, two prices) — P6 prices a line by its siblings, not by itself.**
  - Scope admits only lines whose SOW, date and level "carry no other block-routed line". project.yaml logs time "per person level, band and day", so a senior engineer with a business-hours line and an after-hours line on one day is an ordinary state.
  - Probe on task 1's world: a lone 120-min senior business-hours line on SOW-337412, 2026-10-15, draws 2.26 h (×0.95 locked discount, ×0.95 class rate). Add a 60-min after-hours line for the same level and date, and the identical 120-min line falls out of scope to base: 120/60 × 1.25 = 2.50 h. It loses the SOW's locked discount and the class rate.
  - The scope test is fixed records, not posting order, but the price is not a function of the line's own attributes, and no MSP drops a SOW's locked discount because the same engineer also worked an after-hours window that day.
  - Knock-on: P7's third prerequisite waits on a draw of "the client's most recently dated line …". When that line is out of P6's scope, P6 says "no project line is figured", so the resolver named in the edge cannot resolve it.
- **N-7b SOURCE-POLICY RED (B.15) — P2 and P6 state a price for every record but their selector cannot reach some records in producible worlds.**
  - **P2.** Passage A: "For the travel entry of every onsite visit … the travel is figured under the travel schedules below" and "Every onsite visit's travel is priced by the schedules below". Passage B: "the visit figured is the block's most recently dated onsite-support draw; where several … carry that date, the one recording the most worked minutes …; When … the visit so found already carries a travel entry …, no travel entry is figured".
  - P2 probe: visit A (60 min) and visit B (75 min) both drawn on 2026-10-15 before A's travel is posted. P2 figures B (0.54). After that it returns 0 for A for good. A says A's travel is priced and drawn; B says none is figured. No charter sentence makes travel immediate (unlike "drawn once, when the service desk resolves" for visits), so the state is producible.
  - **P6.** Two in-scope lines of one SOW and date at different levels: after the most-minutes line is drawn, P6 returns 0 for the other (probe on task 1's world: a 120-min senior line beside the drawn 165-min architect line -> 0). This contradicts "Project lines are drawn one at a time" and "Every line in that scope is priced".
  - Charter-level: neither world contains such a state.
- **Observations.**
  - O-12: P3s/P4/P5 single-record selectors rely on the drawn-at-resolution premise. That is fine for producible worlds; a seed violating it would be a D.20 defect.
  - O-10 and O-1 stand.
  - The P2 -> P3s condition still names "the client's latest onsite resolution"; it is the same record.

### closing_checklist (revision_5)
- Reveal at 09:21:26Z, after every revision_5 section was on disk. Both tasks match GT figure for figure, and no proof text is stale.
- Round-4 REDs:
  - N-8 closed.
  - N-6 closed for P3s, P4 and P5.
  - N-7 closed for P3s, P4 and P5.
  - Still open: N-6b (P6 only) and N-7b (P2 and P6).
- Complete member list of the open classes:
  - N-6b: P6 (sibling-dependent scope), plus its knock-on on P7's third edge.
  - N-7b: P2 (travel of a same-date visit whose travel lags) and P6 (second in-scope line of one SOW and date).
  - No other policy is a member. P1 and P7 price single objects. P3s, P4 and P5 are covered by the drawn-at-resolution premise.
- Regressions: none. Every round-4 PASS item was re-checked on the changed text.
- Gates were not re-run by the auditor; the coordinator snapshot @ 09:17:18 (7/7 rc=0) stands.

VERDICT revision_5: task0=PASS task1=PASS charter=N-6b,N-7b

## revision_6

### charter_global_frozen (revision_6)
- Gate: the worklog's last line is exactly `REWORK round 6: gates 7/7 green`. Claims are the "round 6 claims" block.
- Snapshot: I executed `/tmp/erl0069_coord/snapshot.sh prepaid_service_hours 6`; output timestamped 2026-10-18T09:52:16. All seven gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Hashes:
  - `r6/0.view.json` 85f79b2f76fe109962f2726824018fbf5c7a9ffcd4f19213184fdef6b5055483 (changed)
  - `r6/1.view.json` 235209c8662d7728f5de49ab4b2c7735c2436f8ad209590286972aff4b7a9837 (same as r5)
  - `timebank.extended.yaml` 846363fbf37d20d116f469c678f6fab5dcf3de42c2bb0a3d2df18166811e9f77 (changed)
  - `task_tools.py` 4515f04123e6b5540af61e36b2b476121c02bb0b2137d8983bf331bb81e4bbb4 (changed)
- Not blind: the claims restate the gold figures. Everything below was recomputed from the r6 views before the reveal.
- World delta, task 0: SB-2309118 and its visit/travel moved from 2026-10-14 to 2026-10-13 (opened 2026-10-09). 2026-10-14 now carries only the gold visit. Task 1 world unchanged. Personas unchanged.

### changed checks (revision_6)
- Mechanical sweep (B.9, A.1/A.2, A.7, XF 26, prerequisite sources/gates/resolved_by): clean on all 7 policies. Factor counts unchanged.
- Tools:
  - Only the travel docstring changed ("the travel entry of one onsite date"). It carries formats only and no sequencing words; the uuid8s are unchanged; XF 24 is unchanged (the events written are the same).
  - The project tool docstring still says "one line of time-and-materials project time", while P6 now draws one summed group — O-13 (wording; the tool body is unchanged).
- P2 (travel):
  - One trip per onsite date. It is priced from that date's draws by stated aggregates (any emergency, then any after-hours/holiday band; any architect, then any senior level; lead from the trip ticket, the longest visit, with the higher ticket number ending a tie). Rule = compute.
  - "a date's trip being posted at the close of that date and before any later date's visit is drawn" makes a waiting earlier date or a lagging same-date visit non-producible. One trip per site day is a real MSP treatment.
  - Seeds 2026-07-15 and 2026-10-13 reproduce 0.54 each.
- P6 (project):
  - A group is one SOW, date and level, drawn once for its summed minutes. It is priced from its own lines and SOW: after-hours minutes are taken in whole hours at the after-hours multiplier, business minutes as logged.
  - The sibling-dependent scope and the base fallback are gone. The seeded project draws reproduce.
- P7's third edge now waits on "each group of the client's most recently dated project time" and matches P6.

### round-5 RED closure (revision_6)
| id | status | evidence |
|---|---|---|
| N-6b | closed | Every P6 group is priced from its own lines and SOW; no line falls to a base regime because of a sibling. |
| N-7b (P2) | closed | One trip per date, plus the close-of-date posting premise. |
| N-7b (P6) | **open, now N-7c** | See below. |

### findings (revision_6, charter)
- **N-7c SOURCE-POLICY RED (XF B.15) — P6 states that every group is drawn and priced, but its selector cannot reach some producible groups.**
  - **Quoted passages.** A: "Every group is priced by the schedules below from its own lines and its statement of work alone, and a group is drawn once". B: "Project groups are drawn one at a time from the client's most recently dated block-routed project time … where every group of that statement of work is drawn, it is the group of the first level, in that order, whose highest-numbered statement of work logging that level that date has not yet drawn it; … no group of that date is found in that order, no project group is figured".
  - **P6 has no premise like P2's close-of-date one or P3s's "drawn once, when the service desk resolves the ticket"**, so the following states are producible. Probes on task 1's world after the gold writes:
    - **Second SOW, same level, same date.** An architect group on SOW-337400 dated 2026-10-15, beside the drawn SOW-337412 architect group. P6 returns 0 (no group found). The level clause reaches only the highest-numbered SOW per level, so a second SOW's same-level group is never reached.
    - **Late line of a drawn group.** A 60-min architect business-hours line logged on 2026-10-15 after the group was drawn. P6 returns 0, because "A group counts as drawn when the block's ledger carries a project-work draw recording its statement of work, date and level". project.yaml logs per level, band and day and triggers `timebank:timebank_hours_drawn` per logged line, so a later second-band line of a group is producible. Its minutes are never drawn.
    - **Earlier date pending.** A line logged for 2026-10-16 before the 2026-10-15 group is drawn. P6 moves to 10-16 (0.90 h), and the 10-15 group is never reached again.
  - Charter-level. In task 1's world each date has one group and the logs were drawn date by date, so there is no value effect.
- **Observations.** O-13 (project tool docstring "one line"). O-12, O-10 and O-1 stand.

### closing_checklist (revision_6)
- Reveal at 09:54:26Z, after every revision_6 section was on disk. Both tasks match GT figure for figure, and no proof text is stale.
- Round-5 REDs: N-6b closed. N-7b closed for P2. N-7b is still open for P6, renamed N-7c, with all three members listed above: a second SOW's same-level group, a late line of a drawn group, and an earlier date still pending.
- Regressions: none. P1, P3s, P4, P5 and P7 are unchanged in value and structure. The tool module change is docstring-only (O-13).
- Gates were not re-run by the auditor. The coordinator's snapshot at 09:52:16 (7/7 rc=0) stands.

VERDICT revision_6: task0=PASS task1=PASS charter=N-7c

## revision_7

### charter_global_frozen (revision_7)
- **Gate:** the worklog's last line is exactly `REWORK round 7: gates 7/7 green`. No revision_7 text existed on disk before this run, because the earlier delivery did not start. The reworker's claims are the "round 7 claims" block.
- **Snapshot:** I executed `/tmp/erl0069_coord/snapshot.sh prepaid_service_hours 7`; output at 2026-10-18T10:29:28. All seven gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- **Hashes:**
  - `r7/0.view.json` 85f79b2f…5483 — same as r6.
  - `r7/1.view.json` 235209c8…9837 — same as r6.
  - `timebank.extended.yaml` 1df42b57b574ad761b6458bf6b06bd1f089dd696000566c759910e4971c4728d — changed.
  - `task_tools.py` 31275c1dad9d35df558688c6106abc2eddcb69565b094b0e3e25996f47cdb1cb — changed (project docstring only, per O-13).
- **What changed:** both worlds are unchanged. The changes are in P6 and in P7's third prerequisite sentence. Checked before the reveal; not blind.

### changed checks (revision_7)
- **Mechanical sweep** (compute_basis verbatim, prerequisite sources/gates/resolved_by, replaced_by, keys): clean on all 7 policies. Factor counts are unchanged.
- **Tasks** recomputed on the r7 charter, all identical to revision_6:
  - task 0: 2.82 / 1.55 / 2938.80, skips 3002.00 / 3002.00 / 0;
  - task 1: 2.36 / 6.47 / 5.08 / 316.23, skips 327.67 / 347.59 / 340.85;
  - every factor baseline is the same;
  - after the writes, every draw policy returns 0;
  - the seeded project draws reproduce.

### round-6 RED closure (revision_7)
| N-7c member | status | evidence |
|---|---|---|
| (a) late line of a drawn group | closed | The "undrawn part" is the group's price over all its lines less what is already drawn. Probe on task 1's world: after the gold 5.08 draw, a 60-min architect business line logged later draws 1.35; 5.08 + 1.35 = 6.43, the whole group's price at once. |
| (b) earlier date pending | closed | "Project time of a work date is logged and drawn at the close of that date, before any line of a later date is drawn" makes it non-producible, the same premise P2 uses. |
| (c) second SOW, same level and date | closed **by reintroducing N-6b** | See N-6c. |
| O-13 | closed | The project docstring now describes a group or a group's undrawn part. |

### findings (revision_7, charter)
- **N-6c SOURCE-FACTOR RED (D.21; one object, two prices — the N-6b class, regressed).** P6 now scopes "a group … on a date and level that no other statement of work logs block-routed time at". Otherwise "the block-routed lines of a date and level that two or more statements of work log keep the standard minutes rule, line by line, … the standard conversion … and the standard time-band precedence".
  - **The price depends on a sibling.** Whether a group gets the schedules depends on another engagement's log. Probe on task 1's world: an architect line on a second T&M SOW (SOW-337400) logged 2026-10-15. The identical SOW-337412 architect group (165 after-hours min), which alone draws 5.08 h, drops out of scope. Base then prices it at 165/60 × 1.5 × 1.25 = 5.16 h: the whole-hour maintenance window, the SOW's 7.5% locked discount and the class rate are lost because a different project logged architect time that day. No MSP prices one engagement's time by another engagement's timesheet. That is the N-6b defect the coordinator's route ("each record's price is a function of its own attributes") was meant to remove.
  - **Knock-on: a second reading for P7.** P7's third sentence now waits only on groups "that the project-time rule prices". In that world, P6 returns 0 and P7 waits on nothing for 2026-10-15. Reading 1 quotes the fee with the 165-min line undrawn: 340.85 on task 1's figures. Reading 2 first draws the line under the base rule, which every block-routed line still falls under, and quotes a lower fee. The charter does not fix which.
  - Charter-level. Neither world has two SOWs on one date and level.
- **Observations:** O-1, O-10 and O-12 stand.

### closing_checklist (revision_7)
- Revealed after every revision_7 section was on disk. See the task files.
- Round-6 REDs: N-7c (a) and (b) closed; O-13 closed. N-7c (c) is closed only by making the scope sibling-dependent, which reopens the N-6b class as N-6c (member: P6, plus the knock-on on P7's third edge). No other policy is a member.
- Regressions: N-6c is a regression of N-6b. Nothing else regressed.
- Gates were not re-run by the auditor; the coordinator snapshot @ 10:29:28 (7/7 rc=0) stands.

VERDICT revision_7: task0=PASS task1=PASS charter=N-6c

## revision_8

### charter_global_frozen (revision_8)
- **Gate:** the worklog's last line is exactly `REWORK round 8: gates 7/7 green`. No revision_8 text existed before this run. The reworker's claims are the "round 8 claims" block.
- **Snapshot:** I executed `/tmp/erl0069_coord/snapshot.sh prepaid_service_hours 8`; output @ 2026-10-18T11:36:31. All 7 gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- **Hashes:**
  - `r8/0.view.json` 85f79b2f…5483 — unchanged.
  - `r8/1.view.json` 235209c8…9837 — unchanged.
  - `timebank.extended.yaml` 8eb32815f8725345c216d293badf4f72ad66b345f9477d094afc290d0cb99f06 — changed.
  - `task_tools.py` 31275c1d…b1cb — unchanged.
- Checked before the reveal; not blind.

### changed checks (revision_8)
- **Mechanical sweep:** clean on all 7 policies.
- **Tasks recomputed on the r8 charter, identical to revision_7:**
  - Task 0: 2.82 / 1.55 / 2938.80.
  - Task 1: 2.36 / 6.47 / 5.08 / 316.23.
  - All baselines, skip runs and after-write probes are the same, and seeded project draws reproduce.
  - Task 1 is in P6's scope: one live T&M engagement, 96f7597d, in_progress.
- **P6 scope:** "a block that is the TimeBank route of exactly one time-and-materials statement of work, meaning the client holds exactly one time-and-materials engagement whose status is signed, in_progress, on_hold or pending_acceptance". Any other client's project time stays "wholly and line by line" under the restated base minutes, conversion and band.
  - P7's third sentence names the same set ("one signed and not yet accepted, closed or cancelled") and says that for any other client "the extension fee does not wait on project time".
  - The late-line probe still gives the 1.35 further draw.

### round-7 RED closure (revision_8)
- **N-6c closed.**
  - Scope is a fixed contract attribute read from engagement records, never from a timesheet line.
  - Inside scope every group is priced from its own lines and the one SOW; all block-routed time is on that SOW, so date + level name the group and every group is reached.
  - The P7 knock-on is settled by the explicit "does not wait" clause.
- **O-14 (observation, not a RED):** a probe that adds a second live T&M engagement with no logged time takes the block out of scope, so the SOW-337412 group would draw base 5.16 h instead of 5.08 h. This is the coordinator's "dedicated project block" construct: a fixed holding attribute, not a sibling's timesheet. It is a coherent commercial program, and I do not find it unreal under the skill's realism test.

### replaced_by tail sweep (revision_8; every overwrite, as asked)
- **Clean:**
  - P1 price: the fall-back is restated, including half-up to the cent.
  - P7 fee: the rounding and the rolled-out restriction are restated.
  - P2 travel: the superseded clause concerns travel only, and the tail keeps every other draw on its own rule.
  - P6 minutes: out-of-scope time keeps "its recorded minutes rounded up to billing_increment_minutes".
  - P3s/P4/P5 minutes: every remote/onsite draw is in one of these scopes, so no in-force minimum is dropped.
- **N-9 SOURCE-POLICY RED (XF C.16) — band and conversion tails drop in-force content of the retired base sentences.**
  - **Band tails (P3s, P4, P5, P6).** Each ends with "every other draw … keeps the standard time-band precedence of holiday, emergency, after_hours and business_hours". The superseded clause's definitions are dropped:
    - "holiday on weekends and observed holidays";
    - "emergency for work dispatched outside business hours at the client's request to restore a down system";
    - "after_hours for other work outside business_hours_start to business_hours_end on business days (business_hours_days, excluding the observed_holiday_list)";
    - "only one band applies to a session".
  - **Conversion tails (P3s, P4, P5, P6).** Each ends with "keeps the standard conversion of worked minutes divided by 60 times the resource ratio times the band multiplier". The enumerations that say which ratio and which multiplier apply are dropped: "(technician_ratio, senior_engineer_ratio or architect_ratio)" and "(holiday_multiplier, emergency_multiplier or after_hours_multiplier, and 1 in business hours)".
  - **Demonstrated consequence.** Take an out-of-scope project line, where P6 restates base "wholly": a client with two live T&M SOWs and a 120-min senior business_hours line on Labor Day, 2026-09-07 (Monday), on a 160-hour block.
    - Under the retired base sentence it is holiday band: 120/60 × 1.25 × holiday_multiplier 1.75 = 4.38 h.
    - The only restatement in force names a precedence but no band test, so a reader of it alone draws the logged business_hours band: 120/60 × 1.25 = 2.50 h.
    - The base sentence is shown as superseded by all four overwrites, so nothing else carries the definition.
  - Charter-level. Neither world has out-of-scope project time or such a holiday line.
- **Observations:**
  - O-15: P7 "does not wait on project time" for out-of-scope clients. Due base-priced project draws are then outside this difficulty's policies, which is the stated reading.
  - O-1, O-10 and O-12 stand.

### closing_checklist (revision_8)
- **Reveal and match.** GT was opened at 11:38:29Z, after every revision_8 section was on disk. Both tasks match figure for figure.
- **Round-7 REDs.** N-6c is closed.
- **Replaced_by tail sweep.** New finding N-9. Its members are the band and conversion tails of P3s, P4, P5 and P6. No other overwrite drops in-force content.
- **Regressions.** None.
- **Gates.** I did not re-run them. The coordinator's snapshot at 11:36:31 (7/7 rc=0) stands.

VERDICT revision_8: task0=PASS task1=PASS charter=N-9

## revision_9

### charter_global_frozen (revision_9)
- **Gate:** the worklog's last line is exactly `REWORK round 9: gates 7/7 green`. No revision_9 text existed before this run. The reworker's claims are the "round 9 claims" block.
- **Snapshot:** executed `/tmp/erl0069_coord/snapshot.sh prepaid_service_hours 9`; output @ 2026-10-18T11:55:02. All seven gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- **Hashes:** `r9/0.view.json` 85f79b2f…5483 and `r9/1.view.json` 235209c8…9837 are unchanged. `timebank.extended.yaml` c7c33eec6f020a4f5820f075a752427b72106429fb0b8979bbbcdd96e0c8c91e is changed. `task_tools.py` 31275c1d…b1cb is unchanged.
- Checked before the reveal; not blind.

### checks (revision_9)
- Mechanical sweep is clean on all 7 policies.
- Tasks recomputed on the r9 charter:
  - task 0: 2.82 / 1.55 / 2938.80;
  - task 1: 2.36 / 6.47 / 5.08 / 316.23;
  - every factor baseline is identical to revision_8. The change is text-only, as claimed.
- **N-9 closed.** A word check of all eight conversion and band tails (P3s, P4, P5, P6) finds every in-force term of the retired base sentences:
  - the ratio enumeration (technician / senior_engineer / architect);
  - the multiplier enumeration (holiday / emergency / after_hours, and 1 in business hours);
  - "divided by 60" and "rounded half up to draw_rounding_hours";
  - "holiday on weekends and observed holidays", the emergency dispatch test, the after-hours test against business_hours_start/end on business_hours_days excluding the observed_holiday_list;
  - "only one band applies to a session, in that order of precedence".
  - Under these tails, the Labor Day probe is 4.38 h.

### findings (revision_9, charter)
- **N-10 SOURCE-POLICY RED (XF C.17; sibling exclusion) — the conversion and band tails sweep travel entries into the base rules.**
  - **The sibling lists leave travel out.** Each of the eight tails names its siblings as "an installation visit, a remote session and a project time line" (or the matching set), then says "every other draw keeps the standard conversion: converted block hours equal worked minutes divided by 60, times the resource ratio … times the band multiplier …" and "every other draw keeps the standard time band: holiday on weekends and observed holidays, …". Travel entries are not named. The minutes tails do name "a travel entry".
  - **So the tails contradict P2's travel rule.** Read literally, they put travel under base conversion and base band, against P2: "For travel to the client's site … the travel is figured under the travel schedules below … The travel entry is recorded in the band whose multiplier the dispatch schedule applied".
  - **Demonstrated consequence, band.** A Saturday onsite visit drawn in the holiday band:
    - P2 multiplies its trip by after_hours_multiplier and records the entry `after_hours`;
    - the band tails record a weekend draw `holiday`.
    - The tool's scored `time_band` argument has two readings.
  - **Demonstrated consequence, hours.** A travel entry carries worked_minutes 0. "Converted block hours equal worked minutes divided by 60 …" gives 0 h, while P2 gives the schedule figure (1.55 h on task 0's world).
  - **Scope and history.**
    - Charter-level: task 0's trip date 2026-10-14 is a weekday emergency, which both readings record as `emergency`. The hours reading is the strained one, and gold is not moved.
    - The defect is pre-existing: the sibling lists have lacked travel since round 2, and round 8's precedence-only tails had the same gap. I missed it in revisions 2-8. Restoring the full base text this round makes the conflict explicit, and nothing else changed.
- Observations O-1, O-10, O-12, O-14 and O-15 stand.

### closing_checklist (revision_9)
- Reveal at 11:56:18Z, after every revision_9 section was on disk. Both tasks match GT figure for figure.
- Round-8 RED N-9 is closed.
- New in this round: N-10, a pre-existing sibling-exclusion gap in the conversion and band tails of P3s, P4, P5 and P6, which leave travel entries out. Revisions 2-8 missed it. No other member exists: every minutes tail names travel, and P1, P2 and P7 retire different clauses.
- Regressions: none.
- Gates were not re-run by the auditor. The coordinator's snapshot at 11:55:02 (7/7 rc=0) stands.

VERDICT revision_9: task0=PASS task1=PASS charter=N-10

## revision_10

### charter_global_frozen (revision_10)
- **Gate.** The worklog's last line is exactly `REWORK round 10: gates 7/7 green`. No revision_10 text existed before this run. Claims: the "round 10 claims" block.
- **Snapshot.** Executed `/tmp/erl0069_coord/snapshot.sh prepaid_service_hours 10`; output @ 2026-10-18T12:28:51. All seven gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- **Hashes.**
  - `r10/0.view.json` 85f79b2f…5483 and `r10/1.view.json` 235209c8…9837 — unchanged.
  - `timebank.extended.yaml` da91795ddc650b45cc85c550b933ca09f4ebd060083e6e0e70e756f5657c16b5 — changed.
  - `task_tools.py` 7da19bcdb159f2fab80d5f704a063e30c930c08bf8667c18deb34be5c03f3bbc — changed. The claims block does not list this; the change is the travel `time_band` docstring.
- **Status.** Checked before the reveal; not blind.

### checks (revision_10)
- **N-10 closed.** All eight conversion and band tails (P3s, P4, P5, P6) now list "… and a travel entry are figured under their own schedules / take their bands from their own rules" before "every other draw keeps the standard …".
  - All 14 scoped overwrites name every sibling case (service visit, remote session, installation visit, project time, travel); P2's tail keeps every non-travel draw on its own rule.
  - Every replaced_by is still verbatim in its rule.
- **Tool module.**
  - The travel docstring now says weekend and holiday trips are recorded `after_hours`, and that `holiday` is never used for a travel entry. This matches P2's dispatch schedule (after_hours or holiday band -> after_hours_multiplier -> recorded after_hours), so the scored `time_band` has one reading.
  - Formats only; no example values; no sequencing words. The bodies still record the band they are passed. uuid8s unchanged; the events written are unchanged (XF 24 PASS).
- **Recompute.** Mechanical sweep clean on all 7 policies. Tasks recomputed on the r10 charter, identical to revision_9: task 0 2.82 / 1.55 / 2938.80; task 1 2.36 / 6.47 / 5.08 / 316.23; every factor baseline the same.

### findings (revision_10, charter)
- None. Observations O-1, O-10, O-12, O-14 and O-15 stand (none is a RED).

### closing_checklist (revision_10)
- **Reveal.** At 12:30:22Z, after every revision_10 section was on disk.
- **Match.** Per-task files 0.md and 1.md each carry a PASS comparison. Both tasks match GT figure for figure.
- **Round-9 RED.** N-10 is closed.
- **New defects.** None found.
- **Regressions.** None.
- **Scope.** Task 0 = {P3s, P2, P1}; task 1 = {P4, P5, P6, P7}. The scopes are disjoint and together cover all 7 extended policies.
- **Trees.** Task 0 has n=2 prerequisite problems and 3 value_input edges; task 1 has n=3 and 3. Each root is the customer's own write, and the whole graph is acyclic.
- **Computations.** Every computation has 4-6 factors, with at least 2 parameter factors and at least 1 method factor. Each task has at least one multi-source factor and at least one cross-difficulty factor. Every factor bears weight against an honest baseline, and each all-baseline figure differs from gold.
- **Gates.** Not re-run by the auditor. The coordinator snapshot @ 12:28:51 (7/7 rc=0) is the final-form gate run.

VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN

## revision_11

### charter_global_frozen (revision_11)
- **Gate.** The worklog's last line is exactly `REWORK round 11: gates 7/7 green`. No revision_11 text existed before this run.
- **Inputs read.** `audits/render_source/prepaid_service_hours/render_r1.md` (renderer STOP report: items 1-4 and a travel note), read in full, then the "round 11 claims" block.
- **Snapshot.** I executed `/tmp/erl0069_coord/snapshot.sh prepaid_service_hours 11`; output @ 2026-10-18T13:41:51. All seven gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- **Hashes.**
  - `r11/0.view.json` 85f79b2f…5483 and `r11/1.view.json` 235209c8…9837 — unchanged.
  - `timebank.extended.yaml` 0df7ce6c85ea473734dc1a6adb5993a0e75bac6f0629c3a8c4d01455b4fea698 — changed.
  - `task_tools.py` 7da19bcd…3bbc — unchanged.
- **Status.** Checked before the reveal; not blind.
- **Auditor miss disclosed.** Since revision_2 I had accepted the A.3/A.4 assembly sentences of P3s, P4 and P7 (and later P6) because they fix a non-commuting order. Under XF A.3, naming factor quantities in an assembly sentence is a defect even when order must be fixed: the order can be stated by kind of operation. The renderer was right; revisions 2-10 missed items 1-4.

### renderer items — closure (revision_11)
| item | status | evidence |
|---|---|---|
| 1 P3s assembly | closed | "…in this order: floors on the minutes first, then a weighting of part of the minutes, then the multipliers and the ratio, which multiply one another with no order between them; …". Generic by operation; matches compute `(MX(basis,floor) + MN(…,split)·(e/a−1))/60·band·ratio·cp`. |
| 2 P4 assembly | closed | Same generic sentence; matches compute. |
| 3a P6 assembly | closed | "replacements of the minutes first, then the multipliers and the ratio …, a multiplier that a schedule applies to part of the minutes leaving the rest at 1". Generic. |
| 3b P6 band window | closed | `pj_window` and `pj_band_extra` are now `project_band_rate` bindings. The window wording sits in the band schedule's own sentence ("has those after-hours minutes, rounded up to the next multiple of 60, multiplied by after_hours_multiplier"). |
| 3c P6 selection by factor content | closed | `pj_p_*` is now `pj_s_* != None and (business + after-hours logged minutes) > recorded worked minutes`, a plain logged-vs-recorded test. Rule: "A group's undrawn part is its logged minutes not yet drawn …". |
| 3 baseline vs compute | closed | baseline.rule: "draws its summed logged minutes divided by 60, at technician_ratio and with a multiplier of 1, less the block hours already drawn for it, rounded half up". With all baselines, compute is `MX(0, total/60·1·1·1 − drawn_h)` — same. |
| 4 P7 assembly | closed | "replacements of the percentage and of the value of an hour first, then additions of points to the percentage, then the multipliers of the fee …". Generic; matches compute. |
| travel note | closed | P2: "A block whose size carries onsite_trip_hours of zero draws no travel, its trip being zero hours whatever the schedules below select". |

### class sweep (all policies, all four classes named in the brief)
- **Assembly sentences naming factor quantities.** None left. P1 ("Every percentage that one of the schedules below grants …"), P2, P5 and the four rewritten sentences are all generic.
- **Single-factor definitions in plain bindings.**
  - Mechanical check: a plain binding read by exactly one factor and by nothing else. Only hit: P5 `in_billable_basis`, read by `install_unit_minutes`.
  - Not a member: it is the standard method's quantity. baseline.rule reads "An installation visit draws its billable minutes, rounded up to billing_increment_minutes and never fewer than minimum_draw_minutes_onsite …", and it is the factor's baseline binding. XF A.5 allows the baseline paragraph to define what the standard method uses.
- **Plain selections depending on factor content.**
  - No plain binding reads a factor binding (XF 26a: no hits).
  - No plain binding uses a factor-tier parameter (no hits once baseline params are excluded).
  - The P2/P3s/P4/P5/P6 selectors read ledger dates, minutes, tickets and engagement records only.
- **Baseline words vs compute.** Each baseline.rule was re-derived against compute under every factor's baseline: P1 0%; P2 onsite_trip_hours ×1; P3s/P4/P5 rounded minutes with their minimum, technician, ×1; P6 as above; P7 extension_fee_pct × balance × hourly_rate. All match. The all-baseline figures equal the baseline wording: 3160.00, 1.00, 1.25, 0.75, 4.25, 2.75, 660.45.
- **Mechanical sweep.** Clean on all 7 policies.
- **Tasks recomputed.**
  - task 0: 2.82 / 1.55 / 2938.80;
  - task 1: 2.36 / 6.47 / 5.08 / 316.23;
  - factor baselines unchanged;
  - after the writes every draw policy returns 0;
  - seeded project draws reproduce with their recorded worked_minutes (255 / 345 / 420 / 300 / 240 = logged minutes).

### findings (revision_11, charter)
- **N-11 SOURCE-POLICY RED — P6 prescribes a ledger row the schema forbids, and P7 waits on it.**
  - **P6 rule:** "a part whose block hours come to zero, because the group's whole-hour window already covers it, being drawn as a zero-hour draw that records its minutes".
  - **Schema:** `db_schema.json` `timebank_hours_ledger.hours` is "hours, 2 decimal places, positive".
  - **P7's third sentence** waits until there is "no part of any group left undrawn".
  - **Probe on task 1's world after the gold writes.** A 15-minute architect after-hours line is logged for 2026-10-15. It falls inside the already-rounded 180-minute window. P6 figures the architect group with result 0.00 h.
    - Reading 1 posts a 0.00 h project-work draw recording 15 minutes. That row violates the schema.
    - Reading 2 posts nothing, because a draw's hours must be positive. The group then keeps an undrawn part, P6 figures it on every pass, and P7's third prerequisite can never be satisfied.
  - Charter-level; neither world has such a line. New in round 11: it was introduced with the logged-vs-recorded undrawn-part rule, which replaced the round-7 hours-based part.
- **Observations.** O-1, O-10, O-12, O-14 and O-15 stand.
- **N-12 SOURCE-POLICY RED (rule vs tool contract; recording convention) — P6 records logged minutes, while its tool and its siblings record the minutes drawn for.**
  - P6: "… with the group's logged minutes not yet drawn as its worked minutes".
  - `post_project_time_draw_e9603a55`: "the minutes the group or its undrawn part is drawn for".
  - The P6 minutes schedule: "drawn with those after-hours minutes in whole hours".
  - Remote, service and installation tools: "drawn for" = the priced minutes (remote: "after rounding and any floor").
  - Demonstrated in task 1: gold worked_minutes 165 against the contract reading 180 (see 1.md).

### closing_checklist (revision_11)
- **Reveal and match.** Revealed at 13:43:58Z, after every revision_11 derivation was on disk. Task 0 matches and passes. Task 1's values match GT; its scored worked_minutes carries the N-12 second reading.
- **Renderer items.** Items 1, 2, 3a, 3b, 3c, the baseline mismatch, item 4 and the travel note are all closed.
- **Class sweep.** No remaining member of any of the four classes (P5 `in_billable_basis` is a baseline quantity, not a member).
- **New in revision_11.** N-11: a zero-hour project draw forbidden by the ledger schema, which P7 waits on. N-12: the worked_minutes convention — rule vs tool contract — with its task-1 consequence R11-1.1.
- **Regressions.** None in values. The project draw's worked_minutes moved from 180 to 165, which introduces N-12.
- **Gates.** Not re-run by the auditor; the coordinator snapshot @ 13:41:51 (7/7 rc=0) stands.

VERDICT revision_11: task0=PASS task1=RED[R11-1.1] charter=N-11,N-12

## revision_12

### charter_global_frozen (revision_12)
- **Gate:** the worklog's last line is exactly `REWORK round 12: gates 7/7 green`. No revision_12 text existed before this run. The reworker's claims are the "round 12 claims" block.
- **Snapshot:** I ran `/tmp/erl0069_coord/snapshot.sh prepaid_service_hours 12`; output @ 2026-10-18T16:14:04. All seven gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- **Hashes (all four changed):**
  - `r12/0.view.json` 755398184e0901021005365487bd2ffd4eef75c34c40674b06a3e1f37f2a953d
  - `r12/1.view.json` af2fd891649c570fe55f6273b53f1164fc84a1dfc83c6f91cc7ade4efc385525
  - `timebank.extended.yaml` 4bf1e7bb716bcf4f42be955ad478971fa56246d50cc582fa7fa1c90d7b6020a0
  - `task_tools.py` f7013dc51432fa1b9ebf55f7d3a97150fb10f9e2c09c5ff0efc1b70aca37239c
- **Read domain, extended for this round:** to re-price the cross-product rows against the published docs, as the brief asks, I read the published KB under `docs/{managed,hardware,project}/`. That is the rollout-visible KB, which includes other difficulties' extended policies. No sibling `tasks/` directory was read.
- **Not blind:** checked before the reveal.

### round-11 RED closure (revision_12)
- **N-11 closed.**
  - P6 adds the premise "Project time of a work date is logged in full at the close of that date, before any of that date's groups is drawn …; no line is logged for a date after that date's groups are drawn".
  - The done test is a plain draw-exists check (`pj_dn_* == 0`), and the zero-hour draw clause is gone.
  - P7's third sentence waits on "the project-work draws of every group" of the latest date. It no longer mentions undrawn parts, consistent with the premise.
  - project.yaml sets no logging time that this premise contradicts.
- **N-12 closed.**
  - P6: "with the minutes the group is drawn for, after the floor or whole-hour rounding the minutes schedule applies, as its worked minutes".
  - Tool: "the minutes the group is drawn for, after any floor or whole-hour rounding the rule applies".
  - These now agree, and match the sibling tools' "drawn for".
  - The seeded project draws reproduce with worked_minutes 255 / 345 / 420 / 300 / 240.

### cross-product re-pricing — one exhaustive pass (both worlds, every ClearPath, hardware and project row)
| row | published rule applied | check |
|---|---|---|
| T0 ClearPath Standard seat_rate 123.38 | managed_ext_auto_renewal_rate (auto_renew true, 7th renewal 2026-07-15) | cap 5 − 1 (≥3 renewals) = 4%; price protection (b) (live ≥ 60 months, never suspended) gives the lowest of 128.32 / list 124.00 / 125.85, i.e. 124.00. Net adjustment −0.5%: tickets opened in the 12 months before renewal number fewer than the 34 seats. Seat growth is nil: expiring contracted seats are 32, the seat count on 2025-07-14, and the 10%-above seat would be 36. No late fees, no service credits. 124 × 0.995 = 123.38 ✓. The expiring rate in steady state is the same 123.38, so the May–July fees are consistent. |
| T0 monthly fees 2026-05..10 = 4194.92 | managed_ext_current_month_fee (current month at posting; no seat change in month; no F3/BP) | 34 billed seats (floor 29) × 123.38 = 4194.92. No credits apply: no Continuum, CSP or Sentinel holding, and fewer than 40 seats for the volume break ✓. ACH payments ✓; balance 4194.92 = October fee ✓. |
| T0 seat ledger 30+2+1+1 = 34 | managed_seat_changes_and_proration | count ✓; prorations fall before the seeded window ✓. **The onboarding tickets referenced (SB-1876402, SB-2155617, SB-2201384) are absent from managed_tickets — see R12-S1.** |
| T0 tickets (billable minutes, classes, routes, SLA) | managed_billable_labor_rates, managed_sla_response_credit | minutes on 15-min steps with minimums ✓; after-hours class against Standard coverage 07-19 ✓; route timebank with the block balance covering ✓; first responses within target (P2 SB-2306631: 20 min of 120) ✓; no credit due ✓. |
| T1 ClearPath Professional seat_rate 148.26 | managed_ext_auto_renewal_rate (renewal 4, 2026-02-24) | 4% cap; protection (b) gives the lowest of uplifted / 149.00 / +2%, i.e. 149.00. Adjustment −0.5% (2 tickets in the prior 12 months against 58 seats). Seat growth nil (expiring contracted 55; the 10%-above seat would be 61). 149 × 0.995 = 148.26 ✓. |
| T1 monthly fees 2025-12..2026-10 = 8542.74 | managed_ext_current_month_fee | 58 × 148.26 = 8599.08; volume break: seats 40–58 (19 × 2.0 = 38) ÷ 58 = 0.6552% off, giving 8542.74 ✓. ACH payments ✓; balance ✓. |
| T1 hardware HQ-604418 deposit 3357.47 / final 15295.13 | hardware_ext_endpoint_approval_deposit (Staged Endpoint, within the 50000.00 limit) | ClearPath live ≥ 36 months, so build 3 (share of quote total). Professional share 20%; no arrears points; managed-spend relief: 148.26 × 58 = 8599.08 is 0.461 of 18652.60, so −2.0. 18% × 18652.60 = 3357.47 ✓; final = 18652.60 − 3357.47 = 15295.13 ✓. Quote: markup 15 − 3 = 12%, 1444.80 ✓; total 18652.60 ✓; PO after the deposit was paid ✓. |
| T1 project SOW-337412 rate_discount 10.5 | project_ext_sow_signature_rate_lock (T&M signed 2026-07-28) | seat scale 58 seats: 0.5; tenure > 1095 days: 1.0; commitment (12-month term): 0; managed (Professional, Advanced 7.5): 7.5; prepaid hours (160 granted 2025-12-09): 1.5. Sum 10.5 ✓. Class Advanced (64000 within 50000–149999.99) ✓. |
| T1 project deposit 7160.00 | project_ext_signature_deposit | estimated fees 64000 × 89.5% = 57280. Rate 25 − 5.0 (six ACH payments after 2026-01-28) − 10.0 (Professional, no late fee) + 0 (no open balance at 07-28) + 0 (no hardware late fees) + 2.5 (start 20 days after) = 12.5%. Planned duration 95 days, so the basis is the estimated fees. 57280 × 12.5% = 7160.00 ✓. Paid 07-31; kickoff max(07-31 + 10 business days = 08-14, scheduled 08-17) = 08-17 ✓. |
| T1 project work logs | project_tm_billing | minutes on 15-min steps ✓; route timebank (Advanced timebank_draw_allowed) ✓; no T&M invoices, since all time is settled from the block ✓. |
| T1 tickets | as for T0 | ✓. SLA: P2 responses 19 / 11 / 15 min, and after-coverage ones count 0 coverage minutes, against 60 ✓; P1 SB-2311409 is after coverage ✓. |
| T1 block order form b83acc45, 20520.00 | timebank_ordering_and_pricing | 21600 × 0.95 ✓. |
- **R12-S1 SOURCE-FACTOR RED (XF D.20/25; supporting records):** five seat additions reference onboarding tickets that are not seeded. Task 0: SB-1876402 (2023-03-06), SB-2155617 (2025-09-08), SB-2201384 (2026-03-02). Task 1: SB-1602771, SB-2003358.
  - managed.yaml: "Seats are added … under a service desk user_onboarding ticket …; A new-user onboarding is ready on the requested start date only when the onboarding ticket was opened at least new_user_lead_business_days business days before that date". The ticket is the servicing record that dates each seat's effective_date.
  - The seat_count these rows support is read by P1's seat schedule (task 0), and by hardware managed-spend relief and the project seat-scale component (task 1).
  - No value moves: the counts are right, and only the servicing rows are missing.
  - This has been present since round 2; I missed it in revisions 2–11.

### other changed checks (revision_12)
- **Mechanical sweep:** clean on all 7 policies.
- **Recomputed gold:**
  - Task 0 is unchanged: 2.82 / 1.55 / 2938.80.
  - Task 1 moves because rate_discount 10.5 ≥ 10 now takes discount_rate_high 0.9: P6 4.81, P7 325.87 (see 1.md).
- **Tool module:** only the project worked_minutes docstring changed. No values, no sequencing words; uuid8s and events unchanged.

### closing_checklist (revision_12)
- **Reveal and match.** Revealed at 16:19:49Z, after every revision_12 section was on disk. Both tasks match GT figure for figure; task 1's moved gold (4.81 / 180 / 325.87) equals my re-derivation.
- **Round-11 REDs.** N-11 and N-12 (R11-1.1) are closed.
- **Cross-product pass.** Every ClearPath, hardware and project row in both worlds reproduces under the published rule that governs it. The one remaining class member set is R12-S1: five seat additions whose onboarding tickets are unseeded (task 0: three; task 1: two).
- **Charter.** No charter-level finding remains.
- **Gates.** I did not re-run them; the coordinator snapshot @ 16:14:04 (7/7 rc=0) stands.

VERDICT revision_12: task0=RED[R12-0.1] task1=RED[R12-1.1] charter=CLEAN

## revision_13

### charter_global_frozen (revision_13)
- **Gate and inputs.** The worklog's last line is exactly `REWORK round 13: gates 7/7 green`. No revision_13 text existed before this run. Claims are the "round 13 claims" block.
- **Snapshot.** Executed `/tmp/erl0069_coord/snapshot.sh prepaid_service_hours 13`; output @ 2026-10-18T16:37:00. All seven gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- **Hashes.**
  - `r13/0.view.json` 58534a97d9824f64fa65f3c72d86fd33b166806370c21da94003a2ae2b15eec3
  - `r13/1.view.json` 2e39343c46eac1309753907026dc2919585ddd7123436a251d46c26bb07e63e1
- **Seed-only round confirmed.** `timebank.extended.yaml` 4bf1e7bb716bcf4f42be955ad478971fa56246d50cc582fa7fa1c90d7b6020a0 and `task_tools.py` f7013dc51432fa1b9ebf55f7d3a97150fb10f9e2c09c5ff0efc1b70aca37239c are unchanged from revision_12. The revision_12 charter and tool conclusions carry forward on these hashes.
- **World delta r12 -> r13.** Only additions: 9 managed_tickets rows in task 0 and 6 in task 1, each an opened / first_response / resolved set for the five onboarding tickets. Nothing else changed, and the personas are unchanged.

### R12-S1 closure (onboarding tickets, against the managed published rules)
| ticket | opened | resolved = seat effective | check |
|---|---|---|---|
| T0 SB-1876402 (+2) | 2023-02-27 Mon 10:05 | 2023-03-06 Mon 09:10 | user_onboarding, P3, portal; first response 35 min (P3 target 240); scope covered. Remote business-hours labor on Standard (helpdesk_remote_included true, inside 07-19) -> included; 60 min on 15-min steps. Opened 5 business days before the effective date (lead 3) -> ready on the requested date ✓ |
| T0 SB-2155617 (+1) | 2025-09-02 Tue 13:20 | 2025-09-08 Mon 09:25 | same pattern; 30 min; 4 business days ≥ 3 ✓ |
| T0 SB-2201384 (+1) | 2026-02-24 Tue 11:15 | 2026-03-02 Mon 09:05 | same; 30 min; 4 business days ≥ 3 ✓ |
| T1 SB-1602771 (+5) | 2022-06-07 Tue 14:10 | 2022-06-13 Mon 10:30 | Professional (lead 2); included; 150 min ✓ |
| T1 SB-2003358 (+3) | 2025-04-01 Tue 09:40 | 2025-04-07 Mon 09:50 | included; 90 min ✓ |
- Knock-on checks: re-priced figures that read tickets do not move.
  - The renewal service-intensity counts become 6 tickets < 34 seats (T0, window before 2026-07-15) and 3 < 58 (T1, window before 2026-02-24), so the −0.5% stands and 123.38 / 148.26 are unchanged.
  - The timebank selectors filter labor_route timebank, so the included tickets are not reached.
  - No SLA credit is due (P3).
  - Proration of each seat addition falls before the seeded billing windows.

### exhaustive referenced-record pass (both seeds)
- Every reference was resolved mechanically:
  - foreign keys: customer_id, managed_agreement_id, timebank_block_id, hardware_order_id, project_engagement_id, managed_seat_change_id, original_ledger_entry_id, counterpart_block_id, rollover_source_block_id;
  - ticket_number on every non-ticket row;
  - sow_number on ledger and log rows;
  - the invoice_number of every payment, against an invoice in the same billing table.
- Result: 152 references in task 0 and 242 in task 1, with **0 dangling**.
- Every ticket carries its opened and first-response milestones. Every timebank-routed resolution has its draw, except the tasks' own pending prerequisites (T0 SB-2306631; T1 SB-2311409, SB-2310275). Every block-routed log has its draw, except T1's pending 2026-10-15 line.
- Values recomputed on r13, all identical to revision_12:
  - task 0: 2.82 / 1.55 / 2938.80, skips 3002.00 / 3002.00 / 0;
  - task 1: 2.36 / 6.47 / 4.81 / 325.87, skips 337.31 / 357.24 / 349.19;
  - every factor baseline is the same;
  - after the writes, every draw policy returns 0.

### findings (revision_13)
- None. Every ClearPath, hardware and project row reproduces under its published rule (revision_12 table, unchanged), and the referenced-record class has no remaining member.

### closing_checklist (revision_13)
- **Reveal and match.** Revealed at 16:38:32Z, after every revision_13 section was on disk. Both tasks match GT figure for figure.
- **REDs.** R12-0.1 and R12-1.1 are closed.
- **Referenced records.** No dangling reference remains, and no referenced-record class member remains.
- **Charter and tools.** Unchanged, so their CLEAN verdict carries forward.
- **Final-form checklist.**
  - Scopes are disjoint and complete.
  - Trees: one to three prerequisites each, with enough value_input edges. Each root is customer-owned, and the graph is acyclic.
  - Factors: four to six per computation, with at least two parameter and one method factor. Each task has multi-source and cross-difficulty factors. Every factor bears weight, and every all-baseline figure differs from gold.
  - Gates: the coordinator snapshot @ 16:37:00 shows 7/7 rc=0. I did not re-run them.

VERDICT revision_13: task0=PASS task1=PASS charter=CLEAN

## revision_14

### charter_global_frozen (revision_14)
- **Gate:** the worklog's last line is exactly `REWORK round 14: gates 7/7 green`. No revision_14 text existed before this run.
- **Inputs read:**
  - the "round 14 claims" block;
  - `audits/policy_kb/prepaid_service_hours/_difficulty.md` revision_1 items SEED-MGB-0, SEED-MGB-1 and SEED-SCOPE-HOWTO (lines 19-21).
- **Snapshot:** executed `/tmp/erl0069_coord/snapshot.sh prepaid_service_hours 14`; output @ 2026-10-18T17:52:48. All seven gates rc=0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- **Hashes:**
  - `r14/0.view.json` f9838f76265b7fdf702908fdcc1215e3242990871ee3f2e05ae6fa1a57ed3b8e
  - `r14/1.view.json` 31ec2ff91171b95a09000389d9a1b31a767e75cc16b3ae43a7f1f2c3a0432a56
- **Seed-only round, confirmed.** `timebank.extended.yaml` 4bf1e7bb…20a0 and `task_tools.py` f7013dc5…239c are unchanged, so the charter and tool conclusions carry forward.
- **World delta r13 -> r14:** six ticket rows changed. issue_category moved from how_to to service_request on the opened, first-response and resolved rows of SB-2275518 (task 0, P4) and SB-2297262 (task 1, P3). Nothing else changed.

### KB-audit source items (revision_14)
| item | verdict | evidence |
|---|---|---|
| SEED-MGB-0 (T0 pre-renewal fees 2026-05..07 at 123.38) | **closed; the rows were already correct** | Term-by-term under managed_ext_auto_renewal_rate, from signing (Standard, 12-month initial term from go-live 2019-07-15, initial rate 124.00):<br>• Renewal 1: first renewal of a 12-month term, so the full 5% cap applies. Live < 60 months, so rule (c): min(130.20, 124.00) = 124.00; ticket-volume −0.5% gives **123.38**.<br>• Renewals 2-5: (c) min(129.55, 124.00) = 124.00, −0.5%, gives 123.38. Renewal 5 ends at 59 live months.<br>• Renewals 6-7: (b) lowest(4% uplift, 124.00, +2% = 125.85) = 124.00, −0.5%, gives 123.38.<br>• Seat growth never reaches the 10%-above seat (contracted 30 -> 32 -> 32 against covered ≤ 34). No late fees and no service credits.<br>So the expiring rate of the term in force on 2026-05/06/07-01 is 123.38, and 34 × 123.38 = 4194.92 is right. The KB note's 120.96 is not reached by any term chain (120.96 × 1.02 = 123.38 omits the −0.5% net adjustment, and no prior term gives 120.96). |
| SEED-MGB-1 (T1 fees 8542.74) | **closed; the rows were already correct** | 8542.74 is the published current-month fee: 58 × 148.26 = 8599.08 less the volume price break, seats 40-58 at 2.0 = 38 ÷ 58 = 0.6552% (revision_12 table). The KB note left this factor out.<br>Professional term chain (initial 36 months from 2020-02-24 at 149 × 0.95 = 141.55):<br>• Renewal 1: first renewal of a 36-month term, cap − 2 = 3%, giving 145.80. Adjustments: −0.5% ticket volume and −0.0091% seat growth (seat 55 is ≥ 10% above contracted 50), giving 145.06.<br>• Renewal 2: full cap gives 152.31; min with 149.00 = 149.00; −0.5% gives 148.26.<br>• Renewal 3: (c) at 59 months gives 148.26.<br>• Renewal 4: (b) gives 148.26.<br>So the pre-renewal months (2025-12..2026-02) run at 148.26 as well, and every fee is 8542.74. |
| SEED-SCOPE-HOWTO | **closed** | Both tickets are now service_request, billable_out_of_scope, remote business hours, routed to the block. That is the same pattern as every other seeded billable service request; managed.yaml's scope rule covers "help desk work", and a how-to question is help-desk work, now removed. The seeded draws reproduce under P4 at their dates (SB-2275518 45 min -> 0.75; SB-2297262 45 min -> 0.75; floor minimum_draw_minutes_remote 15 instead of the how_to tier, same value). P4's how_to tier stays reachable for ClearPath Monitor clients (helpdesk_remote_included false). |

### exhaustive pass on the re-seeded rows (revision_14)
- The six changed rows are consistent with the published managed rules on category, scope, labor route, coverage class and first-response target.
- No re-priced figure reads these categories:
  - P2/P3s/P4/P5 selectors and schedules: P4's level tier reads security_concern/outage, and its floor tier reads how_to;
  - the renewal ticket-volume counts: unchanged;
  - the project and hardware rows.
- The referenced-record pass of revision_13 still holds (no rows added or removed).
- Values recomputed on r14, identical to revision_13:
  - task 0: 2.82 / 1.55 / 2938.80;
  - task 1: 2.36 / 6.47 / 4.81 / 325.87;
  - every factor baseline is the same;
  - after the writes, every draw policy returns 0.
- **O-16 (observation, not a RED; complete member list).** managed.yaml's priority rule ends "P4 is a service request, how-to question or scheduled change". It also defines priority by impact ("P3 is a single user unable to work …"), so a P3 service request reads as a request blocking a single user. No scored value reads the priority of these tickets: P4 and P3s read P1 only. Seeded service_request / user_onboarding tickets at P3:
  - task 0: SB-2240817, SB-2249362, SB-2262290, SB-2291047, SB-2303384, SB-2309118, SB-1876402, SB-2155617, SB-2201384;
  - task 1: SB-2190477, SB-2209951, SB-2219840, SB-2251190, SB-2281513, SB-2297262, SB-2310275, SB-1602771, SB-2003358.

### closing_checklist (revision_14)
- **Reveal:** 17:55:39Z, after every revision_14 section was on disk. Both tasks match GT figure for figure.
- **KB-audit items:**
  - SEED-MGB-0 and SEED-MGB-1: the seeded rows were already correct under the published renewal and current-month-fee rules. The seed checks now state the derivation, so both items are closed.
  - SEED-SCOPE-HOWTO: closed by the re-seed.
- **New defects:** none. O-16 is listed in full as an observation.
- **Charter and tools:** unchanged, so their CLEAN verdict stands.
- **Gates:** the coordinator snapshot @ 17:52:48 (7/7 rc=0) is the final-form run. I did not re-run them.

VERDICT revision_14: task0=PASS task1=PASS charter=CLEAN
