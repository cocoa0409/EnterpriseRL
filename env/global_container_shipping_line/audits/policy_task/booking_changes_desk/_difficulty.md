# Policy-task audit — booking_changes_desk / charter-global

## charter_global_frozen

- Freeze time: 2026-09-13T04:40Z (written before any task's GT was revealed; contains nothing derived from a revealed GT).
- Auditor: independent erl-task-policy-audit agent (Claude Opus 5). It is not the authoring agent and took no answer from anyone.
- Frozen inputs (sha256):
  - `tasks/booking_changes_desk/booking.extended.yaml` = `bc019e2accb5b572e8983e7c1db98fa7d7253a681ab77c3b56864e3b56bb6708` (equals the coordinator's masking-time hash)
  - `tasks/booking_changes_desk/task_tools.py` = `0f320b37a48f7371df60ed5e44f3c96cf123e1347050f4847203beeaa2163fb4` (equals the masking-time hash)
  - `blueprint/products/booking.yaml` = `d7458d793c96c705fc1d7abbeeb1ea40d0668e693c1ae906be3669ddbd3b1a33`
  - `blueprint/share_tools.py` = `144e14049ea0784b5c08ab2b5c7890913acec41c57e6ad9fe2f874a56785e610`
  - `blueprint/db_schema.json` = `29583758d2faca0a3a5da9807e1aa85606a1e168b4d512600290a3151e09fe3c`
  - `blueprint/blueprint.yaml` = `1e0deff2026e1c89bab5360a15aee23111210f87387faf3242d87d662a37c419`
- Fields read: the blueprint (scenario, difficulty claim), `products/booking.yaml`, `db_schema.json`, `share_tools.py`, the full extended charter (base copy + `extended_policies` + `workflows`), and the full `task_tools.py`. The tasks were read only through the coordinator's masked views (`0.masked.json` sha256 `73445a4e…80f6`, `1.masked.json` sha256 `d84ef8d8…a7d7a0`, which keep only task_index / frozen_time / user_scenario / initial_state).
- Fields masked and unread at freeze: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`; any earlier audit; the scenario-level `worklog.md`; the scratchpad outside `masked/booking_changes_desk/source/`; other scenarios; sibling difficulties.
- Entry conditions (Step 0): the brief supplied the gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and check_cross_fire, all exit=0 on the current files; check_traceability deferred until the KB is published). It also supplied the masked views and their hashes, which HASHES.txt records. Complete. The gates were not run by this auditor.
- Base-copy check: the extended file's `category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies` each compare equal (parsed YAML) to `blueprint/products/booking.yaml`, and a textual diff of lines 1–1064 against the product file shows only a trailing blank line. **The base copy is verbatim.**
- DSL scope assumption: this auditor did not read the compute DSL evaluator, because it is outside the brief's read domain. `COUNT/SUM/LATEST('booking_charges', …)` with no key filter is taken as holding-scoped (`booking_id = HID`), because every rule sentence that these bindings quote says "on the booking" / "of the booking" / "on the same booking". Where a customer-scoped reading would change a value, the task files say so.

### policy_conflict_scan

The charter has six extended policies and one workflow:

| id | subject | charge_code / effect | target_tool | prerequisite |
|---|---|---|---|---|
| booking_ext_destination_change_fee | booking_amendment_fee_charged | pod_change_fee | charge_destination_change_fee_9814adc0 | [] |
| booking_ext_customer_roll_fee | booking_amendment_fee_charged | customer_roll_fee | charge_customer_roll_fee_5e1ab19d | [] |
| booking_ext_roll_fee_goodwill | booking_charge_waived | waiver of a customer_roll_fee row | waive_customer_roll_fee_66cbaf18 | customer_roll_fee (value_input), destination_change_fee (value_input) |
| booking_ext_carrier_roll_credit | booking_roll_compensation_credited | roll_compensation | credit_roll_compensation_f67bce09 | [] |
| booking_ext_late_si_record | booking_late_document_fee_charged | late_si_fee | record_late_si_fee_242ae989 | carrier_roll_credit (state_gate) |
| booking_ext_late_vgm_record | booking_late_document_fee_charged | late_vgm_fee | record_late_vgm_fee_5d1f74dd | late_si_record (value_input) |
| booking_wf_rolled_booking_late_documents | workflow | credit, user SI, late SI, user VGM, late VGM | 5 steps | [] |

Overlapping subjects and how they are separated:
- `booking_amendment_fee_charged` has two extended owners, which are separated by charge_code (`pod_change_fee` vs `customer_roll_fee`), by tool, and by history filter (`amendment_type=pod_change` rows vs `roll_initiator=customer` rows). No subject/trigger overlap. Each overlaps its base clause (booking_amendment pod-change sentence; booking_rollover customer-roll sentence), and both base clauses are named in `overwrite` (see override_declarations).
- `booking_late_document_fee_charged` has two extended owners, separated by charge_code and by receipt field (`si_submitted_at` vs `vgm_submitted_at`). They share one counter, `prior_late_on_booking = COUNT(booking_late_document_fee_charged)` on the booking, so the order in which the two are written changes both amounts. booking_ext_late_vgm_record fixes that order only "for documents received before it". Which document is received first is not decided by any rule sentence. The workflow step list decides it (bearing: task 1, see its file).
- `booking_charge_waived`: the extended policy covers only customer_roll_fee rows. The base booking_goodwill_waiver (all waivable fees) and the base booking_cancellation (premium_refund) stay in force for the other rows. The extended policy adds gates that base does not state (see override_declarations, finding F-D2).
- `booking_roll_compensation_credited` overlaps base booking_rollover (see F-D3).
- Time anchors. The two state_due fee policies charge "when the booking is next handled, as long as the booking still accepts amendment charges under booking_amendment", which inherits base `amend_live_booking` and `amend_before_lead_time`, whose `applies_to` includes booking_amendment_fee_charged. The late-document policies inherit base `si_inside_grace`, `late_fee_on_live_booking` and the VGM grace sentence. The goodwill policy uses the base window (event_date + waiver_request_window_days, calendar dates). No two anchors conflict.
- Cross-category reads: `dg.container_count/status` (rejected acceptance subtracted, approved acceptance opens the late-document allowance) and `contract.shortfall_balance_usd`. Both are read-only and are reachable through `find_dg_acceptances` / `find_service_contracts`. The rejected-acceptance subtraction appears identically in four policies. It never collides with base booking_cancellation's `line_rejection_free_cancellation` because no extended policy touches cancellation.
- Cross-policy coupling: booking_ext_late_si_record states generally that "Entries owed on a booking are booked in the order of the events that gave rise to them: before a late submission is recorded, any charge or credit the booking already owes from an earlier event, such as compensation for an earlier carrier roll, must already be on the account". Read literally, the sentence also makes owed pod_change_fee / customer_roll_fee rows prerequisites of a late SI record, and it could order charges from different events against each other. The graph declares only the carrier-credit edge (F-D4, F-D8).
- Scope exclusivity (from the charter and the prerequisite graph only): the graph has exactly two weakly connected components, {roll_fee_goodwill, customer_roll_fee, destination_change_fee} and {late_vgm_record, late_si_record, carrier_roll_credit} + the single workflow, whose steps use exactly the three tools of the second component. With M=2, a disjoint and complete split is possible only as one component per task. The masked worlds match that split: task 0's world is a customer-rolled, pod-changed Contract Booking with no carrier roll and no document receipt; task 1's world is a carrier-rolled Guaranteed Loading booking with no pod change and no customer roll. Whether the declared `charter_scope` matches is checked only after the reveal, in the closing checklist.

### rule_compute_equivalence

Check 2, policy by policy. "✓" means the binding quotes a rule sentence verbatim and implements it with no added basis, and that the rule sentence it quotes is implemented.

booking_ext_destination_change_fee
- per_container_fee = P(pod_change_fee_per_container_usd) ← "The fee is pod_change_fee_per_container_usd times the chargeable containers" ✓
- pod_change_allowed and `0 if not pod_change_allowed` ← "On a tier whose pod_change_allowed is false … has no chargeable containers and bears no fee." ✓
- changes_logged / changes_charged / changes_owing ← the two count sentences + "When no change is still owing a fee, nothing is charged." ✓
- rejected_dg_containers = CFIELD(dg, container_count, booking_id=HID, status=rejected) or 0 ← "containers covered by the booking's dangerous-goods acceptance that the line has rejected … are left out" ✓ (singular acceptance assumed; see F-D6)
- chargeable_containers = MX(container_count − rejected, 0) ← "never below zero; when the booking has no rejected acceptance nothing is subtracted" ✓
- result = RND(fee × chargeable, 2) if changes_owing > 0 ← "one fee row per change … rounded to two decimal places only at the end" ✓
- Rule sentences with no compute counterpart: (a) the eligibility "as long as the booking still accepts amendment charges under booking_amendment", which is delegated to the base eligibility entries; (b) the per-row `vessel_voyage` ("the sailing shown on the pod_change amendment entry it charges"), a non-computed verbatim argument that the rule fixes. Neither is an empty promise.

booking_ext_customer_roll_fee
- customer_rolls, rolls_owing_fee = 0 if customer_rolls ≤ free else customer_rolls − free, fees_charged, rolls_still_owing ← the four quoted sentences ✓ (same count basis as base "counted including the roll being handled")
- rejected/chargeable ✓ as above; result ✓ ("rounded to two decimal places only at the end")
- vessel_voyage (non-computed) ← "the sailing the charged roll moved the booking off, exactly as shown on that roll's booking_roll_recorded row; the rolls still owing a fee are the latest customer rolls of the booking" — fixed by the rule.
- The base `customer_roll_cap` (max_customer_rolls_per_booking) is inherited as eligibility and is not in compute. Correct, since it gates the roll, not the fee.

booking_ext_roll_fee_goodwill
- authority, window_days, within_authority (`fee_amount > 0 and ≤ authority`), in_window (DAYS(fee_date, NOW) ≤ window_days) ← quoted ✓
- roll_fee_rows, fee_amount / fee_date = LATEST(…, charge_code=customer_roll_fee) ← "The fee row concerned is the latest customer_roll_fee row of the booking by event_date" ✓
- pod_changes_owing, customer_rolls, roll_fees_owing, account_complete ← "Goodwill is decided only on a complete change account … no pod_change amendment … left without its pod_change_fee row and no customer roll beyond free_customer_rolls_per_booking … left without its customer_roll_fee row" ✓. pod_changes_owing does not carry destination_change_fee's `pod_change_allowed=false` / zero-chargeable branch (F-D5).
- contract_shortfall / contract_clear ← quoted ✓; result = RND(fee_amount, 2) if all four hold ✓
- A rule sentence with no compute counterpart: "The quota and once-per-row conditions of booking_goodwill_waiver continue to decide whether a waiver may be written at all." This is delegated to base eligibility `within_quota` / `waive_once`. Not an empty promise, but `result` can be > 0 where the base quota refuses. The task file checks the quota separately.

booking_ext_carrier_roll_credit
- carrier_rolls, compensations_credited, rolls_owing, roll_position = compensations_credited + 1, credited_so_far, headroom = MX(cap − so_far, 0), uncapped_credit (0 when per-container credit ≤ 0), chargeable, result = RND(MN(uncapped, headroom), 2) if rolls_owing > 0 and roll_position ≤ max_rolls ← each quoted ✓
- reference_event_id (non-computed) ← "credited in the order they were recorded, one credit row per roll, each referencing the roll row it compensates" — the earliest uncompensated carrier roll row.

booking_ext_late_si_record
- received_late = F(si_submitted_at) > F(si_cutoff) ← quoted ✓. Both fields share the `YYYY-MM-DDTHH:MM` format, so the string comparison is chronological. An empty si_submitted_at compares false, which gives "book nothing".
- prior_late_on_booking = COUNT(booking_late_document_fee_charged) ← "counted on the booking itself" ✓; approved_dg_containers / allowance_open / within_allowance ✓; result ✓
- The in-grace condition is base eligibility `si_inside_grace` and is not in compute. The ordering sentence ("before a late submission is recorded, any charge or credit … must already be on the account") is a gate carried by the prerequisite graph, not by compute.

booking_ext_late_vgm_record
- Same as the SI policy, plus rejected/chargeable containers and `result = RND(per_container_fee × chargeable, 2)` ✓. "including a late shipping-instruction row recorded before it" ✓ — the same unfiltered COUNT.

Result: no compute binding invents a basis. The only rule conditions compute does not carry are base eligibility gates (lead time, grace, quota, once-per-row), which the rules delegate explicitly. **Check 2: pass.** Observations F-D5 and F-D6 cover edge domains that no task instantiates.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: (charge_destination_change_fee_9814adc0, fee_usd), (charge_customer_roll_fee_5e1ab19d, fee_usd), (waive_customer_roll_fee_66cbaf18, waiver_usd), (credit_roll_compensation_f67bce09, compensation_usd), (record_late_si_fee_242ae989, fee_usd), (record_late_vgm_fee_5d1f74dd, fee_usd). Each tool is claimed by exactly one policy, and the two user tools (submit_shipping_instructions_a84d5d18, submit_vgm_declaration_120f73ac) are claimed only by workflow steps. ✓
- uuid8s: 9814adc0, 5e1ab19d, 66cbaf18, f67bce09, a84d5d18, 242ae989, 120f73ac, 5d1f74dd. They are pairwise distinct, share no common prefix or suffix, are not sequential or adjacent, and none is another with a changed tail. Nothing suggests batch derivation. ✓
- Tool bodies (task_tools.py lines 38–51, 80–94, 123–135, 164–177, 199–202, 229–242, 264–267, 294–307). Each tool does one `ctx.create` and/or `ctx.update` with the passed amount rounded by Python `round` (half-to-even, as the docstrings say). None checks status, time, duplicates, prerequisites or eligibility, and none computes an amount. The tool layer judges no prerequisite. ✓
- Docstrings add no confirmation, review or wait. The late SI and late VGM tools take the row's `vessel_voyage` from the booking's current allocation, which matches "The row carries the booking's allocated sailing". The two charge tools take `vessel_voyage` as a verbatim argument, which the rules fix.
- Observation (F-D7): the four charge/credit tools never write `container_count` or `equipment_type` on the new row, although the charter events give those fields ("container_count: containers the fee is computed on"). This changes no scored amount and no reading. Recorded only.
- **Check 3: pass.**

### prerequisite_graph

Check 7.
- Every policy and the workflow has `prerequisite` (dest [], roll_fee [], carrier [], workflow [], goodwill 2 edges, late_si 1, late_vgm 1). Every `problem` names an extended policy id in this file, none names a base policy, and none is self-referential. ✓
- Edges: E1 goodwill→customer_roll_fee (value_input, gate `fee_amount`); E2 goodwill→destination_change_fee (value_input, gate `pod_changes_owing`); E3 late_si→carrier_roll_credit (state_gate, gate `booking_charges.reference_event_id`); E4 late_vgm→late_si (value_input, gate `prior_late_on_booking`). No cycle. The graph is two disjoint trees. ✓
- `policy_source` located verbatim in the cited rule: E1 "A goodwill waiver is decided only against a fee row already on the booking's account" (goodwill rule, sentence 2) ✓. E2 "before a customer roll fee is waived, every change-of-destination fee and customer roll fee the booking owes must already be charged" ✓. E3 "before a late submission is recorded, any charge or credit the booking already owes from an earlier event, such as compensation for an earlier carrier roll, must already be on the account" ✓. E4 "a verified gross mass is recorded only after every late shipping-instruction row for documents received before it is on the booking" ✓.
- `resolved_by` is the target_tool of the problem it points at, in each case (5e1ab19d, 9814adc0, f67bce09, 242ae989), and each write changes the named binding or field. ✓
- `kind` vs `gate`: E1 `fee_amount` and E4 `prior_late_on_booking` are compute bindings whose value flows into the result (genuine value inputs). E2 `pod_changes_owing` is a compute binding, but it feeds only the boolean `account_complete`, so it acts as a 0/1 gate on the result and is labelled value_input (observation). E3 `booking_charges.reference_event_id` is a ledger field, not a named eligibility of the late-SI policy (extended policies carry no `eligibility` list). The gate the rule sentence describes is real (observation).
- `condition` vs cited sentence: E1, E2, E4 agree. E3's condition "No compensation owed for an earlier carrier roll of the booking remains uncredited" narrows the cited sentence's "any charge or credit the booking already owes from an earlier event" to one example (F-D4).
- **`effect` texts written from the authoring world — F-D1, SOURCE-POLICY RED (charter-global).**

### override_declarations

Check 1, sentence by sentence against every `base_policy_refs` entry. The consequence for a task is left to that task's file.

booking_ext_destination_change_fee (refs booking_amendment, booking_rollover)
- booking_amendment s1 (what may be amended), s2 (status confirmed/equipment_released), s3–s4 (lead time and counting): followed, and inherited through "as long as the booking still accepts amendment charges under booking_amendment".
- s5–s6 (every amendment logged; booking_msr_amendments): followed ("The change still counts toward the free amendment allowance").
- s7 "it is charged pod_change_fee_per_container_usd times the booking's container_count whatever the free allowance": handled differently (container_count → chargeable containers, final rounding) and **declared** in `overwrite` ✓.
- s8 (other amendments / amendment_fee), s9 (quantity increase), s10 (reduction), s11 (cargo category), s12 (change of sailing = customer roll): not touched, inherited.
- Timing: base gives no charging moment. Extended adds "charged when the booking is next handled", which contradicts no base sentence.
- booking_rollover: no sentence governs pod-change fees. Nothing to declare.

booking_ext_customer_roll_fee (refs booking_amendment, booking_rollover)
- booking_rollover: roll definition, carrier/customer causes, logging and vessel replacement: followed. Compensation sentences: untouched.
- "A customer roll is accepted only while … fewer than max_customer_rolls_per_booking. Beyond that the customer must cancel": inherited, not weakened.
- "A customer roll is free while booking_msr_customer_rolls, counted including the roll being handled, does not exceed free_customer_rolls_per_booking": followed (`rolls_owing_fee` uses the same inclusive count).
- "… and is otherwise charged customer_roll_fee_per_container_usd times the container_count as a booking_amendment_fee_charged row with charge_code customer_roll_fee and amendment_type customer_requested_vessel_change": the amount is handled differently and **declared** ✓. The row shape is followed. The added final rounding cannot change a 2-dp per-container fee times an integer.
- "Carrier rolls never bear a fee": followed.
- booking_amendment s12 (change of sailing is a customer roll): followed.

booking_ext_roll_fee_goodwill (refs booking_cancellation, booking_goodwill_waiver, booking_rollover, booking_amendment)
- booking_goodwill_waiver s1 (desk may waive a single fee row at the verified customer's request), s2 (waivable codes incl. customer_roll_fee), s3 (whole row, charge_code waiver, full amount_usd), s4 (amount ≤ authority), s5–s6 (quota across all bookings against the tier of the fee's booking), s7–s8 (request window, calendar dates, last day inside), s9 (once per row): all followed. s5, s6 and s9 are re-affirmed verbatim ("The quota and once-per-row conditions … continue to decide").
- s10 "A fee that fails any of these conditions stays payable, and the desk has no authority to reduce it.": **declared**, with an equivalent sentence.
- Handled differently and **not named** in `overwrite`: the extended policy adds four conditions that no base sentence states. They are a complete change account, contract `shortfall_balance_usd` exactly 0.00, `amount_usd` above 0.00, and "the fee row concerned is the latest customer_roll_fee row". Each enters `result` as a 0/1 multiplier on the amount that base s3 fixes. Base formula `when_not: amount_usd > goodwill_waiver_authority_usd or booking_msr_goodwill_waivers_365d >= goodwill_waivers_per_365d` lists only two blockers. → F-D2.
- booking_cancellation (premium refunds are not goodwill): followed. booking_rollover / booking_amendment: used only to define owed fees. Nothing contradicted.

booking_ext_carrier_roll_credit (ref booking_rollover)
- "Compensation is credited only for a roll whose recorded roll_initiator is carrier": followed.
- "the booking is credited roll_compensation_per_container_usd times its container_count": **declared** ✓.
- "… when booking_msr_carrier_rolls, counted including the roll being compensated, does not exceed max_compensated_carrier_rolls": handled on a different count basis ("position one above the number of compensation rows already on the booking") and **not named** in `overwrite` (anonymous intermediate factor). → F-D3.
- Cap sentence (credit reduced so that total + credit ≤ cap), zero-tier sentence, once-per-roll, "Carrier rolls never bear a fee": followed.

booking_ext_late_si_record (ref booking_late_documentation)
- Cut-off sentence, SI grace acceptance, grace counting, "after cut-off but inside grace book one late_si_fee row … per booking", the after-grace roll, "A late documentation fee may be booked only while … confirmed, equipment_released or gated_in", "Documents received on time book nothing": followed.
- "the row is recorded at 0.00 while booking_msr_late_doc_fees_365d for the customer is below late_doc_fee_free_occurrences_365d, and at the full fee otherwise": handled differently (booking-scoped, no 365-day window, DG allowance gate) and **declared** ✓. The `replaced_by` includes "and the free allowance is open".
- The added ordering gate contradicts no base sentence, since base is silent on order.

booking_ext_late_vgm_record (ref booking_late_documentation)
- VGM grace sentence, "no container is loaded without a verified gross mass …", the live-status sentence: followed.
- The free-allowance sentence: **declared** ✓ (booking-scoped, counts an earlier SI row).
- "books one late_vgm_fee row of late_vgm_fee_per_container_usd times the booking's container_count": **declared** ✓ (chargeable containers).

Summary: every amount-changing clause is declared. There are two undeclared differences, F-D2 and F-D3. For each, the task file decides whether it hands the task a second answer.

### findings

**F-D1 — SOURCE-POLICY RED (charter-global; check 7). Bears on task 0 (E1, E2) and task 1 (E4).**
- Symptom: three prerequisite `effect` texts state outcomes that hold only in the authoring world. They sit in general text that is rendered with the policy.
- Root cause: `effect` was written as a narration of the author's task world, not as the general effect of the resolving write.
- Evidence (booking.extended.yaml):
  - E4 (booking_ext_late_vgm_record.prerequisite[0].effect): "prior_late_on_booking rises from 0 to 1, the free allowance is used up, and the verified gross mass row is recorded at the full fee instead of 0.00."
  - E2 (booking_ext_roll_fee_goodwill.prerequisite[1].effect): "pod_changes_owing falls to 0, account_complete becomes true, and the waiver result moves from 0 to the fee row's amount_usd."
  - E1 (…prerequisite[0].effect): "fee_amount changes from 0 (no customer_roll_fee row on the booking) to …".
- Demonstrated consequence (two passages, same situation, different conclusions):
  - E4. Take an AHL Premium Express booking (late_doc_fee_free_occurrences_365d: 3), cargo general, no earlier late rows on the booking, SI and VGM both received late inside grace, SI row recorded first. E4's effect says the VGM row "is recorded at the full fee instead of 0.00". booking_ext_late_vgm_record's rule ("recorded at 0.00 while the late submissions already recorded on the same booking … are fewer than the tier's late_doc_fee_free_occurrences_365d") and compute (`prior_late_on_booking` = 1 < 3 → `within_allowance` → result 0) give 0.00. AHL Contract Priority (free 2) gives the same contradiction.
  - E2. Take a Contract Booking whose contract has `shortfall_balance_usd` 1,000.00. E2's effect says the result "moves from 0 to the fee row's amount_usd". Compute `contract_clear` = False, so the result stays 0.
- Affected artifact: `booking.extended.yaml`, the `prerequisite[*].effect` of booking_ext_late_vgm_record and booking_ext_roll_fee_goodwill. The task files show whether the contradiction reaches their own worlds.
- Relation to previous revisions: first audit revision.

**F-D2 — observation (check 1, undeclared narrowing; 0/1-multiplier form). Bears on task 0.**
- Symptom: booking_ext_roll_fee_goodwill adds the gates `account_complete`, `contract_clear`, `fee_amount > 0` and "latest row", none of which is named in `overwrite`.
- Why this is not recorded as RED at charter level: base s1 grants a permission ("The desk may waive …"), and no base sentence states that meeting its conditions obliges a waiver. So the added gates narrow the permission without contradicting a base conclusion, and conditions from both texts simply accumulate into one merged reading. The strongest counter-signal is the base formula `when_not`, which lists exactly two blockers. In a world where only the added gates fail (for example contract shortfall > 0), a reader who takes `when_not` as exhaustive writes the full-amount waiver while the extended policy writes none. Task 0's file checks whether its world reaches that case.
- Affected artifact: booking.extended.yaml booking_ext_roll_fee_goodwill `overwrite` / `rule`.

**F-D3 — observation (check 1, anonymous intermediate factor). Bears on task 1.**
- Symptom: base counts eligibility for roll compensation as "booking_msr_carrier_rolls, counted including the roll being compensated" (measure window "Life of the booking, including the roll being handled"). Extended counts "the position one above the number of compensation rows already on the booking". The change is not named in `overwrite`.
- When the two differ: they agree whenever every earlier carrier roll was credited in order. They differ when uncompensated carrier rolls are backlogged and base's measure is evaluated at handling time. Example: Premium Express, 3 carrier rolls recorded, none credited, max 2. Base count 3 > 2 gives 0 for the first roll. Extended position 1 ≤ 2 gives 350 × containers. They also differ when a cap-exhausted roll wrote no row.
- Affected artifact: booking.extended.yaml booking_ext_carrier_roll_credit `overwrite` / `rule` / compute `roll_position`.

**F-D4 — observation (check 7, graph under-declares what its own rule sentence imposes). Bears on task 1 (and on scope exclusivity).**
- Symptom: the sentence behind E3 makes every charge or credit a booking owes from an earlier event a gate on recording a late submission. That includes an owed pod_change_fee (booking_ext_destination_change_fee) or an owed customer_roll_fee (booking_ext_customer_roll_fee). The graph declares only the carrier-credit edge, and E3's `condition` narrows the sentence to that one example.
- Consequence: only in a world where a pod change or customer roll fee is owed at the moment a late SI is recorded. Task 1's file checks its world. If such a world were instantiated, the undeclared edges would join the two components across the task split.

**F-D5 — observation (check 2 edge domain). No task instantiates it.** booking_ext_roll_fee_goodwill.pod_changes_owing counts every pod_change amendment. booking_ext_destination_change_fee charges nothing (result 0, and the tool accepts only a positive amount) when `pod_change_allowed` is false or all containers belong to a rejected acceptance. In such a world, the goodwill account could never become complete. The customer-roll side has the same shape (zero chargeable containers).

**F-D6 — observation (check 2 edge domain).** `CFIELD('dg', 'container_count', booking_id=HID, status=…)` reads one acceptance's field. The rules say "that rejected dangerous-goods acceptance" (singular) and "at least one of its dangerous-goods acceptances is approved". A booking with two rejected acceptances or two approved acceptances has no single defined value. Both task worlds have exactly one rejected and one approved acceptance on the booking concerned.

**F-D7 — observation (tool contract vs event fields).** The charge and credit tools write no `container_count` / `equipment_type` on new ledger rows (see action_binding_and_uuids).

**F-D8 — observation (scope of a general sentence). Bears on task 0.** booking_ext_late_si_record's rule says "Entries owed on a booking are booked in the order of the events that gave rise to them". The sentence is general, and the colon that follows applies it to late submissions. A reader who takes it as general gets an order between two owed charges from different events (for example, a pod change logged before a customer roll). Task 0's file checks whether that order changes anything.

Per-task checks 4, 5 and 6 (handling time, zero-wait, workflow shape) are in the task files. The workflow is examined in the file of the task whose world it fits (task 1).

## closing_checklist

Written 2026-09-13T04:52Z, after both tasks' derivations were frozen (hashed 04:46:30Z) and both GTs revealed (04:46:30Z, 04:47:36Z). This is the only section of this file written after a reveal. The charter-global section above is unchanged since that hash, except that it had three pre-reveal label corrections at about 04:44Z (F-D5/F-D6/F-D7 cross-references).

**The difficulty does not close.** Not every comparison section carries PASS. Per-task verdicts:

| Task | Policy self-consistency | Problem tree | Unique solution | Verdict line |
|---|---|---|---|---|
| 0 | SOURCE-POLICY RED (F-D1 demonstrated in its own world, T0-2) | SOURCE-CHAIN RED (false closure assertion E2 `flips_to_true_by`, T0-1) | PASS | SOURCE-POLICY RED + SOURCE-CHAIN RED |
| 1 | SOURCE-POLICY RED (workflow order_rationale contradicts the late-VGM rule, T1-2) | SOURCE-CHAIN RED (persona names the late-SI prerequisite, T1-1) | PASS | SOURCE-POLICY RED + SOURCE-CHAIN RED |

Neither task's scored solution (values, objects, owners, final-state hash) differs from the independent derivation. All four REDs concern the proof or the problem-tree construction, not a second or missing answer.

Step 4 checklist:
- Per-task files correspond one-to-one: `0.md` ↔ tasks/0.json and `1.md` ↔ tasks/1.json, with `_difficulty.md` alongside. First revision, so there are no older revisions to trace. Every comparison section has a verdict, but not all are PASS (above). ✗
- The extended policies are fully covered and pairwise disjoint. Task 0 charter_scope = {destination_change_fee, customer_roll_fee, roll_fee_goodwill}, workflows []. Task 1 = {carrier_roll_credit, late_si_record, late_vgm_record} + booking_wf_rolled_booking_late_documents. The union is all 6 extended policies, and the intersection is empty. Each scope spans its whole declared tree (root + prerequisites), which matches the two graph components found pre-reveal. ✓
- Exactly one workflow, claimed only by task 1. ✓
- Task tools and GT are closed. Task 0 uses 3 tools and task 1 uses 5, disjoint, and together they are all 8 in task_tools.py. Every tool in GT is in its task's charter_scope, and every uuid8 is independently generated and frozen (see `### action_binding_and_uuids`). ✓
- Each task's problem tree has at least 2 prerequisites, at least 1 value_input edge, and no cycle. Formally yes for both (task 0: E1 value_input + E2; task 1: E4 value_input + E3). Substantively, task 1 fails, because the E4 prerequisite is customer-named (T1-1). ✗ for task 1.
- The prerequisite edges of the whole difficulty form a DAG: {goodwill→roll_fee, goodwill→dest_fee, late_vgm→late_si, late_si→carrier_credit}, with no cross-task reference. The edges late_si→dest_fee/roll_fee implied by F-D4's sentence (undeclared) would also create no cycle. ✓
- Instantiation-stage gates on the final form: this auditor did not re-run them (Step 0 / brief: cite, do not run). The artifacts are byte-identical to those the coordinator's snapshot ran on. At close, `booking.extended.yaml` = bc019e2a…6708 and `task_tools.py` = 0f320b37…63fb4, both equal to the masking-time hashes. The current hashes of `tasks/0.json` = 5939b610…aedb and `tasks/1.json` = fec931f9…d6d0 are recorded for the next round. The snapshot (all seven gates exit 0; check_traceability deferred) therefore stands for the final form.

Charter-global findings and their reach, for the next round:
- F-D1 (SOURCE-POLICY RED): its E2 part is demonstrated in task 0's world (T0-2). Its E4 part is true in task 1's world, so it does not reach task 1.
- F-D2, F-D3, F-D4, F-D8: observations. None changes a scored value in either world.
- F-D5, F-D6, F-D7: edge-domain or tool-field observations that neither world instantiates.

## revision_2

### charter_global_frozen (revision_2)

- Freeze: written 2026-09-13 from 05:05Z, before either round-2 task view or round-2 GT was opened. It contains nothing derived from a revealed GT. Round-1 text above is untouched.
- Auditor: the same independent erl-task-policy-audit agent (Claude Opus 5). No answer supplied by the reworker is used as evidence. The reworker's item-id claims are verified one by one below.
- Why this section is re-derived in full: both shared inputs changed.
  - `booking.extended.yaml`: round 1 `bc019e2a…6708` → round 2 **`7838ceb01aeee13f73aa4584e026238637a75855eb5eedbe49d66e95991e224e`**.
  - `task_tools.py`: round 1 `0f320b37…63fb4` → round 2 **`29d2830425ce29e7133453f9e54ff14ef4aa47ba78aec19eb0766c106b38609a`**.
  - Both equal the coordinator's round-2 source hashes.
  - Unchanged since round 1: `products/booking.yaml` d7458d79…1a33, `share_tools.py` 144e1404…e610, `db_schema.json` 29583758…fe3c, `blueprint.yaml` 1e0deff2…c419.
- Entry conditions: the round-2 gate snapshot (all seven instantiation gates exit 0; check_traceability deferred) and the rebuilt masked views (`source_r2/0.masked.json` 782ded2f…2f71, `source_r2/1.masked.json` fd8c0355…2b42, the same four kept keys per HASHES.txt) were supplied. Complete. The auditor did not run the gates.
- Base copy: parsed-YAML equality of all ten base keys against `products/booking.yaml` holds again. **Verbatim.**
- DSL scope assumption: the same as round 1.

### policy_conflict_scan (revision_2)

- Inventory: the six extended policy ids are unchanged. The workflow keeps its id `booking_wf_rolled_booking_late_documents` but is rebuilt to four steps: credit (agent) → record late SI (agent) → submit VGM (user) → record late VGM (agent). The user tool `submit_shipping_instructions_a84d5d18` is **removed** from `task_tools.py` and from the workflow, so seven task tools remain.
- `booking_amendment_fee_charged` (pod_change_fee vs customer_roll_fee) and `booking_late_document_fee_charged` (late_si_fee vs late_vgm_fee) are separated as in round 1.
- **The shared late-row counter is now ordered by a rule sentence.** booking_ext_late_si_record adds: "A shipping-instruction receipt that is already on the booking without its late row is recorded when the booking is next handled and before any further document is taken in for the booking, so that the ledger records late submissions in the order the documents arrived." booking_ext_late_vgm_record keeps "Late submissions are recorded in the order the documents were received". The rebuilt workflow's scenario puts the SI receipt in the world before the consultation, so receipt order is a recorded fact (si_submitted_at < vgm_submitted_at) and no longer a choice made by step order. Round-1 W4 / T1-3 was about which document is received first when both arrive in the call; that mechanism no longer exists on this surface.
- **Cross-policy coupling.** booking_ext_late_si_record no longer carries the general sentence "Entries owed on a booking are booked in the order of the events that gave rise to them … any charge or credit the booking already owes from an earlier event". Its replacement is scoped: "Roll compensation comes first on a booking the line has rolled: before a late submission is recorded on such a booking, the compensation owed for the earlier carrier roll must already be credited under booking_ext_carrier_roll_credit." The coupling to owed pod-change or customer-roll fees (round-1 F-D4) and the general event-order reading (F-D8) are gone.
- `booking_charge_waived`: the goodwill additions are now declared (see override_declarations). A new residue concerns the scope of the superseded permission sentence (R2-O2).
- Time anchors and cross-category reads are as in round 1. booking_ext_roll_fee_goodwill now also reads `dg.container_count/status`, to decide whether an owed change has any chargeable container.
- Scope exclusivity, from the graph only: still two weakly connected components, {roll_fee_goodwill, customer_roll_fee, destination_change_fee} and {late_vgm_record, late_si_record, carrier_roll_credit} + the workflow, whose steps use exactly the three agent tools of the second component plus the one remaining user tool. With M = 2 the only disjoint and complete split is one component per task. It is checked against charter_scope only after the reveal.

### rule_compute_equivalence (revision_2)

Only changed bindings and sentences are listed. Every unchanged binding was re-read against its unchanged sentence and still holds.

- destination_change_fee / customer_roll_fee / carrier_roll_credit / late_vgm_record: each adds "A booking on which more than one dangerous-goods acceptance has been rejected falls outside this policy's rules, because its chargeable containers are not defined by them." This closes the undefined domain of `CFIELD(… status='rejected')` by declaring it out of scope. No compute change was needed. ✓
- roll_fee_goodwill:
  - `rejected_dg_containers` / `chargeable_containers` ← "leaves no chargeable container once the containers of the booking's rejected dangerous-goods acceptance are left out" ✓
  - `pod_changes_owing = (logged − charged) if (P('pod_change_allowed') and chargeable_containers > 0) else 0` ← "A change that owes no fee under its own policy, because the tier does not accept a change of port of discharge, … or leaves no chargeable container …, does not leave the account incomplete" ✓. This agrees with destination_change_fee's `chargeable_containers = 0 if not pod_change_allowed …` and `result … if changes_owing > 0`.
  - `roll_fees_owing = (…) if (P('customer_roll_fee_per_container_usd') > 0 and chargeable_containers > 0) else 0` ← "charges no customer roll fee, or leaves no chargeable container" ✓. Every tier's customer_roll_fee_per_container_usd is > 0, so the first factor never fires. Not a defect.
  - The rule's "more than one rejected acceptance" exclusion is not restated here. The goodwill policy reads `chargeable_containers` through the same CFIELD, so on such a booking it inherits the fee policies' exclusion only implicitly (observation R2-O4).
- late_si_record: the two new ordering sentences are procedure gates. The prerequisite graph and the workflow carry them, and compute does not, which is correct because they gate order and not amount. The amount bindings are unchanged ✓.
- carrier_roll_credit: compute is unchanged. The count-basis sentence is now declared (below).
- **Check 2: pass.**

### action_binding_and_uuids (revision_2)

- `(target_tool, computes)` pairs are unchanged for the six policies. User tool `submit_vgm_declaration_120f73ac` is claimed only by workflow step 2. The removed `submit_shipping_instructions_a84d5d18` is referenced nowhere in the charter (grep of the round-2 yaml: no occurrence). ✓
- uuid8s 9814adc0, 5e1ab19d, 66cbaf18, f67bce09, 242ae989, 120f73ac, 5d1f74dd are unchanged, distinct, and not batch-derived. ✓
- Tool bodies (task_tools.py lines 40–54, 85–100, 131–144, 175–189, 218–232, 254–257, 286–300): one create/update each. They now also write `equipment_type` from the booking. None checks status, time, duplicates, prerequisites, receipt order or eligibility, and none computes an amount. ✓
- Round-1 F-D7 (no container_count or equipment_type on new rows): equipment_type is now written. Each docstring now declares "it records no container count, because the amount passed in is already the whole amount of the entry." The residual difference from the charter event field list ("container_count: containers the fee is computed on") is now disclosed in the tool contract and changes no amount or reading. **Closed as an observation; no residual finding.**
- **Check 3: pass.**

### prerequisite_graph (revision_2)

- The edges are unchanged in structure: E1 goodwill→customer_roll_fee (value_input, fee_amount); E2 goodwill→destination_change_fee (value_input, pod_changes_owing); E3 late_si→carrier_roll_credit (state_gate); E4 late_vgm→late_si (value_input, prior_late_on_booking). Acyclic, no base or self targets, and `prerequisite` is present on all six policies and the workflow ✓.
- `policy_source` located verbatim:
  - E1, E2 and E4: unchanged sentences ✓.
  - E3 now quotes "before a late submission is recorded on such a booking, the compensation owed for the earlier carrier roll must already be credited under booking_ext_carrier_roll_credit". It is found verbatim in the late_si rule ✓. E3's `condition` ("No compensation owed for an earlier carrier roll of the booking remains uncredited.") now matches its sentence exactly. **Round-1 F-D4 closed.**
- `effect` texts, re-read as general text (round-1 F-D1):
  - E4: "raises prior_late_on_booking by one, so the verified gross mass is measured against the allowance after that row: it stays at 0.00 only while the booking's late rows are still fewer than late_doc_fee_free_occurrences_365d and the allowance is open, and is charged the full fee otherwise." Conditional and general. In the round-1 counter-world (AHL Premium Express, free 3) it gives 0.00, which agrees with compute ✓.
  - E2: "pod_changes_owing falls to 0; the change account becomes complete only when no customer roll fee is owed either, and the waiver result can take the fee row's amount only after that and only if the other conditions of the waiver hold." It agrees with compute in both admissible orders and in the shortfall counter-world ✓.
  - E3: general ✓.
  - E1: "fee_amount is that row's amount_usd instead of 0". The "instead of 0" describes the prior state only where the booking has no earlier customer_roll_fee row. With an earlier row, fee_amount before the charge is that older row's amount (LATEST). After the charge, the conclusion (fee_amount = the new, latest row) is right in every world, so there are not two conclusions. Observation R2-O1.
  - **Round-1 F-D1 closed.** No `effect` now contradicts compute in any world.
- **Check 7: pass.**

### override_declarations (revision_2)

- roll_fee_goodwill (round-1 F-D2): a second `overwrite` entry now names base s1 "The desk may waive a single fee row as goodwill at the verified customer's request." Its `replaced_by` is "These conditions are added to those of booking_goodwill_waiver: a customer roll fee row that meets every base condition but fails the complete change account, the positive amount or the contract condition is not waived." The same sentence is in the rule. The three added 0/1 gates (account complete, amount > 0, contract shortfall 0) are now declared. The merged semantics are unique: base conditions plus the additions, for customer roll fee rows. **F-D2 closed.** Two residues:
  - R2-O2: the superseded clause is base s1, the general permission, which reaches every waivable charge code. The replacement speaks only of customer roll fee rows. A literal splice would leave booking_goodwill_waiver without its opening permission sentence for cancellation, no-show, late-document, amendment and pod-change fee rows. The remaining base sentences ("Only rows with charge_code … may be waived", the authority, quota and window gates) still carry that permission, and no task in this difficulty waives another code. Observation.
  - R2-O3: "The fee row concerned is the latest customer_roll_fee row of the booking by event_date" still narrows base s1's "a single fee row at the verified customer's request" without being named. It bites only where a booking carries two or more customer_roll_fee rows and the customer asks about an older one. Observation, to be checked against each world.
- carrier_roll_credit (round-1 F-D3): the second `overwrite` names "when booking_msr_carrier_rolls, counted including the roll being compensated, does not exceed max_compensated_carrier_rolls". Its replacement is the position sentence. **F-D3 closed.**
- late_si_record: the two new ordering sentences have no base counterpart, since base is silent on order. They declare nothing and need no declaration. The allowance overwrite is as in round 1 ✓.
- destination_change_fee, customer_roll_fee, late_vgm_record: as in round 1, and all amount-changing clauses are declared. The added "more than one rejected acceptance" exclusion narrows only the extended quantity (chargeable containers) and touches no base sentence ✓.

### findings (revision_2)

Status of each round-1 charter item, as verified by the auditor:

| Round-1 item | Round-2 status | Evidence |
|---|---|---|
| F-D1 (RED) world-bound `effect` texts | **closed** | E4 and E2 effects are now conditional and agree with compute in the round-1 counter-worlds. E1 has a harmless residue (R2-O1). |
| F-D2 undeclared goodwill gates | **closed** (declared) | second overwrite on booking_goodwill_waiver s1. Residues R2-O2 and R2-O3. |
| F-D3 undeclared carrier-roll count basis | **closed** | second overwrite on booking_rollover |
| F-D4 E3 narrower than its sentence | **closed** | the sentence itself is now narrowed to carrier-roll compensation, so condition = sentence |
| F-D5 goodwill completeness vs zero-fee changes | **closed** | the zero-fee branches are added to `pod_changes_owing` / `roll_fees_owing` together with their rule sentence |
| F-D6 CFIELD single-acceptance domain | **partly closed** | the rejected side is declared out of scope in four policies. The approved side ("at least one … approved with a positive container_count" vs a single CFIELD read) is unchanged in late_si/late_vgm. It is still an observation; no world instantiates it. |
| F-D7 tool rows without container_count / equipment_type | **closed** (declared) | equipment_type is written, and "records no container count" is declared in each docstring |
| F-D8 general event-order sentence | **closed** | the sentence is removed |

New charter-level items (all observations, none demonstrable as a second answer):
- **R2-O1**: E1 `effect` "instead of 0" is a prior-state description true only where no earlier customer_roll_fee row exists. The post-charge conclusion is right everywhere.
- **R2-O2**: the scope of the superseded base s1 (above).
- **R2-O3**: the "latest row" selection is still undeclared against base s1 (above).
- **R2-O4**: goodwill's `chargeable_containers` uses the rejected-acceptance CFIELD without restating the "more than one rejected acceptance" exclusion that the fee policies declare.
- **R2-O5 (workflow dataflow, bears on task 1)**: the rebuilt `dataflow` declares only `object_binding` edges on booking_id (0→1, 1→3, 2→3). The state dependencies the order_rationale relies on are not declared: step 2's `bookings.vgm_submitted_at` consumed by step 3, step 1's late_si_fee row counted by step 3's `prior_late_on_booking`, and step 0's credit gating step 1. The round-1 wrong edge (1→4 via si_submitted_at) is gone. Nothing is misdeclared, but the state flow is under-declared. The step list and order_rationale fix the order, so no scored value moves. Assessed in task 1's file.

**No charter-global RED in revision_2.**

### closing_checklist (revision_2)

Written 2026-09-13 after both round-2 derivations were frozen (hashed 05:09:47Z) and both round-2 GTs revealed (05:09:59Z). The charter-global part of `## revision_2` above was written about 05:06Z, before any round-2 task view or GT was opened, and is unchanged since.

**The difficulty closes at the source layer in revision_2.** Every comparison section now carries PASS:

| Task | Policy self-consistency | Problem tree | Unique solution | revision_2 verdict line |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | **PASS** |

Every round-1 RED is closed:
- F-D1 (charter): the effects are now general.
- T0-1: the closure sentence was recomputed and is now true.
- T0-2: the E2 effect agrees with compute in both orders.
- T1-1: the persona raises only the VGM, and the SI node is policy-discovered.
- T1-2: the order_rationale is grounded in rule sentences, and its swap figures were replay-verified.

Step 4 checklist:
- Per-task files map one-to-one to the tasks, with `_difficulty.md` alongside. Round-1 text is untouched and round-2 text is appended under `## revision_2`. Every revision_2 comparison is PASS ✓
- The extended policies are fully covered and disjoint (charter_scope, revealed): task 0 = {destination_change_fee, customer_roll_fee, roll_fee_goodwill}; task 1 = {carrier_roll_credit, late_si_record, late_vgm_record} + the workflow. The union is all six, and each scope spans its whole tree ✓
- Exactly one workflow, claimed only by task 1 ✓
- Task tools and GT are closed. Task 0 uses 3 tools and task 1 uses 4, disjoint, together the 7 tools in task_tools.py. The removed tool is referenced nowhere. Every uuid8 is independent and frozen ✓
- Each tree has 2 policy-discovered prerequisites, at least 1 value_input edge, and no cycle. Task 0: E1 value_input + E2. Task 1: E4 value_input + E3 state_gate, ordering-only (observation) ✓
- The difficulty-wide prerequisite graph is a DAG with no cross-task edge. The coupling sentence behind round-1 F-D4/F-D8 is removed, so no latent cross-component edge remains ✓
- Gates on the final form: the auditor did not re-run them (cite, do not run). The coordinator's round-2 snapshot (all seven exit 0; traceability deferred) ran on the reworked files, whose hashes at close are extended 7838ceb0…, tools 29d28304…, 0.json bcfad1bb…, 1.json b96916aa…. The auditor's own erlbench replay of both golds reproduces the dossiers' terminal hashes (e4a634e5…, 1f8029b7…) ✓

Observations carried into any later round (none is a RED, and none gives a second answer in either world):
- R2-O1: E1 effect "instead of 0".
- R2-O2: scope of the superseded goodwill s1.
- R2-O3: the "latest row" narrowing is undeclared.
- R2-O4: goodwill does not restate the multi-rejected exclusion.
- R2-O5: dataflow declares only object bindings.
- F-D6: approved-acceptance CFIELD domain, residual.
- R2-T1-O1: world-bound illustration in order_rationale.
- R2-T1-O2: late SI row dated today rather than on the receipt date.
- E3 ordering-only.
- T1-4: VGM grace not in temporal_feasibility.
