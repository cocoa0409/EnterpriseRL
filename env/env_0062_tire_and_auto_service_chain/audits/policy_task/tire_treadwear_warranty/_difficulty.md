# Policy-task audit — tire_treadwear_warranty / charter-global

## charter_global_frozen
- revision 1, written 2026-10-14 before any task's GT was revealed; contains nothing derived from GT.
- auditor: independent policy-task auditor (erl-task-policy-audit).
- hashes (sha256, equal to `.audit_views/policy/tire_treadwear_warranty/snapshot_r1.txt`): `tires.extended.yaml` 538965d60bc1e7f77dbaf6bca9724536fa318772ecb9a24ec85e4d23c210ef2e; `task_tools.py` 63a49782d806a61213d83de0a2041dc9ea6c3ab7ee0cdc9bbc87500ba7668b0e.
- read: blueprint.yaml, db_schema.json, share_tools.py, products/{tires,alignment,card,fleet,hazard}.yaml, the extended charter, task_tools.py, the DSL evaluator (skills/erl-task-instantiate/scripts/check_compute.py). Masked: every task GT field, worklogs, plan.md.
- entry conditions: gate snapshot supplied (all d_gates green; validate_scenario / check_traceability red only on pre-render items, per brief); masked views supplied with hashes, verified. Complete.
- base copy: the charter text before `extended_policies:` is byte-identical (modulo trailing newline) to blueprint/products/tires.yaml and yaml-equal key by key.

### policy_conflict_scan
Six extended policies: tires_ext_treadwear_credit (C), tires_ext_share_settlement (S), tires_ext_ticket_redemption (T), tires_ext_lapsed_order_refund (L), tires_ext_workmanship_share (W), tires_ext_trial_refund (R).
- Subjects/targets: C -> tires_treadwear_adjustment; S and T -> tires_adjustment_credit_applied (distinct tools, distinct scopes: S "toward a workmanship share", T "toward a replacement ticket"; each overwrite hands the other kind to its own rule); L -> tires_order_cancellation + tires_refund (store-initiated lapse only, customer cancellation stays base); W -> tires_workmanship_replacement; R -> tires_satisfaction_return + tires_refund. No two policies compute the same quantity on the same subject.
- Eligibility/time anchors: all inherited base gates stay in force (set status, term, inspection freshness, one adjustment per position, wear pattern, rotation gap, credit validity, trial window/miles/per-vehicle count). R narrows base "past the trial" (declared). W changes the free-replacement test to whole months (declared).
- Cross-category read boundaries: fleet roster/accounts (C, S, L), alignment plans/events (C, T, R), card account/transactions (C, S, T, W), hazard certificates (S, W). All reads are value reads; no write crosses categories.
- Scope: the derived trees are task 0 = {T root; C, S, L} and task 1 = {R root; W} (see 0.md / 1.md problem_chain). Disjoint; together they cover all six extended policies.
- Conflict found: base tires_evt_treadwear_adjustment vs C on miles driven (F-UNDECL-MILES, below).

### rule_compute_equivalence
Every compute_basis entry is a verbatim substring of its policy's rule (scripted check, 0 misses); every baseline.rule sentence is a sentence of the rule; every factor ladder tier is a rule sentence and a branch of its `decides` binding. Divergences where compute implements something the rule does not say (class F-RC):
1. W `defect_code_found` picks the defect by a priority tread_separation > belt_shift > bead_leak > out_of_round over every inspection row of the set, then `def_depth/def_odo/def_date` read the latest row of that code; the rule says "the set's inspection entry that records the defect" (the one tire being replaced). A set with an earlier defect row on another position selects the wrong entry. Not present in either world.
2. W `worn_measure` tier 2 tests `months_since` = MONTHS(purchase_date, NOW); the rule says "for a defect found after the trial but while fewer than workmanship_free_replacement_months whole months have elapsed since purchase_date" (time of finding = inspection date). Diverges only when inspection and today straddle the month limit. Not present in either world.
3. R `recapture` gives half for `plan_alignments <= 1` (includes 0); rule tier 2 is "used only for the alignment of its purchase visit". The alignment charter always performs the first alignment at purchase, so 0 should not arise. Observation.
4. L `missed_count` counts every non-latest booking as passed; the rule counts "booked appointments whose date has passed". Diverges only for a reschedule to an earlier date. Observation.
5. S `fleet_pts` tier 2 compares `removed_on >= enrolled_on` without a None guard (a removal row with no enrollment row raises). Observation.
6. `RND` is Python float round, not half-up; no tie arises in either world. Observation.
7. C/S/L read only the latest enrollment and latest removal of the vehicle; the rules speak of "the enrollment" (one episode). Observation.

### action_binding_and_uuids
(target_tool, computes): C issue_treadwear_adjustment_f769c805/amount; S apply_credit_to_workmanship_share_57ed5afc/amount; T apply_credit_to_replacement_ticket_eafdabc1/amount; L cancel_lapsed_tire_order_8987209f/amount; W record_workmanship_replacement_cc1528ea/charge_amount; R confirm_trial_return_33503dcd/amount — each claimed once. uuid8s f769c805, 57ed5afc, eafdabc1, 8987209f, cc1528ea, 33503dcd: distinct, no shared prefix or sequence. No factor id is a substring of any tool name (scripted check over all 33 tool names). Docstrings carry no concrete example value equal to a scored value (only formats such as "T- followed by 8 digits") and name no other tool; each contains the template sentence "Afterwards the set shows …", which describes the call's own effect, not a sequence (observation O-AFTERWARDS). Tool bodies check nothing (no status/balance/order validation). Owners: T, S, R owner=user; C, L, W owner=agent.

### prerequisite_graph
- prerequisite filled everywhere: C [], L [], W []; S -> C; T -> C, S, L; R -> W. All targets are extended ids of this file; no self-edge; acyclic.
- policy_source of every edge is verbatim in the blocked policy's own rule (scripted, 4 + 1 + 1 edges).
- form = state on all edges; no fallback_reason, none needed.
- kind/gate: S<-C value_input `credit_remaining` (binding exists); T<-C value_input `credit_issued` (exists); T<-S value_input `redemption_base` (exists); T<-L state_gate `tire_sets.status`; R<-W value_input `wrk_shares` (exists). resolved_by = the depended-on policy's target_tool in each case and the tool's effect makes the condition hold.
- condition vs sentence: T<-C, T<-S, T<-L, R<-W match. S<-C: condition adds "whose defect_code is none" and "for every … entry", the sentence reads "for the position that the latest inspection of the set measured at or below the line's wear-out depth" (O-SHARE-SENTENCE).
- No authoring-viewpoint wording in any prerequisite field.

### prerequisite_sentences
Four-point test, each edge:
- T<-C "The credit applied toward a replacement ticket is fixed only after the set carries a treadwear adjustment entry for every position that its latest tread inspection measured at or below the line's wear-out depth without a recorded defect." connective "only after"; state named in record words (adjustment entry, inspection, depth, defect); no tool/id; scope "every position" = condition. Unique writer: only issue_treadwear_adjustment_f769c805 creates tires_treadwear_adjustment rows (share tools are read-only). Derivation: a reader finds the worn, non-defective position on the latest inspection, then the policy whose rule "A treadwear adjustment credit is worked out for one worn wheel position" books it.
- T<-S "… fixed only after every workmanship share charged on the set at the visit of its latest treadwear adjustment carries a credit-applied entry naming that share's wheel position." Unique writer: apply_credit_to_workmanship_share_57ed5afc is the only tool that writes a credit-applied row with a wheel position (the ticket tool writes position ALL). Reader path: S's rule "A share settlement applies part of the treadwear adjustment credit of a set toward the workmanship share charged on the same set".
- T<-L "Before the credit applied toward a replacement ticket is fixed, no tire order on the customer's profile may stand in status ordered past the end of its hold period counted from its purchase date." Unique writer of ordered->cancelled: cancel_lapsed_tire_order_8987209f (installation has no tool here). Reader path: L's rule "an ordered set the store cancels because it was still not mounted after order_hold_days".
- S<-C "The credit settled on a workmanship share is not fixed until the set carries a treadwear adjustment entry for the position that the latest inspection of the set measured at or below the line's wear-out depth." "not … until"; state form; unique writer as above. Wording narrower/broader than the condition (singular "the position", no defect exclusion) — O-SHARE-SENTENCE.
- R<-W "The trial refund is not paid until every manufacturing defect recorded on an inspection entry of the set carries a workmanship replacement entry on the set." Unique writer record_workmanship_replacement_cc1528ea. Reader path: W's rule "A workmanship share is worked out for the one tire of an active set that a Crestline tread inspection found defective".
No rule restates another's sentence; no rule names a tool, a policy id or a route; no undeclared cross-problem order in an extended rule. Base rules stating cross-problem orders (tires_agg_vehicle_tire_count "that older set is retired first and only then is the new ticket opened") ground no edge of either tree.

### override_declarations
Sentence-by-sentence against base_policy_refs:
- C vs tires_commercial_use_coverage: commercial-use reading, mileage share/term, "Without commercial use …" — all three named in overwrite. vs tires_evt_treadwear_adjustment: credit_pct sentence and price-basis sentence named; inherited unchanged: status, term, inspection freshness, one-per-position, wear-out depth, excluded wear patterns, rotation gap, "nothing is issued" at or above covered miles, half-up rounding of the amount, no installation/fee/tax. NOT named: base "miles_driven is the inspection odometer minus install_odometer" (the inspection = "the tread inspection the adjustment rests on") vs C "The miles run are the odometer of the set's latest tread inspection minus the set's install_odometer" -> F-UNDECL-MILES. The card-member points change credit_pct; the base credit_pct sentence is named, but its replaced_by text describes only the aged-set proration (O-REPLACED-BY).
- S vs tires_evt_credit_redemption: the "reduces only the tire price on the replacement ticket" sentence named; validity, same set, never cash inherited.
- T vs tires_evt_credit_redemption: amount-applied sentence named; rest inherited.
- L vs tires_evt_order_cancellation (refund + restocking incl. "applies both … to a hold-period lapse" — named) and tires_purchase_ticket (ticket total — named).
- W vs tires_evt_workmanship_replacement: free-period sentence and customer-pays sentence named; the worn-measure ladder, defect-class rate, discounts and hazard mounting waiver all change quantities inside the named "customer pays" sentence, whose replaced_by speaks only of the price (O-REPLACED-BY).
- R vs tires_evt_satisfaction_trial: "past the trial", confirmation, amount sentences named; per-vehicle count, window, miles, remedy inherited.
- Three disguised forms checked: anonymous intermediate (F-UNDECL-MILES is one), 0/1 multiplier (none), dropped branch (none: base exclusion of all-commercial All-Season/Value coverage is replaced by a declared share).

### factor_ladders
| policy | factor | label | ladder tiers | multi-source | cross-difficulty | structural verdict |
|---|---|---|---|---|---|---|
| C | commercial_use_share | parameter | 3 | yes (roster rows + set install/today) | fleet | ok |
| C | care_package_points | parameter | 3 | yes (plan + alignment events) | alignment | ok |
| C | rotation_record_points | parameter | 3 | yes (rotation rows + inspection/install odometers) | — | ok |
| C | aged_set_proration | method | 3 | yes | — | ok |
| C | card_member_points | parameter | 3 | yes (ticket tender + card account + purchases) | card | ok |
| C | price_paid_basis | method | 3 | tier 2 yes | alignment | label dishonest (F-LABEL); tier 2 unreal (F-BUNDLE) |
| S | settleable_portion | method | 3 | tier 2 yes | — | label dishonest (F-LABEL); tier 1 = fall-through on the Ultra line (O-TIER-EQ) |
| S | settlement_start | parameter | 3 | yes | — | ok |
| S | card_points | parameter | 3 | yes | card | condition realism (F-REAL-1) |
| S | road_hazard_points | parameter | 3 | yes | hazard | condition realism (F-REAL-1) |
| S | fleet_points | parameter | 3 | yes | fleet | ok |
| T | redemption_base_rule | method | 3 | yes | — | borderline label (F-LABEL, PLAUSIBLE); tier 2 = fall-through unless a lapse row exists (O-TIER-EQ) |
| T | card_route_points | parameter | 3 | yes | card | condition realism (F-REAL-1) |
| T | alignment_plan_points | parameter | 3 | no | alignment | ok |
| T | rotation_history_points | parameter | 3 | no | — | ok |
| L | restocking_rate_by_bookings | parameter | 3 | no | — | ok |
| L | fleet_restocking_share | parameter | 3 | yes | fleet | ok |
| L | storage_charge_method | method | 3 | no | — | ok |
| L | weekly_storage_rate | parameter | 3 | yes | — | unreal ladder (F-LADDER-WEEKLY) |
| L | missed_slot_charge | parameter | 3 | yes | — | ok |
| W | worn_measure_basis | method | 3 | yes | — | label dishonest (F-LABEL) |
| W | defect_class_rate | parameter | 3 | no | — | ok |
| W | card_share_discount | parameter | 3 | yes | card | ok |
| W | maintained_set_discount | parameter | 3 | yes | — | ok |
| W | replacement_mounting_waiver | parameter | 3 | yes | hazard | ok |
| R | refunded_installation_part | parameter | 3 | yes | — | tier 1 = fall-through on Premium/Ultra (O-TIER-EQ) |
| R | trial_usage_charge | method | 3 | yes | — | ok |
| R | alignment_bundle_recapture | parameter | 3 | yes | alignment | anchor differs from alignment charter (F-BUNDLE, observation part) |
| R | truck_size_restock | parameter | 3 | no | — | ok |
Counts as labelled: every policy 4–6 factors, >= 2 parameter, >= 1 method. After honest re-labelling: S has 0 method, W has 0 method (fail); C keeps aged_set_proration; T keeps redemption_base_rule only if its borderline label is accepted. Every factor's fall-through equals its baseline except L weekly_storage_rate (baseline.rule states no storage charge at all).

### findings
- F-UNDECL-MILES — SOURCE-POLICY RED (charter). Base tires_evt_treadwear_adjustment: "miles_driven is the inspection odometer minus install_odometer" (inspection = "the tread inspection the adjustment rests on"); C: "The miles run are the odometer of the set's latest tread inspection minus the set's install_odometer." Same situation, different conclusions: a set whose worn RR was inspected 2026-10-08 at 39460 and whose LF was re-inspected 2026-10-12 at 39700 gives base 18000 miles vs C 18240 for the RR adjustment. Not named in C's overwrite. Bears on: task 0 (no scored value moves: the latest inspection is the one the adjustment rests on). Same class across the charter: W "the miles run are the odometer of the inspection entry that records the defect" (consistent with base, not a member); R miles run from the latest inspection (a new quantity, not a base override). Only C is a member.
- F-RC — SOURCE-POLICY RED (charter), rule/compute non-equivalence, items 1–2 of rule_compute_equivalence (W defect selection by priority; W tier-2 timing at NOW). Bears on task 1; no scored value moves there (one defect row; inspection and today both 1 month after purchase). Items 3–7 are observations.
- F-LABEL — SOURCE-FACTOR RED (mislabelled effect). Members: S `settleable_portion` (share owed − k × line mount, k ∈ {0, ½, 1}); W `worn_measure_basis` ((tread worn − a) × 100 / usable, a ∈ {free wear, ½ free wear, 0}); C `price_paid_basis` (unit_price − X / tire_count, X ∈ {set_instant_savings, plan tire_bundle_discount, 0}); borderline (PLAUSIBLE) T `redemption_base_rule` (credit issued − coefficient-weighted credit entries). Consequence: S and W fall to 0 honest `method` factors (task 0 via S, task 1 via W).
- F-LADDER-WEEKLY — SOURCE-FACTOR RED (unreal ladder / dishonest baseline), L `weekly_storage_rate`: its fall-through "any other order is stored at standard_weekly_storage_per_tire" is never charged — storage_charge uses the weekly rate only when more than long_storage_days past hold, and in exactly that case the weekly ladder is on tier 1 or 2; the part "held more than long_storage_days days past hold" of tiers 1–2 therefore holds of every order whose weekly rate is used and only restates scope; its declared baseline (2.00/week) is not stated by baseline.rule, which has no storage charge. Live ladder = 2 tiers. Bears on task 0 (L is in its tree). Other members across the charter: none found (every other fall-through equals baseline and is reachable).
- F-REAL-1 — SOURCE-FACTOR RED (unreal baseline value). T baseline "The redemption percentage is standard_redemption_pct" (20) caps the credit a customer may put on the replacement tire at 20 % of the credit (plus points) and leaves the rest to lapse within its 30–90-day validity; S baseline "The settlement percentage is standard_settlement_pct" (50) does the same for a workmanship share. A tire chain's prorated treadwear credit exists to be applied to the replacement tire, and the owning base rule lets the amount applied go up to tires_msr_credit_remaining; no tire retailer meters an issued adjustment credit by percentage per ticket. Conditions in the same ladders that no such business weighs for how much of an issued credit may be applied: S card purchase within the last card_recent_window_months = 1 month; S road hazard certificate status; T a card purchase "on or after the date of the set's latest tread inspection". Bears on task 0 (S and T in its tree).
- F-BUNDLE — SOURCE-FACTOR RED (PLAUSIBLE; unreal tier value) for C `price_paid_basis` tier 2: alignment charter: "purchase_price is plan_price minus tire_bundle_discount" and tire_bundle_discount is "Discount on the plan price when it is bought within tire_bundle_window_days of a Crestline tire set installed on the same vehicle" — the discount was given on the plan, yet C takes it off the tire price paid. Both C tier 2 and R `alignment_bundle_recapture` read the bundle as ABS(DAYS(set purchase_date, plan purchase_date)) <= window and from the variant parameter, whereas alignment_msr_tire_bundle is "install_date within tire_bundle_window_days before the plan's purchase_date" and the plan row's purchase_price records whether the discount was given (observation for R; R's recapture itself is realistic). No scored value moves in either world.
- F-CHAIN-WRK — SOURCE-CHAIN RED (fabricated real-world event), charter part: R's rule makes a trial refund wait for "every manufacturing defect recorded on an inspection entry of the set carries a workmanship replacement entry on the set", and tires_workmanship_replacement is a physical store replacement ("replacing store", "odometer at replacement", "carries the replacement tire forward on the same set"). Where the defective tire has not been replaced, the only route books a replacement from the desk on a set the customer is handing back. Demonstrated on task 1's world (1.md).
- Observations:
  - O-SHARE-SENTENCE: S's sentence ("for the position …", no "without a recorded defect") is singular and broader on defects than its condition; the base exclusion rule closes the defect reading, the singular could select one of several worn positions. Only one worn position in task 0.
  - O-REPLACED-BY: C overwrite #4 replaced_by omits the card-member points; W "customer pays" replaced_by omits the worn-measure ladder, defect-class rate, discounts and mounting waiver. The base sentences are named, so the overrides are declared.
  - O-TIER-EQ: S settleable tier 1 = fall-through on Ultra Touring (no mounting charged after the free period); R refunded_installation_part tier 1 = fall-through on Premium/Ultra (installation already refunded); T redemption_base tier 2 = fall-through whenever the set carries no credit-expired row.
  - O-AFTERWARDS: template "Afterwards …" in every task tool docstring.
  - O-ORDERED-TICKET: L's overwrite says an ordered set's ticket "carries the tire price paid alone, because the mounting, the valve-stem or TPMS-kit charge and the disposal fee are rung when the tires are mounted"; task 0 seeds card purchase b9844db9 = 206.11 = (159.99 + 21.00 + 6.99 + 3.75) × 1.075 for the still-ordered ticket T-15093342, i.e. installation rung at purchase. The premise is contradicted by the world's own ledger; the lapsed refund of set eb3df77d then keeps whatever installation charges its bank-card ticket carried. Not a second scored answer (L's rule is explicit).
  - O-REALISM-POINTS: C's care-package, rotation and card points raise covered mileage above the line's warranted miles; loyalty-style bonuses are plausible but not industry practice for a treadwear warranty.

## closing_checklist
Written 2026-10-15 after both reveals (resumed session; the sections above were frozen before any reveal and are unchanged).
- Files: `_difficulty.md`, `0.md`, `1.md` — one per task, plus this file; first revision, no older revisions.
- Scopes: GT charter_scope task 0 = {lapsed_order_refund, treadwear_credit, share_settlement, ticket_redemption}, task 1 = {workmanship_share, trial_refund} — equal to the derived trees, pairwise disjoint, jointly cover all six extended policies; task tools closed; uuid8s independent.
- Trees: task 0 has 3 prerequisite problems with 3 value_input edges, task 1 has 1 with 1; each has owner=user writes; the whole graph is acyclic.
- Unique solution: both tasks' derivations equal GT figure for figure.
- Not closed — the difficulty does NOT pass the source-layer audit:
  - task 0: SOURCE-FACTOR RED (F-LABEL on S, F-REAL-1, F-LADDER-WEEKLY, F-BUNDLE PLAUSIBLE)
  - task 1: SOURCE-CHAIN RED (F-CHAIN-WRK, PLAUSIBLE) and SOURCE-FACTOR RED (F-LABEL on W)
  - charter-wide open items: F-UNDECL-MILES, F-RC (items 1–2), F-LABEL, F-REAL-1, F-LADDER-WEEKLY, F-BUNDLE, F-CHAIN-WRK
- Gate re-run on the final form: not applicable until rework (this audit edits nothing; gates are the coordinator's).

## revision_2

### charter_global_frozen (revision 2)
- written 2026-10-15 before either round-2 task's GT was revealed; nothing here derives from GT. Round-1 text above is left untouched.
- hashes (sha256, equal to `snapshot_r2.txt`): `tires.extended.yaml` 6e45e4251ee04ae73f24410262031cd4218c50a42f3421323a799ba8c0e01fd2; `task_tools.py` 0bb046e6193d308e0dac06e41658c00b0a8236f8287c008ba0abe6270304796c. Both changed since round 1, so every charter-global section is re-derived in full below.
- gate snapshot r2: all d_gates green; validate_scenario / traceability red only on pre-render items. Entry conditions complete.
- base copy: still byte-identical to blueprint/products/tires.yaml.

### policy_conflict_scan (r2)
Same six policies and targets. T now computes `balance_due` (the replacement ticket balance) and passes the credit applied as `amount`; S settles a share by a waterfall against the replacement ticket; W posts a replacement "a Crestline store found defective at a tread inspection and replaced at that visit"; R returns "what the customer paid on the set, including the share paid". No two policies compute the same quantity on the same subject. One cross-policy disagreement: the share's mounting part (F-MOUNT-HALF, below). Scopes (derived): task 0 = {T; C, S, L}, task 1 = {R; W}; disjoint, jointly complete.

### rule_compute_equivalence (r2)
Scripted: every compute_basis entry verbatim in its rule; every baseline.rule sentence in the rule; every value_input gate is a compute binding. Round-1 F-RC items: (1) W's defect priority is now stated in the rule ("chosen among the set's inspection entries carrying a defect in this order: a tread separation, then a belt shift, then a bead leak, then an out-of-round tire, the latest entry of the first defect found") — closed; (2) W's timing now uses the replacement visit (`months_at_visit` = MONTHS(purchase_date, def_date)) — closed; (3) R recapture now `plan_alignments == 1` — closed; (4) L missed_count unchanged — observation; (5) the unguarded comparison left with S's fleet points (removed) — gone; (6) Python round vs half-up — no tie in either world (observation); (7) latest-episode roster reads — observation.
New: T road hazard line takes price_pct_of_tire_price of the recorded selling price without the hazard charter's "rounded half up to the cent" before the min/max clamp (O-HAZ-ROUND; no scored value moves in task 0: 27.20/2 vs 27.1983/2 both give 112.35).

### action_binding_and_uuids (r2)
Six (target_tool, computes) pairs, each claimed once (T now `balance_due`). uuid8s unchanged and independent. No factor id is a substring of any of the 33 tool names. No docstring carries a scored figure; the round-1 "Afterwards …" template is now "Once booked, …" — still a description of the call's own effect, not a sequence (O-AFTERWARDS, benign). Tool bodies validate nothing. New tool parameters: issue_treadwear_adjustment takes `current_selling_price`; apply_credit_to_replacement_ticket takes `balance_due` (stored in charge_amount); record_workmanship_replacement takes `store_id` and dates the entry at the source inspection's date.

### prerequisite_graph (r2)
Edges: S<-C value_input credit_remaining; T<-C value_input credit_issued; T<-S value_input credit_remaining; T<-L state_gate tire_sets.status; R<-W value_input wrk_shares. All policy_sources verbatim in the blocked rule; all form=state; acyclic; resolved_by = the depended-on target tool; gates exist in compute. S<-C now reads "for every position that the latest inspection of the set measured at or below the line's wear-out depth without a recorded defect" = its condition (O-SHARE-SENTENCE closed). T<-S now reads "every workmanship share charged on the set within thirty days before its latest treadwear adjustment" = condition "dated no more than 30 days before the latest tires_treadwear_adjustment entry".

### prerequisite_sentences (r2)
Four-point test passes on all five edges (connectives "only after", "not … until", "Before"; record-visible states; no tool/id). Unique writers: adjustment entries only via issue_treadwear_adjustment; credit-applied rows naming a wheel position only via apply_credit_to_workmanship_share (the ticket tool writes ALL); ordered->cancelled only via cancel_lapsed_tire_order; workmanship entries only via record_workmanship_replacement. S's rule words "The credit goes first to the replacement ticket", "is settled first", "waits behind the replacement ticket" describe how the credit is allocated in S's own amount, not an order of writes; the only write order stated is T<-S (O-ALLOC-WORDING, observation).

### override_declarations (r2)
- C: round-1 F-UNDECL-MILES now declared ("the miles run are the odometer of the set's latest tread inspection, which is the inspection the adjustment rests on … an adjustment resting on an older inspection is not worked out under this policy") — closed. credit_pct overwrite's replaced_by now carries the age deduction; even-wear points carried in the covered-pct overwrite (O-REPLACED-BY closed for C).
- W: replaced_by now names the defect-class rate, both discounts and the certificate mounting part (O-REPLACED-BY closed for W). Free-period sentence declared ("to the replacement visit").
- T: credit_redemption amount sentence and tires_purchase_ticket total declared for a one-tire replacement ticket.
- S, L, R: declared as in round 1 (L's purchase-ticket overwrite now also hands the replacement-ticket balance to T's rule).
No undeclared override found.

### factor_ladders (r2)
| policy | factor | label | honest? | ladder note |
|---|---|---|---|---|
| C | commercial_use_share | parameter | yes | unchanged |
| C | care_package_points | parameter | yes | unchanged |
| C | rotation_record_points | parameter | yes | unchanged |
| C | even_wear_points | parameter | yes | new; condition realism weak (rewarding inspection count) — observation |
| C | age_deduction_method | method | yes (linear in months vs flat) | new |
| C | price_paid_basis | parameter | yes | tiers 1 and 2 give the same value; "no refund entry on the set" holds of every set reaching the write (F-PRICE-TIER) |
| S | settlement_order_method | method | yes (min / pro-rata / remainder) | new |
| S | share_mounting_part | parameter | yes | tier 2 disagrees with W on lines without post-free-period mounting (F-MOUNT-HALF) |
| S | apportioning_price_basis | parameter | yes | new |
| S | apportioning_mounting | parameter | yes | new, fleet cross-difficulty |
| T | tire_line_basis | method | borderline-yes (tier 2 takes a minimum of two prices; tiers 1/3 select a price) | new |
| T | replacement_mounting_line | parameter | yes | new |
| T | fleet_labor_rate | parameter | yes | fleet |
| T | member_labor_rate | parameter | yes | alignment |
| T | road_hazard_line | parameter | yes | hazard |
| L | restocking_rate_by_bookings / fleet_restocking_share / missed_slot_charge | parameter | yes | unchanged |
| L | storage_basis_method | method | yes (one-week floor / three-week cap / per whole week) | new |
| L | weekly_storage_rate | parameter | yes | fall-through now the baseline rate stated in baseline.rule and reachable (non-truck line, <= 28 days) — F-LADDER-WEEKLY closed |
| W | proration_basis_method | method | yes (mileage share / time share / tread share — three different formulas) | F-LABEL closed for W |
| W | defect_class_rate / maintained_set_discount / alignment_maintained_discount / replacement_mounting_waiver | parameter | yes | alignment discount on a manufacturing-defect share: realism weak — observation |
| R | four factors | as round 1 | yes | recapture now reads the alignment charter's bundle (install_date window, purchase_price < plan_price) — F-BUNDLE closed |
Counts: C 6 (5P/1M), S 4 (3P/1M), T 5 (4P/1M), L 5 (4P/1M), W 5 (4P/1M), R 4 (3P/1M). Every fall-through equals its baseline. Line-conditional tier equalities remain (R refunded_installation_part tier 1 = fall-through on Premium/Ultra; S share_mounting_part tier 1 = fall-through and W waiver all-zero on Ultra) — O-TIER-EQ, observation.

### findings (r2, charter-global)
Round-1 items: F-UNDECL-MILES closed; F-RC 1–2 closed; F-LABEL closed (S, W, C re-built; T's redemption_base gone); F-REAL-1 closed (credit applied = smaller of credit remaining and the tire line; the share takes only what the waterfall leaves); F-LADDER-WEEKLY closed; F-BUNDLE closed (C tier removed, R reads the alignment charter's measure and the plan's purchase_price); F-CHAIN-WRK: charter part closed (W now posts a replacement "replaced at that visit"; R returns "the share paid") — task 1's world judged in 1.md.
New:
- F-PRICE-TIER — SOURCE-FACTOR RED (unreal ladder), C `price_paid_basis`. Tier 1 "a ticket of exactly set_instant_savings_min_tires tires that received set_instant_savings … pays unit_price less set_instant_savings divided by tire_count" and tier 2 "a ticket of more tires than set_instant_savings_min_tires … pays unit_price less set_instant_savings divided by set_instant_savings_min_tires" select the same value on every line (tire_count = set_instant_savings_min_tires = 4 in tier 1), so the ladder has two outcomes; and the condition part "with no refund entry on the set" holds of every set that reaches an adjustment (a tires_refund row exists only for satisfaction_trial_return or order_cancellation, which move the set to returned/cancelled, while the adjustment requires status active). Bears on task 0. Other members of the class across the charter: none unconditional; line-conditional equalities listed under O-TIER-EQ.
- F-MOUNT-HALF — SOURCE-POLICY RED (charter; no scored value moves in either task). S: "The share's mounting part follows the road hazard certificate on the set, as the workmanship replacement was charged: … an active certificate whose plan does not include it leaves half of mounting_balancing_charge_per_tire"; W: "The mounting part is mounting_balancing_charge_per_tire when workmanship_mounting_charged_after_free_period is true, and 0 otherwise … an active certificate whose plan does not include it halves the mounting part". Same situation — an Ultra Touring set (mounting not charged after the free period) under a 12- or 24-Month certificate: W charges 0 mounting, S treats 12.50 of the share as mounting and settles 12.50 less. Task 0's certificate includes mounting (tier 1), so no value moves.
- Observations: O-ALLOC-WORDING; O-HAZ-ROUND; O-TIER-EQ (line-conditional); O-AFTERWARDS (benign); F-RC 4/6/7; realism of even-wear points and the alignment discount on a defect share (loyalty-style, plausible, not industry-standard).

## closing_checklist (revision 2)
Written 2026-10-15 after both round-2 reveals.
- Files: `_difficulty.md`, `0.md`, `1.md`, each with revision_1 untouched and revision_2 appended.
- Scopes (GT charter_scope): task 0 = {lapsed_order_refund, treadwear_credit, share_settlement, ticket_redemption}, task 1 = {workmanship_share, trial_refund}: equal to the derived trees, disjoint, jointly complete. uuid8s unchanged and independent.
- Trees: task 0 — 3 prerequisite problems, 3 value_input edges, user writes S and T; task 1 — 1 prerequisite, 1 value_input edge, user write R; whole graph acyclic.
- Unique solution: both tasks' derivations equal GT figure for figure (all write arguments, all factor sensitivities, all all-baseline figures).
- Round-1 RED closure: F-UNDECL-MILES, F-RC 1–2, F-LABEL, F-REAL-1, F-LADDER-WEEKLY, F-BUNDLE, F-CHAIN-WRK — all closed. Round-1 observations: O-ORDERED-TICKET, O-REPLACED-BY, O-SHARE-SENTENCE, O-RECAPTURE-ZERO, O-T0-2 closed; O-AFTERWARDS reworded ("Once booked"), benign; O-TIER-EQ partly remains (line-conditional); O-T0-1 persists (inherent vacuity of the T<-S clause before any adjustment exists).
- Regressions / new: F-PRICE-TIER (SOURCE-FACTOR RED, task 0), F-MOUNT-HALF (SOURCE-POLICY RED, charter, no value moved), R2-1 (SOURCE-CHAIN RED proof figure 32.48 in task 0, edge still bears weight).
- Not closed — the difficulty does not yet pass. Gates on a final form are the coordinator's to re-run.

## revision_3

### charter_global (revision 3, frozen 2026-10-15 before the round-3 reveal)
- hashes = `snapshot_r3.txt`: `tires.extended.yaml` 4133ee06da15d287e0bd5557144bacee7b874a38518146d96b0caefa44d0e0d3 (changed -> charter sections re-derived); `task_tools.py` 0bb046e6… (unchanged -> action_binding_and_uuids carried forward from revision_2 on that hash). Base copy still verbatim. Gates green except the pre-render items.
- Scripted re-checks (all pass): policy_sources verbatim in the blocked rule; every compute_basis and baseline.rule sentence in its rule; replaced_by texts in the rule; value_input gates exist; no factor id inside a tool name; every fall-through = baseline.
- Changes found: (a) C `price_paid_basis` rebuilt — tier 1 "a ticket charged to a fleet account pays unit_price, less set_instant_savings divided by tire_count when the ticket had at least set_instant_savings_min_tires tires, less the fleet discount taken on the tires invoice … divided by tire_count"; tier 2 "a ticket paid by any other tender that had at least set_instant_savings_min_tires tires and received set_instant_savings pays unit_price less set_instant_savings divided by tire_count"; fall-through unit_price. The three tiers now give three different values (every fleet program's tires discount is 5–15 %, > 0), and the "no refund entry" clause is gone -> F-PRICE-TIER closed. The same fleet-discount clause was added to T's tire line, L's and R's tire price paid (and their baseline.rule sentences). (b) S share mounting part tier 2 now "half of the line's mounting part stated above" (compute `line_mount / 2`) = W's charge -> F-MOUNT-HALF closed.
- New observation O-FLEET-DISC: fleet charter "The discount_amount is category_discount_pct … applied to the ticket's pre-tax price excluding discount_excluded_items" — i.e. it also discounts the mounting and valve/TPMS lines — while the new clause subtracts the whole tires-invoice discount from the tire price per tire. Not reached in either world (no fleet-charged tire ticket); no scored value moves.
- New finding F-TENDER (from task 1's changed world, charter part): R returns "what the customer paid on the set, including the share paid for a tire the store replaced under the workmanship warranty" and "is returned to the tender that paid the ticket", while base tires_refund_tender (in R's base_policy_refs, not overwritten) says "A refund on a tire ticket goes back to the tender that paid the ticket … a Crestline credit card ticket is refunded as a merchandise credit on the card account … A refund is never split across tenders and never paid to a tender other than the original one." Whenever the share was paid on a different tender from the set's ticket the two clauses conflict; undeclared. Demonstrated in 1.md r3.

### closing_checklist (revision 3)
- Round-2 items: F-PRICE-TIER closed; F-MOUNT-HALF closed; R2-1 closed (task 0 deletion figure 22.38); O-T1-EVIDENCE addressed (counter payment seeded as card purchase a83f6d19 and read by gold).
- Both tasks: derivations equal GT figure for figure; scopes disjoint and complete; trees hold; every factor bears weight against an honest baseline; labels honest.
- Open: F-TENDER (SOURCE-POLICY RED, task 1) — introduced by the round-3 seed/persona change that moved the counter payment from the bank card to the Crestline card. Observations carried: O-PRICE-SOURCE, O-APPORTION-BASE, O-ALLOC-WORDING, O-HAZ-ROUND, O-TIER-EQ (line-conditional), O-T0-1, O-FLEET-DISC (new), F-RC 4/6/7.
VERDICT revision_3: task0=PASS task1=SOURCE-POLICY RED (F-TENDER) charter=F-TENDER

## revision_4

### charter_global (revision 4, frozen 2026-10-15 before the round-4 reveal)
- Gate: worklog tail = "REWORK round 4: gates 7/7 green"; snapshot built with /tmp/erl0062_coord/snapshot.sh (round 4): all d_gates green, validate/traceability red only pre-render. Hashes: charter 8d8172ea…, tools 04c0745a…, view 0 84cdb65a… (unchanged), view 1 3cfae14e…. Charter and tools changed -> re-derived. Base copy verbatim. Scripted structure re-checks pass (sources verbatim, compute_basis/baseline/replaced_by in rule, gates exist, no factor id in a tool name, fall-through = baseline).
- F-TENDER: R now refunds "every share the customer paid … on the counter ticket it was paid on and to the tender that paid that ticket, never added to the refund on the set's ticket"; the amount overwrite now reads "the trial refund on the set's ticket is the tire price paid plus the refunded installation part, less …"; confirm_trial_return books a second tires_refund row (share_ticket_number, share_payment_method, share_amount). Checked against base tires_refund_tender ("goes back to the tender that paid the ticket"; "a Crestline credit card ticket is refunded as a merchandise credit on the card account"; "only one refund per refund reason"; "never split across tenders and never paid to a tender other than the original one") — each refund row now has one ticket and its own tender: satisfied. Checked against card charter card_evt_merchandise_credit ("A Crestline refund on a ticket that was paid with the card posts as a merchandise credit for the refund amount") and the tires event trigger (tires_refund with crestline_card -> card:card_merchandise_credit mapping source_ticket_number = ticket_number): the share refund row on T-16188204 with crestline_card is exactly that source; no task tool or erlbench layer materialises cross-category triggers (same as every other refund in this scenario) — consistent. Sales tax "returned by the point-of-sale tax line and never part of these amounts" agrees with tires_purchase_ticket. Closed.
- R's prerequisite gate moved to `install_part` (value_input; binding exists); policy_source unchanged and verbatim.
- O-FLEET-DISC: the four policies now state outright that "the whole discount_amount of that invoice is counted against the tire price, the part taken on the mounting and kit lines included" — a declared business choice, not reached in either world. Addressed (observation closed).
- New defects: none found.

### closing_checklist (revision 4)
- Round-3 items: F-TENDER closed; O-FLEET-DISC addressed. No regression: task 0 figures unchanged; task 1 derivation = GT.
- Both tasks pass all four relationships; scopes disjoint and complete; trees hold (task 0: 3 prerequisites / 3 value_input; task 1: 1 / 1), each with customer-owned writes; every factor bears weight against an honest baseline; labels honest; cross-difficulty rows seeded and consistent with their owning charters (fleet roster/accounts, alignment plans/events, hazard certificates, card account/purchase).
- Remaining observations (not grounds for rework): O-PRICE-SOURCE, O-APPORTION-BASE, O-ALLOC-WORDING, O-HAZ-ROUND, O-TIER-EQ (line-conditional), O-T0-1, F-RC 4/6/7.
VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

### charter_global (revision 5, frozen 2026-10-15 before the round-5 reveal)
- Gate: worklog tail "REWORK round 5: gates 7/7 green"; snapshot.sh round 5: d_gates green, validate/traceability red only pre-render. Hashes: charter 945e1387…, tools 47bb83c0…, view 0 7e893182… (changed), view 1 3cfae14e… (unchanged). Base copy verbatim. Scripted re-checks pass (sources verbatim, compute_basis/baseline/replaced_by in rule, gates exist, no factor id in a tool name, fall-through = baseline).
- Render-source notes (audits/render_source/tires/notes.md) §1–§5, checked in the source:
  - §1 assembly sentences: C ("the covered-mileage percentage being 100, plus every point addition and less every point reduction this policy states, each worked out on its own"), T ("plus every line this policy adds and less every relief it takes off, each worked out on its own"), L order_cancellation ("less every other charge this policy states and plus every relief it gives"), W ("the prorated share less every part of it this policy takes off, each a percentage of the prorated share worked out on its own"), R ("plus every part this policy returns and less every charge it takes, each worked out on its own") now name no factor quantity; single-factor sentences ("the age deduction stated below", "the commercial-use cut stated below") each have one home. Remaining instance: L's tires_purchase_ticket replaced_by — "a one-tire replacement ticket written against a treadwear adjustment credit carries the tire line less the credit applied, plus the line's mounting charge less its reliefs, plus the road hazard line it adds and tire_disposal_fee_per_tire" — an assembly sentence in L naming T's factor quantity (the road hazard line) together with T's reliefs; T's own replaced_by states the same balance without naming factors. -> F-ASSEMBLY-L (open; no scored value moves).
  - §2 method reading other factors' outputs: S's settlement order is now part of S's baseline over plain bindings (settleable part, apportioning base); S's method factor `apportioning_tire_line` reads only the recorded price, set age, ticket and fleet invoice. Closed. Scan of every factor: no factor's tier or value reads another factor's decided quantity (L's fleet relief now reads the line's full restocking fee, not the booking-rate fee; W's cuts/discounts are each a percentage of the prorated share, combined only in `share_pct`; C's points combine only in `covered_pct`; T/S reliefs combine only in `mounting_net`/`apportion_base`). Factor independence: holds.
  - §3 overwrites: every replaced_by now restates the superseded clause in force for the cases outside the policy (miles basis, commercial-use reading incl. usage_class commercial and "though workmanship replacement still applies", credit amount basis, purchase-ticket total, customer-requested cancellation, credit cap, workmanship tread_worn_share, trial confirmation and amount). C now applies only to vehicles with usage_class personal ("a set on a vehicle whose usage_class is commercial is adjusted under the base rule alone"). Closed.
  - §4 undefined branches: C "enrolled for less than one whole month … or never enrolled … has nothing taken off"; R "or 0 for a set with no tread inspection entry"; W "A set with no inspection entry recording any of these defects has no workmanship share to work out, and its share is 0.00" (compute `none` -> 0.00). Closed.
  - §5 docstring: confirm_trial_return now says it "writes nothing on any card account; … the merchandise credit is posted by the refund event's card trigger, not by this call". Closed.
- Factor re-shapes (structure): C commercial share -> `commercial_cut` (points off, ladder 50/… unchanged in effect); S factors apportioning_tire_line (M), share_mounting_part, apportioning_fleet_relief, apportioning_member_relief (P); T tire_line_basis (M), balancing_relief, fleet_labor_relief, member_labor_relief, road_hazard_line (P); L restocking_rate_by_bookings, fleet_restocking_relief, storage_surcharge, missed_slot_charge (P), storage_basis_method (M, standard rate × {1, 3, whole weeks}); W proration_basis_method (M), defect_class_cut, maintained_set_discount, alignment_maintained_discount, replacement_mounting_waiver (P). Counts within bounds; every ladder 3 distinct outcomes (line-conditional equalities as before, O-TIER-EQ); conditions and values plausible for the line of business.

### closing_checklist (revision 5)
- Render-source misses §2–§5 closed in the source; §1 closed except F-ASSEMBLY-L (L's tires_purchase_ticket replaced_by names T's road hazard line and reliefs in an assembly sentence; T's own replaced_by already states that balance without naming factors). SOURCE-POLICY (render-surface), no scored value moves.
- Factor independence verified for all 29 factors. Both tasks: derivation = GT; trees, factor weight, honest baselines and labels hold. No regression.
- Observations carried: O-PRICE-SOURCE, O-APPORTION-BASE, O-ALLOC-WORDING, O-HAZ-ROUND, O-TIER-EQ, O-T0-1, F-RC 4/6/7.
VERDICT revision_5: task0=PASS task1=PASS charter=F-ASSEMBLY-L

## revision_6

### charter_global (revision 6, frozen 2026-10-15 before the round-6 reveal)
- Gate: worklog tail "REWORK round 6: gates 7/7 green"; snapshot.sh round 6 green except pre-render items. Hashes: charter 7e1f6204… (changed); tools 47bb83c0…, view 0 7e893182…, view 1 3cfae14e… (all unchanged from revision_5 -> action_binding_and_uuids and per-task worlds carried forward on those hashes). Base copy verbatim; scripted structure checks pass.
- F-ASSEMBLY-L: L's tires_purchase_ticket replaced_by now ends "a one-tire replacement ticket written against a treadwear adjustment credit carries the balance figured under that ticket's own rule" — no factor quantity named. Closed.
- Full scan of every rule sentence (incl. replaced_by text) of the six policies for sentences naming two or more factor quantities or another policy's factor quantity: none.
- Nothing else changed in effect: every compute re-evaluated on both worlds gives the revision_5 figures (C 66.74, L 436.58, S 9.63, T 57.11/109.59, W 3.31, R 872.70 + 3.31), all factor and all-baseline figures identical, deletion figures 20.09 / 99.96 / 756.70.

### closing_checklist (revision 6)
- All round-1..5 REDs closed; render-source notes §1–§5 closed; factor independence holds; both tasks' GT (re-read after the freeze) equal the derivation figure for figure; no regression.
- Observations carried (not grounds for rework): O-PRICE-SOURCE, O-APPORTION-BASE, O-ALLOC-WORDING, O-HAZ-ROUND, O-TIER-EQ, O-T0-1, F-RC 4/6/7.
VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

### charter_global (revision 7, 2026-10-15)
- Gate: worklog tail "REWORK round 7: gates 7/7 green"; snapshot.sh round 7: all gates green, validate_scenario VALID, traceability OK (0 misses). Hashes: charter fde6faff… (changed); tools 47bb83c0…, view 0 7e893182…, view 1 3cfae14e… unchanged (carried forward on those hashes). Base copy verbatim; scripted structure checks pass; factor bindings pairwise disjoint within every policy; no factor id in a tool name.
- KB-E1 closed: S's apportioning tire line sentence now reads "The apportioning tire line follows the set's age and the line's price basis: …" (the phrase "as the replacement ticket figures its tire line" is gone).
- KB-E2 closed: S's share mounting sentence now reads "The share's mounting part, held back from settlement, follows the road hazard certificate on the set: …" ("as the workmanship replacement was charged" is gone).
- "Miles run" baseline line closed: W's baseline.rule no longer defines miles run; each factor that uses mileage defines its own in its own tier ("the miles run, that entry's odometer minus install_odometer" in proration_basis_method; `maint_miles` in maintained_set_discount) — factor independence kept.
- Scan of every rule/replaced_by sentence for phrases pointing at another policy's factor or naming several factor quantities: none remaining (the only cross-references are scope sentences such as "carries the balance figured under that ticket's own rule").
- Re-evaluation on both worlds: every scored value, factor figure, all-baseline figure and deletion figure identical to revision_6 (C 66.74, L 436.58, S 9.63, T 57.11/109.59, W 3.31, R 872.70 + 3.31; 20.09 / 99.96 / 756.70). GT re-read: identical. Process note: this round's re-evaluation and the GT re-read ran in one command, so no separate pre-reveal file was written; the blind reference is the revision_5/6 derivation already on disk, which the re-evaluation reproduces exactly.

### closing_checklist (revision 7)
All round-1..6 REDs and the KB auditor's source-side items KB-E1, KB-E2 and the W "miles run" baseline line are closed; no regression; observations carried unchanged (O-PRICE-SOURCE, O-APPORTION-BASE, O-ALLOC-WORDING, O-HAZ-ROUND, O-TIER-EQ, O-T0-1, F-RC 4/6/7).
VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN
