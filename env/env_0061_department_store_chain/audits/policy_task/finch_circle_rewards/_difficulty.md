# Policy-task audit — finch_circle_rewards / charter-global

## charter_global_frozen

- Frozen sources: `tasks/finch_circle_rewards/loyalty.extended.yaml` sha256[:16] `88da07b45084a9d8`; `tasks/finch_circle_rewards/task_tools.py` sha256[:16] `d8465483604d8bf5` (both re-hashed by the auditor, equal to the brief).
- Freeze time: written to disk 2026-10-13T15:59:53Z (file mtime; corrected from an estimated "16:05Z" stamp written by mistake — metadata only, no derivation text changed). Auditor: erl-task-policy-audit agent (independent of the instantiator).
- Read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/loyalty.yaml` (+ `card.yaml`, `order.yaml`, `alteration.yaml` by targeted grep only, for the realism of seeded cross-category rows), the extended charter, the tool module, and the two masked views `.audit_views/policy/finch_circle_rewards/{0,1}.json` (sha256[:16] `caaef07d1c266e34`, `d0b7f65f2ad5d051`; keys `frozen_time`, `user_scenario`, `initial_state`).
- Masked / not read before the per-task freezes: `tasks/finch_circle_rewards/tasks/*.json` (all of `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`), `tasks/finch_circle_rewards/plan.md`, every other audit. No recursive search touched `tasks/*/tasks/`.
- Entry conditions: gate snapshot supplied in the brief (all green except the expected pre-render traceability/validate_scenario document misses); masked views supplied with hashes. Complete.
- Base copy: lines 1-1258 of the extended charter are byte-identical to `blueprint/products/loyalty.yaml` (`diff` shows only one trailing blank line). Every `superseded_clause` is verbatim in the named base rule; every `replaced_by` is verbatim in its own extended rule; every `compute_basis` quotation and every `baseline.rule` sentence is verbatim in its own rule (scripted check, `/tmp/audit_loyalty_0061/`).

### policy_conflict_scan

Five extended policies, all claimed by this difficulty (`categories [loyalty]`):

| policy | target_tool (owner) | computes | trigger | prerequisite |
| --- | --- | --- | --- | --- |
| loyalty_ext_missing_points_credit | file_missing_points_claim_8cff3bd6 (user) | points | on_request | <- loyalty_ext_card_floor_tier (value_input, earn_rate) |
| loyalty_ext_card_floor_tier | apply_card_status_floor_f82dd75f (agent) | top_up_amount | state_due | [] |
| loyalty_ext_return_points_deduction | book_return_points_deduction_52e06983 (agent) | points | state_due | [] |
| loyalty_ext_note_reinstatement | reinstate_returned_note_1c0adac4 (agent) | note_amount | state_due | [] |
| loyalty_ext_courtesy_note_reissue | request_courtesy_note_reissue_8b12a7a8 (user) | validity_days | on_request | <- return_points_deduction (value_input, return_pct); <- note_reinstatement (state_gate) |

- Subjects: two policies write `loyalty_points_ledger` (`loyalty_points_adjustment` vs `loyalty_points_reversal`), two write `loyalty_note_issue` with different `issue_reason` (`return_reinstatement` vs `courtesy_reissue`), one writes `loyalty_tier_change` + benefit grant. No two policies decide the same row or the same quantity.
- Triggers / eligibility / time anchors: each extended policy inherits its base gates (claim window and waiting period from `loyalty_missing_points`; active status and floor eligibility from `loyalty_tier_qualification`; dedup from `loyalty_evt_points_reversal` and `loyalty_note_reinstatement`; window, rolling count and exclusions from `loyalty_expired_note_courtesy`). No extended rule weakens one of them.
- Object selection: the deduction and reinstatement policies both select "the member's purchase record most recently received back in returned status"; the courtesy policy selects "the member's most recently lapsed note"; the missing-points policy selects the unlinked unit in completed status. Compatible.
- Cross-category read boundaries: reads only (order, card, alteration, registry); no extended policy writes another category.
- Graph components: {missing_points <- card_floor} and {courtesy <- deduction, reinstatement}. With M=2 the natural partition is task 0 = first component, task 1 = second; mutual exclusivity and joint completeness hold under that partition (to be confirmed against `charter_scope` after the reveal).

### rule_compute_equivalence

Sweep of every binding of every policy against its quotation (all quotations verbatim, see above). Results:

- loyalty_ext_missing_points_credit: qualifying amount, earn rate (tier on record at request date), dating ladder, bonus-event ladder, late share, card rate, financing share, standing share (6 whole months), each `int()` floor, and the three-part sum: equivalent both ways.
- loyalty_ext_card_floor_tier: equivalent except one filter. Rule: "when the customer's active card account shows no late fee charged within the last 6 whole months"; compute `late_fees: XCOUNT('card','card_transactions', within_months=6, ..., event_type='card_fee', fee_type='late_fee')` carries no account filter, so a late fee on a closed second account would count. Not demonstrable on either task world (task 0 holds one card account) -> observation O3. `floor_card`/`card_review`/`card_opened` use `CFIELD(..., status='active')`, i.e. the first active account; the rule speaks of "the customer's active card" in the singular -> observation O4 (no task world holds two active accounts).
- loyalty_ext_return_points_deduction: equivalent (refund basis order: restocking first, then Merchandise Credit Card, then default; card basis; event/card/exchange/cushion ladders; per-component half-up, then cushion, half-up once more).
- loyalty_ext_note_reinstatement: equivalent (allocation / proportional / whole ladder; fee share; lapse share keyed on the redeemed note's issue entry; timing share from completed date; uplift; single final rounding).
- loyalty_ext_courtesy_note_reissue: compute equivalent to the ladders, but `compute_basis.result` quotes "The courtesy validity days are the tier courtesy days." while `result` binds `courtesy_days` (the return-share-adjusted day count). The rule carries both that flat sentence and "otherwise they are the courtesy day count"; read as baseline + overriding ladder the later sentence governs -> observation O5 (same baseline-then-ladder shape as "A late-credited purchase is dated by its purchase date." in the missing-points rule).
- Every factor's ladder tiers are rule sentences and branches of the `decides` binding, and vice versa: no tier lives only in one face.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are distinct across the five policies; each tool is claimed by exactly one policy.
- Docstrings: no docstring names another tool, states a position in a sequence, or uses an ordering word (the only hits for "once" are "credited at once" / "issued at once", meaning immediately). No docstring or parameter description carries a concrete example value (formats only: "USD, 2 decimal places", "YYYY-MM-DD", "FN- followed by 8 characters") -> no gold value can leak through a published docstring.
- No tool validates anything: every body reads the membership row, writes the given values and returns (lines 25-44, 61-76, 124-137, 155-168, 186-206). The courtesy tool's `return_id` description fixes the empty value for a courtesy reissue.
- uuid8s: `8cff3bd6`, `f82dd75f`, `52e06983`, `1c0adac4`, `8b12a7a8` — pairwise distinct, no shared prefix or tail, no sequence pattern.

### prerequisite_graph

- `prerequisite` is filled on all five policies (`[]` on three). Every `problem` is an extended policy id of this file, never a base policy, never self. Graph: card_floor -> missing_points; return_deduction -> courtesy; note_reinstatement -> courtesy. Acyclic.
- Each `policy_source` is verbatim in its own (blocked) rule. `form: state` on all three edges, no `fallback_reason` (correct for state form).
- `resolved_by` equals the depended-on policy's `target_tool` on all three edges, and the tool's write makes `effect` hold (variant_name update; reversal entry with qualifying_amount; note issue with `issue_reason return_reinstatement` naming the return and original note).
- `kind`: `value_input` edges name bindings that exist (`earn_rate` in missing_points compute; `return_pct` in courtesy compute); the `state_gate` edge names `loyalty_note_ledger.issue_reason`, the field the gate reads. No authoring-viewpoint words in any `prerequisite` text.

### prerequisite_sentences

1. missing_points <- card_floor: "The missing-points credit is fixed only after the membership record shows the Finch Circle tier that an active Marlowe & Finch card status floor grants the member." Ordering connective "only after"; record-visible state (membership record's tier); no tool, id or snake_case. Only `apply_card_status_floor_f82dd75f` writes `variant_name` in this difficulty. Derivation: sentence + card record (active Platinum MC / Store Card Elite / World Elite) + the card-floor rule ("the membership is moved to that floor tier as a card floor") -> the card-floor write, single reading. Strength: the `condition` says "at least the floor tier", the sentence literally says "shows the tier that ... floor grants"; for a member already above the floor the sentence read literally can never hold -> observation O1 (no task world has a member above the floor).
2. courtesy <- deduction: "The courtesy note's validity is fixed only after every refunded return on the member's purchases shows its return deduction entry on the membership's points history." "only after"; state; no tool. Only `book_return_points_deduction_52e06983` writes reversal entries. Scope: the `condition` restricts to returns "on a purchase record of the member that earned points"; the sentence covers every refunded return, including one on a purchase that earned nothing -> observation O2 (both refunded returns in task 1 earned points).
3. courtesy <- reinstatement: "A courtesy reissue is not granted until every refunded return of merchandise paid in part with a Finch Note shows its reinstatement note on the membership." "not ... until"; state; only `reinstate_returned_note_1c0adac4` issues a `return_reinstatement` note (the courtesy tool issues `courtesy_reissue`).
- The depended-on rules (card floor, deduction, reinstatement) carry no restatement of these sentences and name no other problem. No rule names another policy's tool or id. No other cross-problem order sentence exists in any extended rule; no base rule sentence states a cross-problem order among these five problems.

### override_declarations

Sentence-by-sentence over each `base_policy_refs` entry (conclusion per sentence; only the non-trivial ones listed):

- loyalty_ext_missing_points_credit
  - loyalty_missing_points: credit clause superseded and declared. All other sentences (purchase in member's name and on/after enrolled_date; claim window per tier on request date; waiting period; no purchase_base / earlier credit row; fully returned earns nothing; purchase-record proof) followed.
  - loyalty_evt_points_earn: "purchase_base points equal the member's base_points_per_dollar on the purchase date ..." and the bonus_event sentence — the quantities they feed into a missing-points credit are those of the superseded missing_points clause ("the purchase_base and bonus_event points that purchase would have earned at the tier and rates in effect on the purchase date"), so they are covered by that declaration. **Not covered**: "When the purchase was charged to a Marlowe & Finch card, a card_bonus row adds the card's mf_bonus_points_per_dollar times the amount charged for it." The base missing-points credit never contained card bonus points, so the card bonus of an unlinked purchase charged to an M&F card is governed only by this sentence. The extended rule handles that quantity differently ("The late-credit card bonus points are the late-credit qualifying amount times the late-credit card bonus rate times the late-credit financing share times the late-credit standing share") and folds it into the adjustment, while its own replaced_by says "every other points entry remains under the base earning rules". `overwrite` names only loyalty_missing_points -> **undeclared override, finding F1**.
- loyalty_ext_card_floor_tier: loyalty_alteration_credit_rules top-up clause superseded and declared; loyalty_tier_qualification card-floor sentences (floor map, active status, never lowers a higher tier, floor-eligible tiers) followed; loyalty_tier_benefits "a downgrade or card floor posts no bonus" followed ("the change posts no points bonus").
- loyalty_ext_return_points_deduction: the per-row proportional clause superseded and declared; negative balance, notes never taken back, bonuses never reversed, dedup followed.
- loyalty_ext_note_reinstatement: value clause superseded and declared; expiry "later of" rule and dedup expressly kept; note_conversion/birthday/courtesy sentences not touched.
- loyalty_ext_courtesy_note_reissue: expiry clause superseded and declared; value kept; window, rolling count, exclusions kept. The extended object rule "the note reissued is the member's most recently lapsed note" narrows the base ("A Finch Note that lapsed with expire_reason validity_ended may be reissued once") without a declaration -> observation O6 (in task 1 the only other lapsed note is a birthday note, which the base excludes anyway).
- Disguised forms: no anonymous intermediate factor or 0/1 multiplier found beyond F1; no dropped base branch.

### factor_ladders

| policy | factor | label | tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| missing_points | event_day_anchor | method | 3 | no | order |
| missing_points | event_multiplier | parameter | 3 | yes (bonus entry AND tier multiplier) | - |
| missing_points | late_event_share | parameter | 3 | no | - |
| missing_points | card_bonus_rate | parameter | 4 | yes (tender AND card product) | card |
| missing_points | financing_share | parameter | 3 | no | card |
| missing_points | card_standing_share | parameter | 3 | yes (status AND returned payments) | card |
| card_floor | floor_credit | parameter | 3 | no | card |
| card_floor | delay_anchor | method | 3 | no | card |
| card_floor | delay_goodwill | parameter | 3 | no | - |
| card_floor | card_spend_allowance | parameter | 3 | no | card |
| card_floor | allowance_standing | parameter | 3 | nominal (see F2) | card |
| card_floor | tailoring_allowance | parameter | 3 | no | alteration |
| deduction | refund_basis | method | 3 | no | order |
| deduction | card_basis | method | 3 | no | card |
| deduction | event_clawback | parameter | 3 | no | order |
| deduction | card_clawback | parameter | 3 | no | card |
| deduction | exchange_relief | parameter | 3 | yes (date AND price, replacement vs returned unit) | order |
| deduction | tier_cushion | parameter | 3 | yes (tier AND deduction count) | - |
| reinstatement | share_basis | method | 3 | yes (kept units AND allocation) | order |
| reinstatement | fee_share | parameter | 3 | no | order |
| reinstatement | expired_original | parameter | 3 | no | - |
| reinstatement | return_speed | parameter | 3 | no | order |
| reinstatement | cardmember_uplift | parameter | 3 | single record (status and product on one card row) | card |
| courtesy | tier_days | parameter | 3 | no | - |
| courtesy | card_days | parameter | 3 | yes (active account AND recent card purchase) | card |
| courtesy | lapse_cut | parameter | 3 | no | - |
| courtesy | registry_days | parameter | 3 | no | registry |
| courtesy | shopping_days | parameter | 3 | no | order |
| courtesy | return_share_rule | method | 3 | no | - |

- Counts per policy as declared: 6/5/... all within 4-6; each has >= 2 `parameter` and >= 1 `method`. Bindings disjoint within each policy; no `decides: result`. Every tier is stated in the rule with its value or method, and every value comes from the policy's own `params` or the variant table. No two tiers of any ladder select the same value or method.
- Labels: method tiers in refund_basis, card_basis, share_basis and return_share_rule change the formula; event_day_anchor and delay_anchor choose which record date anchors a day count (borderline "method", accepted, observation O7); parameter tiers change a number.
- Realism and reach (charter-global half; per-world weight is in each task file):
  - **card_floor scope makes three fall-throughs unreachable (finding F2).** The rule's scope sentence is "When the customer holds a Marlowe & Finch card account in active status whose card grants a higher Finch Circle tier than the membership record shows (Finch Circle Gold for a Store Card Elite or a Platinum Mastercard, Finch Circle Platinum for a World Elite Mastercard)". Every customer who reaches this write therefore holds an active World Elite, Store Card Elite or Platinum Mastercard, and: (a) floor_credit's fall-through "otherwise it stays the annual alteration credit of the tier on the membership record" is reached by no such customer; its baseline value, the credit of the tier being left, is what no programme tops a card-floor member up to (base `loyalty_alteration_credit_rules` uses "the new tier's annual amount"); its two live tiers (100.00 / 50.00) are exactly the Platinum and Gold `alteration_credit_annual_usd`, i.e. the base standard relabelled as a variation. (b) allowance_standing's condition part "the customer holds an active card account" holds of every customer who reaches this write, and its fall-through "none (0) when the customer holds no active card account" is reached by none. (c) delay_anchor's fall-through "otherwise from the change date" is reached by none: Store Card Elite and Platinum Mastercard are reached only by status review (card.yaml `application_open: false`), World Elite only by application, and every opened account carries `opened_date` ("Approval date"). Striking these three leaves delay_goodwill, card_spend_allowance, tailoring_allowance: 3 factors (< 4) and no `method` factor.
  - event_clawback (deduction) keeps all bonus-event points for returns authorized more than 60 days after purchase and card_clawback keeps card bonus points when the charged card is closed; a later return clawing back less is an unusual incentive for a department store -> observation O8 (not demonstrable to the RED standard; task 1 sits on tier 1 / active).
  - All other ladders' conditions are ones a department-store loyalty programme plausibly weighs (claim lateness, deferred-interest financing, card standing, restocking/label fees, note lapse, return speed, exchange, registry event, shopping recency, return share), and their outcomes are plausible goodwill amounts.
- Per-task requirements (>= 1 multi-source, >= 1 cross_difficulty): task component {missing_points, card_floor} has multi-source factors in missing_points and cross_difficulty factors reading order, card, alteration; component {courtesy, deduction, reinstatement} has multi-source factors in all three and cross_difficulty factors reading order, card, registry.

### findings

- **F1 — SOURCE-POLICY RED (undeclared override).** Symptom: loyalty_ext_missing_points_credit computes the card bonus of the claimed unit as "the late-credit qualifying amount times the late-credit card bonus rate times the late-credit financing share times the late-credit standing share" inside the adjustment entry. Root cause: base `loyalty_evt_points_earn` "When the purchase was charged to a Marlowe & Finch card, a card_bonus row adds the card's mf_bonus_points_per_dollar times the amount charged for it." governs that quantity and is not named in `overwrite` (which names only `loyalty_missing_points`); the extended replaced_by even keeps "every other points entry ... under the base earning rules". Affected: extended charter lines 1263-1274 (overwrite) and 1307-1317 (rule). Bears on task 0 (demonstration in `0.md`).
- **F2 — SOURCE-FACTOR RED (unreal ladders, charter structure).** Symptom and evidence as in factor_ladders (a)-(c). Affected: loyalty_ext_card_floor_tier rule lines 1544-1566, factors lines 1617-1691, baseline lines 1707-1712. Bears on task 0 (demonstration in `0.md`).
- Observations O1-O8 as listed above (no consequence demonstrable on either task world).

## closing_checklist

Written after both reveals (2026-10-13T16:01:18Z); nothing above this heading was derived from GT.

- Audit files: `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; this file sits alongside; first revision, no older revisions.
- Coverage and scopes: `charter_scope` of task 0 = {loyalty_ext_missing_points_credit, loyalty_ext_card_floor_tier}; task 1 = {loyalty_ext_courtesy_note_reissue, loyalty_ext_return_points_deduction, loyalty_ext_note_reinstatement}. Pairwise disjoint, jointly all five extended policies; each tree's root and prerequisites lie inside its own scope. Task tools closed (five tools, each used by exactly one task's GT), uuid8s independent.
- Trees: task 0 — 1 prerequisite, 1 value_input, user write (claim); task 1 — 2 prerequisites, 1 value_input + 1 state_gate, user write (reissue). Whole-difficulty graph acyclic, no cross-task edges.
- Factors: task 1 computations all bear weight against honest baselines; task 0's points computation bears weight; task 0's card-floor computation fails (F2: 3 surviving factors, no method).
- Gates: not re-run by this audit (the instantiation-stage gates were supplied green in the brief, with the expected pre-render traceability/validate_scenario misses).
- **The difficulty does not pass the source-layer audit.**
  - task 0: SOURCE-POLICY RED (F1, undeclared override of the `loyalty_evt_points_earn` card-bonus sentence); SOURCE-FACTOR RED (F2 card-floor ladders; seeded `status_review_date` 2026-03-15 not producible by the card charter). Problem tree PASS. GT equals the independent derivation in every value.
  - task 1: SOURCE-FACTOR RED (seeded refund `restocking_fee_amount` 97.35 contradicts the order charter's 95.96; producible values 2,195 / 6.52 instead of 2,189 / 6.51). Policy, tree and unique solution PASS. GT equals the independent derivation in every value.

## revision_2

### charter_global_frozen (revision 2)

- Inputs: `loyalty.extended.yaml` sha256[:16] `3407e05e6384fcf6` (changed from `88da07b45084a9d8` -> every charter-global section re-derived in full); `task_tools.py` `d8465483604d8bf5` (unchanged -> tool-module conclusions carried forward by reference to revision 1 § action_binding_and_uuids, re-confirmed by hash). Blueprint files unchanged since before round 1 (mtimes 2026-10-13T12:09-12:13). Masked views rebuilt by the coordinator: `0.json` `50502e5b24781283`, `1.json` `d42aff8ed77ae597`.
- Gate snapshot: `.audit_views/policy/finch_circle_rewards/snapshot_r2.txt` (2026-10-14T19:21:10Z): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; traceability only `discoverable_tool:tool_name` misses (0 others); validate_scenario INVALID with every `required document` line filtered by the script and no other error line. Entry conditions met; claims file `tasks/finch_circle_rewards/rework_r2_claims.md` present and read.
- Masked until the revision-2 per-task freezes: `tasks/finch_circle_rewards/tasks/*.json`, `plan.md`. Written before any revision-2 reveal; nothing here derives from revision-2 GT.
- Base copy: lines 1-1258 byte-identical to `blueprint/products/loyalty.yaml`. Every `superseded_clause` verbatim in its base rule; every `compute_basis` quotation and every `baseline.rule` sentence verbatim in its own rule; every `policy_source` verbatim; every `replaced_by` verbatim in its own rule **except** missing_points overwrite 3, whose folded YAML yields "the late- credit card bonus points" where the rule reads "late-credit" (observation R2-O1, wording only).

### policy_conflict_scan (revision 2)

Same five policies, tools, triggers and graph components as revision 1. New object rules: missing_points "the claimed unit is the member's most recent purchase record, by purchase date, on which no Finch Circle number was captured and which is kept"; card_floor "The floor card is the active card that grants the floor: an active World Elite Mastercard when the customer holds one, otherwise an active Store Card Elite, otherwise an active Platinum Mastercard." No two policies decide the same quantity; read boundaries unchanged (plus registry in card_floor).

### rule_compute_equivalence (revision 2)

- missing_points: claim bindings now `XLATEST(..., date_field='purchase_date', membership_linked=False, status='completed')` = "most recent ... by purchase date" — equivalent. Rest unchanged and equivalent.
- card_floor: floor card chain, floor credit (100.00/50.00 by floor tier), held credit, delay anchor (enrolled date if later than the card's review/opened date; else review date; else opened date), four-tier goodwill, spend net of merchandise credits, late-fee count over all the customer's card accounts (as the rule now states), tailoring, bridal (active Wedding Registry, 0-120 / 120-365 days), single half-up rounding: equivalent. `floor_credit` keeps a guard `else P('alteration_credit_annual_usd')` for "no floor card", which the rule's scope never reaches (observation R2-O2). Revision-1 O3 and O4 closed.
- deduction: refund basis, card basis, reason-keyed event share, exchange share, frequency cushion (0.95/0.98/1 on other deductions in 12 months), balance relief (deduction before relief vs ledger-sum balance, by tier group), per-component half-up then one final half-up: equivalent.
- reinstatement: fee share now over "the refunded merchandise before that fee (the refund amount plus the fee, less the sales tax refunded)": equivalent; rest unchanged.
- courtesy: "The courtesy validity days are the courtesy day count. The courtesy day count starts from the tier courtesy days." plus "... are added to the courtesy day count, and the courtesy lapse cut is taken from it": no flat sentence competes with the return-share ladder any more; registry days now an active **Wedding** Registry. Revision-1 O5 closed.

### action_binding_and_uuids (revision 2)

Carried forward (tool module hash unchanged): pairs distinct, no sequencing words, no example values in docstrings or parameter descriptions (no gold can leak), tools validate nothing, uuid8s independent.

### prerequisite_graph and prerequisite_sentences (revision 2)

- Same three edges, all `form: state`, verbatim, acyclic, `resolved_by` = depended-on `target_tool`, `kind` bindings exist (`earn_rate`, `return_pct`).
- missing_points: "The missing-points credit is fixed only after the membership record shows at least the Finch Circle tier that an active Marlowe & Finch card status floor grants the member." — now at the strength of its condition (revision-1 O1 closed).
- courtesy <- deduction: "The courtesy note's validity is fixed only after every refunded return of a purchase that earned points shows its return deduction entry on the membership's points history." — now at the scope of its condition (revision-1 O2 closed).
- courtesy <- reinstatement: unchanged, passes. No other cross-problem order sentence in any rule; no restatement in depended-on rules.

### override_declarations (revision 2)

- missing_points: `loyalty_evt_points_earn` purchase/bonus-event sentence and card-bonus sentence now named in `overwrite`, each scoped to the claimed unit and leaving every other purchase under base. **Revision-1 F1 closed.** The object rule "most recent purchase record ... on which no Finch Circle number was captured" narrows base `loyalty_missing_points` ("may ask for the points of that purchase ... naming the purchase_id") without a declaration -> observation R2-O3 (in task 0 the named mattress is that unit).
- card_floor: top-up clause declared; floor card chain consistent with base floor map and "A floor never lowers a higher earned tier".
- deduction: whole per-row clause superseded; the balance relief adjusts a quantity covered by that declaration ("then adjusted by the return shares worked out below").
- reinstatement: unchanged, declared.
- courtesy: the "most recently lapsed note" restriction now declared as a second overwrite keeping the base exclusions (revision-1 O6 closed).

### factor_ladders (revision 2)

| policy | factors (label, tiers) | multi-source | cross_difficulty |
| --- | --- | --- | --- |
| missing_points | event_day_anchor (m,3), event_multiplier (p,3), late_event_share (p,3), card_bonus_rate (p,4), financing_share (p,3), card_standing_share (p,3) | event_multiplier, card_bonus_rate, card_standing_share | order, card |
| card_floor | delay_anchor (m,3), delay_goodwill (p,4), card_spend_allowance (p,3), allowance_standing (p,3), tailoring_allowance (p,3), bridal_allowance (p,3) | delay_anchor (membership vs card dates) | card, alteration, registry |
| deduction | refund_basis (m,3), card_basis (m,3), event_clawback (p,3), exchange_relief (p,3), frequency_cushion (p,3), balance_relief (p,3) | exchange_relief, balance_relief | order, card |
| reinstatement | share_basis (m,3), fee_share (p,3), expired_original (p,3), return_speed (p,3), cardmember_uplift (p,3) | share_basis | order, card |
| courtesy | tier_days (p,3), card_days (p,3), lapse_cut (p,3), registry_days (p,3), shopping_days (p,3), return_share_rule (m,3) | card_days | card, registry, order |

- **Revision-1 F2 closed.** floor_credit is no longer a factor (plain floor-tier credit, the base standard). allowance_standing is a 0 / 1 / 2+ late-fee count, every tier reachable for a customer of the write. delay_anchor's three tiers are all reachable: enrolled after the card reached its current status; card reached at a review with an older membership; World Elite (opened by application, never reviewed) with an older membership. Its baseline ("counted from the date the floor card account was opened") is the third tier. Card floor: 6 factors, 5 parameter, 1 method.
- Revision-1 O8 closed: event_clawback is keyed on the return reason (fault returns 0, fit/gift 0.5, otherwise 1); card_clawback replaced by balance_relief; tier cushion replaced by frequency cushion. All outcomes plausible goodwill a department-store programme would publish.
- No two tiers of any ladder share a value or method; every tier is in the rule and in compute; labels honest (delay_anchor and event_day_anchor choose the anchor date of a day count, borderline method, accepted as in revision 1).

### findings (revision 2)

- F1: closed. F2: closed. Revision-1 observations O1-O6, O8: closed; O7 unchanged (accepted).
- New charter-global defects: none at RED level. Observations R2-O1 (replaced_by "late- credit"), R2-O2 (unreachable compute guard), R2-O3 (undeclared narrowing of the claimed-unit choice).
- Charter verdict: **CLEAN** (no open charter-global RED).

### closing_checklist (revision 2)

Written after the revision-2 reveals (2026-10-14T19:26:14Z).
- Files: `0.md`, `1.md` each carry `## revision_2` appended below revision 1 (revision-1 text untouched apart from the freeze-time metadata correction disclosed in revision 1).
- Scopes disjoint and complete (task 0 {missing_points, card_floor}; task 1 {courtesy, deduction, reinstatement}); tools closed; uuid8s independent; trees 1 and 2 prerequisites, value_input floors met, user writes present, acyclic.
- Factors: all 29 declared factors bear weight on their task worlds against honest baselines; per-task multi-source and cross-difficulty requirements met.
- Gates: taken from the coordinator snapshot `snapshot_r2.txt` (not re-run by the auditor).
- Charter: **CLEAN** (F1, F2 closed).
- Task 0: **SOURCE-FACTOR RED** — seeded `card_accounts.status_review_date` 2026-01-15 not producible given the seeded 2025 card spend (card charter mid-year upgrade by 2025-09-10); no scored consequence. Task 1: **PASS**.
- The difficulty does not yet pass the source-layer audit (one open seed-realism RED in task 0).

## revision_3

### charter_global_frozen (revision 3)

- Inputs: charter `b75cb2df6403a4f0` (changed from `3407e05e6384fcf6` -> re-derived), tools `d8465483604d8bf5` (unchanged -> revision-1 § action_binding_and_uuids carried forward by hash), blueprint unchanged (mtimes 2026-10-13T12:09-12:13). Views: `0.json` `8748fcb20b11a670` (rebuilt, changed), `1.json` `d42aff8ed77ae597` (identical to revision 2).
- Gate snapshot `snapshot_r3.txt` (2026-10-14T20:36:44Z): all gates OK; traceability non-tool_name misses 0; validate_scenario shows only the filtered `required document` class. Claims file `rework_r3_claims.md` present and read. `plan.md` not read.
- Written before any revision-3 reveal.

### re-derivation (revision 3)

- Scripted sweep over the whole charter: base lines 1-1258 byte-identical to the product; every `superseded_clause` verbatim in its base rule; every `replaced_by`, `compute_basis` quotation, `baseline.rule` sentence and `policy_source` verbatim in its own rule; no split hyphenated word (`\w+- \w+`) in any rule or replaced_by (**R2-O1 closed**).
- Changed text: (a) missing_points gains a fourth overwrite naming the base request sentence of `loyalty_missing_points`, scoped to "a missing-points request this policy handles", defining the claimed unit as "the member's most recent purchase record, by purchase date, on which no Finch Circle number was captured and which is kept"; a request for any other purchase stays under base (**R2-O3 closed**). (b) card_floor `floor_credit: K('platinum_floor_credit') if floor_card == 'Marlowe & Finch World Elite Mastercard' else K('gold_floor_credit')` — the unreachable guard is gone and the binding reads exactly the two tiers the rule names (**R2-O2 closed**).
- Unchanged in substance (params and the decisive compute bindings re-read): deduction, reinstatement, courtesy, card-floor ladders, prerequisite sentences (all three verbatim, state form, at their conditions' strength and scope), graph acyclic, `kind` bindings exist. Factor tables of `_difficulty.md` § revision_2 factor_ladders stand: 29 factors, each policy 4-6 with >= 2 parameter and 1 method, every tier reachable and plausible, no shared tier outcome.
- Charter-global findings: none. **Charter: CLEAN.**

### closing_checklist (revision 3)

Written after the revision-3 reveal (2026-10-14T20:39:11Z).
- Files `0.md`, `1.md`, `_difficulty.md` carry `## revision_3` below the untouched earlier revisions.
- Scopes disjoint and complete (task 0 {missing_points, card_floor}; task 1 {courtesy, deduction, reinstatement}); tools closed, uuid8s independent; trees of 1 and 2 prerequisites with value_input floors met, user writes present, graph acyclic.
- All 29 factors bear weight on their task worlds against honest baselines; per-task multi-source and cross-difficulty requirements met; every seeded cross-category row checked against its owning charter on its own dates (card status, statements, payments, promo, refunds, loyalty tier history) — none contradicts.
- Gates: coordinator snapshot `snapshot_r3.txt` (not re-run by the auditor).
- Charter **CLEAN**; task 0 **PASS**; task 1 **PASS**. All four relationships hold for both tasks: the difficulty passes the source-layer audit.

## revision_4

### charter_global_frozen (revision 4)

- Inputs: charter `2cc02a805e4486f0` (changed from `b75cb2df6403a4f0` -> re-derived), tools `d8465483604d8bf5` (unchanged, carried forward), blueprint unchanged. Views `0.json` `3b805be3087dd179` (changed), `1.json` `d42aff8ed77ae597` (unchanged). Snapshot `snapshot_r4.txt` (2026-10-14T21:12:02Z): all gates OK, TRACEABILITY OK, validate_scenario **VALID** (352 documents). Read in full: `audits/render_source/finch_circle_rewards/render_r1_loyalty.md` and `tasks/finch_circle_rewards/rework_r4_claims.md`. `plan.md` not read. Written before any revision-4 reveal.

### re-derivation (revision 4)

Scripted sweep over all five policies: base lines 1-1258 byte-identical; every superseded clause verbatim in its base rule; every replaced_by, compute_basis quotation, baseline.rule sentence and prerequisite sentence verbatim in its own rule; no split hyphenated word; a transitive reference walk over compute finds **no factor binding that reads a binding owned by another factor, and no factor owning `result`**.

Renderer items:
1. missing_points (two factors read `event_day`): closed. `event_day_anchor` (method) now decides `event_indicator` itself (the day tested by channel/fulfillment, then the bonus-entry lookup); `late_event_share` reads the claimed unit's purchase date (plain read `claim_date`, owned by no factor); the old event-multiplier factor is replaced by `price_type_share` (doorbuster/final sale 0, clearance 0.5, otherwise 1) and the tier multiplier is a plain `P('bonus_event_multiplier')`. Result: purchase points + int(pp x (mult-1) x indicator x late share x price share) + int(qualifying x card rate x financing x standing) — equal to the rule's result sentences.
2. card_floor (goodwill read the anchor's output): closed. One method factor `goodwill_anchor` applies the 25/15/10/0 scale to the days from the anchor it selects (enrolled date / review date / opened date); `apparel_allowance` added (3+ completed Apparel purchases in 12 whole months 10.00, 1-2 5.00, none 0.00).
3. deduction (card basis read `refund_dest`): closed. `refund_dest`, `refund_tax`, `card_credit` are plain reads owned by no factor; balance relief now compares the points the returned unit earned with the ledger-sum balance (no other factor's output).
4. courtesy (result inside a factor): closed. `return_share_rule` decides only `share_mode`; `result` assembles tier/card/registry/shopping days less lapse cut and applies the mode, quoting the rule's result sentence.
5. deduction rounding: closed. replaced_by and rule now read "each taken in proportion ... multiplied by the return share that applies to it and rounded half up to whole points, the sum then multiplied by the return frequency cushion and the return balance relief and rounded half up once more" = compute.
- Renderer note (baselines lacked the combination): closed. Each `baseline.rule` now carries the policy's result sentence and every factor default ("The late-credit card bonus rate is 0.", "The floor allowance standing share is none (0).", ...). Each stated default equals its ladder's fall-through, and each ladder sentence follows with explicit conditions, so the specific sentence governs (observation R4-O1: the rule now states each default flatly before its ladder — consistent with the baseline design, no second value on either world).

Factor structure (revision 4): missing_points — event_day_anchor (m), late_event_share, price_type_share, card_bonus_rate, financing_share, card_standing_share (6; multi-source card_bonus_rate, card_standing_share; cross order, card). card_floor — goodwill_anchor (m; multi-source membership vs card dates), card_spend_allowance, allowance_standing, tailoring_allowance, bridal_allowance, apparel_allowance (6; cross card, alteration, registry, order). deduction, reinstatement, courtesy — as revision 2 (6/5/6; result and balance-relief inputs restructured only). Every ladder >= 3 disjoint, reachable tiers stated in the rule; no shared tier outcome; outcomes plausible for a department-store programme (clearance/doorbuster items earning reduced or no event bonus is common practice; apparel buyers receiving alteration credit plausible). Prerequisite graph and sentences unchanged (three state-form edges, verbatim, acyclic).

Charter-global findings: none. **Charter: CLEAN.**

### closing_checklist (revision 4)

Written after the revision-4 reveal (2026-10-14T21:14:03Z). Earlier revisions untouched. Scopes disjoint and complete; tools closed; trees (1 and 2 prerequisites) hold with user writes; graph acyclic; 29 factors, all bear weight against honest, self-sufficient baselines; no factor reads another factor's output; every seeded cross-category row producible by its owning charter. Gates per `snapshot_r4.txt` (all OK, validate_scenario VALID). Charter **CLEAN**; task 0 **PASS**; task 1 **PASS** — the difficulty passes the source-layer audit.
