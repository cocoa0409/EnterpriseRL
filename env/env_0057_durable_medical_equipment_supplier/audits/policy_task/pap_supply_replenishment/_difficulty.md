# Policy-task audit — pap_supply_replenishment / charter-global

## charter_global_frozen

- Auditor: erl-task-policy-audit auditor (independent of the instantiating agent; a previous auditor on this unit was cut before writing anything, so this is revision 0 written from a clean start).
- Freeze time: 2026-10-12T19:20Z (wall clock), written before any task's GT was revealed.
- Frozen inputs (sha256 re-verified against `.audit_views/policy_task/pap_supply_replenishment/HASHES.txt`):
  - `tasks/pap_supply_replenishment/resupply.extended.yaml` e9a2f4f64385af6dc5a458d0ce0e4646d4060791d62d65a673f91079044a89cd
  - `tasks/pap_supply_replenishment/task_tools.py` 2ba39951ef0bb94d7f09c087e9b4ef8574297e4a4e6eb563f884091892d96283
- Read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/resupply.yaml` (base copy compared programmatically: every base key of the extended file equals the blueprint verbatim), `blueprint/products/pap.yaml` (device-class parameters the cross reads use), the extended charter, `task_tools.py`, the two `.view.json` masked views, and the compute sandbox `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS/DAYS/within_months semantics).
- Masked and not read: `tasks/pap_supply_replenishment/tasks/*.json` (evaluation_criteria, computations, design_rationale, solvability_contract, prerequisite_closure, charter_scope, required_documents, db_closure*), any earlier audit, worklog.
- Nothing in this charter-global section is derived from a revealed GT.

Policy short names used below: P1 `resupply_ext_continued_use_proof_date`, P2 `resupply_ext_covered_filter_units`, P3 `resupply_ext_wrong_cushion_reship_units`, P4 `resupply_ext_refill_request_items`, P5 `resupply_ext_recorded_style_from_use`, P6 `resupply_ext_standing_order_charge`, P7 `resupply_ext_ground_charge_catch_up`, P8 `resupply_ext_rush_shipping_charge`.

### policy_conflict_scan

- Base section: verbatim equal to `blueprint/products/resupply.yaml` for every key (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies). Only `extended_policies` is added.
- Subjects / target tools: P1 resupply_order_renew -> record_continued_use_proof_c97fce72; P2 resupply_item_shipped (coverage A7038) -> ship_covered_refill_e8c1261e; P3 resupply_no_charge_replacement -> send_no_charge_replacement_8a217fc0; P4 resupply_refill_confirmed -> confirm_refill_request_b3535d21 (owner=user); P5 resupply_preference_update -> update_mask_style_bfa4256b; P6 resupply_item_shipped (self-pay standing order) -> book_subscription_line_cd282959; P7 resupply_shipping_charge (ground) -> book_ground_shipping_charge_38ca3aab; P8 resupply_shipping_charge (expedited) -> pay_expedited_shipping_41dc5e4a (owner=user). P2 and P6 share the subject resupply_item_shipped but split it by billing basis (coverage A7038 vs self-pay standing-order cushion) and by tool; P7 and P8 share resupply_shipping_charge but split by shipping method and tool. No two policies decide the same quantity on the same tool.
- Triggers / time anchors: P2 ships on the day a confirmation reaches its last allowed ship day (base `confirmation_fresh`, Medicare 14 days); P6 ships when the cushion supply is within `ship_no_earlier_days`; P7 books against a past ship date; P8 today. No two policies fix the same date differently.
- Cross-category reads: P1 and P2 read `pap` compliance downloads / re-evaluations / device status and class parameters; P6 reads `pap_billing` pap_purchase_sale. All read-only.
- Terminal states: all writes are row inserts or single-field updates on the enrollment; no lifecycle transition is claimed.
- Scope exclusivity (inferred from the prerequisite graph and the two views, to be checked against `charter_scope` after reveal): tree A = {P4 root; P1, P2, P3}, tree B = {P8 root; P6, P7; P5 under P6}. The two trees are disjoint and together cover all 8 extended policies.

### rule_compute_equivalence

Every quantity of every policy has a verbatim `compute_basis` quotation (checked policy by policy). Every factor ladder tier appears as a rule sentence and as a branch of its `decides` binding, and vice versa. The divergences found (each recorded as a charter-global observation in `findings`; consequences are only demonstrable per task):

1. P1 — the opening sentence "When the device record holds a proof of continued use that is newer than the continued-use date on the supply enrollment, the enrollment's continued-use date is brought up ..." has no compute counterpart: `result: governing` is never compared with `F('last_continued_use_date')` (empty promise when the governing date is older than the recorded one).
2. P1 — the rule says a fallback (newest *met*) download is "credited at the last night of its window" (`met_end`), while the general sentence "The date credited to a download that proves continued use is ... the date the download was taken when it was taken no more than 7 days after the last night of its window" would credit that same download at its taken date; compute applies `dl_credit` to the newest download only. `note_date == dl_taken` compares only the newest re-evaluation, while the rule says "a re-evaluation documenting benefit is dated the same day".
3. P2 — "two calendar months before the ship date" is implemented as the rolling window `within_months=2` (0 <= MONTHS(d, NOW) < 2); `DAYS(last_decline, confirmed_on) <= 30` is also true for a decline dated after the confirmation, which the rule ("fell no more than 30 days before the refill was confirmed") excludes. The rule states no covered-through date for the line while also saying "The months a line covers are counted from an anchor" (see override_declarations item O1).
4. P4 — the cash tier "when its only self-pay line is for the tubing type not in use" is implemented as `cash_any == False and alt_tubing_cash` (self-pay lines of items outside the recorded equipment do not stop the tier, although the rule's "only" would). Coverage-billed lines named by a `resupply_line_reversal` are not excluded from `cov_*` although the base measure `resupply_msr_item_covered_through` excludes them.
5. P5 — in the `all` evidence mode the rule says "every interface and cushion line counts", but `al_*` counts `resupply_item_shipped` lines plus mask_fit_exchange lines only (no-charge replacements for wrong_item / manufacturer_defect / carrier_lost are dropped). In the `branch` mode the rule names what counts (branch lines, exchange lines) and what does not (standing-order lines) but is silent about other lines (coverage lines, non-branch non-standing self-pay lines); compute drops them.
6. P6 — "the latest standing-order line's units per month plus those branch units divided by three, rounded up" is implemented as `std_rate + ceil(branch/3)` (the rounding point is ambiguous in the rule); `units: int(...)` truncates although the rule states no rounding of units; "the months the standing-order lines shipped in that span cover" is implemented as `std_units_12 / std_rate` over lines of `std_item` only (equivalent only when every standing-order line in the span has the same item and rate); a "standing-order line" is identified in compute as `billing_basis=self_pay, shipping_method=ground`, a convention the rule never states.
7. P7 — the rule charges "the newest self-pay shipment that went out by ground and carries no shipping charge"; compute takes the newest self-pay ground shipment first (`box_date`) and only then tests `box_charged == 0`, so an older uncharged ground shipment behind a newer charged one is charged by the rule and not by compute. The first sentence "Every self-pay shipment that went out by ground carries one ground shipping charge" covers every uncharged shipment; compute books one.
8. P8 — `credit` tier 1 additionally requires `P('self_pay_free_shipping_min') > 0`, a condition the P8 rule does not state (it mirrors the base "when that value is above 0.00").

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (8 distinct tools, 8 policies).
- uuid8 tails: c97fce72, e8c1261e, 8a217fc0, b3535d21, bfa4256b, cd282959, 38ca3aab, 41dc5e4a — no shared prefix or suffix, no sequence, no adjacency; consistent with independent generation.
- Tool bodies (`task_tools.py`): each performs one `ctx.create`/`ctx.update`; none reads another row to refuse, error or hint on an unresolved prerequisite. The tools do not judge prerequisites.
- Docstrings: none names another tool. Sequence-flavoured wording (observations, no demonstrable scored consequence): every docstring says ids are "read from the ... lookup before the call" (read ordering only); `confirm_refill_request_b3535d21` says "Once recorded, the request is visible ... and the named items may be shipped against it"; `ship_covered_refill_e8c1261e` says "shipping today against a refill confirmation already on file"; `pay_expedited_shipping_41dc5e4a` says "The charge then appears ... next to today's item lines". These hint at a ship-after-confirm and lines-before-rush order.
- `book_subscription_line_cd282959` takes a free `shipping_method` (ground / expedited / branch_pickup) that P6's rule never fixes; the docstring's enum glosses ("expedited when the patient asked for the faster paid service") are the only source.

### prerequisite_graph

- `prerequisite` is filled for all 8 policies (P1, P2, P3, P5, P7: `[]`).
- Edges: P4 <- P2 (gate `cov_filt`), P4 <- P3 (gate `nc_cush`), P4 <- P1 (gate `lead_proof`), P6 <- P5 (gate `item`), P8 <- P6 (gate `today_amount`), P8 <- P7 (gate `last_ground_box`). Every `problem` is another extended policy id of this file; no self-edge; the graph is acyclic (two trees, depth <= 2).
- Each `policy_source` is verbatim in the blocked policy's own rule (checked programmatically); every edge is `form: state` with no `fallback_reason`; every `resolved_by` equals the depended-on policy's `target_tool`; every `gate` is a binding of the blocked policy's compute; `kind: value_input` everywhere.
- `condition` vs sentence: see prerequisite_sentences items S1 and S3 (two conditions are broader than, or read differently from, what the resolving write brings about).
- No authoring-viewpoint wording ("in this task", "at the opening") in any prerequisite field.

### prerequisite_sentences

Four-point test per edge (connective / state named in record words / no tool, id or snake_case / strength equals the condition), plus the derivation sentence + records + depended-on rule -> resolving action:

- S1. P4 <- P2: "The item list is fixed only after every earlier refill confirmation that has reached the last day it may ship stands answered by a coverage-billed line for each item it names." Connective "only after"; state form; no tool. Resolving write: the only coverage-billed line writer of this difficulty is `ship_covered_refill_e8c1261e`, and the only extended policy that sizes such a line is P2, whose rule covers disposable filters (A7038) only ("ships against the patient's refill confirmation once that confirmation reaches the last day it may ship"). Strength defect: "has reached the last day it may ship" literally includes every confirmation whose last ship day has already passed. A passed confirmation can no longer be shipped against (base `confirmation_fresh`: "an older confirmation needs a new contact"), so for such a confirmation left unanswered the waited-on state cannot be brought about by any lawful write. The declared `condition` ("every refill confirmation on the enrollment that has reached its last shipping day is followed, on or after its contact date, by a coverage-billed shipped line of each item it names") has the same breadth. The edge is also broader than its depended-on policy: a confirmation that names an item other than A7038 needs a coverage-billed line that P2's rule does not size. -> SOURCE-POLICY RED (sentence broader than the edge, second reading); demonstrated against task 0's world in `0.md`.
- S2. P4 <- P3: "No item list is fixed until each coverage-billed line that shipped a cushion item not fitting the recorded mask style stands answered by a no-charge reship of the fitting cushion item." Connective "until"; state form; the only no-charge writer is `send_no_charge_replacement_8a217fc0`, and P3's own rule describes that write ("replacing that line with replacement reason wrong_item"). Single reading. PASS (P3's compute picks only the newest non-fitting cushion line, while the sentence says "each". That difference matters only on a world with two such lines; check per task).
- S3. P4 <- P1: "The item list is fixed only after the enrollment's continued-use date carries the date credited to the newest proof of continued use on the device record." Connective "only after"; state form; the only writer of `last_continued_use_date` is `record_continued_use_proof_c97fce72` (P1). Reading defect: "the newest proof of continued use on the device record" is not what P1 records. P1 records the *governing* proof ("when the download that proves continued use has a window that ended within the last 90 days, that download governs and a practitioner note is not used"), which can be older than the newest proof on the record (a newer practitioner note). The `condition` repeats "equals the date credited to the newest proof". -> SOURCE-POLICY RED where a world has a note newer than a governing download; demonstrated in `0.md`.
- S4. P6 <- P5: "A standing-order cushion line is booked only after the recorded mask style matches the style that the patient's own interface and cushion lines establish." Connective "only after"; state form; single writer `update_mask_style_bfa4256b`; P5's rule describes the evidence. Single reading. Form defect: the depended-on rule P5 restates the dependency in its own words, "the record is changed to the style that evidence establishes before any standing-order line of a cushion item ships" (a second wording in the depended-on rule). Same scope and same conclusion, so no second terminal state can be demonstrated -> observation. The base `resupply_item_compatibility` also says "A change of style is recorded as a preference update before items of the new style ship". This base cross-problem order does not ground the edge alone (P6 carries its own sentence) -> observation.
- S5. P8 <- P6: "The rush charge for a shipment is fixed only after every standing-order line due on the enrollment stands booked on that shipment." Connective "only after"; state form; single self-pay line writer `book_subscription_line_cd282959`; P6's rule gives "due" ("once the cushion supply on the enrollment is within the schedule's ship-window days of running out"). PASS.
- S6. P8 <- P7: "No rush charge is fixed until every earlier shipment that went out by ground carries its ground shipping charge." Connective "until"; state form; single ground-charge writer `book_ground_shipping_charge_38ca3aab`. The condition adds "and owes a ground charge", which the sentence carries implicitly through "its ground shipping charge" (a shipment that owes none has none). PASS.
- No rule names a tool, a policy id or another problem's id. Apart from S4's restatement, no rule states a cross-problem order that grounds no declared edge. P2's "once that confirmation reaches the last day it may ship" binds P2 to an existing confirmation's date, not to P4's write, because a confirmation recorded today has not reached its last day.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- P1 / `resupply_order_continuity`: "a newer proof of continued use only from a compliance download or practitioner note of the kind continued_use_basis accepts; a patient's own account of use is never proof" — followed (restated). Other sentences (renewed order, hold clearing, auto-ship) are not touched. `overwrite: []` — consistent.
- P2 / evt_shipment, refill_confirmation, schedule_match, item_compatibility, shipping, self_pay_pricing:
  - O1. Base `resupply_evt_shipment`: "the units shipped on one line cover units divided by qty times months calendar months from the ship date, and covers_through_date is the day before the same day of the month that many months later". P2 handles the same quantity differently in two places, with no `overwrite`. (a) "The months a line covers are counted from an anchor" (the run-out day or the confirmation date, not the ship date). (b) Its filters-per-month tiers ("otherwise one a month", "none") ship fewer units a month than the schedule's qty (2/month on Medicare). By the base formula those units cover units/qty*months, so 1 filter covers half a month, a figure the base convention cannot even express as a covered-through date. -> undeclared override (anonymous intermediate), SOURCE-POLICY RED at charter level. Whether it costs a task a second scored answer is shown per task (`covers_through_date` of the P2 write).
  - Base `confirmation_fresh` (ship no later than lead days after the confirmation) — followed (P2 ships on the last allowed day). Base "Quantities not shipped in an earlier period are never added to a later line unless missed_cycle_backfill_allowed" — followed (lapsed months are dropped).
- P3 / `resupply_replacement_rules`: no-charge, wrong_item, one per reason per original line — followed; base is silent on units and covered-through, and P3 adds them. `overwrite: []` — consistent.
- P4 / `resupply_refill_confirmation`: the superseded clause "A refill is confirmed only on the patient's own statement of the items wanted and their supply status." is declared and replaced. The rest (channels, not_exhausted -> declined, freshness, caregiver) is inherited. Merged semantics are unique.
- P5 / item_compatibility, order_continuity: style-before-items sentence followed; nothing overridden.
- P6 / refill_confirmation, self_pay_pricing (declared twice), evt_shipment, schedule_match, item_compatibility, shipping: both overrides declared. Base "The subscription has no unit limits but still follows max_months_per_shipment" — followed for months; made-up units ride on base backfill (Self-Pay `missed_cycle_backfill_allowed: true`). Base evt_shipment covered-through formula is undefined on Self-Pay (qty 0 = no limit), and P6 states its own. No undeclared conflict found.
- P7 / `resupply_shipping`: the ground-fee clause is declared and replaced; "One shipping charge is taken per shipment" is followed.
- P8 / `resupply_shipping`: the expedited clause is declared and replaced (the replacement drops the base transit-time promise `expedited_transit_business_days`). O2: `ground_credit` tier 2 ("when a ground shipping charge is already booked for today's shipment, that charge is credited", while an expedited charge is also booked for that shipment) leaves two shipping-charge lines on one shipment against the inherited base sentence "One shipping charge is taken per shipment, whatever the number of item lines", and no `overwrite` names it. Observation at charter level; consequence only on a world where today's shipment already carries a ground charge.

### factor_ladders

Per policy (label as declared -> label after the honesty test; multi-source = some non-fall-through tier is a conjunction over distinct records; cross = cross_difficulty):

| Policy | Factors (declared effect) | Honest-label result | Counts after tests | Multi-source | Cross-difficulty |
|---|---|---|---|---|---|
| P1 | use_hours_bar (p), window_nights_bar (p), four_hour_share_bar (p), credited_night (m), governing_kind (m) | credited_night only selects which date is credited (visit / taken / window end), i.e. a value; governing_kind tier 3 is MX(download, note) vs single picks, a different selection algorithm -> method holds | 5 factors; >=3 p; >=1 m | window_nights_bar (class modem parameter AND the download's pull lag) | pap x4 (pap_service, pap_holdings, class params) |
| P2 | line_span (p), monthly_filter_rate (p), lapsed_month_anchor (m), held_supply_months (p) | lapsed_month_anchor: every tier is `MONTHS(anchor, ship date)` with anchor in {run-out day, confirmation date, ship date (=0)}, the same formula with a different date substituted -> a parameter, not a method | 4 factors; 4 p; **0 m** | line_span (enrollment_date AND count of filter lines) | pap (monthly_filter_rate) |
| P3 | reship_monthly_rate (p), period_share (m), remainder_start (m), letdown_months (p), went_without_spares (p) | remainder_start: `MONTHS(start, wrong_end)` with start in {handling day, earlier supply's run-out, replaced line's ship date}, the same formula -> parameter; period_share chooses between a remainder count, zero and the full span counted with the +1 convention -> method holds | 5; 4 p; 1 m | reship_monthly_rate (fitting item's latest line vs schedule allowance) | none |
| P4 | nocharge_period_rule (m), cash_period_rule (m), answering_lead (p), proof_recency_lead (p), tenure_lead (p) | both methods change which records count -> hold | 5; 3 p; 2 m | answering_lead (confirmations AND declines) | none |
| P5 | evidence_lines (m), look_back_span (p), candidate_pick (m), switch_threshold (p) | both methods hold (record selection; argmax vs latest) | 4; 2 p; 2 m | none clearly | none |
| P6 | unit_basis (m), cycle_months (p), missed_month_makeup (m), owner_discount (p) | missed_month_makeup: tiers are `2*rate`, `rate`, `0`, i.e. k*rate with k in {2,1,0}, a number substituted (cf. P3 letdown_months, labelled parameter for the same shape) -> parameter; unit_basis holds | 4; 3 p; 1 m | owner_discount (pap purchase sale AND subscription age) | pap (pap_billing) |
| P7 | compared_value (m), free_ship_floor (p), late_booking_share (p), parcel_rate (p) | compared_value holds (different value formulas) | 4; 3 p; 1 m | parcel_rate (no mask/cushion line AND a non-filter line) | none |
| P8 | rush_parcel_fee (p), ground_credit (m), recent_payer_share (p), first_rush_softener (p) | ground_credit: `fee - credit` with credit in {schedule ground fee, the booked ground charge, 0}, a fee substituted into the same formula (the skill's own example of a mislabel) -> parameter | 4; 4 p; **0 m** | rush_parcel_fee (all lines cushions/filters AND units <= 6) | none |

- Tier counts: every ladder has exactly three tiers, pairwise disjoint as stated, every tier stated in the rule (condition and value or method) and implemented in compute.
- Distinct outcomes: no two tiers of one ladder select the same value or method under the charter's parameters (P1 class values 4 h / 30 nights / 70 % or 0 differ from 1.5/3.0, 21/25, 40/55; P2 allowance is 2 or 4 vs 1 vs 0; P6 Self-Pay discount 10 vs 12/15; P7 Self-Pay minimum 75 vs 100/85, ground fee 6.95 vs 3.95/4.95; P8 expedited 14.95 vs 12.95/13.95).
- Business realism (observations, not demonstrable as unreal): P2's baseline/fall-through "one disposable filter a month" and "one month" span sit below the schedule allowance (2 a month, 3 months) that suppliers ordinarily ship. P1's 55 % bar for a stale note is lower than the 70 % class bar a patient with no note faces. P7's "charge booked late is reduced" is a goodwill rule. None of these reaches a tier no business would publish.
- Baselines: each `baseline.rule` is a sentence of the rule, its `params` are charter keys, and every factor's fall-through tier equals its `baseline` binding. P6's baseline.rule says "for the schedule's maximum months per shipment" while the compute baseline keeps `MN(span, order_left)`. The two diverge only when the order's remaining validity is shorter than 3 months (checked per task).

### findings

- F-G1 SOURCE-POLICY RED — prerequisite sentence S1 (P4 <- P2) is broader than the write that resolves it ("has reached the last day it may ship" includes passed confirmations, which no lawful write can answer). Bears on task 0 (demonstrated in `0.md`).
- F-G2 SOURCE-POLICY RED — prerequisite sentence S3 (P4 <- P1) waits on "the date credited to the newest proof", which differs from the governing date P1 records whenever a newer note is set aside. Bears on task 0 (demonstrated in `0.md`).
- F-G3 SOURCE-POLICY RED (charter level) — undeclared override O1 of the base covered-period convention by P2 (anchor-counted months; sub-allowance monthly rates). Bears on task 0 (P2 write `covers_through_date`; see `0.md`).
- F-G4 SOURCE-FACTOR RED — P2 has no honest `method` factor (lapsed_month_anchor is a substituted date in one formula). Bears on task 0.
- F-G5 SOURCE-FACTOR RED — P8 has no honest `method` factor (ground_credit substitutes a fee into `fee - credit`). Bears on task 1.
- F-G6 SOURCE-FACTOR (label) — remainder_start (P3), missed_month_makeup (P6) and, more weakly, credited_night (P1) are labelled `method` but only substitute a value. Their policies keep >= 1 honest method, so the counts hold. Recorded against tasks 0 and 1 as label defects.
- F-G7 Observation — P5's rule restates the P6 <- P5 dependency ("before any standing-order line of a cushion item ships"); the base item_compatibility sentence states the same order. Task 1.
- F-G8 Observation — rule/compute divergences 1–8 in rule_compute_equivalence; each is checked for a consequence on its task's world in that task's file.
- F-G9 Observation — O2 (P8 tier 2 vs base "One shipping charge is taken per shipment"); docstring sequence hints; `book_subscription_line_cd282959.shipping_method` not fixed by P6's rule. Task 1 checks the consequence.

## closing_checklist

Written after both reveals (about 19:18Z UTC). The charter-global section above was frozen first (mtime 19:16:10), and its header "freeze time" was a forward estimate. It is not edited.

- Audit files: `0.md` and `1.md` match tasks 0 and 1 one to one; `_difficulty.md` sits alongside them; revision 0, no older revisions. Comparison sections: task 0 — **not PASS** (SOURCE-POLICY, SOURCE-CHAIN, SOURCE-FACTOR, SOURCE-TASK RED). Task 1 — policy, chain and unique solution PASS; **SOURCE-FACTOR RED**.
- Coverage and scope: `charter_scope` task 0 = {P1, P2, P3, P4}, task 1 = {P5, P6, P7, P8}. Pairwise disjoint, jointly cover all 8 extended policies, matching the scope inferred before the reveal. Task tools are closed (4 + 4, each used once). uuid8s are independent (see action_binding_and_uuids).
- Trees: each has 3 prerequisite problems, 3 value_input edges (>= 2), an owner=user root and no cycle. The difficulty's graph is a DAG with no cross-task references. Task 0's P4 <- P2 edge fails its own declared condition (F-G1 / 0.md F-0.1, F-0.4).
- Factors: every computation declares a definite baseline that differs from gold, and every factor bears weight on its task's world (all figures equal GT `factor_sensitivity`). Two policies (P2 in task 0, P8 in task 1) have **no honest method factor** (F-G4, F-G5). Three further method labels are dishonest (F-G6).
- Gates: not re-run by this auditor. The difficulty does not close, and Step 0 limits the auditor to citing the coordinator's snapshot (check_extended, check_task_tools, replay --check, check_solvability, check_compute, check_grounding, check_cache_diff and check_cross_fire rc=0; check_traceability rc=1, pre-render by design).
- **Difficulty result: does NOT pass the source-layer audit.** Open REDs: F-G1, F-G2, F-G3 (SOURCE-POLICY; costs task 0); F-0.4 (SOURCE-CHAIN, task 0); F-G4, F-G5 (SOURCE-FACTOR; tasks 0 and 1). Each task's GT equals the auditor's principal blind reading on every scored value. Every RED concerns a second defensible reading, an unreachable declared condition, or a factor label, not a computation error.

## revision_2

### charter_global_frozen (revision 2)
- Written before any round-2 task JSON was opened. Rev-0 text above is untouched.
- Inputs: `resupply.extended.yaml` sha256 5f1b4204a2df920c6d79ad6c06d087bfebc4bbbb1ad1978963967e234f787a17 and `task_tools.py` sha256 c78e74e414db6c9e9e3865b9cc78c0cda6addf9c73ed63d792f76e0ab5093afd. Both changed from round 1, so every charter-global section is re-derived in full below. The views are unchanged: 0.view 709056…a850a, 1.view a586c209…e5204f2a5e3.
- Base section: still verbatim equal to `blueprint/products/resupply.yaml`. The tool names and uuid8s are unchanged, and no tool body reads, refuses or branches; each performs one create or update.

### verification of round-1 findings (against the new artifacts)

| Item | Round-1 defect | Revision-2 text / compute | Status |
|---|---|---|---|
| F-G1 (S1) | P4<-P2 sentence covered passed confirmations and non-filter items | "The item list is fixed only after every earlier refill confirmation naming disposable filters whose last shipping day falls on the day of the request stands answered by a coverage-billed disposable-filter line shipped on or after its contact date." The `condition` matches it (A7038, last day = handling day). The only resolver is `ship_covered_refill_e8c1261e` under P2, which sizes A7038. | **closed** |
| F-G2 (S3) | P4<-P1 sentence said "newest proof" while P1 records the governing proof | "... the enrollment's continued-use date is no older than the credited date of the proof of continued use that governs on the device record." The condition says "on or after". P1's result is now `governing if governing > F('last_continued_use_date') else F(...)`, and P1's opening sentence speaks of the proof "that governs". | **closed** |
| F-G3 (O1) | P2 undeclared override of the base covered period ("counted from an anchor") | The anchor wording is removed ("Months that lapsed before the line ships are dropped ... counted as the whole months from a lapse date to the ship date"). An overwrite of `resupply_evt_shipment` is declared, replaced by "A disposable-filter line covers the months shipped, counted from the ship date ...". This yields one covered-through date. | **closed** (new observation N1 below) |
| F-G4 | P2 had no honest method | `monthly_filter_rate` is now `method`. Tier 1 ships the allowance as it stands. Tier 2 is a genuinely different algorithm: `MN(allowance, ceil(allowance*newest_avg/8))`, scaled to measured use. Tier 3 is a fixed 1. `lapsed_month_anchor` is relabelled parameter. | **closed** |
| F-G5 | P8 had no honest method (fee substitution) | `ground_credit` now selects a pricing algorithm: upgrade `fee - G`, split `G + (fee - G)/2`, or full `fee`. Tier 2 is a different formula, so the method is honest. | **closed** |
| O2 | P8 tier 2 left two shipping charges on one shipment | The "booked ground charge for today's shipment" tier is gone. | **closed** |
| F-G6 | credited_night, remainder_start, missed_month_makeup mislabelled method | All three are now `parameter`. Methods remaining: P1 governing_kind, P3 period_share, P6 unit_basis. | **closed** |
| F-G7 | P5 restated the P6<-P5 order | P5's rule no longer carries "before any standing-order line ... ships". The base `resupply_item_compatibility` sentence remains, as base must. That is an observation only, because P6 carries its own prerequisite sentence. | **closed** |
| F-G8.1 | P1 "newer than" had no compute | result compares with the enrollment date ("a date that is not newer leaves the enrollment as it is") | closed |
| F-G8.2 | P1 credit scope / any vs newest note | The rule now says "The date credited to the newest download ... when the newest re-evaluation documenting benefit is dated on or no more than 7 days before the day the download was taken". Compute: `note_date <= dl_taken and DAYS(note_date, dl_taken) <= 7`. | closed |
| F-G8.3 | P2 decline window / decline after confirmation | "dated less than two whole months before the ship date" (= within_months 2); "dated on or before the confirmation date and no more than 30 days before it" (compute adds `last_decline <= confirmed_on`) | closed |
| F-G8.4 | P4 alt-tubing "only"; reversals | The cash tier now reads "shows no self-pay line for an item of the recorded equipment but shows one for the tubing type not in use" (= compute). Reversed lines are now declared to "still count", with the scoping sentence "These supply dates serve the item list only and do not change when a coverage-billed line may ship." | closed (see N2) |
| F-G8.5 | P5 'all' / 'branch' coverage | 'all' mode counts "shipped lines and no-charge lines of any reason alike" (`al_*`, `dal_*` count every no-charge line); 'branch' mode reads "and no other line does" | closed |
| F-G8.6 | P6 rounding / truncation / missed basis / standing-order identity | All four are now stated in the rule and match compute: rounding up "the result of dividing those branch units by three"; units "rounded down to a whole unit"; the missed months "of the latest standing-order item ... at that line's units per month"; and "The standing-order history is read from the enrollment's self-pay cushion lines that went out by ground". The baseline.rule now includes the order-validity cap. | closed |
| F-G8.7 | P7 newest-uncharged vs newest-then-check | Rule: "the newest such shipment, when it is found without a shipping charge, has the charge ... booked" (= compute). The overwrite replaced_by matches. The P8<-P7 sentence now waits on "the newest shipment that went out by ground before the day of the rush". | closed |
| F-G8.8 | P8 min > 0 | Tier 1 is stated as "... and that minimum is above 0.00" | closed |
| F-G9 | docstring sequence hints; P6 shipping_method unfixed | The docstrings no longer contain "may be shipped against it", "already on file" or "next to today's item lines". P6 rule: "A standing-order line travels expedited when the patient asks for faster shipping of it, is collected at a branch when the patient asks to collect it, and otherwise travels by ground." The remaining "before the call" refers to read lookups only. | closed |

### re-derived charter-global checks (revision 2)
- policy_conflict_scan: the same 8 subjects, tools and splits as rev 0. No two policies decide one quantity, and the cross reads are unchanged (pap).
- rule_compute_equivalence: re-swept policy by policy. Every rev-0 divergence is closed (table above). No new divergence was found between any changed sentence and its binding.
- action_binding_and_uuids: unchanged tools and uuids; one `(target_tool, computes)` per policy; no prerequisite judging in the bodies.
- prerequisite_graph: the same 6 edges. Every `policy_source` is verbatim in its own rule, every `resolved_by` is the depended-on `target_tool`, every gate is a binding of the blocked compute, all are state form with no fallback, and the graph is acyclic (checked programmatically).
- prerequisite_sentences: S1–S6 each pass the four-point test. Each has one resolving writer (S1 P2/A7038; S2 P3; S3 P1; S4 P5; S5 P6; S6 P7). No rule names a tool or policy id, and the only order sentences in any rule are the six edge sentences.
- override_declarations: the rev-0 conclusions stand, plus P2's new declared overwrite (see N1).
- factor_ladders (revision 2):

| Policy | Factor count | Parameter | Method |
|---|---|---|---|
| P1 | 5 | 4 | 1 (governing_kind) |
| P2 | 4 | 3 | 1 (monthly_filter_rate) |
| P3 | 5 | 4 | 1 (period_share) |
| P4 | 5 | 3 | 2 |
| P5 | 4 | 2 | 2 |
| P6 | 4 | 3 | 1 (unit_basis) |
| P7 | 4 | 3 | 1 (compared_value) |
| P8 | 4 | 3 | 1 (ground_credit) |

  Every ladder has 3 tiers stated in the rule. No two tiers of a ladder share a value or method, and all labels pass the honesty test. Multi-source and cross-difficulty factors are as in rev 0 (P1 window_nights_bar, P2 line_span, P6 owner_discount, etc.; cross pap in P1, P2 and P6).

### new observations (revision 2; no demonstrable consequence on either world)
- N1. P2's overwrite supersedes the whole base clause "the units shipped on one line cover units divided by qty times months ... that many months later". That clause governs every item, but the replacement speaks only of disposable-filter lines. Read literally, the merged policy leaves non-filter coverage lines with no covered-period convention. Neither task writes a non-filter coverage line (task 0's reship states its own covered-through date), so this is an observation.
- N2. P2 ("a line a payer later took back still counting because its filters were delivered") and P4 count reversed coverage lines toward an item's run-out. The base `resupply_evt_line_reversal` says "The reversed line no longer counts for resupply_msr_item_covered_through", and P2 neither cites it nor declares an overwrite (P4 scopes its dates to the item list; P2 does not). Neither seed has a `resupply_line_reversal` row, so there is no consequence.
- N3. P8 `recent_payer_share` ladder, tier 3, still reads "the full credited fee (100 percent)", while the rule now says "the full priced rush". The ladder text is stale wording; value and compute agree.

### findings (revision 2)
No charter-global RED remains open. N1–N3 are observations.

### closing_checklist (revision 2)
- Written after the round-2 reveals at 20:22:58Z. The revision-2 charter-global section was frozen at 20:22:21Z.
- Audit files: `0.md` and `1.md` match the tasks one to one, with `_difficulty.md` alongside. Revision 0 text is preserved and revision 2 is appended. Both revision-2 comparison sections carry PASS on all four relationships.
- Coverage and scope: task 0 = {P1, P2, P3, P4}, task 1 = {P5, P6, P7, P8}. The scopes are disjoint and cover the charter. Task tools are closed: each is used once, and the uuid8s are independent and unchanged.
- Trees: 3 prerequisite problems each, 3 value_input edges, an owner=user root, acyclic. The difficulty-wide graph is a DAG.
- Factors: 4–6 per computation, each with >= 2 parameter and >= 1 honest method factor. Every factor bears weight against an honest baseline, and every all-baseline number is definite and differs from gold. Each task has a multi-source and a cross-difficulty factor whose pap rows are seeded.
- Gates: not re-run by this auditor; the coordinator's round-2 snapshot is cited (all rc=0 except check_traceability, which lists only the 8 unlock names, pre-render by design).
- Open items: none RED. Observations N1 (P2 overwrite replacement narrower than the superseded base clause), N2 (reversed lines counted without citing `resupply_evt_line_reversal`), N3 (stale "credited fee" wording in P8's share ladder) and task 0 F-0.7 (weak P3 near-miss).
- **Difficulty result (revision 2): passes the source-layer audit.**

## revision_3

### entry (revision 3)
- Upstream gates, from `bash /tmp/erl0057_coord/gates.sh pap_supply_replenishment` run at the repository root:
  - check_extended: EXTENDED OK
  - check_task_tools: TASK TOOL CONTRACT OK
  - replay_tasks: REPLAY OK
  - check_solvability: SOLVABILITY OK
  - check_compute: COMPUTE OK
  - check_grounding: GROUNDING OK
  - check_cache_diff: CACHE-DIFF INFO
  - check_cross_fire: SCOPE OK
  - All 8 lines are OK/INFO, so the audit proceeds.
- Views rebuilt with `make_views.py`: 0.view 709056042e52d65db595be31eb4939452dbb384c02e41a5caf1791e6712d850a and 1.view a586c209f3475495d91b85963d91bb965c782aa4cfe168318e681e5204f2a5e3, both unchanged.
- Changed inputs:
  - `resupply.extended.yaml` sha256 5f4bdba304b6ee38b3dbd4494740dcc158ce019ff9883d21125ea5710459f2d6
  - `task_tools.py` sha256 c3ae066acb63a2b52db41b0abbd1251d80b9f58de7f0c9636a6a2d2adb2efeef
  - Both changed, so the charter-global checks are re-derived below.
- Base section: still verbatim. Tool names and uuid8s are unchanged. Each body performs one create or update; the only conditional is the `customer_id` / `previous` fallback when the holding lookup is empty, and no body checks a prerequisite.
- Inputs read: the render report `audits/render_source/pap_supply_replenishment/render_r1_source_mismatches.md`. No task JSON was read before the revision-3 freeze.

### verification of render-found items R1–R8 and revision-2 observations N1–N3

| Item | Revision-3 text | Status |
|---|---|---|
| R1 / N1: P2 overwrite wider than replacement | replaced_by: "For a coverage-billed disposable-filter line booked under this rule, and only for such a line, ... every other line remains under the base covered-period rule." | closed (see N5) |
| R2: P7 overwrite wider than replacement | "For a self-pay shipment that went out by ground, and only for such a shipment, ...; every other shipment remains under the base ground-shipping rule." Coverage-billed ground shipments keep the base `ground_shipping_fee` (0.00 on the five coverage schedules). | closed |
| R3: period_share depends on remainder_start's output | Restructured. remainder_start now decides `start_date` (parameter: handling day / earlier supply's run-out / replaced line's ship date). period_share decides `months_covered` as a function of start and end: whole months, zero, or whole months + 1 (inclusive count). That is three different counting functions of the same inputs, so the method label is honest. The bindings are disjoint, and baseline.rule = replaced line's rate times inclusive months from its ship date = the replaced units. | closed at the policy layer (the shared term "start date" remains; the KB audit judges document coupling) |
| R4: P8 rule vs compute when minimum = 0 | Rule: "otherwise, whether no item line is booked on today's shipment or the schedule has no free-shipping minimum above 0.00, the rush is priced at the full rush fee". Compute tier 2 adds `P(min) > 0`. | closed |
| R5: P6 fractional missed months | Rule: "counted in whole months with a part month not counting". Compute: `missed: int(MX(0, 12 - ...))`. | closed (see N4) |
| R6: update_mask_style docstring | The "decides which ... items its standing order ships" claim is removed. | closed |
| R7: P6 discount scope | replaced_by: "On the Self-Pay Supply Subscription ... it applies to every self-pay line of the subscription, standing-order lines, branch purchases and add-on items alike". The base clause "a beyond-schedule self_pay line on a coverage schedule receives no discount" is outside the superseded text and still governs. | closed |
| R8: P4 phone channel | The overwrite is scoped "For a refill request the patient places on a phone call, and only for such a request". Rule: "A request is placed on a phone call only on a schedule whose accepted channels include phone calls; on a schedule that accepts no phone call, such as the Self-Pay Supply Subscription, no request is recorded on the call." | closed |
| N2: reversed lines | P2: "this run-out date serves only the months dropped here, and when a covered line may ship still follows the base covered-through measure, from which a reversed line drops out". P4 keeps its item-list-only scoping. | closed |
| N3: stale P8 ladder wording | Tier 3 now reads "the full priced rush (100 percent)". | closed |

### re-derived charter-global checks (revision 3)
- rule_compute_equivalence: re-swept, with no divergence apart from N4 below.
- action_binding_and_uuids: unchanged.
- prerequisite_graph: the same 6 edges. Each is verbatim in its own rule, its resolver is the depended-on target tool, its gate is a binding of the blocked compute, it is state form, and the graph is acyclic.
- prerequisite_sentences: S1–S6 unchanged and passing. Only the edge sentences carry an order (P4 has 3, P6 has 1, P8 has 2), and no rule names a tool or policy id.
- factor_ladders: unchanged except P3. P3: 5 factors, 4 parameter, 1 method (period_share). Every policy has >= 2 parameter and >= 1 honest method factor. Every ladder has 3 tiers stated in the rule, and every baseline.rule sentence is in its rule.

### override_declarations: scope sweep (each overwrite vs the base lines it still governs)
- P2 / evt_shipment: scoped correctly to P2's filter lines (but see N5).
- P4 / refill_confirmation sentence 2: scoped to phone-call requests.
- P6 / self_pay_pricing: scoped to the Subscription.
- P7 / shipping (ground): scoped to self-pay ground shipments.
- P8 / shipping (expedited): a full replacement. The transit-time promise is restated in the rule.
- **P6 / refill_confirmation lead-days sentence: R9, a new defect introduced in revision 3.**
  - The replaced_by (and the identical P6 rule sentence) reads: "A standing-order line on the Self-Pay Supply Subscription for a patient who chose automatic shipments ships on its cycle without a refill confirmation, and only such a line is exempt; every other line ships on a refill confirmation and no later than the schedule's refill lead days after it, ...".
  - It supersedes only the lead-days sentence, yet it now asserts a confirmation requirement for "every other line". The unsuperseded base sentence 1 of `resupply_refill_confirmation` says "On a schedule whose `auto_ship_allowed` is false, or for a patient whose auto_ship is false, every shipment of coverage-billed items must rest on the patient's own refill request". So a patient who chose auto-ship on a schedule that allows it needs no request; Commercial HMO and Commercial PPO both have `auto_ship_allowed: true`.
  - Same situation, two conclusions: an auto-ship patient's coverage-billed line on the Commercial PPO Resupply Schedule. Base sentence 1 says it ships without a request; the P6 replacement says it is not exempt and ships on a refill confirmation.
  - The replacement also reaches lines the base clause never governed: no-charge reships under `resupply_replacement_rules`, and self-pay purchases.
  - The round-2 text ("while a line that rests on a refill confirmation still ships no later than ...") was correctly scoped, so this is a regression introduced by the round-3 rework.
  - **SOURCE-POLICY RED.** The consequence on task 0 is demonstrated in `0.md` § revision_3.

### new observations (revision 3)
- N4. P6: "the standing-order months missed ... are 12 less the months that the standing-order lines ... cover ..., counted in whole months with a part month not counting".
  - The rounding point is ambiguous. It can be read as floor(12 - covered), which is the compute, or as 12 - floor(covered); a world with 10.5 covered months gives 1 vs 2.
  - Task 1 covers exactly 11 months (11 one-unit lines at 1 per month), so there is no consequence there.
- N5. The P2 replacement's "every other line remains under the base covered-period rule" literally reaches two kinds of line that state their own covered-through date without declaring an overwrite:
  - P6 standing-order lines (self-pay `resupply_item_shipped`);
  - P3 no-charge reships, which sit outside `resupply_evt_shipment`'s subject.
  - The base formula "units divided by qty times months" gives no definite date for either: the Self-Pay limits are qty 0, meaning "no limit", and reships are not that clause's subject. So there is no second scored value; this is an observation.

### findings (revision 3)
- **R9: SOURCE-POLICY RED.** It is new and is a regression.
- Every other round-2 and render item is closed. N4 and N5 are observations.

### closing_checklist (revision 3)
- Reveals at 05:03:04Z; all revision-3 frozen sections precede them (05:02:29Z / 05:02:58Z).
- Coverage and scope: task 0 = {P1–P4}, task 1 = {P5–P8}. Disjoint and complete. Tools are closed and the uuid8s are unchanged.
- Trees and factors: both tasks still hold. Every factor bears weight, labels are honest, and the GT figures equal mine.
- Gates: the coordinator script's 8 lines are cited above (all OK/INFO); check_traceability is not part of that script.
- **Difficulty result (revision 3): does NOT pass.**
  - Open: R9, SOURCE-POLICY RED. It is a regression introduced in round 3: P6's confirmation-freshness overwrite now asserts "only such a line is exempt; every other line ships on a refill confirmation". That contradicts the unsuperseded base sentence 1 for auto-ship coverage lines (Commercial HMO/PPO) and reaches no-charge reships and self-pay purchases. Consequence demonstrated on task 0.
  - Observations N4 (P6 missed-month rounding point) and N5 (P2's "every other line" reaches lines that state their own covered-through date) have no consequence on either world.
  - Every render item R1–R8 and every revision-2 observation N1–N3 is closed.

## revision_4

### entry (revision 4)
- Upstream gates from `gates.sh` (repo root):
  - EXTENDED OK
  - TASK TOOL CONTRACT OK
  - REPLAY OK
  - SOLVABILITY OK
  - COMPUTE OK
  - GROUNDING OK
  - CACHE-DIFF INFO
  - SCOPE OK
  - All 8 lines are OK/INFO, so the audit proceeds.
- Views rebuilt: 0.view 709056042e52d65db595be31eb4939452dbb384c02e41a5caf1791e6712d850a and 1.view a586c209f3475495d91b85963d91bb965c782aa4cfe168318e681e5204f2a5e3 (unchanged).
- `resupply.extended.yaml` sha256 c393fb9777bd77e74935bcc85f4e329c9c02f3c1fdd91e3d176a2c62c6ae29d0 (changed), so the charter-global checks are re-derived.
- `task_tools.py` sha256 c3ae066acb63a2b52db41b0abbd1251d80b9f58de7f0c9636a6a2d2adb2efeef (unchanged since revision 3), so the tool sections carry forward.
- Base section still verbatim. Every overwrite's `replaced_by` is verbatim in its policy's rule. No task JSON was read before this freeze.

### overwrite scope sweep (each replacement vs the superseded clause's domain and the in-force base sentences)
- **R9: closed.** P6 / `resupply_refill_confirmation` lead-days sentence.
  - New text: "A standing-order line on the Self-Pay Supply Subscription for a patient who chose automatic shipments ships on its cycle without a refill confirmation, while a line that rests on a refill confirmation still ships no later than the schedule's refill lead days after it ... and an older confirmation needs a new contact; whether a coverage-billed line must rest on a refill request still follows the base rule, and a no-charge reship, which answers the line it replaces, is not held to this window."
  - The window again governs exactly the lines that rest on a confirmation, which is the superseded clause's domain.
  - Base sentence 1 ("On a schedule whose `auto_ship_allowed` is false, or for a patient whose auto_ship is false, every shipment of coverage-billed items must rest on the patient's own refill request") is expressly left in force. An auto-ship Commercial HMO/PPO coverage line again ships without a request.
  - Reships are excluded, which agrees with `resupply_replacement_rules`, a base policy that requires no request.
  - No in-force base sentence is contradicted.
- **N5: closed.** P2 / `resupply_evt_shipment` covered-period clause.
  - New text: "every other line that an item limit dates remains under the base covered-period rule, while a no-charge reship, which counts toward no limit, and a standing-order line on the Self-Pay Supply Subscription, which has no unit limits, take the covered-through dates their own rules state."
  - The base clause keeps every line its formula actually dates, including other items' coverage lines and beyond-schedule self-pay lines on coverage schedules (the item's `limit_<item>` exists there).
  - Reships (base: "without counting toward any limit") and Self-Pay standing-order lines (qty 0, "no limit"), which the base formula could not date, take P3's and P6's stated dates.
  - Other Self-Pay non-standing lines (branch purchases, add-ons) remain as undated as under base, so nothing changes for them.
- **N4: closed.** P6 missed months: "the difference rounded down to a whole month and never below zero" = compute `int(MX(0, 12 - covered))`. One reading.
- P6 / `resupply_self_pay_pricing`: "applies to every self-pay item line of the subscription ...; a shipping charge is not an item line and takes no discount, its amount following the shipping rules".
  - The superseded clause governed the Subscription's self-pay lines and the replacement governs the same set. Base "a beyond-schedule self_pay line on a coverage schedule receives no discount" stays in force.
  - The shipping-charge carve-out agrees with base `resupply_shipping` (charges set there).
  - Consistent.
- P7 / `resupply_shipping` ground clause: "every other shipment that went out by ground remains under the base ground-shipping rule, and an expedited shipment or a branch pickup, which is not a ground shipment, owes no ground charge".
  - The superseded clause governed ground shipments only, so the carve-out matches its domain.
  - Base "Branch pickup is free where `branch_pickup_allowed` is true" (true on all six schedules) and the expedited sentence (P8) agree.
  - Consistent.
- P8 / `resupply_shipping` expedited clause: "charged to the card on file, never to coverage, once for each shipment that goes out expedited, at the rush charge worked out here on the day the shipment goes out; it arrives in the schedule's expedited transit business days".
  - The domain (every expedited shipment) equals the superseded clause's.
  - Base "One shipping charge is taken per shipment" is honoured ("once for each shipment").
  - Consistent.
- P4 / `resupply_refill_confirmation` sentence 2: unchanged (phone-call requests only; "every other refill confirmation remains under the base rule"). The channel sentence (R8) is intact.

### render items R1–R8 (still closed) and re-derived checks
- R1 (P2 scope; now refined by N5) and R2 (P7 scope; refined) remain closed.
- R3: P3 `start_date` / `months_covered` structure unchanged, labels honest.
- R4: P8 "or the schedule has no free-shipping minimum above 0.00" sentence and the compute guard are present.
- R5: closed and refined by N4.
- R6: the tools file is unchanged.
- R7: closed and refined (item lines only).
- R8: P4 channel sentence present.
- Prerequisite graph: 6 edges. Each `policy_source` is verbatim in its own rule, each resolver is the depended-on target tool, each gate is in the blocked compute; all are state form and the graph is acyclic. The only order sentences are the six edge sentences; no rule names a tool or policy id.
- Factor ladders: unchanged from revision 3 (labels, 3 tiers each, every baseline.rule sentence in its rule).
- Rule/compute: no divergence found.
- New defects: none found.

### findings (revision 4)
None RED. R9, N4 and N5 are closed.

### closing_checklist (revision 4)
- Reveals at 05:41:12Z; all revision-4 frozen sections precede them (05:41:07Z).
- Coverage and scope: disjoint and complete ({P1–P4}, {P5–P8}). Tools are closed and unchanged, and the uuid8s are independent.
- Trees: 3 prerequisite problems each, 3 value_input edges, a user-owned root, acyclic.
- Factors: 4–6 per computation, each with >= 2 parameter and >= 1 honest method factor. Every factor bears weight; every baseline is definite and differs from gold. Each task has a multi-source factor and a seeded cross-difficulty (pap) factor.
- Gates: the coordinator script's 8 lines are cited above (all OK/INFO).
- Open items:
  - none RED;
  - R9, N4, N5 closed; R1–R8 stay closed;
  - observation carried forward: task 0 F-0.7, the weak P3 near-miss.
- **Difficulty result (revision 4): passes the source-layer audit.**

## revision_5

### entry (revision 5)
- Upstream gates from `gates.sh` (repo root):
  - EXTENDED OK
  - TASK TOOL CONTRACT OK
  - REPLAY OK
  - SOLVABILITY OK
  - COMPUTE OK
  - GROUNDING OK
  - CACHE-DIFF INFO
  - SCOPE OK
  - All 8 lines are OK/INFO, so the audit proceeds.
- Views rebuilt: 0.view 709056042e52d65db595be31eb4939452dbb384c02e41a5caf1791e6712d850a and 1.view a586c209f3475495d91b85963d91bb965c782aa4cfe168318e681e5204f2a5e3 (unchanged).
- Changed inputs, so the tool sections are re-derived:
  - `task_tools.py` sha256 85c75925f9c38a2c20d84cecb0e2d688eee27bb1c9a8d05c4deea08c31b3f81c
  - `resupply.extended.yaml` sha256 b403368cbce958cb4159342f02e8c19bc30ff0572e963df6e17b5aaa1c232d68 (also changed, although the brief called this round "docstring-only")
- Read: `audits/render_source/pap_supply_replenishment/kb_r1_source_leak.md`. No task JSON was read before this freeze.

### auditor miss disclosed
In revision 0 this auditor read `confirm_refill_request_b3535d21`'s docstring, including "(for example the form A7034,A7037)", and did not flag it, even though "A7034,A7037" is task 0's scored `items_requested`. Revisions 0–4 therefore under-reported a source-layer answer leak in the tool contract (relationship: policy <-> task unique solution; the example hands the agent the answer). It is recorded here and not rewritten into the older revisions.

### leak verification (revision 5)
- `confirm_refill_request_b3535d21.items_requested` now reads: "written as HCPCS codes separated by commas in ascending order, no spaces, each code written in full as one capital letter followed by four digits and named once". No example value remains.
- Scan of all nine docstrings (module + 8 tools) for gold or plausible values on either world:
  - Item lists: no comma-joined code list anywhere.
  - HCPCS codes: they appear only in `ship_covered_refill_e8c1261e`, `send_no_charge_replacement_8a217fc0` and `book_subscription_line_cd282959`, each time as the complete 12-code enum (A4604, A7030–A7039, A7046), which is a definition rather than a hint.
  - Dates, ids, money: no date, no record id, and no amount (2.97, 3.80, 96.90, 6.95, 12.95, 14.95).
  - Numbers: the only ones are "0.00" (the pending-claim amounts) and "2" ("2 decimal places").
  - Enum glosses (nearly_exhausted / not_exhausted, the replacement reasons, the shipping methods, the mask styles) list every member of each set with its business meaning.
  - **Leak closed.**
- Charter scan: no extended-policy field contains a gold string (no comma-joined item list, no 2026 date, no gold amount, no customer name, no record id, no "for example" or "e.g."). "nasal_pillows" occurs only in the style definitions.

### tool contract equality (revision 5)
- I kept no file snapshot from round 4, so the comparison is an AST unparse of every decorator, signature and docstring-stripped body, checked against the source read in revision 0 and the call and branch inventories recorded in revisions 2–4:
  - the same 8 names and uuid8s;
  - the same owners (user: `confirm_refill_request_b3535d21`, `pay_expedited_shipping_41dc5e4a`) and rw;
  - the same parameter lists and types;
  - identical bodies: the same `ctx.find` / `create` / `update` calls and field assignments, and the same `make_id` prefixes and arguments;
  - the only conditional is the empty-lookup fallback.
- Only docstrings changed. The tools still judge no prerequisite.

### charter (revision 5)
- I kept no round-4 file snapshot, so the change is checked by invariants rather than by diff:
  - the base section is verbatim;
  - all 14 round-4 load-bearing sentences checked in revision 4 (R9 / N4 / N5 replacements, R4 / R8 / N2 sentences, edge sentences) are present verbatim;
  - every `replaced_by` is in its rule, and every `superseded_clause` is verbatim in its base policy;
  - every `compute_basis` value is verbatim in its rule;
  - every baseline.rule sentence is in its rule;
  - the prerequisite graph is the same: 6 state-form edges, verbatim, resolvers equal the target tools, gates in compute, acyclic;
  - no rule names a tool or policy id, and the only order sentences are the six edge sentences;
  - factor labels and 3-tier ladders are unchanged;
  - recomputation of all 8 computations, every factor baseline, the all-baselines, the opening contrasts and the skip runs on both worlds reproduces the revision-4 figures exactly.
- No new defect found.

### findings (revision 5)
- The KB-reported answer leak (`confirm_refill_request_b3535d21.items_requested` example = task 0 gold) is **closed**. It was a SOURCE-TASK-class defect present in revisions 0–4 and missed by this auditor until now.
- Nothing open.

### closing_checklist (revision 5)
- Reveals at 09:10:35Z; frozen sections at 09:10:30Z precede them.
- Scope: disjoint and complete.
- Tools: names, signatures and bodies are unchanged, the docstrings are free of answer values, and the uuid8s are independent.
- Trees: 3 prerequisite problems each, 3 value_input edges, a user-owned root, acyclic.
- Factors: every one bears weight against an honest, definite baseline that differs from gold, with labels and counts within bounds.
- Gates: the 8 coordinator lines are cited above.
- Open items: none RED; the KB-reported leak is closed. Observation carried forward: task 0 F-0.7 (weak P3 near-miss).
- **Difficulty result (revision 5): passes the source-layer audit.**
