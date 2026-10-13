# Policy-task audit — seller_standing_reviews_account_actions / charter-global

## charter_global_frozen

- Auditor: independent erl-task-policy-audit agent (not the instantiating agent). Revision 1 (no earlier audit of this difficulty exists; `audits/policy_task/seller_standing_reviews_account_actions/` was created by this audit).
- Freeze time (system clock, at writing): 2026-10-11 05:15:54 UTC. Written before any task's GT was revealed; contains nothing derived from a revealed GT.
- Frozen inputs (sha256, recomputed by the auditor and equal to `.audit_views/.../HASHES.txt`):
  - `tasks/seller_standing_reviews_account_actions/standing.extended.yaml` dd1f9e9d7b2b3543338770d4e7ffc530954ad803420fa923cff65696a4971643
  - `tasks/seller_standing_reviews_account_actions/task_tools.py` aa7e1af083d680beb4b7a7e447b0e8d21a8ca40189374e0224cb6bf82fef22bf
  - `0.view.json` 6421e7ee…4a6b, `1.view.json` 440fd66e…f024f4; source task files 0.json f4525dd5…aa8, 1.json d3545f08…53e6 (hashed only, not opened).
- Permitted: `blueprint/{blueprint.yaml,db_schema.json,share_tools.py,products/*.yaml}`, the extended charter, `task_tools.py`, the two masked views (`frozen_time`, `user_scenario`, `initial_state`), the DSL primitive semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`MONTHS`, `_within`, `SUM/COUNT/LATEST/CFIELD/XCOUNT`).
- Masked (not read before freeze): `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`.
- Entry conditions (Step 0): gate snapshot `gates.r2.txt` supplied — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK (all rc=0); masked views and hashes supplied and verified. Entry conditions complete.
- Base copy: `diff` of extended lines 1-764 against `blueprint/products/standing.yaml` differs only by one trailing blank line — verbatim compatible.

### policy_conflict_scan

Six extended policies, all on `standing`:

| id | trigger | subject | target_tool (owner) | computes | prerequisite |
|---|---|---|---|---|---|
| standing_ext_clean_span_relief (CS) | state_due | standing_points_expiry | grant_clean_span_relief_513362ca (agent) | points | [] |
| standing_ext_action_plan_relief (AP) | on_request | standing_points_expiry | apply_action_plan_relief_841772f9 (user) | points | CS (value_input, state) |
| standing_ext_listing_violation_expiry (LE) | state_due | standing_points_expiry | book_listing_violation_expiry_caba69b5 (agent) | points | [] |
| standing_ext_serious_violation_step_down (SSD) | state_due | standing_points_expiry | book_serious_step_down_71a20607 (agent) | points | [] |
| standing_ext_top_performer_relief (TP) | state_due | standing_points_expiry | grant_top_performer_relief_7abd26c5 (agent) | points | LE, SSD (value_input, state) |
| standing_ext_closure_carry_forward (CF) | on_request | standing_close | close_selling_account_90945f31 (user) | carried_points | TP (value_input, state) |

- Overlapping subject: five policies write `standing_points_expiry` rows. Their eligibility is partitioned: CS only Below/Developing/Standard/Above Standard levels; TP only Top Rated/Preferred Partner; LE only listing types (listing_policy, restricted_product); SSD only serious types (intellectual_property, inauthentic_complaint, product_authenticity, review_manipulation); AP only on the seller's request. The six violation types are exactly covered by LE ∪ SSD, so the base 180-day clause (superseded by all five) has a unique replacement per type.
- Time anchors: CS "on the handling date"; TP "on the evaluation day, once that month's evaluation is recorded"; LE/SSD on the handling date by whole-month periods. No two policies set different time anchors for the same quantity.
- Terminal states: all five relief/expiry writes leave status unchanged; CF sets `closed`. Compatible with base lifecycle (`good_standing|at_risk -> closed` by user).
- Cross-category read boundaries: payout (CS, TP, CF), fulfill (AP, LE, SSD, TP, CF), selling (AP, TP, CF), all read-only, declared in `cross_category`.
- Indistinguishable rows: every one of the five tools writes the same row shape (`event_type=standing_points_expiry`, `violation_ref`, `violation_type`, `points`, no reason field). Record-visible state therefore cannot tell a clean-span relief, an action-plan relief, a listing expiry, a step-down or a top-performer relief apart; only the rules plus dates can. See findings O-3 and O-4.
- Scope exclusivity / completeness (from the graph alone, pre-reveal): the graph has two weakly connected components, {CS -> AP} and {LE, SSD -> TP -> CF}. With M=2, the natural partition is task 0 = {AP, CS}, task 1 = {CF, TP, LE, SSD}: pairwise disjoint and jointly complete. (Confirmed against each task's world in the task files; `charter_scope` itself is checked only after reveal.)

### rule_compute_equivalence

Checked binding by binding against `compute_basis` (every binding carries a verbatim sentence of its own rule) and swept back sentence by sentence.

- CS: active points, 12-month count, rate ladder, clean span `MONTHS(LATEST(...), NOW)`, span multiplier ladder, payments bonus (two XCOUNTs), tenure cap `DAYS(enrolled_date, NOW)`, order "rate x multiplier, round down, add bonus, limit to cap" — all quoted and implemented. Eligibility sentences (level set, status, active>0, three clean months, once per clean span) and the booking sentence (most points, oldest on tie) are object/eligibility rules, not compute — no empty promise in the quantity. PASS.
- AP: active points, serious active points ("on entries carrying those types"), share ladder, risk multiplier via `P('warning_points_threshold')`, stock bonus (3-month XCOUNTs), store cap via `CFIELD('selling','variant_name')`, order of operations — PASS.
- LE: `within_months=mn_period` implements "counted in whole calendar months back from the handling date"; repeat count three-way method; stock offset (CFIELD units + 6-month XCOUNT); `MX(0, …)` = "never less than zero"; sum of both types — PASS. Note `CFIELD('fulfill','units_on_hand')` returns None for a seller with no enrollment and `None > 0` would raise; the rule's "nothing for … who has no enrollment" tier is therefore unimplementable in compute (O-6; no task has such a seller).
- SSD: `sv_carried` is wrapped in `MX(0, …)`; the rule's carried-points sentence states no floor at zero — compute adds a basis of its own (O-5; no consequence in either task, carried = 8 > 0). The rule's "the rest expiring when a second period of the same length has run" and "a serious violation that has stepped down keeps its remaining points on record until its second period has run" are not implemented: compute does not exclude a violation that already stepped down (replayed on task 1's post-write world it yields a second step-down of 2), and no policy books the second-period expiry (O-5).
- TP: all ladders and the "rate x store multiplier, round down, add payments and band bonuses, limit to cap" order — PASS.
- CF: listing/serious points at closing, share (two conditions per tier), serious multiplier, payments/FBN surcharges, store cap, recent-points surcharge, round-up implemented as `int(x) + (1 if x > int(x) else 0)` — PASS.
- Factor ladders vs rule vs `decides` binding: every tier named in `factors[].ladder` is a sentence of the rule and a branch of the `decides` expression, and every branch is a stated tier, for all 27 factors. PASS.

### action_binding_and_uuids

- Six distinct `(target_tool, computes)` pairs, each claimed by exactly one policy. PASS.
- uuid8s: 513362ca, 841772f9, caba69b5, 71a20607, 7abd26c5, 90945f31 — no shared prefix/suffix, no sequence, no near-duplicate tails. PASS.
- Docstrings: no docstring names another tool or a position in a sequence of writes. Ordering words occur only about input provenance ("read from the standing record lookup before the call"), receipt values ("active points before and after") and, in `apply_action_plan_relief_841772f9`, the seller's off-platform act ("applies … after working through the account health action plan"). Observation O-7; no sequencing of writes is carried by a tool.
- Tool bodies (all six): look up the record, write one row / one update, return a receipt. None reads another policy's state, refuses, errors or hints when a prerequisite is unresolved. PASS (tool layer judges no prerequisite).

### prerequisite_graph

- `prerequisite` filled on all six (CS, LE, SSD `[]`). Edges: AP<-CS, TP<-LE, TP<-SSD, CF<-TP. All point at extended policy ids in this file, none at a base policy or itself. Acyclic (two chains). PASS.
- `policy_source` verbatim in the blocked policy's own rule: AP "Action-plan relief is fixed only after the standing record carries a points-expiry entry for every clean-span relief owed on it." ✓; TP "Top-performer relief is not worked out until every listing-type violation whose listing expiry period has run carries its expiry entry." ✓; TP "Top-performer relief is not worked out until every serious violation whose first period has run carries its step-down entry." ✓; CF "The carried-forward points are fixed only after any top-performer relief owed on the evaluation day stands booked on the standing record." ✓.
- `form: state` on all four; no `fallback_reason` key on any (correct for state form). `kind: value_input` with `gate` = `ap_active`, `lv_active`, `lv_active`, `cf_lt_active` — all exist in the blocked policy's compute. `resolved_by` equals the depended-on policy's `target_tool` in all four.
- `condition` wording: AP<-CS adds "dated on or after the day the clean-span relief fell due", a date restriction the prerequisite sentence does not carry (O-8, slight strengthening; no consequence where the entry is booked on the handling date). CF<-TP names gate `cf_lt_active` though a top-performer relief booked against a serious violation would move `cf_ser_active` instead (effect text covers both) — O-8.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "current world") in any `prerequisite` field. PASS.

### prerequisite_sentences

Four-point test per edge:

| edge | connective | waited-on state (record-visible) | names tool/id/snake_case? | strength vs condition |
|---|---|---|---|---|
| AP<-CS | "only after" | the standing record carries a points-expiry entry for every clean-span relief owed on it | no | matches (date nuance O-8) |
| TP<-LE | "not … until" | every listing-type violation whose listing expiry period has run carries its expiry entry | no | matches |
| TP<-SSD | "not … until" | every serious violation whose first period has run carries its step-down entry | no | matches |
| CF<-TP | "only after" | any top-performer relief owed on the evaluation day stands booked on the standing record | no | matches |

- Single resolving write per state-form edge: for each sentence the only write whose own rule produces that state is the named depended-on policy's write (CS grant / LE booking / SSD booking / TP grant). Caveat O-3: because CS's once-per-span test is "a record that already carries a points-expiry entry dated after its most recent violation is not owed another", any points-expiry entry dated after the latest violation (a listing expiry, a step-down, a top-performer relief, or the action-plan relief itself) makes "every clean-span relief owed" vacuously true. In a world where such another write is due, two writes could bring the AP<-CS state about. Neither task's world has such a second due write (task files show LE = SSD = 0 in task 0), so no consequence is demonstrable here; recorded as an observation.
- Derivations (sentence + records + depended-on rule -> resolving action, single reading):
  - AP<-CS: "points-expiry entry for every clean-span relief owed" -> CS rule says relief is owed to a Below…Above Standard seller in good_standing/at_risk with active points > 0, no violation in the last three whole calendar months, and no points-expiry entry dated after the latest violation -> if owed, book CS relief (`grant_clean_span_relief`).
  - TP<-LE: "every listing-type violation whose listing expiry period has run carries its expiry entry" -> LE rule defines the period and the expiring points -> book LE expiry.
  - TP<-SSD: "every serious violation whose first period has run carries its step-down entry" -> SSD rule -> book the step-down.
  - CF<-TP: "any top-performer relief owed on the evaluation day stands booked" -> TP rule (evaluation day, evaluation recorded, Top Rated/Preferred, good_standing/at_risk, active > 0) -> book TP relief.
- No second wording of any dependency in the blocked rules; no depended-on rule restates the sentence. PASS.
- Cross-problem orders in rules that ground no declared edge: TP's "once that month's evaluation is recorded" depends on the base evaluation event (`standing_evaluate`, base policy `standing_monthly_evaluation`), not on an extended problem — O-9 (state-satisfied in task 1: `last_evaluation_date` 2026-10-20). Base `standing_closure` "a suspended or under_appeal seller must first have the suspension resolved" is a base cross-problem order that no task's tree rests on — O-9.

### override_declarations

Sentence by sentence against each `base_policy_refs` entry.

`standing_violation_rules` (refs of CS, AP, LE, SSD, TP):
- S1 "Each recorded policy violation adds the points of its type from the violation points map." — followed (no extended policy records violations).
- S2 "Points expire when the point expiry period has passed, counted in calendar days from the violation's event_date." — superseded and declared by all five. LE replaces it for listing types (whole-month listing expiry period), SSD for serious types (step-down at six whole months); CS/AP/TP replacements are additive ("also comes off before any violation's point expiry period has passed"). Union of LE and SSD covers all six violation types, so the merged semantics are unique per type.
- S3 IP reversal on retraction — followed.
- S4 "A violation is reversed when an appeal on the basis violation_issued_in_error is accepted; an accepted plan_of_action appeal reinstates the seller but keeps the points on record until they expire." — followed; AP's "account health action plan" relief applies to good_standing/at_risk sellers (not to a suspension appeal), so it does not govern the same situation. Naming proximity noted (O-10).
- S5 "A reversed or expired violation is never reversed or expired a second time." — superseded and declared by all five with replacement texts. (In both task worlds no violation receives two entries, so even the base dedup contract `reverse_once` is not crossed.)
- Eligibility blocks `expiry_due` / `reverse_once` quote S2/S5 and fall with them.

`standing_closure` (ref of CF): C1 (allowed statuses; suspension must first be resolved) followed; C2 (deactivated closed by system) untouched.

`standing_agg_multi_holding` (ref of CF): A1 followed; A2 "A closed record does not count, so a seller who closed voluntarily and returns gets a new record." superseded and declared ("… which opens with the carried-forward points of the closed record").

Undeclared deviation found outside `base_policy_refs` policies, in base text rendered with the charter: base `accounts.violation_points.meaning` "Active policy violation points of the seller: points of recorded violations in, reversals and expiries out; the holding's violation_points is its running sum." vs CF rule "the closing write sets the record to closed with the closing date and records the carried-forward points as the closed record's active points". CF's carried points add payments, fulfilment and recent-points surcharges and a serious multiplier, so the closed record's `violation_points` is not the running sum of its violation events. No `overwrite` names the accounts sentence. Finding F-1 (consequence demonstrated in task 1's file).

Disguised forms: no anonymous intermediate factor, 0/1 multiplier or dropped branch found against S1-S5, C1-C2, A1-A2.

### factor_ladders

Per policy (P = parameter, M = method as labelled; "MS" = some non-fall-through tier is a conjunction/disjunction over distinct records; X = cross_difficulty):

| policy | factor | label | ladder values | MS | X |
|---|---|---|---|---|---|
| CS | clean_relief_rate | P | 0.30 / 0.28 / 0.25 | yes (level on standing_records ∧ count on standing_events) | – |
| CS | clean_span_multiplier | M | x2 / x1.5 / x1 | – | – |
| CS | payments_clean_bonus | P | 2 / 1 / 0 | – | payout |
| CS | clean_relief_tenure_cap | P | 10 / 8 / 5 | – | – |
| AP | action_plan_share | P | 0.35 / 0.25 / 0.15 | yes (level ∧ serious points) | – |
| AP | action_plan_risk_multiplier | M | x1.5 / x1.25 / x1 | – | – |
| AP | action_plan_stock_bonus | P | 2 / 1 / 0 | – | fulfill |
| AP | action_plan_store_cap | P | 6 / 4 / 3 | – | selling |
| LE | listing_expiry_base_period | P | 4 / 5 / 6 months | yes (level ∧ 3-month listing count) | – |
| LE | listing_repeat_extension | P | +2 / +1 / 0 | – | – |
| LE | listing_repeat_count_basis | M | count all types / both listing types / more frequent listing type | – | – |
| LE | stock_hold_offset | P | +2 / +1 / 0 | yes (units_on_hand on enrollment ∧ disposal-fee events) | fulfill |
| SSD | serious_step_share | P | 0.40 / 0.30 / 0.25 | yes (level ∧ 12-month serious count) | – |
| SSD | serious_quiet_multiplier | M | x1.25 / x1.125 / x1 | – | – |
| SSD | serious_stock_bonus | P | 2 / 1 / 0 | – | fulfill |
| SSD | serious_step_tenure_cap | P | 6 / 5 / 4 | – | – |
| TP | top_performer_rate | P | 0.15 / 0.10 / 0.05 | yes (level ∧ 3-month count) | – |
| TP | store_subscription_multiplier | M | x1.5 / x1.25 / x1 | – | selling |
| TP | payments_standing_bonus | P | 2 / 1 / 0 | yes (account status ∧ returned payouts) | payout |
| TP | warning_band_bonus | P | 2 / 1 / 0 | – | – |
| TP | fbn_program_relief_cap | P | 6 / 4 / 2 | – | fulfill |
| CF | carry_forward_share | P | 0.25 / 0.50 / 0.75 | yes (level ∧ tenure) | – |
| CF | serious_carry_multiplier | M | x3 / x2 / x1 | – | – |
| CF | payments_closing_surcharge | P | 3 / 2 / 0 | yes (balance ∧ status) | payout |
| CF | fbn_closing_surcharge | P | 2 / 1 / 0 | – | fulfill |
| CF | store_carry_cap | P | 10 / 8 / 6 | – | selling |
| CF | recent_points_surcharge | P | 2 / 1 / 0 | – | – |

Structural checks:
- Counts as declared: CS 4, AP 4, LE 4, SSD 4, TP 5, CF 6 — all within 4-6; each has ≥2 P and exactly 1 M as labelled. Every ladder has 3 pairwise-disjoint tiers; no two tiers of one ladder share a value or method; `decides` is never `result`; binding sets are disjoint within each policy; every tier stated in prose in the rule and implemented in compute (see rule_compute_equivalence). Fall-through tier = `baseline` binding for all 27 factors.
- **Label honesty (F-2):** five of the six `method` factors — clean_span_multiplier, action_plan_risk_multiplier, serious_quiet_multiplier, store_subscription_multiplier, serious_carry_multiplier — select only a different multiplier number in one unchanged formula (`int(points × share × mult) + …`, `serious × mult + listing`), with "taken as they are" being the multiplier 1. That is a `parameter` effect labelled `method`. Only LE's listing_repeat_count_basis changes how a quantity is computed (which violations the repeat count counts). Counting honest labels: CS 0 M, AP 0 M, LE 1 M, SSD 0 M, TP 0 M, CF 0 M.
- **Realism of tier conditions (F-3).** Violation points are, by the base charter's own account definition, "points of recorded violations in, reversals and expiries out" — a policy-compliance measure. The following ladders decide a violation-point quantity from a condition no marketplace weighs for policy-compliance relief or carry-over, and which a marketplace would not publish as its treatment (enforcement relief bought by subscription tier, or violation points added for a payments or fulfilment status):
  - CS payments_clean_bonus — negative-balance card charges on the payments ledger (and whether one was declined) add 2 / 1 / 0 points of violation relief.
  - AP action_plan_store_cap — the store subscription tier (Premium/Anchor/Enterprise vs Starter/Basic vs Individual) sets the relief cap 6 / 4 / 3.
  - TP payments_standing_bonus — a payout returned by the bank (e.g. invalid account number) or a non-active payments account removes 1-2 points of violation relief.
  - TP store_subscription_multiplier — the number of store subscription fees billed in 12 months multiplies violation relief (×1.5 for a year-long paying subscriber; an Individual-plan seller who pays no subscription is always ×1).
  - CF payments_closing_surcharge — a negative payments balance (+3) or a payout hold (+2) is converted into carried-forward violation points.
  - CF fbn_closing_surcharge — an active/inbound-suspended (+2) or winding-down (+1) FBN enrollment is converted into carried-forward violation points. Real-world closure logic would instead require the inventory to be removed and the balance settled before closure.
  - CF store_carry_cap — the store subscription tier sets the carried-points cap 10 / 8 / 6.
  Accepted as real (observation only): level/count/tenure ladders; the FBN disposal/return-removal bonuses in AP and SSD and LE's stock-hold offset (removing or still holding flagged stock is remediation evidence a marketplace does weigh); LE repeat-count basis. Borderline, recorded as observations: TP fbn_program_relief_cap (FBN program is placed by volume, so a scale proxy; O-11), AP risk multiplier and TP warning-band bonus (both give more relief to sellers carrying more recent points — counter-intuitive but defensible as "relief scaled to the remediation burden"; O-11).
- **Fall-through realism (F-4):** TP's baseline / fall-through rate 0.05 gives `int(p × 0.05) = 0` for every eligible seller. TP is owed only to good_standing/at_risk sellers, and base suspends at 16 active points, so an eligible seller carries at most 15 points: 15 × 0.05 = 0.75 → 0. The "standard top-performer relief" is identically zero for its whole population — a straw-man default, not a treatment any business publishes.
- Counts that survive F-2 and F-3 (structure only; per-task weight lives in the task files): CS 3 factors (0 M) — rate, span-mult (as P), tenure cap; AP 3 (0 M) — share, risk-mult (as P), stock bonus; LE 4 (1 M); SSD 4 (0 M); TP 3 (0 M) — rate, band bonus, FBN cap (borderline kept); CF 3 (0 M) — share, serious-mult (as P), recent surcharge.
- Cross-difficulty per task (from the task graph): task 0 tree (CS, AP) declares payout, fulfill, selling factors — after F-3 only AP stock bonus (fulfill) survives; task 1 tree (LE, SSD, TP, CF) declares fulfill (LE, SSD, TP), selling (TP, CF), payout (TP, CF) — LE stock offset and SSD stock bonus (fulfill) survive.

### findings

- **F-1 SOURCE-POLICY RED (bears on task 1).** Symptom: closed record's `violation_points` set to a number that is not the running sum of its violation events. Root cause: CF rule "records the carried-forward points as the closed record's active points" vs base `accounts.violation_points.meaning` "the holding's violation_points is its running sum"; no overwrite names the accounts sentence. Evidence: both quotations above; tool `close_selling_account_90945f31` body `ctx.update("standing_records", standing_id, status="closed", closed_date=today, violation_points=int(carried_points))`. Consequence: demonstrated in `1.md`. Affected: standing.extended.yaml CF rule / overwrite; task_tools.py close tool.
- **F-2 SOURCE-FACTOR RED (bears on tasks 0 and 1).** Five `method` factors are multipliers (parameter effects). Evidence: CS `cs_span_mult: K('span_mult_long') if cs_span >= 6 else (K('span_mult_mid') if cs_span >= 4 else 1)` inside `int(cs_active * cs_rate * cs_span_mult)`; AP `ap_mult` ∈ {1.5, 1.25, 1}; SSD `sv_mult` ∈ {1.25, 1.125, 1}; TP `lv_mult` ∈ {1.5, 1.25, 1}; CF `cf_ser_mult` ∈ {3, 2, 1}. Consequence: CS, AP, SSD, TP, CF each have no honest `method` factor (bound: ≥1). Affected: `factors[].effect` of those five policies.
- **F-3 SOURCE-FACTOR RED (bears on tasks 0 and 1).** Seven ladders whose conditions no marketplace weighs for violation-point relief/carry (list above). Consequence on counts: CS, AP, TP and CF fall to 3 surviving factors (bound: ≥4). Affected: CS, AP, TP, CF `rule` + `factors`.
- **F-4 SOURCE-FACTOR RED (bears on task 1).** TP fall-through/baseline yields zero for every eligible seller. Affected: TP `params.rate_standard`, `baseline`.
- O-1 (observation) Month-counting convention. The engine counts `MONTHS(d, NOW)` by corresponding date and a window "in the last N whole calendar months" as `0 ≤ MONTHS < N`. The charter states this convention only in LE ("counted in whole calendar months back from the handling date"). Read in isolation, "the last twelve whole calendar months" could also mean the N complete calendar months before the current month, and "number of whole calendar months from X to Y" could mean the complete calendar months lying between. The per-task files give the alternative values where they differ.
- O-2 (observation) LE and SSD subtract every expired/relieved/reversed point of a type from the expiring/carried points of only the violations whose period has run, so relief booked on a still-running violation reduces the expiry of an old one. Rule and compute agree; no task world has such a prior entry.
- O-3 (observation) CS once-per-span test is satisfied by any points-expiry entry dated after the latest violation, whatever wrote it (base expiry, LE, SSD, TP, AP). The AP<-CS state can therefore be brought about vacuously by another write, and a seller whose older violation expired by time after the latest violation is never owed CS. No consequence in task 0.
- O-4 (observation) Five tools write identical `standing_points_expiry` rows with no reason field; "its step-down entry" / "its expiry entry" are distinguishable from relief entries only by date and rule.
- O-5 (observation) SSD compute: `MX(0, …)` floor not stated in the rule; no dedup of an already-stepped-down violation; second-period expiry not implemented by any policy.
- O-6 (observation) LE `mn_units > 0` raises for a seller with no FBN enrollment (CFIELD → None).
- O-7 (observation) Docstring ordering words concern only input provenance and receipt values.
- O-8 (observation) `condition` nuances on AP<-CS (date) and CF<-TP (gate names one of two bindings).
- O-9 (observation) TP's "once that month's evaluation is recorded" and base closure's "must first have the suspension resolved" are cross-problem orders on base events, grounding no extended edge.
- O-10 (observation) "account health action plan" (AP) vs base "plan_of_action appeal … keeps the points on record" — different situations, similar names.
- O-11 (observation) Borderline ladders kept: TP fbn_program_relief_cap; AP risk multiplier and TP warning-band bonus direction.

## closing_checklist

Written after both reveals (2026-10-11 05:22 UTC). Step 4 close-out is **not reached**: neither task passes all four relationships.

| task | policy self-consistency | problem tree | factors | unique solution |
|---|---|---|---|---|
| 0 (`0.md`) | SOURCE-POLICY RED (F-T0-2, proof assertion only) | PASS | SOURCE-FACTOR RED (F-2, F-3) | SOURCE-TASK RED (F-T0-1, proof assertions only; scored solution unique and equal to GT) |
| 1 (`1.md`) | SOURCE-POLICY RED (F-1) | PASS | SOURCE-FACTOR RED (F-2, F-3, F-4, F-T1-1) | PASS |

Checklist items that do hold: the per-task files correspond one-to-one with tasks 0 and 1, and `_difficulty.md` sits alongside them (revision 1, no older revisions). The six extended policies are fully covered by two pairwise-disjoint scopes ({CS, AP}, {LE, SSD, TP, CF}). Each task tool has an independent uuid8. Both trees have 1 and 3 prerequisite problems, with value_input edges 1 ≥ 1 and 3 ≥ 2, an owner=user write each, and an acyclic difficulty-wide graph. Every declared factor bears weight numerically against its baseline, and every all-baseline fall-back differs from gold. Items that fail are listed in the table. The instantiation-stage gates were not re-run by this audit (outside its write domain, and no final form exists yet).

## revision_2

### charter_global_frozen (revision 2)

- Auditor: the same independent erl-task-policy-audit agent (round-2 re-audit). Freeze time of this section (system clock): 2026-10-11 07:11:31 UTC. Written before either task's round-2 GT was revealed; it contains nothing derived from a revealed GT.
- Inputs recomputed and equal to `HASHES.txt`: `standing.extended.yaml` c7201b8243c78b3c65d09305a66b9abf4c19eaa3b21b054a1c4a28140d8b1f7f (was dd1f9e9d…), `task_tools.py` 3646ab089100e873e698fb110ba23f84d63456799559c878fb99bc5eb9412022 (was aa7e1af0…), `0.view.json` 01f400c3…6ccb (source 0.json c9388b47…0773), `1.view.json` e2496318…b823 (source 1.json b4a56922…7c7f). The task files were hashed only.
- Both shared inputs changed, so every charter-global section below is re-derived in full; nothing is carried forward from revision 1.
- Gate snapshot `gates.r3.txt`: EXTENDED OK (cross-cat=3), TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK, all rc=0. Entry conditions complete.
- Base copy: extended lines 1-764 still equal `blueprint/products/standing.yaml` apart from the trailing blank line.
- Masked fields are the same as in revision 1.

### policy_conflict_scan (r2)

| id | trigger | target_tool (owner) | computes | prerequisite | cross_category |
|---|---|---|---|---|---|
| CS | state_due | grant_clean_span_relief_513362ca (agent) | points | [] | [] |
| AP | on_request | apply_action_plan_relief_841772f9 (user) | points | CS (value_input, state, gate ap_active) | fulfill |
| LE | state_due | book_listing_violation_expiry_caba69b5 (agent) | points | [] | fulfill |
| SSD | state_due | book_serious_step_down_71a20607 (agent) | points | [] | fulfill |
| TP | state_due | grant_top_performer_relief_7abd26c5 (agent) | points | LE, SSD (value_input, state, gate tp_active) | [] |
| CF | on_request | close_selling_account_90945f31 (user) | retired_points | TP (value_input, state, gate cf_ser_active) | [] |

- CF now books a `standing_points_expiry` entry (subject `standing_close` + `standing_points_expiry`) and leaves the rest of the points on the closed record, so the record's points stay equal to its running sum.
- Eligibility partitions are unchanged: CS covers Below…Above Standard, TP covers Top Rated/Preferred, LE covers listing types, SSD covers serious types, AP and CF run on request. The two components {CS→AP} and {LE, SSD→TP→CF} are disjoint and together complete.
- Cross-category reads are now only the FBN removal fees and units on hand (AP, LE, SSD). The payout and selling reads have been removed.

### rule_compute_equivalence (r2)

- CS: active points; 12-month count; rate ladder; threshold `P('warning_points_threshold')`; three-branch band method; suspension-history credit from `reinstated_date`; tenure cap; "rounded down, credit added, limited to cap". All are quoted and implemented. Two notes: the compute wraps rounding in `int(RND(x, 4))`, a 4-decimal float guard the rule does not state (O-15, harmless); and in the first branch only the threshold product is floored, which is equivalent because the excess is a whole number.
- AP: active, listing-type and listing_policy points; the 12-month count of listing-type violations; share ladder; coverage method from FBN disposal/return fees; listing clean-span bonus (no such violation → 99 → long); tenure cap; order of operations. PASS.
- LE: unchanged apart from the convention sentence and `CFIELD(...) or 0` (O-6 closed). PASS.
- SSD: "never less than zero" is now in the rule (the round-1 MX floor gap is closed), and the rule now says "steps down once". The compute still does not exclude a violation that already stepped down, and no policy books the second-period expiry (O-5 is only partly closed; observation).
- TP: base rate + repeat adjustment; three-branch band method; history credit; appeal credit; tenure cap; "added together, rounded down, limited". Gap (O-13): the rule's appeal tiers are "no appeal on the standing record" / "all accepted" / "a rejected appeal on record". The compute gives 0.5 to any record whose appeals include no rejection, including `withdrawn` or `submitted` appeals (`appeal_status` enum: submitted, accepted, rejected, withdrawn). The rule places those in no tier. Neither task world has such an appeal, so this is an observation.
- CF: active, listing-type and serious points at closing; share ladder; three-branch basis method (half / three quarters rounded down / all); recent-listing hold; suspension hold; floor at zero; tenure cap. PASS.
- Every factor tier is a rule sentence and a branch of its `decides` binding, and every branch is a stated tier. PASS.

### action_binding_and_uuids (r2)

- Six distinct `(target_tool, computes)` pairs. The uuid8s are unchanged and independent. `close_selling_account_90945f31` changed its contract (`carried_points` became `violation_ref, violation_type, retired_points`) but kept its uuid8 (O-14, observation).
- The close tool now writes the expiry row and lowers `violation_points` by `retired_points` before setting the record closed. None of the six bodies checks a prerequisite. Docstring ordering words still concern only receipts and input provenance (O-7).

### prerequisite_graph (r2)

- Edges: AP←CS, TP←LE, TP←SSD, CF←TP. Every edge is value_input and state form with no `fallback_reason`. The gates (`ap_active`, `tp_active`, `cf_ser_active`) exist in the blocked policy's compute, and each `resolved_by` is the depended-on policy's target tool. The graph is acyclic.
- Each `policy_source` is verbatim in the blocked rule: CF's sentence now reads "The retired points are fixed only after …".
- AP←CS `condition` no longer carries the date restriction, and CF←TP now names the serious-points gate with an effect covering both bindings (O-8 closed).
- No authoring-viewpoint phrasing.

### prerequisite_sentences (r2)

- The four sentences pass the four-point test: connectives are "only after" / "not … until", each waits on a record-visible entry state, and none names a tool, id or token. The derivations are as in revision 1.
- O-3 is narrowed but not closed. CS now treats relief as received when the record "carries a points-expiry entry dated three or more whole calendar months after its most recent violation". That still accepts an entry of any origin (LE, SSD, TP, AP, closure). For example, an AP entry booked before CS more than three months after the latest violation would make "every clean-span relief owed" vacuously true. The AP sentence still selects the CS write in reading order, so this remains an observation.
- O-9 and O-10 are unchanged (answered; observations).

### override_declarations (r2)

- `standing_violation_rules` S2 and S5 are now superseded by all six policies, with CF's replacements declaring that the closing write books a points-expiry entry and that its booking order covers listing types before serious ones. LE ∪ SSD still cover every type, so the merged semantics are unique.
- `standing_agg_multi_holding` A2 is superseded: "… opens with the active points the closed record kept".
- `standing_closure` C1 is followed.
- **F-1 closed.** The base `accounts.violation_points` running-sum definition is no longer contradicted: CF books its retirement as an expiry entry and the tool lowers `violation_points` by exactly that number.

### factor_ladders (r2)

| policy | factor | label (honest?) | ladder | MS | X |
|---|---|---|---|---|---|
| CS | clean_relief_rate | P ✓ | 0.30 / 0.25 / 0.20 | level ∧ count | – |
| CS | clean_relief_band_method | M ✓ (three algorithms) | above-threshold off in full + threshold×rate / threshold×rate + excess×2·rate / all×rate | points ∧ span | – |
| CS | suspension_history_credit | P | 2 / 1 / 0 | – | – |
| CS | clean_relief_tenure_cap | P ✓ | 8 / 6 / 4 | – | – |
| AP | action_plan_share | P ✓ | 0.35 / 0.30 / 0.25 | level ∧ count | – |
| AP | action_plan_coverage | M ✓ (changes the base quantity) | all active / listing-type / listing_policy | – | fulfill |
| AP | listing_clean_span_bonus | P ✓ | 2 / 1 / 0 | – | – |
| AP | action_plan_tenure_cap | P ✓ | 5 / 4 / 2 | – | – |
| LE | (unchanged four) | 3 P + 1 M ✓ | as r1 | yes | fulfill |
| SSD | serious_step_share | P ✓ | 0.20 / 0.15 / 0.125 | level ∧ count | – |
| SSD | serious_quiet_multiplier | P ✓ (relabelled) | ×1.5 / ×1.25 / ×1 | – | – |
| SSD | serious_remediation_scope | M ✓ | all carried / share-points + ¼ remainder / share-points | – | fulfill |
| SSD | serious_step_tenure_cap | P ✓ | 4 / 3 / 2 | – | – |
| TP | top_performer_rate | P ✓ | 0.30 / 0.20 / 0.125 | level ∧ count | – |
| TP | top_performer_repeat_adjustment | P ✓ | +0.10 / +0.05 / 0 | – | – |
| TP | top_performer_band_method | M ✓ | as CS band (6-month window) | points ∧ count | – |
| TP | top_performer_history_credit | P | 1 / 0.5 / 0 | – | – |
| TP | top_performer_appeal_credit | P | 1 / 0.5 / 0 | count ∧ status | – |
| TP | top_performer_tenure_cap | P ✓ | 6 / 4 / 2 | – | – |
| CF | retirement_share | P ✓ | 1.0 / 0.75 / 0.5 | level ∧ count | – |
| CF | retirement_basis | M ✓ | listing + ½ serious / listing + ¾ serious / all active | – | – |
| CF | recent_listing_hold | P ✓ | 2 / 1 / 0 | – | – |
| CF | suspension_history_hold | P | 2 / 1 / 0 | – | – |
| CF | retirement_tenure_cap | P ✓ | 3 / 2 / 1 | – | – |

- Counts: CS 4 (3 P / 1 M), AP 4 (3/1), LE 4 (3/1), SSD 4 (3/1), TP 6 (5/1), CF 5 (4/1). All ladders have 3 disjoint tiers with distinct outcomes. Each fall-through equals its baseline.
- **F-2 closed:** every policy now has exactly one honest method factor, and the multipliers are labelled parameter.
- **F-3 closed:** the payments, subscription-tier and FBN-status ladders are gone.
- **F-4 closed:** TP's standard rate 0.125 gives 1 point for 8-15 active points (0 below 8), so the standard treatment is no longer zero across the whole eligible population.
- O-11 closed (all three borderline ladders removed).
- **New F-5 (realism of the suspension/appeal ladders).** CS suspension_history_credit, TP top_performer_history_credit, TP top_performer_appeal_credit and CF suspension_history_hold decide their tier from `reinstated_date` and from accepted appeals without distinguishing a suspension overturned as issued in error. Base `standing_violation_rules` reverses the violation in full when a `violation_issued_in_error` appeal is accepted, and `standing_appeal_rules` treats that appeal as proof the violation should not stand. A marketplace weighs a seller's real enforcement history; it does not publish a treatment that lowers a seller's relief, or holds back points, because Northloop's own erroneous suspension was overturned. In particular, TP's "accepted-appeal credit" pays a seller with an accepted error appeal half of what a seller with no appeal gets. The rules are reasonable for plan-of-action reinstatements but have no tier for error reinstatements. Whether F-5 bears on a task is a world fact; see the task files.
- Cross-difficulty factors surviving: AP coverage, LE stock offset and SSD remediation (all fulfill).

### findings (r2)

- Round-1 items closed at charter level: F-1, F-2, F-3, F-4, O-1 (convention sentence now in every rule that uses month windows), O-6, O-8, O-11.
- Partly closed (observations remain): O-3 (narrowed), O-5 (floor stated, "once" stated; compute dedup and second-period expiry still missing).
- Answered without change and still observations: O-2, O-4, O-7, O-9, O-10.
- New:
  - **F-5 SOURCE-FACTOR RED candidate** (charter-global; demonstrated per task).
  - O-13: TP appeal-credit rule/compute gap for withdrawn or submitted appeals.
  - O-14: close tool contract changed under the same uuid8.
  - O-15: the `RND(…, 4)` float guard.
  - O-16: retiring points on voluntary closure runs against the carry-forward rationale. It is plausible as goodwill and capped at 1-3 points; observation.

### closing_checklist (r2)

Written after the r2 reveals (2026-10-11 07:14 UTC). The Step 4 close-out is **not reached**.

| task | policy self-consistency | problem tree | factors | unique solution |
|---|---|---|---|---|
| 0 | PASS | PASS | SOURCE-FACTOR RED (F-5) | SOURCE-TASK RED (F-T0-3, stale proof sums only) |
| 1 | PASS | PASS | SOURCE-FACTOR RED (F-5) | PASS |

Round-1 claim verification:
- Closed: F-1, F-2, F-3, F-4, O-1, O-6, O-8, O-11, F-T0-1, F-T1-1, F-T1-2.
- Withdrawals accepted (consistent with the charter): F-T0-2, F-T1-3.
- Narrowed, not closed (observations): O-3, O-5.
- Answered and still observations: O-2, O-4, O-7, O-9, O-10, O-12.

New in r2:
- F-5 (both tasks): suspension/appeal-history ladders penalise error-overturned suspensions, and both worlds are seeded with exactly that history.
- F-T0-3: stale "36 / 20 + 16 recorded" proof sums.
- Observations O-13 to O-17.

What still holds: scopes are disjoint and complete; uuid8s are independent; both trees have value_input edges at or above the floor, a user write and no cycle; one honest method factor per computation; every factor bears weight; every all-baseline result differs from gold. The instantiation gates were not re-run by this audit.

## revision_3

### charter_global_frozen (revision 3)

- Auditor: the same independent auditor (round-3 re-audit). Freeze time (system clock): 2026-10-11 08:07:26 UTC. Written before either task's round-3 GT was revealed; nothing in it comes from a revealed GT.
- Hashes recomputed; all equal `HASHES.txt`:
  - `standing.extended.yaml` 983bff4313c989241ee91deba9750656c8b35b20fb3b7d5f3f5c5ce532d41d7f (r2: c7201b82…)
  - `task_tools.py` 0134908c8091aff0c9e2f19f66f76219c97a24b389bb1e9ecbc182af3ced1b03 (r2: 3646ab08…)
  - `0.view.json` 41ff10f8…bf09 (source 0.json 6e752cf1…fce1)
  - `1.view.json` ede00dc7…77c2 (source 1.json da74ca0d…62da)
- Both shared inputs changed, so every charter-wide section below was re-derived in full.
- Gate snapshot `gates.r4.txt`: all 8 gates rc=0 (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING OK; CACHE-DIFF INFO; SCOPE OK).
- Base copy is still verbatim apart from the trailing blank line.
- Masked fields: same as revisions 1 and 2.

### policy_conflict_scan (r3)

- Same six policies, triggers, owners and graph as r2. The closure tool is renamed to `close_selling_account_c808e333`; no stale reference to the old uuid remains in the charter or the tools.
- Cross-category reads: FBN removal fees and units only, in AP, LE, SSD and now TP (remediation credit). Payout and selling are not read anywhere.
- Scopes {CS, AP} and {LE, SSD, TP, CF} remain disjoint and jointly complete.

### rule_compute_equivalence (r3)

- **CS:** the suspension-history credit is replaced by a repeat-record credit (2 / 1 / 0 by the most-repeated violation type in 12 months). It is quoted and implemented. O-15 is closed: every computing rule now says "products are worked to four decimal places before any rounding down", which matches `int(RND(…, 4))`.
- **AP, LE:** unchanged apart from the four-decimal sentence. PASS.
- **SSD:** unchanged apart from the four-decimal sentence. O-5 stands as in r2: the rule says "steps down once", but the compute still does not exclude a violation that already stepped down, and no policy books the second-period expiry. I see no further narrowing since r2. Observation.
- **TP:**
  - The history and appeal credits are replaced by a severity credit (1 / 0.5 / 0) and an FBN remediation credit (1 / 0.5 / 0). Both are quoted and implemented. O-13 is closed because the appeal credit is gone.
  - **O-18 (new, observation):** the severity ladder's middle tier ("a seller whose active serious points all come from serious violations recorded six or more whole calendar months before") and its fall-through ("a seller with a serious violation recorded in the last six whole calendar months") both hold for a seller whose recent serious violation was fully reversed while an older one still carries points. As stated, the tiers overlap there. The compute (`tp_serious_6 == 0`) resolves that case to the fall-through. Neither task world has such a record.
- **CF:** the suspension-history hold is replaced by an at-risk hold (2 / 1 / 0 by `status` and active points against the warning threshold), quoted and implemented. `cf_risk_points` duplicates `cf_active`, which is harmless. PASS.

### action_binding_and_uuids (r3)

- Six distinct `(target_tool, computes)` pairs. The closure tool has a fresh uuid8 `c808e333`, independent of the other five, so O-14 is closed.
- The tool bodies are unchanged in behaviour: closure books the retirement expiry entry and lowers `violation_points`; no tool checks a prerequisite. Docstrings unchanged (O-7).

### prerequisite_graph and prerequisite_sentences (r3)

- Same four state-form value_input edges, with verbatim `policy_source` sentences and gates present in each blocked policy's compute (`ap_active`, `tp_active` ×2, `cf_ser_active`). The graph is acyclic.
- O-3 remains narrowed (any expiry entry dated three or more months after the latest violation counts as clean-span relief received). Observation.
- O-9 and O-10 unchanged.

### override_declarations (r3)

- Same as r2: S2 and S5 are superseded by all six policies with declared replacements; A2 is superseded; C1 is followed.
- F-1 remains closed: the closure books an expiry entry, so the running sum is preserved.

### factor_ladders (r3)

| policy | factors (label) | method honest | conditions realistic? |
|---|---|---|---|
| CS | rate P; band M; repeat_record_credit P (2 / 1 / 0); tenure cap P | ✓ | ✓ (repeat history is a compliance signal) |
| AP | share P; coverage M (fulfill); span bonus P; tenure cap P | ✓ | ✓ |
| LE | base period P; extension P; repeat basis M; stock offset P (fulfill) | ✓ | ✓ |
| SSD | share P; quiet P; remediation scope M (fulfill); tenure cap P | ✓ | ✓ |
| TP | rate P; repeat adj P; band M; severity_credit P (1 / 0.5 / 0); remediation_credit P (fulfill, 1 / 0.5 / 0); tenure cap P | ✓ | ✓ (severity and remediation are compliance signals); O-18 overlap |
| CF | share P; basis M; listing hold P; at_risk_hold P (2 / 1 / 0); tenure cap P | ✓ | ✓ |

- Counts: 4 / 4 / 4 / 4 / 6 / 5. Each policy has one honest method factor and at least 2 parameter factors. Every ladder has three tiers with distinct outcomes, and each fall-through equals its baseline.
- **F-5 closed at charter level.** No ladder reads `reinstated_date` or `standing_appeals`. The suspension/appeal history factors are gone, so an error-overturned suspension can no longer move a relief or retirement.
- The new ladders weigh repeat violations, serious-violation recency, removal of flagged stock and at-risk status. A marketplace does weigh all of these for violation-point relief or carry-over.

### findings (r3)

- Closed at charter level: F-5, O-13, O-14, O-15. O-17 is a persona item; see `0.md`.
- Round-1 closures still intact: F-1, F-2, F-3, F-4, O-1, O-6, O-8, O-11.
- Still observations: O-2, O-3 (narrowed), O-4, O-5 (unchanged since r2), O-7, O-9, O-10, O-16 (answered without change).
- New: O-18 (TP severity tiers overlap on an unexercised edge).

### closing_checklist (r3)

Written after the r3 reveals (2026-10-11 08:09 UTC). All four relationships pass for both tasks, so the Step 4 close-out applies.

| task | policy self-consistency | problem tree | factors | unique solution |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- Files. `0.md` and `1.md` correspond one-to-one with tasks 0 and 1, and `_difficulty.md` sits alongside them. Revisions 1-3 are appended in order with earlier text untouched, and every comparison section of r3 reads PASS.
- Coverage. The six extended policies are fully covered by two disjoint scopes (each scope is the whole problem tree): {CS, AP} and {LE, SSD, TP, CF}. Task tools and GT are closed. The six uuid8s are independent and frozen; `c808e333` is freshly generated for the reworked closure contract.
- Trees.
  - Task 0: one prerequisite problem, one value_input edge, user write AP.
  - Task 1: three prerequisite problems, three value_input edges, user write CF.
  - The graph across the difficulty (AP←CS, TP←LE, TP←SSD, CF←TP) is acyclic.
- Computations. Each of the six declares a self-sufficient baseline and 4-6 factors, including one honest method factor and at least two parameter factors. Each task has at least one multi-source factor and at least one cross-difficulty (FBN) factor, with the rows seeded. Every ladder has three tiers with distinct outcomes and conditions a marketplace weighs. Every factor bears weight against its baseline on its task's world. Every all-baseline result is definite and differs from gold:
  - CS 2 vs 5
  - AP 1 vs 3
  - LE 6 vs 2
  - SSD 1 vs 3
  - TP 1 vs 4
  - CF 1 vs 2
- Gates. This audit did not run them (outside its write domain). The coordinator's snapshot `gates.r4.txt` was taken on the same final form whose hashes this audit verified (charter 983bff43…, tools 0134908c…, task files 6e752cf1… / da74ca0d…), and it shows all 8 gates rc=0.
- Open observations (not grounds for rework): O-2, O-3 (narrowed), O-4, O-5, O-7, O-9, O-10, O-16, O-18.

## revision_4

### charter_global (r4) — carried forward on unchanged hashes

- Same independent auditor; round-4 re-audit. Written 2026-10-11 08:49:46 UTC (system clock).
- Hashes recomputed; all equal `HASHES.txt`:
  - `standing.extended.yaml` 983bff4313c989241ee91deba9750656c8b35b20fb3b7d5f3f5c5ce532d41d7f, identical to revision 3;
  - `task_tools.py` 0134908c8091aff0c9e2f19f66f76219c97a24b389bb1e9ecbc182af3ced1b03, identical to revision 3;
  - views `0.view.json` 41ff10f8…bf09 and `1.view.json` ede00dc7…77c2, both identical to revision 3. The masked world, persona and frozen_time are unchanged.
- Only the task files changed: 0.json 6e752cf1… → 008b2a28e93b4c60be3c2ddbda0093a8b88cfefc74ec8d7e7db53211d0907792; 1.json da74ca0d… → f05df893737469f95f004f949c87645c7c954ebc09e33c687ef72330417d5925.
- Both shared inputs are byte-identical to revision 3, so every revision_3 charter-global section (policy_conflict_scan, rule_compute_equivalence, action_binding_and_uuids, prerequisite_graph/sentences, override_declarations, factor_ladders, findings) is carried forward by reference without re-derivation. The two hashes above are the grounds.
- Gate snapshot `gates.r5.txt`: 9/9 rc=0, including TRACEABILITY OK.
- Not re-derived: the scored-solution fields of each task. They are compared value for value in the task files.

### closing_checklist (r4)

| task | policy self-consistency | problem tree | factors | unique solution |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- The revision_3 closing checklist still holds item for item: shared inputs, worlds and every scored value and factor-sensitivity figure are unchanged (see the task files).
- The gates were re-run by the coordinator on this final form (`gates.r5.txt`, 9/9 rc=0); this audit verified that the hashes match.
- Open observations are unchanged: O-2, O-3, O-4, O-5, O-7, O-9, O-10, O-16, O-18.
