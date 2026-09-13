# Policy-task audit — dnd_billing_desk / charter-global

## charter_global_frozen

- Scenario: `env/global_container_shipping_line`, difficulty `dnd_billing_desk`, category `dnd`, M = 2 (tasks 0, 1). Revision 1 (no earlier revision exists in this directory).
- Auditor: independent policy-task auditor (erl-task-policy-audit), not the authoring agent.
- Freeze time of this section: 2026-09-13T04:37Z. Written before any task's GT was revealed; contains nothing derived from a revealed GT.
- Freeze hashes (re-measured by the auditor, equal to the coordinator's HASHES.txt):
  - `tasks/dnd_billing_desk/dnd.extended.yaml` sha256 `afe4956138cdec3f41ccf550f872039c9056334f0db95acbffcfc97371139e71`
  - `tasks/dnd_billing_desk/task_tools.py` sha256 `d6dc8184cd2a51beb23c92c427c879b115937c587f5336380aa63a55ebdb5173`
  - masked views `0.masked.json` sha256 `bf82e71e…3fed65`, `1.masked.json` sha256 `e6f4e498…925e25` (keep = task_index, frozen_time, user_scenario, initial_state).
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/products/dnd.yaml`, `blueprint/products/booking.yaml` (only as the `booking` cross-category binding that `CFIELD('booking', …)` resolves against), `blueprint/db_schema.json` (dnd_free_time, dnd_ledger, dnd_disputes, bookings), `blueprint/share_tools.py`, the extended charter, `task_tools.py`; the compute DSL semantics from `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`: SUM/COUNT/LATEST auto-scoped to the holding `dnd_id`; CFIELD scoped to the customer; RND = Python `round`) and the dataflow index convention from `check_extended.py` (0-based `from_step`/`to_step`).
- Explicitly masked and not read before the reveal: every task JSON field other than the four kept above (`evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`); `env/global_container_shipping_line/worklog.md`; any other scratchpad content; any sibling difficulty or other scenario.
- Entry conditions (Step 0): the brief carries the seven instantiation-stage gate lines (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire, all exit 0, re-run 2026-09-13T04:2x); `check_traceability` is stated as deferred until the KB is published. Masked views and their hashes were supplied and verified. Entry conditions complete. The green gates are taken as admission only.

### policy_conflict_scan

Base-copy integrity: lines 1–685 of `dnd.extended.yaml` are byte-identical to `blueprint/products/dnd.yaml` (`diff` shows only the added `extended_policies` banner after line 685). The base copy has not been rewritten.

Extended surface: six extended policies and one workflow.

| id | subject | target_tool | computes | prerequisite |
| --- | --- | --- | --- | --- |
| dnd_ext_final_detention_charge | dnd_detention_invoiced | book_detention_invoice_dba94f21 | amount_usd | [] |
| dnd_ext_final_demurrage_charge | dnd_demurrage_invoiced | book_demurrage_invoice_a2ad21e7 | amount_usd | ← detention (value_input, slab_offset) |
| dnd_ext_goodwill_waiver_amount | dnd_charge_waived | grant_goodwill_waiver_e03c98b1 | amount_usd | ← demurrage (value_input, invoiced_amount) |
| dnd_ext_dispute_lodged_amount | dnd_dispute_credited | lodge_dnd_dispute_1c3d36b3 (owner user) | disputed_amount_usd | [] |
| dnd_ext_dispute_credit_amount | dnd_dispute_credited | book_dispute_credit_515e844f | amount_usd | ← lodged (value_input, disputed_amount) |
| dnd_ext_late_invoice_waiver | dnd_charge_waived | clear_late_invoice_2264ae48 | amount_usd | ← credit (value_input, earlier_credits) |
| dnd_wf_combined_record_closeout (workflow) | 5 steps: detention → demurrage → goodwill → pay (user) → settle | — | — | [] |

Overlap scan over subjects, triggers, eligibility, time anchors, parameters, terminal states and cross-category reads:

- Two extended policies write `dnd_charge_waived` (goodwill, reason `commercial_goodwill`; late invoice, reason `late_invoice`). They are distinguished by waiver_reason, by trigger (`on_request` vs `state_due`) and by the base dedup `distinguish_by: [reference_event_id, waiver_reason]`; no situation makes both claim the same row.
- Two extended policies have subject `dnd_dispute_credited` (lodged amount computes the dispute's `disputed_amount_usd` through the user tool; credit amount computes the credit row). Different tools and different computed fields — no double claim.
- Both invoice policies read the same recorded dates and the same slab/rate parameters; their day-typing sentences (import: ≤ full_gate_out demurrage, later detention; export: ≤ full_gate_in detention, later demurrage) are mirror images and agree with base `dnd_invoicing`. Slab continuation: detention on combined import continues after the preceding chargeable demurrage days; demurrage on combined export continues after the booked detention row's chargeable_days. Each record direction therefore has exactly one continuing clock type; no double-offset case exists.
- The rate-class override (reefer equipment billed at reefer rates only under booking cargo_type reefer, otherwise dry) is stated identically in substance by the four policies that recompute day rates (detention, demurrage, goodwill recomputation, dispute-credit recomputation). The two policies that do not recompute (lodged amount, late invoice) do not touch rate class. No conflicting rate-class rule in the extended surface.
- DG uplift: demurrage-only 50 %/25 % uplift (base) is followed by all four recomputing policies; detention carries none. The "uplift share" (open × u/(100+u)) is removed from the goodwill base, from the lodged disputed amount and from the late-invoice waiver; the dispute credit is `min(overcharge, disputed)` where the overcharge is the difference of two uplifted amounts. Observation O-3 below records the one textual tension this produces; it is not a conflict of conclusions.
- Time anchors: invoice deadline (clock_stopped_date + invoice_issue_deadline_days, inclusive), dispute window (invoice event_date + dispute_window_days, inclusive), goodwill window (invoice event_date + waiver_request_window_days, inclusive), goodwill quota (trailing 365 days ending on the waiver date, inclusive, across all the customer's records). All are base, inherited unmodified by every extended policy.
- Terminal states: invoice rows move the record to `invoiced` (tool effect = base transition `dnd_invoice_issued`); settlement only at balance 0.00 (base `dnd_payment`/`dnd_invoicing`), used only by the workflow. No extended policy changes a terminal state.
- Cross-category read boundary: every extended policy reads exactly `booking.cargo_type` through `CFIELD('booking','cargo_type', booking_id=F('booking_id'))`; reachable at runtime through `find_bookings`. No policy reads balances of other categories (base `dnd_agg_overdue_portfolio_block` boundary untouched).

Scope partition (inferred from the charter's two prerequisite chains and the two masked user scenarios; `charter_scope` itself is masked and is compared at each task's reveal):
- chain A = {dnd_ext_final_detention_charge, dnd_ext_final_demurrage_charge, dnd_ext_goodwill_waiver_amount} + the workflow (its steps are exactly chain A + pay + settle);
- chain B = {dnd_ext_dispute_lodged_amount, dnd_ext_dispute_credit_amount, dnd_ext_late_invoice_waiver}.
The two chains share no policy and no edge; together they cover all six extended policies and the one workflow. Claimed event types `dnd_free_time_extended` / `dnd_extension_fee_charged` are carried by base policies only and no extended policy exercises them (observation O-7).

No overlapping subject in the extended surface reaches incompatible conclusions. Conflict scan: PASS, with observations O-1…O-7.

### rule_compute_equivalence

Check 2, per policy. Every compute binding was evaluated by the auditor with the gate's own DSL (`build_env`/`eval` of `check_compute.py`) on the masked worlds; values are in the task files.

**dnd_ext_final_detention_charge.**
- Clock start/stop by model and direction: rule "Under clock_model separate the detention clock of an import record runs from full_gate_out_date to empty_return_date … export record from empty_pickup_date to full_gate_in_date … Under clock_model combined the merged clock of an import record runs from discharge_date to empty_return_date and that of an export record from empty_pickup_date to loaded_date" → `clock_start`, `clock_stop` implement exactly these four pairs.
- Days used: "the days used are the stop date minus the start date in calendar days" → `DAYS(clock_start, clock_stop) - P('clock_start_offset_days') + 1` (equal for offset 1, the only offset any product carries; the general offset form is base `dnd_clock_rules`' formula).
- Free days: "against the combined free days of the direction" / separate free days → `free_days`.
- Day typing: "the n-th day of the merged clock falls on the start date plus n calendar days, and on import the days after full_gate_out_date are detention days while on export the days up to and including full_gate_in_date are detention days" → `terminal_boundary_day` = number of merged-clock days up to and including the terminal movement; `detention_days` = import `max(0, used − max(free, tb))`, export `max(0, min(used, tb) − free)` — the set {position > free} ∩ {detention positions}.
- Slab count: "on import their slab count continues after the chargeable demurrage days that precede them in the merged clock, and on export it starts at the first chargeable day" / separate "their slab count starts at the first detention day" → `slab_offset` = `max(0, min(used, tb) − free)` on combined import, else 0; `days_slab1..4` place positions offset+1 … offset+detention_days against bounds 5/10/20 (or 7/14/28).
- Rate class: override sentence → `container_class` hard-codes the equipment_class_map lists (20RF/40RH reefer, 20OT/40OT/20FR/40FR/20TK special, rest dry), identical in all six variants; reefer → dry unless cargo_type reefer.
- "detention days carry no dangerous-goods uplift, the day rates are added up, and only the sum is rounded to the cent" → `result = RND(Σ days × rate, 2)` with no uplift factor.
- "A record with no detention day beyond free time gets no detention row" → not a compute value (row existence); inherited base "a row with no chargeable day is not written".
- Sweep back: no compute binding lacks a rule sentence; no rule sentence governing the amount lacks a binding. `chargeable_days`, `period_start_date`, `period_end_date` are tool arguments fixed by the rule ("the first and last detention day billed") but not computed by any binding (they are not the declared `computes`). PASS.

**dnd_ext_final_demurrage_charge.** Mirror of the above: separate import discharge→gate_out, export gate_in→loaded; combined as above; demurrage typing "on import the days up to and including full_gate_out_date … on export the days after full_gate_in_date"; `demurrage_days` = import `max(0, min(used, tb) − free)`, export `max(0, used − max(free, tb))`; `slab_offset` = `SUM('dnd_ledger','chargeable_days', event_type='dnd_detention_invoiced')` on combined export, else 0 — quoting "on an export record the slab count of the demurrage days continues after the chargeable_days of the detention row already booked on the record, counting none when the record carries no detention row; on import the slab count starts at the first chargeable day"; DG: "every demurrage day rate is increased by dg_container_uplift_pct percent of itself" → `(Σ days × rate) × (100 + u)/100` (distributive equal to per-day uplift); "only the sum is rounded to the cent" → single `RND`. PASS (see O-2 for the base-basis rebinding in `slab_offset`).

**dnd_ext_goodwill_waiver_amount.** `invoiced_amount` (sum of demurrage rows on the record) and `demurrage_row_id` (latest demurrage row) ← "computed only on a demurrage invoice row already booked on the record"; `earlier_credits` ← "its amount_usd less every waiver and dispute credit already booked with that row as reference_event_id" (SUM of all ledger rows referencing the row; payments carry `reference_event_id` null by tool and schema); recomputation block identical to the demurrage policy ← "exactly as its final demurrage row is computed, with the slab count of an export record under clock_model combined continuing after the chargeable_days of the detention row booked on the record"; `gross_goodwill_base = MN(open, recomputed)` ← "The gross goodwill base is the smaller of the amount still open and the recomputed amount"; `uplift_share` ← "that base times dg_container_uplift_pct divided by the sum of 100 and dg_container_uplift_pct"; `capped_goodwill = MN(base × pct/100, cap)`; `result = int(round(x·100, 6))/100` = floor to the cent for positive x ← "rounded down to the cent only at the end". "Products whose goodwill_waiver_pct_max is 0 give no goodwill" is implemented by pct = 0 → 0. "Goodwill on a detention row remains governed by dnd_goodwill_waiver alone" is a delegation, not a compute promise. PASS.

**dnd_ext_dispute_lodged_amount.** `open_amount` ← "the row's amount_usd less every waiver and dispute credit already booked with the row as reference_event_id, including waivers granted by the operations department"; `dg_uplift_pct` + `result = RND(open − open·u/(100+u), 2)` ← "the uplift share … is left out of the dispute … rounded to the nearest cent only at the end". The sentence "A dispute on any other ground, or on a detention row, is lodged for the amount the billed party states" is a customer-supplied branch with no compute, by nature (not an empty promise: the policy assigns the value to the customer). PASS.

**dnd_ext_dispute_credit_amount.** `disputed_amount = LATEST(dnd_disputes.disputed_amount_usd, outcome='submitted') or 0` ← "The credit is the smaller of the overcharge and the disputed_amount_usd of the dispute"; recomputation block identical to the demurrage policy; `overcharge = MX(0, invoiced − recomputed)` ← "The overcharge is the row's amount_usd less the recomputed amount, and none when the recomputed amount is not lower"; `result = RND(MN(overcharge, disputed), 2)`. The outcome rule (upheld / partially_upheld / denied with no row) governs the tool's `outcome` argument and is not a compute value. Note (observation O-4): `disputed_amount` picks the latest *submitted* dispute on the whole record, not the one on the demurrage row; the rule scopes the credit to "a dispute the billed party has lodged on the invoice row". They coincide whenever the record carries at most one submitted dispute. PASS.

**dnd_ext_late_invoice_waiver.** `open_amount` ← "The amount still open is the row's amount_usd less every waiver and dispute credit already booked with the row as reference_event_id, including waivers of the operations department"; `result = RND(open − open·u/(100+u), 2)` ← "the waiver is the amount still open less the uplift share, rounded to the nearest cent only at the end". The rule's last sentence "A late detention row carries no uplift and is cleared whole." has no compute_basis quotation and no binding: every binding is keyed to `event_type='dnd_demurrage_invoiced'`. In a world whose late row is a detention row, the rule gives that row's open amount and the compute gives the demurrage row's figure (or 0). This is a rule→compute loss on an unexercised branch — observation O-5 (no task world carries a late detention row, so no scored consequence can be demonstrated; see task files).

Rounding convention across the charter: `RND` is Python `round(float, 2)` (binary float, half-to-even on exact ties); the rule says "rounded to the nearest cent". No value in either task world lands on a half-cent (all intermediates are exact multiples of 0.25 or 0.5), so no divergence is demonstrable. Observation only.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: (book_detention_invoice_dba94f21, amount_usd), (book_demurrage_invoice_a2ad21e7, amount_usd), (grant_goodwill_waiver_e03c98b1, amount_usd), (lodge_dnd_dispute_1c3d36b3, disputed_amount_usd), (book_dispute_credit_515e844f, amount_usd), (clear_late_invoice_2264ae48, amount_usd). Each claimed by exactly one policy. `pay_dnd_balance_a831ef2f` and `settle_dnd_record_d9ada3ba` are claimed by no computing policy (workflow `computed_by: []`); their values come from base `dnd_payment` (amount ≤ balance, reference verbatim) and base settlement.
- Business reading of each tool: docstrings match the policy subject and the base event (`dnd_detention_invoiced`, `dnd_demurrage_invoiced`, `dnd_charge_waived` commercial_goodwill / late_invoice, `dnd_dispute_credited` with dispute decision, `dnd_payment_received` owner user, `dnd_settled`). No docstring adds a confirmation, review, waiting step or procedure outside the policy.
- Function bodies (lines 33–49, 74–90, 112–126, 146–160, 177–184, 207–217, 241–256, 278–292): the only refusal in every tool is "no free-time record under that dnd_id". No tool reads status, dates, dispute state, quotas, windows or balances to refuse or hint. The tool layer judges no prerequisite and no eligibility.
- uuid8s: dba94f21, a2ad21e7, e03c98b1, a831ef2f, d9ada3ba, 1c3d36b3, 515e844f, 2264ae48 — eight distinct values, no shared prefix longer than one hex digit (d/d, a/a, 1-/5-/2- all differ from the second digit), no sequential or adjacent pattern, none reused. No batch-derivation signal. PASS.

### prerequisite_graph

Check 7 over the whole graph.

- Every extended policy and the workflow fills `prerequisite` (three `[]`, four edges). Every `problem` names another extended policy id in this file (never a base policy, never itself).
- Graph: detention → demurrage → goodwill; lodged → credit → late_invoice. Two disjoint chains, acyclic.
- Edge demurrage ← detention (kind value_input, gate `slab_offset`): `policy_source` is verbatim in the demurrage rule ("Under clock_model combined the record's detention row is booked before its demurrage row, and on an export record the slab count of the demurrage days continues after the chargeable_days of the detention row already booked on the record, counting none when the record carries no detention row"). `condition` ("Under clock_model combined the record's detention row is booked before its demurrage row.") restates the first clause without strengthening. `resolved_by` book_detention_invoice_dba94f21 writes a `dnd_detention_invoiced` row with `chargeable_days`, which is exactly what `slab_offset` sums. `effect` correctly limits the value change to "an export record under clock_model combined". `slab_offset` is a real binding. Note: on combined import and on any separate record the edge moves no value (slab_offset is 0 by construction) — load-bearing is therefore world-dependent and is judged per task.
- Edge goodwill ← demurrage (value_input, gate `invoiced_amount`): `policy_source` verbatim ("A commercial goodwill waiver on the demurrage row of a record is granted at the billed party's request and is computed only on a demurrage invoice row already booked on the record."). `invoiced_amount` is a real binding; `resolved_by` book_demurrage_invoice_a2ad21e7 creates the row it sums. Effect accurate.
- Edge credit ← lodged (value_input, gate `disputed_amount`): `policy_source` verbatim ("A dispute credit is booked only against a dispute the billed party has lodged on the invoice row and that is still submitted, and the credit references both that dispute and the disputed row."). `resolved_by` lodge_dnd_dispute_1c3d36b3 (owner user) creates a `submitted` dispute whose `disputed_amount_usd` the binding reads. Effect accurate.
- Edge late_invoice ← credit (value_input, gate `earlier_credits`): `policy_source` verbatim ("Before a late demurrage row is cleared, any overcharge it carries against its recomputation is taken off through a decided dispute credit, so that the late-invoice waiver acts on what remains."). `resolved_by` book_dispute_credit_515e844f writes a `dnd_dispute_credited` row referencing the invoice row, which `earlier_credits` sums. Effect accurate. The `condition` carries the rule's own conditionality ("Any overcharge …"), so the edge is live only in a world whose late row is overcharged — judged per task.
- `kind` matches `gate` for all four edges (each gate is a binding of the dependent's compute). No authoring-viewpoint phrasing ("in this task", "at the opening", "current world") appears anywhere in the charter (grep empty).
- Cross-chain: no edge crosses chains, so the difficulty-wide graph is a DAG.
PASS.

### override_declarations

Check 1, finding half. Sentence-by-sentence against each `base_policy_refs` entry. "F" = followed, "D" = handled differently and declared in `overwrite`, "U" = handled differently and undeclared, "I" = not restated, inherited unweakened.

**dnd_ext_final_detention_charge** (refs dnd_invoicing, dnd_clock_rules; overwrite: dnd_invoicing rate-class sentence).
- dnd_clock_rules: offset/whole-day/calendar counting F; separate clock pairs F; combined clock pairs F; "product in force … governs every clock" F ("for the product on the record"); recorded dates only F; status transitions I.
- dnd_invoicing: "computed once its last clock has stopped" F; "Chargeable days … beyond its free days" F; separate slabs restart per clock F; combined typing F; "slab position … counted across the whole sequence of chargeable days" F (import continuation / export start); slab thresholds F; "Each day is billed at the rate of its clock type, slab and the rate class … equipment_class_map" D (declared); DG demurrage-only F; one row each / cent rounding / no-row-when-zero F; minimum invoice I; deadline and its counting I; status gate I; payment term I; settled-when-cleared I.
- Result: one deviation, declared.

**dnd_ext_final_demurrage_charge** (same refs; overwrite: rate-class sentence). As above, plus the slab-continuation sentence: base "the slab position of a day is counted across the whole sequence of chargeable days" (a date-derived count) vs extended "continues after the chargeable_days of the detention row already booked on the record, counting none when the record carries no detention row" (a ledger-derived count) — U in form, not named in `overwrite`. Under the extended rule's own order sentence ("the record's detention row is booked before its demurrage row") and a detention row computed from the same recorded dates, the two counts are equal; they differ only if the order is breached or the booked detention row's chargeable_days disagree with the dates. Recorded as observation O-2; each task file checks whether its world can reach the divergent case.

**dnd_ext_goodwill_waiver_amount** (refs dnd_goodwill_waiver, dnd_invoice_dispute, dnd_invoicing, dnd_clock_rules; overwrite: the goodwill-amount sentence, the rate-class sentence).
- dnd_goodwill_waiver: one waiver, at request, reason commercial_goodwill F; amount sentence D; "grants the full amount so computed" F; quota I; window I; one per invoice I; "When a dispute on the invoice is still submitted, the dispute is decided first and goodwill is computed on what remains" F (open amount after credits); pct 0 F; operations-only reasons I.
- dnd_invoice_dispute: nothing handled differently. dnd_invoicing/clock_rules: as demurrage (rate class D; O-2 applies to the recomputation's slab count).
- Result: every deviation of the scored quantity is declared.

**dnd_ext_dispute_lodged_amount** (refs dnd_invoice_dispute, dnd_invoicing; overwrite []).
- dnd_invoice_dispute: "billed party may dispute one invoice row, which only the billed party can do; … lodged by the customer and decided by the desk" F; window I; "An invoice row carries at most one dispute" I; three grounds and their decisions not touched; "never more than the disputed_amount_usd" F. No base sentence fixes how large the disputed amount is; the extended rule fills a quantity base leaves to the customer, it does not replace one. dnd_invoicing: DG uplift F (the uplift share computation reads it, does not change it).
- Result: `overwrite: []` is correct.

**dnd_ext_dispute_credit_amount** (refs dnd_invoice_dispute, dnd_invoicing, dnd_clock_rules; overwrite: rate-class sentence).
- dnd_invoice_dispute: "On rate_misapplied or free_time_misapplied, the desk recomputes the invoice row under dnd_invoicing with the product and recorded dates of the record; when the invoiced amount exceeds the recomputed amount, the dispute is upheld or partially upheld and credited by a dnd_dispute_credited row of the difference, but never more than the disputed_amount_usd, and when it does not, the dispute is denied with no row" F (the upheld / partially_upheld split is a refinement base leaves open); "A credit may be booked only on a record whose status is invoiced" I; decision within dispute_response_days F (decided in the call).
- Recomputation: rate class D; "with the product and recorded dates of the record" vs extended "on export the slab count continues after the chargeable_days of the detention row booked on the record" — O-2 again.
- Result: declared except O-2.

**dnd_ext_late_invoice_waiver** (refs dnd_invoice_dispute, dnd_goodwill_waiver, dnd_invoicing; overwrite: "the whole amount still open on the invoice is cleared by a dnd_charge_waived row with waiver_reason late_invoice").
- dnd_invoice_dispute: lateness test "event_date is later than the record's clock_stopped_date plus invoice_issue_deadline_days" F; whole-amount clearing D (DG share retained); "no dispute credit is written for this ground" F (the extended credit is booked on a separate rate/free-time dispute, not on the late ground); "the same waiver clears a late invoice raised by the customer without a formal dispute" F — the late ground still needs no formal dispute; the added sentence "Before a late demurrage row is cleared, any overcharge … is taken off through a decided dispute credit" governs the overcharge, a subject base does not address, and fixes a sequencing that base (whole amount cleared, order-free) never needed. The two sentences apply together without contradiction: the late ground is recognised informally, the overcharge part goes through a formal dispute first.
- dnd_goodwill_waiver: nothing touched. dnd_invoicing: "A record whose deadline has passed without an invoice is settled without one" I.
- Result: the one deviation of the scored quantity is declared.

Disguised forms: no anonymous intermediate factor changes a base-governed quantity except O-2 (`slab_offset` rebound to the ledger); no 0/1 multiplier zeroes a base-fixed amount (the `dg_uplift_pct` switch is a declared branch of base's own uplift); no base branch is dropped (separate/combined × import/export are all produced by every selector). No author note calls base's output a "wrong value" in the charter.

### findings

Charter-global findings (pre-reveal). No SOURCE-POLICY RED is established at charter level; each item is an observation whose task consequence, if any, is judged in the task file named.

- **O-1 (observation; bears on task 0).** `db_schema.json` `dnd_ledger.period_end_date` meaning reads "last chargeable day covered by the invoice (the day the clock stopped)". Under clock_model combined the detention row of an export record ends on full_gate_in_date and the demurrage row of an import record ends on full_gate_out_date — not on the day the clock stopped. The extended rules ("the first and last detention day billed") and the tool docstrings ("last detention day covered by the line") are explicit and agree with each other; the schema parenthetical is the only source of the alternative. Affected: `blueprint/db_schema.json` dnd_ledger.period_end_date. Task 0 checks whether GT's detention period_end_date follows the rule.
- **O-2 (observation; bears on tasks 0 and 1 by check).** `dnd_ext_final_demurrage_charge.compute.slab_offset` (and the identical binding in the goodwill and dispute-credit recomputations) derives the export combined slab offset from the booked detention row's `chargeable_days`, while base `dnd_invoicing` counts "across the whole sequence of chargeable days" from the recorded dates. Not named in any `overwrite`. The values coincide whenever the declared order is followed and the detention row was computed from the same dates; divergence needs a pre-existing detention row whose chargeable_days disagree with the dates, or an order breach. Task 0 books its detention row in the same call from the dates; task 1 is an import separate record (slab_offset ≡ 0). No demonstrable consequence expected; confirmed per task.
- **O-3 (observation; bears on task 1).** The goodwill rule says "The dangerous-goods uplift is passed through to the terminal and is never reduced by the desk" and the lodged-amount rule says it "is never disputed at the desk", while the dispute-credit rule credits `min(overcharge, disputed)` where the overcharge is the difference of two uplifted amounts, so a credit can include the uplift carried by overbilled days. Read with the specific credit sentence, the desk only removes uplift that was billed on days or rates it recomputes away; the uplift on the correct amount is untouched. The general sentences sit in other policies and are scoped to goodwill and to the disputed amount. No second defensible credit value is produced.
- **O-4 (observation; bears on task 1 by check).** `dnd_ext_dispute_credit_amount.compute.disputed_amount` reads the latest `submitted` dispute on the whole record, not the dispute on the demurrage row the rule names. Coincident in any world with at most one submitted dispute on the record.
- **O-5 (observation; bears on task 1 by check).** `dnd_ext_late_invoice_waiver`: the rule sentence "A late detention row carries no uplift and is cleared whole." has no `compute_basis` quotation and no binding; every binding is keyed to `dnd_demurrage_invoiced`. A rule→compute loss on an unexercised branch. It becomes scored only in a world with a late detention row.
- **O-6 (observation; bears on task 1).** Base eligibility wording "An invoice row carries at most one dispute." counts every dispute, while its `dedup_contract.duplicate_filters.outcome` lists [submitted, upheld, partially_upheld, denied] and so excludes `withdrawn`. The structured contract resolves the reading (a withdrawn dispute does not block a new one); the prose alone is looser. Task 1's record carries a withdrawn dispute on the same row — judged there.
- **O-7 (observation; no task).** The claimed event types `dnd_free_time_extended` / `dnd_extension_fee_charged` are exercised by no extended policy and no task; base `dnd_free_time_upgrade` / `dnd_agg_overdue_portfolio_block` remain the only policy for them. Coverage note, not a relationship failure.

## post_reveal_charter_note

Written 2026-09-13T04:48Z, after both task derivations were frozen (hash-attested at 04:43:31Z) and both reveals. The charter-global section above is unchanged. This note records one charter-level observation the pre-reveal scan missed; it is derivable from the charter alone, and was noticed because `tasks/1.json` `solvability_contract.gold_actions[step 11]` lists goodwill gates on a late-invoice waiver.

- **O-8 (observation; bears on task 1, no consequence there).** Base `dnd_goodwill_waiver` eligibility items `goodwill_quota`, `goodwill_window` and `one_goodwill_per_invoice` carry `applies_to: [dnd_charge_waived]` — the whole event type, which also carries the late-invoice waiver of `dnd_ext_late_invoice_waiver` (and base `dnd_invoice_dispute`'s late_invoice clearing). The rule prose of `dnd_goodwill_waiver` scopes the same sentences to "one commercial goodwill waiver … recorded with waiver_reason commercial_goodwill". Read structurally, a late-invoice waiver is refused once the customer's goodwill quota is used or the product's waiver_request_window_days has run from the invoice date; read by the prose, it is not. Two conclusions in the same situation exist only in a world where one of those gates fails; in task 1's world all three hold (quota 0 < 1, window to 2026-09-26, no goodwill on the row), so no scored value can move. `dnd_ext_late_invoice_waiver` lists `dnd_goodwill_waiver` in `base_policy_refs` without saying which of its gates it inherits. Affected: `products/dnd.yaml` (base, verbatim in the charter) `dnd_goodwill_waiver.eligibility[*].applies_to`; `dnd_ext_late_invoice_waiver.base_policy_refs`.

## closing_checklist

Written 2026-09-13T04:48Z, after all M = 2 comparisons. Step 4 closes a difficulty only when every task passes all three relationships; that does not hold, so the difficulty is **not closed**. Status of each item:

- Audit files correspond one-to-one with the tasks: `0.md`, `1.md`, and this `_difficulty.md` alongside; revision 1 (no older revision to preserve). Comparison sections carry verdicts; not all are PASS:
  - task 0: policy self-consistency PASS; problem tree **SOURCE-CHAIN RED** (F-0.1); unique solution **SOURCE-TASK RED** (F-0.2).
  - task 1: policy self-consistency PASS; problem tree PASS; unique solution **SOURCE-TASK RED** (F-1.1).
- Extended policies fully covered by the two scopes, scopes pairwise disjoint across whole trees (GT `charter_scope`: task 0 = detention, demurrage, goodwill + workflow; task 1 = lodged, credit, late — matches the pre-reveal partition); exactly one workflow, claimed by task 0 only; the eight task tools are each called in exactly one task's GT and every GT task-tool call is inside that task's scope; every uuid8 independent (see action_binding_and_uuids). Holds.
- Every task's tree has 2 prerequisites, both value_input, acyclic; the difficulty-wide `prerequisite` graph is two disjoint chains, a DAG with no cross-task edge. Holds.
- Instantiation-stage gates: not re-run by the auditor (Step 0: the auditor cites, does not run). The coordinator's snapshot (7 gates green, 2026-09-13T04:2x) was taken on the charter hashes this audit froze; `check_traceability` is deferred until the KB is published, so the gate set on the final form is incomplete by the coordinator's own statement.
- Difficulty verdict: **does not pass the source-layer audit.** Findings are reported only; no artifact was edited and no fix is proposed.

## revision_2

Round-2 re-audit (brief: verify each round-1 RED is closed, no new defect, nothing regressed). Revision-1 text above is left untouched.

### charter_global_frozen (revision_2)

- Auditor: same independent auditor as revision 1. Written 2026-09-13T04:59Z, before any round-2 GT field was opened; contains nothing derived from a round-2 GT.
- Inputs and hashes (re-measured): `dnd.extended.yaml` sha256 `42c5200f321f3a572f25720415f8d98287fe7181333d73eeea21b53285177235` (**changed** from `afe49561…`; 1226 → 1255 lines); `task_tools.py` `d6dc8184…5173` (unchanged); `blueprint/products/dnd.yaml` `e8d3f230…6640`, mtime unchanged since 02:50; masked views `source_r2/0.masked.json` `561fed0f…02cf` (changed), `source_r2/1.masked.json` `e6f4e498…5e25` (identical to round 1). Because the charter changed, every charter-global section is re-derived below against the current text; nothing is carried forward by reference.
- Masked and not read before the round-2 freeze: every round-2 task JSON field outside the masked views. contamination_disclosure (charter level): the auditor has read the **round-1** GT of both tasks (revision 1 reveal). No round-2 GT field, no scratchpad file outside `dnd_audit_self/` and `coord_7f3a/masked/dnd_billing_desk/source_r2/`, and no other scenario or difficulty was read.
- Entry conditions: round-2 gate snapshot supplied (7 gates exit 0 on the reworked files; check_traceability deferred). Complete.

Base copy: lines 1–685 of the current charter are still byte-identical to `blueprint/products/dnd.yaml` (diff empty).

What changed in the extended surface (current text read in full, lines 686–1255):
1. `dnd_ext_final_detention_charge.rule` — new last sentence: "The first and last detention day billed are the first and last chargeable detention days themselves, so a detention row that ends at a terminal movement, such as the full_gate_in_date of an export record, ends on that movement's date and not on the clock_stopped_date."
2. `dnd_ext_final_demurrage_charge` — second `overwrite` entry superseding base `dnd_invoicing` "the slab position of a day is counted across the whole sequence of chargeable days" by the booked-detention-row continuation; mirror period sentence for demurrage rows.
3. `dnd_ext_goodwill_waiver_amount` — third `overwrite` entry (same base sentence → "with the slab count of an export record under clock_model combined continuing after the chargeable_days of the detention row booked on the record"); the uplift sentence now reads "The dangerous-goods uplift carried by the goodwill base is passed through to the terminal and is never reduced by goodwill".
4. `dnd_ext_dispute_lodged_amount.rule` — uplift sentence now "is left out of what the billed party disputes"; new sentence "A withdrawn dispute does not count toward the one dispute an invoice row may carry, so a row whose only earlier dispute was withdrawn may be disputed again within the dispute window."
5. `dnd_ext_dispute_credit_amount` — second `overwrite` entry (same base slab sentence → "on export the slab count continues after the chargeable_days of the detention row booked on the record"); new binding `demurrage_row_id`, and `disputed_amount` now `LATEST('dnd_disputes', 'disputed_amount_usd', date_field='created_at', outcome='submitted', invoice_event_id=demurrage_row_id) or 0`; new rule sentence "The credit may include the dangerous-goods uplift that the row billed on days or rates the recomputation removes, while the uplift carried by the recomputed amount is never credited."
6. `dnd_ext_late_invoice_waiver.rule` — "A late detention row carries no uplift and is cleared whole." replaced by "A late detention row is cleared under dnd_invoice_dispute alone."; new sentence making the late-invoice waiver subject to `dnd_goodwill_waiver`'s quota, window and one-goodwill-per-row eligibility.
7. Workflow, prerequisite edges, target tools, `computes`, all other compute bindings: unchanged in text.

### policy_conflict_scan (revision_2)

- Subjects/tools/computes table of revision 1 still exact (no id, subject, target_tool or computes changed).
- Rate-class override: still stated in substance identically by the four recomputing policies. DG uplift: now scoped per quantity — goodwill base ("never reduced by goodwill"), disputed amount ("left out of what the billed party disputes"), credit (explicitly "may include the uplift … the recomputation removes, while the uplift carried by the recomputed amount is never credited"), late waiver (share of the remainder stays collectible). The four sentences no longer contain a general claim that another policy's formula contradicts. Round-1 O-3 tension: gone.
- Slab counting: the base whole-sequence sentence is now superseded, by declaration, in the three policies whose compute reads the booked detention row (demurrage, goodwill, dispute credit); the detention policy still follows the base sentence (import continuation after the date-derived demurrage days; export start at the first chargeable day). Under the declared order (detention row first) the two bases give the same position for every day; no double offset. Round-1 O-2: closed by declaration.
- Late-invoice waiver vs goodwill gates: the extended rule now states outright that a late-invoice waiver is subject to the quota, window and one-goodwill-per-row gates of `dnd_goodwill_waiver`, matching the base structure (`applies_to: [dnd_charge_waived]`). Residual tension (observation O-8r): base `dnd_invoice_dispute` prose says a late invoice "is upheld as not collectible" and "the same waiver clears a late invoice raised by the customer without a formal dispute", with no gate; in a world where one of the three gates fails, the extended text leaves an uncollectible row uncleared. The tension originates in the base (prose vs structured `applies_to`) and the extended text takes the structured side explicitly; no task world makes a gate fail (checked per task).
- Late detention rows: now delegated to base ("cleared under dnd_invoice_dispute alone" — the base's whole-open-amount clearing; detention carries no uplift, so the superseded clause and the base clause give the same figure for a detention row). Round-1 O-5 rule→compute loss: gone (the rule no longer promises a detention figure from this compute).
- Withdrawn disputes: rule prose now agrees with the base `dedup_contract` filter. Round-1 O-6: closed.
- Time anchors, terminal states, cross-category read boundary: unchanged, as in revision 1.
- Scope partition: chain A + workflow / chain B, unchanged; both chains still cover all six extended policies and the workflow. Claimed-but-unexercised upgrade events (O-7): unchanged.
Conflict scan: PASS, with observations O-7 (carried), O-8r.

### rule_compute_equivalence (revision_2)

Mechanical sweep of the current text: every `compute_basis` quotation is verbatim in its policy's `rule` (all six policies, auditor script, no miss). Per-policy conclusions:
- detention: bindings unchanged; the new period sentence governs `period_start_date`/`period_end_date` tool arguments, not the computed `amount_usd`. PASS.
- demurrage: bindings unchanged; `slab_offset` now has a declared basis in `overwrite` as well as the rule quotation. PASS.
- goodwill: bindings unchanged; uplift-share binding quotes the (reworded) rule verbatim. PASS.
- lodged amount: bindings unchanged; the withdrawn-dispute sentence is an eligibility statement, not a compute value. PASS.
- dispute credit: `demurrage_row_id` ← "On a demurrage row disputed on rate_misapplied or free_time_misapplied the desk recomputes the row"; `disputed_amount` ← "A dispute credit is booked only against a dispute the billed party has lodged on the invoice row and that is still submitted" — now scoped to the row by `invoice_event_id=demurrage_row_id`. Auditor check on task 1's masked world with an extra later `submitted` dispute on a different row: the credit still evaluates to the disputed row's figure (210.00). Round-1 O-4: closed. The new uplift sentence restates what `overcharge = invoiced − recomputed` already implies. PASS.
- late waiver: bindings unchanged; the detention branch is no longer a promise of this compute; the gate sentence is eligibility. PASS.
- Rounding (`RND` = Python round vs "nearest cent"): unchanged; still no half-cent value in either world. Observation carried.

### action_binding_and_uuids (revision_2)

`task_tools.py` unchanged (hash); `(target_tool, computes)` pairs unchanged; each still claimed by exactly one policy; tool bodies still refuse only on a missing record; the eight uuid8s unchanged and independent. PASS.

### prerequisite_graph (revision_2)

All four edges unchanged in text; each `policy_source` re-verified verbatim in the current rule (auditor script); kinds/gates/resolved_by/effects unchanged; two disjoint acyclic chains; no authoring-viewpoint phrasing (grep empty). PASS.

### override_declarations (revision_2)

Every `overwrite.superseded_clause` in the current charter is verbatim in the named base rule (auditor script: 8/8). Sentence sweep, deltas against revision 1 only:
- demurrage, goodwill, dispute credit: base "the slab position of a day is counted across the whole sequence of chargeable days" — was U in revision 1, now **D** (declared) in all three.
- lodged amount: the withdrawn-dispute sentence follows the base `one_dispute_per_invoice` dedup contract (F); `overwrite: []` still correct.
- late waiver: "whole amount still open … cleared" D (as before); "no dispute credit is written for this ground" F; "the same waiver clears a late invoice raised by the customer without a formal dispute" F for the formality point, and the gate sentence follows base structured eligibility `applies_to: [dnd_charge_waived]` (see O-8r); detention delegation F.
- All other sentence conclusions of revision 1 re-checked against the current text and unchanged.
No undeclared override remains.

### findings (revision_2, pre-reveal)

- Round-1 charter observations: O-1 closed in the charter (both invoice rules now fix the first/last billed day and exclude the clock_stopped_date; the schema parenthetical in `db_schema.json` `dnd_ledger.period_end_date` is unchanged but no longer has a rule gap to fill — residual schema wording only). O-2, O-3, O-4, O-5, O-6 closed (evidence above). O-7 unchanged (coverage note). O-8 → O-8r (explicit in the extended text; residual base tension, no task consequence expected). Rounding observation unchanged.
- New charter-global defect: none found.

### closing_checklist (revision_2)

Written 2026-09-13T05:03Z, after both round-2 comparisons (post-reveal; the revision_2 charter-global sections above were frozen at 05:00:44Z and are unchanged).

- Audit files one-to-one with the tasks (`0.md`, `1.md`) with `_difficulty.md` alongside; revision 1 preserved verbatim, revision 2 appended under `## revision_2` in each file. Every revision_2 comparison carries PASS on all three relationships:
  - task 0: policy self-consistency PASS; problem tree PASS; unique solution PASS (round-1 F-0.1, F-0.2, S-2 closed).
  - task 1: policy self-consistency PASS; problem tree PASS; unique solution PASS (round-1 F-1.1 closed).
- Charter observations: O-1, O-2, O-3, O-4, O-5, O-6 closed; O-8 made explicit (O-8r residual base tension, no task consequence); O-7, rounding, workflow-dataflow and lodged-amount-sensitivity observations carried with recorded reasons that re-check. No new defect in the charter, the tool module or either task.
- Extended policies fully covered; scopes pairwise disjoint over whole trees (GT `charter_scope`: task 0 = detention, demurrage, goodwill + workflow + 5 tools; task 1 = lodged, credit, late + 3 tools); exactly one workflow, claimed by task 0 only; task tools and GT closed; uuid8s independent and frozen (`task_tools.py` unchanged).
- Each task's tree: 2 prerequisites, both value_input, acyclic; difficulty-wide graph two disjoint chains, a DAG with no cross-task edge.
- Instantiation-stage gates on the final form: the coordinator's round-2 snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire — all exit 0 on the reworked files, charter hash `42c5200f…7235`); `check_traceability` deferred until KB publication by the coordinator's statement. Not re-run by the auditor (Step 0).
- Difficulty verdict (revision_2): **passes the source-layer audit** (policy self-consistency PASS + problem tree PASS + unique solution PASS for both tasks), subject to the deferred check_traceability gate outside this skill.

## revision_3

Round-3 re-audit (brief: no round-2 RED existed; after KB publication `check_traceability` went red on task 1 and the renderer flagged a parameter key inside a prerequisite condition; the source was changed; verify no new defect and no regression). Revisions 1 and 2 above are left untouched.

### charter_global_frozen (revision_3)

- Auditor: same independent auditor. Written 2026-09-13T07:32Z, before any round-3 GT field was opened; nothing here is derived from a round-3 GT.
- Inputs (re-measured): `dnd.extended.yaml` sha256 `c30652c47f10802ac4e5b8d52c5d331665cc7c5352fe4dab89551bad23984593` (changed from `42c5200f…`; still 1255 lines); `task_tools.py` `fb15c0746469034be2a9a07be14a72b3fccaff88859c6e0f875762a16b59a2a6` (changed from `d6dc8184…`); `blueprint/products/dnd.yaml` `e8d3f230…6640`, `share_tools.py` `144e1404…e610`, `db_schema.json` `29583758…fe3c` — unchanged; base section still byte-identical to the blueprint (diff empty); masked views `source_r3/0.masked.json` `561fed0f…02cf`, `source_r3/1.masked.json` `e6f4e498…5e25` — byte-identical to round 2.
- Both shared inputs changed, so every charter-global section is re-derived below.
- contamination_disclosure (charter level): the auditor has read the round-1 and round-2 GT of both tasks. No round-3 GT field, no published KB document, no scratchpad file outside `dnd_audit_self/` and `coord_7f3a/masked/dnd_billing_desk/source_r3/`, and no other scenario or difficulty was read.
- Entry conditions: round-3 gate snapshot supplied, now including `check_traceability` (all 8 exit 0). Complete.

Exact extent of the change (proved, not estimated):
- `dnd.extended.yaml`: replacing the one line "When demurrage and detention run on one merged clock, the record's detention row is booked before its demurrage row." by the round-2 line "Under clock_model combined the record's detention row is booked before its demurrage row." reproduces sha256 `42c5200f…7235`, the audited round-2 file. So the **only** charter change is `dnd_ext_final_demurrage_charge.prerequisite[0].condition`; rule, policy_source, compute, compute_basis, overwrite and every other policy are byte-identical to revision 2.
- `task_tools.py`: substituting the round-2 text of `book_dispute_credit_515e844f` (lines 220–257 of the audited file) for the current lines 220–260 reproduces sha256 `d6dc8184…5173`. So the **only** tool change is that one function; the other seven tools are byte-identical.

### policy_conflict_scan (revision_3)

The reworded condition is a prerequisite field, not a rule sentence: no subject, trigger, eligibility, time anchor, parameter, terminal state or cross-category read changed. The revision_2 scan (`_difficulty.md` › revision_2 › policy_conflict_scan) therefore holds over byte-identical policy text; its result stands: PASS, observations O-7 and O-8r.

### rule_compute_equivalence (revision_3)

Compute and rule text byte-identical to revision 2 (proved above). Mechanical sweep repeated on the current file: 80 verbatim checks (every `overwrite.superseded_clause` in its base rule, every `policy_source` in its rule, every `compute_basis` quotation in its rule), 0 misses. Auditor recomputation on the round-3 masked worlds reproduces 600.00 / 1445.00 / 216.75 and 395.00 / 210.00 / 255.00 with the same skip values (975.00, 146.25, 0.00; 0.00, 395.00). PASS.

### action_binding_and_uuids (revision_3)

`book_dispute_credit_515e844f`, new contract (lines 220–260):
- Signature: `dnd_id, invoice_event_id, outcome, amount_usd` — the `dispute_id` parameter is gone. Body: `lodged = ctx.find("dnd_disputes", dnd_id=dnd_id, invoice_event_id=invoice_event_id)`; `latest = max(lodged, key=created_at)`; the credit row is written with `dispute_id` = that latest dispute (or `None` if the line carries none), and `outcome` is written onto that dispute only if one exists. The only `Error:` return is still a missing record.
- **Business judgement in the tool?** No. The tool resolves an object (which dispute row the credit points at) by a fixed rule — the latest-lodged dispute on the named line, whatever its outcome — and checks nothing: not whether that dispute is `submitted`, not the dispute window, not the amount or outcome against the recomputation. It never refuses, never hints before writing, and books the credit even when the line carries no dispute (auditor simulation on task 1's masked world: with the lodge skipped, the credit attaches to the withdrawn dispute `6934fef4…`, overwrites its outcome to the value passed, and returns normally). The eligibility "a dispute the billed party has lodged on the invoice row and that is still submitted" remains wholly the agent's judgement, as the policy requires.
- **Second reading of which record the write attaches to?** No, in any state where the policy permits a credit. The policy selects "a dispute … lodged on the invoice row and that is still submitted"; the tool selects the latest-lodged dispute on that row. Base `one_dispute_per_invoice` (duplicate outcomes submitted/upheld/partially_upheld/denied; withdrawn excluded) forbids lodging a second dispute on a row while a non-withdrawn one stands, so every dispute lodged after a submitted one is impossible and every earlier one is withdrawn or decided: whenever a submitted dispute exists on the row, it is the latest-lodged one. The two selection rules therefore pick the same row whenever a credit is permitted; they diverge only in states where the policy forbids the credit (no submitted dispute), which is exactly the skip case above. Ties on `created_at` are excluded by the same dedup. The row-level target (`dnd_id`, `reference_event_id = invoice_event_id`) is still passed explicitly and unambiguous.
- The docstring's addition ("The dispute is identified by the invoice line alone: the one with the latest lodging time among the disputes filed against the line") describes this mechanic; it adds no confirmation, review, wait or business procedure outside the policy. The receipt now names the dispute decided, so the agent can read which dispute was decided without a separate id argument.
- `(target_tool, computes)` pairs unchanged; each still claimed by one policy. uuid8s unchanged and independent; `515e844f` was kept through the signature change (observation only: the name stays unique and non-derived; the skill's uuid rule — independent, frozen, not reused, not batch-derived — is still met).
PASS.

### prerequisite_graph (revision_3)

- Changed edge: demurrage ← detention. `condition` now "When demurrage and detention run on one merged clock, the record's detention row is booked before its demurrage row." `policy_source` (unchanged, verbatim in the rule) opens "Under clock_model combined the record's detention row is booked before its demurrage row, …". `parameter_schema.clock_model` defines combined as "on one merged clock", so the condition is the same proposition in plain words: neither strengthened nor weakened. kind, gate (`slab_offset`), resolved_by and effect unchanged. (The `effect` text still names `slab_offset` and "clock_model combined"; the renderer flag concerned the condition only; observation.)
- All other edges byte-identical; two disjoint acyclic chains; no authoring-viewpoint phrasing (grep empty). PASS.

### override_declarations (revision_3)

No rule or overwrite text changed (proved above); the revision_2 sentence sweep stands unchanged: no undeclared override.

### findings (revision_3, pre-reveal)

- New charter-global defect: none. The tool change moves no eligibility judgement into the tool and creates no second reading of the credit's target in any policy-permitted state; the condition rewording is semantically identical to its quoted rule sentence.
- Observations carried: O-7, O-8r, rounding; new observation O-9 (tool-side dispute resolution attaches a credit to a withdrawn or decided dispute if the agent books a credit the policy forbids — reachable only off the policy path, no scored consequence); the `515e844f` name kept through a signature change (no consequence).

### closing_checklist (revision_3)

Written 2026-09-13T07:35Z, after both round-3 comparisons (the revision_3 charter-global sections above were frozen at 07:32:56Z and are unchanged).

- Audit files one-to-one with the tasks, revisions 1–2 preserved, revision 3 appended in each file. Round-3 verdicts:
  - task 0: policy self-consistency PASS; problem tree PASS; unique solution PASS.
  - task 1: policy self-consistency PASS; problem tree **SOURCE-CHAIN RED** (F-1.2, a false terminal-state sentence in `prerequisite_closure.edge_load_bearing[1]`, present since revision 1 and missed by the auditor in revisions 1–2, made substantive by the round-3 tool rework); unique solution PASS.
- Charter and tool module: no new charter-global defect. The only changes (one prerequisite `condition`, one tool function) were isolated by reverted-hash proof; the condition is semantically identical to its policy_source; the dispute-credit tool resolves its dispute by a rule that coincides with the policy's selection in every state where a credit is permitted, and judges no eligibility. New observation O-9 (off-path attachment to a withdrawn/decided dispute).
- Coverage, scope disjointness, single workflow claimed by task 0, tool/GT closure, uuid8s: unchanged and holding (task 1 GT still calls exactly its three tools; `515e844f` kept through the signature change — observation only).
- Trees: two value_input prerequisites each, acyclic; difficulty-wide DAG.
- Gates on the final form: the coordinator's round-3 snapshot (8 gates exit 0, including check_traceability). Not re-run by the auditor.
- Difficulty verdict (revision_3): **not closed** — task 1 carries F-1.2. Findings reported only; no artifact edited, no fix proposed.

## revision_4

Round-4 re-audit (brief: verify the round-3 RED F-1.2 is closed, no new defect, nothing regressed). Revisions 1–3 above are left untouched.

### charter_global_frozen (revision_4)

- Auditor: same independent auditor. Written 2026-09-13T07:40Z, before any round-4 GT field was opened.
- Inputs (re-measured): `dnd.extended.yaml` sha256 `6ae8ac0188b147b60de2b94569d95b907df848b1e7520954a3a7865a2947dcca` (changed from `c30652c4…`; 1256 lines); `task_tools.py` `b6508afdc684c048e029045acbed9e8ee71264cf5fe978ce87b1c4f272a5f70c` (changed from `fb15c074…`); blueprint files unchanged (same hashes as revision 3); base section still byte-identical to the blueprint; masked views `source_r4/0.masked.json` `561fed0f…02cf`, `source_r4/1.masked.json` `e6f4e498…5e25` — byte-identical to rounds 2–3.
- contamination_disclosure (charter level): the auditor has read the round-1, round-2 and round-3 GT of both tasks. No round-4 GT field, no KB document, no scratchpad file outside `dnd_audit_self/` and `coord_7f3a/masked/dnd_billing_desk/source_r4/`, and no other scenario or difficulty was read.
- Entry conditions: round-4 gate snapshot (8 gates exit 0, traceability included). Complete.

Exact extent of the change (proved by reverted-hash):
- `dnd.extended.yaml`: restoring the round-3 text of the four `prerequisite[*].effect` fields (demurrage, goodwill, dispute credit, late waiver) reproduces sha256 `c30652c4…4593`. **Only the four effect texts changed**; rules, conditions, policy_sources, computes, compute_basis, overwrites and the workflow are byte-identical to revision 3.
- `task_tools.py`: restoring the round-3 docstring sentence of `book_dispute_credit_515e844f` ("… among the disputes filed against the line.") reproduces sha256 `fb15c074…a2a6`. **Only that docstring changed** — it now adds "whatever outcome it currently carries, and the outcome passed replaces that outcome"; the function body is byte-identical.

### policy_conflict_scan / rule_compute_equivalence / override_declarations (revision_4)

No rule, overwrite, compute or compute_basis text changed, so the revision_2/3 conclusions hold over byte-identical text: conflict scan PASS (O-7, O-8r); rule↔compute PASS; no undeclared override. Mechanical re-sweep on the current file: 80 verbatim checks, 0 misses. Auditor recomputation on the round-4 masked worlds reproduces 600.00 / 1445.00 / 216.75 and 395.00 / 210.00 / 255.00 with the same skip values.

### action_binding_and_uuids (revision_4)

- `book_dispute_credit_515e844f`: behaviour unchanged (revision_3 analysis stands: object resolution by latest lodging time on the line, no eligibility check, no refusal, coincides with the policy's "still submitted" dispute in every state where a credit is permitted). The docstring now states the off-path behaviour that O-9 recorded (a withdrawn or decided latest dispute is overwritten with the outcome passed). This is a description of the tool's own write, not a confirmation, review or business procedure; it neither refuses nor signals a missing prerequisite before the write. O-9: disclosed in the contract; behaviour kept, as claimed.
- All other tools byte-identical; `(target_tool, computes)` pairs and uuid8s unchanged. PASS.

### prerequisite_graph (revision_4)

The four `effect` texts, re-checked against their bindings and the tools that resolve them:
- demurrage ← detention: "Once the detention row is booked, on an export record whose demurrage and detention run on one merged clock the slab count of the demurrage days starts after that row's chargeable days, which moves every demurrage day to a later slab and changes the demurrage amount; on any other record the booked detention row leaves the demurrage amount unchanged." The second half is exact (`slab_offset` is 0 unless combined export). The phrase "moves every demurrage day to a later slab" is stronger than the compute: an offset shifts each day's *position*, and a day changes *slab* only when the shift crosses a slab bound (e.g. offset 1 with 3 demurrage days keeps all three in slab 1, and the amount is unchanged). The same overstatement stood in the revision_2/3 text ("moves every demurrage day to its later slab"), so it is not a regression; it is an observation (O-10) because `effect` describes the value change, the edge's existence and kind are carried by `condition`/`policy_source`, and the per-task load-bearing run is what proves weight. In task 0's world (offset 5, positions 6–11) every day does move to a later slab.
- goodwill ← demurrage, credit ← lodged, late ← credit: accurate plain-language restatements of the same value effects (invoiced/open amounts from nothing to the row's figures; the disputed amount now exists and bounds the credit; credits grow and the open amount falls by the credit).
- No parameter key remains in any `condition` or `effect` (scan for slab_offset, clock_model, invoiced_amount, disputed_amount, earlier_credits, chargeable_days, amount_usd, _usd: none). Round-3 effect-field observation: closed.
- Edges, kinds, gates, resolved_by, policy_sources unchanged; acyclic; no authoring-viewpoint phrasing. PASS.

### findings (revision_4, pre-reveal)

- New charter-global defect: none. O-9 disclosed (behaviour kept); effect-field observation closed; new observation O-10 (demurrage effect overstates "every day to a later slab", carried from earlier wording, no scored consequence). O-7, O-8r, rounding carried.

### closing_checklist (revision_4)

Written 2026-09-13T07:43Z, after both round-4 comparisons (the revision_4 charter-global sections above were frozen at 07:40:52Z and are unchanged).

- Revisions 1–3 preserved; revision 4 appended in each file. Round-4 verdicts:
  - task 0: policy self-consistency PASS; problem tree PASS; unique solution PASS.
  - task 1: policy self-consistency PASS; problem tree PASS (revision-3 F-1.2 closed); unique solution PASS.
- Changes this round isolated by reverted-hash proof: four `prerequisite.effect` texts in the charter; one docstring sentence in `book_dispute_credit_515e844f`. No rule, compute, condition, policy_source, overwrite or tool body changed. Effect-field observation closed (no parameter key in any condition or effect); O-9 disclosed in the tool contract (behaviour kept); new observation O-10 (demurrage effect's "every demurrage day to a later slab" is stronger than the compute in general, true in task 0's world, wording carried from earlier rounds). Carried: O-7, O-8r, rounding.
- Coverage, scope disjointness, one workflow claimed by task 0, tool/GT closure, uuid8s: unchanged and holding. Trees: 2 value_input prerequisites each, acyclic; difficulty-wide DAG.
- Skip-replay and world-fact sentences of both tasks checked word for word against the auditor's own replay on the current tools: all true.
- Gates on the final form: the coordinator's round-4 snapshot (8 gates exit 0, including check_traceability). Not re-run by the auditor.
- Difficulty verdict (revision_4): **passes the source-layer audit** — policy self-consistency, problem tree and unique solution PASS for both tasks.
