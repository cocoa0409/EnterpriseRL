# Policy-task audit — operating_line_servicing / charter-global

## charter_global_frozen

- Frozen: 2026-10-11T04:18:23Z (file mtime), before any task's GT was revealed. Auditor: erl-task-policy-audit agent (independent of the instantiating agent).
- Inputs and hashes (re-checked with `sha256sum` and matching the coordinator's HASHES.txt):
  - `tasks/operating_line_servicing/operating.extended.yaml` sha256=1b28195c369bc6e89310d08aa7a43babfa1a063cae442a5abc9b3d0d9af9c49a
  - `tasks/operating_line_servicing/task_tools.py` sha256=2d3f4744e492bf56eab4180a276cfa212968bbb454e5c9e6c60b211e814d33d6
  - `blueprint/products/operating.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/blueprint.yaml` (difficulties list), `blueprint/products/cropins.yaml` (coverage_level_pct / price_election_pct only), and the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS, DAYS, COUNT within_months, LATEST, CPARAM, CFIELD).
- Permitted: everything above. Masked and not read while this section was written: every task JSON field other than `frozen_time`, `user_scenario` and `initial_state` (and those only through the coordinator's `.audit_views/.../{0,1}.view.json`). No existing audit, revision or worklog was read.
- Entry conditions (Step 0): the gate snapshot came with the brief (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire green; check_cache_diff informational; check_traceability deferred because the KB isn't published yet). Masked views and hashes came with the brief. The entry conditions are met. The deferred traceability gate is noted, not counted as missing input.
- Base copy: `head -n 1514` of the extended charter is byte-identical to `blueprint/products/operating.yaml` (diff shows only the appended extended header). The base is verbatim.

### policy_conflict_scan

Six extended policies, one target tool each:

| policy | subject | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| operating_ext_certificate_lendable_value | operating_bbc_submitted | record_certificate_borrowing_base_37c8bf27 (agent) | borrowing_base_amount | [] |
| operating_ext_overadvance_fee | operating_draw | assess_overadvance_fee_10e059b9 (agent) | amount | cert (action, value_input) |
| operating_ext_borrowing_base_shortfall_paydown | operating_principal_payment | authorize_shortfall_paydown_62bf68fd (user) | amount | cert (action, value_input); overadvance fee (state, value_input) |
| operating_ext_late_charge_amount | operating_fee_assessed | assess_late_charge_706782fd (agent) | amount | [] |
| operating_ext_autodraft_enrolment_rate | operating_autodraft_change | enroll_autodraft_36bd3fb2 (user) | interest_rate | late charge (state, value_input) |
| operating_ext_most_available_advance | operating_draw | book_operating_advance_f71c3718 (agent) | amount | autodraft (state, value_input) |

Overlaps:
- Two policies share the subject `operating_draw`: overadvance fee and most-available advance. The first fixes a fee on an advance already booked, the second fixes the amount of a new phone advance. They have different target tools and computed fields, so they don't compete for one quantity. The most-available advance is never larger than the available credit, so it can never trigger an overadvance fee.
- The late charge and the overadvance fee both book `operating_fee_assessed` rows, with different fee codes (late_charge vs overadvance) and different tools. Neither policy counts the other's fee code. The shortfall reserve counts every unpaid fee, but that is a read, not a conflict.
- Cross-category reads are read-only. The only rows written are operating_lines, operating_transactions and operating_borrowing_base.
- Time anchors: certificate as-of/received dates; each bill's due date and grace; the term start (last_renewed_date, else opened_date); the first booking date (opened_date); and "today". Inside the extended charter they don't conflict. The conflicts with base are listed under `override_declarations`.
- Scope partition (inferred from the two worlds before reveal, to be confirmed at reveal): one tree is {certificate → overadvance fee → shortfall paydown}, the other is {late charge → autodraft enrolment → most-available advance}. The two trees are disjoint and together cover all six extended policies. No prerequisite edge crosses between them.

### rule_compute_equivalence

Check 2, policy by policy. Each `compute_basis` quotation was checked to be verbatim in its rule, and each rule sentence was swept back to a binding. Gaps found:

- operating_ext_certificate_lendable_value: equivalent. Every ladder tier is a rule sentence and a branch of its `decides` binding. The guarantee formula and the harvest-price fork match the rule.
- operating_ext_overadvance_fee:
  - The rule says the fee "is charged once against each advance that took outstanding principal past the line's available credit". It measures that credit against "the line's most recent certificate", and its prerequisite sentence says "the certificate that was the line's most recent when the advance was drawn". The compute defines the quantity for the **latest** advance only: `advance_amount = LATEST(... operating_draw)`, `latest_certificate_* = LATEST(operating_borrowing_base ...)` over all certificates. The rule's own definition, "the line's principal worked out from its transaction history ... less the advance itself", is likewise only the principal before the advance when that advance is the latest one.
  - So the rule promises an outcome for "each advance" that neither its own method nor the compute can produce for an earlier advance. That is an empty promise in the sense of check 2 (finding F1).
  - `DAYS(latest_certificate_as_of, advance_date) <= bbc_staleness_days` also accepts a certificate dated after the advance (negative days), where the rule says "before the advance". This has no effect on either world.
- operating_ext_borrowing_base_shortfall_paydown: equivalent.
- operating_ext_late_charge_amount:
  - `bill_ref` / `bill_due` take the latest-due bill without the rule's "that has passed its grace period" filter.
  - `returned_on_bill` sums `operating_interest_payment_return` rows whose `effective_date` equals the bill's due date, where the rule says "the interest payments applied to it ... that came back unpaid". The rule's sense is a link through `source_txn_id` to a payment on that bill. The compute uses a date coincidence instead.
  - Both are approximations, recorded as observation O3. On task 1's world both readings pick the same rows (see 1.md).
- operating_ext_autodraft_enrolment_rate: equivalent. The rule states the standard discount set twice ("The discounts are the program discount ... capped at rate_discount_cap_pct. The program, AutoDraft, relationship, equipment, membership and Country Home discounts are added together and the total is capped ..."). The two statements agree, so this is observation O5.
- operating_ext_most_available_advance: equivalent. `lending_limit` falls back to the commitment when a borrowing-base product has no certificate (`... and certificate_base`). The rule doesn't state that case, but base advance eligibility would stop such an advance anyway. Neither world is affected.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy. Six tools, six policies.
- uuid8 tails: 37c8bf27, 10e059b9, 62bf68fd, 706782fd, 36bd3fb2, f71c3718. No common prefix, no sequence, no tail reused or near-copied.
- No tool body reads the state of the line to refuse, check or hint: each body rounds the argument and writes. Owners: `authorize_shortfall_paydown_62bf68fd` and `enroll_autodraft_36bd3fb2` are `owner="user"`, the other four are `owner="agent"`.
- Docstrings name no other tool and state no position in a cross-action sequence. Literal ordering words do occur: "Afterwards the certificate lists the recorded amount" (line 18), "rounded half up ... before it is passed" in every amount argument, and "already delivered" (line 14). All of them describe the call's own effect or argument format, not an order between problems. Observation O6.
- Tool effect against base, where it matters: `book_operating_advance_f71c3718` always books "effective today" (`effective_date=today`). Base `operating_advance_eligibility` keeps "A request received on a business day after same_day_draw_cutoff_local_time Central time, or on a weekend or Federal Reserve holiday, takes effect the next business day." That sentence isn't superseded, so the tool can't carry a next-business-day effect (finding F4; consequence demonstrated in 1.md).

### prerequisite_graph

Check 7:
- `prerequisite` is filled in on every policy (`[]` on cert and late charge).
- Every `problem` is an extended policy id of this file, never a base policy and never itself.
- Edges: overadvance fee → cert; shortfall → cert; shortfall → overadvance fee; autodraft → late charge; advance → autodraft. The graph is acyclic: two components, each a DAG.
- Each `policy_source` is verbatim in its own policy's rule. Located:
  - overadvance fee: "The overadvance fee on an advance is fixed only after the association has recorded its own borrowing base on the certificate that was the line's most recent when the advance was drawn."
  - shortfall: "The shortfall paydown is not fixed until the association has worked out its own borrowing base for the line's most recent certificate and recorded it in place of the member's own figure." and "The shortfall paydown is fixed only after an overadvance fee stands against every advance that took the line past its available credit."
  - autodraft: "The contract rate set when AutoDraft is enrolled is fixed only after the records carry a late charge on every interest bill still unpaid when its grace period ended."
  - advance: "On a line whose AutoDraft was cancelled after returned payments, the amount of an advance is not fixed until the line's records show AutoDraft enrolled again."
- `form` is declared on every edge, and `fallback_reason` appears exactly on the two action-form edges.
- `kind` is `value_input` on all five edges, and every `gate` names a real binding of the blocked policy's compute: credit_before_advance, lendable_limit, reserve, autodraft_part, interest_reserve.
- Each `resolved_by` is the depended-on policy's `target_tool`.
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite` field.
- Condition against sentence, for the overadvance-fee edge: the sentence names "the certificate that was the line's most recent when the advance was drawn", which is a point-in-time object. The `condition` says "The line's most recent borrowing base certificate carries the borrowing base the association worked out", which is the current latest certificate. The two name different certificates whenever a certificate was received after the advance. This is part of finding F1.

### prerequisite_sentences

Check 6, four-point test per edge:

1. overadvance fee → cert (action form).
   - Connective "only after". It names the depended-on action in business words (the association recording its own borrowing base). No tool name, policy id or snake_case token.
   - The fallback reason holds: a certificate always carries a figure in `borrowing_base_amount`, and no field tells the member's figure from the association's. A state form could only say "carries the association's figure", which isn't record-visible.
   - Derivation: the sentence plus the certificate rows plus the certificate policy's own rule (it "records it on that certificate in place of any figure the member worked out") lead to `record_certificate_borrowing_base` on that certificate.
   - Scope: the sentence's point-in-time object differs from the condition's latest certificate (F1).
2. shortfall → cert (action form).
   - Connective "not ... until". Business action. The fallback reason holds for the same reason as edge 1.
   - The object is "the line's most recent certificate", which is the same object the certificate policy fixes ("the one with the latest as-of date"). One reading.
3. shortfall → overadvance fee (state form).
   - Connective "only after". The state is "an overadvance fee stands against every advance that took the line past its available credit": a fee row with the overadvance code pointing at each such advance, which is record-visible. Exactly one write in this difficulty produces that state: `assess_overadvance_fee`.
   - Scope: "every advance that took the line past its available credit" is only as determinate as the overadvance policy's measure of available credit for each historical advance. That measure has two readings for an advance drawn before a certificate arrived whose as-of date precedes the advance (F1), so the set of advances this sentence covers has two readings. The consequence is demonstrated in 0.md.
4. autodraft → late charge (state form).
   - Connective "only after". The state is "the records carry a late charge on every interest bill still unpaid when its grace period ended", which is record-visible. One write: `assess_late_charge`.
   - Scope: the late-charge policy charges "the line's interest bill with the latest due date that has passed its grace period" only, while this sentence covers "every" such bill. If two unpaid, uncharged bills had passed grace, the depended-on policy couldn't resolve the second one. That is a charter-level scope gap (observation O4). It has no consequence where only one such bill exists (see 1.md).
5. advance → autodraft (state form).
   - Connective "not ... until". The state is "the line's records show AutoDraft enrolled again" (`autodraft_enrolled` true), and only `enroll_autodraft` writes it.
   - The condition "AutoDraft was cancelled after returned payments" is read from the records: `autodraft_enrolled` false, together with two AutoDraft-channel payment returns in the rolling window under base `operating_evt_returned_payment`.

Checked on every edge:
- No rule carries a second wording, tool name or other problem's id for its dependency.
- No depended-on rule restates the sentence.
- No extended rule states a cross-problem order that grounds no declared edge.
- No base rule sentence grounds any edge here.

### override_declarations

Check 1, the finding half. Each extended policy was swept sentence by sentence against its `base_policy_refs`.

- operating_ext_certificate_lendable_value vs operating_borrowing_base_calculation:
  - The advance-rate sum is superseded and declared.
  - "Insured growing crops count only when ... (operating_msr_assigned_crop_policy at least 1); otherwise that class contributes zero": the extended rule follows this in its 0-tier. However, it narrows the qualifying policy from base's measure ("indemnity is assigned to the association") to "assigned to the association for this line". That is undeclared, and the two give different results for a member whose assigned policy names another of the member's loans (F2a).
  - The baseline rule ("plus the stated insured growing crops value times advance_rate_insured_growing_crops_pct") drops base's zero condition. That makes it a straw-man standard for lines without a qualifying policy (O1).
  - Receivable age, certificate frequency, and the line-status gate are inherited.
- operating_ext_overadvance_fee vs operating_advance_eligibility + operating_overadvance:
  - The fee sentence of operating_overadvance is superseded and declared.
  - Base operating_advance_eligibility says: "The available credit of a revolving product is the commitment (or, when borrowing_base_required is true, the lower of the commitment and the borrowing_base_amount of the most recent certificate) minus outstanding principal; the available credit of a non-revolving product is the commitment minus all advances booked in the current term". The base overadvance formula `revolving_limit: min(commitment_amount, borrowing_base_amount) if borrowing_base_required else commitment_amount` agrees with it.
  - The extended rule handles that quantity differently in two places:
    - Its standard sentence: "The available credit immediately before the advance is the commitment less the outstanding principal before the advance", with no borrowing base, even on a product that requires one.
    - Its fall-through: "as the commitment less the outstanding principal before the advance when the product is revolving and either requires no borrowing base or has no certificate that recent". On a borrowing-base product with a stale certificate this gives commitment less principal. Base gives the lower of commitment and borrowing base less principal, and base advance eligibility stops the advance outright.
  - The non-revolving tier "the commitment less every earlier advance booked on the line" also differs from base's "all advances booked in the current term".
  - No `overwrite` entry names operating_advance_eligibility. This is an undeclared override (F2b). In the situation "borrowing-base line, latest certificate as-of more than 45 days before the advance", base reaches a borrowing-base-limited credit and the extended rule reaches the commitment.
- operating_ext_borrowing_base_shortfall_paydown vs operating_payment_application + operating_borrowing_base_calculation:
  - The deficiency-cure sentence is superseded and declared.
  - The freeze on an uncured deficiency is inherited.
  - Payment designation is followed: "a principal paydown ... applied as designated, up to what is owed".
- operating_ext_late_charge_amount vs operating_evt_late_charge (and the other fee policies in refs):
  - The amount clause is superseded and declared. Grace, one charge per bill and the waivers are inherited.
  - "It is charged on an interest bill ... whose billed amount is not fully paid": base allows a charge on every such bill. The extended rule fixes the object as "the line's interest bill with the latest due date that has passed its grace period". That narrowing is undeclared, and it reaches a different conclusion whenever two unpaid bills have passed grace (F2c). It has no consequence where only one such bill exists.
  - The other refs (overadvance, returned payment, renewal, unused commitment, commitment change, booking fees) are untouched.
- operating_ext_autodraft_enrolment_rate vs operating_rate_setting + operating_evt_returned_payment + operating_autodraft_enrolment:
  - The program, AutoDraft, relationship and cap sentences are superseded and declared. Each `replaced_by` quotes only the first tier of its ladder, but the rule carries the full ladder.
  - Base "Losing the relationship discount because a Farm Real Estate loan closed takes effect only at the next renewal, never mid-term" is not superseded. The extended tier "zero when the member holds no Farm Real Estate loan in active status" reaches zero mid-term for a member whose FRE loan paid off during the term, where base keeps the discount. Undeclared (F2d).
  - The base-rate history, floor, rounding and the effective-day rule are followed.
- operating_ext_most_available_advance vs operating_advance_eligibility + operating_overadvance:
  - The available-credit and staleness sentences are superseded and declared.
  - The status gate, cutoff date, min_draw_usd, daily channel limits and disbursement options are inherited.
  - The same-day cutoff sentence is inherited, but the tool cannot honour it (F4).

### factor_ladders

Structure only: counts, labels and ladder realism. Whether each factor bears weight is judged in each task file. "Multi-source" below means every fork beyond the fall-through combines two or more conditions with and/or (the gate's definition). Where it matters, the note says whether those conditions sit on distinct records.

| policy | factors (effect) | param / method | multi-source (forks all compound) | cross_difficulty |
| --- | --- | --- | --- | --- |
| cert lendable value | growing_crop_advance_rate (p), growing_crop_value_counted (m), prepaid_inputs_seasonal_rate (p), late_certificate_market_value (m), bin_secured_stored_grain_rate (p), certificate_reporting_receivables_rate (p) | 4 / 2 | growing_crop_advance_rate (cropins coverage vs the line product's min coverage), growing_crop_value_counted, bin_secured_stored_grain_rate | bin_secured → equipment (a difficulty) |
| overadvance fee | overadvance_credit_measure (m), overadvance_repeat_percentage (p), overadvance_channel_points (p), overadvance_depth_points (p), land_relationship_fee_relief (p) | 4 / 1 | land_relationship_fee_relief only (credit measure's 2nd fork `not P('revolving')` is single) | relief → farmland (a difficulty: farm_real_estate_servicing) |
| shortfall paydown | unpaid_charges_reserve (p), repeat_overadvance_cushion (m), land_equity_allowance (p), assigned_indemnity_credit (p) | 3 / 1 | unpaid_charges_reserve (fees ledger and interest ledger: distinct records), land_equity_allowance, assigned_indemnity_credit | land_equity → farmland |
| late charge | returned_debit_charge_base (m), repeat_late_percentage (p), land_standing_share (p), line_tenure_share (p) | 3 / 1 | returned_debit_charge_base, land_standing_share | land_standing → farmland |
| autodraft rate | beginning_farmer_program_taper (p), autodraft_payment_record (p), land_relationship_scaling (m), equipment_relationship_points (p), membership_tenure_points (p), country_home_relationship_points (p) | 5 / 1 | program taper (cropins certification and line booking date), autodraft_payment_record (late-charge ledger and return ledger), land_relationship_scaling, equipment, country home | farmland, equipment, equity, homeloan |
| most-available advance | crop_cover_limit_share (p), program_season_share (p), past_due_interest_reserve (p), returned_payment_interest_reserve (p), returned_payment_hold (m), equipment_deferral_share (p) | 5 / 1 | crop_cover, season, past_due (interest ledger and the bill's due date), hold (two windows), deferral | deferral → equipment |

Every ladder has three tiers, and the tiers are pairwise disjoint as stated. Every tier is stated in its rule with its condition and its value or method, and every tier is a branch of its `decides` binding. Labels:
- The method factors use multipliers on intermediates (market-value haircut, cushion, hold) or change the algorithm (guarantee cap, credit measure, charge base, proportional relationship scaling). The gate's own definition admits a multiplier on an intermediate as a method, so none of these is mislabelled.
- No parameter factor changes an algorithm.

Ladder realism:
- **unpaid_charges_reserve** (shortfall): the fall-through is "nothing when no fee is owed". That tier reserves nothing for billed interest that is unpaid whenever no fee also happens to be owed, while tier 1 reserves the same interest once any fee is owed. The charter's own collection priority for the products that carry borrowing bases puts billed interest ahead of fees (`payment_application_order: [interest, fees, principal]` on Borrowing Base and Agribusiness lines). No lender publishes a borrowing-base reserve that counts unpaid interest only when a fee is outstanding beside it. This is an unreal ladder (F3a).
- **overadvance_credit_measure** (overadvance fee):
  - Tier 1 ("the lower of the commitment and that certificate's borrowing base, less the outstanding principal") is the base charter's own standard method for a borrowing-base product (operating_advance_eligibility / operating_overadvance formula). The factor's "baseline", "commitment less the outstanding principal before the advance", is not the charter's standard for that product. It is a straw man that ignores the borrowing base on a borrowing-base line.
  - Its fall-through, applied to a borrowing-base product with a stale certificate, is a treatment no borrowing-base lender publishes: base itself stops advances on a stale certificate.
  - So the factor varies nothing that the in-force standard doesn't already fix (F3b; per-task consequence in 0.md).
- **growing_crop_advance_rate** (cert): tier 2 (zero) restates base's own zero rule and the baseline drops it (O1). Tier 1 (70% at ≥80% coverage) is a genuine variation.
- **beginning_farmer_program_taper** and **autodraft_payment_record** select P(...) multiples, so all three tiers collapse to 0 on products whose program or AutoDraft discount is 0. The ladders are real only on products that offer the discount (O7).
- **growing_crop_value_counted**: its fall-through ("stated value when no assigned policy") always meets a 0 rate from the companion factor, so that tier never reaches the result (O8).

All other tiers are conditions and outcomes an agricultural lender plausibly weighs:
- staleness haircuts, in-season prepaid-input runoff, and bin-secured grain;
- reporting-discipline receivables rates;
- repeat and channel overadvance pricing;
- relationship relief;
- NSF-based late charge bases, repeat late percentages, and tenure/land relationship shares;
- program tapers and relationship points;
- insured-share, season-share and returned-payment holds;
- deferral shares.

### findings

- **F1 — SOURCE-POLICY RED (check 2 / check 6 scope). Consequence demonstrated in 0.md.**
  - Symptom: operating_ext_overadvance_fee promises a fee "once against each advance that took outstanding principal past the line's available credit". Which certificate measures an earlier advance's credit has two readings:
    - (a) "the certificate that was the line's most recent when the advance was drawn", i.e. on file at the draw (prerequisite sentence);
    - (b) the latest as-of certificate dated before the advance, whenever it was received. This reading is suggested by "the line's most recent certificate" and by the compute's LATEST-by-as_of.
  - The rule's own principal definition and the compute only define the latest advance.
  - The shortfall paydown's state-form sentence "an overadvance fee stands against every advance that took the line past its available credit" inherits both readings.
  - The condition of the overadvance-fee edge (current latest certificate) also differs in scope from its sentence (certificate at the draw).
  - Affects: overadvance-fee rule and compute; the shortfall prerequisite sentence; the overadvance-fee prerequisite `condition`. Bears on task 0.
- **F2 — SOURCE-POLICY RED, charter-level undeclared overrides.** Each has two passages quoted above that reach different conclusions in a stated situation. None changes a scored value on either task world, so neither task file carries a consequence for them.
  - (a) cert: policy assigned "for this line" vs base "assigned to the association";
  - (b) overadvance fee: available-credit standard and fall-through vs base operating_advance_eligibility (not named in `overwrite`);
  - (c) late charge: only the latest past-grace bill vs base "an interest bill" (each);
  - (d) autodraft: mid-term relationship loss vs base "only at the next renewal".
  - F2b is also the root of F3b.
- **F3 — SOURCE-FACTOR RED (ladder realism / honest baseline).**
  - (a) unpaid_charges_reserve fall-through. Bears on task 0's shortfall computation.
  - (b) overadvance_credit_measure: the baseline is not the in-force standard and the tier-1 value is the base standard method. Bears on task 0's overadvance-fee computation.
- **F4 — SOURCE-TASK root (tool/base conflict).** `book_operating_advance_f71c3718` books "effective today" whatever the request time. Base operating_advance_eligibility (inherited by operating_ext_most_available_advance) moves a request received after same_day_draw_cutoff_local_time to the next business day. Bears on task 1, whose clock is 14:05 CDT against StartRight's '14:00'.
- Observations (no demonstrated consequence):
  - O1: the cert baseline drops base's zero rule for growing crops.
  - O3: the late-charge compute approximates "payments applied to the bill that came back" by date, and doesn't filter the bill by grace.
  - O4: the autodraft sentence says "every" bill while the late-charge policy charges the latest bill only.
  - O5: the autodraft rule states its standard discount set twice.
  - O6: docstrings use literal "before"/"Afterwards"/"already" without stating any cross-action order.
  - O7: the program and AutoDraft ladders collapse on products that don't offer the discount.
  - O8: the inert fall-through of growing_crop_value_counted.

## closing_checklist

Written after both reveals (2026-10-11T04:20:22Z). This section is the only post-reveal content of this file. The charter-global section above is unchanged since its freeze, except that the freeze timestamp line was corrected to the file's mtime.

- One audit file per task (0.md, 1.md) sits alongside this file. This is the first revision, and each comparison section is on record. **Not every comparison carries a PASS:** task 0 is SOURCE-POLICY / SOURCE-FACTOR / SOURCE-TASK RED, and task 1 is SOURCE-TASK RED.
- Coverage and exclusivity hold, confirmed against `charter_scope`:
  - task 0 = {operating_ext_certificate_lendable_value, operating_ext_overadvance_fee, operating_ext_borrowing_base_shortfall_paydown};
  - task 1 = {operating_ext_late_charge_amount, operating_ext_autodraft_enrolment_rate, operating_ext_most_available_advance}.
  The scopes are disjoint, cover all six policies, and each claims its three tools. uuid8s are independent.
- Problem trees: each task has 2 prerequisite problems on 2 value_input edges, one owner=user write, and no cycle. The difficulty-wide graph is a DAG of two components.
- Factors:
  - Task 1: every computation passes with 4/6/6 factors, all bearing weight against honest baselines.
  - Task 0: the overadvance-fee computation fails the ≥1 method floor once overadvance_credit_measure is struck (F3b). The shortfall falls below 4 factors once unpaid_charges_reserve is struck (F3a).
- Gate re-run on the final form: not applicable. The difficulty doesn't close, so no final form exists to re-run on. The auditor didn't run the gates; the coordinator's snapshot is cited in § charter_global_frozen.
- **Status: the difficulty does NOT pass the source-layer audit.** Open items:
  - F1 → task 0 SOURCE-TASK (second paydown 62,873.03, or a handoff);
  - F3a and F3b → task 0 SOURCE-FACTOR;
  - F4 → task 1 SOURCE-TASK (advance effective date);
  - charter-level F2a–d (undeclared overrides with no task-world consequence in this bundle).

## revision_2

### charter_global_frozen (revision_2)

- Re-derived in full because `operating.extended.yaml` changed. Round 1: 1b28195c…c49a. Round 2: aac5aa1abdef19fe07d390f94d3d5517bb7e4af2fd39c0eb2b1a81a339aa86cb. `task_tools.py` is unchanged (2d3f4744…33d6), so § action_binding_and_uuids carries forward from round 1 on the tool hash, except its F4 note, re-judged below.
- Base copy re-checked: still byte-identical to `blueprint/products/operating.yaml`.
- Written before either round-2 GT was revealed. Inputs: the round-2 charter, the unchanged tool module, the rebuilt views (0.view.json 7ca01113…cad77, 1.view.json 9b844dd4…10431; both hashes match HASHES.txt), and the gate snapshot from the brief (all green, traceability deferred). Entry conditions are met.
- The reworker's closure claims were not taken on trust. Each item below was checked against the artifact text.
- contamination_disclosure: the auditor has seen the round-1 GT of both tasks (revealed in round 1). That knowledge is disclosed. It was not used as evidence: every figure below was recomputed from the round-2 charter and views.

### Round-1 items re-checked against the round-2 charter

- **F1 (overadvance scope / certificate reading): CLOSED.**
  - The overadvance rule now reads: "This rule prices the fee on the line's latest advance; every earlier advance was priced, or found within its available credit, on the day it was drawn. The overadvance fee on the line's latest advance is fixed only after the association has recorded its own borrowing base on the line's most recent certificate."
  - The prerequisite sentence and its `condition` now name the same object, the line's most recent certificate.
  - The shortfall sentence is now "an overadvance fee stands against the line's latest advance whenever that advance took the line past its available credit", which matches the depended-on policy's scope.
  - The compute (LATEST draw, LATEST certificate) now equals the rule's promise.
  - The rule's historical premise ("every earlier advance was priced, or found within its available credit") is a world assertion. It is verified per task (0.md revision_2).
- **F2a: CLOSED by declaration.** A second `overwrite` entry names the base sentence "Insured growing crops count only when ... (operating_msr_assigned_crop_policy at least 1); otherwise that class contributes zero". Its replacement is the "for this line" definition. The merged reading is unique: the zero rule lives in the extended ladder and in the baseline.
- **F2b: CLOSED.**
  - The available credit is now "On a revolving product ... the lending limit less the outstanding principal before the advance, the lending limit being the lower of the commitment and the borrowing base on the line's most recent certificate when the product requires a borrowing base and the commitment when it does not; on a product that is not revolving, which runs a single term, it is the commitment less every earlier advance booked on the line."
  - That agrees with base operating_advance_eligibility. A non-revolving Seasonal Operating Loan "matures and a new loan is applied for", so "every earlier advance on the line" equals "advances booked in the current term".
  - The stale-certificate fall-through is gone. No declaration is needed, because nothing conflicts any more.
- **F2c: CLOSED by declaration.** The late-charge `overwrite` now names "It is charged on an interest bill ... whose billed amount is not fully paid by then (operating_msr_bill_paid below the bill amount)". The replacement is "A line carries at most one late charge for a run of unpaid bills ... an older bill still unpaid at that point carries no further late charge". That is a no-pyramiding rule lenders really use, and the merged reading is unique.
- **F2d: CLOSED by declaration.** The autodraft `overwrite` names "Losing the relationship discount because a Farm Real Estate loan closed takes effect only at the next renewal, never mid-term."
- **F3a: CLOSED.**
  - The reserve ladder is now: billed interest unpaid and the latest bill's due date passed → unpaid interest plus unpaid fees; otherwise fees owed → fees alone; otherwise nothing.
  - Past-due billed interest is now reserved whether or not a fee is owed, so the unreal fall-through is gone.
  - The tiers are disjoint (compute `interest_past_due` / `not interest_past_due and fees_unpaid > 0` / else). They are multi-source over distinct ledgers plus the bill's due date.
- **F3b: CLOSED.**
  - overadvance_credit_measure is removed. Its content is now the standard sentence of the rule and the baseline, so the baseline equals the base charter's standard.
  - A new method factor, `technical_overadvance_share`, replaces it: the fee is taken at 0.5 or 0.75 of itself when the advance was drawn ≤3 or ≤10 days after the most recent certificate was received, and whole otherwise or when the advance came before receipt.
  - The ladder is real: leniency for an advance drawn on a member's own unverified certificate. It has three disjoint tiers stated in the rule and implemented in compute (`days_after_receipt`, `unverified_share`). The multiplier label is honest (method).
  - The computation now has 5 factors: 4 parameter, 1 method.
- **F4 (tool always books "effective today"; base same-day cutoff inherited): the charter-level shape persists.** task_tools.py is unchanged, and the advance policy's `overwrite` still doesn't touch the cutoff sentence. It now carries no task consequence (task 1's clock moved to 10:05 CDT; see 1.md revision_2). Reclassified as **observation O9**: a latent tool/base gap for any request after the product cutoff.
- **O1: CLOSED.** The cert `baseline.rule` and `factors[growing_crop_advance_rate].baseline` now carry the zero condition ("... when the member holds a crop insurance policy ... at a coverage level of at least crop_insurance_min_coverage_pct and nothing for that class when the member holds none").
- **O3: CLOSED.** The late-charge compute now links the return through the bill's AutoDraft debit: `debit_on_bill` = LATEST autodraft interest payment with source_txn_id the bill, and `returned_on_bill` / `return_reason_on_bill` are keyed by `source_txn_id=debit_on_bill`. The rule now speaks of "the bill's AutoDraft debit", matching the compute. Choosing the latest-due bill now equals the rule's object ("the line's interest bill with the latest due date"); the grace test is the inherited eligibility gate.
- **O4: CLOSED.** The autodraft sentence is now "a late charge on the line's latest interest bill whenever that bill is still unpaid after its grace period". It matches the late-charge policy's object and its own `condition`.
- **O5–O8: unchanged, as the reworker claims.**
  - O5: the autodraft rule still states its standard discounts twice. It is consistent.
  - O6: docstrings unchanged.
  - O7: the program and AutoDraft ladders still collapse on products that don't offer the discount.
  - O8: the inert fall-through of growing_crop_value_counted is still there.
  - All remain observations.

### New-defect sweep over the round-2 charter

- **Override sweep:** no new undeclared deviation. The new technical-overadvance share and the rewritten reserve are new extended rules, not restatements of base quantities.
- **rule ⇄ compute:**
  - Overadvance: `lending_limit_before` falls back to the commitment when a borrowing-base product has no certificate. The rule doesn't state that case, and base advance eligibility would block such an advance. This is observation O10, with no task consequence.
  - Shortfall: `interest_past_due` = unpaid > 0 and DAYS(latest due, NOW) > 0, which is the rule's "the due date of the line's latest interest bill has passed" ✓.
  - Late charge: tier 3's "billed amount less the payments applied" counts a returned non-AutoDraft payment as paid. That falls inside the declared superseded clause, so it is a deliberate narrowing (observation O11, no task consequence).
  - Everything else is equivalent.
- **Prerequisite graph and sentences (checks 6 and 7):**
  - Same five edges, acyclic. Each `policy_source` is verbatim in its own rule.
  - Each `condition` now has the same scope as its sentence.
  - Connectives: "only after", "not ... until", "only after", "only after", "not ... until".
  - Both action-form fallbacks still hold. Every state is produced by exactly one write.
  - No second wording, tool name or id appears.
- **Factor structure:** cert 6 (4p/2m), overadvance 5 (4p/1m), shortfall 4 (3p/1m), late charge 4 (3p/1m), autodraft 6 (5p/1m), advance 6 (5p/1m). Every ladder has three tiers stated in the rule and implemented in compute, the tiers are distinct in outcome, the labels are honest, and every baseline is the base standard for its input.
- **Shortfall reserve, new edge case:** "past due" is defined by the latest bill's due date, so an older overdue bill sitting beside a newer, not-yet-due bill is ignored. On borrowing-base products that state normally comes with a 15-day past-due suspension first. Observation O12; no task world has it.

### findings (revision_2)

- Round-1 REDs F1, F2a–d, F3a and F3b are closed in the charter text, as set out above.
- F4 is reduced to latent observation O9.
- No new charter-level RED was found.
- Per-task closure of the consequences is judged in 0.md and 1.md revision_2.

### closing_checklist (revision_2)

Written after both round-2 reveals (2026-10-11T10:21:43Z).

- Audit files: one per task, alongside this file. Round-1 text is preserved, and revision_2 is appended to each. Both revision_2 comparison sections carry PASS on all four relationships.
- Coverage and exclusivity: confirmed against `charter_scope`.
  - task 0 = {certificate, overadvance fee, shortfall paydown};
  - task 1 = {late charge, AutoDraft rate, most-available advance}.
  The scopes are disjoint and together cover all six policies. Task tools and GT are closed. The uuid8s are unchanged and independent.
- Problem trees: each has 2 prerequisite problems on 2 value_input edges, one owner=user write, and no cycle. The difficulty graph is a DAG of two components.
- Factors: 6/5/4 factors in task 0 and 4/6/6 in task 1, each computation with ≥2 parameter and ≥1 method. Each task has ≥1 multi-source and ≥1 cross-difficulty factor on seeded rows. Every ladder has three tiers, stated in full, distinct in outcome and realistic. Every factor bears weight against an honest baseline, and each all-baseline fall-back is definite and differs from gold.
- Gates on the final form: the coordinator's post-rework snapshot is all rc=0 (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; CACHE-DIFF informational; traceability deferred until the KB is published). The auditor did not run the gates itself.
- **Status: the difficulty PASSES the source-layer audit at revision_2.**
- Observations carried forward (no task consequence):
  - O5–O8 (round 1);
  - O9: `book_operating_advance_f71c3718` cannot book a next-business-day advance for an after-cutoff request;
  - O10: the overadvance lending limit falls back to the commitment when no certificate exists;
  - O11: a returned non-AutoDraft payment counts as paid in the late-charge base;
  - O12: the shortfall reserve's "past due" is keyed to the latest bill only.
