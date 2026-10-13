# Policy-task audit — gift_cards_and_store_credit / charter-global

## charter_global_frozen

- auditor: independent policy-task auditor (erl-task-policy-audit), revision 1
- freeze time: 2026-10-05T00:55Z (wall clock), written before any task's GT field was opened
- freeze hashes (sha256, recomputed by the auditor and equal to `audits/_views/policy_task/gift_cards_and_store_credit/HASHES.txt`):
  - `tasks/gift_cards_and_store_credit/credit.extended.yaml` = `1bb5ab220f3309f05a2d5d3a18ae1b3c6ef72c9894b728064167dafd3a9b0c47`
  - `tasks/gift_cards_and_store_credit/task_tools.py` = `40d756c543db3020653f9ba3d2b0b80451cd9dc67b69fb67aff82cc8714ff81e`
  - `0.view.json` = `b69fdde606d850d96e16c50ed5e794250564526ead97b7288c6352735e49d28f`; `1.view.json` = `925c277561dfd8f852674eb20369f8b6d5dcb62d20e9ad45cfdaf59dd581c341`
- fields read: `blueprint/blueprint.yaml`, `blueprint/share_tools.py`, `blueprint/products/{credit,returns,loyalty,pass,claims}.yaml` (targeted sections), the extended charter in full, `task_tools.py` in full, the two masked views (`frozen_time`, `user_scenario`, `initial_state`).
- fields masked and not opened before this file and both tasks' frozen sections were on disk: `tasks/gift_cards_and_store_credit/tasks/*.json` in full (`evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, closures), `worklog.md`, any earlier audit.
- entry conditions (Step 0): gate snapshot `audits/_views/policy_task/gift_cards_and_store_credit/GATES.txt` supplied — EXTENDED / TASK-TOOL-CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK, CACHE-DIFF informational, traceability deferred to the KB stage; masked views and hashes supplied. Entry conditions met.
- read isolation: no other `env/` scenario and no sibling difficulty's `tasks/` directory was read; every grep was scoped to explicit files under `blueprint/products/` or `erlbench/`.
- note on the compute DSL: the evaluator of the restricted expressions lives outside the read domain; where this file reasons about a compute expression it relies on the expression text and on the `rule`, which is authoritative.

### policy_conflict_scan

Structured policy = base section (verbatim copy of `blueprint/products/credit.yaml`; `diff` of lines 1–1067 against the blueprint shows only a trailing blank line) + four extended policies:

| id | subject | target_tool / computes | owner | trigger |
| --- | --- | --- | --- | --- |
| credit_ext_instant_credit_recovery | credit_clawed_back | claw_back_instrument_value_f010c427 / clawback_usd | agent | state_due |
| credit_ext_small_balance_cash_out | credit_closed_by_customer, credit_cashed_out | confirm_balance_cash_out_04a53640 / cash_out_usd | user | on_request |
| credit_ext_stolen_card_replacement | credit_replaced, credit_transferred_out | issue_card_replacement_8a64787f / replacement_usd | agent | on_request |
| credit_ext_card_balance_consolidation | credit_closed_by_customer, credit_transferred_out | confirm_card_consolidation_106a95bf / consolidation_usd | user | on_request |

Overlaps examined:
- `credit_closed_by_customer` is shared by the cash-out and consolidation policies (and by base `credit_evt_cash_out`). They are separated by the tool, by `close_reason` (cashed_out vs consolidated) and by the request type; no situation makes both apply to one write. Compatible.
- `credit_transferred_out` is shared by replacement and consolidation; separated by `transfer_reason` (replacement vs consolidation) and by tool. Compatible; this separation is what lets the consolidation prerequisite sentence single out the replacement write (see `prerequisite_sentences`).
- Eligibility / time anchors: replacement keeps base `settlement_wait` (1 business day for gift cards, lock date day zero), `ownership_proof`, `replacement_limit`; cash-out keeps base state register thresholds, `cash_out_eligible`, "A locked instrument must be unlocked or replaced first"; consolidation keeps `consolidation_min_instruments` active instruments of a type with `consolidation_allowed`. No extended policy weakens them.
- Cross-category read boundaries: every compute read of another category is declared in `cross_category` (recovery: returns/loyalty/pass; cash-out: returns/orders/loyalty/claims; replacement: claims/loyalty; consolidation: loyalty/pass/returns). No undeclared read found.
- Cross-charter overlap (outside this charter, recorded as observation O-1 below): `returns_evt_instant_credit` (returns charter) also governs recovery of instant Return Store Credit, and its event `returns_instant_credit_reversed` triggers `credit:credit_clawed_back` with reason `failed_return_inspection`.

Scope exclusivity (derived from the policies and the two worlds, before reveal): task 0's world (an inspected instant-credit Store Credit Return with a small CA balance) engages recovery → cash-out; task 1's world (a reported_stolen plastic gift card plus an e-Gift Card) engages replacement → consolidation. The two scopes are disjoint and together cover all four extended policies. To be confirmed against `charter_scope` after reveal.

### rule_compute_equivalence

Check 2, per policy. Every compute binding carries a `compute_basis` quotation that is a verbatim fragment of the rule; the sweep back:

**credit_ext_instant_credit_recovery**
- instant credit / line credits / rejected part / restocking part / box-fee part / fee part / limit-to-balance + half-up rounding: each sentence of the rule implemented (`instant_credit`, `line_credits`, `rejected_part`, `restock_booked`, `box_booked`, `fee_part`, `result`).
- restocking cap ladder (60/24 whole months; 15.00/25.00/uncapped) = `restocking_part`; box share ladder (0/0.5/1.0) = `box_share`; absorption ladder (>14 / >7..≤14 / ≤7 days) = `absorbed_share`; member treatment (Platinum/Icon/Atelier ∧ ≥6 earning postings → ×0.5 floor to dollar; Silver/Gold ∧ ≥3 → ×0.75 ceil to cent; else unchanged) = `fee_after_member`; allowance (0 → 5.00; 1 → 2.00; ≥2 → 0) on the customer's *other* returns = `incident_lines_all − incident_lines_this`, `allowance`. Every ladder tier is a rule sentence and a branch of its binding, and vice versa.
- Minor (observation O-2): `rejected_part` carries `MX(0, …)` with no rule sentence saying "never below zero"; with line credits never exceeding the instant credit it is inert. `box_fee_part` rounds in all three tiers while the rule states rounding only for the 0.5 tier; inert on cent amounts at shares 0 and 1.0.

**credit_ext_small_balance_cash_out**
- current balance, returned-order value (balance − refunds to the instrument, floor 0), promotional exclusion (share / whole / none, half-up), settlement hold (1.0 / 0.5 half-up / 0), availability period (7 / 9 / 12) adjusted by claims record (−1 / +3 / 0), refund hold (whole refunded value until the period has passed since the latest refund), lock reserve (0.25 / 0.10 / 0 of balance − held refund, half-up), result (balance − all deductions, floor 0): each sentence has its binding.
- `refunds_in` sums every `credit_refunded_to_instrument` row while the rule says "refunds loaded onto it from orders paid with it"; under base `credit_evt_refund_to_instrument` a refund lands only on the instrument it was spent from, so the two coincide.
- Counting boundary (observation O-3): the rule says refunds "become payable once the refund availability period has passed since the most recent such refund, counted in calendar days from that refund's date"; compute holds while `DAYS(last_refund, NOW) < period`, i.e. payable on the day the count is reached. The rule states the count's origin (day zero = refund date) but, unlike base `credit_evt_lost_stolen` ("the lock date is day zero, and the replacement may be issued on the day the count is reached"), does not state in words whether the day the count is reached is already payable. The natural English reading ("N days have passed since D" on D+N) matches compute; the consequence in task 0 is examined in `0.md`.
- The lock reserve rule says "After a lock on the instrument has been lifted"; compute reads `locked_date` without testing that the lock is lifted. Base "A locked instrument must be unlocked or replaced first" keeps a currently-locked instrument out of cash-out, so the two cannot diverge on an eligible instrument.

**credit_ext_stolen_card_replacement**
- protected balance (sum of every ledger entry), hold share ladder (stolen/unauthorized ∧ unregistered on or before lock → 0.40; stolen/unauthorized ∧ registered → 0.15; lost → 0), claims adjustment (none in 12 m → −0.05; ≥2 → +0.20; once → 0; floor 0), release (≥4 uses → 30.00; 2–3 → 20.00; else 0), hold on the balance above the release (half-up), member treatment (Gold+ ∧ ≥24 m → ×0.5 floor to dollar; Silver ∧ ≥12 m → ×0.75 ceil to cent; else unchanged), result: all implemented.
- Rule-internal wording (observation O-4): the rule carries the baseline sentence "The investigation hold share is nothing, and the investigation hold is the protected balance times the investigation hold share" and, two sentences later, "A card locked for a theft or misuse report carries an investigation hold share: … the share is `hold_registered_share` …". Read as default-then-specific the two compose; read literally they assert two values for the same quantity. This is the baseline-in-rule form the instantiation design prescribes; recorded as an observation, not a red, because the factor sentence is explicitly conditional and the baseline sentence is the one a reader displaces.

**credit_ext_card_balance_consolidation**
- carried value (replacement transfer-out on the stolen/lost card), standing limit (150/100/60), age application (≥12 m → no limit, whole carried value; 3–11 m → ×1.5 floor to dollar; <3 m → as set), Unlimited add-on (40/20/0), purchasing add-on (30/15/0), return record (+10 / −25 floor 0 / 0), add-ons applied after the age application, result `MN(carried, limit)`: all implemented.
- Latent rule-internal conflict (observation O-5): the age tier says "no move limit applies and the whole carried value moves", while the closing sentence says the return amount is "taken off … the move limit after its application for the card's age"; compute sets `aged_limit = carried_value` and then subtracts `return_heavy_reduction_usd`, so for a card ≥12 months old and a holder with ≥3 authorized return lines the result is carried − 25.00, not "the whole carried value". No task world of this difficulty reaches that corner (task 1's card is 10 months old, 0 authorized lines in window), so no consequence is demonstrable here.
- `return_change` counts authorized return *lines* (`XCOUNT return_lines event_type=returns_line_authorized`); the rule says "when lines were authorized on returns `return_heavy_count` or more times". Lines-vs-returns is a latent reading split only when several lines sit on one return; not reached in task 1 (0 lines in window).

No tier present in one face and absent from the other was found. Check 2: PASS (observations only).

### action_binding_and_uuids

- `(target_tool, computes)` pairs: four distinct pairs, each claimed by exactly one policy.
- uuid8s: `f010c427`, `04a53640`, `8a64787f`, `106a95bf` — no shared prefix, no shared tail, no sequence; consistent with independent generation.
- Docstrings: none names another tool, none carries before/after/first. One soft reference (observation O-6): `confirm_card_consolidation_106a95bf.source_instrument_id` says the reference is read out "from the stored-value instrument lookup or from the receipt of the action that issued it" — it points at the output of an issuing action without naming it or stating an order.
- Business reading of each tool is single: clawback (reason enum with `failed_return_inspection` / `qualifying_purchase_refunded`), cash-out (holder confirms, partial allowed), replacement (new active instrument of the replacement type, old card stays locked holding the remainder), consolidation (holder confirms, partial allowed, source stays active holding the remainder). The tools add no confirmation, review or wait.
- Tool bodies validate nothing: none checks status, eligibility, ownership, timing or a prerequisite (`claw_back…` and the others only `find` the instrument and write). Check 3: PASS.

### prerequisite_graph

| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| credit_ext_small_balance_cash_out | credit_ext_instant_credit_recovery | value_input | balance_now | state | claw_back_instrument_value_f010c427 |
| credit_ext_card_balance_consolidation | credit_ext_stolen_card_replacement | value_input | carried_value | state | issue_card_replacement_8a64787f |

- `prerequisite` filled on all four policies (`[]` on recovery and replacement). Each `problem` is another extended id in this file; none points at a base policy or itself. Graph: two disjoint edges, acyclic.
- `policy_source` verbatim in the blocked policy's own rule: cash-out sentence "The cash-out amount is fixed only after the store credit's ledger carries the recovery entry owed for every return whose instant credit was loaded onto it and whose inspection results have posted." — present in `credit_ext_small_balance_cash_out.rule`; consolidation sentence "The consolidation amount is not worked out until the stolen or lost card's ledger carries the replacement transfer-out entry naming the card that took over its protected value." — present in `credit_ext_card_balance_consolidation.rule`.
- `form: state` on both, no `fallback_reason` on either (correct).
- `gate` bindings exist in the blocked computes (`balance_now`, `carried_value`); `resolved_by` is the depended-on policy's `target_tool` in both; each write changes the gate's value (clawback lowers `balance_usd`; replacement writes the `credit_transferred_out` row that `carried_value` sums).
- `condition` vs sentence: cash-out condition matches the sentence's scope ("every such return whose `return_cases.inspected_date` is set"). Consolidation condition adds "and that replacement card is active", which the sentence does not carry (observation O-7: slight strengthening; the same replacement write creates the card `status=active`, so the extra clause never separates from the sentence's state).
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` text. Check 7: PASS (observation O-7).

### prerequisite_sentences

Edge A — cash-out ← recovery.
- Four-point test: (1) ordering connective "only after", joining the policy's own result ("the cash-out amount is fixed") to what it waits on; (2) state form — "the store credit's ledger carries the recovery entry owed for every return whose instant credit was loaded onto it and whose inspection results have posted": a record-visible state of `credit_transactions` on the instrument, no performer, no tool; (3) no tool name, policy id, snake_case token or row id; (4) scope equals `condition` (all such returns, inspection posted).
- Single resolving write: the only write of this difficulty that puts a recovery entry for a return on a store credit's ledger is the clawback with reason `failed_return_inspection` described by `credit_ext_instant_credit_recovery` ("clawed back, once the return's inspection results are posted, for the instant-credit recovery … booked against the return's number"). Replacement and consolidation write transfer rows, cash-out writes a cash-out row. Exactly one.
- Derivation (single reading): sentence → look at the store credit's `source_reference` return → its `return_cases.inspected_date` is set → the ledger has no `credit_clawed_back` row for that return → the policy whose own rule books a recovery on an instant Return Store Credit once inspection results post is the instant-credit recovery → book it → read the lowered balance.
- The depended-on rule does not restate the sentence; the cash-out rule carries no second wording of the dependency.

Edge B — consolidation ← replacement.
- Four-point test: (1) "not … until"; (2) state form — "the stolen or lost card's ledger carries the replacement transfer-out entry naming the card that took over its protected value": record-visible (`credit_transferred_out`, `transfer_reason=replacement`, `counterpart_instrument_id`); (3) no tool/id/snake_case; (4) scope matches (modulo O-7).
- Single resolving write: only the replacement write books a transfer-out with reason replacement; consolidation's own write books reason consolidation. Exactly one.
- Derivation: the stolen card's ledger has no replacement transfer-out → the policy whose rule issues "a new instrument of the `replacement_variant` … the transfer-out row on the old instrument names the replacement as counterpart" is the stolen-card replacement → issue it → the new card is the moving card and the transfer-out amount is the carried value.
- The replacement rule does not restate the sentence.

Other cross-problem orders in rules:
- Base `credit_evt_cash_out`: "A locked instrument must be unlocked or replaced first." — a base sentence stating a cross-problem order. Neither task's tree rests on it (task 0's store credit is active with its lock lifted; task 1's root is consolidation, whose edge is grounded by its own extended sentence). Observation O-8.
- `credit_ext_stolen_card_replacement`: "the investigation hold stays frozen on the old instrument until the theft review releases it" — an external process, not a problem of this charter and not a prerequisite of any write. Not an undeclared dependency.
- Docstrings are silent about sequence (see O-6).
Check 6: PASS.

### override_declarations

**credit_ext_instant_credit_recovery vs credit_evt_clawback** (sentence by sentence):
1. "Value is taken back only from an instrument with `clawback_allowed`." — followed (Return Store Credit `clawback_allowed: true`).
2. "Return Store Credit issued before a return was inspected is clawed back for the value of the units the returns charter rejects at inspection (reason failed_return_inspection)." — replaced; declared in `overwrite[0]` verbatim.
3. Bonus Gift Card clawback / voiding sentence — not touched; governs a different instrument.
4. "A clawback is limited to the current balance (`clawback_limit`); whatever cannot be recovered is settled under the returns charter or written off, and the balance never goes below zero." — followed (`result` = `MN(balance_now, …)`).
5. "Only one clawback is made per instrument for each return or order that caused it." — followed.
No undeclared override inside the credit charter. Disguised forms: no anonymous intermediate (the fee parts are named in the replacing sentence's "instant-credit recovery worked out below"), no 0/1 multiplier, no dropped base branch.

**credit_ext_small_balance_cash_out vs credit_evt_cash_out**:
1. State-register sentence (pay only where billing-state law requires it; other states cannot cash out) — followed; inherited.
2. "Only instruments with `cash_out_eligible` qualify — promotional value is never cashed out." — followed; extended adds a promotional-tender exclusion that is consistent with it.
3. "The balance must meet the state's threshold with its comparison … and in Massachusetts credit_msr_used_pct …" — not overwritten, therefore inherited: the instrument's balance at the cash-out must be below (or at/below) the state threshold. Extended is silent on it; the merged semantics are unique (threshold on the balance, amount by the extended computation).
4. "A cash-out closes the instrument for its whole balance; it is never partial." — replaced; declared `overwrite[0]`.
5. Confirmation sentence — replaced; declared `overwrite[1]`.
6. Mailed check within `cash_out_processing_business_days` — followed.
7. "A locked instrument must be unlocked or replaced first." — followed (inherited).
8. Consolidation sentence — not touched by this policy (replaced by the consolidation policy).

**credit_ext_stolen_card_replacement vs credit_evt_lost_stolen**:
1. Lock on the holder's report; "only value still on the instrument at the lock is protected … spending before the lock is never reimbursed" — followed; the protected balance nets charges captured after the lock for orders placed before it, consistent with "only value still on the instrument at the lock".
2. Unlock sentence — not engaged.
3. `replaceable_if_lost` — followed. 4. settlement wait (business days, lock date day zero) — followed. 5. registration-or-purchaser proof — followed. 6. `replacement_limit_12m` with handoff beyond it — followed.
7. "The replacement is a new instrument … loaded with the whole balance at the lock plus refunds received while locked; the old instrument closes with reason replaced …" — replaced; declared `overwrite[0]` (investigation hold stays on the old card).

**credit_ext_card_balance_consolidation vs credit_evt_cash_out, credit_evt_lost_stolen**:
- Consolidation sentence of `credit_evt_cash_out` (new target instrument, whole balances, each closes) — replaced; declared `overwrite[0]` (existing receiving card, partial move, source closes only when empty).
- `credit_evt_lost_stolen`: no sentence governs the consolidation amount; nothing overridden, nothing needing declaration.
- `credit_agg_multi_holding` ("value moves between instruments only by replacement or a consolidation the holder confirms") — followed.

Observation O-1 (cross-charter, outside `base_policy_refs`): `returns_evt_instant_credit` (returns charter) — "At settlement the difference between that instant credit and what is actually owed after inspection and fees is reconciled: … a negative difference is recovered from the Return Store Credit instrument up to its current balance" — and the event `returns_instant_credit_reversed` ("Instant credit paid at first scan for units that inspection rejected or found missing is recovered"), which triggers `credit:credit_clawed_back` (`failed_return_inspection`). The extended recovery's `overwrite` names only `credit_evt_clawback`. The returns rule speaks "at settlement" and the credit rule "once the return's inspection results are posted", so on a world whose return is inspected but not settled they do not both fire on the same write; the latent cost is that, at the later settlement, the returns rule would compute its own recovery of the fees the credit-side clawback already took (or partly forgave). Its bearing on task 0 is examined in `0.md`.

Check 1 finding half: no undeclared override inside the credit charter. PASS with O-1.

### factor_ladders

Counts per policy (structure only):

| policy | factor | effect | decides | tiers | non-fall-through tiers compound over distinct records? | cross_difficulty (declared) | records read |
| --- | --- | --- | --- | --- | --- | --- | --- |
| recovery | restocking_cap_by_membership_length | parameter | restocking_part | 3 | no (enrolled_date only) | loyalty | loyalty_memberships |
| recovery | box_fee_share_by_unlimited_plan | parameter | box_share | 3 | conjunction status ∧ plan coverage, but both from the one pass_memberships row (coverage is the plan's charter parameter) | null | pass_memberships |
| recovery | late_inspection_absorption | parameter | absorbed_share | 3 | no (one return_cases row) | returns | return_cases |
| recovery | member_fee_treatment | method | fee_after_member | 3 | **yes**: tier (loyalty_memberships) ∧ earning-posting count (loyalty_ledger) | loyalty | loyalty_memberships + loyalty_ledger |
| recovery | first_recovery_allowance | parameter | allowance | 3 | no (one aggregate) | returns | return_lines |
| cash-out | promotional_tender_exclusion | method | promo_exclusion | 3 | tiers are partitions of one capture aggregate (return_cases → order_payments); not a conjunction of conditions | null | return_cases + order_payments |
| cash-out | unsettled_return_hold | parameter | settlement_share | 3 | no | returns | return_cases |
| cash-out | refund_availability_by_standing | parameter | availability_days | 3 | conjunction tier ∧ enrolment, both on the one loyalty_memberships row | loyalty | loyalty_memberships |
| cash-out | delivery_claim_record_adjustment | parameter | claims_adjustment | 3 | no | **null, though it reads claims** (O-9) | claim_events |
| cash-out | lifted_lock_reserve | parameter | reserve_share | 3 | no | null | credit_instruments |
| replacement | theft_report_hold_share | parameter | hold_share | 3 | conjunction lock_reason ∧ registered-before-lock, all on the one credit_instruments row | null | credit_instruments |
| replacement | claim_record_hold_adjustment | parameter | claims_share_adjustment | 3 | no | claims | claim_events |
| replacement | regular_use_release | parameter | released_at_once | 3 | no | null | credit_transactions |
| replacement | member_hold_treatment | method | hold_final | 3 | conjunction tier ∧ enrolment, one loyalty_memberships row | loyalty | loyalty_memberships |
| consolidation | move_limit_by_standing | parameter | standing_limit | 3 | conjunction tier ∧ enrolment, one loyalty_memberships row | loyalty | loyalty_memberships |
| consolidation | card_age_limit_application | method | aged_limit | 3 | no | null | credit_instruments |
| consolidation | unlimited_membership_addon | parameter | plan_addon | 3 | conjunction status ∧ plan coverage, one pass_memberships row | null | pass_memberships |
| consolidation | recent_purchasing_addon | parameter | purchase_addon | 3 | no | loyalty | loyalty_ledger |
| consolidation | return_record_limit_change | parameter | return_change | 3 | no | returns | return_lines |

- Factor counts: recovery 5 (4 parameter, 1 method); cash-out 5 (4 parameter, 1 method); replacement 4 (3 parameter, 1 method); consolidation 5 (4 parameter, 1 method). All within 4–6, ≥2 parameter, ≥1 method.
- Bindings disjoint within each policy; every `decides` is an input binding, never `result`.
- Every ladder has 3 tiers, pairwise disjoint as stated, and every tier is stated in the rule (condition and value/method) and implemented in its binding.
- No two tiers of one ladder select the same value or method (values listed in `rule_compute_equivalence`).
- Every fall-through equals the policy's `baseline.rule` for that input (restocking uncapped; box share 1.0; nothing absorbed; fee kept; no allowance; no promotional exclusion; no settlement hold; 12 days; no claims adjustment; no lock reserve; share nothing; no claims share adjustment; nothing released; hold kept; limit 60.00; limit as set; nothing added ×2; no return change). `baseline.params` keys match (`[]`, `[avail_days_standard]`, `[]`, `[limit_standard_usd]`), and every baseline sentence is a verbatim sentence of its rule.
- Labels: the three "member treatment" method factors (`member_fee_treatment`, `member_hold_treatment`) change a multiplier *and* the rounding procedure (floor to dollar / ceil to cent / none); `card_age_limit_application` removes the cap, scales it, or applies it as set; `promotional_tender_exclusion` switches between a proportional formula, the whole value and nothing. None is a pure number substitution. Observation O-10: the two member-treatment factors carry their "method" content mainly in the rounding mode.
- Business realism: every condition divides the customers who reach the write (none restates the policy's scope) and every outcome is a treatment a retailer could publish. Observation O-11: an Unlimited (free-shipping) plan raising a stored-value consolidation move limit (`unlimited_membership_addon`) is the least natural condition of the charter; no consequence is demonstrable, so it is not a red.
- **Multi-source factors (every non-fall-through tier a conjunction over distinct records):** only `member_fee_treatment` (recovery) qualifies — loyalty tier from `loyalty_memberships` ∧ earning-posting count from `loyalty_ledger`. Every other compound ladder conjoins fields of a single row (`loyalty_memberships.variant_name` ∧ `.enrolled_date`; `credit_instruments.lock_reason` ∧ `.registered_date`/`.locked_date`; `pass_memberships.status` ∧ the plan's `covers_return_label`). Consequence: a task whose computations are replacement + consolidation has **no** multi-source factor (finding F-1).
- Cross-difficulty factors: recovery (loyalty ×2, returns ×2), cash-out (returns, loyalty; plus claims undeclared, O-9), replacement (claims, loyalty), consolidation (loyalty ×2, returns). Every pairing of policies has ≥1. Categories read: loyalty, returns, claims.
- Observation O-9: `delivery_claim_record_adjustment` reads `claim_events` (the delivery_claims difficulty) but declares `cross_difficulty: null`, while the identical construction in replacement declares `claims`; `promotional_tender_exclusion` reads `return_cases.order_id` (returns difficulty) to reach `order_payments` and declares `null`. Labelling only.

### findings

- **F-1 — SOURCE-FACTOR (structure) — bears on task 1.** Symptom: the factors of `credit_ext_stolen_card_replacement` and `credit_ext_card_balance_consolidation` include no multi-source factor. Root cause: each compound ladder of those two policies conjoins two fields of one row (see table). Evidence: `theft_report_hold_share.ladder[0].when` "lock reason reported_stolen or unauthorized_use AND the card was never registered to the holder on or before the lock date" (all `credit_instruments`), `member_hold_treatment` / `move_limit_by_standing` "Marlowe Rewards … member AND membership enrolled at least … months" (both `loyalty_memberships`), `unlimited_membership_addon` "status trial or active AND its plan covers return labels" (`pass_memberships` + its plan parameter); the remaining five factors are single-condition. Demonstrated consequence: the per-task count in `1.md` (`factor_weight`). Affected: `credit.extended.yaml` → `extended_policies[2].factors`, `extended_policies[3].factors`.
- O-1 … O-11 as recorded above (observations, no demonstrated consequence at charter level).

Tasks bearing on charter-global items: task 0 — O-1, O-3, O-8, O-9; task 1 — F-1, O-4, O-5 (not reached), O-6, O-7, O-11.

## closing_checklist

Written after both tasks' `source_gt_comparison` (reveal 2026-10-05T00:58Z–00:59Z). Nothing above this heading was edited after the reveal.

- Per-task files: `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; this file sits alongside them; revision 1 (no older revisions).
- Verdicts: task 0 **PASS** (all four relationships). Task 1 **RED — SOURCE-FACTOR** (F-1 / F-1-T1: no multi-source factor). Policy, chain and unique-solution relationships PASS on both.
- Coverage and scope: `charter_scope` task 0 = {recovery, cash-out}, task 1 = {replacement, consolidation}. These are pairwise disjoint over whole trees and jointly cover all four extended policies, matching the blind scope derivation in `policy_conflict_scan`. Task tools are closed over GT (four tools, each used by exactly one task). The uuid8s are independent (`action_binding_and_uuids`).
- Trees: each has 1 prerequisite problem, 1 value_input edge, an owner=user root and no cycle. The difficulty's graph is two disjoint edges with no cross-task references, so it is acyclic.
- Factors: every computation declares a self-sufficient baseline and 4–6 factors (≥2 parameter, ≥1 method). Every ladder has 3 distinct tiers, all stated in the rule. Every factor bears weight on its task's world, and every whole-baseline figure differs from gold (60.31 / 2.93 / 259.17 / 60.00). Cross-difficulty ≥1 per task. Multi-source ≥1 per task: **not met for task 1**.
- Instantiation-stage gates on the final form: not re-run by this audit. The gates are outside the auditor's read domain, and the difficulty does not pass, so it is not closed. The coordinator's snapshot (`GATES.txt`) stands as the entry record.

**Difficulty result: does not pass the source-layer audit (task 1 SOURCE-FACTOR RED).**

## revision_2

### charter_global_frozen (revision 2)

- auditor: the same independent auditor as revision 1. Freeze time 2026-10-05 (wall clock, after 04:28Z when the r2 views were built). This section was written before any round-2 task JSON was opened.
- inputs: r2 views `audits/_views/policy_task/gift_cards_and_store_credit/r2/{0,1}.view.json`, with `r2/HASHES.txt` and `r2/GATES.txt` (7 gates green, traceability deferred). Entry conditions are met.
- hashes recomputed by the auditor:
  - `credit.extended.yaml` = `ea43536fb8fb2040d3e6e69f8290d25198b5e680b644ce4072d4c37ecbf7ee1c` (revision 1: `1bb5ab22…0c47`, changed).
  - `task_tools.py` = `e0b1dde03c2df70b3d9f18e487ee053238e24c6a41a59089b1a07e94c4ada743` (revision 1: `40d756c5…981e`, changed).
  - `r2/0.view.json` = `b69fdde6…9d28f` and `r2/1.view.json` = `925c2775…c341`. Both are **identical** to revision 1, so both worlds and both personas are unchanged.
- Because both shared inputs changed, every charter-global section is re-derived below. Where the conclusion is unchanged, the reason is stated against the new text.
- contamination_disclosure (charter level): none for round-2 GT. The auditor knows round-1 GT from the revision-1 reveal; that knowledge carries no charter-global conclusion.
- The base section is still verbatim: `diff` of lines 1–1066 against `blueprint/products/credit.yaml` is empty.

### Changes located (revision 1 → revision 2)

| item | location | change |
| --- | --- | --- |
| F-1 | `credit_ext_stolen_card_replacement` rule, compute, `factors[2]` (`regular_use_release`), `cross_category`, `inputs` | Release at once now requires "the holder is the purchaser of record of the order line that bought the card" **and** the use count. There is a new binding `holder_bought_card` = `XCOUNT('orders','order_lines', order_line_id=F('source_reference'), event_type='orders_line_booked') >= 1`. An orders `cross_category` (existence) entry and an inputs line are added. |
| O-3 | `credit_ext_small_balance_cash_out` rule and `baseline.rule`; `compute_basis.refund_age_days` | Added "That refund's date is day zero, and the refunded value is payable on the day the count reaches the refund availability period." |
| O-5 | `credit_ext_card_balance_consolidation` rule, `compute_basis`, `factors[1].ladder[0]` | The age ≥12 m tier now reads "the move limit is the whole carried value in place of the standing limit". It no longer reads "no move limit applies and the whole carried value moves". |
| O-7 | consolidation `prerequisite[0].condition` | The clause "and that replacement card is active" is removed. |
| O-9 | cash-out `promotional_tender_exclusion.cross_difficulty` | `null` → `returns`. `delivery_claim_record_adjustment` is still `null`. |
| O-6 | `task_tools.py` `confirm_card_consolidation_106a95bf.source_instrument_id` | The phrase "or from the receipt of the action that issued it" is removed. The source is now read only "from the stored-value instrument lookup". |

Unchanged: the recovery policy in full, verified sentence by sentence against the revision-1 reading. Also unchanged: all four uuid8s, all four tool bodies (they still only `find` and write), and every other ladder, param and compute line.

### policy_conflict_scan (r2)
The conclusion is unchanged. The new orders read in replacement is a declared `cross_category` existence read. It overlaps no other policy's subject or terminal state. Scope derivation from the unchanged worlds: task 0 = {recovery, cash-out}, task 1 = {replacement, consolidation}. These are disjoint and complete.

### rule_compute_equivalence (r2)
- Replacement: the new rule sentence ("when the holder is the purchaser of record of the order line that bought the card and the card was spent on at least `regular_use_count` orders … ; when the holder is that purchaser of record and … ; otherwise, including for any card bought by someone else, nothing is released at once") maps to `holder_bought_card` and `released_at_once`. Each ladder tier is a rule sentence and a branch of the binding, and vice versa.
  - Observation O-R2-1: the rule's "holder is the purchaser of record" is implemented as a count of `orders_line_booked` rows with `order_line_id = source_reference` in the orders category. That equals "the holder bought it" only if the cross-category count is scoped to the holder. The evaluator is outside the read domain, so this cannot be confirmed. The rule text is authoritative. In task 1's world the line's `customer_id` is the holder, so the two readings agree.
- Cash-out: the new day-zero sentence states the counting convention that compute already used (`DAYS(last_refund, NOW) < period` → held). It has a `compute_basis` quotation (`refund_age_days`). The rule and compute now agree in words. **O-3 is closed.**
- Consolidation: the new age-tier sentence says the limit becomes the carried value. Add-ons and the return reduction are then applied "after its application for the card's age", and the result is capped at the carried value. This equals compute (`aged_limit = carried_value`, then `move_limit`, then `MN`). The two sentences no longer contradict each other. **O-5 is closed.** (The lines-vs-returns latent reading of `return_change` is unchanged and still not reached.)
- Recovery: unchanged (O-2 remains an observation).
- The replacement rule still carries "The investigation hold share is nothing …" beside the conditional shares (O-4 remains an observation).
Check 2: PASS.

### action_binding_and_uuids (r2)
- Four distinct `(target_tool, computes)` pairs. The uuid8s are unchanged (`f010c427`, `04a53640`, `8a64787f`, `106a95bf`).
- No docstring names another tool, carries an ordering word, or points at another action's output (**O-6 closed**). The source card is reachable through `find_credit_instruments`, because the replacement write creates a `credit_instruments` row.
- The tool bodies still validate nothing.
Check 3: PASS.

### prerequisite_graph (r2)
Same two edges and same fields.
- Edge B's `condition` now reads exactly at the sentence's strength ("… a credit_transferred_out row with transfer_reason replacement whose counterpart_instrument_id is the replacement card"). **O-7 closed.**
- Graph is acyclic; `form: state`; no `fallback_reason`; the gates `balance_now` and `carried_value` still exist in the blocked computes.
Check 7: PASS.

### prerequisite_sentences (r2)
Both `policy_source` sentences are verbatim unchanged and still in their own rules. The four-point test and the single-resolving-write derivations are the same as revision 1:
- Edge A: only the clawback writes a recovery entry.
- Edge B: only the replacement writes a transfer-out with reason replacement.

The new replacement sentence states no cross-problem order. It refers to the purchase order line as a record, not to another problem of this charter. Base "A locked instrument must be unlocked or replaced first" is unchanged (O-8 remains an observation). Check 6: PASS.

### override_declarations (r2)
- The `overwrite` blocks of all four policies are unchanged.
- The new replacement condition restricts how much of the protected balance is released at once. It reads the same purchaser-of-record relation that base `ownership_proof` uses ("the caller must be the purchaser of record of the order line that bought it") and changes no base sentence: base governs whether a replacement may be issued at all, and the extended rule governs its value, which is already declared replaced by `overwrite[0]`.
- The new cash-out sentence narrows no base clause.
- No undeclared override. O-1 (returns charter reconciliation) remains an observation.
Check 1: PASS.

### factor_ladders (r2)
Only the rows that changed from the revision-1 table are listed:

| policy | factor | effect | tiers | non-fall-through tiers compound over distinct records? | cross_difficulty | records |
| --- | --- | --- | --- | --- | --- | --- |
| replacement | regular_use_release | parameter | 3 | **yes**: purchaser of record (`order_lines` row of the card's source line) ∧ use count (`credit_transactions` redemption rows). Both non-fall-through tiers are conjunctions. | null (orders has no difficulty; correct) | order_lines + credit_transactions |
| cash-out | promotional_tender_exclusion | method | 3 | as revision 1 | returns (relabelled) | return_cases + order_payments |

- Counts per policy are unchanged: recovery 5 (4p/1m), cash-out 5 (4p/1m), replacement 4 (3p/1m), consolidation 5 (4p/1m).
- Bindings in replacement are still disjoint: `[card_uses, holder_bought_card, released_at_once]`.
- Tier outcomes are still distinct: 30.00 / 20.00 / 0.
- The new condition divides the customers who reach a replacement. Base `ownership_proof` also admits a registered holder who did not buy the card (for example a gift recipient), and Return Store Credit has no purchase line at all, so not every customer who reaches this write is the purchaser. It is a condition a retailer weighs for releasing part of a stolen card's value, because the purchaser holds proof of payment. The fall-through outcome (nothing released at once) is what the baseline states.
- **Multi-source per policy pairing: recovery + cash-out → `member_fee_treatment`; replacement + consolidation → `regular_use_release`. F-1 closed at charter level.**
- Cross-difficulty factors are present in every pairing.
- O-9 is partly closed: `delivery_claim_record_adjustment` (cash-out) still declares `cross_difficulty: null` although it reads `claim_events`. This is labelling only.
- O-10 and O-11 remain observations.

### findings (r2)
- F-1: **closed** (see `factor_ladders (r2)`). Demonstration on task 1's world is in `1.md` → `revision_2`.
- Closed: O-3, O-5, O-6, O-7. Partly closed: O-9. Still observations: O-1, O-2, O-4, O-8, O-9 (claims factor label), O-10, O-11.
- New: O-R2-1 (observation; the scope of the purchaser-of-record count cannot be verified from the read domain).
- No new red at charter level.

### closing_checklist (revision 2)

Written after both revision-2 reveals. The revision-2 charter-global sections above were frozen before them.

- Per-task files correspond one-to-one with the tasks. Revision 1 text is untouched, and revision 2 is appended under `## revision_2` in all three files.
- Verdicts: task 0 **PASS**, with no regression. Task 1 **PASS**: the round-1 red F-1 / F-1-T1 is closed.
- Coverage: the scopes are disjoint and cover all four extended policies (`charter_scope` confirmed). Task tools are closed over GT. The uuid8s are unchanged and independent.
- Trees: each has 1 prerequisite problem, 1 value_input edge, an owner=user root and no cycle. The difficulty graph is acyclic.
- Factors:
  - Every computation has a self-sufficient baseline and 4–6 factors (≥2 parameter, ≥1 method).
  - Every ladder has 3 distinct tiers stated in the rule, and every factor bears weight.
  - The whole-baseline figures (60.31 / 2.93 / 259.17 / 60.00) all differ from gold.
  - Each task has ≥1 multi-source factor (task 0 `member_fee_treatment`, task 1 `regular_use_release`) and ≥1 cross-difficulty factor.
- Reworker claims verified:
  - Closed as claimed: F-1/F-1-T1, O-3, O-5, O-6, O-7, O-T0-3.
  - Partly closed as claimed: O-9. The promotional exclusion is relabelled; the claims factor of cash-out is still `null`.
  - Left as observations, as claimed: O-1, O-2, O-4, O-8, O-10, O-11, O-T0-1, O-T0-2, O-T1-1.
- New: observation O-R2-1 only. No new red.
- Instantiation-stage gates on the final form: the coordinator's `r2/GATES.txt` shows all seven green (traceability deferred to the KB stage). The auditor did not re-run the gate scripts, which are outside its read domain.

**Difficulty result (revision 2): passes the source-layer audit. Policy self-consistency, problem tree, factor weight and unique solution are all PASS on both tasks.**
