# Policy-task audit — rate_lock_extensions_and_disputes / charter-global

## charter_global_frozen

- Freeze time: 2026-10-13 05:51 UTC (written before any task's GT was revealed; nothing in this section derives from a revealed GT).
- Auditor: erl-task-policy-audit (independent auditor; not the instantiating agent).
- Frozen inputs (hashes re-checked against the coordinator brief, all match):
  - `tasks/rate_lock_extensions_and_disputes/lock.extended.yaml` sha256 `fd0da683afc72aa2fa5c5e2dc14b1399c16a41cec38d6d84e45601ce1f2928f1`
  - `tasks/rate_lock_extensions_and_disputes/task_tools.py` sha256 `96583d238dace22e7c044f773074f156c086b4dff50248f351de75fcc25ea951`
  - `.audit_views/policy_task/rate_lock_extensions_and_disputes/0.view.json` sha256 `0168b359…b7d`, `1.view.json` sha256 `4aea3d14…2c1`
- Fields permitted: `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml), the extended charter, task_tools.py, and each view's `frozen_time`, `user_scenario`, `initial_state`.
- Fields masked and not read before the per-task freeze: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`; `worklog.md` (both) never read; no other `env/` scenario, sibling difficulty or `/tmp/*_0059` instantiator scratch read; no recursive grep over `env/…/tasks/`.
- Entry conditions (Step 0): gate snapshot supplied with the brief (check_extended OK, check_task_tools OK, replay_tasks --check OK, check_solvability OK, check_compute OK, check_grounding OK, check_cross_fire OK; check_traceability NOT OK only on `unlock_*_discoverable_tool:tool_name` misses, a pre-render gate out of scope here). Masked views and hashes supplied. Entry conditions met.
- Base section: the base copy in the extended charter is verbatim identical to `blueprint/products/lock.yaml` (key-by-key YAML equality on all ten keys, and a textual diff of the base section shows only the trailing blank line before `extended_policies`).

Policy short names used below:

| short | policy id | target_tool (owner) | computes |
| --- | --- | --- | --- |
| EP1 | lock_ext_extension_request_length | submit_lock_extension_request_8348adff (user) | requested_term_days |
| EP2 | lock_ext_extension_dispute_relief | decide_extension_charge_dispute_a9bc145e (agent) | waived_amount |
| EP3 | lock_ext_extension_charge | book_lock_extension_178d685b (agent) | cost_amount |
| EP4 | lock_ext_appraisal_delay_waiver | waive_extension_charge_02e9996e (agent) | waived_amount |
| EP5 | lock_ext_relock_price | relock_expired_rate_20a82baa (agent) | relocked_price_points |
| EP6 | lock_ext_relock_fee | book_relock_fee_339fcee1 (agent) | cost_amount |
| EP7 | lock_ext_float_down_fee | exercise_float_down_fc7d974d (user) | fee_amount |

### policy_conflict_scan

- Subjects / triggers: EP1 `lock_request_logged` (on_request); EP2 `lock_dispute_resolved, lock_cost_waived` (state_due); EP3 `lock_extension_booked, lock_expiration_updated` (on_request); EP4 `lock_cost_waived` (state_due); EP5 `lock_relocked` (state_due); EP6 `lock_relock_fee_booked` (state_due); EP7 `lock_float_down_fee_booked, lock_repriced` (on_request). The only shared subject is `lock_cost_waived` (EP2 and EP4). They are partitioned by the rules themselves: EP2 decides "a dispute the borrower filed against an extension charge"; EP4 waives "when no dispute has been filed against that extension". No world can satisfy both on one extension entry. Compatible.
- Eligibility / time anchors: every extended policy inherits the base gates of its refs (lock_extension: locked, requested ≤ current expiration, file status list, increments, max_extensions/max_total_extension_days; lock_relock: inside the 30-day window, max_relocks; lock_float_down: float_down_allowed, locked, no CD, min improvement; lock_dispute_resolution: 10-business-day filing window, 5-business-day response). No extended rule weakens one of them.
- Action parameters / terminal states: EP3 writes expiration + cost; EP5 writes status/rate/price/expiration and books no fee; EP6 books the fee only; EP7 writes the float-down fee and new rate. No two policies write the same field of one record to different values in a shared situation.
- Cross-category reads: EP1 funding/loan/appraisal; EP2 loan/appraisal/credit; EP3 loan/funding/appraisal; EP4 appraisal/loan; EP5 loan/funding; EP6 appraisal/credit; EP7 loan/credit. Each `cross_category` block lists exactly the categories the compute reads (checked against every CFIELD/XCOUNT/XLATEST call).
- Task scopes (as derivable from the two worlds before the reveal): task 0 = {EP1, EP2, EP3}; task 1 = {EP4, EP5, EP6, EP7}. Pairwise disjoint; jointly cover all seven extended policies. (Confirmed against `charter_scope` only after the reveal, in the task files.)

### rule_compute_equivalence

Mechanical sweep (scratch script, deleted): every `compute_basis` quotation of all seven policies is a verbatim substring of that policy's `rule`; every sentence of every `baseline.rule` is a verbatim sentence of the `rule`; every `overwrite.replaced_by` is verbatim in the rule and every `superseded_clause` is verbatim in the named base policy's rule. Every factor's ladder tiers appear as rule sentences and as branches of the `decides` binding, and vice versa (manual check, policy by policy).

Back-sweep findings (no invented basis; the differences are approximations that coincide on both worlds — see findings CG-12):
- EP1 `ptd_issued - ptd_resolved > 0` counts issued vs cleared/waived rows instead of matching each condition through `source_condition_id`.
- EP3 `unrelieved_ext = prior_ext - waiver_entries` counts waiver entries rather than "earlier extensions that no waiver entry names".
- EP6 `waiver_count >= borrower_ext` counts waiver entries rather than "every borrower-borne extension entry … named by a waiver entry".
- EP3 `ext_days` rounds the ask up to a multiple of the shortest sold length; for every variant's `extension_increment_days` ([5,10], [5,10,15], [15,30]) this equals "the shortest of the lock's sold extension lengths that is at least the days asked", capped at the longest. Equivalent.
- EP3 `notice_adjust` applies the same-day surcharge to `notice_days <= 0`; the rule says "on the current expiration date itself"; a request after expiration cannot reach booking (base gate), so equivalent on the bookable domain.
- Tool arguments not produced by compute (EP3 `extension_seq`, `larkspur_borne_days`, `cost_bearer`, `new_expiration_date`; EP4 `waived_points`; EP5 `relocked_rate`, `new_expiration_date`; EP7 `new_rate`) each have a rule sentence that fixes them ("booked as the next extension in the lock's sequence", "the Larkspur-borne days booked on the entry are the extension days less the charged days", "set under the extension policy", "carries the waived points (the waived amount divided by the loan amount at lock times 100, rounded to three decimal places)", "keeps the expired lock's rate unless the rate on that relock request is higher", "the relock date plus the lock's relock term in calendar days", "the rate on the lock's latest float-down request").

### action_binding_and_uuids

- `(target_tool, computes)` pairs: seven distinct pairs, each claimed by exactly one policy (table above).
- uuid8 tails: 8348adff, a9bc145e, 178d685b, 02e9996e, 20a82baa, 339fcee1, fc7d974d — no shared prefix, no sequence, no adjacent values; consistent with independent generation.
- Docstrings: none names another tool, none states a position in a sequence relative to another problem. Literal ordering words occur only as argument provenance ("read out to the borrower before the call"), result description ("Afterwards the borrower's lock shows…") and ordinal ("1 for the first, 2 for the second"). Recorded as CG-15 (observation).
- No tool judges a prerequisite: every function body is unconditional create/update (no branch on lock status, request log, disputes, waivers or relock fees; `decide_…` branches only on its own `resolution` argument to decide whether to book its own waiver).

### prerequisite_graph

| edge | blocked | depends on | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | EP3 | EP1 | state_gate | lock_extension.requested_by_expiration (real eligibility id) | state | submit_lock_extension_request_8348adff = EP1 target |
| E2 | EP3 | EP2 | value_input | repeat_step (EP3 binding exists) | state | decide_extension_charge_dispute_a9bc145e = EP2 target |
| E3 | EP6 | EP5 | state_gate | `rate_locks.status` (a field, not an eligibility id — CG-10) | state | relock_expired_rate_20a82baa = EP5 target |
| E4 | EP6 | EP4 | value_input | borrower_share (EP6 binding exists) | state | waive_extension_charge_02e9996e = EP4 target |
| E5 | EP7 | EP5 | state_gate | lock_float_down.float_lock_active (real eligibility id) | state | relock_expired_rate_20a82baa = EP5 target |
| E6 | EP7 | EP6 | value_input | relocked_surcharge (EP7 binding exists) | state | book_relock_fee_339fcee1 = EP6 target |

- Every policy has `prerequisite` filled (EP1, EP2, EP4, EP5 `[]`). Every `problem` is an extended policy id of this file, none self-referential, none a base policy. Graph is acyclic (leaves EP1, EP2, EP4, EP5; EP3 → {EP1, EP2}; EP6 → {EP5, EP4}; EP7 → {EP5, EP6}).
- Every `policy_source` is verbatim in the blocked policy's own rule (mechanical check). All six edges `form: state`, no `fallback_reason` (correct).
- `condition` strength: E2, E3, E5, E6 match their sentences. E1's condition adds "later than the event_date of every extension entry already booked on the lock", a date-precise rendering of the sentence's "an extension request for it" (CG-9). E4's condition matches.
- `effect`: each resolving write genuinely makes the gate hold / moves the binding. E4's and E6's `effect` texts are phrased as a specific world's transition ("moves from the part-relief share to the full-relief share", "raises relock_entries from zero to one") rather than generally (CG-10, observation).

### prerequisite_sentences

Four-point test, per edge (connective / record-visible state / no tool, id or snake_case / strength):

- E1 "An extension is booked, and its cost fixed, only after the lock request log carries an extension request for it dated no later than the lock's current expiration date." — "only after"; state = a request-log row; clean; strength: "for it" carries the not-yet-consumed requirement (CG-9). Single write that brings it about: only `submit_lock_extension_request_8348adff` creates `lock_requests` rows. Derivation: EP3 sentence → request log holds no unconsumed extension request (each logged extension request already has its booked entry) → EP1 rule "An extension request asks the lock desk for a number of calendar days … whether the borrower logs it in the borrower portal or a loan officer logs it for the borrower" → the borrower's portal request.
- E2 "The cost of an extension is not fixed until every dispute filed on the lock against an earlier extension charge carries its decision record." — "not … until"; state = decision record; clean; strength = condition. Single write: only `decide_extension_charge_dispute_a9bc145e` creates `lock_disputes` rows. Derivation: pending extension_charge_disputed filing with no resolution record → EP2 rule "A dispute the borrower filed against an extension charge is owed a decision by the lock desk".
- E3 "A relock fee is booked only after the lock's record shows the relock, the lock back in locked status with a new expiration date." — "only after"; state = lock status + expiration; clean; matches condition. Single write: only `relock_expired_rate_20a82baa` moves status from expired to locked. Derivation: EP5 rule "The relock sets the lock back to locked with the relocked rate, the relocked price and the new expiration date." Second wording in the same rule ("owed as soon as the relock is recorded") — CG-7.
- E4 "The relock fee is not fixed until every borrower-borne extension charge on the lock that the appraisal-delay case covers carries its waiver entry." — "not … until"; state = waiver entry; clean; matches condition. Two writes of the difficulty can create a `lock_cost_waived` entry (EP4's tool, and EP2's tool with `extension_cost_waived`); the two are partitioned by whether a dispute was filed against the extension (CG-8), so the hop resolves uniquely on any world. Derivation: covered borrower-borne extension with no waiver → EP4 rule "Larkspur waives, on its own initiative, the cost of a borrower-borne extension that the appraisal-delay case covers when no dispute has been filed against that extension".
- E5 "A float-down is exercised, and its fee fixed, only once the lock's status reads locked." — "only once"; state = status; clean; matches. Single write from expired: the relock. Base `lock_float_down.float_lock_active` restates the gate (CG-7).
- E6 "The float-down fee is not worked out until every relock requested on the lock's request log carries its relock fee entry." — "not … until"; state = fee entry; clean; matches. Single write: `book_relock_fee_339fcee1`.
- No depended-on rule restates the blocked sentence. No extended rule states a cross-problem order that grounds no declared edge. No base sentence is the sole ground of any tree edge.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (finding half only):

- EP1 (refs lock_eligibility, lock_extension; `overwrite: []`): lock_eligibility's term-reach sentence governs `lock_requested` (initial lock), not an extension request; lock_extension governs the booked length, not the asked count. No sentence of either fixes `requested_term_days` of an extension request. No conflict.
- EP2 (refs lock_dispute_resolution, lock_extension): base "For an extension_charge_disputed dispute, the charged extension is waived … only when the appraisal-delay case … covers it; otherwise it is denied_borrower_caused." — declared. "Larkspur bears extension days in two cases only." — declared. Inherited intact: filing window, denied_untimely, 5-business-day response, "Every decision names the filing record". Consistent.
- EP3 (ref lock_extension): charged-days/cost sentence — declared; "two cases only" — declared. Base "never more than lender_delay_waiver_max_days borne for this reason across the lock" is followed in form, but EP3's "lender-delay days already relieved" counts every borne day beyond the complimentary days and every waiver's dollars, i.e. also days relieved for other reasons (CG-5, observation). "Underwriting backlog … never shift the cost" — EP3's clear-to-close relief is not a delay-based shift. Followed.
- EP4 (refs lock_extension, lock_dispute_resolution): "two cases only" — declared (goodwill and valuation). Base "Larkspur bears as many extension days as the appraisal was late" is not named, while the builder-completion offset can take covered days below it (CG-3). The amount-rose valuation makes a waiver's `cost_amount` differ from `cost_points × loan_amount_at_lock / 100`, against the base events/schema field meanings (CG-4).
- EP5 (ref lock_relock): worst-case clause — declared. Replacement text's scope ("every other relock keeps the higher-of comparison") vs. the rule applying the adders to every relock (CG-6).
- EP6 (ref lock_relock): relock-fee sentence — declared. Window, max_relocks inherited.
- EP7 (refs lock_float_down, lock_program_change_reprice, lock_dispute_resolution): new-rate/fee clause — declared; eligibility gates inherited; no conflict with the other two refs.
- "Larkspur bears extension days in two cases only." is superseded three times (EP2, EP3, EP4) with three different replacements; each adds a distinct situation, so the merged reading is additive (CG-2).

### factor_ladders

| policy | factor | effect | decides | tiers | multi-source tier? | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| EP1 | target_anchor | method | days_to_target | 3 | yes (funding status × loan purpose × occupancy) | funding |
| EP1 | stage_cushion | parameter | stage_cushion | 3 (3/1/0) | yes (loan conditions × funding status) | loan |
| EP1 | copy_cushion | parameter | copy_cushion | 3 (2/3/0) | yes (completed × delivered × waiver) | appraisal |
| EP1 | method_cushion | parameter | method_cushion | 3 (1/2/0) | no | funding |
| EP1 | cd_cushion | parameter | cd_cushion | 3 (2/1/0) | partly | loan |
| EP2 | order_clock | method | clock_start | 3 | yes (order × fee ledger × ITP) | appraisal |
| EP2 | order_grace | parameter | order_grace | 3 (1/5/3) | yes (rush × report type) | appraisal |
| EP2 | wait_goodwill | parameter | wait_goodwill | 3 (2/1/0) | no | — |
| EP2 | loyalty_goodwill | parameter | loyalty_goodwill | 3 (2/1/0) | yes (credit status × credit ledger) | credit |
| EP2 | suspension_offset | parameter | suspension_offset | 3 (2/1/0) | no | loan |
| EP3 | repeat_step | parameter | repeat_step | 3 (1.0/0.5/0) | yes (extensions × waivers × relocks) | — |
| EP3 | notice_adjust | parameter | notice_adjust | 3 (−0.25/+0.5/0) | yes (request × lock) | — |
| EP3 | returning_credit | parameter | returning_credit | 3 (0.25/0.125/0) | no | loan |
| EP3 | program_step | parameter | program_step | 3 (0.5/0.25/0) | no | loan |
| EP3 | occupancy_step | parameter | occupancy_step | 3 (0.5/0.25/0) | no | loan |
| EP3 | counting_rule | method | counted_days | 3 | yes (loan status × closing) | funding |
| EP4 | correction_goodwill | parameter | late_goodwill | 3 (2/1/0) | no | appraisal |
| EP4 | homebuyer_goodwill | parameter | homebuyer_goodwill | 3 (2/1/0) | two fields of one record | loan |
| EP4 | completion_offset | parameter | completion_offset | 3 (2/1/0) | yes (appraisal × loan status) | appraisal |
| EP4 | waiver_valuation | method | waived_value | 3 | yes (pricing entry × lock) | — |
| EP5 | pricing_basis | method | price_basis | 3 | yes (relock entries × request × lock) | — |
| EP5 | staleness_adder | parameter | staleness_adder | 3 (0.25/0.125/0) | yes (request × lock) | — |
| EP5 | fallout_adder | parameter | fallout_adder | 3 (0.25/0.125/0) | yes (funding × loan) | loan |
| EP5 | deposit_relief | parameter | deposit_relief | 3 (0.25/0.125/0) | yes (deposits × lock) | — |
| EP6 | fee_basis | method | fee_basis | 3 | yes (extension entries × request × lock) | — |
| EP6 | extension_step | parameter | extension_step | 3 (0.125/0.1/0) | yes | — |
| EP6 | borrower_share | parameter | borrower_share | 3 (0.25/0.5/1) | yes (waivers × appraisal) | appraisal |
| EP6 | partner_discount | parameter | partner_discount | 3 (0.05/0.025/0) | yes (credit × ledger) | credit |
| EP7 | improvement_pricing | method | improvement_points | 3 | yes (request × lock) | — |
| EP7 | relocked_surcharge | parameter | relocked_surcharge | 3 (0.25/0.125/0) | no | — |
| EP7 | stage_surcharge | parameter | stage_surcharge | 3 (0.2/0.1/0) | no | loan |
| EP7 | program_adjustment | parameter | program_adjustment | 3 (−0.125/+0.125/0) | no | loan |
| EP7 | loyalty_discount | parameter | loyalty_discount | 3 (0.1/0.05/0) | no | loan |
| EP7 | heroes_discount | parameter | heroes_discount | 3 (0.1/0.05/0) | yes (credit × ledger) | credit |

- Counts: EP1 5 (1 m / 4 p); EP2 5 (1/4); EP3 6 (1/5); EP4 4 (1/3); EP5 4 (1/3); EP6 4 (1/3); EP7 6 (1/5). All within 4–6, each ≥ 2 parameter and ≥ 1 method. Each policy's set has a multi-source and a cross-difficulty factor; task 0's set reads funding/loan/appraisal/credit, task 1's reads appraisal/loan/credit/funding.
- Bindings: each factor's `bindings` list is disjoint from every other factor's; every `decides` is an input, never `result`.
- Ladder sizes: every ladder has three pairwise-disjoint tiers including the fall-through, stated in the rule; no two tiers of any ladder select the same value or method (values listed above; method tiers differ in algorithm).
- Fall-through = baseline: true for every factor (checked binding by binding: target_anchor→DAYS(cur_exp,file_close); order_clock→itp_on; order_grace→standard grace; counting_rule→ext_days; waiver_valuation→entry per-day pricing; pricing_basis→higher-of; fee_basis→relock_fee_points; improvement_pricing→float_down_fee_points; all others 0 or share 1).
- Labels: the method labels of EP3 counting_rule, EP4 waiver_valuation (tier 1 is a different algorithm), EP5 pricing_basis, EP6 fee_basis and EP7 improvement_pricing change the algorithm. EP1 target_anchor and EP2 order_clock pick which event a day count runs to/from (tier 2 of target_anchor also adds a lag term); accepted as method but borderline (CG-11).
- Realism of conditions and outcomes: every other ladder is a treatment a residential lender's lock desk plausibly publishes (repeat-extension surcharges, notice credits, LLPA-style program/occupancy steps, loyalty and partner discounts, relock staleness/fallout adders, deposit relief, grace relocks, per-eighth float-down pricing, closing-stage and method cushions). The exception is EP2 `order_clock` (CG-1, SOURCE-FACTOR RED): measured against this scenario's own appraisal charter its tier 2 condition holds of essentially every non-transferred order, and its outcome coincides with tier 1's.

### findings

- **CG-1 — SOURCE-FACTOR RED (unreal ladder; bears on task 0).** Symptom: EP2's `order_clock` tier 2 ("when the borrower paid the base appraisal fee on that order after giving the intent to proceed, the clock starts on the day the fee was paid, because the order cannot be placed before the fee is collected") does not divide customers in any world consistent with the appraisal charter. Root cause: `blueprint/products/appraisal.yaml` policy `appraisal_fee_schedule`: "Appraisal charges are collected only while the loan file status is processing, … This follows from fee_collection_requires_itp: only after the borrower has received the Loan Estimate and given intent to proceed. The base_fee is charged once when the order is placed"; event `appraisal_ordered` trigger `map: {fee_component: base_fee, entry_date: ordered_date}`. So every non-transferred order's base fee is dated its `ordered_date`, which cannot precede ITP. Consequence: if the order is placed on a day after ITP, tier 2 holds and the clock starts on the order date, so the ordering days are 0. If it is placed on the ITP day, the fall-through starts the clock on ITP, which is also the order date, so the ordering days are again 0. Tier 1 (transferred in) also gives 0. Every tier therefore yields 0 ordering days, and the tier 2 condition holds of every non-transferred order placed after the ITP day. The tier divides customers only where a world's appraisal seed contradicts the appraisal charter. The task demonstration is in `0.md`. Affected: EP2 `rule`/`factors[order_clock]` in `lock.extended.yaml`, and task 0's seeded `appraisal_fee_ledger` row.
- CG-2 — observation. "Larkspur bears extension days in two cases only." is superseded by EP2, EP3 and EP4 with three different replacements. Read together they are additive (dispute relief, clear-to-close relief, own-initiative goodwill). Neither task shows a consequence.
- CG-3 — observation (bears on task 1, no consequence there). EP4's builder-completion offset ("the unfinished-home offset days are subtracted") can take covered days below base lock_extension's "Larkspur bears as many extension days as the appraisal was late … never more than lender_delay_waiver_max_days". That base sentence is not named in EP4's `overwrite`. On task 1, goodwill (4) exceeds the offset (2), so the covered days (14) stay at or above the appraisal-delay days (12).
- CG-4 — observation (bears on task 1's EP4 figures). Under EP4's amount-rose valuation, the waiver entry's dollars are "the extension's cost amount times the covered days divided by its charged days", and its points are "the waived amount divided by the loan amount at lock times 100, rounded to three decimal places". The base charter defines `lock_cost_waived.cost_amount` as "points times loan_amount_at_lock divided by 100, rounded to the cent" and `loan_amount_at_lock` as the "basis for every point-to-dollar conversion on the lock". That deviation is undeclared. It is not a RED: the conflicting text is an events/schema field description, not a sentence of a cited base policy, and EP4's own rule pins both figures explicitly. The numbers are in `1.md`.
- CG-5 — observation. EP3's "lender-delay days already relieved" counts every borne day beyond the complimentary days (including EP3's own clear-to-close relief days) and every waiver's dollars (including EP2's dispute relief granted on ordering days) against the appraisal-delay allowance. Base caps only days "borne for this reason". There is no consequence in task 0 (appraisal not late, so `appraisal_borne` is 0 either way), and EP3 is not scored in task 1.
- CG-6 — observation. EP5's `replaced_by` limits the replacement to "a first relock inside the grace days and … a second or later relock; every other relock keeps the higher-of comparison". But the rule then adds the staleness/fallout adders and deposit relief to every relock. Whether a late first relock gets the adders reads two ways. Task 1's relock is a first relock inside grace, so there is no consequence.
- CG-7 — observation. Second wordings of declared dependencies: EP6's rule "owed as soon as the relock is recorded" (in addition to E3's sentence); base `lock_float_down` "A float-down is accepted only while the lock status is locked." (E5); base `lock_extension` "An extension is booked only if the extension request was logged no later than the current lock expiration date." (E1). Each points to the same resolving write, so neither task shows a consequence.
- CG-8 — observation. E4's state ("carries its waiver entry") can be produced by EP4's tool or by EP2's tool (outcome `extension_cost_waived`). The two are partitioned by the rules ("when no dispute has been filed against that extension" / "a dispute the borrower filed"). Task 1 has no `lock_disputes` rows, so only EP4 applies.
- CG-9 — observation (bears on task 0). E1's sentence relies on "an extension request for it" to exclude extension requests already consumed by a booking. The declared condition makes that date-precise. Task 0 demonstrates that EP3's figures read off the consumed request would be identical, so the edge's weight rests entirely on the "for it" reading. See `0.md`.
- CG-10 — observation. E3's `gate: rate_locks.status` names a field rather than an eligibility id. The `effect` texts of E4 and E6 state one world's transition ("from the part-relief share to the full-relief share", "from zero to one") in the general charter.
- CG-11 — observation. EP1 `target_anchor` and EP2 `order_clock` are labelled `method` while their tiers mainly choose the date a day count runs to or from. They are accepted as method because they change which event is measured, and target_anchor tier 2 adds a term. The label is borderline.
- CG-12 — observation. The count-for-naming approximations listed under rule_compute_equivalence give identical results on both worlds.
- CG-13 — observation. EP1's baseline sentence "A count of zero or less means the lock already reaches that date, and the request asks for no days" and the extended "never below zero" after cushions disagree when the count is negative but the cushions are positive. Task 0's count is +4, so there is no consequence.
- CG-14 — observation. EP3's `baseline.rule` uses "the Larkspur-borne days" without carrying the defining sentence. The definition is in the rule and in base lock_extension, and `baseline.params` names complimentary_extension_days/lender_delay_waiver_max_days. On task 0 the baseline is still definite (0 borne days).
- CG-15 — observation. The docstrings' "before the call", "Afterwards" and "first" are argument provenance, result description and ordinal. None states an ordering between problems.

## closing_checklist

Written 2026-10-13 after both reveals. Everything above this heading was frozen before any reveal and is unchanged.

**The difficulty does not close.** Task 0 is SOURCE-FACTOR RED (`0.md` T0-1, rooted in CG-1). Task 1 is PASS.

| item | status |
| --- | --- |
| Per-task files one-to-one with tasks, `_difficulty.md` alongside, every comparison section present | yes (`0.md`, `1.md`); no older revisions exist |
| Every comparison carries a PASS | **no**: task 0 is SOURCE-FACTOR RED |
| Extended policies fully covered; scopes pairwise disjoint (whole trees) | yes: task 0 {EP1, EP2, EP3}, task 1 {EP4, EP5, EP6, EP7}; `charter_scope` agrees |
| Task tools and GT closed; uuid8s independent and frozen | yes (7 tools, 7 distinct pairs, see action_binding_and_uuids) |
| Each tree has 1–3 prerequisite problems, ≥ max(n−1,1) value_input edges, an owner=user problem, no cycle | yes: task 0 n=2 / 1 value_input / EP1 user; task 1 n=3 / 2 value_input / EP7 user; difficulty-wide graph acyclic, no cross-task edges |
| Every computation has a self-sufficient baseline and 4–6 surviving factors (≥2 parameter, ≥1 method), real ladders, every factor bearing weight, baseline ≠ gold | **no** for EP2 on task 0: `order_clock` fails the real-ladder / charter-consistent-seed test, leaving 0 surviving method factors. All other computations yes. |
| Instantiation-stage gates re-run on the final form | not run by this auditor (Step 0: gates are the coordinator's). The brief's snapshot is all green except check_traceability, whose misses are pre-render unlock names. |

## revision_2

### charter_global_frozen (revision 2)

- Freeze time: 2026-10-13 09:21 UTC. No round-2 task GT had been read when this section was written. Round-1 text above is untouched.
- Re-derivation grounds:
  - `lock.extended.yaml` changed: round 1 sha256 `fd0da683…28f1`, round 2 sha256 `cdfb268d3bf989c29cf0296ffb33409b7a861926f07d1de55e003aae63065fb2`.
  - `task_tools.py` is unchanged (`96583d23…a951`).
  - So every charter-global check that reads the charter was re-derived in full. The tool-module checks (uuids, docstrings, no prerequisite judging) carry forward by reference to the round-1 `action_binding_and_uuids` on the unchanged tool hash.
- The base section is still verbatim the blueprint `lock.yaml` (key-by-key YAML equality, all ten keys). The extended policies were re-read in full rather than trusting the reworker's "re-serialized, layout only".
- Mechanical sweep (scratch, deleted), all clean for all seven policies:
  - every `compute_basis` quotation is verbatim in its rule, and the basis keys equal the compute bindings;
  - every `baseline.rule` sentence is verbatim in the rule;
  - every `policy_source` is verbatim in the blocked rule;
  - every `replaced_by` is verbatim in its rule, and every `superseded_clause` is verbatim in the named base rule;
  - factor bindings are pairwise disjoint.

### Round-1 items: closed or not (verified against the round-2 charter text, not the reworker's claims)

- **CG-1 (SOURCE-FACTOR RED): CLOSED.** EP2 `order_clock` no longer reads the appraisal fee ledger. Its ladder is now:
  - transferred-in order → no ordering days;
  - not transferred in, and intent to proceed given on a Saturday or Sunday → clock starts the following Monday ("because Larkspur's appraisal desk places orders on business days");
  - otherwise → ITP date.
  - Compute: `itp_weekday = DAYS(K('reference_monday'), itp_on) % 7` (reference 2024-01-01 is a Monday), `clock_days = … DAYS(itp_on, ordered_on) - (7 - itp_weekday) if itp_weekday >= 5 …`, which is equivalent to the rule.
  - Against the scenario's charters: a weekend ITP is lawful under loan `loan_intent_to_proceed` ("in any way (e-sign portal acknowledgment …)"; the window counts business days only for its end), and nothing in the appraisal charter fixes the order date relative to ITP beyond fees requiring ITP. Every tier now yields a distinct outcome on charter-consistent worlds, and the tier 2 condition divides customers (weekend vs weekday ITP). The ladder is real.
  - `cross_category` for appraisal no longer lists `appraisal_fee_ledger`, which matches the compute.
- CG-2: unchanged, observation, and now extended. "Larkspur bears extension days in two cases only." is still superseded by EP2, EP3 and EP4. Base lock_extension's "Second, when the loan's appraisal order was completed after its due_date, …" is now superseded by both EP3 ("On an extension booked under this policy, every lender-delay day already relieved on the lock, for any reason, counts against the lender-delay allowance …") and EP4 ("With these, the covered days are …"). Each replacement is scoped to its own action (booking vs own-initiative waiver), and each rule restates the appraisal-delay case in full. The merged reading is additive, with no consequence on either world.
- CG-3: **CLOSED.** EP4 now names the "Second, when …" sentence in its `overwrite`.
- CG-4: **CLOSED.** EP4's valuation now fixes the waived points ("the waived points are the extension's cost amount times the covered days divided by its charged days, divided by the loan amount at lock and times 100, rounded to three decimal places"). Then "In every case the waived amount is the waived points times the loan amount at lock divided by 100, rounded to the cent", which is consistent with the base field meaning.
- CG-5: **CLOSED.** EP3 declares the base "Second, …" sentence superseded and states "for any reason". EP4's relieved-before now also counts waiver dollars, so the two policies agree.
- CG-6: **CLOSED.** EP5's `replaced_by` is now "The relocked price is the pricing basis plus the staleness and fallout adders less the deposit relief, rounded to three decimal places." It applies to every relock, as the rule does.
- CG-7: **PARTLY CLOSED, as claimed.** EP6's second wording ("owed as soon as the relock is recorded") is removed. The remaining second wordings are base-section sentences (`lock_float_down` float_lock_active; `lock_extension` requested_by_expiration), which the instantiator may not edit. Observation remains, no consequence.
- CG-8: unchanged, observation. The partition by "when no dispute has been filed against that extension" still holds.
- CG-9: **CLOSED.** E1's sentence now reads "… only after the lock request log carries an extension request dated later than the lock's latest extension entry and no later than the lock's current expiration date." That is record-precise and equal to the condition ("whose request_date is later than the event_date of the lock's latest lock_extension_booked entry and on or before rate_locks.lock_expiration_date").
- CG-10: **PARTLY CLOSED.** The E4/E6 `effect` texts are now general ("each waiver entry raises waiver_count; once …", "each relock fee entry adds one to relock_entries …"). E3's `gate` is still `rate_locks.status`, a field rather than an eligibility id. Observation remains, wording only.
- CG-11: **NOT CLOSED; observation** (it was never a RED). EP1 `target_anchor` and EP2 `order_clock` are still labelled `method`. order_clock's tiers are: no ordering days (a different computation), shift the start to Monday, and start at ITP. That is accepted as method, but borderline.
- CG-12: **CLOSED.** EP1 stage cushion ("issued prior-to-documents conditions outnumber its cleared and waived prior-to-documents conditions"), EP3 repeat step ("earlier extension entries outnumber its waiver entries by two or more / by exactly one") and EP6 share ("the lock's waiver entries are at least as many as its borrower-borne extension entries") now state exactly what the compute counts.
- CG-13: **CLOSED.** EP1 now reads "A count below zero is taken as zero" and "the days counted to the date to reach, taken as zero when below zero, plus the … cushions". Compute: `int(MX(0, days_to_target) + …)`. Rule, baseline and compute agree.
- CG-14: **CLOSED.** EP3's `baseline.rule` now carries the Larkspur-borne-days definition verbatim.
- CG-15: unchanged (tools unchanged), observation.

### New-defect scan over the changed charter

- policy_conflict_scan: subjects, triggers and the EP2/EP4 partition are as in round 1. EP4's new `education_goodwill` reads `homebuyer_education_completed` and `qualifying_income_pct_ami`, both declared in its `cross_category` (loan). EP2's appraisal `cross_category` reads match its compute.
- rule_compute_equivalence:
  - EP4 `education_goodwill`: `educated == True and income_pct <= K('moderate_income_ceiling_pct_ami')` matches "at or below the moderate-income ceiling"; tier 2 "certificate on file and above that ceiling" matches.
  - EP4 `waived_pts` is the three-tier valuation in points. `result = RND(waived_pts * L / 100, 2)` matches "In every case …".
  - EP4 `relieved_before` adds waiver dollars over one day at the standard per-day cost, matching the rule's parenthesis.
  - EP2 clock as above. No invented basis; no empty promise.
- prerequisite graph and sentences: same six edges, same kinds, forms and resolving tools; acyclic. E1's sentence is now precise (CG-9 closed). The others are unchanged in substance, and E2–E6 pass the four-point test as in round 1.
- factor_ladders (re-derived for changed factors):
  - EP2 order_clock: method, 3 tiers, distinct outcomes, real (see CG-1). Cross-difficulty: appraisal (order_reason, ordered_date) plus loan (ITP).
  - EP4 education_goodwill (replaces homebuyer_goodwill): parameter, 3 tiers (2/1/0), multi-source (education flag × income percentage), cross-difficulty loan. Goodwill for an educated buyer, larger at moderate income, is a plausible lender goodwill treatment. Fall-through 0 equals its baseline.
  - EP4 waiver_valuation: method, three tiers in points. Tier 1 (amount-rose proportion) is a different algorithm from tiers 2 and 3.
  - Counts: EP1 5 (1 m/4 p), EP2 5 (1/4), EP3 6 (1/5), EP4 4 (1/3), EP5 4 (1/3), EP6 4 (1/3), EP7 6 (1/5). All within bounds.
- No new charter-global RED found.

### findings (revision 2, charter-global)

- No charter-global RED. Remaining observations: CG-2 (now including the doubly superseded "Second, …" sentence), CG-7 (base-only wordings), CG-8, CG-10 (`gate: rate_locks.status`), CG-11, CG-15.

### closing_checklist (revision 2)

Written after both revision-2 reveals. The revision_2 charter-global section above was frozen before them.

| item | status |
| --- | --- |
| Per-task files one-to-one with tasks, `_difficulty.md` alongside, revisions appended (round-1 text untouched) | yes |
| Every comparison carries a PASS | yes: task 0 PASS, task 1 PASS (revision 2) |
| Extended policies fully covered; scopes pairwise disjoint | yes: {EP1, EP2, EP3} and {EP4, EP5, EP6, EP7}, matching `charter_scope` |
| Task tools and GT closed; uuid8s independent and frozen | yes (tool module unchanged) |
| Trees: 1–3 prerequisite problems, ≥ max(n−1,1) value_input edges, an owner=user problem, acyclic | yes: task 0 n=2 / 1 value_input / EP1 user; task 1 n=3 / 2 value_input / EP7 user |
| Every computation: self-sufficient baseline, 4–6 factors (≥2 p, ≥1 m), real ladders, every factor bearing weight, baseline ≠ gold | yes, on both worlds |
| Instantiation-stage gates on the final form | not run by this auditor. Coordinator's round-2 snapshot: all OK except check_traceability (7 pre-KB unlock-name misses, out of scope). |

**The difficulty passes the source-layer audit at revision 2.** Remaining observations (no RED): CG-2, CG-7 (base-only wordings), CG-8, CG-10 (`gate: rate_locks.status`), CG-11, CG-15, T0-3.

## revision_3

### entry (gated chain link; mechanical steps run by the auditor, read-only)

- Gate snapshot: `/tmp/erl0059_coord/gates.sh rate_lock_extensions_and_disputes --trace`, run 2026-10-13 from the repository root. Tail lines:
  - `EXTENDED OK`
  - `TASK TOOL CONTRACT OK`
  - `REPLAY OK` (0.json 21 acts det/nonvac True closure 29=29; 1.json 23 acts closure 21=21)
  - `SOLVABILITY OK`
  - `COMPUTE OK` (history_rows_max=8, branches_max=84)
  - `GROUNDING OK`
  - `SCOPE OK`
  - `TRACEABILITY OK` (0.json copied 27 missing 0; 1.json copied 28 missing 0)
  - No red gate, so this is not RED-INPUT.
- `mkviews.py rate_lock_extensions_and_disputes` printed:
  - `0.view.json sha256=8fe0a36cadf7f340b3a1db5a42164fc76542002add2f51ebb21edb9bf4092187` (unchanged from revision 2)
  - `1.view.json sha256=b38637e86311d2294d87cc00f5f284e4902a293d004f7f2e453da6db063f9b5a` (unchanged)
  - `task_tools.py sha256=96583d238dace22e7c044f773074f156c086b4dff50248f351de75fcc25ea951` (unchanged)
  - `lock.extended.yaml sha256=d5e1e5b2798dac3843856dffd2e605e10414bf47b2b8dd59db7c1a97c2ab23a0` (changed from `cdfb268d…`)
- Read: `audits/render_source/rate_lock_extensions_and_disputes/render_lock_r1.md` (the renderer's source-mismatch report). Not read: the worklogs.
- Freeze of this charter-global section: 2026-10-13, before reading any revision-3 task JSON.

### Re-derivation scope

- The charter changed, so every charter-global check was re-derived. The tool module is unchanged (round-1 uuid, docstring and no-judging conclusions carried forward on its hash). The views are unchanged (both worlds identical to revision 2).
- Base section: still verbatim the blueprint `lock.yaml`.
- Diff of `extended_policies` against revision 2:
  - Rule text changed in EP2, EP3, EP4, EP5 and EP7. EP1 and EP6 rules are unchanged.
  - Compute changed only in EP3 (`appraisal_borne`, `charged_days`) and EP4 (`base_covered`); everything else is identical.
  - EP5 gained `lock_dispute_resolution` in `base_policy_refs` and a second `overwrite`.

### Render-report items: closed in the source?

1. EP3 `charged_days` int truncation with no rule basis: **CLOSED.** The truncation moved to `appraisal_borne = int(MX(0, MN(appraisal_late, allowance) - relieved_days))`, and the rule now says "…less the lender-delay days already relieved on the lock, never below zero and counted in whole days with any fraction of a day dropped". `charged_days = MX(0, counted_days - comp_days - appraisal_borne)` is integer-valued (all terms are integers), and the rule says "never below zero". int() of a non-negative number is floor, which is "fraction dropped". Equivalent.
2. EP3 `appraisal_borne` floor at zero with no rule basis: **CLOSED** by the same sentence ("never below zero").
3. EP4 `booked_basis` rounded to the cent with no rule basis: **CLOSED.** The rule reads "(the extension's cost amount divided by its cost points times 100, rounded to the cent, is below the current loan amount at lock)". EP4 `base_covered` likewise gained `int(...)` together with the rule words "never below zero, counted in whole days with any fraction of a day dropped" (also in `baseline.rule`).
4. EP5 deposit relief with a 0.000 deposit percentage: **CLOSED.** The rule reads "when the lock holds a deposit above zero (…) that is at least the lock's deposit percentage of the loan amount at lock, rounded to the cent, the full deposit relief is subtracted". The ladder tier text matches, and this equals `deposit_held > 0 and deposit_held >= RND(pct × L / 100, 2)`.
5. EP5 `replaced_by` dropping the rate half: **CLOSED.** It now reads "For every relock this policy prices (…), the relocked rate stays the expired lock's rate unless the rate on its latest relock request is higher, and the relocked price is …; a lock past its relock window, or past its maximum relocks, remains under the base rule and takes a new lock at current market terms." It is verbatim in the rule and covers both halves of the retired clause.
6. Base `lock_dispute_resolution` relock-pricing dispute clause still pointing at the retired worst-case rule: **CLOSED.** EP5 now refs `lock_dispute_resolution` and supersedes exactly "relock_pricing_disputed disputes are upheld only when the relock price is worse than the worst-case rule allows, by repricing to the rule's result." (verbatim in base) with "A relock pricing dispute on a relock priced under this policy is upheld only when the relocked rate or price is worse for the borrower than this policy gives, by repricing to this policy's result." (verbatim in the rule). The retired clause genuinely conflicted, so it was right to retire it.
- Minor (same-day surcharge): **CLOSED.** The rule and ladder now say "on the current expiration date itself or later", equal to `notice_days <= 0`.
- Minor ("five steps"): **CLOSED.** It is now "Each step below adds to or subtracts from the per-day cost, and the adjusted per-day cost is never below zero" (`per_day_bps = MX(0, …)`).

### Six-kind sweep over the whole charter (revision 3)

- **Rule/compute rounding and floors:** every rounding (`RND`, `int`) and every floor or cap (`MX`, `MN`) in all seven computes has a rule clause:
  - EP1 `int(MX(0, days_to_target) + …)`: "taken as zero when below zero … as a whole number of calendar days".
  - EP2 `MX(0, clock_days - grace)`, `MN/MX` relief, `RND` 3 and 2: stated.
  - EP3: as item 1; `per_day` `MX(0, …)`; `RND` 3 and 2.
  - EP4: `int(MX(0, …))`, `MN(entry_charged, MX(0, …))`, `RND` 2 basis, `RND` 3 points, `RND` 2 amount: stated.
  - EP5: `RND` 3 price, `RND` 2 deposit due: stated.
  - EP6: `RND` 3 fee basis, `RND(MX(0, …) × share, 3)`, `RND` 2: stated.
  - EP7: `RND` 3 improvement ("to three decimal places", new wording), `RND(MX(0, …), 3)`, `RND` 2: stated.
  - The only unstated one is EP7's per-eighth tier `RND(per_eighth × improvement / eighth, 3)`. It is an identity on a 3-decimal improvement (0.125 × x / 0.125 = x), so it moves nothing.
- **compute_basis quotes verbatim:** mechanical sweep clean for all seven (every quote is in its rule; basis keys equal compute bindings).
- **replaced_by completeness and scope:** every `replaced_by` is verbatim in its rule. The three replacements of "Larkspur bears extension days in two cases only." (EP2, EP3, EP4) each scope themselves ("and only in that decision" / "and only on an extension this policy books" / "and only in such a waiver") and name the other two as the only exceptions to the surviving base cases. The merged reading is now explicit and unique (CG-2's residue is resolved). The two replacements of the base "Second, …" sentence (EP3, EP4) are each scoped to their own action and point to the other ("an extension booking measures its appraisal-delay days under the extension-charge rules" / "a waiver … and a decided extension-charge dispute measure their days under their own rules").
- **Overwrites retire nothing that does not conflict:** each of the nine `superseded_clause`s is verbatim in its base rule and is genuinely contradicted by its extended policy. Every overwritten base policy appears in `base_policy_refs` (EP5 now refs `lock_dispute_resolution`).
- **Undeclared base departures:** re-swept sentence by sentence against every `base_policy_refs` entry. No undeclared departure remains:
  - CG-3, CG-4 and CG-5 stay closed.
  - The render-report item 6 departure is now declared.
  - The EP7 improvement rounding agrees with base (base gives no rounding, and the rate field is 3-decimal).
- **Docstrings:** the tool module is unchanged, so effects vs body are as verified in round 1 (each docstring's stated writes match its body; no tool judges a prerequisite).
  - No gold value in docstring examples. The only examples are "(e.g. 6.875)" in `relock_expired_rate_20a82baa.relocked_rate` and `exercise_float_down_fc7d974d.new_rate`. Both tools are called only in task 1, whose gold arguments are 6.75 and 6.375.
  - 6.875 is task 0's world rate, not a gold argument of either tool. Extension_seq's "1 for the first, 2 for the second" is not task 0's gold (3).
- Prerequisite graph and sentences: unchanged from revision 2 (six edges, state form, acyclic; E1 precise).
- Factor ladders: unchanged in structure. The EP5 deposit_relief tier text and the EP3 notice tier text were reworded to match compute. Counts are as in revision 2; every ladder has 3 distinct, real tiers.

### Earlier closures: no regression

- CG-1 (RED) stays closed: order_clock unchanged from revision 2.
- CG-3, 4, 5, 6, 9, 12, 13, 14 stay closed.
- CG-2 is now resolved (explicit scoping).
- CG-7, CG-10 and CG-11 remain observations: base-only second wordings; `gate: rate_locks.status`; borderline method labels.
- CG-8 and CG-15 remain observations.

### findings (revision 3, charter-global)

- No charter-global RED. No new defect.
- Observations carried: CG-7, CG-8, CG-10, CG-11, CG-15.

### closing_checklist (revision 3)

Written after both revision-3 reveals; the revision-3 charter-global section above was frozen before them.

- Per-task files carry revision_3; earlier revisions untouched. Both comparisons PASS.
- Coverage and disjoint scopes: unchanged and confirmed ({EP1, EP2, EP3} / {EP4, EP5, EP6, EP7}).
- Trees: task 0 n=2 / 1 value_input / user EP1; task 1 n=3 / 2 value_input / user EP7. Acyclic.
- Computations: every one has a self-sufficient baseline ≠ gold. Factor counts are within bounds, every ladder is real, and every factor bears weight on its world.
- Gates on the final form: all OK, including TRACEABILITY (0 misses), per the snapshot in the entry section above.
- Every render-report item (6 mismatches + 2 minor) is closed in the source. The six-kind sweep is clean. No round-1 or round-2 closure regressed. No scored value changed (all equal revision 2), and all remain uniquely entailed.

task0=PASS  task1=PASS
