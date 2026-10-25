# Policy-task audit — road_hazard_claims / charter-global

## charter_global_frozen

- Freeze time: 2026-10-14T23:12Z (written before any task's GT was revealed; holds nothing derived from a revealed GT)
- Auditor: erl-task-policy-audit sub-agent (independent of the instantiator)
- Frozen inputs (sha256, matching the coordinator snapshot `snapshot_r1.txt`):
  - `tasks/road_hazard_claims/hazard.extended.yaml` 47a99398e30157a412ed75fc8ea8f1965f03a318bcb61bfd3086b6741d5228dd
  - `tasks/road_hazard_claims/task_tools.py` 5a00887c368394810ccab935c730f3d892914cc2ad2c0691c1debaf82522e8d1
- Read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/{hazard,tires,card,fleet,alignment}.yaml` (variant parameters and the rules the cross-category reads rest on), the extended charter, `task_tools.py`, and the masked views `.audit_views/policy/road_hazard_claims/{0,1}.json`.
- Masked / not read: every task JSON under `tasks/road_hazard_claims/tasks/`, `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, db closures, `worklog.md` (scenario and difficulty), `plan.md`, any `/tmp/*_0062` scratch, any other scenario, any sibling difficulty's tasks or audits.
- Entry conditions (Step 0): gate snapshot supplied; all seven d_gates green; `validate_scenario` INVALID only on pre-render "required document not found" and `check_traceability` NOT OK only on unpublished unlock tool names (both out of scope, re-run after rendering). Masked views supplied with hashes; recomputed hashes match. Entry conditions complete.
- Base copy: every base key of the extended file (`category` … `policies`) is `==` to `blueprint/products/hazard.yaml` (checked by YAML load). Base section verbatim.

### policy_conflict_scan

Six extended policies, two problem trees inferred from the prerequisite graph:

| Tree | Root (target_tool, owner) | Prerequisites |
| --- | --- | --- |
| A | `hazard_ext_lot_cancellation_refund` (`confirm_life_of_tread_cancellation_58ab2fcf`, user) | `hazard_ext_counter_replacement_posting` (agent), `hazard_ext_outside_replacement_reimbursement` (agent) |
| B | `hazard_ext_store_replacement_authorization` (`authorize_hazard_store_replacement_0d9adf2d`, user) | `hazard_ext_outside_repair_reimbursement` (agent) <- `hazard_ext_outside_tow_reimbursement` (agent) |

- Overlapping subjects: counter posting and store authorization both write `hazard_replacement`; their scopes are disjoint by situation ("already carried out at its counter … claim history does not yet carry it" vs "authorizes in person on the day the store's technician inspects the damaged tire", inspection `event_date=NOW`), and each rule names the other's situation as excluded. The three out-of-area policies all write `hazard_third_party_reimbursement`, distinguished by `reimbursement_type` (replacement / repair / tow) and each restates the out-of-area condition only for its own type. No two policies compute the same quantity for the same situation.
- Triggers / time anchors: the out-of-area replacement judges its full-replacement period on the reimbursement date (NOW) while counter/store use the service date; both are stated in their own rules (no conflict, realism note O11).
- Cross-category read boundaries: reads are confined to the fleet roster / fleet invoice discount / fleet program `national_price_file`, tire-set ticket fields and tire-line parameters, tire events (inspections, rotations), card account status and late fees, and alignment plan status/ticket/purchase date. All are declared in each policy's `cross_category`.
- Scope partition (inferred pre-reveal from the graph; confirmed per task after reveal): tree A covers {lot_cancellation_refund, counter_replacement_posting, outside_replacement_reimbursement}, tree B covers {store_replacement_authorization, outside_repair_reimbursement, outside_tow_reimbursement}. Pairwise disjoint and jointly complete over the six extended policies.
- Conflicts found: C1 (undeclared override of base `hazard_evt_replacement`'s 100-percent sentence) — see findings.

### rule_compute_equivalence

Every compute binding of every policy has a verbatim `compute_basis` quotation located in its own `rule` (checked); sweep back:

- LOT: clock start (open roster enrollment -> enrollment date; pending request -> `created_at`; else NOW), day count (MONTHS(eff, from) <12 actual days ratio; <36 whole 30-day periods / term; else whole months / term), tread-life factor (latest `wear_pattern=even` reading, `MONTHS(date,NOW) < 6`, share thresholds 0.2/0.4), fee schedule, benefits sum (replacement + third-party + roadside amounts), call credit, bundle clawback (same ticket / other ticket within ±30 days), `MX(0,RND(...))`. All match the rule, including the two rounding points (prorated amount; final). No empty promise.
- Counter posting: damage reading/date/position from the latest `wear_pattern=damage` inspection; full window `MONTHS(dmg_date, exp) >= term - full`; base pct; price ladder; four point schedules; clamp 0..100; single final rounding (plus the tier-1 price rounding the rule states). Match.
- Outside replacement: full window `MONTHS(eff, NOW) < full`; months pct; tread basis (<=120 days / 121–365 days less one 32nd floored at min / none); cap uplift; price ceiling; three point schedules; clamp; final rounding. Match.
- Store authorization: today's damage reading; position covered repairs = repair entries + out-of-area repair reimbursements on the position; route (>= max: none; >=1: full//2; else full); price ladder (fleet tender + tires invoice on purchase date with discount / not fleet + instant savings / unit price); fleet points; care; bundle; clamp; final rounding. Match.
- Outside repair / outside tow: size multiplier, card uplift, fleet uplift, repeat-repair / roadside-usage deduction; `MX(0,RND(cap*mult + uplifts - deduction))`. Match.
- Gap (observation O10): every fleet-points/fleet-uplift compute reads `CPARAM('fleet','national_price_file', status='active')` from the customer's active fleet account, without tying it to the account whose roster carries the vehicle; the rule says "the roster of a Crestline fleet account in status active whose program carries…". Equivalent only when the customer holds one fleet account (true in both worlds).
- Gap (observation O7): "covered repair entries" in `counter_repair_points_fx`, `outside_repair_points_fx` and `repair_repeat_deduction_fx` is computed as `hazard_repair` rows only, whereas the store-authorization rule defines a position's "covered repairs" as repair entries plus out-of-area repair reimbursement entries. A world carrying an out-of-area repair reimbursement at those handling times would admit two readings; neither world does (see task files).

### action_binding_and_uuids

- `(target_tool, computes)`: six distinct pairs, one per policy. Share tools contain only finders, identity verification and transfer; no base write tool competes.
- uuid8s: 58ab2fcf, 324c4972, 5f5d3272, 0d9adf2d, 3bff1c36, 444e27b0 — all distinct, no common prefix or sequence; two share a "72" tail (chance level, not a derivation pattern).
- No factor id is a substring of any tool name (all factor ids end `_fx`; checked mechanically).
- Docstrings carry no concrete example equal to a scored value (only numeric literal `0.00`; the only example `RHC-0482913` cannot equal a tool-generated claim number, which always begins `RHC-2`).
- Docstrings and sequence (observation O5): every write docstring says "Once it succeeds …" about its own effect; the tow docstring adds "Once it succeeds the claim number can be quoted for the other services of the same breakdown", and the outside-repair docstring "under the claim number of the breakdown it belongs to … as shown on the certificate's claim history" — a tool-layer restatement of edge E4's ordering. The blocked rule states the edge too, so no scored value moves; recorded as an observation against check 3.
- Tool bodies judge nothing: no tool reads history, checks status, a prerequisite, a window or a cap; the only refusal is `confirm_life_of_tread_cancellation_58ab2fcf` rejecting a `refund_tender` outside its enum.
- Tool contract gap (observation O6): `confirm_life_of_tread_cancellation_58ab2fcf.refund_tender` accepts only `cash_or_debit`/`bank_card`; base `hazard_evt_cancellation_refund` sends the refund to the certificate's tender, which may be `crestline_card` or `fleet_account` (and base triggers a card merchandise credit / fleet credit memo for those). A Life-of-Tread certificate paid on the Crestline card has no expressible solution. Not reached in task 0 (bank_card).
- The confirm tool creates a new `confirmed` cancellation request instead of confirming an existing pending one (observation O12); the overwrite says it "records the holder's cancellation request as confirmed". Not reached in task 0 (no pending request).

### prerequisite_graph

| Edge | Blocked -> depended-on | kind / gate | form | resolved_by = target_tool | policy_source verbatim in own rule |
| --- | --- | --- | --- | --- | --- |
| E1 | lot_cancellation_refund -> counter_replacement_posting | value_input / `benefits_paid` (exists) | state | post_hazard_counter_replacement_324c4972 ✓ | ✓ |
| E2 | lot_cancellation_refund -> outside_replacement_reimbursement | value_input / `benefits_paid` (exists) | action (+fallback_reason) | reimburse_hazard_outside_replacement_5f5d3272 ✓ | ✓ |
| E3 | store_replacement_authorization -> outside_repair_reimbursement | value_input / `position_covered_repairs` (exists) | action (+fallback_reason) | reimburse_hazard_outside_repair_444e27b0 ✓ | ✓ |
| E4 | outside_repair_reimbursement -> outside_tow_reimbursement | state_gate / `hazard_events.claim_number` | state | reimburse_hazard_outside_tow_3bff1c36 ✓ | ✓ |

- `prerequisite` filled everywhere (`[]` on counter, outside replacement, tow); every `problem` is an extended policy of this file, none self-referencing; graph acyclic (two disjoint trees, depth 1 and 2).
- `fallback_reason` present exactly on the action-form edges. Conditions are not strengthened relative to the sentences except E3 (observation O2 below).
- E4 `gate` names a field, not an eligibility gate (the extended policies declare no eligibility entries); what E4 actually feeds is the `claim_number` parameter of the repair write (observation O4).
- No authoring-viewpoint phrasing in any `prerequisite` field.

### prerequisite_sentences

- E1: "The Life-of-Tread cancellation refund is fixed only after every tire that a Crestline technician's inspection recorded as damaged on the covered set during the term carries its replacement entry on the certificate." Connective "only after"; waited-on thing is a record-visible state (damage inspections on `tire_events`, replacement entries on `hazard_events`); no tool, id or snake_case. Writes that can bring it about: the counter posting and the store authorization both create `hazard_replacement` rows; they are separated only by scope (inspection recorded on an earlier day and replacement already carried out vs inspection recorded today and authorized in person). For any inspection dated before the handling day only the counter posting applies, so the hop resolves to one write; a same-day counter replacement would admit both (observation O3). Derivation: sentence -> find damage inspections without a replacement entry -> the counter-posting rule's own scope names that situation -> post it.
- E2: "The Life-of-Tread cancellation refund is not paid until any tire replacement the holder bought out of the area during the term, and can still claim within the receipt window, has been reimbursed under the certificate." "not … until"; action form; scope matches the condition (open set, window-limited). Fallback reason tested (observation O1): the depended-on write leaves a record-visible state — "every such replacement carries its out-of-area replacement reimbursement entry on the certificate" — and the charter itself states the identical situation for tows in state form (E4); the fallback is not justified. Derivation: sentence -> ask the holder about outside replacements / read the outside merchant charge on the card ledger -> the outside-replacement rule covers a non-surrendered out-of-area replacement -> reimburse.
- E3: "The plan's share of an authorized store replacement is fixed only after every repair of the same wheel position that the holder paid an outside shop for during the term has been reimbursed under the certificate." "only after"; action form; same fallback weakness as E2 (O1). Scope (observation O2): the sentence covers every outside repair of the position "during the term", the `condition` only those "the holder can still claim within reimbursement_claim_window_days"; an outside repair older than the window can never be reimbursed, so the sentence as written would block the authorization forever. Not reached in task 1 (only one outside repair, inside the window).
- E4: "An out-of-area repair is reimbursed only after the tow of the same breakdown carries its out-of-area tow reimbursement entry on the certificate, and the repair entry is booked under that tow entry's claim number." "only after"; state form; exactly one write (`reimbursement_type=tow`) produces it. Single reading.
- Depended-on rules do not restate any sentence. No other cross-problem order stated in any extended rule. Base rules state no cross-problem order a tree rests on.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- LOT vs `hazard_evt_cancellation_refund`: holder-decision sentence — declared (replaced for LOT); active-at-completion — followed; first-rule-applies order and void/covered_set_returned/full_refund_window — followed (scope is pro_rata only); pro_rata sentence — declared; refund-to-tender — followed (tool enum gap O6); remaining calls lapse — declared (credit). Clean.
- Counter posting vs `hazard_evt_replacement`: same-tire/plan-pays-share — followed; per-position limit — inherited; **"The plan pays 100 percent while both hold: hazard_msr_within_full_months is true and the tread worn … is at most full_replacement_wear_32nds." — not named**, yet the counter points (card/care/bundle up to +12, repair points -4/-8) are added to a 100 base and clamped, so a full-period replacement with repair points pays 92 or 96 percent (finding C1); "Otherwise coverage_pct …" — declared (restated identically); amount sentence — declared (ticket price replaces current selling price); customer-pays sentence — not acted on by the tool (O13); surrender/remaining-term — not touched. vs `hazard_claim_coverage` / `hazard_commercial_use_exclusion` / `hazard_defect_exclusion` — inherited by explicit sentence.
- Outside replacement vs `hazard_evt_third_party_reimbursement`: the replacement sentence (including "computed exactly as in hazard_evt_replacement") — declared; out-of-area condition — declared for its own type; window and documents — inherited; tender — followed. Clean.
- Store authorization vs `hazard_evt_replacement`: amount and "Otherwise" sentences — declared; **the 100-percent sentence — not named, and directly contradicted**: "Authorization repair route: when the wheel position's covered repairs … have reached repairs_per_tire_max, the full-replacement period does not apply …; when the position has at least one covered repair but fewer than repairs_per_tire_max, the full-replacement period is cut to full_replacement_months divided by 2" (finding C1). The author declared the else-branch sentence but left the if-branch in force.
- Outside repair vs `hazard_evt_third_party_reimbursement`: repair sentence — declared; out-of-area condition — declared; rest inherited. Clean.
- Outside tow vs `hazard_evt_third_party_reimbursement`: tow sentence — declared (allowance can exceed `tow_reimbursement_cap` by uplifts, declared); out-of-area condition — declared. Clean.
- Base-level known issues (not extended overrides): `hazard_msr_commercial_use` / `hazard_commercial_use_exclusion` never define "the claim date" (date of loss/service vs date the claim is opened/paid) (O8); `hazard_claim_coverage` makes the "recorded damage_type" the authority, but `tire_events` inspection rows carry no damage type, so every posting/authorization takes `damage_type` from the persona (O9).

### factor_ladders

| Policy | Factors (effect, cross_difficulty) | parameter / method (declared) | honest method | multi-source |
| --- | --- | --- | --- | --- |
| LOT | clock_start (method, fleet), day_count (method), tread_life (param, tires), fee_schedule (param, card), call_credit (param), bundle_clawback (param, alignment) | 4 / 2 | day_count ✓; clock_start selects an anchor date into the same formula (borderline, O11) | clock_start (enrollment ∧ no later removal), fee (active card ∧ late-fee count) |
| Counter | price_rule (method, tires), card_points (param, card), care_points (param, tires), bundle_points (param, alignment), repair_points (param) | 4 / 1 | price_rule ✓ (formula / recorded posting / ticket price) | price_rule, card, care |
| Outside repl. | tread_basis (method, tires), card_uplift (param, card), price_ceiling (method, tires), care (param, tires), bundle (param, alignment), repair_points (param) | 4 / 2 | tread_basis ✓, price_ceiling ✓ | card, price_ceiling, care |
| Store auth. | repair_route (method), price_rule (method, fleet), fleet_points (param, fleet), care (param, tires), bundle (param, alignment) | 3 / 2 | price_rule ✓; repair_route mixed (tier 1 drops the 100 branch, tier 2 halves a threshold) | price_rule (fleet tender ∧ tires invoice discount), fleet_points, care |
| Outside repair | size_multiplier (method, tires), card_uplift (param, card), fleet_uplift (param, fleet), repeat_deduction (param) | 3 / 1 | **none** — size_multiplier substitutes 1.25 / 0.9 / 1 into `cap * factor` (finding C2) | card, fleet |
| Outside tow | size_multiplier (method, tires), card_uplift (param, card), fleet_uplift (param, fleet), roadside_usage (param) | 3 / 1 | **none** (finding C2) | card, fleet |

- Every ladder has three pairwise-disjoint tiers, fall-through = the factor's baseline, every tier stated in the rule and implemented in compute, `decides` is an input (never `result`), binding sets disjoint within each policy. No two tiers of any ladder select the same value or method (LOT fee 0 / 12.50 / 25.00 with `cancellation_admin_fee`=25 on Life-of-Tread; all point and uplift ladders strictly distinct).
- Every `baseline.rule` sentence is a sentence of its `rule` (checked); each is self-sufficient (gives a definite number with no factor) and its `params` are the keys it uses.
- Realism of tiers (top priority for this scenario):
  - Realistic: LOT clock start (coverage stopped when the vehicle entered commercial use; honouring an earlier pending request), tread-life factor, fee waiver for cardholders in good standing, unused-call credit, bundle clawback; counter/store price ladders (instant-savings net price, recent posted price, fleet net price); out-of-area tread basis and price ceiling; store repair route (repaired position loses part of the full-replacement period).
  - Plausible loyalty perks, recorded as observations (O11): card points / card uplifts, alignment bundle points, rotation (tire-care) points, fleet-program points added to a coverage percentage or allowance.
  - **Unreal (finding C3)**: (a) `repair_size_multiplier_fx` and `tow_size_multiplier_fx` tier 2 — "a line whose original_tread_depth_32nds is at most small_tread_32nds" (10/32: Value Touring 40K and All-Season 50K) multiplies the repair/tow allowance by 0.9, under the label "vehicle-size multiplier"; 10/32 versus 11/32 passenger touring lines fit the same sedans and SUVs, and neither the cost of a puncture repair nor a tow depends on the tire's new tread depth; (b) `tow_roadside_usage_fx` — a tow reimbursement cut by 10/20 because the holder used roadside calls the plan already counts against its allowance; (c) `repair_repeat_deduction_fx` — an outside repair reimbursed 4/8 less because the certificate already carries repairs (on any position); (d) `outside_repair_points_fx` — the coverage percentage of one replaced tire reduced by repairs on *other* positions of the certificate (contrast the counter posting's per-position schedule). No tire retailer weighs these conditions for these quantities.
- Counts per task (from the trees): tree A computations carry fleet, tires, card and alignment cross-difficulty factors and several multi-source factors; tree B the same, but its two prerequisite computations fail the method bound (C2).

### findings

- **C1 — SOURCE-POLICY RED (undeclared override, class "100-percent sentence")**. Symptom: extended coverage percentages contradict base `hazard_evt_replacement` "The plan pays 100 percent while both hold: hazard_msr_within_full_months is true and the tread worn (hazard_msr_original_tread minus remaining_tread_32nds) is at most full_replacement_wear_32nds." Root cause: the store-authorization repair route removes or halves the full-replacement period, and the counter posting's negative repair points are added to a 100 base; neither policy's `overwrite` names that sentence (both name only the amount sentence and the "Otherwise coverage_pct…" sentence). Class members: `hazard_ext_store_replacement_authorization` (repair route; also its point schedules once a 100 base clamps), `hazard_ext_counter_replacement_posting` (repair points on a 100 base). Not a member: `hazard_ext_outside_replacement_reimbursement` (its overwrite names the whole replacement sentence). Bears on task 1 (demonstrated there); counter member undemonstrated in task 0 (its base pct is 33, not 100).
- **C2 — SOURCE-FACTOR RED (mislabelled effect, class "method that is a number")**. `repair_size_multiplier_fx`, `tow_size_multiplier_fx`: tiers substitute a multiplier (1.25 / 0.9 / 1) into the same `cap × multiplier` formula — a parameter; the outside-repair and outside-tow computations are left with zero honest `method` factors (bound: at least 1). Other members reviewed and kept: `refund_clock_start_fx` (anchor date, borderline; LOT keeps `refund_day_count_fx`), `auth_repair_route_fx` (mixed; store keeps `auth_price_rule_fx`). Bears on task 1.
- **C3 — SOURCE-FACTOR RED (unreal ladder, class "condition the trade does not weigh")**. Members (a)–(d) above. (a), (b), (c) bear on task 1; (d) bears on task 0.
- Observations (no scored consequence demonstrable in these worlds): O1 action-form fallback unjustified on E2/E3; O2 E3 sentence broader than its condition; O3 E1 two candidate writes separated only by scope; O4 E4 gate is a field; O5 tool-layer sequence hint in tow/repair docstrings; O6 LOT confirm tool tender enum; O7 "covered repair entries" undefined outside the store rule; O8 base "claim date" undefined (task 0 shows the alternative figure); O9 damage_type authority unseeded; O10 fleet price-file read not tied to the roster's account; O11 realism notes (loyalty points, reimbursement-date full period, three-method LOT day count, clock-start label); O12 confirm tool creates a new request; O13 `customer_paid_amount` never written.

## closing_checklist

Written after both reveals (2026-10-15). The difficulty does **not** close.

- Audit files 0.md and 1.md correspond one-to-one with tasks 0 and 1, with _difficulty.md alongside. This is the first revision. Comparison sections: task 0 SOURCE-FACTOR RED; task 1 SOURCE-POLICY RED and SOURCE-FACTOR RED.
- Coverage and scopes: the six extended policies are fully covered by the two disjoint `charter_scope`s, confirmed against the GT. Each tool has an independent uuid8. Tools and GT are closed; every GT argument matched the blind derivation.
- Trees: each tree has 2 prerequisite problems and at least 1 value_input edge. Each root is an `owner=user` write. The graph is acyclic within and across tasks. PASS.
- Factors: counts and weights PASS on both worlds, and every baseline_result and per-factor figure matches the audit's recomputation. Open items:
  - C2: the outside repair and outside tow computations have no honest method factor.
  - C3(a)–(d): unreal ladder conditions.
  - Task-1 seed: the alignment row contradicts the alignment charter.
- Policy self-consistency: C1 is open (undeclared override of base `hazard_evt_replacement`'s 100-percent sentence, demonstrated in task 1).
- Gate re-run on the final form: not applicable until rework.
- Open charter-wide items: C1, C2, C3.
- Observations not counted as blockers: O1–O13, and the task-0 alignment price field.

## revision_2

### charter_global_frozen (round 2)

- Freeze time: 2026-10-15 (before any round-2 GT reveal). Auditor: the same sub-agent as round 1, still independent of the reworker.
- Inputs (sha256, matching `snapshot_r2.txt`): `hazard.extended.yaml` 1d3296574dee8f80b3471a2cc318d30a17752e872b7d01481e0d1886b01bebfc and `task_tools.py` 7b00699f168f7dc9c5ad7a2517091658d3f2ad734fd84824b452b5382103a608. Both differ from round 1, so every charter-global section below is re-derived in full. The round-1 text above is untouched.
- Step 0:
  - All seven d_gates are green.
  - validate_scenario has 0 errors besides the pre-render ones. Traceability has 6 misses, all unpublished unlock names.
  - The masked views match their hashes.
  - The base section is still `==` blueprint `hazard.yaml`.
- Read domain unchanged. No task JSON, worklog or plan.md was read before the freezes below.

### policy_conflict_scan (r2)

- Same six policies and the same two trees.
  - Tree A: LOT <- counter, outside replacement.
  - Tree B: store authorization <- outside repair <- outside tow.
- Counter and store scopes are now disjoint on the record.
  - Counter: "the technician's damage reading being dated before the posting day".
  - Store: "recorded today".
  - This closes O3.
- Each extended claim policy now says "commercial use being judged on the service date". That closes O8 for the extended policies; the base measure is unchanged.
- LOT scope now covers only certificates "bought in cash, by debit card or on a bank credit card". Crestline-card and fleet certificates stay under base. This matches the tool's tender enum and closes O6.
- No new conflict between policies.

### rule_compute_equivalence (r2)

- Every compute binding has a `compute_basis` quotation located in its own rule (checked mechanically). Sweep back:
  - LOT: day-count basis now reads `MONTHS(effective_date, NOW)` (rule: "to the cancellation date").
  - Counter: price ladder (fleet net / instant savings / unit price); repair points per position, counting repair entries plus out-of-area repair reimbursements as the rule states.
  - Outside replacement: miles proration on the latest rotation odometer less `install_odometer`; card cap uplift; own-price ladder; service allowance.
  - Store authorization: card points replace bundle points; the roster account is tied through `roster_account`.
  - Repair: breakdown limit, labor allowance, card and fleet uplifts.
  - Tow: light-truck rate, card and fleet uplifts, breakdown limit.
- No empty promise.
- Rounding points match the rules: the tow allowance is rounded inside, then again at the end; the repair is rounded once on the sum.
- O7 closed: "covered repairs" is defined in every rule that uses it.
- O10 closed: the fleet program is read from the roster's own account.

### action_binding_and_uuids (r2)

- Six distinct `(target_tool, computes)` pairs. uuid8s unchanged and distinct.
- No factor id is a substring of a tool name.
- No docstring numeral equals a scored value (only `0.00`; the example `RHC-0482913` cannot equal a generated `RHC-2…`).
- O5 closed. The tow docstring now ends "The new claim number is shown in the confirmation", and the repair tool books "under a given claim number"; no sequence statement remains. The benign "Once it succeeds" phrasing stays.
- `remaining_tread_32nds` on the outside-replacement tool is now "tread depth shown on the outside shop's receipt", so it is defined even though the percentage no longer rests on tread.
- Tool bodies judge nothing; the only refusal is the tender enum, now consistent with the LOT scope.
- O12 and O13 unchanged.

### prerequisite_graph and prerequisite_sentences (r2)

| Edge | kind / gate | form | sentence verbatim in own rule | single resolving write |
| --- | --- | --- | --- | --- |
| E1 LOT <- counter | value_input / benefits_paid | state | ✓ | ✓ counter (store scope excluded by date) |
| E2 LOT <- outside replacement | value_input / benefits_paid | state: "…not paid until every out-of-area tire replacement that the holder can still claim within the receipt window carries its out-of-area replacement reimbursement entry on the certificate." | ✓ | ✓ |
| E3 store <- outside repair | value_input / position_covered_repairs | state: "…fixed only after every repair of the same wheel position that the holder paid an outside shop for and can still claim within the receipt window carries its out-of-area repair reimbursement entry on the certificate." | ✓ | ✓ |
| E4 repair <- tow | value_input / repair_part (the tow's amount enters the breakdown limit; its claim number is booked) | state | ✓ | ✓ |

- O1 (action-form fallbacks), O2 (E3 scope) and O4 (E4 gate is a field) are closed.
- The graph is acyclic, each `resolved_by` is the target tool, and no authoring-viewpoint text appears in any `prerequisite` field.
- Undeclared cross-problem order (tow rule): see C4 below.

### override_declarations (r2)

- C1 is closed.
  - Store authorization now names the base sentence "The plan pays 100 percent while both hold…" in its `overwrite`.
  - Counter and outside replacement add points "only to a prorated … coverage percentage …; … of 100 stays 100", so the base 100-percent sentence is no longer contradicted.
- All other sentence-by-sentence conclusions are as in round 1. The base window, documents, tender and per-position limits are inherited.

### factor_ladders (r2)

| Policy | Factors (effect / xd) | param / method | honest method |
| --- | --- | --- | --- |
| LOT | clock_start (m, fleet), day_count (m), tread_life (p, tires), fee (p, card), call_credit (p), bundle_clawback (p, alignment) | 4/2 | day_count ✓ |
| Counter | price_rule (m, tires), card (p), care (p), bundle (p), repair_points (p, per position) | 4/1 | price_rule ✓ |
| Outside repl. | proration_measure (m, tires), card_uplift (p), own_price (m), care (p), bundle (p), service_allowance (p, tires) | 4/2 | proration ✓, own_price ✓ |
| Store | repair_route (m), price_rule (m, fleet), fleet_points (p), care (p), card_points (p) | 3/2 | price_rule ✓ |
| Repair | breakdown_limit (m), labor_allowance (p, tires), card (p), fleet (p) | 3/1 | breakdown_limit ✓ (different formula per tier) |
| Tow | breakdown_limit (m), light_truck_rate (p, tires), card (p), fleet (p) | 3/1 | breakdown_limit ✓ |

- C2 is closed: the multipliers are now honestly labelled `parameter`, and each computation keeps one honest method.
- C3 is closed:
  - (a) the 10/32 tier is gone; the light-truck rate keys on the plan plus the LT line.
  - (b) the roadside-usage deduction and (c) the repeat-repair deduction are removed.
  - (d) the certificate-wide repair points are removed.
- Every ladder has three disjoint tiers; each fall-through equals the factor's baseline; every tier is in the rule and in compute.
- Factor independence: no factor binding reads another factor's `decides`, and `result` is in no binding (checked mechanically).
- Every `baseline.rule` sentence is in the rule and is self-sufficient.
- New ladders, realistic:
  - per-breakdown limits (one tow allowance per breakdown; repair held to a combined tow-plus-repair ceiling);
  - labor and service allowances at the line's own mounting, TPMS-kit and disposal charges, on plans that include them;
  - mileage proration against warranted miles;
  - light-truck tow rate.
- `repair_labor_allowance_fx` and `outside_service_allowance_fx` take their tier from the hazard plan's own parameters. They read only the tire line's charges, so their `cross_difficulty: tires` is a value read, not a tier read. Each task still has card, fleet and alignment tier-from-other-difficulty factors (observation R2-O1).
- **C4 — SOURCE-FACTOR RED (dead or self-contradictory tier), with an embedded order statement.**
  - Factor: `tow_breakdown_limit_fx`, tier 2.
  - Tier text: "when there is no such roadside entry but the certificate already carries an out-of-area repair reimbursement whose service date is within that window (the repair of the same breakdown, the tow then joining that claim), it is the lower of the tow allowance and tow_reimbursement_cap".
  - Reading 1 (as its parenthesis says, the same breakdown): the tier is unreachable. The repair rule forbids that state: "An out-of-area repair is reimbursed only after the tow of the same breakdown carries its out-of-area tow reimbursement entry on the certificate". "The tow then joining that claim" also cannot be expressed: `reimburse_hazard_outside_tow_3bff1c36` always opens a new claim number.
  - Reading 2 (its operative date condition): it caps the tow of a different breakdown because an unrelated out-of-area repair falls within 30 days. No business weighs that for a tow allowance.
  - Either way the ladder has only two real tiers.
  - The tier also states a value consequence of the reverse order (repair before tow) that grounds no declared edge.
  - Bears on task 1, whose tree contains the tow computation (tier 1 is taken there, so no scored value moves).
  - Other members of the class, checked and kept as live: every other tier of every ladder is reachable in a charter-consistent world.
  - Neighbouring observation (R2-O2): tow tier 1 and repair tiers 1 and 2 identify "the same breakdown" by a 30-day date window. They are reachable with their true meaning (same-day entries), but the window over-reaches if two breakdowns fall in one month.
- Observation R2-O3: the counter, store and outside price ladders take "the fleet invoice … with service category tires" discount and divide it by tire_count. Under the fleet charter that discount also covers mounting and TPMS kits on the ticket, so the tire's net price is understated by about 1.85 per tire in task 1. The rule is definite; this is a realism note.
- Observations unchanged: O9, O11 (loyalty points: card, care, bundle, fleet), O12, O13.

### findings (r2)

- Round-1 items: C1, C2 and C3(a)–(d) are closed. O1–O8 and O10 are closed or addressed as noted. O9, O11, O12 and O13 are unchanged, as the reworker reported.
- New: **C4** (SOURCE-FACTOR RED, charter-global, bears on task 1). Observations R2-O1, R2-O2, R2-O3.

### closing_checklist (r2)

Written after both r2 reveals.

- Files and revisions: one file per task plus `_difficulty.md`; revision_2 is appended and round 1 is untouched.
- Coverage and uniqueness: the six policies are fully covered by two disjoint scopes; uuid8s are independent; GT is closed and every GT argument matched the blind derivation.
- Trees: each has 2 prerequisites, both value_input, a user-owned root, no cycle.
- Factors: weights, baselines and fall-backs are proven on both worlds, and every figure equals `computations`.
- Round-1 items: C1, C2, C3(a)–(d) and the task-1 alignment seed are closed. O1–O8 and O10 are closed. O9, O11, O12 and O13 are unchanged (non-blocking).
- Open charter item: **C4** (tow breakdown-limit tier 2, dead or self-contradictory). The difficulty does not close until C4 is resolved.
- Gate re-run on the final form: pending rework.

## revision_3

### charter_global_frozen (r3)

- Freeze: 2026-10-15, before the r3 reveal.
- Inputs:
  - `hazard.extended.yaml` 8a0d400c… (changed).
  - `task_tools.py` 10c48b49… (changed).
  - Views 0.json and 1.json unchanged from r2 (277a6d33…, 458ca500…).
- The changed charter and tools are re-derived below; unchanged conclusions carry forward from §revision_2 by reference.
- Base still verbatim. All seven d_gates are green; traceability misses are only unpublished unlock names.

### changes found and checked (r3)

- **Tow breakdown limit (C4).** The ladder is rebuilt on "the certificate's most recent claim entry by service date", when that entry is a Crestline roadside service within 30 days.
  - Tier 1: after a flat_tire_change dispatch, the allowance less what that dispatch's claim number received.
  - Tier 2: after a Crestline tow dispatch, the lower of the allowance and tow_reimbursement_cap less that claim's paid amount.
  - Otherwise: the allowance.
  - The tow is "booked under that dispatch's claim number".
  - Every tier is reachable in a charter-consistent world. Dispatches of type tow exist on the Plus, Life-of-Tread and Commercial LT plans.
  - Every tier is realistic: one roadside benefit, or one tow cap, per breakdown. The old tier that conflicted with the repair rule is gone, and nothing in the rule states the reverse order any more.
  - **C4 closed.**
- **Repair breakdown limit.** Now keyed on the tow's or dispatch's own claim number ("the amounts reimbursed on that tow's claim number" / "the amounts paid on that dispatch's claim number"). This narrows R2-O2.
  - Observation R3-O1: in task 1 the tow and the dispatch now share one claim number. "Reimbursed" (the tow reimbursement) is the operative word; compute filters `reimbursement_type='tow'`. A reader who also counted the 30.00 dispatch on that claim would get 49.00 instead of 69.00. The rule's own "reimbursed" versus "paid" wording excludes that reading, so single reading.
- **R2-O1 addressed.** The two allowance factors now carry `cross_difficulty: null`.
- **R2-O3 addressed.** Each price ladder now says "(the whole tires-invoice discount, mounting and kits included, spread over the ticket's tires)". Compute is unchanged, and the rule now states what the formula does.
- **Tow tool.** It now takes `claim_number` ("as shown on a claim entry of the certificate") and no longer opens a claim.
  - **Observation R3-O2, a regression by construction.** The rule names a claim number only when a dispatch is on file. For the fall-through tier (an out-of-area tow with no Crestline dispatch), neither the rule nor the tool supplies a claim number, and the tool cannot open one. That situation has no expressible write.
  - Neither world reaches it, so it is an observation and not a RED. It should be closed before reuse.
- Mechanical sweep across all six policies:
  - every `compute_basis` entry is in its own rule;
  - every prerequisite sentence is verbatim in its blocked rule;
  - every `baseline.rule` sentence is in its rule;
  - every ladder has three tiers, with no factor reading another factor's output and no `result` in any binding;
  - no factor id is a substring of a tool name;
  - no docstring numeral equals a scored value.
- Graph unchanged: E1–E4 are all state form; E1–E3 value_input with the same gates; E4 value_input/repair_part.
- Unchanged policies keep the same compute (LOT, counter, outside replacement, store): only the price-ladder parentheticals were added.

### closing_checklist (r3)

- Task files carry revision_3 with frozen derivations and comparisons; earlier revisions are untouched.
- Scopes disjoint and complete; uuid8s independent; GT closed and identical to the blind derivations.
- Trees: two prerequisites each, all edges value_input and state form, user-owned roots, acyclic.
- Factors: four to six per computation, at least two parameter and one honest method; multi-source and cross-difficulty factors on both tasks; every factor bears weight against an honest baseline; fall-backs are definite and differ from gold.
- Round-2 RED C4 is closed. No open RED.
- Open observations (non-blocking):
  - R3-O1: "reimbursed" versus "paid" on a shared claim number.
  - **R3-O2: no claim-number source for a dispatch-less out-of-area tow (tool regression). Recommended to close before any reuse of this charter.**
  - O9, O11, O12, O13 as before.
- Instantiation gates re-run on this final form: all green per `snapshot_r3.txt`. Validate and traceability are pre-render only.

VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN

## revision_4

### charter_global_frozen (r4)

- Freeze: 2026-10-15, before the r4 reveal.
- Gate:
  - The worklog's last line (read with `tail -1` only) is `REWORK round 4: gates 7/7 green`.
  - `snapshot.sh road_hazard_claims 4` was executed: d_gates 7/7 green; validate and traceability fail only on pre-render items.
- Hashes: views 0.json and 1.json unchanged (277a6d33…, 458ca500…); `task_tools.py` 4ede7327…; `hazard.extended.yaml` 4abb11fb…. Base still verbatim.
- Changes found:
  - **R3-O2 closed.** The tow rule now adds "while a tow with no such dispatch on file opens a new claim number of its own". The tow tool opens a new `RHC-2…` claim number when `claim_number` is empty and otherwise books under the given one. The fall-through tier now has an expressible write. The tool still judges nothing.
  - **R3-O1 closed.** The repair breakdown limit now reads "less the amounts of the out-of-area tow reimbursement entries on that tow's claim number (a Crestline dispatch paid on the same claim number is not counted here)". This matches compute (`reimbursement_type='tow'`) and leaves a single reading.
- Mechanical sweep across all six policies: compute_basis in rule, prerequisite sentences verbatim, baselines in rule, three-tier ladders, no factor reading another factor's output, factor counts and labels, no factor id in a tool name, no docstring numeral equal to a scored value — all clean.
- The other four policies' compute is spot-checked identical to r3. No other change found.

### closing_checklist (r4)

- R3-O1 and R3-O2 are closed.
- No new defect and no regression.
- Both tasks PASS on all four relationships, with GT identical to the blind derivations.
- Remaining non-blocking observations: O9, O11, O12, O13.
- Gates per `snapshot_r4` are green; validate and traceability fail only on pre-render items.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

### charter_global_frozen (r5)

- Freeze: 2026-10-15, before the r5 reveal.
- Gate:
  - The worklog's last line (`tail -1` only) is `REWORK round 5: gates 7/7 green`.
  - `snapshot.sh road_hazard_claims 5` was executed: 7/7 green; validate fails only on pre-render items; **traceability is now OK**.
- Hashes: views unchanged (277a6d33…, 458ca500…); `task_tools.py` 9b9585c9…; `hazard.extended.yaml` b387b42a…. Base still verbatim.
- Additional read authorized by the coordinator: `audits/render_source/hazard/notes.md`. It holds source-side notes and no GT.

### renderer notes (items 1–14) against the r5 source

1–6. Assembly sentences that named several factor quantities: **closed**. Each policy now has a factor-silent assembly sentence in its baseline and rule:
   - LOT: "after every addition to it and deduction from it that applies, it is rounded … and held at 0.00 or more".
   - Counter, outside replacement and store: "Points added to … apply only to a prorated percentage …".
   - Outside replacement: "plus every allowance that applies to it, and only that sum is rounded".
   - Repair: "plus every allowance and uplift that applies to it".
   - Tow: "the tow rate is 1 … plus every uplift that applies … less every deduction … kept within every limit".
   Each factor sentence states its own effect ("adds … to the …", "is deducted from …").
7. Miles floor: **closed**. The rule now reads "the warranted_miles less the miles driven, held at 0 or more", matching `MX(0, …)`.
8. Binding homes, outside replacement: **closed**. `last_rotation_date` is in the proration factor's bindings; the care factor uses its own `care_last_rotation`.
9. Binding homes, repair and tow: **closed**.
   - Repair: `repair_part`, `last_tow_claim`/`paid` and `last_dispatch_claim`/`paid` are in `repair_breakdown_limit_fx`.
   - Tow: `last_dispatch_claim`/`paid`, `tow_deduction` and `tow_ceiling` are in `tow_breakdown_limit_fx`; `result` only assembles them.
10. Confirm-tool docstring against body: **closed**, and O12 is closed with it.
    - The overwrite and rule now say the confirmation "confirms the cancellation request awaiting the holder's confirmation on the certificate, or records one as confirmed when none is on file".
    - The body updates the latest pending request, or creates a confirmed one.
11. Overwrites retiring clauses still in force: **closed**. Each `replaced_by` now restates the base clause "for every … other than the one this policy handles" and scopes the extended treatment to "only it". No base clause is retired outside its scope.
12. LOT lapse overwrite: **closed**. The overwrite retiring "Remaining roadside calls lapse with the certificate" is removed; the extended rule adds the credit and keeps the lapse, so base and extended are consistent.
13. Day count reading clock start: **closed**.
    - The rule now defines a baseline quantity, "The Life-of-Tread counting date is the cancellation date". Clock start sets "the Life-of-Tread counting date is instead …", and day count chooses its method by months from `effective_date` to the cancellation date, applied "from the counting date".
    - `refund_day_basis` reads only `refund_months_in_force`; `refund_count_from` is combined only in the non-factor `refund_unused_share`.
14. Repair breakdown limit, which tow or dispatch: **closed**. The rule now says "the most recent out-of-area tow reimbursement … by service date" and "the most recent Crestline roadside service entry … by service date", matching LATEST.

### factor independence and sweep (r5)

- Strict check, all six policies:
  - no binding is owned by two factors;
  - no factor binding's expression reads another factor's binding;
  - no `result` sits in a factor binding;
  - every ladder has three tiers.
- Also clean: compute_basis in rule; prerequisite sentences verbatim; baselines in rule; no factor id in a tool name; no docstring numeral equal to a scored value.
- Compute is value-identical to r4. The tow restructuring (`tow_deduction`/`tow_ceiling`) gives the same figure on every tier.

### closing_checklist (r5)

- All 14 renderer notes are closed in the source; O12 is closed with note 10.
- Factor independence is verified strictly.
- No new defect and no regression; both tasks' GT is identical to the blind derivations.
- Gates are 7/7 green; traceability is OK; validate fails only on pre-render items.
- Remaining non-blocking observations: O9 (damage_type from the persona), O11 (loyalty points), O13 (`customer_paid_amount` not written).

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

### charter_global_frozen (r6)

- Freeze: 2026-10-15, before the r6 reveal.
- Gate:
  - The worklog's last line (`tail -1` only) is `REWORK round 6: gates 7/7 green`.
  - `snapshot.sh road_hazard_claims 6` was executed: 7/7 green; **validate_scenario is VALID**; traceability is OK.
- Hashes: views unchanged; `task_tools.py` unchanged (9b9585c9…); `hazard.extended.yaml` 04751cd8… (changed). Base verbatim.
- Additional read authorized by the coordinator: the S-1..S-7 and KB-1 sections of `audits/policy_kb/road_hazard_claims/{0,1}.md`.
- **S-1 closed.** The three out-of-area policies now carve out sibling scopes with one uniform phrase, "an out-of-area tire replacement reimbursed at the out-of-area reimbursement, an out-of-area tire repair reimbursed at the out-of-area repair reimbursement and an out-of-area tow reimbursed at the out-of-area tow reimbursement". The undefined "repair allowance" and the off-target "reimbursement base" carve-outs are gone. Each overwrite's `replaced_by` is verbatim in its rule.
- **S-3 closed.** Each scope now defines its receipt test, e.g. "The receipt covers the out-of-area reimbursement when the amount the holder paid the outside shop on it is at least the out-of-area reimbursement" (likewise for repair and tow). This matches the reading used in r2–r5.
- Sweep across all six policies is clean: compute_basis in rule; prerequisites verbatim; baselines in rule; no binding owned by two factors; no factor reading another factor's binding; three tiers everywhere.
- Every `result` expression and every factor compute is value-identical to r5.
- S-2, S-5, S-6 and S-7 are noted by the KB auditor as non-moving; they match my O9/O8 history and the base formula note. KB-1 is a KB-side item and out of scope here.

### closing_checklist (r6)

- S-1, S-3 and S-4 are closed; S-4 was verified by a full prose sweep of both task JSONs against records and charters.
- KB-1 is KB-side and outside this audit.
- No change other than the S-1/S-3 wording: compute is value-identical; tools and views are unchanged.
- No regression. Both tasks PASS, with GT identical to the blind derivations.
- Gates: 7/7 green; validate_scenario VALID; traceability OK.
- Remaining non-blocking observations: O9 (including the two wording notes above), O11, O13.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN
