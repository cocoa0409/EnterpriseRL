# Policy-task audit — dangerous_goods_desk / charter-global

## charter_global_frozen

- Frozen: 2026-09-13T05:47Z, before any task GT of this difficulty was revealed. Auditor: Claude Opus 5, running as an independent erl-task-policy-audit subagent. It did not author any of the audited artifacts.
- Frozen inputs (sha256 re-checked at freeze time; they match the coordinator's masking-time hashes):
  - `env/global_container_shipping_line/tasks/dangerous_goods_desk/dg.extended.yaml` = `4e5de01bcb99817fa6bf06af931e64937729dd2fc596273290ede23c4d69bc1b`
  - `env/global_container_shipping_line/tasks/dangerous_goods_desk/task_tools.py` = `ed780a298d733add6b6fcd89c5b7175a0863cbe4aaeb5da95f28adf44cfe7d74`
  - I also read `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/dg.yaml`, the tier-rank lines of `blueprint/products/contract.yaml` and `blueprint/products/booking.yaml`, and `erlbench/` (scoring.py, tools.py make_id/now, engine.py unlock flow). For the DSL semantics I read only `build_env`/`eval_compute` in `skills/erl-task-instantiate/scripts/check_compute.py`.
- Permitted when writing this section: the charter, the schema, the shared and task tool contracts, the runtime. Nothing here derives from `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract` or `prerequisite_closure`. None of those were open when this section was written.
- Entry conditions (Step 0): the brief supplied the 7 instantiation-stage gate lines (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and check_cross_fire all exit=0), the two masked views with their hashes, and HASHES.txt. check_traceability is deferred until the KB is published. The inputs are complete. I cite the gates and did not re-run them.
- Base-copy check: `diff <(head -n 861 dg.extended.yaml) blueprint/products/dg.yaml` gives only `861d860 <` (one blank separator line). **The base section is a verbatim copy.**

### DSL facts used below (from `check_compute.build_env`)
- `CFIELD(cat, field, **eq)` always adds `customer_id = CUST`, where `CUST` is the **holding's** customer_id. It returns the first matching row (`hs[0]`), or None.
- `COUNT/SUM/LATEST` are auto-scoped to the holding (`dg_id`). `NOW` = `frozen_time[:10]`.
- `RND(x, n)` = Python `round(float(x), n)`: binary-float, half-to-even at exact ties. It is **not** half-up.

### policy_conflict_scan

The structured policy has 12 base policies, 7 `extended_policies` and 1 workflow.

**Overlapping subjects**
| Subject | Extended owners | Relation |
| --- | --- | --- |
| `dg_amendment_fee_charged` | `dg_ext_amendment_fee` (charge_code amendment_fee, tool `book_dg_amendment_fee_40feddd0`) and `dg_ext_re_review_fee` (re_review_fee, tool `book_dg_re_review_fee_c46e22ec`) | Different charge codes and different tools. Neither compute reads the other's rows, so there is no conflict. |
| `dg_approved` | `dg_ext_review_decision` (computes `decision`) and `dg_ext_approval_admin_fee` (computes `admin_fee_usd`) | Both bind to `record_dg_review_decision_9aa03de9` on different args, so they complement each other. See F-6: the admin-fee compute does not read the decision. |
| `dg_surcharge_charged` | `dg_ext_loading_surcharge` (dg_surcharge) and `dg_ext_marine_pollutant_surcharge` (marine_pollutant_surcharge) | **The tool contracts overlap (F-8).** |
| `dg_payment_received` | `dg_ext_remittance_application` | Reads the whole account. |

**Triggers and time anchors**
- All extended policies are `state_due` except the remittance, which is `on_request`.
- No extended policy restates a base time gate: late acceptance, amendment deadline, approval validity or waiver window. They are inherited unchanged through `base_policy_refs` and contradicted nowhere (see override_declarations).

**Eligibility and cross-category reads**
- Every cross-category read is a `booking` or `contract` read through CFIELD, so it is scoped to the holding's customer.
- The booking status sets differ on purpose:
  - "ahead of loading" = {requested, confirmed, equipment_released, gated_in}, in the amendment and re-review fees.
  - "live" = {requested, confirmed, equipment_released}, in the decision and admin fee. This matches base `booking_is_dg_and_live.state_contract`.
  - "loaded" = {loaded, departed, closed}, in the loading and marine-pollutant surcharges.
- These sets never overlap in a way that yields two conclusions for one quantity.

**Terminal states**
- The decision tool writes approved + approved_date + a dg_admin_fee row, or rejected + rejected_date with no row.
- Reopen writes `under_review` only.

**Task scopes as derivable from the charter alone** (to be confirmed against `charter_scope` in closing_checklist, after the reveals)
- The workflow `dg_wf_amended_declaration_redecision` binds `dg_ext_amendment_fee`, `dg_ext_re_review_fee`, `dg_ext_review_decision` and `dg_ext_approval_admin_fee` (steps 2–4).
- The remaining three, `dg_ext_loading_surcharge`, `dg_ext_marine_pollutant_surcharge` and `dg_ext_remittance_application`, form a separate tree rooted at the remittance.
- With M=2, the natural partition is {workflow tree} and {remittance tree}. It is disjoint and it covers all 7 extended policies and the one workflow.

**Blueprint claim coverage (observation only)**
- The claimed event types `dg_application_submitted`, `dg_review_started`, `dg_rejected`, `dg_late_declaration_fee_charged`, `dg_withdrawn`, `dg_withdrawal_fee_charged` and `dg_charge_waived` have no extended policy and no task tool.
- The skill requires only that the extended policies be fully covered, so this is recorded and not graded.

### rule_compute_equivalence

Check 2 over all 7 extended policies. The sweep ran in both directions: every `compute` binding has a `compute_basis` quote, and every rule sentence is either implemented or inherited.

**dg_ext_amendment_fee — equivalent.**
- Implemented:
  - The count of signed amendments (filter submission_type=amendment, outcome=signed), which excludes awaiting, returned and withdrawn submissions.
  - `signed_before = now − 1`. This is valid only when evaluated after the amendment being charged is on file, which the workflow order guarantees.
  - The free-allowance tier, the full fee ("never pro rata"), the acceptance-open branch, the booking-ahead-of-loading branch and RND 2.
- The amendment gates of base `dg_amendment` are not restated in compute. They are inherited as base eligibility, not overwritten, so this is only an observation. The gates are: the deadline (`amendment_deadline` applies_to dg_amendment_fee_charged), the maximum count (`amendment_count`), the ±weight percentage and the sailing capacity.

**dg_ext_re_review_fee — NOT equivalent: F-3.**
- Implemented: the category flag and rate, "approved at least once" (a dg_admin_fee row exists), the "one change charged once" date comparison, the open and ahead-of-loading branches, and RND.
- **Not implemented:** the triggering condition "When the booking carrying approved goods moves to another sailing". No binding reads a roll or vessel-change record, and no `compute_basis` quotes this clause.

**dg_ext_review_decision — NOT equivalent: F-1 and F-2.**
- Implemented: the signed initial declaration, chargeable amendments (MX), amendment_fees_settled, and the goods-fit list: class/PG, lane, equipment, POD, DG + live booking, and quantity/weight.
- **Not implemented, part 1 (F-1):** "A review reopened because the booking moved to another sailing is decided only after the re-review fee for that change of sailing is booked." No binding exists, and `result` gates only on `signed_declaration_on_file and amendment_fees_settled`.
- **Not implemented, part 2 (F-2):** "The booking mix and sailing allotment are counted under dg_agg_booking_mix and dg_agg_sailing_capacity on the booking's current sailing, and a review failing either of them is rejected." `goods_fit` has no mix or allotment term. The `compute_basis` quote for `result` does contain "the booking mix and sailing allotment still hold", but the expression ignores it: an empty promise.

**dg_ext_approval_admin_fee — near-equivalent: F-6 (observation).**
- The rule "a rejection books no fee and records 0.00" has no binding. The compute returns 60.00-type values for any under_review acceptance on a live DG booking, whatever the decision.
- The decision tool writes no ledger row on `rejected` and stores no fee. So this divergence can never change a DB state, and it stays an observation.

**dg_ext_loading_surcharge — NOT equivalent in rounding mode: F-7.**
- Branches equivalent to the rule:
  - The 20-foot type list; this matches the equipment enum.
  - Hard-coded class uplifts. They equal every category's `class_surcharge_uplift_pct_map` over that category's eligible classes, and LQ is 0.
  - Hard-coded lane uplifts. They are identical across all six variants.
  - The contract rank 1..6. This matches `products/contract.yaml` ranks.
  - `min_rank != 0`, the discount applied on the uplifted figure, the weight exemption, and the once-per-acceptance and loaded branches.
- **Not equivalent:** the rule says "rounded half up to the cent only on that final product", but `RND` is Python round.
  - Demonstration: F&C, class 3, PG II, transatlantic_westbound, 40DV, 1 container, rank ≥ 5.
  - Compute: `375*(1+15/100)*(1-10/100)*1 = 388.12499999999994`, so `RND` gives **388.12**.
  - Rule, in exact decimal half-up: 431.25 × 0.9 = 388.125, so **388.13**.
  - Script output is recorded in the task files' re-check notes.

**dg_ext_marine_pollutant_surcharge — equivalent.**
- Rate × container_count, no uplift, discount or exemption, the marker and loaded branches, and once per acceptance.

**dg_ext_remittance_application — NOT equivalent: F-4.**
- The charges due are equivalent: the whole-life ledger sums, rounded.
- **Not implemented:** "a remittance smaller than the charges due is applied at the amount remitted". No binding reads the remittance amount, and `result` returns `charges_due` unconditionally when it is > 0 and the payer check passes.
- Also: the rule's `payer_is_booking_party` test is implemented as `CFIELD('booking','customer_id', booking_id=…) == CUST`. Because CFIELD pre-filters `customer_id = CUST` (the acceptance holder), the expression tests "booking party == applicant", not "paying caller == booking party" (F-5).

### action_binding_and_uuids

**(target_tool, computes) pairs — each is claimed by exactly one policy.**
- `(book_dg_amendment_fee_40feddd0, amount_usd)`
- `(book_dg_re_review_fee_c46e22ec, amount_usd)`
- `(record_dg_review_decision_9aa03de9, decision)`
- `(record_dg_review_decision_9aa03de9, admin_fee_usd)`
- `(book_dg_loading_surcharge_44d311b2, amount_usd)`
- `(book_dg_marine_pollutant_surcharge_a7ecff71, amount_usd)`
- `(record_dg_payment_ee299820, amount_usd)`
- Tools with no computed arg: `sign_amended_dg_declaration_eb5287cf` (owner=user) and `reopen_dg_review_a9bc3033`.

**Single business reading — FAILS for the two surcharge tools (F-8).**
- The two tools are `task_tools.py:168` and `task_tools.py:200`.
- Both expose `charge_code` as an enum of all 11 dg codes. The loading tool documents `marine_pollutant_surcharge` as "the second loading row for goods marked marine pollutant", and the marine-pollutant tool documents `dg_surcharge` as "the per-acceptance hazardous-cargo surcharge written when the goods are loaded".
- Both write an identical row shape. The only difference is the id prefix:
  - `ctx.make_id("dgl_", dg_id, charge_code, container_count, amount_usd)` in the loading tool;
  - `ctx.make_id("dgm_", …)` in the marine-pollutant tool.
  - `erlbench/tools.py` make_id is `prefix + sha256(prefix:parts)`, so the two tools write different `dg_event_id`s for the same row. That gives a different final DB hash under `erlbench/scoring.py`.
- The loading tool's enum also admits dg_admin_fee, late_declaration_fee, amendment_fee, re_review_fee, withdrawal_fee, misdeclaration_penalty, inspection_cost_recovery, payment and waiver. It would write all of them with `event_type=dg_surcharge_charged`, which invites mis-booking outside the owning policies.

**Other contracts — no findings.**
- The remaining tools' docstrings admit only their policy's reading.
- No tool adds a confirmation, review, wait or out-of-policy procedure.

**UUID8s — PASS.**
- The eight suffixes are `eb5287cf`, `a9bc3033`, `40feddd0`, `c46e22ec`, `9aa03de9`, `44d311b2`, `a7ecff71` and `ee299820`.
- They are pairwise distinct. No two share a prefix longer than 1 hex digit (`a9…`/`a7…`, `4…`), and there is no sequential, adjacent or common-stem pattern. They are consistent with independent generation.
- Each appears only on its own tool: in the def name, in the charter `target_tool`/workflow `tool`, and nowhere else.

### prerequisite_graph

Check 7.

**Coverage.** `prerequisite` is filled everywhere:
- `[]` on dg_ext_amendment_fee, dg_ext_re_review_fee, dg_ext_approval_admin_fee, dg_ext_loading_surcharge, dg_ext_marine_pollutant_surcharge and the workflow;
- two edges each on dg_ext_review_decision and dg_ext_remittance_application.

Every `problem` names an extended policy id in this file. None names a base policy, and none is a self-edge.

**Graph.**
- Edges: review_decision→{amendment_fee, re_review_fee}; remittance→{loading_surcharge, marine_pollutant_surcharge}.
- It is acyclic, with two disjoint stars.

| Edge | policy_source verbatim in rule? | condition vs sentence | resolved_by | kind / gate |
| --- | --- | --- | --- | --- |
| review_decision → dg_ext_amendment_fee | yes ("every amendment fee owed on the acceptance's signed amendments is booked before its review is decided") | same | `book_dg_amendment_fee_40feddd0` = the target tool of that policy; booking raises `amendment_fees_booked` | value_input → `amendment_fees_settled`, which exists in compute. PASS |
| review_decision → dg_ext_re_review_fee | yes (full sentence) | same | `book_dg_re_review_fee_c46e22ec` | state_gate → `gate: dg_ledger.charge_code`. **FAIL (F-1):** a table field, not an eligibility gate id (the extended policy has no `eligibility` block) and not a compute binding. The rule's gate has no executable counterpart. |
| remittance → dg_ext_loading_surcharge | yes | same | `book_dg_loading_surcharge_44d311b2` | value_input → `surcharges_booked`, which exists. PASS |
| remittance → dg_ext_marine_pollutant_surcharge | yes (with "likewise") | same, minus "likewise" | `book_dg_marine_pollutant_surcharge_a7ecff71` | value_input → `surcharges_booked`, which exists. PASS |

- No authoring-viewpoint phrasing ("in this task / at the opening / current world") appears in any `prerequisite` field.
- `effect` texts are accurate, except that the re-review edge's "the gate that holds a sailing-change review open" names a gate that no compute holds (F-1).

### override_declarations

Check 1, finding half only. Each extended policy is compared sentence by sentence against each of its `base_policy_refs`. Verdict words: **follows** = the extended text computes the base quantity the same way; **inherited** = the extended text is silent and the base provision stands; **differs** = the extended text handles the scored quantity differently.

**dg_ext_amendment_fee** — refs [dg_amendment], `overwrite: []`
| Base sentence (dg_amendment) | Verdict |
| --- | --- |
| "A declaration is amended only by a new declaration the shipper signs…" | follows (signed-only count; the sign tool is owner=user) |
| "An amendment may change only the particulars listed in … amendable_attributes…" | inherited |
| "After approval an amendment is possible only when amendment_after_approval_allowed is true, and it returns the acceptance to review." | inherited |
| "An amendment is accepted only when it is signed no later than … late_amendment_cutoff_hours_before_cargo_cutoff…" (+ counting rule) | inherited; not in compute (observation) |
| "An acceptance takes at most max_amendments_per_acceptance signed amendments…" | inherited; not in compute (observation) |
| "The declared gross weight may change by no more than max_gross_weight_change_pct … always within dg_agg_sailing_capacity." | inherited |
| "An amendment is free while dg_msr_signed_amendments is below free_amendments_per_acceptance and otherwise costs amendment_fee_usd, referencing the amendment submission." | follows (`signed_before` = the measure "before the amendment being handled") |
| "When the booking moves to another sailing …" | not this policy's quantity |
| "Amendment and re-review fees may be booked only while the acceptance is submitted, under_review or approved." | follows. **The extended text adds a condition** the base does not have: "only for goods whose booking has not yet been loaded … requested, confirmed, equipment_released or gated_in". This is a 0/1 multiplier on an amount the base already fixes, and it is undeclared. See F-9. |

**dg_ext_re_review_fee** — refs [dg_amendment, dg_surcharges], `overwrite: []`
- The dg_amendment re-review sentence ("charged re_review_fee_usd once for that change of sailing, with no submission reference") is followed.
- "approved at least once via dg_admin_fee row" and the date-window reading of "once for that change" are operationalisations of "an approved acceptance" and "once".
- "Amendment and re-review fees may be booked only while …" is followed, plus the same undeclared ahead-of-loading multiplier (F-9).
- dg_surcharges "Goods not loaded by then return to review under dg_amendment" is not charged by this policy. That is consistent, because the base fee is tied to "change of sailing" only.

**dg_ext_review_decision** — refs [dg_declaration_and_review, dg_application_eligibility, dg_agg_booking_mix, dg_agg_sailing_capacity, dg_amendment]; one overwrite
- The `superseded_clause` is a verbatim substring of base dg_declaration_and_review, so the declaration is well formed. The replacement adds the "can be decided" gate, giving a third outcome (stays under_review). Both are declared.
- Remaining base sentences:
  - "Review starts only once the shipper has signed…" — follows (reused as a decide gate).
  - Lead time, late acceptance and late fee — inherited, not this quantity.
  - "The line decides within review_sla_hours" — inherited; it is a service deadline, not a wait.
  - "the shipper is told the reason and nothing is charged for a rejection" — follows (the tool writes no row on rejection).
  - "Approval sets approved_date and charges dg_admin_fee_usd" — delegated to dg_ext_approval_admin_fee.
- Merged-semantics residue (observation, F-11): the replacement narrows "fits the category under dg_application_eligibility" to an enumerated list introduced by "only when all of the following hold". That phrasing states a necessary condition. dg_application_eligibility is still in `base_policy_refs`, so its applicant conditions could be read as still binding at the decision: contract_booking_required, min_customer_tenure_days, the misdeclaration block, the resubmission wait and limited-quantity routing. Compute treats the list as sufficient. The two readings diverge only on facts those conditions test.

**dg_ext_approval_admin_fee** — refs [dg_declaration_and_review, dg_surcharges], `overwrite: []`
- Followed: "Approval sets approved_date and charges dg_admin_fee_usd" and "The admin fee is charged at each approval".
- Base dg_surcharges "Each charge code is booked once per charging date" (dedup `code_once_per_date`) means a second same-date dg_admin_fee row is not booked. The extended text says "when a dg_admin_fee row is already dated on the handling date the fee booked is 0.00". Combined with the decision tool, which always writes a dg_admin_fee row on `approved`, this produces a 0.00 row where the base produces none. That is an undeclared deviation in the row set (F-10).

**dg_ext_loading_surcharge** — refs [dg_surcharges], `overwrite: []`
- Each base sentence is followed: base/20-40 ft; "sum of three uplifts … never compounded"; discount on the uplifted figure when rank ≥ min_rank ≠ 0; × container_count rounded to cent; 0.00 below the weight threshold; approved-or-loaded; once.
- The extended text specifies half-up, which the base leaves open. That is allowed; its compute mismatch is F-7.
- Anonymous substitution: the base says "the uplift of the booking's trade lane", while the extended rule and compute use the acceptance's `trade_lane`. Schema `dg_acceptances.trade_lane` is defined as "trade lane of the carrying booking", so the invariant makes them one quantity. Observation.

**dg_ext_marine_pollutant_surcharge** — refs [dg_surcharges], `overwrite: []`
- Follows "a second row of marine_pollutant_surcharge_per_container_usd times container_count".
- "No weight exemption / no discount" agrees with the base, whose exemption and discount sentences attach to the base surcharge, and with parameter_schema "below which the base surcharge is 0.00".

**dg_ext_remittance_application** — refs [dg_payment, dg_surcharges, dg_goodwill_waiver], `overwrite: []`
- dg_payment "applied to one acceptance, written with the remittance reference exactly as quoted and the amount remitted; it may not exceed the acceptance's charges_due_usd, and any excess is returned by finance and not booked" — the rule follows it; the compute does not (F-4).
- "recomputed from its account rather than read from the balance shown on the acceptance" is a deviation signal, but `charges_due_usd` is by schema "identically the sum of dg_charges deltas", so it is one quantity. Observation.
- **Differs, undeclared:** "A remittance is applied only for the customer who is the booking party … the desk applies no remittance to an acceptance whose booking belongs to another party". This is a 0/1 multiplier on base `applied_amount` that base dg_payment does not contain, and `overwrite` does not name it (F-5).
- The "surcharges booked before a remittance" sentences add ordering. They are not in conflict with dg_surcharges. dg_goodwill_waiver waivers are subtracted, as the base account definition requires.

### findings

How to read these:
- A charter-level **SOURCE-POLICY RED** means two passages of the artifacts reach different conclusions in one situation of the charter's real domain. That situation is demonstrated below; where no task world exhibits it, it is a minimal constructed one.
- "Task bite" says whether a task's own world and scored solution are affected. The per-task demonstration lives in that task's file.

**F-1 — SOURCE-POLICY RED (checks 2 and 7): the re-review gate of dg_ext_review_decision exists only in prose.**
- Symptom: the rule says "A review reopened because the booking moved to another sailing is decided only after the re-review fee for that change of sailing is booked. While either condition is missing the review stays under_review and no decision is recorded."
  - The compute is `result: "'under_review' if not (signed_declaration_on_file and amendment_fees_settled) else (…)"`. It has no re-review term.
  - The prerequisite edge declares `kind: state_gate, gate: dg_ledger.charge_code`. That is a column name, not an eligibility gate and not a compute binding.
- Root cause: the rule→compute translation dropped a gate, and the prerequisite `gate` field was filled with a field path instead of a real gate.
- Demonstrated consequence: take any acceptance reopened after a change of sailing, with the initial declaration signed, amendment fees settled, goods fitting and the re-review fee not yet booked.
  - Rule: no decision (stays under_review).
  - Compute: `approved`.
  - Same situation, two conclusions.
- Task bite: **task 0**. This is the second edge of its tree; the load-bearing run is in `0.md`.

**F-2 — SOURCE-POLICY RED (check 2): booking mix and sailing allotment are promised by the decision rule but absent from its compute.**
- Rule: "a review failing either of them is rejected". Compute: `goods_fit = class_fits and lane_fits and equipment_fits and port_fits and booking_live_dg and quantity_fits`.
- Constructed demonstration: an F&C acceptance of 4 containers under review, where the same customer's other live F&C acceptances on the same vessel_voyage hold 7 containers (7 + 4 = 11 > `max_containers_per_sailing_per_customer` 10).
  - Rule: `rejected`. Compute: `approved`.
- Task bite: **task 0 only if its allotment or mix actually fails.** Evaluated in `0.md`.

**F-3 — SOURCE-POLICY RED (check 2): dg_ext_re_review_fee has no binding for its own trigger, "When the booking carrying approved goods moves to another sailing".**
- Constructed demonstration: an F&C acceptance approved once (one dg_admin_fee row), with no re_review_fee row, on a confirmed booking that was never rolled.
  - Compute: `approvals_charged>0 and ''<approved_date and open and ahead_of_loading` gives **75.00**.
  - Rule: no change of sailing, so no fee.
- Task bite: task 0's world contains such an acceptance, but it is not the scored holding. See `0.md`.

**F-4 — SOURCE-POLICY RED (check 2): the remittance compute ignores the remittance amount.**
- Rule: "a remittance smaller than the charges due is applied at the amount remitted" (the base `applied_amount: min(amount_usd, dg_charges)`). Compute: `result = RND(0 if charges_due <= 0 else (charges_due if payer_is_booking_party else 0), 2)`.
- Constructed demonstration: charges due 1,000.00 and a remittance of 600.00.
  - Rule and base: 600.00. Compute: 1,000.00.
- Task bite: task 1 only if the quoted remittance is below the charges due. Evaluated in `1.md`.

**F-5 — SOURCE-POLICY RED (check 1, undeclared override; plus a check 2 mismatch): the booking-party restriction on remittances.**
- The base `dg_payment` has no payer restriction. The extended text adds "applied only for the customer who is the booking party", and `overwrite: []`.
- Separately, compute `CFIELD('booking','customer_id', booking_id=F('booking_id')) == CUST` tests "booking party == acceptance holder", because CFIELD pre-filters on the holder.
- Constructed demonstration: forwarder X holds the acceptance on a booking whose booking party is Y.
  - When X remits: base applies min(amount, due); the extended rule applies 0.
  - When Y remits: the extended rule applies; the compute returns 0.
- Task bite: task 1 only if the payer, the booking party and the holder differ. Evaluated in `1.md`.

**F-6 — observation: dg_ext_approval_admin_fee's compute does not read the decision.**
- The rule says "a rejection books no fee and records 0.00".
- The decision tool writes nothing and stores no fee on `rejected` (`task_tools.py:159-161`), so no DB state can differ.

**F-7 — SOURCE-POLICY RED (check 2): the rounding mode of dg_ext_loading_surcharge.**
- The rule says half-up. `RND` is Python round on binary floats.
- Demonstration: 375 × 1.15 × 0.9 × 1 gives rule **388.13** and compute **388.12**.
- Task bite: task 1 only if its product has a third-decimal 5. Evaluated in `1.md`.

**F-8 — SOURCE-POLICY RED (check 3): the two surcharge tools both write both surcharge rows.**
- `book_dg_loading_surcharge_44d311b2` and `book_dg_marine_pollutant_surcharge_a7ecff71` share an 11-code `charge_code` enum, and each docstring describes the other's row as its own.
- The rows differ only in the id prefix (`dgl_` vs `dgm_`), so the same business write through the other tool gives a different `dg_event_id` and a different DB hash.
- Task bite: **task 1**, which needs both rows. The demonstration is in `1.md`.

**F-9 — SOURCE-POLICY RED (check 1, undeclared override, 0/1 multiplier): the ahead-of-loading condition on amendment and re-review fees.**
- Base: fees may be booked while the acceptance is submitted, under_review or approved. The extended text additionally zeroes them unless the booking status is in {requested, confirmed, equipment_released, gated_in}. Neither `overwrite` names this.
- Constructed demonstration: an approved F&C acceptance whose booking is `cancelled`, with a second signed amendment before the amendment deadline.
  - Base: 175.00. Extended: 0.00.
- Task bite: task 0 only if its booking status is outside the set. Evaluated in `0.md`.

**F-10 — SOURCE-POLICY RED (check 1): a second same-date approval conflicts with the base's once-per-date rule.**
- Base `code_once_per_date`: "Each charge code is booked once per charging date", so a second dg_admin_fee row is not booked.
- The extended rule books "0.00", and the decision tool unconditionally writes a dg_admin_fee row on `approved` (`task_tools.py:151-155`).
- Constructed demonstration: approve, reopen and re-approve on one date.
  - Base: one admin row. Extended + tool: two rows.
- Task bite: only where a dg_admin_fee row is already dated on the handling date. Evaluated in `0.md`.

**F-11 — observation: the decision overwrite leaves a sufficiency residue.**
- Its "only when all of the following hold" wording leaves open whether the applicant conditions of dg_application_eligibility still apply at the decision (see override_declarations).
- The readings diverge only for categories or customers that trip those conditions. Evaluated per task.

**F-12 — observation: inherited base amendment gates are not restated in compute.**
- The gates are: deadline, maximum count, weight change percentage and sailing capacity.
- They are inherited, not overridden. Each task file checks them on its own world.

**F-13 — observation: workflow metadata.**
- `dg_wf_amended_declaration_redecision` has no `requires_external_wait` or `zero_wait_proof` field. Its zero-wait claim sits only in the last sentence of `order_rationale`.
- Its `dataflow` misstates the objects moved between steps:
  - The 0→2 `object_binding` names `dg_id`, which step 0 consumes rather than produces. The produced `submission_id`, which step 2 consumes, is undeclared.
  - The 1→2 `state_effect` claims to establish `fee_while_open`, which already holds at `approved`.
  - No flow into step 4 is declared, although step 4 needs status under_review, the amendment-fee row and the re-review-fee row.
- These are shape defects of the one workflow. Their task consequence (none on the terminal state) is argued in the claiming task's file.

(End of the charter-global section, frozen 2026-09-13T05:58Z. Nothing above derives from any revealed GT.)

Freeze record: the "05:47Z / 05:58Z" stamps above were estimates. The authoritative pre-reveal freeze of this file is sha256 `a7d112746d6a812204ba937498b56a0fd79e53deb9aa39d44d7395d40d3cc5d1`, recorded at 2026-09-13T05:52:01Z before either task JSON was opened. The text above that line is unchanged.

## closing_checklist

Written 2026-09-13T05:57Z, after both reveals. It stands below the frozen section on purpose. **Outcome: the difficulty is NOT closed.** The skill closes a difficulty only when every task passes all three relationships, and neither task does.

**Per-task verdicts**
| Task | Policy self-consistency | Problem tree | Unique solution | Verdict line |
| --- | --- | --- | --- | --- |
| 0 (workflow) | SOURCE-POLICY RED (F-1 bites; false dataflow proof on reopen adjacency) | SOURCE-CHAIN RED (re-review edge carries no weight into the decision under the compute) | PASS (GT = frozen derivation; all permutations reach the gold hash) | **SOURCE-POLICY RED + SOURCE-CHAIN RED** |
| 1 | SOURCE-POLICY RED (F-8 bites) | PASS | SOURCE-TASK RED (two terminal states via the surcharge tools) | **SOURCE-POLICY RED + SOURCE-TASK RED** |

**Step 4 items**
| Item | Status |
| --- | --- |
| One audit file per task, with `_difficulty.md` beside them; revisions traceable | `0.md`, `1.md` and `_difficulty.md`, all revision 1. Each comparison section is present; **neither carries PASS.** |
| Extended policies fully covered | yes. Task 0 `charter_scope` = {dg_ext_amendment_fee, dg_ext_re_review_fee, dg_ext_review_decision, dg_ext_approval_admin_fee} + the workflow. Task 1 = {dg_ext_loading_surcharge, dg_ext_marine_pollutant_surcharge, dg_ext_remittance_application}. The union is all 7. This matches the pre-reveal partition in policy_conflict_scan. |
| Scopes pairwise disjoint, spanning each whole tree | yes: no shared policy, workflow or task tool (5 + 3 = 8 tools) |
| Exactly one workflow, claimed by exactly one task | yes (task 0) |
| Task tools and GT closed | yes; GT uses only charter-bound tools. **But** the tool module admits a second writer for the surcharge rows (F-8). |
| Independent, frozen uuid8 per tool | yes (action_binding_and_uuids) |
| Each tree has ≥ 2 prerequisites, ≥ 1 value_input edge, no cycle | declared: yes for both. **Load-bearing: task 0 has only 1 load-bearing prerequisite under the executable compute** (F-1 / SOURCE-CHAIN). Task 1: 2 of 2. |
| Difficulty-wide prerequisite graph is a DAG | yes: two disjoint stars, and no cross-task reference |
| Gates re-run on the final form | not applicable yet. There is no final form, because the audited artifacts carry open REDs. The current form's gate snapshot is the one supplied in the brief (all 7 exit=0). Hashes at closing time are unchanged: extended `4e5de01b…c1b`, tools `ed780a29…fe74`, `tasks/0.json` `6d553a4f…fd96`, `tasks/1.json` `e5cbf17d…32bd5`. |

**Charter-level REDs with no bite on either task**

These still block a clean charter, but neither task exhibits them:
- F-2 (mix/allotment absent from the decision compute);
- F-3 (the re-review fee compute has no change-of-sailing trigger; exhibited on task 0's non-scored sibling `bfc0f29f…`);
- F-4 (remittance amount absent from compute; the artifact concedes it as a "Known limit");
- F-5 (undeclared booking-party restriction, and the compute tests the holder instead of the payer);
- F-7 (half-up vs Python round);
- F-9 (undeclared ahead-of-loading multiplier);
- F-10 (same-date second admin row).

Post-reveal corroboration:
- Task 0's design_rationale states "Mix and allotment are measured across acceptances and are judged by the agent from the records … The re-review gate is a state gate the agent applies (not a compute binding)". That confirms F-1 and F-2 were deliberate authoring choices, not oversights.
- These conclusions stand as recorded in the frozen section. Nothing in it was edited after the reveal.

The cross-difficulty merge surface and the scenario-level checks are out of scope and were not run.

---

## revision_2

### charter_global_frozen (revision 2)

**Freeze metadata**
- Written 2026-09-13T06:16Z, before any round-2 task GT was opened. Auditor: Claude Opus 5 (the same independent auditor as round 1).
- The round-1 text above is untouched. Its file hash at the start of round 2 was `709706499b3ca4d4f232780e29e71dd6408f22356609f26691816187e160f39f`.

**Inputs (re-hashed at freeze)**
- `dg.extended.yaml` = `ae78645fe3669e32242a7518b7f64af944a0520260c3659c676bd0161b6d37a0`. Changed from round 1 (`4e5de01b…`).
- `task_tools.py` = `e2eaaa4e88e7cca802710e0a1fb784b6f3337e40ef7d73e44bf5b6222a4db38f`. Changed from round 1 (`ed780a29…`).
- Both shared inputs moved, so **every charter-global section is re-derived in full below**. Nothing is carried forward by reference.

**Entry conditions**
- Coordinator gate snapshot on the reworked files: all 7 exit=0.
- Masked views `source_r2/0.masked.json` (`6bf5119e…`) and `source_r2/1.masked.json` (`71b097ae…`) are byte-identical to round 1, so the task worlds and personas did not change.

**Base copy**
- `diff <(head -n 861 dg.extended.yaml) blueprint/products/dg.yaml` gives only `861d860 <` (one blank line). Verbatim.

**contamination_disclosure (charter and both tasks)**
- In round 1 I revealed and compared both tasks' GT. So I know the round-1 scored values: task 0 = 84200.0 / 175.00 / 75.00 / approved / 60.00; task 1 = 1316.25 / 225.00 / 1541.25.
- Consequently, the round-2 re-derivations **cannot be treated as blind with respect to round-1 GT**. They are recomputations of the reworked charter on the unchanged worlds. Wherever a value agrees with round 1, that agreement is not independent evidence.
- I have not seen any **round-2** GT field.
- Scratchpad reads: only `masked/dangerous_goods_desk/source_r2/` and my own `audit_dg_private/`. The script `audit_dg_private/derive_r2.py` evaluates the reworked computes on those worlds and on constructed probes.

### policy_conflict_scan (revision 2)

**Subjects and tool bindings**
- These are as in round 1.
- The two surcharge tools now each accept a single `charge_code` value (see action_binding_and_uuids).

**Changed rules to re-scan**

1. **dg_ext_re_review_fee — the trigger is redefined.**
   - The new trigger: when the current booking's `etd_date` is more than `approval_valid_days` after the latest `approved_date`, the acceptance returns to review, and a fee is charged if `re_review_on_vessel_change` is true.
   - It is declared as an override of two base sentences: dg_amendment's change-of-sailing sentence and dg_surcharges' "Goods not loaded by then return to review under dg_amendment". Both `superseded_clause`s are verbatim substrings of the base text.
   - The ahead-of-loading multiplier is dropped here; this policy now follows the base state gate.
   - **New conflict surface: see R2-N1.**

2. **dg_ext_review_decision.**
   - Adds a third decide-gate (the re-review fee is booked when owed), implemented as `rereview_settled`.
   - The overwrite now replaces the approval sentence with "decided as approved when the goods fit the category and as rejected otherwise". Mix and allotment are moved to admission, i.e. application or amendment signing. The rule states "These are the only tests of the decision".

3. **dg_ext_approval_admin_fee.**
   - The rule is scoped ("governs no other decision").
   - A 0.00 approval writes no row, and the tool matches this.

4. **dg_ext_amendment_fee.**
   - The ahead-of-loading addition is now a declared overwrite.
   - "an amendment that is free books no row at all".
   - The inherited amendment gates are "judged when the shipper signs and are not part of this fee" (see R2-N2).

5. **dg_ext_loading_surcharge.**
   - Exact cent arithmetic with half-up rounding.

6. **dg_ext_remittance_application.**
   - A declared overwrite of dg_payment's first sentence introduces the holder-is-booking-party restriction.
   - The rule is scoped to covering remittances; a partial remittance is deferred to dg_payment (see R2-N4).

7. **Workflow.**
   - `dataflow: []`, with `requires_external_wait: false` and `zero_wait_proof` present.
   - The order_rationale concedes that the order reopen → fees and fee → fee is a convention.

**Other checks**
- Terminal states and the status sets are unchanged, apart from the re-review policy no longer reading the booking status.
- The derivable partition is unchanged: {workflow + 4 policies} and {3 remittance-tree policies}. It is disjoint and complete.

### rule_compute_equivalence (revision 2)

| Policy | Result | Note |
| --- | --- | --- |
| dg_ext_amendment_fee | equivalent | The compute is unchanged. The new rule sentences (no row for free; declared ahead-of-loading; gates judged at signing) either match the compute or are procedural. |
| dg_ext_re_review_fee | **equivalent** | `latest_approval`, `current_departure`, `days_approval_to_departure` (DAYS = calendar difference; `check_compute.DAYS`), `departs_after_validity` (`>`, so a departure on the last covered day owes nothing), `sailing_uncharged`, `acceptance_open`. Probe: task 0's world with ETD set to 2026-09-24 gives 0.00; with 2026-09-25 it gives 75.00. |
| dg_ext_review_decision | **equivalent** | `rereview_owed` / `rereview_settled` implement "Third, …". Mix and allotment are no longer promised at the decision ("the decision does not count them again"). `result` gates on all three. |
| dg_ext_approval_admin_fee | equivalent | The rejection is out of scope by the rule's own scoping. The "0.00 writes no row" part is carried by the tool (`task_tools.py:152`). |
| dg_ext_loading_surcharge | **equivalent** | `amount_in_cents = base*(100+uplift)*(100−disc)*count/100`, then `int(x+0.5)/100`. All tariff bases are whole dollars, so the float products are exact. The round-1 F-7 probe now gives **388.13** (cents 38812.5 → 38813), and the ×3 case gives 1164.38. The bindings `uplifted_per_container` and `per_container` are no longer used by `result`; this is observation R2-N5. |
| dg_ext_marine_pollutant_surcharge | equivalent | unchanged |
| dg_ext_remittance_application | **equivalent within its declared scope** | The rule now "sets the amount applied from a remittance that covers the acceptance's charges due in full", and `result` = charges due, which matches within that scope. `holder_is_booking_party` compares the booking party with `CUST`, the holder, as the rule now says. |

### action_binding_and_uuids (revision 2)

**(target_tool, computes) pairs**
- Unchanged, and each is still claimed by exactly one policy.

**Surcharge tools (round-1 F-8)**
- `book_dg_loading_surcharge_44d311b2` documents `charge_code` "accepts only one value: dg_surcharge … The marine-pollutant row and every other dangerous-goods charge are never booked with this action", and hard-codes `charge_code="dg_surcharge"` on the row (`task_tools.py:182,193`).
- `book_dg_marine_pollutant_surcharge_a7ecff71` mirrors this for `marine_pollutant_surcharge` (`:214,225`).
- Each business row now has a single documented writer. The shared `dgl_` id prefix cannot collide, because the `charge_code` argument is part of the hash and differs between the two permitted calls.
- **F-8 closed.**

**Decision tool**
- It writes an admin-fee row only when `decision == "approved" and fee != 0` (`:152`).

**Re-review tool docstring** — unchanged, and now in tension with the redefined policy:
- "Book the re-review fee charged when a dangerous-goods acceptance goes back to review because its booking moved to another sailing."
- The `booking_id` argument is described as "reference number of the booking that moved to the new sailing".
- See R2-N1.

**UUID8s**
- The eight suffixes are unchanged and still pairwise independent. **PASS.**

### prerequisite_graph (revision 2)

**Edges**
- review_decision → amendment_fee: value_input, gate `amendment_fees_settled`. The `policy_source` is verbatim in the rule.
- review_decision → re_review_fee: **now value_input, gate `rereview_settled`**. That binding exists in the compute. The `policy_source` "a review whose approval no longer covers the booking's current sailing is decided only after the re-review fee for that sailing is booked" is verbatim in the rule (after "Third, "). `effect` is accurate: booking the fee puts a row dated ≥ approved_date on the account, so `rereview_settled` becomes true.
- remittance → loading and remittance → marine pollutant: unchanged, and PASS.

**Graph checks**
- The graph is acyclic, and every `prerequisite` field is filled.
- No authoring-viewpoint phrasing appears.
- **F-1's check-7 half is closed.**

### override_declarations (revision 2)

Only the sentences that changed are re-swept; the rest are as in the round-1 sweep, and were re-read against the reworked text.

- **dg_ext_amendment_fee.**
  - dg_amendment "Amendment and re-review fees may be booked only while …" is now **declared** superseded, with the ahead-of-loading replacement. The re-review half of that sentence is restated by dg_ext_re_review_fee ("Re-review fees may be booked only while the acceptance is submitted, under_review or approved"), so the merged semantics stay unique. **F-9 closed.**
  - New sentence: the amendment gates "are judged when the shipper signs and are not part of this fee". Base `amendment_deadline` and `amendment_count` have `applies_to` [dg_declaration_amended, **dg_amendment_fee_charged**]. The extended text withdraws them from the fee without naming them in `overwrite` → R2-N2.
- **dg_ext_re_review_fee.** Two declared overwrites, both verbatim. Their merged semantics collide with unrevised base texts → R2-N1.
- **dg_ext_review_decision.** The declared overwrite now also drops mix and allotment from the decision. The base eligibility rules `booking_mix_limit` and `sailing_allotment` have `applies_to` limited to [dg_application_submitted(, dg_declaration_amended)], so nothing structured is weakened. The residue from round-1 F-11 is resolved by "These are the only tests of the decision … not again at the decision". **F-2 and F-11 closed.**
- **dg_ext_approval_admin_fee.** Now consistent with the base `code_once_per_date` (a second same-date approval books no row). **F-10 closed.**
- **dg_ext_remittance_application.**
  - dg_payment's first sentence is declared superseded, so the holder restriction is legal. **F-5 closed.**
  - The superseded sentence also carried "written with the remittance reference exactly as quoted and the amount remitted; it may not exceed … any excess is returned by finance and not booked". The extended rule restates the reference, the cap and the excess handling.
  - For a partial remittance it points back to "dg_payment at the amount remitted", a clause that the same overwrite has just superseded → R2-N4.

### findings (revision 2)

**Status of the round-1 charter findings**
| Round-1 id | Revision-2 status | Evidence |
| --- | --- | --- |
| F-1 (re-review gate only in prose; gate named a column) | **closed** | `rereview_settled` binding + value_input edge. Task 0 probe: skipping the re-review fee now gives `under_review`. |
| F-2 (mix/allotment promised, not computed) | **closed** by a declared redefinition | The rule no longer promises it at the decision. |
| F-3 (re-review trigger not in compute) | **closed as rule↔compute**; replaced by new surface R2-N1 | Rule and compute now agree (task 0 sibling bfc0f29f: 14 days ≤ 21, so 0.00). |
| F-4 (remittance amount ignored) | **closed** by scoping | The compute matches within the declared scope. Residue: R2-N4 (observation). |
| F-5 (undeclared booking-party restriction; payer vs holder) | **closed** | Declared overwrite; the rule and compute are both holder-based. |
| F-6 (admin compute ignores decision) | **closed** | The rule is scoped to approvals. |
| F-7 (half-up vs Python round) | **closed** | 388.13 / 1164.38 half-up (probe). |
| F-8 (two tools write both surcharge rows) | **closed** | Single-value contracts and hard-coded codes. |
| F-9 (undeclared ahead-of-loading multiplier) | **closed** | Declared (amendment); removed (re-review). |
| F-10 (second same-date admin row) | **closed** | Tool and rule. |
| F-11 (decision sufficiency residue) | **closed** | "the only tests". |
| F-12 (inherited amendment gates not restated) | **re-surfaced as R2-N2** (observation) | The gates are now explicitly moved to signing. |
| F-13 (workflow metadata / dataflow) | **partly closed** | The fields are present and the false "establishes fee_while_open" is gone. The empty dataflow is R2-N3 (observation). |

**R2-N1 — SOURCE-POLICY RED (checks 1 and 3; new, introduced by the rework): the redefined re-review trigger leaves unrevised base and tool texts that still define the fee by an actual move of the booking.**
- **Passage A** — the dg_ext_re_review_fee rule (and its declared `replaced_by`): "When the scheduled departure of the sailing the booking currently holds falls more than the category's approval_valid_days calendar days after the acceptance's latest approved_date, an approved acceptance returns to review and, if the category's re_review_on_vessel_change is true, is charged the category's re_review_fee_usd once for that sailing"; "a departure on or before the last covered day leaves the approval standing and owes nothing".
- **Passage B** — base and tool texts outside any `overwrite`:
  - parameter_schema `re_review_fee_usd`: "Fee for a re-review caused by a change of sailing";
  - parameter_schema `re_review_on_vessel_change`: "Whether an approval returns to review when the booking moves to another sailing";
  - lifecycle approved→under_review: "An approved acceptance is reopened after an amended declaration or a change of sailing";
  - the target tool `book_dg_re_review_fee_c46e22ec`: "charged when a dangerous-goods acceptance goes back to review because its booking moved to another sailing".
- The extended rule's own sentence "A change of sailing is read on the records by comparing the booking's current sailing with the acceptance's latest approval" asserts a definition. It does not revise those texts.
- **Demonstration 1 (probe W-a).** Task 0's world, with sibling `bfc0f29f…` approved on 2026-08-20. Its booking `29fcd508…` has no roll row and ETD 2026-09-25.
  - A: **75.00** re-review fee, and the decision is gated on it (script "N-1 W-a … rereview 75.0 | booking_charges rows for booking: []").
  - B: the booking never moved, so there is no re-review caused by a change of sailing, and the fee is 0.
- **Demonstration 2 (probe W-b).** The same sibling, approved 2026-09-11 and rolled on 2026-09-12 to a new vessel with ETD 2026-09-20.
  - A: **0.00**, and the approval stands.
  - B: the parameter is true and the booking moved to another sailing, so the acceptance returns to review with a 75.00 fee.
- In both situations the charter reaches two conclusions. Declaring an override made the replacement legal; it did not make the merged semantics unique.
- **Task bite:** evaluated in each task's file. On the scored holding of task 0, both readings coincide: the booking was rolled on 2026-09-10 after the 2026-09-03 approval, and 22 > 21.

**R2-N2 — observation: the inherited amendment gates are withdrawn from the fee without being named.**
- `amendment_deadline` and `amendment_count` apply to `dg_amendment_fee_charged` in the base. The extended text says they "are not part of this fee".
- A divergence needs a signed amendment that failed its admission gates. Such an amendment is not representable as a `signed` submission that the base would refuse to charge without inventing an outcome, and every gate holds in task 0. No demonstrable consequence, so this is an observation.

**R2-N3 — observation: the workflow `dataflow: []` omits real flows.**
- Step 0's `submission_id` feeds step 2's argument. Step 1's `under_review` status is read by step 4's `in_review`. Steps 2 and 3's rows feed step 4's gates.
- The zero_wait_proof justifies the empty list only by an argument-of-the-same-table criterion.
- No false world assertion remains, and there is no terminal-state consequence.

**R2-N4 — observation: a self-cancelling pointer in the remittance rule.**
- The rule says "a remittance smaller than the charges due is not governed here and is booked under dg_payment at the amount remitted". The dg_payment clause carrying "the amount remitted" is exactly the one this policy's overwrite supersedes.
- What survives is only the base formula `applied_amount: min(amount_usd, dg_charges)`, which yields the same figure.
- Same answer, so this is an observation.

**R2-N5 — observation: dead bindings.**
- `uplifted_per_container` and `per_container` in dg_ext_loading_surcharge are no longer consumed by `result`. Their `compute_basis` quotes are still accurate.

(End of the revision-2 charter-global section. Nothing in it derives from any round-2 GT.)

Freeze record: this section was hashed at 2026-09-13T06:18:05Z (`_difficulty.md` `95a5aaff…4d19`), before either round-2 task JSON was opened. The in-text "06:16Z" is an estimate.

### closing_checklist (revision 2)

Written 2026-09-13T06:21Z, after both round-2 reveals. **Outcome: the difficulty is still NOT closed.**

**Per-task verdicts**
| Task | Policy self-consistency | Problem tree | Unique solution | Verdict line (rev 2) |
| --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED — proof text only: the design_rationale rule↔compute sweep names non-existent re-review bindings | SOURCE-CHAIN RED — proof text only: the rationale asserts "skip [14] -> decision 'approved'" and an opening 'approved', both false on recomputation and contradicted by the task's own closure | PASS | **SOURCE-POLICY RED + SOURCE-CHAIN RED** |
| 1 | PASS | PASS | PASS | **PASS** |

**Did each round-1 RED close?**
- Task 0 round-1 #1 (F-1) and #2 (SOURCE-CHAIN): **closed in the artifacts**. Both edges now bear weight under the executable compute: skipping the re-review fee now gives `under_review`. Task 0's new REDs are regressions confined to its stale design_rationale sentences.
- Task 1 round-1 #1 (F-8, SOURCE-POLICY → SOURCE-TASK): **closed**. The single-value tool contracts were verified by replay.

**Charter-level status**
- F-1 through F-11: closed. F-12 → observation R2-N2. F-13: partly closed → observation R2-N3.
- **New charter-level RED R2-N1** (introduced by the re-review trigger redefinition). It bites neither task, and on task 0's scored holding it holds only by a 1-day margin. The redefinition collides with the unrevised parameter_schema (`re_review_fee_usd`: "Fee for a re-review caused by a change of sailing"; `re_review_on_vessel_change`: "…when the booking moves to another sailing"), with the lifecycle wording, and with the target tool's docstring ("because its booking moved to another sailing"). Probes W-a (no roll: 75.00 vs 0) and W-b (roll inside validity: 0.00 vs 75.00) give two conclusions each.
- New observations: R2-N2 through R2-N5.

**Step 4 items**
| Item | Status |
| --- | --- |
| Audit files one per task, plus this file | yes. The revision-2 sections are appended; round-1 text is untouched (hashes at the start of round 2: `709706…`, `d16116…`, `78913f…`). |
| Extended policies covered; scopes disjoint and complete | yes. `charter_scope` of the round-2 GT is unchanged from round 1 (4 + workflow; 3). |
| Exactly one workflow, claimed by task 0 | yes |
| Tools and GT closed; uuid8s independent | yes. The surcharge rows now each have one writer. |
| Each tree ≥ 2 prerequisites, ≥ 1 value_input, no cycle, all edges load-bearing | yes for both on recomputation. Task 0 has 2 value_input edges, both bearing weight; task 1 has 2/2. |
| Difficulty-wide graph is a DAG | yes |
| Gates on the final form | The coordinator's round-2 snapshot (all 7 exit=0) is on the current hashes: extended `ae78645f…`, tools `e2eaaa4e…`, `tasks/0.json` `80f92c55…`, `tasks/1.json` `a701f60f…`. These are unchanged at closing time. There is no final form yet, because RED items remain open. |

The cross-difficulty merge surface and the scenario-level checks are out of scope and were not run.

---

## revision_3

### charter_global_frozen (revision 3)

**Freeze metadata**
- Written 2026-09-13T06:40Z (estimate; the authoritative freeze is the hash record taken before the reveal). Auditor: the same.
- Earlier revisions are untouched. `_difficulty.md` hash at the start of round 3: `3b387be517e83482b475678203ffb7fb615cf404fc7b096da4f21b4ab26e4a82`.

**Inputs**
- `dg.extended.yaml` = `7f48b365db9edbaf34635f756770fb3cc52c3a2ef826a20204f35906dfbd0b60`. Changed from round 2.
- `task_tools.py` = `7f1ca962f8c8ea3ce930b127e3a0b8bd6b56cf0d074d6687a1d395169f932120`. Changed from round 2.
- Every charter-global section is re-derived in full.

**Masked views**
- `source_r3/0.masked.json` = `19deded9…45e2`. The world and persona are **rebuilt**.
- `source_r3/1.masked.json` = `71b097ae…eb8`. Unchanged.

**Other checks**
- Gate snapshot (coordinator): all 7 exit=0.
- Base copy: `diff <(head -n 861 …) products/dg.yaml` gives only `861d860 <`. Verbatim.

**contamination_disclosure**
- **Task 0:** its current world is new and I have not seen its current GT. The round-3 task-0 derivation is a genuine blind one. My round-1 and round-2 knowledge of the *old* task 0 (a different world) is disclosed, but it carries no value for this world.
- **Task 1:** its world and scored values are known to me from rounds 1 and 2, so its round-3 derivation is a recomputation, not a blind answer.
- Scratchpad reads: only `masked/dangerous_goods_desk/source_r3/` and my own `audit_dg_private/`. The script is `audit_dg_private/derive_r3.py`.

### policy_conflict_scan (revision 3)

**Surface changes**
- **Removed:**
  - `dg_ext_re_review_fee`;
  - tools `reopen_dg_review_a9bc3033` and `book_dg_re_review_fee_c46e22ec`.
  - `grep` confirms: no `re_review` text remains in the extended section, except the amendment-fee replacement's "A re-review fee, which this policy does not set, remains bookable only while …".
- **Added:**
  - `dg_ext_late_declaration_fee`: state_due, on `dg_late_declaration_fee_charged`, target tool `book_dg_late_declaration_fee_00f931c0`.
  - The decision's third gate is now "late declaration fee owed … is booked before its review is decided".

**Scope split derivable from the charter**
- The workflow `dg_wf_amended_declaration_redecision` has 4 steps:
  1. late fee (agent)
  2. sign (user)
  3. amendment fee (agent)
  4. decision + admin fee (agent)
- Its `computed_by` set is {dg_ext_late_declaration_fee, dg_ext_amendment_fee, dg_ext_review_decision, dg_ext_approval_admin_fee}.
- The remittance tree is {dg_ext_loading_surcharge, dg_ext_marine_pollutant_surcharge, dg_ext_remittance_application}.
- The 4 + 3 = 7 extended policies are disjoint and complete.
- The task tools split 4 (sign, late fee, amendment fee, decision) + 3 (loading, marine pollutant, payment) = 7, disjoint.
- **Exactly one workflow** is in the file.

**Overlap scan**
- `dg_late_declaration_fee_charged` has one owner.
- `dg_amendment_fee_charged` now has one owner (amendment_fee only).
- The decision and the admin fee still share the decision tool on different args.
- The two surcharge tools keep their single-value contracts.
- Cross-fire check: the task-0 policies evaluated on task 1's acceptance (`ea95e73c…`, loaded, late fee already booked) give 0.00 (script "T1 cross-fire"). The remittance tree has no task-0 object.

**Blueprint claim coverage (observation)**
- `dg_re_review_opened`, `dg_review_started`, `dg_rejected`, `dg_withdrawn`, `dg_withdrawal_fee_charged` and `dg_charge_waived` have no extended policy or task tool.
- The skill requires only extended-policy coverage.

### rule_compute_equivalence (revision 3)

| Policy | Result | Note |
| --- | --- | --- |
| dg_ext_late_declaration_fee (new) | equivalent, with one semantic note | Implemented: `signed_initial_declarations` (signed initial only); `signed_on` = LATEST `created_at`; `lead_days` = DAYS(signed_on, booking etd), defaulting to "not late" when a date is missing; `declaration_late` (< lead days); `accepted_in_review` (under_review); `already_charged` (any late-fee row on the acceptance); rate; RND. Note R3-O1: the rule measures from "the date on which the shipper signed it", but the compute reads `created_at`, which schema defines as "moment the submission was registered". No signing date exists in the schema. |
| dg_ext_amendment_fee | **NOT equivalent: R3-N1** | The rule: "The amendment fee is settled once for each chargeable signed amendment declaration … booked as one amendment_fee row that references that amendment submission". No binding checks whether a row for the latest signed amendment already exists; `result` depends only on `signed_before`, status and booking. |
| dg_ext_review_decision | equivalent | `initial_signed_on`, `lead_days`, `late_fee_owed` and `late_fee_settled` implement "Third, …". `result` gates on all three. The goods-fit list is unchanged. |
| dg_ext_approval_admin_fee | equivalent | unchanged |
| dg_ext_loading_surcharge | equivalent | `uplifted_per_container_x100` → `per_container_x10000` → `amount_in_cents` → `int(x+0.5)/100`. Every binding is consumed, so **R2-N5 is closed**. The F-7 probe still gives 388.13, and task 1 gives 1316.25. |
| dg_ext_marine_pollutant_surcharge | equivalent | unchanged |
| dg_ext_remittance_application | equivalent within its declared scope | unchanged compute |

### action_binding_and_uuids (revision 3)

**(target_tool, computes) pairs** — each claimed by exactly one policy:
- `(book_dg_late_declaration_fee_00f931c0, amount_usd)`
- `(book_dg_amendment_fee_40feddd0, amount_usd)`
- `(record_dg_review_decision_9aa03de9, decision / admin_fee_usd)`
- `(book_dg_loading_surcharge_44d311b2, amount_usd)`
- `(book_dg_marine_pollutant_surcharge_a7ecff71, amount_usd)`
- `(record_dg_payment_ee299820, amount_usd)`
- The sign tool is owner=user and computes nothing.

**Late-fee tool** (`task_tools.py:46-75`)
- It hard-codes `event_type=dg_late_declaration_fee_charged` and `charge_code=late_declaration_fee`, and it has no guard.
- Its id is `make_id("dgl_", dg_id, booking_id, submission_id, "late_declaration_fee", amount_usd)`, a different part list from the amendment-fee id, so the two cannot collide.
- Its docstring ("a shipper's declaration that was signed after the lead time but accepted for the sailing") admits only this policy's reading.

**Other tools**
- No tool writes another policy's row.
- The remaining docstrings are unchanged from round 2.
- The re-review tool whose docstring conflicted in R2-N1 no longer exists.

**UUID8s — PASS.**
- The seven suffixes are `eb5287cf`, `00f931c0`, `40feddd0`, `9aa03de9`, `44d311b2`, `a7ecff71` and `ee299820`.
- They are pairwise distinct, share no stem or sequence, and each is frozen on its own tool. `00f931c0` is new, with no relation to the retired `a9bc3033` and `c46e22ec`.

### prerequisite_graph (revision 3)

**Edges**
- review_decision → dg_ext_amendment_fee: value_input, gate `amendment_fees_settled` (the binding exists). The `policy_source` is verbatim in the rule.
- review_decision → **dg_ext_late_declaration_fee**: value_input, gate `late_fee_settled` (the binding exists).
  - `policy_source`: "a late declaration fee owed on the acceptance's signed initial declaration is booked before its review is decided". It is verbatim in the rule, after "Third, ".
  - `condition` says "is on its account before", which is equivalent to "booked before".
  - `effect` is accurate.
- remittance → loading and remittance → marine pollutant: unchanged, and PASS.

**Graph checks**
- Every `prerequisite` field is filled, and the workflow's is `[]`.
- The graph is acyclic, and no authoring-viewpoint phrasing appears. **PASS.**

### override_declarations (revision 3)

**dg_ext_amendment_fee**
- The `replaced_by` now also restates the re-review half of the superseded sentence ("A re-review fee, which this policy does not set, remains bookable only while the acceptance is submitted, under_review or approved"). The merged semantics are unique.
- The inherited amendment gates are now said to "continue to govern both the signed amendment and its fee as inherited eligibility; this policy adds no condition to them". **R2-N2 closed.**

**dg_ext_late_declaration_fee (new)**
- The `superseded_clause` "A late but accepted declaration is charged late_declaration_fee_usd once, referencing the late submission;" is a verbatim substring of base dg_declaration_and_review.
- The replacement proxies "accepted" as "review having started". This is consistent with the base, where an accepted declaration starts review and one signed past the deadline "stays submitted".
- Remaining base sentences:
  - The on-time lead rule is followed (DAYS ≥ lead days ⇔ "signed no later than … days before the booking's etd_date").
  - The late-acceptance deadline is inherited (proxied by status).
  - "A late declaration fee may be booked only while the acceptance is submitted or under_review" is followed, narrowed to under_review as declared.
- Residue (observation **R3-O2**): the base "A late submission is charged at most once" and the base dedup `late_fee_once` (object_bindings `{submission_id}`) are per submission. The extended text is per acceptance ("when a late_declaration_fee row is already on the acceptance's account nothing further is charged") and judges only the signed initial declaration. The two granularities diverge only on an acceptance that carries more than one late signed declaration eligible under the base.

**dg_ext_remittance_application**
- The `superseded_clause` is now just "A remittance is applied to one acceptance,". The rest of the dg_payment sentence ("written with … the amount remitted; it may not exceed … not booked") survives.
- The rule's pointer "booked under dg_payment, which writes it with the amount remitted" now lands on a surviving clause. **R2-N4 closed.**

**dg_ext_review_decision**
- The overwrite is unchanged. The third gate is new extended procedure; it narrows no base gate.

### findings (revision 3)

**Status of the round-2 charter findings**
| Round-2 id | Revision-3 status | Evidence |
| --- | --- | --- |
| **R2-N1** (redefined re-review trigger vs "booking moved" texts) | **closed by removal** | The policy dg_ext_re_review_fee and both of its tools are deleted. The base dg_amendment re-review sentence, the parameter_schema entries and the lifecycle wording are again the only re-review text, and they agree with one another. No task writes a re-review fee. |
| R2-N2 (amendment gates withdrawn from the fee) | closed | See override_declarations. |
| R2-N3 (empty dataflow) | observation, reduced | The zero_wait_proof now names the three real hand-offs. See R3-O3. |
| R2-N4 (self-cancelling pointer) | closed | The superseded clause is narrowed. |
| R2-N5 (dead bindings) | closed | All loading bindings are consumed. |

The round-1 F-series stays closed. F-1 and F-3 are moot because their policy is gone, and F-8 and F-10 were re-checked on the reworked tools.

**R3-N1 — SOURCE-POLICY RED (check 2; new in revision 3; latent since revision 1, first exhibited by the rebuilt task-0 world): "settled once" in dg_ext_amendment_fee has no compute binding.**
- Passage A, the rule: "The amendment fee is settled once for each chargeable signed amendment declaration … booked as one amendment_fee row that references that amendment submission".
- Passage B, the compute: `signed_before = signed_amendments_now - 1`; `result = RND(tariff_fee if acceptance_open and ahead_of_loading else 0, 2)`. Nothing reads existing `amendment_fee` rows.
- **Demonstration on task 0's own opening world:**
  - The latest signed amendment is `9474bb1c…` (signed 2026-09-14 17:45). It is already settled by `dg_ledger.890e9789…` (amendment_fee 225.00, `submission_id` = 9474bb1c…).
  - Compute: **225.00** is due (script "T0 opening dg_ext_amendment_fee 225.0").
  - Rule: that amendment has been settled once, so **nothing** is due.
  - Same situation, two conclusions.
- Why it was not exhibited earlier: in rounds 1 and 2 the category allowance (F&C, free 1) made the latest signed amendment free at the opening. So the gap was latent, and I did not flag it.
- Task bite: evaluated in `0.md` rev 3.

**R3-O1 — observation: the "signing date" is read from `created_at`.**
- The late-fee rule measures lead time "from the date on which the shipper signed it". The compute uses `created_at`, which schema defines as the "moment the submission was registered".
- The base lifecycle registers the initial declaration at application, "awaiting the shipper's signature".
- In task 0's world the signed initial `5d646ae2…` is a separate submission created 2026-09-14 15:30, and no other date for its signature exists anywhere in the records. So there is no competing value.

**R3-O2 — observation: late-fee dedup granularity.**
- The extended text is per acceptance and initial-only; the base is per late submission (see override_declarations).
- There is no divergence in any task world: task 0 has one signed initial declaration, and task 1's acceptance is already charged and loaded.

**R3-O3 — observation: the zero_wait_proof's argument for `dataflow: []`.**
- It claims "a link may name only a field of the table the producing step's event targets and pass it into an argument of the later step".
- The round-1 revision of this same charter used a `state_effect` link with `consumer_bindings: []` and `establishes_gates`, i.e. a link that passes no argument. So the claim describes the format more narrowly than the charter's own history.
- There is no world assertion and no terminal consequence.

**R3-O4 — observation: the workflow now has 4 write steps** (3 agent + 1 user). This meets "at least 4 non-trivial synchronous write steps", counting the user step, with no margin.

(End of the revision-3 charter-global section. Nothing in it derives from any round-3 GT.)

Freeze record: hashed at 2026-09-13T06:44:50Z (`_difficulty.md` `a74a7a47…f7e`), before either round-3 task JSON was opened.

### closing_checklist (revision 3)

Written after both round-3 reveals. **Outcome: the difficulty is still NOT closed.** Task 0 carries a proof-text SOURCE-CHAIN RED, and the charter carries R3-N1.

**Per-task verdicts**
| Task | Policy self-consistency | Problem tree | Unique solution | Verdict line (rev 3) |
| --- | --- | --- | --- | --- |
| 0 (rebuilt; genuine blind derivation) | PASS (R3-N1 does not bite) | SOURCE-CHAIN RED — proof text only: `prerequisite_closure.edges[0].why_false` says the acceptance's account "holds no row at all", which `dg_ledger.890e9789…` refutes | PASS (blind = GT; terminal 975.00) | **SOURCE-CHAIN RED** |
| 1 | PASS | PASS | PASS | **PASS** |

**Did each round-2 RED close?**
- Task 0 rev-2 #1 (stale load-bearing figures) and #2 (stale sweep): **closed**. The rationale was rewritten for the rebuilt world, and every figure and binding name was verified.
- Charter R2-N1: **closed by removal** of dg_ext_re_review_fee and both of its tools.
- R2-N2 and R2-N4: closed. R2-N5: closed. R2-N3: reduced to observation R3-O3.

**Regression check**
- Task 1's world, values, tools and hash are unchanged (`ea26b4e2…`).
- The round-1 F-series stays closed on the reworked charter: the F-7 probe gives 388.13, the F-8 single-value contracts hold, and the F-10 decision tool writes no row at 0.00.
- **New charter defect R3-N1.** The amendment fee's "settled once" has no compute binding. It was latent since revision 1 and is first exhibited by the rebuilt task-0 world: the compute says 225.00 for the already-settled `9474bb1c…`, while the rule says nothing is due. It does not bite either scored solution.

**Step 4 items**
| Item | Status |
| --- | --- |
| Audit files | `0.md`, `1.md` and `_difficulty.md` carry revisions 1–3. Earlier text is untouched; the start-of-round-3 hashes were `f88d0489…`, `c37e02df…` and `3b387be5…`. |
| Coverage / disjointness of the new split | GT `charter_scope`: task 0 = {dg_ext_late_declaration_fee, dg_ext_amendment_fee, dg_ext_review_decision, dg_ext_approval_admin_fee} + the workflow, with 4 tools; task 1 = {loading, marine pollutant, remittance}, with 3 tools. The union covers all 7 extended policies and all 7 task tools, and the scopes are pairwise disjoint. This matches the pre-reveal partition. |
| One workflow, one claimant | yes. `dg_wf_amended_declaration_redecision` is the only workflow and is claimed only by task 0. The GT tool sequence equals the workflow steps (late fee, sign, amendment fee, decision). |
| uuid8s | 7 tools, independent (action_binding_and_uuids rev 3) |
| Trees | Task 0: 2 value_input edges, both load-bearing, with the late-fee edge unmet on the raw seed. Task 1: 2 value_input edges, both load-bearing. The difficulty-wide graph is acyclic. |
| Gates on the final form | The coordinator's round-3 snapshot (all 7 exit=0) is on extended `7f48b365…`, tools `7f1ca962…`, `tasks/0.json` `ad9289d7…` and `tasks/1.json` `10fa132f…`. There is no final form yet, because a RED remains open. |

The cross-difficulty merge surface and the scenario-level checks are out of scope and were not run.

---

## revision_4

### charter_global_frozen (revision 4)

**Freeze metadata**
- Written before any round-4 task GT was opened; the authoritative freeze is the pre-reveal hash record. Auditor: the same.
- Earlier revisions are untouched. Hash at the start of round 4: `77d5d320d7a26ed1a31569ea1bd8b19ac1d67df442cad0fb2b0c364e8ee083bb`.

**Inputs**
- `dg.extended.yaml` = `7064c66b5b56568dbb97b050a0a30fe23005acc4fc63138bcffbac6d0d9eb112`. **Changed**, so the charter-global sections are re-derived below.
- `task_tools.py` = `7f1ca962f8c8ea3ce930b127e3a0b8bd6b56cf0d074d6687a1d395169f932120`. **Unchanged** since round 3, so the revision-3 **action_binding_and_uuids** section is **carried forward by reference**. The grounds are the identical tools hash, plus an unchanged `target_tool` set in the charter: every policy's `target_tool` and every workflow `tool` line is byte-identical to round 3.

**Masked views**
- `source_r4/0.masked.json` `19deded9…45e2` and `source_r4/1.masked.json` `71b097ae…eb8`. Both are byte-identical to round 3.

**Other checks**
- Gate snapshot: all 7 exit=0.
- Base copy: still verbatim (`861d860 <` only).

**contamination_disclosure**
- The round-3 GT of both tasks is known to me. Both round-4 derivations are recomputations on unchanged worlds (`audit_dg_private/derive_r4.py`), not blind answers.
- Round-4 GT has not been seen.

### What changed in the charter

Read in full and compared with the round-3 text.

| Block | Change |
| --- | --- |
| dg_ext_amendment_fee | **Rule and compute reworked.** Signed amendments are "taken in the order in which they were signed: the first free_amendments_per_acceptance of them are free and every later one is chargeable". "Each chargeable amendment is settled by one amendment_fee row: while the acceptance's account holds fewer amendment_fee rows than it has chargeable amendments, the amendment not yet settled — the latest signed one — owes … amendment_fee_usd in full …; when every chargeable amendment already has its row, nothing further is owed". The compute is now `chargeable_amendments = MX(signed − free, 0)`, `amendment_fees_booked`, `unsettled_amendment = chargeable > booked`, `tariff_fee = 0 if not unsettled else rate`. |
| dg_ext_late_declaration_fee | The judged declaration is "the latest such submission when more than one exists". "Amendment declarations are held to the amendment deadline of dg_amendment instead and never carry a late declaration fee". The signing date "is the date its signed submission was registered, the created_at of that submission, which is the only date the declaration file records for a signature". Dedup: "a late submission is charged at most once: when a late_declaration_fee row already references the judged declaration, nothing further is charged". The compute adds `judged_declaration` and filters `already_charged` on it. |
| dg_ext_review_decision | The third gate now reads "settled once a late_declaration_fee row referencing that signed initial declaration is on the acceptance's account". `late_fee_settled` counts late rows with `submission_id` = the judged declaration. The signing date is named as `created_at`. |
| Workflow | `zero_wait_proof` rewritten: it now names both dataflow kinds (`object_binding`, `state_effect`) and states why neither fits. The steps, order_rationale and `prerequisite` are unchanged. |
| dg_ext_approval_admin_fee, dg_ext_loading_surcharge, dg_ext_marine_pollutant_surcharge, dg_ext_remittance_application | unchanged |

### policy_conflict_scan (revision 4)

- Subjects, owners and the scope split are unchanged from revision 3:
  - {late fee, amendment fee, decision, admin fee} + the one workflow;
  - {loading, marine pollutant, remittance}.
  - 7 policies and 7 tools, disjoint and complete. Exactly one workflow.
- The late-fee policy and the decision gate now use the **same** settlement key (the judged submission).
  - Probe: a late-fee row that references the *returned* initial `82afc51b…` leaves the fee owed (450.00) **and** the gate unsettled. The two agree (script "probe: late row on returned initial").
- The amendment-fee policy and the decision's `amendment_fees_settled` now use the same count test (`chargeable` vs `booked`), so they cannot disagree.
- Cross-fire on task 1's acceptance: the late fee and the amendment fee both give 0.00. Nothing changed.

### rule_compute_equivalence (revision 4)

| Policy | Result | Note |
| --- | --- | --- |
| dg_ext_amendment_fee | **equivalent** | Every new rule sentence has a binding and vice versa. Equivalent to base "free while dg_msr_signed_amendments is below free_amendments_per_acceptance" (first-N-free ⇔ count-before < N). On task 0's opening world the fee is now **0.00**: chargeable 1, booked 1 (`890e9789…`). **R3-N1 closed.** Residue R4-O1 (backlog wording). |
| dg_ext_late_declaration_fee | equivalent | `judged_declaration` (LATEST submission_id by created_at), `already_charged` keyed to it, and the signing date declared as `created_at`. **R3-O1 and R3-O2 closed.** |
| dg_ext_review_decision | equivalent | `late_fee_settled` is keyed to the judged submission. The `inputs.history` entry `{dg_ledger, count, filters: {event_type: dg_late_declaration_fee_charged}}` still lacks the submission filter the compute applies (observation R4-O2: metadata only). |
| other four | equivalent | unchanged |

### prerequisite_graph (revision 4)

- The edges, kinds, gates and `policy_source` strings are unchanged. The strings are verbatim; the amendment and late-fee sentences are still present in the reworked rule.
- The late-fee edge's `effect` ("puts a late_declaration_fee row on the account, so late_fee_settled turns true") is still true, as long as the row references the judged declaration, which the tool's `submission_id` argument carries.
- The graph is acyclic. **PASS.**

### override_declarations (revision 4)

**dg_ext_amendment_fee**
- The superseded clause and its replacement are unchanged.
- The new counting sentences follow base "An amendment is free while dg_msr_signed_amendments is below free_amendments_per_acceptance and otherwise costs amendment_fee_usd, referencing the amendment submission". No base sentence is handled differently.

**dg_ext_late_declaration_fee**
- The declared overwrite is unchanged.
- "a late submission is charged at most once" now mirrors the base sentence and the base dedup `late_fee_once` (keyed on `submission_id`).
- Restricting the fee to the signed initial declaration ("Amendment declarations are held to the amendment deadline of dg_amendment instead") makes explicit the base split between dg_declaration_and_review and dg_amendment. That base split is not overridden.

**Others** — unchanged.

### findings (revision 4)

**Status of the round-3 charter findings**
| Round-3 id | Revision-4 status | Evidence |
| --- | --- | --- |
| **R3-N1** (SOURCE-POLICY RED: "settled once" not in compute) | **closed** | Count-based settlement is in both rule and compute. Task 0's opening world gives 0.00 for the already-settled `9474bb1c…`, and 225.00 after the new signature. |
| R3-O1 (signing date read from `created_at`) | closed | Declared in the rule. |
| R3-O2 (dedup granularity) | closed | Per judged submission; amendments excluded explicitly. |
| R3-O3 (zero_wait_proof format claim) | closed | Both link kinds are now addressed. Its supporting claims are true: the `dg_approved` subject has no base eligibility gate in dg_declaration_and_review, and `gross_weight_kg` is read by no base gate of `dg_amendment_fee_charged` (`amendment_deadline` reads `bookings.cargo_cutoff`, `amendment_count` reads submissions, `fee_while_open` reads status). |
| R3-O4 (4 write steps) | unchanged observation | The minimum is met. |

**R4-O1 — observation: the amendment-fee backlog wording.**
- With more than one unsettled chargeable amendment, "the amendment not yet settled — the latest signed one — owes" names only the latest. Repeated evaluation settles the backlog one row at a time: probe with 1 chargeable and 0 booked gives 225.00.
- Neither task world has a backlog.

**R4-O2 — observation: stale `inputs.history` metadata** in dg_ext_review_decision (no submission filter on the late-fee count). The compute is authoritative, and there is no value consequence.

**No new RED at charter level.**

(End of the revision-4 charter-global section. Nothing in it derives from any round-4 GT.)

Freeze record: hashed at 2026-09-13T06:56:23Z (`_difficulty.md` `83dbae64…c77e`), before either round-4 task JSON was opened.

### closing_checklist (revision 4)

Written 2026-09-13T06:59Z, after both round-4 reveals. **Outcome: all three relationships PASS for both tasks. The difficulty passes the source-layer audit.**

**Per-task verdicts**
| Task | Policy self-consistency | Problem tree | Unique solution | Verdict line (rev 4) |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | **PASS** |

**Did each round-3 RED close?**
- Charter **R3-N1** (SOURCE-POLICY): **closed**. The amendment fee's count-based "settled once" is in both rule and compute. Task 0's opening world gives 0.00 for the already-settled `9474bb1c…`; the handling moment gives 225.00.
- Task 0 rev-3 #1 (SOURCE-CHAIN, proof text): **closed**. The closure's edge-1 `why_false` and its evidence now state `890e9789…` correctly.
- R3-O1, R3-O2 and R3-O3 are closed. R3-O4 is kept, with its reason.

**Regression check**
- The worlds, the GT write sequences and the terminal hashes are unchanged from round 3: task 0 `fc721dd5…`, 975.00; task 1 `ea26b4e2…`, 0.00.
- The tools are byte-identical.
- The round-1 and round-2 closures still hold on this charter: the F-7 probe gives 388.13; F-8's single-value contracts are intact; the F-10 decision tool writes no row at 0.00; the re-review surface is gone.
- A word-for-word sweep of every world-asserting proof sentence in both tasks (design_rationale, prerequisite_closure, factor traces, solvability_contract) found **no false world assertion**. The details are in `0.md` and `1.md` rev 4.
- New items are observations only:
  - R4-O1: backlog wording;
  - R4-O2: stale `inputs.history` metadata;
  - task 0: an incomplete evidence list on `late_fee_once`;
  - task 1: a mis-pointed `reference_once` evidence binding.

**Step 4 items**
| Item | Status |
| --- | --- |
| Audit files, one per task, plus this file; old revisions traceable; each comparison carries PASS | yes. `0.md`, `1.md` and `_difficulty.md` hold revisions 1–4 with the earlier text untouched (start-of-round-4 hashes `112a0c54…`, `f9c956cf…`, `77d5d320…`). Both revision-4 comparisons carry PASS. |
| Extended policies fully covered; scopes pairwise disjoint and spanning whole trees | yes. Task 0 = {dg_ext_late_declaration_fee, dg_ext_amendment_fee, dg_ext_review_decision (root), dg_ext_approval_admin_fee} + the workflow. Task 1 = {dg_ext_loading_surcharge, dg_ext_marine_pollutant_surcharge, dg_ext_remittance_application (root)}. The union is all 7; the intersection is empty. |
| Exactly one workflow, claimed by exactly one task | yes. `dg_wf_amended_declaration_redecision`, task 0. The GT tool sequence equals the workflow steps: late fee → sign (user) → amendment fee → decision. |
| Task tools and GT closed; independent frozen uuid8 per tool | yes. 7 tools (4 + 3); suffixes `eb5287cf`, `00f931c0`, `40feddd0`, `9aa03de9`, `44d311b2`, `a7ecff71`, `ee299820`. |
| Each tree has ≥ 2 prerequisites and ≥ 1 value_input edge, with no cycle; the difficulty-wide graph is a DAG | yes. Task 0: 2 value_input edges, both load-bearing, and the late-fee edge is unmet on the raw seed. Task 1: 2 value_input edges, both load-bearing and unmet on the raw seed. There are two disjoint stars and no cross-task edge. |
| Instantiation-stage gates on the final form | The coordinator's round-4 gate block (all 7 exit=0; check_traceability deferred until KB publication) was run on extended `7064c66b…` and tools `7f1ca962…`. Those hashes, and the revealed `tasks/0.json` `4412827f…` and `tasks/1.json` `96c048fc…`, are unchanged at closing (checked 2026-09-13T06:58:46Z). |

**Open observations, not grounds for rework**
- R3-O4: the workflow has exactly 4 write steps.
- R4-O1 and R4-O2.
- The two solvability evidence-pointer notes in the task files.
- The amendment-fee edge of task 0 is unmet only after the customer's own amendment.
- The tools are unguarded, so some prerequisite orderings cannot be seen in the terminal DB.

The cross-difficulty merge surface, the scenario-level checks and the KB audit are out of scope and were not run.

---

## revision_5

### charter_global_frozen (revision 5)

**Freeze metadata**
- Written before any round-5 task GT was opened; the authoritative freeze is the pre-reveal hash record. Auditor: the same.
- Earlier revisions are untouched. Hash at the start of round 5: `fab0ed1611d27c5c479e78fb3fd5a6bc3aa6ba1e0f8bc49a404164e7293b9822`.

**Inputs**
- `dg.extended.yaml` = `9970e3c42c8cf60876538d14e8aa8429f2aea5cebd55aaf0d7256c71b273d0c0`. Changed.
- `task_tools.py` = `3306fb4b5941aca6488ad428b2520b027ef54eed3568ae3f3efc2b2036ca884c`. Changed.
- Both shared inputs moved, so every section is re-derived; nothing is carried by hash.

**Masked views**
- `source_r5/0.masked.json` `19deded9…45e2` and `source_r5/1.masked.json` `71b097ae…eb8`. Both are byte-identical to rounds 3 and 4.

**Other checks**
- Gate block (coordinator, now including TRACEABILITY OK): all exit=0.
- Base copy: verbatim (`861d860 <` only).

**contamination_disclosure**
- The round-4 GT of both tasks is known to me. The round-5 derivations are recomputations.
- The pre-reveal probe `audit_dg_private/probe_r5.py` runs the **real** reworked tools on the masked task-0 world and on a constructed variant. It reads no GT.

**Round context.** No RED was open after revision 4. This round verifies a source change made after the coordinator's post-KB traceability failure on task 0: a scored id argument had no agent-reachable source.

### What changed

| Artifact | Change |
| --- | --- |
| `task_tools.py` → `book_dg_amendment_fee_40feddd0` | The `submission_id` parameter is **removed**. The tool now resolves the attachment itself (`task_tools.py:99-101`): `signed = ctx.find("dg_declaration_submissions", dg_id=dg_id, submission_type="amendment", outcome="signed")`, then `latest = max(signed, key=created_at)`, then `sub_id = latest.submission_id` (or "" when there is none). The row id is `make_id("dgl_", dg_id, booking_id, sub_id, amount_usd)`. The docstring: "attached by this action to the acceptance's most recently signed amendment declaration". |
| other six tools | unchanged (the same signatures, bodies and `make_id` parts as round 4) |
| `dg.extended.yaml` | Only the workflow `zero_wait_proof` changed. It now says the signed amendment "is found and attached by the amendment-fee action … which ties its charge to the acceptance's most recently signed amendment declaration". Every policy `rule`, `compute`, `compute_basis`, `overwrite` and `prerequisite` is identical to round 4: the same line offsets, and every compute binding was listed and compared. |

### policy_conflict_scan / rule_compute_equivalence / prerequisite_graph / override_declarations (revision 5)

- **Policies:** unchanged from revision 4, which was re-verified by listing every compute binding. All four conclusions of `_difficulty.md` § revision_4 still hold:
  - scope split 4 + workflow / 3; exactly one workflow;
  - rule ↔ compute equivalent for all 7 policies;
  - the graph is acyclic, with `policy_source` verbatim;
  - no undeclared override.
- **Workflow zero_wait_proof:** true against the tool. The signed amendment is found by the fee action and not passed as an argument. No step waits.

### action_binding_and_uuids (revision 5)

**Unchanged parts**
- The (target_tool, computes) pairs and the seven uuid8 suffixes are unchanged, and the uuid8s are still independent.
- The late-fee, decision, loading, marine-pollutant, payment and sign contracts are unchanged.

**The amendment-fee tool now performs an object-binding judgement.**
- It reads the declaration history and chooses which submission the charge attaches to. It judges no eligibility and computes no amount: the amount is still passed in, and the tool never refuses.
- But the module's own docstring still says "The tools never judge eligibility, never aggregate history and never compute a charge: every amount, decision and particular is decided by the agent". Selecting `max(created_at)` over the history is an aggregation, and the attached particular is no longer decided by the agent.
- The tool's reading ("most recently signed amendment") equals the policy's object ("the amendment not yet settled — the latest signed one") **only when at most one chargeable amendment is unsettled**. See R5-N1.

### findings (revision 5)

**R5-N1 — SOURCE-POLICY RED (check 3; a regression introduced by the round-5 tool change): the amendment-fee tool cannot settle a second unsettled chargeable amendment.**
- **Passage A** — the policy dg_ext_amendment_fee, unchanged: "Each chargeable amendment is settled by one amendment_fee row: while the acceptance's account holds fewer amendment_fee rows than it has chargeable amendments, the amendment not yet settled — the latest signed one — owes the category's amendment_fee_usd in full"; "a chargeable amendment is booked as one amendment_fee row that references that amendment submission". The decision gate requires `amendment_fees_booked >= chargeable_amendments`.
- **Passage B** — the tool contract of the policy's `target_tool`: "The charge is attached by this action to the acceptance's most recently signed amendment declaration". The body always takes `max(created_at)`, and the row id includes that `sub_id`.
- **Demonstration** (`probe_r5.py`, real tools). Task 0's world without row `890e9789…`, so `9474bb1c…` is chargeable but unsettled. Toxics, allowance 0. The customer then signs the requested amendment, giving 2 chargeable and 0 booked. A policy-following desk:
  - Pass 1: the policy says 225.00 is owed. The tool attaches to `dgs_b97d849e16ef` (the newest) and writes row `dgl_a1a666f0673f`.
  - Pass 2: the policy says 225.00 is still owed, because 2 chargeable > 1 booked, and the unsettled amendment is `9474bb1c…`. The tool again attaches to `dgs_b97d849e16ef` and computes the **same** row id. `erlbench/db.py` `insert` is idempotent (a no-op on an existing id), so no row is written, yet the tool still adds 225.00 to `charges_due_usd` (`task_tools.py:108-109`).
  - Pass 3 repeats pass 2.
  - End state: one amendment_fee row; `charges_due_usd` **1125.00** against a ledger sum of **675.00**, which breaks the schema identity "identically the sum of dg_charges deltas". The decision compute stays **`under_review`**.
- Two passages, one situation. The policy requires a second row attached to `9474bb1c…`. The tool contract attaches it to the newest amendment and can never produce it. The policy's terminal state is unreachable.
- In round 4 the same backlog was settleable, because the agent passed `submission_id` (R4-O1). **R4-O1 escalates into this finding.**
- **Task bite:** evaluated per task. In both scored worlds at most one chargeable amendment is unsettled at any moment.

**R5-O1 — observation: a timestamp-tie edge.**
- `max(created_at)` is ambiguous when two signed amendments share a `created_at`, for example two signatures in one consultation, where `ctx.now()` is frozen. The first-encountered row wins.
- Neither task has two signatures in one consultation.

**R5-O2 — observation: traceability history.**
- The round-4 gold's `submission_id` (`dgs_b97d849e16ef`) was an output of the user-owned signing tool. At the source layer it was also reachable through the share tool `find_dg_declaration_submissions(dg_id=…)` after the signature.
- The coordinator's traceability red concerned the GT trace, which had no read carrying that id. The round-4 PASS stands on the source layer, and the fix chosen (moving resolution into the tool) is what introduces R5-N1.
- I report this and do not arrange any fix.

(End of the revision-5 charter-global section. Nothing in it derives from any round-5 GT.)

Freeze record: hashed at 2026-09-13T07:36:55Z (`_difficulty.md` `d76b4c7e…55e3`), before either round-5 task JSON was opened.

### closing_checklist (revision 5)

Written after both round-5 reveals. **Outcome: the difficulty is NOT closed.** The charter carries R5-N1, and task 1 carries a proof-text SOURCE-TASK RED.

**Per-task verdicts**
| Task | Policy self-consistency | Problem tree | Unique solution | Verdict line (rev 5) |
| --- | --- | --- | --- | --- |
| 0 | PASS (R5-N1 does not bite: at most one unsettled chargeable amendment at any moment) | PASS | PASS (GT = recomputation; hash `fc721dd5…` unchanged) | **PASS** |
| 1 | PASS | PASS | SOURCE-TASK RED — proof text only: `evaluation_criteria[8/10/12].argument_uniqueness_tracing.dg_id` says "no other acceptance exists for the customer", but `dg_acceptances.dd7e9040…` exists (closed) | **SOURCE-TASK RED** |

**Round-4 REDs:** none were open.

**New defects and regressions in this round**
- **R5-N1** (SOURCE-POLICY RED, charter-level): a regression introduced by the amendment-fee tool change.
  - The tool's resolution ("most recently signed amendment") replaces the agent-supplied `submission_id`. When two chargeable amendments are unsettled, the policy's second required row can never be written: identical row id, idempotent insert, yet `charges_due_usd` inflates (1125.00 vs a ledger sum of 675.00), and the decision stays `under_review`.
  - This was demonstrated with the real tools (`probe_r5.py`). In round 4 the same backlog was settleable.
  - It bites neither scored solution.
- The tool change also makes the module docstring's "never aggregate history … every … particular is decided by the agent" inaccurate for this tool.
- **Task 1 proof-text RED**, above. It was found by a field I had not swept before (see the disclosure below).

**Nothing else regressed**
- Every policy rule and compute is identical to round 4.
- The six other tools are unchanged.
- Both terminal hashes are unchanged: `fc721dd5…` (975.00) and `ea26b4e2…` (0.00).
- The closures from rounds 1–4 stand: F-7 388.13, the F-8 single-value contracts, the F-10 no-row-at-0.00 decision tool, R3-N1 count-based settlement, and the task-0 closure edge 1.

**Audit-gap disclosure.**
- My closing checklist of revision 4 said a word-for-word sweep found "no false world assertion". That sweep covered design_rationale, prerequisite_closure, factor traces and solvability_contract, but **not** `evaluation_criteria[*].argument_uniqueness_tracing`, which the skill lists among proof fields.
- The false task-1 sentence reported in this revision may therefore have been present in earlier rounds undetected.
- The revision-4 text is left untouched, as the re-audit rules require; this paragraph corrects its scope.

**Step 4 items**
| Item | Status |
| --- | --- |
| Scope | Unchanged. Task 0 has {late, amendment, decision, admin} + the workflow and 4 tools; task 1 has {loading, marine pollutant, remittance} and 3 tools. The union is 7 / 7; the scopes are disjoint. There is one workflow, claimed by task 0. |
| Trees | Both have 2 value_input edges, both load-bearing, and the graph is a DAG. Task 0's problem tree still has no tool judging a prerequisite; the amendment-fee tool resolves an object, not a prerequisite. |
| uuid8s | unchanged; independent |
| Gates on the final form | The coordinator's round-5 block (including TRACEABILITY OK) is on extended `9970e3c4…` and tools `3306fb4b…`, which are unchanged at closing, with `tasks/0.json` `1a519f42…` and `tasks/1.json` `576daeb1…`. There is no final form yet, because a RED remains open. |

The cross-difficulty merge surface and the scenario-level checks are out of scope and were not run.

---

## revision_6

### charter_global_frozen (revision 6)

**Freeze metadata**
- Written before any round-6 task GT was opened; the authoritative freeze is the pre-reveal hash record. Auditor: the same.
- Earlier revisions are untouched. Hash at the start of round 6: `fbc5997f2a4d46ef8a91050250525b03dca03d041ce6fbf9392f0b75f6148125`.

**Inputs**
- `dg.extended.yaml` = `9003f0bff1d2b44b149115d3653b5d86a6403aef647d6291ea431f88f2add6ee`. Changed.
- `task_tools.py` = `9c5e47e2dafc887c274656d7570cd230b0e59bec7f361bb865053fa9bac5e369`. Changed.
- Both are re-derived. Private copies are kept in `audit_dg_private/r6_copy/` for future diffs.

**Masked views**
- `source_r6/0.masked.json` `19deded9…45e2` and `source_r6/1.masked.json` `71b097ae…eb8`. Both are byte-identical to round 5.

**Other checks**
- Gate block, including TRACEABILITY: all exit=0.
- Base copy: verbatim.

**contamination_disclosure**
- The GT of both tasks is known to me from earlier rounds, so the derivations are recomputations.
- The pre-reveal probe `audit_dg_private/probe_r6.py` runs the real reworked tools on the masked task-0 world and on constructed variants. It reads no GT.

### What changed

| Artifact | Change |
| --- | --- |
| dg_ext_amendment_fee **rule** | The object sentence now reads: "while the acceptance's account holds fewer amendment_fee rows than it has chargeable amendments, one further row is owed at the category's amendment_fee_usd in full, never pro rata, and it references the most recently signed amendment that no amendment_fee row references yet, so that a backlog of unsettled amendments is settled one row per amendment". `compute_basis.unsettled_amendment` / `fee_rate` were re-quoted to match. **The `compute` is unchanged** (the same 11 bindings as rounds 4 and 5). |
| workflow `zero_wait_proof` | It names the attachment as "the acceptance's most recently signed amendment declaration that no amendment-fee charge references yet". |
| other six policies | Unchanged. Each policy offset shifted by exactly +1 line, following the one-line growth of the amendment rule. The compute bindings were re-listed and match revisions 4 and 5. |
| `book_dg_amendment_fee_40feddd0` | Attachment: `charged` = the `submission_id`s already on amendment_fee rows of this acceptance. `signed` = the signed amendments not in `charged`. `latest` = `max` by (`created_at`, `submission_id`), so a tie goes to the higher reference. The row is written on that `sub_id`, or "" when none is left. |
| all six writing task tools (late fee, amendment fee, decision/admin fee, loading, marine pollutant, payment) | A repeat guard: `repeat = bool(ctx.find("dg_ledger", dg_event_id=rid))`, and the balance moves by `0 if repeat else amt`. The docstrings add "A repeated identical call writes nothing further and leaves the balance unchanged". The decision tool says "A repeated identical approval writes no second charge". |
| module docstring | It now says one particular is resolved by a tool (the amendment-fee attachment), "a deterministic look-up of the declaration file that the policy prescribes and that involves no amount, eligibility or prerequisite", and states the repeat rule. |
| sign tool | unchanged |

### policy_conflict_scan / rule_compute_equivalence / prerequisite_graph / override_declarations (revision 6)

- Scope split, subjects, owners, gates and edges are unchanged from revision 4. There is exactly one workflow.
- **dg_ext_amendment_fee.**
  - The new sentence governs *which submission* the row references. That is an object binding, not a computed quantity: `computes: amount_usd`.
  - The amount compute is untouched and still equivalent: every `compute_basis` quote is present in the rule, and the rule adds no new quantity.
  - The sentence follows base dg_amendment "otherwise costs amendment_fee_usd, referencing the amendment submission". The rule also still says free amendments "book no row at all" and that "the first free_amendments_per_acceptance of them are free".
  - With latest-first attachment, the rows fill the chargeable (later) amendments before the tool could ever reach a free (earlier) one. Once rows equal chargeable, the policy owes nothing further, so no free amendment is ever attached.
- Other policies: unchanged, and the revision-4 conclusions carry.

### action_binding_and_uuids (revision 6)

**Pairs and uuid8s**
- The (target_tool, computes) pairs are unchanged. The seven uuid8 suffixes are unchanged and independent.

**Amendment-fee attachment against the policy object**
- The two now state the same object: "most recently signed amendment that no amendment_fee row references yet" in both the rule and the docstring.

**Does a tool now judge anything?**
- *Attachment look-up:* the tool reads the declaration file and the ledger to pick the unreferenced latest amendment. It judges no eligibility, amount or prerequisite; it never refuses; it never blocks the call. With nothing unreferenced it still writes the row with `submission_id` "" (probe: receipt `submission_id: ''`). This is an object resolution that the policy prescribes verbatim, and the module docstring now declares it. **PASS.**
- *Repeat guard:* an exactly identical call (same row id) leaves the row set and the balance unchanged and returns a normal receipt. It does not refuse and does not hint at a prerequisite.
  - It never suppresses a policy-required write, because no policy ever requires two identical rows. Each dedup the charter imposes (late fee once per submission, a charge code once per date, a remittance reference once per acceptance, one amendment row per chargeable amendment) either forbids the duplicate or, for distinct objects, yields distinct ids.
  - It does not enforce those dedups either. For example, the same remittance reference with a different amount still writes a new row, so the judgement stays with the agent.
  - It removes the round-5 phantom-balance effect: `charges_due_usd` now always equals the ledger sum.
  - **PASS.**

### findings (revision 6)

**R5-N1 — closed** (`probe_r6.py`, real tools, the same constructed backlog as revision 5)
- Pass 1: the policy owes 225.00, and the tool attaches to `dgs_b97d849e16ef` (row `dgl_a1a666f0673f`).
- Pass 2: the policy still owes 225.00 (2 chargeable, 1 booked), and the tool attaches to **`9474bb1c…`** (row `dgl_3bedb6cbdc03`).
- Pass 3: the policy owes 0.00 (2 = 2).
- Two amendment_fee rows result. `charges_due_usd` **900.00 = ledger sum 900.00**, and the decision compute gives **`approved`**.

**R5-O1 — closed.** The tie-break by `submission_id` is deterministic. Probe: two unsettled amendments with the same `created_at` resolve to the higher reference `ZZZ_b`.

**R5-O2** — task-level; see `0.md` rev 6.

**R6-O1 — observation: a call with nothing left to attach still writes a row.** On task 0's opening world (before the signature), the tool writes an amendment_fee row with `submission_id` "".
- The policy gives 0.00 on that world (1 chargeable = 1 booked), so a policy-following agent never makes the call, and the tool rightly does not refuse.
- The docstring says so ("empty when every signed amendment already has a charge").

**No new RED at charter level.**

(End of the revision-6 charter-global section. Nothing in it derives from any round-6 GT.)

Freeze record: hashed at 2026-09-13T07:48:43Z (`_difficulty.md` `675df355…785`), before either round-6 task JSON was opened.

### closing_checklist (revision 6)

Written after both round-6 reveals. **Outcome: the difficulty is NOT closed.** Both tasks carry a proof-text SOURCE-CHAIN RED, and both were induced by the round-6 tool change.

**Per-task verdicts**
| Task | Policy self-consistency | Problem tree | Unique solution | Verdict line (rev 6) |
| --- | --- | --- | --- | --- |
| 0 | PASS | SOURCE-CHAIN RED — proof text only: "without reading the ledger" (decision tool), in the problem-tree card and `tools_do_not_block`; refuted by `task_tools.py:154` | PASS (hash `fc721dd5…`, 975.00) | **SOURCE-CHAIN RED** |
| 1 | PASS | SOURCE-CHAIN RED — proof text only: "the payment tool checks nothing", "without reading the ledger", "without checking … existing rows"; refuted by `:194`, `:228`, `:260` | PASS (hash `ea26b4e2…`, 0.00) | **SOURCE-CHAIN RED** |

**Did each round-5 RED close?**
- **R5-N1** (charter SOURCE-POLICY): **closed**. The tool attachment and the policy object now match. The backlog probe gives two rows, 900.00 = 900.00, and approved.
- **Task 1 rev-5 #1** (SOURCE-TASK, proof text): **closed**. The uniqueness tracing now names and excludes `dd7e9040…` correctly.
- **R5-O1** (tie): closed. **R5-O2 / task 0 rev-5 #2** (unverifiable harness claim): closed by a verified gate citation.

**New surface checked against "tools judge nothing / never refuse"**
- The amendment-fee attachment look-up and the repeat guard on all six writing tools **judge no eligibility, amount or prerequisite and never refuse** (`_difficulty.md` rev-6 action_binding). The relationship holds.
- What regressed is the proof text of both tasks, which still describes the pre-guard tool bodies.

**Regression check**
- The policies are unchanged apart from the amendment object sentence, and the compute is identical.
- GT write sequences and terminal hashes are unchanged in both tasks.
- The F-7, F-8, F-10, R3-N1 and R4 closures still hold.

**Step 4 items**
| Item | Status |
| --- | --- |
| Scope | Unchanged: 4 policies + the workflow and 4 tools (task 0); 3 policies and 3 tools (task 1). The union is 7 / 7 and the scopes are disjoint. One workflow, claimed by task 0. |
| Trees | Both have 2 value_input edges, both load-bearing. The graph is a DAG. On the function bodies no tool judges a prerequisite. |
| uuid8s | unchanged; independent |
| Gates on the final form | The coordinator's round-6 block (all 8 exit=0) is on extended `9003f0bf…` and tools `9c5e47e2…`, which are unchanged at closing, with `tasks/0.json` `b0d9365e…` and `tasks/1.json` `5c137c0d…`. There is no final form yet, because a RED remains open. |

**Open observations:** R6-O1 (a no-target call writes a `submission_id` "" row); R3-O4; R4-O1 (superseded by the rev-6 policy wording); R4-O2; and the solvability evidence-pointer notes (task 0 `late_fee_once`, task 1 `reference_once`).

The cross-difficulty merge surface and the scenario-level checks are out of scope and were not run.

---

## revision_7

### charter_global_frozen (revision 7)

**Freeze metadata**
- Written before any round-7 task GT was opened; the authoritative freeze is the pre-reveal hash record.
- Earlier revisions are untouched. Hash at the start of round 7: `4777ea955c88a93525b917be4931488ed04e989a391ff356cd3b4da6a4de621b`.

**Carry-forward by hash** (the skill's re-audit rule)
- `dg.extended.yaml` = `9003f0bff1d2b44b149115d3653b5d86a6403aef647d6291ea431f88f2add6ee`.
- `task_tools.py` = `9c5e47e2dafc887c274656d7570cd230b0e59bec7f361bb865053fa9bac5e369`.
- Both are **byte-identical** to the round-6 inputs (`cmp` against my private copies in `audit_dg_private/r6_copy/`).
- So `policy_conflict_scan`, `rule_compute_equivalence`, `action_binding_and_uuids`, `prerequisite_graph`, `override_declarations` and `findings` of **revision 6** are carried forward by reference, unchanged.
  - No charter RED is open.
  - R5-N1 stays closed.
  - The repeat guard and the attachment look-up judge nothing and never refuse.
  - R6-O1 stays an observation. The reworker records it without a code change, which is consistent with its observation status.

**Masked views**
- `source_r7/0.masked.json` `19deded9…45e2` and `source_r7/1.masked.json` `71b097ae…eb8`. Byte-identical.
- Gate block, including TRACEABILITY: all exit=0.

**contamination_disclosure** — Both tasks' GT is known to me from earlier rounds. This round's derivations are recomputations; the values and tool behaviour are those established by `probe_r6.py` and `replay_r3.py` on byte-identical inputs.

(End of the revision-7 charter-global section. Nothing in it derives from any round-7 GT.)

Freeze record: hashed at 2026-09-13T07:55:02Z (`_difficulty.md` `80cc2867…c669`), before either round-7 task JSON was opened.

### closing_checklist (revision 7)

Written 2026-09-13T07:56Z, after both round-7 reveals. **Outcome: all three relationships PASS for both tasks, and no charter RED is open. The difficulty passes the source-layer audit.**

**Per-task verdicts**
| Task | Policy self-consistency | Problem tree | Unique solution | Verdict line (rev 7) |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | **PASS** |

**Did each round-6 RED close?**
- Task 0 rev-6 #1 (SOURCE-CHAIN, proof text): **closed**. Both tool-behaviour sentences now state exactly the reads in `task_tools.py:146`, `:154`, `:69`, `:72` and `:107-115`.
- Task 1 rev-6 #2 (SOURCE-CHAIN, proof text): **closed**. The problem-tree card and `tools_do_not_block` now match `:191`, `:194`, `:225`, `:228`, `:257` and `:260`.

**Regression check**
- The shared inputs are byte-identical to round 6, so the charter conclusions carry by hash.
- Only the proof fields of the task files moved. GT tools, arguments, computations and worlds are identical to my round-6 copies.
- The terminal hashes are unchanged: `fc721dd5…` (975.00) and `ea26b4e2…` (0.00).
- The changed sentences, and a full extraction of every tool-behaviour sentence in both task files, are true.

**Step 4 items**
| Item | Status |
| --- | --- |
| Audit files, one per task, plus this file; old revisions traceable; each comparison carries PASS | yes. Revisions 1–7 are appended, and the earlier text is untouched (start-of-round-7 hashes `dd1af01e…`, `4e5642c7…`, `4777ea95…`). Both revision-7 comparisons carry PASS. |
| Extended policies fully covered; scopes pairwise disjoint and spanning whole trees | yes. Task 0 = {dg_ext_late_declaration_fee, dg_ext_amendment_fee, dg_ext_review_decision (root), dg_ext_approval_admin_fee} + the workflow. Task 1 = {dg_ext_loading_surcharge, dg_ext_marine_pollutant_surcharge, dg_ext_remittance_application (root)}. The union is 7; the intersection is empty. |
| Exactly one workflow, claimed by exactly one task | yes. `dg_wf_amended_declaration_redecision`, task 0; the GT sequence equals its steps. |
| Task tools and GT closed; independent frozen uuid8 per tool | yes. 7 tools (4 + 3), with suffixes unchanged since revision 3. |
| Each tree has ≥ 2 prerequisites and ≥ 1 value_input edge, with no cycle; the difficulty-wide graph is a DAG | yes. Both trees have 2 value_input edges, both load-bearing. No tool judges a prerequisite. |
| Instantiation-stage gates on the final form | The coordinator's round-7 block (all 8 exit=0, including TRACEABILITY) was run on extended `9003f0bf…` and tools `9c5e47e2…`, with `tasks/0.json` `08f30b8a…` and `tasks/1.json` `7a4d8cfc…`. All are unchanged at closing (checked 2026-09-13T07:55:59Z). |

**Open observations, not grounds for rework**
- R6-O1: a no-target amendment call writes a `submission_id` "" row.
- R3-O4: the workflow has exactly 4 write steps.
- R4-O2: stale `inputs.history` metadata.
- Task 1: the `reference_once` binding field (kept with a reason), and the contract-level "admits no other value" phrasing.
- Task 0's amendment-fee edge is unmet only after the customer's own amendment.
- The tools are unguarded, so some prerequisite orders cannot be seen in the terminal DB.

The cross-difficulty merge surface, the scenario-level checks and the KB audit are out of scope and were not run.
