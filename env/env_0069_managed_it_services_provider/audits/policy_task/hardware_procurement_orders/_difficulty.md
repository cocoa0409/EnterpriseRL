# Policy-task audit — hardware_procurement_orders / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-18 before any task GT was revealed; auditor: independent erl-task-policy-audit agent (not the instantiator).
- `hardware.extended.yaml` sha256 42125f76239ce54c9ada3c6dafc4e9cf219ca9807b9b47c0d7b0fb0499512328; `task_tools.py` sha256 fc9d6fee5f1d48fe0fd7a82848e9d00a3feb523f8aebd17eddaec8861f53ab25 (both re-hashed on disk, equal to the brief).
- Read: blueprint/ (blueprint.yaml, db_schema.json, share_tools.py, products/hardware.yaml + the managed/licensing/security/project charters for cross-product checks), the extended charter, task_tools.py, audits/render_source/XF_recipe.md, erlbench/scoring.py + engine.py (unlock/order semantics), the two masked views r1/0.view.json (e8caee7d…) and r1/1.view.json (9cffabb4…).
- Masked and not read: tasks/*.json, plan.md, worklog.md, every `_masked_keys` field (charter_scope, computations, db_closure, design_rationale, evaluation_criteria, prerequisite_closure, required_documents, solvability_contract). No recursive grep touched tasks/.
- Not readable within the brief's read domain: the compute-DSL implementation (it lives under skills/, outside the domain), so MONTHS()/XCOUNT()/CFIELD() semantics are taken from the rule text; see observation O8.
- Entry conditions: gate snapshot supplied (7 gates rc=0, check_traceability deferred), masked views with hashes supplied. Entry conditions met.

### policy_conflict_scan
Seven extended policies, two trees:
- Endpoint tree: `hardware_ext_endpoint_cancellation_fee` (P1, user, sign_order_cancellation_55862425) -> `hardware_ext_staged_requote_total` (P2, agent, revise_staged_quote_eb003c71) -> `hardware_ext_endpoint_approval_deposit` (P3, user, sign_quote_approval_0590c0d2).
- Infrastructure tree: `hardware_ext_infrastructure_cancellation_fee` (P4, user, sign_infrastructure_cancellation_1779b7d3) -> `hardware_ext_cancelled_deposit_credit` (P5, agent, post_deposit_credit_9245a342) -> `hardware_ext_infrastructure_approval_deposit` (P7, user, sign_build_approval_1b1ae884) <- `hardware_ext_lapsed_quote_reissue` (P6, agent, reissue_lapsed_quote_93c9a091).
- Subjects/order types are partitioned: P1 Standard Endpoint after-PO cancellation; P4 Network/Server after-PO cancellation; P5 Network/Server deposit credit; P2 Staged re-quote of a cancelled endpoint line; P6 re-issue of a lapsed Network/Server quote; P3 Standard/Staged approval deposit within credit limit; P7 Network/Server approval deposit within credit limit. Sibling pairs (P1/P4 on the cancellation sentence, P2/P6 on the two pricing sentences, P3/P7 on the deposit sentence) name each other's case in their replaced_by (exception: P5, finding CG-4).
- Credit-exposure base rule: P3 and P7 both exclude over-limit approvals ("is prepaid under the credit-exposure rule and is not priced here") — compatible with hardware_agg_credit_exposure.
- Time anchors: every DAYS/MONTHS/XCOUNT is anchored at the write day (NOW) or at record dates; no anchor conflicts with base temporal_basis (validity counted from quote_date day 0, inclusive — P2/P6 re-date to today, so base approve_in_validity holds for P3/P7 approvals).
- Cross-category read boundary: reads are status/variant/go_live_date/seat_count of managed, status/variant of licensing, security and project, and managed_billing late-fee rows — all declared in `cross_category`.
- Scope exclusivity: the two trees share no policy and no target tool; jointly they cover all seven extended policies (to be confirmed against charter_scope after reveal, in closing).
Conflicts found: none that yields two numbers on one quantity at policy level beyond the findings below.

### rule_compute_equivalence
- Mechanical sweep (scratch, whitespace-normalised): every `compute_basis` value of all 7 policies is verbatim in its own rule; every `baseline.rule` sentence is verbatim in its rule; every prerequisite `policy_source` is verbatim in its rule. Compute bindings without a basis entry are plain field reads (b_units, b_quote_total, b_unit_price, b_unit_cost, b_inf_deposit_paid) whose wording sits in the rule's standard/combination sentence.
- Ladders: every `factors[].ladder` tier is a branch of its `decides` binding and a sentence of the rule, and every branch of each decides binding is a stated tier (checked per factor for all 34 factors).
- Rounding: every rule says "rounded half up to the cent once, on the final amount"; every compute wraps only `result` in RND(…, 2). Matches.
- Windows: late-fee counts "fewer than twelve whole months before" <-> XCOUNT(within_months=12, date_field=posted_date, event_type=managed_late_fee). Tenure "whole months … a month completing only once the day of the month reaches the go-live date's day number" <-> MONTHS(go_live, NOW). PO age "calendar days from PO date to the day the cancellation is recorded" <-> DAYS(order_placed_date, NOW). Lapse "from quote_date plus quote_validity_days to the re-issue day" <-> DAYS(quote_date, NOW) − quote_validity_days.
- Caps: P4 "the built fee never exceeds the deposit paid on the order, the sum of the payments on its ledger" <-> MN(…, SUM(hardware_payment)); P2 "the lesser of that cancellation fee and credit_cap_per_unit_usd for each unit" <-> MN(b_cancel_fee, K*b_units); P5 "counted up to the deposit invoiced" <-> MN(SUM payments, SUM deposit invoice).
- Absent-record branches (B13): all stated and implemented (no go-live -> tier/0; no seats -> 0; no Sentinel -> named tier; no in-progress project -> named tier; no cancellation date -> 9999/0 with "nothing … for an order not yet cancelled").
- P2 object binding: the rule reads every order field from the cancelled order ("units of the cancelled line", "the cancelled order's unit_price_usd", "when the cancelled order was quoted with rush", "the cancelled order's cancellation date", "the cancellation fee charged on the cancelled order"), while compute writes F('…')/SUM('hardware_billing',…) with no object argument and the tool's primary id is the staged quote. Whether compute's F/SUM resolve to the source (cancelled) order is not visible in the charter; to be checked against computations.expected after reveal (task 0 file).
- Same-day ties (B11): see CG-3 (project in_progress first-match). Managed reads are safe (managed charter: "A client organisation holds at most one ClearPath agreement at a time"), security reads are safe (security_agg_multi_holding max_per_customer 1), licensing reads are EXISTS.

### action_binding_and_uuids
- (target_tool, computes) pairs: (sign_order_cancellation_55862425, fee_usd) P1; (revise_staged_quote_eb003c71, quote_total_usd) P2; (sign_quote_approval_0590c0d2, deposit_usd) P3; (sign_infrastructure_cancellation_1779b7d3, fee_usd) P4; (post_deposit_credit_9245a342, credit_usd) P5; (reissue_lapsed_quote_93c9a091, quote_total_usd) P6; (sign_build_approval_1b1ae884, deposit_usd) P7 — each claimed once.
- uuid8s 55862425, eb003c71, 0590c0d2, 1779b7d3, 9245a342, 93c9a091, 1b1ae884: pairwise distinct, no shared prefix/suffix, no sequence; consistent with independent generation.
- No tool body validates a prerequisite, status, variant or window (every body does find -> create/update only). No docstring names another tool or a position in a sequence; docstrings carry format descriptions only (INV-/HQ- + 6 digits, YYYY-MM-DD), no example values (XF D19 clean); every claimed effect is in the body.
- Observation O5: the docstrings of sign_order_cancellation_55862425 ("their own hardware order"), sign_quote_approval_0590c0d2 ("a hardware quote") and reissue_lapsed_quote_93c9a091 ("unsigned hardware quote") are wider than their policies' scopes and cover the infrastructure cases whose policies bind sign_infrastructure_cancellation / sign_build_approval; the bodies of each pair are write-identical (same make_id prefixes), so a mis-pick gives the GT hash but fails erlbench.scoring.check_order (the required `before` tool is never called). Not RED: each policy names its own tool, so no policy reading selects the generic tool for an infrastructure order.
- Observation O6: docstrings say "cancelled after its purchase order" — this names the cancellation_stage value, not a tool sequence.

### prerequisite_graph
- `prerequisite` present on all 7 (P1, P4, P6: []). Edges: P2->P1 (value_input, gate b_cancel_fee), P3->P2 (value_input, b_quote_total), P5->P4 (value_input, b_bench_days), P7->P6 (value_input, b_quote_total), P7->P5 (state_gate, hardware_billing.event_type). All `problem` ids are extended ids of this file, none self, none base. Acyclic (two DAGs, no shared node).
- All `form: state`, no `fallback_reason` (correct for state form).
- policy_source verbatim in own rule: yes for all 5 edges (mechanical sweep).
- resolved_by = depended-on target_tool for all 5; each effect genuinely holds (tool bodies set status/cancelled_date/fee row; quote_date/quote_total; order_credit row).
- value_input gates name real bindings (b_cancel_fee, b_quote_total, b_bench_days exist in compute); the state_gate names a field rather than an eligibility id (extended policies carry no eligibility list) — observation only.
- Observation O3: two `condition` texts are stronger than their sentence: P3 edge condition adds "carrying the revised quote_total_usd" and P7 edge 1 adds "carrying the re-issued quote_total_usd"; the sentences name only the quote date. No consequence: the only write of this difficulty that re-dates each quote also sets its total.
- No authoring-viewpoint phrasing in any prerequisite field.

### prerequisite_sentences
Four-point test per edge:
- P2->P1: "A re-quote of a cancelled endpoint line is priced only after the order it re-quotes shows status cancelled and its ledger carries the cancellation fee charged on it." Connective "only after"; record-visible state (status cancelled; cancellation-fee ledger row); no tool/id/snake_case; strength = condition. One write brings it about: an after-PO cancellation of a Standard Endpoint Order -> P1 (P4's scope is Network/Server only). Derivation: re-quote of the laptop line -> needs that line cancelled with its fee booked -> the policy that books an endpoint after-PO cancellation and its fee is P1 -> P1's tool.
- P3->P2: "The deposit on a staged quote that takes over a plain endpoint line cancelled after its purchase order is not fixed until that staged quote carries a quote date no earlier than the cancellation date of the line it takes over." "not … until"; state = staged quote_date >= line's cancelled_date; one write: P2 (re-dates the staged quote to the revision day; P6 is infrastructure-only). Observation O10: the scope phrase "a plain endpoint line cancelled after its purchase order" describes the line as already cancelled (P7 edge 2 uses "takes over an ordered infrastructure order"); see task 0 file.
- P5->P4: "The deposit credit of a cancelled infrastructure order is fixed only after the order shows status cancelled and its ledger carries the cancellation fee charged on it." Passes; one write: P4 (P1 is Standard-Endpoint-only).
- P7->P6: "The deposit of an infrastructure approval is fixed only after the quote being signed carries a quote date that keeps it within its validity period on the approval day." Passes; one write: P6 (P2 is Staged-only). Coincides with base approve_in_validity, compatible.
- P7->P5: "An infrastructure approval that takes over an ordered infrastructure order of the client is not recorded until the order it takes over carries an order credit returning its paid deposit." Passes; one write: P5 (only tool creating hardware_order_credit). Observation O2: under P5's fall-through credit form the order credit offsets the fee and returns none of the deposit, so "an order credit returning its paid deposit" is literally false for that form; no effect on task 1 (form 1 there).
- Depended-on rules (P1, P4, P5, P6, P2) never restate the blocked sentence; no rule names a tool, policy id or another problem's route.
- Observation O4: P5's opening sentence "…once the order has been cancelled after its purchase order…" is a second (action-form, weaker) wording of the P5->P4 dependency; no demonstrable second conclusion (P5 is scoped to after-PO cancellations, which always carry a fee row from P4's tool).
- No rule states an undeclared cross-problem order. Base sentence "The purchase order may be placed only after any required deposit has been paid in full" grounds no edge here.

### override_declarations
Sentence-by-sentence against each base_policy_refs entry:
- hardware_cancellation (P1, P4, P5): S1 before-PO free cancellation — followed (out of scope). S2 after-PO only where cancellable_after_po — followed (true for Standard, Network, Server). S3 fee + deposit treatment — overwritten by P1 (Standard), P4 (Network/Server fee, deposit handed to P5), P5 (Network/Server deposit credit), each with replaced_by restating the in-force text for other cases. S4 Special-Order non-cancellable / S5 shipped not cancellable — followed.
- hardware_client_signed_requests (P1, P3, P4, P7): e-signature, verified contact — followed (tools are owner=user and create a signed client request).
- hardware_quote_and_pricing (P2, P6; P3, P7 cite it): unit-price sentence and quote-total sentence overwritten by P2 and P6 with sibling exclusions; "must reach min_order_value_usd and quantity may not exceed max_units_per_order" lies outside the superseded clause and is followed (4 <= 100; 3 <= 100); deposit-required sentence followed by P3/P7; validity/revision sentence followed (quote_revision_resets_validity true); entitlements followed.
- hardware_approval_and_purchase_order (P3, P7): validity/signature, counting, price protection followed; deposit sentence overwritten; PO-after-deposit and configuration-sheet sentences followed.
- hardware_agg_credit_exposure (P3, P7): over-limit -> prepaid, explicitly excluded from scope; "Orders within the limit follow the order type's normal deposit rule" — that normal rule is the declared overwrite.
- hardware_agg_multi_holding (P2, P6): followed; P2 carries another order's unit price and fee credit into the staged quote, which the base "its own price" sentence does not forbid (observation only).
- Disguised forms: no anonymous intermediate, 0/1 multiplier or dropped branch found beyond CG-1 (gating of whole factors by a method tier). No author text calls base output "wrong".
- XF C16 (scoped replaced_by): all overwrites carry "and only for such …" and restate the in-force text. C17: see CG-4. C18: no empty overwrite, no rule deferring to a retired clause.

### factor_ladders
Per policy (P = parameter, M = method; multi-source = every non-fall-through tier is a conjunction/disjunction over distinct records):
- P1 (4: 3P+1M): po_age_build M (date; 3 tiers: admin/unit | pct·total+freight/unit | pct·total); tier_fee_rate P (managed; 6% | 8% | 10%); tenure_return_freight P (managed date; 0 | 12 | 25 per unit); arrears_admin_charge P (managed ledger; 50 | 25 | 0). Cross-difficulty: managed. No multi-source factor in P1.
- P2 (5: 4P+1M): autopilot_staging_rate P multi-source (licensing ∧ managed; 55 | 70 | 95); tenure_handling P (0 | 15 | 25); tier_rush_rate P (0 | 75 | 150); fee_credit_basis M multi-source on tier 1 (date ∧ managed tier; whole fee | min(fee, 25·units) | none); edr_hardening_rate P (security; 0 | 8 | 15). Cross-difficulty: licensing, managed (security read, labelled null).
- P3 (4: 3P+1M): tier_deposit_share P (10 | 20 | 25 %); arrears_deposit_points P (15 | 5 | 0 pts); sentinel_deposit_relief P (5 | 2 | 0 pts); tenure_deposit_build M (cost·units | service charges + pct·goods | pct·total).
- P4 (6: 5P+1M): bench_stage_build M (admin/unit | pct·total + rework/unit | pct·total); infra_tier_rate P (9 | 12 | 15); project_scope_points P (2 | 1 | 0); arrears_fee_points P (3 | 1 | 0); covered_seat_points P (1.5 | 0.5 | 0); sensor_rework_rate P (55 | 35 | 20). Cross-difficulty: managed, project.
- P5 (5: 4P+1M): standing_credit_form M multi-source tier 1 (managed tier ∧ late-fee ledger; D | D − retentions | min(D, F)); bench_time_retention P (staging·qty | half | 0); tenure_handling_retention P (handling | half | 0); expedite_retention P (rush | half | 0); project_coordination_retention P (60 | 30 | 0). Cross-difficulty: managed, project.
- P6 (5: 4P+1M): xdr_bench_staging_rate P multi-source (security ∧ managed; 95 | 120 | 145); sensor_template_rate P (25 | 10 | 0); reissue_tenure_handling P (0 | 20 | 35); reissue_tier_rush P (0 | 75 | 150); lapse_charge_basis M (60/unit | 1.5%·goods | none).
- P7 (6: 5P+1M): infra_deposit_share P (35 | 40 | 50); infra_arrears_points P (10 | 5 | 0); infra_sentinel_relief P (5 | 2 | 0); infra_project_relief P (5 | 2 | 0); infra_seat_relief P (3 | 1 | 0); infra_relationship_build M (cost·units | service + pct·goods | pct·total).
- Every ladder has 3 pairwise-disjoint tiers with distinct outcomes, every tier is in the rule and in compute, every `decides` is an input (none is `result`), binding sets are disjoint, and every fall-through equals the factor's `baseline`. Mechanical check: no factor binding reads another factor's binding (XF A1 direct-read clean); factor ids are not substrings of any tool name (A7 clean).
- Method labels are honest (each method tier changes the formula's shape). A6 pairwise table — tiers coincide only on sub-domains: P1 tiers 2/0 when freight is 0 (tenure >= 60 months); P2 tiers 2/1 when fee <= 25·units; P5 tiers 2/1 when the retention sum is 0. None coincides on its whole reachable domain.
- Gating through another factor: CG-1. Assembly sentences: CG-2.
- Realism (observation O1, judgement not demonstrable as "no business does this"): ClearPath tenure as a condition on endpoint return freight (P1); ClearPath late fees as an admin charge on a hardware cancellation (P1); Sentinel tier as a deposit relief (P3, P7 — a security subscription is not a credit signal); a 35/unit "rework" for non-XDR Sentinel tiers that have no network sensor to strip (P4); a new per-unit sensor-template charge appearing only on re-issue (P6) while the lapsed unit price is carried over unchanged (P6); P5 bench retention of the full staging fee on top of P4's bench rework charge, both triggered by the same PO age >= 7 days. The remaining ladders (Autopilot staging via Intune-capable M365 plans, EDR bench hardening vs subscription-deployed agent, tier-based fee/deposit shares, late-fee points, tenure build of deposits, lapse re-validation charges, coordination retained unless billed through a project) are ones a VAR/MSP plausibly runs.

### findings
- **CG-1 SOURCE-FACTOR RED (XF A1/A3 "no factor is gated through another factor"), charter-level.** Symptom: six parameter factors contribute only inside a non-fall-through tier of a method factor. Members: P1 tenure_return_freight (used only when po_age_build selects tier "at least allocated_after_days": result `… + (f_freight_per_unit * b_units if f_fee_build == 2 else 0)`); P4 sensor_rework_rate (`(f_inf_rework * b_units if f_inf_build == 2 else 0)`); P5 bench_time_retention, tenure_handling_retention, expedite_retention, project_coordination_retention (used only in `f_credit_form == 1`). Root cause: the gated quantity is not one the baseline defines — P1 baseline "cancellation_after_po_fee_pct percent of the order's quote total" has no freight, yet tenure_return_freight's fall-through is freight_std_usd 25/unit; P4 baseline has no rework, yet the fall-through is rework_std_usd 20/unit; P5 baseline "the lesser of the deposit paid … and the cancellation fee" has no retentions. P5's tenure_handling_retention tier "or with no active ClearPath agreement" is unreachable where the factor applies (form 1 needs an active agreement). Demonstrated consequence: with the method factor at its baseline, substituting the gated factor's baseline changes nothing on any world (e.g. P1 at build 0 gives the same fee for freight 0, 12 or 25; P5 at form 0 gives min(D, F) for every retention value), so none of these six factors contributes on its own; their per-task weight exists only because the gating tier is taken. Bears on tasks 0 (P1) and 1 (P4, P5) — demonstrated in their files.
- **CG-2 SOURCE-POLICY RED (XF A3 assembly sentence names factor quantities), charter-level, no task effect.** Members: P1 "the fee is first built … as the build rule selects, and any administration charge is then added to the built amount"; P3 "the deposit percentage is then summed from the deposit share, the late-payment points and the Sentinel relief points; and the build rule last …"; P4 "the fee percentage is first settled as the tier rate less the project points, plus the late-payment points, less the seat points; … as the build rule selects …"; P5 "the retained amounts are first summed, and the credit form then decides …"; P7 "the deposit share plus the late-payment points, less the Sentinel relief points, the project relief points and the seat relief points; the build rule then …". Not members: P2 ("every charge … summed first, and any credit is deducted … last" — generic categories) and P6. Consequence: the combination sentence is published with the computation document, which must be silent about variations; these sentences name each hidden factor (and the method factor) there.
- **CG-3 SOURCE-POLICY RED (XF B11 first-match without a tie rule), charter-level, no task effect.** Members: P4 project_scope_points, P5 project_coordination_retention, P7 infra_project_relief — each reads CFIELD('project','variant_name', status='in_progress') and the rule speaks of "a project engagement whose status is in_progress" / "whose in-progress engagement is classed …". The project charter permits concurrent engagements (project_agg_multi_holding: "A client may hold any number of engagements at once", max_per_customer null). Second reading, client with an in-progress Quick Start Project and an in-progress Standard Project: P7 2 pts vs 5 pts; P5 30 vs 0; P4 1 vs 2 pts — the rule states no tie rule and CFIELD's pick is not stated in the rule. Neither task world has two in-progress engagements (task 1: one in_progress, one closed).
- **CG-4 SOURCE-POLICY RED (XF C17 sibling overwrite), charter-level, no task effect.** P5 overwrites the base clause "any deposit paid is applied against that fee by an order credit with the excess refunded by the accounting team", which P1 and P4 also supersede; P5's replaced_by names its own case and "every other order cancelled after its purchase order" but not the endpoint sibling (P1's schedule) by name, unlike P1/P4/P2/P6/P3/P7. Consequence: none on a computed value (P1 keeps the same deposit treatment); a form defect of the overwrite set.
- Cross-product seed findings (XF D20) are per-task and are reported in 0.md and 1.md.
- Observations O1–O10 as listed in the sections above; O7: P4's cap at the deposit paid lives in the combination sentence, not in `baseline.rule`, so "the baseline alone" is ambiguous whenever the deposit paid is below cancellation_after_po_fee_pct of the total (not the case in task 1); O8: DSL semantics of MONTHS/XCOUNT/CFIELD were not readable within the brief's domain; the seeded dates avoid month-end go-lives and every late fee sits clear of the 12-month boundary, so both readings agree on these worlds; O9: XF A2 letter — the ClearPath tier selection is re-bound inside each factor that uses it (no shared non-factor binding), but no factor reads another factor's binding.

## closing_checklist
Written after both reveals (2026-10-18T03:38:44Z); nothing above this heading was changed by a reveal.
- Per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; this is revision_1 (no older revision exists).
- Scopes: task 0 charter_scope = {P1 endpoint_cancellation_fee, P2 staged_requote_total, P3 endpoint_approval_deposit; tools sign_order_cancellation_55862425, revise_staged_quote_eb003c71, sign_quote_approval_0590c0d2}; task 1 = {P4 infrastructure_cancellation_fee, P5 cancelled_deposit_credit, P6 lapsed_quote_reissue, P7 infrastructure_approval_deposit; tools sign_infrastructure_cancellation_1779b7d3, post_deposit_credit_9245a342, reissue_lapsed_quote_93c9a091, sign_build_approval_1b1ae884}. Pairwise disjoint, jointly cover all 7 extended policies and all 7 task tools; uuid8s independent.
- Trees: task 0 has 2 prerequisite problems / 2 value_input edges / customer writes P1, P3; task 1 has 3 / 2 value_input + 1 state_gate / customer writes P4, P7; the difficulty's graph is a DAG.
- Factors: every computation declares 4–6 factors with >= 2 parameter and 1 method; each task has a multi-source and a cross-difficulty factor; every factor bears weight on its task's world and every all-baseline fall-back differs from gold (both task files). Not closed: CG-1 (six factors gated through a method tier), and the tenure tiers of both tasks rest on unproducible managed rows (T0-F1, T1-F1).
- Unique solution: both tasks' frozen derivations equal GT value for value (SOURCE-TASK PASS on both).
- Gates: the coordinator snapshot of 2026-10-18T03:19:28 (all rc=0) is the instantiation-stage run on this exact form (hashes unchanged); no re-run is meaningful before rework.
- Difficulty does NOT pass the source-layer audit: open REDs — charter CG-1 (SOURCE-FACTOR), CG-2, CG-3, CG-4 (SOURCE-POLICY); task 0 T0-F1, T0-F4 (SOURCE-FACTOR), T0-F2 (SOURCE-CHAIN), T0-F3 (SOURCE-POLICY); task 1 T1-F1, T1-F2 (SOURCE-FACTOR).

VERDICT revision_1: task0=RED:T0-F1,T0-F2,T0-F3,T0-F4 task1=RED:T1-F1,T1-F2 charter=CG-1,CG-2,CG-3,CG-4

## revision_2

### charter_global_frozen (revision_2)
- Gate: last line of tasks/hardware_procurement_orders/worklog.md is exactly `REWORK round 2: gates 7/7 green` (read with `tail -n 1` only).
- Snapshot executed (not read): `/tmp/erl0069_coord/snapshot.sh hardware_procurement_orders 2` @ 2026-10-18T07:06:07 — check_extended rc=0 EXTENDED OK; check_task_tools rc=0 TASK TOOL CONTRACT OK; replay_tasks rc=0 REPLAY OK; check_solvability rc=0 SOLVABILITY OK; check_compute rc=0 COMPUTE OK; check_grounding rc=0 GROUNDING OK; check_cross_fire rc=0 SCOPE OK. Views r2/0.view.json sha256 15ee42eda702caccf2290b27393490cae6db67b6a3c26658c90cc87ef895aa90, r2/1.view.json sha256 0a31296d24096124f0497238b9109232433ff2fba49395ae69d07600602d4c9d; hardware.extended.yaml 27e2e46f3cb7179204075c8a76f923f3eda0009157037dbdf7b36ce5ac781233; task_tools.py 565f6102036cdea86b10ae070733ec4ceeb8ca99ce7eff165aa4d8596b379e63.
- Both shared inputs changed (revision_1: 42125f76… / fc9d6fee…), so every charter-global section is re-derived in full below. Base copy still verbatim (diff against blueprint/products/hardware.yaml differs only by trailing blank lines).
- Not blind: revision_1's GT of both tasks was read in round 1. The round-2 derivations rest on the r2 views and the r2 charter; the round-2 GT and the reworker's "round 2 claims" are read only after 0.md and 1.md revision_2 derivations are on disk.

### policy_conflict_scan (revision_2)
- Same seven policies, same two trees, same target tools and edges (P2->P1, P3->P2, P5->P4, P7->P6, P7->P5). Order-type partition, credit-exposure exclusion, time anchors and sibling exclusions as in revision_1; P5's replaced_by now names the endpoint sibling ("a Standard Endpoint Order's paid deposit is settled under the endpoint cancellation schedule").
- Cross-category reads now: managed (all seven), licensing (P2), project (P4, P5, P6, P7); no policy reads security any more; every `cross_category` block and `inputs.cross_category` matches the categories compute reads.
- Redesigned content: P1 drops the tenure freight factor (return freight is now the fixed freight_per_unit_usd inside the "allocated" build tier) and adds expedite_forfeit (rush fee forfeited); P2's security-preparation factor reads the Microsoft 365 plan (E5 / Business Premium or E3 / other); P3 and P7 replace Sentinel relief by managed-spend relief (seat_rate_usd × seat_count against the quote total); P4 drops sensor rework (fixed freight in the bench tier) and adds tenure_loyalty_points; P5 is rebuilt (standard credit = deposit paid less the whole staging charge; method bench_retention_basis none / prorated / whole; additive handling, expedite and coordination retentions and a tier goodwill add-back; floor at zero); P6 re-prices the unit on the re-issue day (markup_pct less a tier reduction), drops the sensor charge and keys the bench staging rate on ClearPath tier and an in-progress project.

### rule_compute_equivalence (revision_2)
- Mechanical sweep: every compute_basis value verbatim in its rule; every baseline.rule sentence in its rule; every prerequisite policy_source in its rule; every superseded_clause verbatim in its base rule; every replaced_by in its rule.
- New/changed bindings checked against their sentences: P1 f_expedite (rush ∧ PO age >= 1 -> rush_fee_usd; rush ∧ same day -> half; no rush -> 0); P2 f_edr_per_unit (E5 -> 0; Business Premium or E3 and no E5 -> edr_essentials_usd; other -> edr_standard_usd); P3/P7 b_dep_monthly / b_nd_monthly = seat_rate_usd × seat_count of the active agreement compared with spend ratios × quote total; P4 project via EXISTS with "the largest class among them deciding", loyalty by MONTHS(go-live, NOW), cap MN(payments, deposit invoiced) = "counted up to the deposit invoiced"; P5 f_bench_basis (<= 2 days none; 3–13 days staging × days / 14; >= 14 whole), MX(0, …) = "never less than zero"; P6 inner RND on the re-priced unit = "The re-issued unit price is rounded half up to the cent", lapse percentage on unit_cost_usd. All match in both directions.
- Ties (B11): project reads in P4, P5, P7 now carry an explicit tie rule; P6 reads only existence of an in-progress engagement; licensing reads in P2 are EXISTS with the E5-first ordering stated; managed reads are single-agreement by the managed charter. B13 absent-record branches stated for every read.

### action_binding_and_uuids (revision_2)
- Pairs and uuid8s unchanged (seven distinct, independent). reissue_lapsed_quote_93c9a091 now takes unit_price_usd and quote_total_usd and writes both; its docstring states format only. No body validates a prerequisite.
- XF 24 (trigger rule): events the tools write — hardware_order_cancelled (base trigger hardware:hardware_cancellation_fee), hardware_cancellation_fee (none), hardware_quote_approved (trigger hardware:hardware_deposit_invoice), hardware_deposit_invoice (none), hardware_order_credit (none), quote revision / re-issue as hardware_quote_issued updates (none), plus hardware_client_requests intake rows. No trigger leaves the hardware category. Clean.
- O5 (generic docstrings of sign_order_cancellation, sign_quote_approval, reissue_lapsed_quote cover the infrastructure cases) and O6 unchanged — observations.

### prerequisite_graph / prerequisite_sentences (revision_2)
- Unchanged edges, sentences, forms, gates, resolved_by; acyclic; all sentences verbatim and passing the four-point test as in revision_1. O3 (conditions add "carrying the revised/re-issued total") and O4 (P5 opening "once the order has been cancelled after its purchase order") persist as observations; O2 is gone (every P5 credit form now returns the deposit paid less retentions); O10 persists.

### override_declarations (revision_2)
- Same sentence-by-sentence result as revision_1 for hardware_cancellation, hardware_client_signed_requests, hardware_approval_and_purchase_order, hardware_agg_credit_exposure, hardware_agg_multi_holding. hardware_quote_and_pricing: P6's superseded unit-price clause now also covers "; the effective markup is markup_pct, reduced by clearpath_markup_reduction_pts …" and its replaced_by restates that clause for other quotes; P2's narrower clause and P6's wider one exclude each other's case by name. C16, C17, C18 clean (CG-4 closed).

### factor_ladders (revision_2)
- P1 4 (po_age_build M; tier_fee_rate P; expedite_forfeit P; arrears_admin_charge P); P2 5 (autopilot_staging_rate P multi-source; tenure_handling P; tier_rush_rate P; fee_credit_basis M; defender_onboarding_rate P); P3 4 (tier_deposit_share P; arrears_deposit_points P; managed_spend_relief P; tenure_deposit_build M); P4 6 (bench_stage_build M; infra_tier_rate, project_scope_points, arrears_fee_points, covered_seat_points, tenure_loyalty_points P); P5 5 (bench_retention_basis M; tenure_handling_retention, expedite_retention, project_coordination_retention, managed_goodwill_credit P); P6 5 (reissue_markup_reduction P; managed_bench_staging_rate P multi-source managed ∧ project; reissue_tenure_handling P; reissue_tier_rush P; lapse_charge_basis M); P7 6 (infra_deposit_share, infra_arrears_points, infra_spend_relief, infra_project_relief, infra_seat_relief P; infra_relationship_build M).
- Every ladder 3 disjoint tiers with distinct outcomes, stated in the rule, implemented in compute, fall-through = baseline. Mechanical: no factor binding reads another factor's binding; no plain binding reads a factor-owned binding (XF 26); no factor id is a substring of a tool name.
- Gating (CG-1): no parameter factor is now used only inside a non-fall-through method tier — P1 freight and P4 freight are fixed constants of the method tier, P5's retentions and goodwill are additive outside the method. Percentage factors of P1/P3/P4/P7 are dropped only by the method tiers that drop the percentage, and each contributes against the baseline build. Closed.
- XF 23 all-pairs method-shape tables (inputs counted once, constants ignored):
  - P1 po_age_build: {units} | {total, units} | {total} — 1/2 PASS (2 adds total), 1/0 PASS (different input), 2/0 PASS (2 adds units).
  - P2 fee_credit_basis: fee | MN(fee, units) | nothing — whole/capped PASS (adds MN and units), nothing/whole PASS (fee > 0 on its reachable domain: the prerequisite books a positive fee), nothing/capped PASS.
  - P3 tenure_deposit_build and P7 infra_relationship_build: {cost, units} | {total, units, price} split | {total} — all pairs PASS (different inputs / added split operation).
  - P4 bench_stage_build: as P1 — PASS.
  - P5 bench_retention_basis: nothing | staging × days / period | staging — nothing/whole PASS (staging_fee_per_unit_usd 145 / 395 > 0 for both order types in scope), prorated/whole PASS (adds days), nothing/prorated PASS.
  - P6 lapse_charge_basis: {units} | {units, cost} | nothing — PASS all pairs.
- XF 26 "each factor's sentences name the result quantity it modifies": every factor sentence names its quantity (endpoint cancellation fee, staged re-quote charge, endpoint/infrastructure deposit percentage, infrastructure fee percentage, deposit credit, re-issued unit/total). Clean.
- Realism (revision_1 O1): the tenure-freight, Sentinel deposit relief, non-XDR rework, re-issue sensor charge, carried-over lapsed price and double bench charge are all gone. Remaining judgement-only observations: ClearPath late fees as a hardware cancellation admin charge (P1); a ClearPath-tier goodwill add-back on a cancelled-order deposit credit (P5).

### findings (revision_2)
- CG-1 (revision_1) — CLOSED (see factor_ladders).
- CG-3 (revision_1) — CLOSED: P4 "the largest class among them deciding: project_major_pts points when any of them is classed …, project_minor_pts points when every one of them is of a smaller class"; P5 "the largest class among them deciding: … nothing when any in-progress engagement is classed Standard Project …"; P7 as P4; compute uses EXISTS over classes in the same priority.
- CG-4 (revision_1) — CLOSED.
- **CG-2 (revision_1) — NOT CLOSED; SOURCE-POLICY RED, all remaining members of the class:**
  - P4: "the fee percentage is settled first, every point adjustment being added to or taken off the tier rate; the fee is then built …" — names the factor quantity "tier rate" (infra_tier_rate's "The tier rate of an infrastructure cancellation is …") and the factors' unit "point adjustment".
  - P7: "the deposit percentage is settled first, every point adjustment being added to or taken off the deposit share; …" — names "deposit share" (infra_deposit_share) and the point adjustments.
  - P5: "the bench retention is settled first, every other retained amount is then taken off the deposit paid and every goodwill amount added back, and the credit is never less than zero" — names "goodwill amount" (managed_goodwill_credit).
  - Now clean: P1 ("the percentage and the way the fee is built are settled first, and any fixed charge is then added to the built fee"), P3 ("the deposit-required test … comes first …; the deposit percentage is then settled; and the way the deposit is built … comes last"), P2, P6. Consequence (no task value effect): the combination sentence goes with the computation document, which must be silent about variations; these three sentences name a hidden factor's quantity there.
- Near-miss coverage after the re-seed is per computation and is judged in 0.md / 1.md.

### closing_checklist (revision_2)
Written after the round-2 reveal (2026-10-18T07:14:01Z); the revision_2 charter-global sections above were written before it.
- Round-2 claims checked item by item: T0-F1, T0-F2, T0-F3, T0-F4, T1-F1, T1-F2, CG-1, CG-3, CG-4 — closed (evidence in 0.md, 1.md and § findings (revision_2)). CG-2 — claim "every combination sentence is generic" not true for P4, P5, P7 (residual members listed above). Realism claims — confirmed.
- Scopes unchanged, disjoint and complete; uuid8s unchanged and independent; DAG unchanged; every task tree 1–3 prerequisites with >= max(n − 1, 1) value_input edges and a customer write; XF 23 (all-pairs) PASS for all seven method factors; XF 24 clean; XF 25 clean on both worlds; XF 26 clean.
- New/regressed: T1-R2-F1 (P6 computation lacks a near-miss after the re-seed). Observation O11 (float half-up artefact in a factor_sensitivity figure).
- Gates on the final form: coordinator snapshot round 2 (2026-10-18T07:06:07) — 7/7 rc=0.
- Difficulty does NOT yet pass: open REDs CG-2 (P4, P5, P7 combination sentences) and T1-R2-F1.

VERDICT revision_2: task0=PASS task1=RED:T1-R2-F1 charter=CG-2

## revision_3

### charter_global_frozen (revision_3)
- Gate: last line of worklog.md is exactly `REWORK round 3: gates 7/7 green` (tail -n 1 only).
- Snapshot executed (not read): `/tmp/erl0069_coord/snapshot.sh hardware_procurement_orders 3` @ 2026-10-18T07:50:26 — check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0 (EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK). r3/0.view.json 0ded5a4b…bb33; r3/1.view.json 200e4e5b…3176; hardware.extended.yaml 3f59c0b2…064b (changed); task_tools.py 565f6102…9e63 (unchanged from revision_2).
- Charter changed -> charter-global sections re-derived; tool module unchanged -> action_binding_and_uuids carried forward from revision_2 on the unchanged hash 565f6102….
- Not blind (earlier GT read). Round-3 claims (worklog § "round 3 claims") read before this derivation to locate the changes; values below are recomputed independently.
- What changed: the combination sentences of P4, P5, P7 (and their `result` compute_basis); nothing else in the charter (all other mechanical checks identical to revision_2). Seeds: task 0 adds an expired Microsoft 365 E5 (no Teams) pilot (2 licences, P1Y annual 2024-06-03..2025-06-02, 1314.00 = 54.75 × 2 × 12 invoiced and paid, order form, add and expiry licence rows); task 1 re-dates HQ-053084 to 2026-09-01 and the ClearPath tier change to 2024-11-01 (request 2024-10-14; Standard fees 3214.08 for 2023-12..2024-10, paid). Persona 1: "almost two years ago".

### exhaustive XF pass (revision_3) — every point × every policy and seed
Policies P1 endpoint_cancellation_fee, P2 staged_requote_total, P3 endpoint_approval_deposit, P4 infrastructure_cancellation_fee, P5 cancelled_deposit_credit, P6 lapsed_quote_reissue, P7 infrastructure_approval_deposit; seeds T0, T1.
1. Factor contributes on its own against a baseline quantity / no factor reads another factor: mechanical sweep clean on all 7; no gating (P1/P4 freight are constants of a method tier; P5 retentions/goodwill additive). Clean.
2. Shared record selections as one plain binding stated once: **members** — P1 DAYS(order_placed_date, NOW) bound twice (po_age_build b_po_age_days, expedite_forfeit b_exp_po_age); P2 EXISTS(licensing active Business Premium / E3 / E5) bound in both autopilot_staging_rate (b_intune_plan) and defender_onboarding_rate (b_e5_plan, b_defender_plan), and CFIELD(managed variant_name active) in tier_rush_rate (b_rush_tier) and fee_credit_basis (b_credit_tier); P6 CFIELD(managed variant_name active) in reissue_markup_reduction (b_ri_tier), managed_bench_staging_rate (b_ri_upper_tier) and reissue_tier_rush (b_ri_rush_tier); P7 CFIELD(managed seat_count active) in infra_spend_relief (b_nd_monthly) and infra_seat_relief (b_nd_seats). P3, P4, P5 clean. No result is assembled inside a factor binding (all 7). -> CG-5.
3. Assembly sentence generic: P1 "the percentage and the way the fee is built are settled first, and any fixed charge is then added to the built fee"; P2 "every charge … summed first, and any credit is deducted from that sum last"; P3 "deposit-required test … first …; the deposit percentage is then settled; and the way the deposit is built … last"; P4 "the fee percentage is settled first; the fee is then built from that percentage, the quote total and the units ordered; and the built fee never exceeds the deposit paid …"; P5 "the bench retention is settled first, every other adjustment is then applied to the deposit paid, and the credit is never less than zero"; P6 "the unit is re-priced first, every charge is then figured, and … summed last"; P7 "the deposit percentage is settled first; the way the deposit is built … comes last". Judgement: "fixed charge", "credit", "charge", "adjustment" name operation kinds (the recipe's own "replacements / caps / additions"), "percentage", "bench retention", "deposit paid" are baseline quantities — no factor quantity named. Clean (CG-2 closed).
4. Non-commuting order fixed: P1 build before additions; P2 credit last; P3 test → percentage → build; P4 percentage → build → cap; P5 bench → others → floor; P6 re-price → charges → sum; P7 percentage → build. Clean.
5. Single-factor quantities in own sentences; no "as another policy figures it": clean on all 7 (P4's cap quantity "deposit paid" is a non-factor rule in the combination sentence — O7).
6. Method/parameter honesty: see 23. Parameter factors select values only. Clean.
7. Factor id ⊄ tool name: clean.
8. Rule == compute both directions: re-checked the three changed sentences against `result`; others as revision_2. Clean. Observation O12: P5's handling, expedite and coordination sentences call each amount a "retention" and the combination sentence says only "every other adjustment is then applied to the deposit paid"; subtraction follows from "retention" as the standard sentence defines it ("returns the deposit paid less a bench retention"); one reading.
9. compute_basis verbatim: clean (mechanical).
10. Rounding placement: one RND on result in P1–P5, P7; P6 two (unit and total), both stated. Clean.
11. Ties: managed single-agreement (managed_agg_multi_holding); security unread; project reads carry "largest class deciding" (P4, P5, P7) or existence only (P6); licensing reads are EXISTS with stated E5-first order (P2). Clean.
12. Month-end convention: every tenure sentence says "a month completing only once the day of the month reaches the go-live date's day number" — definite; whether MONTHS() implements it for go-live days 29–31 is not verifiable within the read domain (DSL lives under skills/). Seeded go-lives 2024-03-11 and 2023-11-13 are clear of it. O8 (unchanged).
13. Absent-record branches: stated and implemented on all reads. Clean.
14. Decoys excluded by the rule alone: status words "whose status is active" (managed, licensing), "in_progress" (project) exclude cancelled/closed/expired rows; seeded decoys now: T0 expired E5 pilot (P2), T1 tier-change date and quote date (P4/P5/P6). Clean.
15. DSL pairing limits: P3's quote-date-vs-cancellation-date pairing is only a prerequisite state, not priced; P2 prices one source record. Clean.
16. Scoped replaced_by: all 10 overwrites carry "and only for such …" and restate in-force text. Clean.
17. Sibling exclusions: P1/P4/P5 on the cancellation clause, P2/P6 on the pricing clauses, P3/P7 on the deposit clause — each names the other case. Clean.
18. No empty/undeclared overwrite: clean.
19. Docstrings: format only, effects in body. Clean (O6: "cancelled after its purchase order" / "already been placed" describe the order's stage, not a tool sequence).
20. Cross-product rows producible and priced by their charters: per task (0.md, 1.md revision_3).
21. Realism: judgement-only observations kept — P1 ClearPath late fees as a cancellation administration charge; P5 tier goodwill add-back. Every other ladder is a plausible VAR/MSP practice.
22. Proof-text sweep: per task after reveal.
23. Method-shape all-pairs: unchanged methods; revision_2 tables stand (all PASS).
24. Trigger rule: tools unchanged; no cross-category trigger. Clean.
25. Complete ledgers: per task.
26. Plain bindings never read factor bindings; no rule word for a missing field; each factor names its result quantity: clean (mechanical + reading).
Skill checks outside the recipe, re-run in the same pass: check 6 "the rule carries nothing else about that dependency: no second wording" — **member**: P5's opening sentence "…the paid deposit of a Network Equipment Order or Server & Storage Build Order once the order has been cancelled after its purchase order…" restates the P5->P4 dependency with an ordering connective in action form, weaker than the declared state-form sentence (no fee-row condition) -> CG-6 (revision_1/2 O4, reclassified). Scan of every other rule sentence for once/until/only after/before/prior to/first/already/then outside the prerequisite sentences finds only scope ("after the order's purchase order was placed and before it shipped"), rounding ("once, on the final amount"), month convention ("only once the day …") and assembly-order uses. P2's scope phrase "a Standard Endpoint Order that was cancelled after its purchase order" carries no ordering connective tied to P2's result — observation O13. Check 7: conditions of P3 and P7 edge 1 add "carrying the revised/re-issued total" (O3, field not rendered, the only resolving write sets both — no consequence).

### findings (revision_3)
- CG-2 — CLOSED (point 3 above).
- **CG-5 SOURCE-FACTOR RED (XF 2, form only, no value effect; revision_1 O9 reclassified under the exhaustive pass)** — members: P1 (PO age ×2), P2 (licensing plan existence ×2 factors; ClearPath tier ×2), P6 (ClearPath tier ×3), P7 (seat_count ×2) as listed in point 2. The same record selection is bound inside each factor that uses it and re-stated in each factor sentence instead of once as a plain binding.
- **CG-6 SOURCE-POLICY RED (skill check 6, second wording; revision_1/2 O4 reclassified)** — P5 opening sentence (quoted above). Consequence: the KB carries the rule verbatim, so P5's hub states its dependency twice — once in the declared state form, once as "once the order has been cancelled after its purchase order" (action form, without the fee-row condition) — which the KB dependency-form scan rejects ("a state-form sentence never restated as an action").
- Observations carried: O1 realism (two items, point 21), O3, O5, O6, O7, O8, O10, O11, O12, O13.

### closing_checklist (revision_3)
Written after the round-3 reveal (2026-10-18T07:54:54Z); the revision_3 exhaustive pass above was written before it.
- Round-3 claims checked: CG-2 closed (all seven combination sentences generic); T1-R2-F1 closed (P6 near-misses seeded and priced per their charters); P2 near-miss added (expired E5 pilot, producible, invoiced and paid); task 0 values, trees and tools unchanged — confirmed. Gates 7/7 rc=0 on the final form (snapshot 2026-10-18T07:50:26).
- Exhaustive pass result (every XF point × every policy and seed, plus skill checks 6/7): open members are CG-5 (XF 2: P1, P2, P6, P7 shared selections bound per factor) and CG-6 (skill check 6: P5 opening sentence's second, action-form wording of its dependency) — both pre-existing (revision_1 O9 / O4), reclassified now so nothing pre-existing surfaces later — and T1-R3-F1 (XF 22: two stale quote-date sentences in task 1's proof). Everything else is listed as clean or as an observation with its reason in § exhaustive XF pass (revision_3).
- Scopes, uuid8s, DAG, tree shapes, factor counts, near-miss per computation (all seven), method all-pairs, trigger rule, complete ledgers, plain-binding reads: all hold.

VERDICT revision_3: task0=PASS task1=RED:T1-R3-F1 charter=CG-5,CG-6

## revision_4

### charter_global (revision_4) — closures and changed parts only
- Gate: last line of worklog.md is exactly `REWORK round 4: gates 7/7 green`. Snapshot executed (not read) `/tmp/erl0069_coord/snapshot.sh hardware_procurement_orders 4` @ 2026-10-18T09:09:45: check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0. r4/0.view.json 0ded5a4b…bb33 and r4/1.view.json 200e4e5b…3176 (identical to r3 — seeds unchanged); hardware.extended.yaml df067b99a899fbf5fec633d2897827e7f73fdd3b98514f4e012fde4095ba3cdf (changed); task_tools.py 565f6102…9e63 (unchanged; action_binding_and_uuids carried forward).
- Round-4 claims (worklog § "round 4 claims") verified item by item below.
- **CG-5 — CLOSED.** Mechanical scan of every CFIELD / CPARAM / EXISTS / XCOUNT / XLATEST / SUM / DAYS / MONTHS call in every policy: no call expression is bound by two factors. Changes: P1 expedite_forfeit reads DAYS(approved_date, NOW) ("The rush processing an order is worked under starts on the day its quote is approved …"), po_age_build keeps DAYS(order_placed_date, NOW); P2 licensing plans are the plain bindings b_lic_e5 / b_lic_bp_e3, stated once ("it holds an E5 plan when it has an active Microsoft 365 E5 (no Teams) subscription, a Premium or E3 plan when … ; a subscription in any other status gives it neither"), read by autopilot_staging_rate and defender_onboarding_rate (factor -> plain reads are allowed; XF 26 clean); fee_credit_basis's whole-fee tier now rests on the late-fee count, defender's zero tier on CPARAM m365_administration_included, tier_rush_rate alone reads the ClearPath tier; P6 reissue_markup_reduction alone reads variant_name, managed_bench_staging_rate reads CPARAM network_device_management_included, reissue_account_rush reads CPARAM technical_account_manager / dedicated_account_manager; P7 infra_seat_relief alone reads seat_count, infra_spend_relief reads XLATEST(managed_billing amount_usd, event_type managed_monthly_fee) gated by an active agreement.
- **CG-6 — CLOSED.** P5's opening now "…the paid deposit of a Network Equipment Order or Server & Storage Build Order cancelled after its purchase order; …" — no ordering connective; the connective scan of all seven rules outside their prerequisite sentences finds only scope, rounding, month-convention and assembly-order uses (as revision_3).
- Changed parts re-checked against every XF point they touch:
  - 1/26 independence and plain bindings: clean (mechanical). 2: clean. 3/4: all seven combination sentences unchanged and generic. 6/23: method factors unchanged (fee_credit_basis keeps whole / capped / none — all-pairs PASS). 8/9: every compute_basis verbatim; rule == compute for the changed bindings (expedite on approval age with the same-day half tier; full credit only with zero late fees in 12 whole months; Defender zero tier only for E5 ∧ tenant administration, essentials for any other E5 / Premium / E3 holder; staging on network-device coverage ∧ project; rush 0 with a TAM, rush_core with a client success manager and no TAM, else rush_fee_usd; spend relief on the latest monthly fee). 11/14: XLATEST of monthly fees — one fee per month per single agreement, other event types (proration, late fee, payment) excluded by the filter; licensing decoy excluded by "a subscription in any other status gives it neither". 13: absent branches stated (no active agreement -> spend 0; no plan -> edr_standard). 21: realism — rush cost counted from approval, full credit for a clean payment record, Defender P2 by policy when the MSP administers the tenant, bench staging cheaper when network devices are managed, rush waived with a named TAM, spend relief on the latest monthly fee — all plausible VAR/MSP practice. Cross-category declarations list every newly read field (m365_administration_included; network_device_management_included, technical_account_manager, dedicated_account_manager; managed_billing.amount_usd).
- Factor counts unchanged (4/5/4; 6/5/5/6); every computation keeps a discriminating near-miss (0.md, 1.md revision_4); trees, edges and tools unchanged; gold unchanged.
- New observations: O14 — "monthly ClearPath seat billing" is defined as seat_rate_usd × seat_count in P3 and as the latest ClearPath monthly fee in P7 (each policy's own sentence governs; equal on task 1's world, P3 is not evaluated there). O15 — P2/P6 CPARAM reads are tier entitlements of the managed charter rather than record fields: the agent derives them from the agreement's variant_name and the managed product's published entitlements; P6's three managed factors all move with the ClearPath tier (independent bindings, not a recipe violation).

### closing_checklist (revision_4)
- Per-task files and _difficulty.md carry revision_1..4; every round-3 RED (CG-5, CG-6, T1-R3-F1) closed; no regression (values, sensitivities, trees, tools, seeds unchanged; near-miss per computation present).
- Scopes disjoint and complete; uuid8s independent; DAG; trees 2 and 3 prerequisites with 2 value_input edges each and customer writes; 4–6 factors per computation (>= 2 parameter, 1 method), multi-source and cross-difficulty per task; every factor bears weight against an honest baseline and every all-baseline fall-back differs from gold.
- Gates on the final form: snapshot round 4, 7/7 rc=0.
- Observations remaining (not grounds for rework): O3, O5, O6, O7, O8, O10, O11, O12, O13, O14, O15, and the two judgement-only realism notes (P1 late-fee administration charge, P5 tier goodwill).
- The difficulty passes the source-layer audit.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

### charter_global (revision_5) — renderer findings render_r1.md 1–3, their classes, regressions
- Gate: last line of worklog.md is exactly `REWORK round 5: gates 7/7 green`. Snapshot executed (not read) `/tmp/erl0069_coord/snapshot.sh hardware_procurement_orders 5` @ 2026-10-18T10:27:00: check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0. r5/0.view.json 0ded5a4b…bb33, r5/1.view.json 200e4e5b…3176 (unchanged since r3); hardware.extended.yaml 4c40c1e11afdb94bcbce714e49a91930ede13ecea409c12223e5614dceb47d1d (changed); task_tools.py 565f6102…9e63 (unchanged).
- Inputs read: audits/render_source/hardware_procurement_orders/render_r1.md in full; worklog § "round 5 claims".
- Audit miss disclosure: all three renderer findings existed in the form I passed at revision_4. I passed P6's "whose network design the bench configures from" in revision_2 and recorded XF 26 ("no rule word refers to a field the records lack") as clean in revisions 3 and 4. I did not test P2's lead phrase against compute. I recorded C16 as clean although the P3/P7 tails did not restate the whole in-force deposit clause.
- **Finding 1 (P6 managed_bench_staging_rate) — CLOSED.** The sentence now reads "…staging_project_usd when the client's active ClearPath agreement covers firewall, switch and wireless configuration changes and the client holds an in-progress project engagement, staging_managed_usd when it holds such an active ClearPath agreement and no in-progress project engagement, and the order type's staging_fee_per_unit_usd for every other client." This equals `f_ri_staging` / `b_ri_project` (EXISTS project in_progress) for every client, and the compute_basis entries for b_ri_project / f_ri_staging are verbatim. Renderer's splitting case (Essentials + one in-progress Assessment Engagement): the rule now gives 95.00 = compute.
- **Finding 2 (P2 defender_onboarding_rate lead) — CLOSED.** The lead now reads "…follows the client's Microsoft 365 plans, an E5 plan deciding when the client holds both an E5 plan and a Premium or E3 plan: …". It is client-level, states E5 precedence, and matches `0 if (b_lic_e5 and b_def_tenant_admin) else (edr_essentials if (b_lic_e5 or b_lic_bp_e3) else edr_standard)`. A client holding both plans gets one reading. No other phrase refers to which plan licenses particular users.
- **Finding 3 (P3 and P7 overwrite tails) — CLOSED.** Both replaced_by tails (verbatim in their rules) now read "…and every other order, including any order whose approval would take the client over its credit limit, keeps the deposit of the base rule: a required deposit of deposit_pct percent of the quote total, or 100 percent of the quote total whatever deposit_pct and deposit_threshold_usd say when the approval would take the client over its credit limit, invoiced on approval, rounded half up to the cent and due on receipt (deposit_due)."
  - They restate the whole retired clause (amount, invoicing on approval, rounding, due on receipt) for out-of-scope orders.
  - They are consistent with hardware_agg_credit_exposure.
  - Each still names its sibling's within-limit scope (XF 16/17).
- **Other members of these classes, swept now over all seven rules:**
  - Class 1 (rule qualifier or rule word with no compute counterpart / resting on data the records lack). I listed every relative, participial and causal clause in every rule; the restrictive test asks whether the clause narrows which record or client a tier counts. Result: no remaining member. The remaining clauses are non-restrictive rationale attached to an already-determined tier or quantity, and none narrows a tier:
    - P2: "Stratton Bay then pushing its Defender for Endpoint Plan 2 onboarding by policy", ", whose Defender onboarding package the bench applies to each unit", ", whose units the bench hardens by hand".
    - P5: ", whose coordination is billed through that project", "the bench slot being booked when the purchase order is placed", "the bench slot is released".
    - P6: ", who books the rush allocation with the distributor directly".
    - P1/P4 build tiers: "has no units allocated yet" / "has its units allocated or in transit" / "has its units shipped to the staging bench", each stated as what the purchase-order age means.
    - P1 rush lead: "The rush processing an order is worked under starts on the day its quote is approved", which is also the binding's own basis.
    - Scope and gate phrases ("for the same part number and quantity as a Standard Endpoint Order …", "a staged quote that takes over a plain endpoint line …", "takes over an ordered infrastructure order …") decide which write or prerequisite applies; they are not tier filters of a computed value.
    - Observation O16: P5's ", whose coordination is billed through that project" is the closest in form to finding 1. It is set off by a comma, so it describes the classes already listed rather than filtering them; a renderer should keep the comma.
  - Class 2 (lead phrase naming a basis that compute does not use): every "follows …" / "by …" / "is built by …" lead in the seven rules names exactly what its binding reads. Checked leads:
    - PO age (P1, P4).
    - ClearPath tenure (P2, P4, P5, P6, P3 build, P7 build).
    - Calendar days from cancellation (P2; the whole-fee tier's late-fee condition is stated in the tier).
    - In-progress engagements with "largest class deciding" (P4, P5, P7).
    - ClearPath tier (P5 goodwill, P6 reduction).
    - Monthly seat billing (P3: seat_rate_usd × seat_count; P7: latest monthly fee — O14).
    - Days from the last valid day (P6).
    - Microsoft 365 plans (P2).

    No remaining member.
  - Class 3 (replaced_by tail dropping in-force content), all ten overwrites:
    - P1 and P4 tails restate the full retired sentence: "stays charged cancellation_after_po_fee_pct percent of the quote total, rounded half up to the cent, with any deposit paid applied against that fee by an order credit and the excess refunded by the accounting team".
    - The P5 tail restates its clause.
    - The P2 and P6 unit-price tails restate the unit price, with the effective-markup definition in P6's wider clause.
    - The P2 and P6 quote-total tails restate every term, including "when rush is requested where rush_available is true".
    - The P3 and P7 tails are as above.

    No remaining member.
- Regression check: every compute_basis, superseded_clause, replaced_by and prerequisite sentence is verbatim (mechanical). No compute, factor or parameter change moves a value; GT values and sensitivities are unchanged (0.md / 1.md revision_5). Combination sentences, the CG-5/CG-6 closures, near-misses, trees, tools and seeds are unchanged. No new defect.
- Observations remaining: O3, O5, O6, O7, O8, O10, O11, O12, O13, O14, O15, O16; realism notes (P1 late-fee administration charge, P5 tier goodwill).

### closing_checklist (revision_5)
- Renderer findings 1–3 are closed and no other member of their three classes remains. The revision_4 closures stand, gates are 7/7 rc=0 on the final form (snapshot round 5), and per-task verdicts are PASS on all four relationships.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

### charter_global (revision_6) — seed-only round, KB-audit source items S1/S2
- Gate: last line of worklog.md is exactly `REWORK round 6: gates 7/7 green`. Snapshot executed (not read) `/tmp/erl0069_coord/snapshot.sh hardware_procurement_orders 6` @ 2026-10-18T13:29:10: check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0. r6/0.view.json 2fb869da53b7f277be202d10fb11e4f21250d8b0f15996d24e8e9091c587a894, r6/1.view.json 8ef959d22b8ddc6d871439c60a6c68630dcc1533708cb1c3bf965d08504d30f5.
- **Charter and tools unchanged:** hardware.extended.yaml 4c40c1e11afdb94bcbce714e49a91930ede13ecea409c12223e5614dceb47d1d and task_tools.py 565f6102036cdea86b10ae070733ec4ceeb8ca99ce7eff165aa4d8596b379e63 equal revision_5's, so every charter-global section is carried forward by reference.
- Inputs read: audits/policy_kb/hardware_procurement_orders/_difficulty.md revision_2 (S1, S2); worklog § "round 6 claims"; docs/managed hubs, baselines and factors of managed_ext_current_month_fee and managed_ext_first_late_fee.
- **S1 — closed for the row it named, class not closed.** INV-310217 (2026-10) = 2649.11 and balance_due 2649.11 reproduce the published schedule. But the same rule, read on the posting-day clock that the re-priced late fees themselves use, also governs the 18 earlier task-0 fees of 2025-04..2026-09, which stay at 2689.45. This is T0-R6-F1 (0.md revision_6).
- **S2 — closed on the posting-day clock for the seeded fee bases.** All five late fees (task 0: 13.84, 20.75; task 1: 18.08, 27.12, 27.12) and their settling payments reproduce the published late-fee schedule on the invoices as seeded. Task 1 is fully consistent. Task 0's two late fees and payments move again once T0-R6-F1's fee bases are corrected (13.68 / 2662.79; 20.53 / 2669.64).
- Other members of the class (cross-product rows against the published owning-product rules), swept now:
  - task 1 monthly fees (no credit-bearing holdings): clean;
  - both tasks' proration, tier-change and onboarding-waiver rows (unchanged, base rules; KB audit concurs): clean;
  - licensing and project rows (KB audit concurs; unchanged since revision_3): clean;
  - task 0 monthly fees 2025-04..2026-09: the T0-R6-F1 member above.
- No moved hardware value; no stale proof text (both tasks).

### closing_checklist (revision_6)
- Charter carried forward (hashes unchanged): CLEAN.
- Task 1: PASS.
- Task 0: RED, for T0-R6-F1 (seed only, no scored effect).

VERDICT revision_6: task0=RED:T0-R6-F1 task1=PASS charter=CLEAN

## revision_7

### charter_global (revision_7) — seed-only round, exhaustive ClearPath pass
- Gate: last line of worklog.md is exactly `REWORK round 7: gates 7/7 green`. Snapshot executed (not read) `/tmp/erl0069_coord/snapshot.sh hardware_procurement_orders 7` @ 2026-10-18T14:13:52: check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0.
  - r7/0.view.json b5e097700634bf2c9dce372df66d2c90a99e1e77518891f42125b13098a447ff (changed);
  - r7/1.view.json 8ef959d22b8ddc6d871439c60a6c68630dcc1533708cb1c3bf965d08504d30f5 (= r6).
- **Both hashes unchanged:** hardware.extended.yaml 4c40c1e11afdb94bcbce714e49a91930ede13ecea409c12223e5614dceb47d1d, task_tools.py 565f6102036cdea86b10ae070733ec4ceeb8ca99ce7eff165aa4d8596b379e63. The charter-global sections are carried forward by reference.
- Published rules applied, from docs/managed:
  - managed_signing_terms; managed_onboarding_and_go_live; managed_seat_changes_and_proration;
  - managed_monthly_fee_calc with managed_ext_current_month_fee (hub, baseline and six factors);
  - managed_late_fee_and_suspension with managed_ext_first_late_fee (hub, baseline and five factors);
  - managed_tier_change (the Essentials -> Standard amendment is not triggered: the moves are Essentials -> Professional and Standard -> Professional);
  - managed_payment_application; managed_agg_multi_holding.
  - Renewal, exit, reinstatement and labor policies have no seeded event.
- Every ClearPath row of both tasks was checked: 2 agreements, 2 seat baselines, 2 tier-change requests, and 64 + 73 billing rows. Late fees were recomputed by a script over every assessment day. Results are in 0.md and 1.md revision_7. **T0-R6-F1 — CLOSED; no remaining member** of the cross-product-row class in either task.
- No moved value; proof text consistent in both tasks.
- Observations added: O18 (true-up input "licensed directory users" not recorded).
- O14 note: the T0 ledger fee (2649.11) now differs from seat_rate × seat_count (2689.45). P3's rule names the latter explicitly, and both give the same tier on every world this task evaluates.

### closing_checklist (revision_7)
- Charter carried forward (hashes unchanged): CLEAN. Task 0: PASS. Task 1: PASS. Gates 7/7 rc=0 on the final form.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN
