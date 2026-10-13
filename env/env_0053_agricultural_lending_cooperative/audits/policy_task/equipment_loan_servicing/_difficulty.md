# Policy-task audit — equipment_loan_servicing / charter-global

## charter_global_frozen

- Freeze time: 2026-10-11 04:17 UTC (written before any task's GT was revealed; nothing below derives from a revealed GT field).
- Auditor: Claude (erl-task-policy-audit, independent of the authoring agent).
- Frozen inputs (sha256, re-verified at audit start against the coordinator's HASHES.txt):
  - `tasks/equipment_loan_servicing/equipment.extended.yaml` = `972277f9cfd24c8cbf26dc6a40a368a95b9245195fda02e3a8bae3d4afb3f698`
  - `tasks/equipment_loan_servicing/task_tools.py` = `4a7d5ba5afe9a336eed22a2d8190cb4e1d876f1c217b4aa3c1055b2dd893c19e`
  - masked views `0.view.json` = `761f0d76…f417`, `1.view.json` = `3fff4e95…3028` (keys present: frozen_time, user_scenario, initial_state only).
- Permitted and read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/equipment.yaml`, `blueprint/products/operating.yaml` (cross-difficulty consistency only), the extended charter, `task_tools.py`, the two masked views, `erlbench/` and skill scripts (`check_compute.py` primitive semantics, `replay_tasks.py` FK map).
- Masked, not read before this file was frozen: every task JSON under `tasks/equipment_loan_servicing/tasks/` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*), worklog.md, any earlier audit. No recursive grep touched `tasks/`.

### entry_conditions
- Gate snapshot received with the brief: check_extended OK, check_task_tools OK, check_solvability OK, check_compute OK, check_grounding OK, check_cache_diff INFO, check_cross_fire SCOPE OK; check_traceability deferred (KB not published).
- replay_tasks rc=1. The only FAIL lines are `dangling foreign key(s): equipment_collateral.loan_id=… (no such row in homeloan_loans)`. Verified the coordinator's ruling: `skills/erl-task-instantiate/scripts/replay_tasks.py::pk_fk_map` resolves a FK's parent by field name and `owner[ids[0]] = t` is overwritten for each table whose PK is `loan_id`; in `db_schema.json` that is `equipment_loans`, `farmland_loans`, `homeloan_loans` (last wins). `db_schema.json` states `equipment_collateral.loan_id` is "foreign key -> equipment_loans", and every runtime finder in `share_tools.py` queries its own table. Gate artefact, not a task defect. Accepted.
- Masked views and hashes present. Entry conditions met.

### policy_conflict_scan
Six extended policies; subjects and target writes:

| policy | subject | target_tool / computes | owner |
| --- | --- | --- | --- |
| equipment_ext_installment_late_charge | equipment_fee_assessed (late_charge) | assess_installment_late_charge_7bb353d6 / late_charge_amount | agent |
| equipment_ext_collateral_protection_premium | equipment_fee_assessed (collateral_protection) | assess_collateral_protection_premium_372633e7 / premium_amount | agent |
| equipment_ext_autopay_enrolment_rate | equipment_autopay_change | enrol_installment_autopay_aa82d556 / interest_rate | user |
| equipment_ext_total_loss_release_price | equipment_unit_released (total_loss) | release_total_loss_unit_e8bdf554 / release_proceeds | user |
| equipment_ext_post_release_curtailment | equipment_principal_payment (prepayment) | apply_ltv_curtailment_c1e2b439 / curtailment_amount | agent |
| equipment_ext_deferral_fee | equipment_deferral_grant | grant_installment_deferral_57477c3f / deferral_fee | agent |

- Overlapping subjects: the late charge and the CPI premium both write `equipment_fee_assessed`, distinguished by fee_code; neither reads the other's rows (LC inputs: bill, payments on bill, late-charge counts, operating late charges; CPI inputs: expiry, maturity, pledges/releases, billed interest, prior CPI). No shared balance, cap or dedup key between them.
- Cross-reads between extended policies outside declared edges: TL `payment_record_adjustment` and deferral `casualty_relief` count late charges; deferral `autodebit_credit` and TL count returned payments. No rule states an order between those writes, and none of the derived trees combines them with a late-charge write (see task files), so no undeclared order arises.
- Time anchors: all on frozen_time (`NOW`), due dates, expiry date, funding date, maturity, next due date. No conflicts among extended policies.
- Cross-category read boundary: only `operating` (operating_lines fields status, opened_date, autodraft_enrolled, crop_year; operating_transactions late-charge rows). Read-only. Consistent with blueprint claim ("read-only facts from the member's operating lines").
- Terminal states: compatible (fee rows, autopay flag + rate, release + release proceeds, prepayment row, deferred status).
- Scope partition (from the prerequisite graph, which has exactly two weakly connected components): {late charge, CPI premium, autopay rate} and {total-loss release, curtailment, deferral fee}. Task 0's persona raises autopay, task 1's raises a deferral, so the two components map one-to-one to the two tasks: pairwise disjoint and jointly complete over the six extended policies (to be confirmed against `charter_scope` at the reveal step in the task files).
- Conflicts with base found in this scan are listed under override_declarations and findings (F1, F2, F3, F5).

### rule_compute_equivalence
Mechanical sweep (script over the charter): every compute binding of every policy has a `compute_basis` entry, every `compute_basis` quotation is verbatim in that policy's `rule`, every `baseline.rule` is verbatim in the `rule`, every factor's ladder tiers are stated in prose in the `rule` with condition and value/method, and each tier is a branch of the factor's `decides` binding. Primitive semantics taken from `check_compute.py` (MONTHS = whole months with day-of-month correction; COUNT/SUM scoped to the loan; XCOUNT scoped to the member's operating rows; CFIELD = first matching holding).

Per policy, the quantities a reader must reproduce, and the result:
- Late charge: latest interest-accrual bill (`LATEST … due_date`), unpaid part = installment due − interest and scheduled-principal payments on that bill, final-installment branch on `bill_due == maturity_date`, repeat pct (24-month counts on loan and on operating lines), size reduction, weekend anchor (`DAYS('2024-01-01',d)%7`, 2024-01-01 a Monday, 5 = Saturday), lateness factor on shifted days, seasonal factor on due month (`MONTHS('2000-01-01',d)%12`, September = 8), one rounding after both multipliers, min/max bounds, active + grace (unshifted) + unpaid + no-prior-charge gate. Equivalent, except F6(a)/(c).
- CPI premium: days since expiry, whole months to maturity, three-tier coverage days (backdated = days since expiry + 365), insured amount (pledged value / principal + billed unpaid interest / principal), units left, average model year of units still pledged, placement calendar year, single rounding, product/active/cure/12-month gate. Equivalent.
- Autopay rate: relationship discount at funding, cap room, months left, offered discount, look-back (24 / months since funding + 1 / 12), counts within look-back, share, AutoDraft increment, reduction capped at cap room, subtract from rate on record, round 3, floor. Equivalent except F6(b) (first-line reads) and the F1 criterion.
- Total-loss release: latest submitted collateral_release request's serial and amount, unit pledged value, value still pledged, seasoning, payment record, operating relationship, small-unit loading, share principal basis, share rounded, premium rounded, max with settlement, min with principal. Equivalent except F6(b).
- Curtailment: casualty releases in 12 months, margin start, operating credit points, remaining-unit points, value left, average model year, test year, depreciation rate, declining (>36 m) / straight (12–36 m) / none, tested balance basis, excess = max(0, round(balance − margin% × value)). Equivalent except F6(b).
- Deferral fee: latest bill's paid interest+scheduled principal as installment size, three-way fee formula, casualty relief, operating credit (crop year == calendar year of grant), early credit (days to next due), seasoning (bills billed), autodebit credit, single rounding, floor 0, active + product gate. Equivalent except F6(a) (installment size ignores returns), F6(b), and the LTV grant gate is stated in the rule but not implemented in `grant_ok` (observation O3: it gates the action, not the fee figure).

### action_binding_and_uuids
- Each `(target_tool, computes)` pair is claimed by exactly one policy (six distinct tools, six distinct computes).
- Docstrings: each describes only its own effect; the eight occurrences of "after" are all "… after the charge/premium/release/curtailment/deferral" describing the tool's own receipt fields; no "before/first/then/until/prior"; no tool names another tool (each tool name occurs once in the module). No confirmation, review or wait is added by a docstring.
- Function bodies: none reads eligibility, history or another problem's state; none refuses or errors on an unresolved prerequisite (they only `ctx.find` the row they update and `ctx.create`/`ctx.update`).
- uuid8 tails: 7bb353d6, 372633e7, aa82d556, e8bdf554, c1e2b439, 57477c3f — distinct, no shared prefix/suffix, not sequential or adjacent. No evidence of reuse or batch derivation.

### prerequisite_graph
- `prerequisite` present on all six policies (LC `[]`, CPI `[]`, TL `[]`).
- Edges: autopay ← LC (value_input, gate `late_charges_in_lookback`); autopay ← CPI (value_input, `protection_premiums_in_lookback`); curtailment ← TL (value_input, `casualty_releases_12m`); deferral ← TL (value_input, `casualty_releases_12m`); deferral ← curtailment (state_gate, `equipment_loans.principal_balance`).
- Every `problem` is an extended policy id in this file, none self-referential, none a base policy. Graph acyclic (two components; longest chain TL → curtailment → deferral).
- Every `policy_source` is verbatim in the blocked policy's own `rule` (script check: all True).
- All edges `form: state`, no `fallback_reason` on any edge (consistent).
- Every `resolved_by` equals the depended-on policy's `target_tool`.
- value_input gates are real binding names in the blocked compute; the state_gate names a DB field rather than an eligibility gate (O3).
- `condition` vs sentence: F4 (deferral ← curtailment), F5 (autopay ← LC), O5 (curtailment ← TL) below.
- No authoring-viewpoint phrasing ("this task", "at the opening", "current world") in any prerequisite field.

### prerequisite_sentences
1. autopay ← LC: "The contract rate set on an enrolment is fixed only after the loan's fee entries carry a late charge for the most recently billed installment whenever that installment is still not paid in full after its late-charge grace period." Connective "only after" joining the policy's own result; state form in record words (fee entries, late charge, most recently billed installment); no tool/id/snake_case. One write brings it about: assess_installment_late_charge_7bb353d6 (the only late-charge write). Derivation: sentence → look up latest bill and its late-charge rows → the late-charge rule's own conditions (active, > grace, unpaid, none yet) say a charge is booked → that write. Single reading. Scope defect F5.
2. autopay ← CPI: "The contract rate set on an enrolment is not fixed until the loan's fee entries carry the collateral protection premium owed whenever renewed proof of insurance was not received within the insurance lapse cure period." "not … until"; state form; "owed" carries the CPI rule's own exclusions. One write: assess_collateral_protection_premium_372633e7. Passes.
3. curtailment ← TL: "The loan-to-value curtailment is worked out only after the collateral records carry the release of the unit named in a submitted collateral release request, with that release's proceeds applied to principal." "only after"; state form. In this difficulty only release_total_loss_unit_e8bdf554 writes a release, so the hop is unique. Breadth vs condition (condition says total loss; sentence any release request): O5, coupled to F3. The curtailment rule's opening "After a unit is released on a total loss, …" is a second wording of the same dependency (O4).
4. deferral ← TL: "The deferral fee is fixed only after the collateral records carry the release of every pledged unit that a submitted collateral release request names as destroyed in a total loss." "only after"; state form for the release; but "names as destroyed in a total loss" is not record-visible: `equipment_requests` has no reason field (request_type `collateral_release` serves sale and total loss alike) and `db_schema` defines `requested_amount` only as "net sale price … or appraised value of the replacement unit" (O2). One write: release_total_loss_unit_e8bdf554.
5. deferral ← curtailment: "A deferral is not granted until the principal balance stands within the post-release margin of the depreciated value of the units still pledged." "not … until"; state form. One write: apply_ltv_curtailment_c1e2b439 (the release lowers principal too but is the other prerequisite and does not alone close the gap). Strength/scope defect F4.
- No depended-on rule restates the sentence (LC, CPI and TL rules never mention autopay, curtailment or deferral; curtailment never mentions deferral).
- No rule states a cross-problem order outside these edges.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry (only the sentences governing a quantity or decision the extended policy touches are listed; all others are followed or untouched and inherited):

- LC vs equipment_evt_late_charge: grace sentence → superseded and replaced (adds latest-bill and active-status restriction) — declared. "Only one late charge … per installment" → superseded, same meaning — declared. Percentage/bounds/rounding clause → superseded — declared. "No late charge … deferred … nonaccrual" → narrowed further by "only while active" inside a declared replaced_by. Waiver sentences untouched. Base measure `equipment_msr_installment_paid` nets returns and uses "installment_amount in force at billing"; compute does neither → F6(a)/(c) (not an overwrite; a compute deviation). vs equipment_evt_returned_payment: reopened-installment late charge "as of the day it arises" vs extended "booked … the day the charge is booked" — latent, no returns in either world (observation). Other refs (deferral, prepayment, release, substitution, insurance) untouched.
- CPI vs equipment_insurance_requirement: amount clause superseded — declared. Base mandate "When it is not, a product with collateral_protection_available true places collateral protection insurance and assesses its premium" vs extended "no premium is booked … on a loan that is not in active status, or when a collateral protection premium was already booked less than 12 whole months before the placement date" — not declared → F2.
- Autopay vs equipment_rate_setting: autopay clause superseded — declared. Base "the relationship discount relationship_rate_discount_pct applies when the member holds an operating line in active status on the funding date" vs extended "the relationship discount the loan received at funding, which it received when the member held an operating line booked on or before the loan's funding date" — not declared → F1. Base cap/round/floor stacking is algebraically equal to the extended "cap less relationship, subtract from rate on record" when the rate on record carries the funding discount. vs equipment_autopay_enrolment: enrolment-date clause superseded — declared; member-instruction and account sentences followed.
- TL vs equipment_collateral_release: release-price clause superseded — declared ("limited to the principal balance" is in replaced_by). "A total-loss release applies the insurance proceeds the same way but carries no release fee and no prepayment fee" followed. Active-status gate and release-once followed. vs agg_cross_collateral: test inherited (no sibling loans in either world).
- Curtailment vs equipment_collateral_release: "after it the principal may not exceed max_ltv_after_release_pct of the value still pledged, any excess being paid down at the same time" superseded — declared, but that base sentence governs every release (sale and total loss) and the extended rule covers only total loss → dropped branch F3. vs payment_application/prepayment: prepayment-when-current and schedule-shortening followed.
- Deferral vs equipment_deferral: fee clause superseded — declared. The extended LTV grant gate is an added necessary condition to a base permission listed as "only when … It further requires …"; compatible addition, not a contradiction. Lead time, spacing, suspended-line, min-paid, max-life, cross-collateral inherited.

### factor_ladders
Per policy (declared label → audited label; multi-source = every non-fall-through tier a conjunction/disjunction over distinct records):

- LC (5 declared: 2 parameter, 3 method)
  - repeat_delinquency_pct — parameter, honest; tiers 6.0 / 5.5 / P(late_charge_pct) (5.0 or 4.0 by product) distinct; multi-source (AND / OR over loan and operating rows); cross_difficulty operating.
  - unpaid_size_reduction — parameter, honest; 1.0 / 0.5 / 0 distinct.
  - weekend_due_anchor — method; computationally a day offset (2/1/0) but it is a business-day due-date convention, accepted as method (O1).
  - lateness_factor — declared method; tiers multiply by 1.5 / 1.25 / 1.0 — a different number in the same formula → mislabelled (F7).
  - seasonal_factor — declared method; multiply by 0.8 / 0.9 / 1.0 → mislabelled (F7).
  - Surviving under the tests: 3 (repeat, size, weekend) — below the floor of 4; 1 method.
- CPI (4 declared: 2 parameter, 2 method)
  - backdated_coverage_term — method, honest (three different day-count formulas); not multi-source (tier 1 single condition).
  - insured_amount_basis — method, honest (three different bases); not multi-source.
  - unit_count_rate — parameter 5.5 / 6.0 / P(6.5); unit_age_loading — parameter 0.5 / 0.25 / 0.
  - 4 surviving, 2 parameter, 2 method; no multi-source and no cross-difficulty factor in this computation (allowed; the requirement is per task).
- Autopay (4 declared: 2 parameter, 2 method)
  - remaining_term_discount — parameter 0 / min(0.20, P) / P, distinct for every product with P > 0.
  - servicing_record_lookback — declared method; tiers set the window length (24 / months since funding + 1 / 12) of the same count → mislabelled (F7); tier 1 single-source.
  - servicing_record_share — declared method; tiers set a multiplier 0.25 / 0.5 / 0.75 / 1.0 → mislabelled (F7); multi-source.
  - autodraft_relationship_increment — parameter 0.04 / 0.02 / 0; multi-source (AutoDraft line AND its late charges); cross_difficulty operating.
  - Surviving: 2 (both parameter), 0 method — below both floors.
- TL (5 declared: 4 parameter, 1 method) — seasoning (+4/+2/0), payment record (−2/+5/0, multi-source), operating relationship (−3/+2/0, multi-source, cross operating), small unit (+10/+5/0), share principal basis (method, three bases). All honest, distinct. 5 surviving.
- Curtailment (6 declared: 4 parameter, 2 method) — casualty_margin_start (66 / 70 / P(max_ltv)) — the "unit released on a total loss in the last 12 months" part holds of every customer reaching this write under the rule's stated scope "After a unit is released on a total loss" (F8, coupled with F3); operating_credit_points (+4/−4/0, cross operating, multi-source); remaining_unit_points (−8/−4/0); depreciation_method (method, declining/straight/none — honest); depreciation_rate (12/10/0); tested_balance_basis (method — honest). Surviving: 5, 2 method.
- Deferral (6 declared: 4 parameter, 2 method) — fee_formula (method, honest: 0.75% / flat + 0.5% of excess / flat); casualty_relief (declared method; multiplies by 0.5 / 0.75 / 1.0 → mislabelled, F7); operating_credit (−50/−25/0, cross operating); early_request_credit (−25/−10/0); seasoning_charge (+50/+25/0); autodebit_credit (−20/+20/0, multi-source). Surviving: 5, 1 method.
- In every policy: bindings of different factors are disjoint, each `decides` is an input (never `result`), every ladder has three or more pairwise-disjoint tiers, no two tiers share an outcome (except remaining_term_discount on EquipDirect where P = 0, a product whose enrolment leaves the rate unchanged by rule), each fall-through equals the factor's `baseline` and equals what `baseline.rule` states (the look-back factor has no counterpart in `baseline.rule` because the baseline carries no share — O6), every tier's value is drawn from the charter.
- Per-task counts (multi-source / cross-difficulty) are evaluated in the task files.

### findings
Charter-global; "latent" means the consequence is demonstrated in a situation the charter covers but neither task world exercises; the task files state the per-world consequence.

- **F1 — SOURCE-POLICY RED (latent). Undeclared override of the relationship-discount criterion.** Base `equipment_rate_setting`: "the relationship discount relationship_rate_discount_pct applies when the member holds an operating line in active status on the funding date (equipment_msr_active_operating_lines at least 1)". Extended `equipment_ext_autopay_enrolment_rate`: "the relationship discount the loan received at funding, which it received when the member held an operating line booked on or before the loan's funding date"; compute `line_before_funding: EXISTS('operating') and CFIELD('operating','opened_date') <= F('opened_date')`. Same situation: member's only line booked 2019, closed or suspended before a 2025 funding → base: no relationship discount, cap room = cap; extended: discount received, cap room = cap − relationship. Different enrolment rates. Not in `overwrite`. Bears on task 0.
- **F2 — SOURCE-POLICY RED (latent). Undeclared narrowing of the CPI mandate.** Base `equipment_insurance_requirement`: "When it is not, a product with collateral_protection_available true places collateral protection insurance and assesses its premium". Extended: "no premium is booked … on a loan that is not in active status, or when a collateral protection premium was already booked less than 12 whole months before the placement date". Same situation: Truck & Trailer loan in deferred or nonaccrual status (an open loan) with lapsed proof → base books a premium, extended books 0. Not in `overwrite` (only the amount clause is). Bears on task 0.
- **F3 — SOURCE-POLICY RED (latent). Dropped branch of the post-release LTV test.** `overwrite` supersedes base "after it the principal may not exceed max_ltv_after_release_pct of the value still pledged, any excess being paid down at the same time", a sentence that in base governs every release (and, through `equipment_agg_cross_collateral`, every substitution). The extended rule scopes itself to "After a unit is released on a total loss", yet its casualty ladder keeps a fall-through "when no unit was released on a total loss in those 12 months" and its prerequisite sentence waits on "the release of the unit named in a submitted collateral release request" (any release). For a sale release: reading A — the extended policy applies (margin = max_ltv + operating points + unit points on depreciated value with interest-loaded balance); reading B — it does not, the base sentence is gone and no paydown is owed (or base still applies, a third reading). Different paydowns. Bears on task 1 (structure only).
- **F4 — SOURCE-POLICY RED (latent). Prerequisite sentence weaker on balance and broader in scope than its condition (deferral ← curtailment).** Sentence: "A deferral is not granted until the principal balance stands within the post-release margin of the depreciated value of the units still pledged." Condition: "after a total-loss release, the principal balance (with the interest the post-release test adds) is no more than …". Same situation: principal ≤ margin × tested value < principal + accrued interest → sentence: gate holds, grant now; condition and curtailment rule: curtail first. And with no total-loss release, the sentence still gates every deferral on an LTV test the condition does not impose. Bears on task 1.
- **F5 — SOURCE-POLICY RED (latent). Autopay waits on a late charge the late-charge rule may refuse.** Autopay sentence and condition wait on "a late charge for the most recently billed installment whenever that installment is still not paid in full after its late-charge grace period"; the late-charge rule books one "only while the loan is in active status". Base `equipment_autopay_enrolment` lets autopay change "while the loan is in active, deferred or nonaccrual status". Same situation: nonaccrual loan, latest bill unpaid past grace, member enrols → the autopay rule waits on a state no write can bring about (no solution) while base permits the enrolment. Bears on task 0.
- **F6 — SOURCE-POLICY RED (latent). Rule/compute gaps.** (a) LC `paid_on_bill` and deferral `installment_size` sum payment rows without netting `equipment_*_payment_return` rows, while base measure `equipment_msr_installment_paid` subtracts "the amount of return rows reversing any of those payments" and the LC rule speaks of payments "as they stand on the day the charge is booked". (b) `CFIELD`/`EXISTS` read only the first matching operating line (autopay `line_before_funding`, `line_on_autodraft`; deferral `line_current_year`) and `XCOUNT` counts late charges on all of the member's lines, while the rules speak of "an operating line … that carries no late charge" / "such an AutoDraft operating line" (that line). (c) LC `installment_due` uses the loan's current `installment_amount`, base measure uses "installment_amount in force at billing". Each gives a different number in a world with a returned payment, two operating lines, or a re-amortization after billing. Bears on both tasks (structure only).
- **F7 — SOURCE-FACTOR RED. Mislabelled `method` factors.** LC `lateness_factor` (×1.5/1.25/1.0) and `seasonal_factor` (×0.8/0.9/1.0); autopay `servicing_record_lookback` (window 24 / months+1 / 12 of one count) and `servicing_record_share` (×0.25/0.5/0.75/1.0); deferral `casualty_relief` (×0.5/0.75/1.0). Each tier substitutes a number into the same formula. Struck from the counts: LC keeps 3 factors (< 4); autopay keeps 2 factors and 0 method (< 4, < 1); deferral keeps 5 with 1 method (count holds). Bears on task 0 (LC, autopay) and task 1 (deferral).
- **F8 — SOURCE-FACTOR RED. Curtailment `casualty_margin_start` restates the policy's scope.** The rule's scope sentence is "After a unit is released on a total loss, the principal may not exceed the post-release margin …"; every customer who reaches this write has a total-loss release dated that day, so the condition part "a unit released on a total loss less than 12 whole months before" holds of every such customer, the fall-through tier is unreachable in scope, and the ladder divides customers only by funding age (66 vs 70). Coupled with F3 (under the broader reading the condition would divide customers). Bears on task 1.

Observations (no demonstrable consequence; not grounds for rework):
- O1 `weekend_due_anchor` is computationally a day offset; accepted as a business-day convention (method). If a stricter reading is taken it joins F7 and the LC computation has no method.
- O2 The deferral prerequisite sentence's "a submitted collateral release request names as destroyed in a total loss" is not record-visible: `equipment_requests` carries no release reason, and `db_schema` describes `requested_amount` as a sale price or replacement value only. The total-loss nature must come from the member.
- O3 The state_gate's `gate` is a DB field (`equipment_loans.principal_balance`), not an eligibility gate; the LTV gate is in the deferral rule but not in `grant_ok`.
- O4 The curtailment rule carries a second wording of its release dependency ("After a unit is released on a total loss, …") besides its prerequisite sentence.
- O5 The curtailment ← TL sentence names any release request while the condition names a total-loss release; unique in this difficulty because only one release write exists.
- O6 The autopay look-back factor's input has no counterpart in `baseline.rule` (the baseline grants the whole discount, so no look-back is read); its baseline is the fall-through tier.
- O7 "the crop year of the grant date" is not defined in prose; compute equates it with the calendar year.
- O8 Base product YAML: the `applied → active` transition's `means` is split by an unquoted comma into a stray key (blueprint parse artefact; no policy effect).
- O9 Seeded operating interest accruals bill periods in which no seeded advance is outstanding (seed history window; outstanding-principal identity still holds over seeded rows). Not a demonstrable contradiction of the operating charter; the late-charge rows the factors read are consistent with `operating_evt_late_charge` (5%, after the 15-day grace).

## closing_checklist
Written 2026-10-11, after both task files received their source_gt_comparison (reveal 04:20:35 UTC). Everything in the sections above was frozen before the reveal; the hash of this file at that moment was `74b753b58424180187f4cf9e7810cc3054fa5dcc1d34aa4050db861de5c31e49`. This checklist is the only part written after the reveal.

**The difficulty is NOT closed: the four relationships do not all PASS for any task.**

- Audit files: `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`, and this file sits alongside them. This is revision 1; no older revision exists. Both comparison sections are present, and neither carries a full PASS.
- Coverage and scope: `charter_scope` of task 0 is {late charge, CPI premium, autopay rate}, and of task 1 is {total-loss release, curtailment, deferral fee}. The two scopes are pairwise disjoint, together cover all six extended policies, and match the graph partition derived above.
  - Task tools: each task's scope names its three tools; there are no shared or orphaned tools, and the six uuid8s are distinct. — holds
- Problem trees: task 0 has n = 2 prerequisites, 2 value_input edges and a user-owned root. Task 1 has n = 2, 2 value_input edges plus 1 state_gate, and a user-owned release. Neither tree has a cycle, and the difficulty-wide graph is a DAG. — holds (task 1's closure proof carries false figures, T1-1)
- Factors: every computation has a self-sufficient baseline that gives a definite number different from gold, and every declared factor bears weight on its task's world. — holds
  - Each task has at least one multi-source factor and one cross-difficulty factor, and the cross-difficulty factors read seeded operating rows. — holds
  - Labels and ladders: — fails
    - LC: 3 surviving factors (F7).
    - Autopay: 2 surviving factors, 0 method (F7).
    - Deferral: `casualty_relief` mislabelled (F7).
    - Curtailment: `casualty_margin_start` restates the policy's scope (F8).
- Policy self-consistency: F1–F6 are charter-global latent REDs, with no consequence on either task world. — fails at charter level
- Proof fields: T0-2 and T1-2 (seed_consistency billing claims contradict `equipment_msr_principal_day_sum`) and T1-1 (closure figures). — fails
- Gates: the auditor did not re-run the instantiation-stage gates; per Step 0 the coordinator's snapshot is cited. The snapshot's replay_tasks FAIL lines are the verified FK-by-name artefact. — cited

Per-task verdicts:

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS on its world (charter F1, F2, F5, F6 latent) | PASS | SOURCE-FACTOR RED (T0-1) | derivation = GT; SOURCE-TASK RED on proof field (T0-2) |
| 1 | PASS on its world (charter F3, F4, F6 latent) | SOURCE-CHAIN RED on closure proof (T1-1); tree itself holds | SOURCE-FACTOR RED (T1-3) | derivation = GT; SOURCE-TASK RED on proof field (T1-2) |

## revision_2

### charter_global_frozen (revision 2)
- Re-audit after rework. Written before any revision-2 task GT was read.
- Inputs (sha256):
  - `equipment.extended.yaml` = `d8935bf4aacb8b7f092c8766375026fe70a56d85d065ff6e8695fdde131adf9e` — changed from round 1 (`972277f9…`), so this section is re-derived in full rather than carried forward.
  - `task_tools.py` = `4a7d5ba5…c19e` — unchanged, so `action_binding_and_uuids` is carried forward on the strength of that hash.
  - Blueprint files unchanged.
  - Masked views `0.view.json` = `d32cc9c9…fd9fc`, `1.view.json` = `777802c4…8c03` — match the coordinator's HASHES.txt.
- Gate snapshot (coordinator, cited not re-run): EXTENDED / TASK TOOL CONTRACT / SOLVABILITY / COMPUTE / GROUNDING OK, CACHE-DIFF INFO, SCOPE OK. REPLAY NOT OK only on the loan_id FK-by-name artefact already verified in round 1 (closures 65/65 and 30/30 True).
- The reworker's closure claims were not relied on; every item below is checked against the artifact.
- Base copy is still semantically identical to `blueprint/products/equipment.yaml` (all ten top-level keys equal).
- Mechanical sweep, all true:
  - every `compute_basis` is verbatim in its rule and every binding has one;
  - every `baseline.rule` is in its rule;
  - every overwrite `superseded_clause` is verbatim in its base rule, and every `replaced_by` is in the extended rule;
  - factor bindings are disjoint and exist, and each `decides` is an input;
  - every prerequisite `policy_source` is verbatim in its own rule, and `resolved_by` equals the depended-on policy's `target_tool`;
  - value_input gates are real bindings;
  - the graph is unchanged and acyclic (autopay ← LC, CPI; curtailment ← TL; deferral ← TL, curtailment).

### round-1 items re-checked
- **F1 — NOT genuinely closed (moved); now F1′, SOURCE-POLICY RED (latent).** The relationship-discount clause is now declared in `overwrite`. The replacement, however, decides "the relationship discount the loan received at funding" by the line's present status: "the member's operating line in active status, the first one the operating-line lookup lists where there are several, was booked on or before the loan's funding date" (compute `EXISTS('operating', status='active') and CFIELD('operating','opened_date', status='active') <= F('opened_date')`). Two base `equipment_rate_setting` sentences remain in force, unsuperseded: "The relationship discount is fixed at funding and is not removed if the operating line later closes" and "the two are added and capped at rate_discount_cap_pct".
  - Same situation: a T&T loan funded with an active line (rate on record = sheet − 0.10) whose line has since closed, then enrolment with a whole offered discount of 0.25.
    - Extended: no active line, so relationship at funding is 0, cap room 0.25, reduction 0.25, and the total discount off the sheet is 0.35.
    - Base: the discount was fixed at funding and the total is capped at 0.25, so the reduction is at most 0.15.
  - Different rates.
  - "The first one the operating-line lookup lists" is also an ordering artefact, not a criterion a lender weighs (N2).
- **F2 — closed.** Both CPI changes are now declared overwrites: the 12-month repeat exclusion, and the exclusion of loans that are not open. Compute `premium_due` admits active, deferred and nonaccrual, matching "no longer open, being paid off, declined or not yet funded".
- **F3 — closed.** The curtailment rule now scopes "When a unit of the loan has been released on the test date on sale, after a total loss or in substitution", with compute `released_today` (non-payoff releases dated NOW). The superseded base LTV sentence is now covered for every release kind.
- **F4 — closed.** The sentence is now "A deferral of a loan with a unit released on the grant date other than at payoff is not granted until the balance tested against the post-release margin stands within that margin of the tested value of the units still pledged". Its condition says the same, including the 90-day interest loading. Strength and scope now agree.
- **F5 — closed.** The sentence and condition now carry "whenever the loan is in active status and that installment is still not paid in full after its late-charge grace period", matching the late-charge rule's active-status restriction.
- **F6(a) — closed.**
  - LC: a fourth overwrite supersedes base "It applies to an installment not paid in full by then (equipment_msr_installment_paid below the installment due)". The replaced text adds back returns of "the most recent interest payment and the most recent principal payment on that bill", and compute `returned_on_bill` / `paid_on_bill` implement exactly that.
  - Deferral: `installment_size` subtracts returns of the latest payments, matching the rule.
  - The narrowing to "most recent" payments is declared, so it is legal (N3 observation).
- **F6(b) — rules and compute closed, factor ladders not → new N1 (below).**
  - Rules now say "none of the member's operating lines carries a late charge" or "one of the member's operating lines carries …" (autopay increment, TL relationship, curtailment credit), matching the all-lines XCOUNT.
  - `line_on_autodraft` is now `CFIELD(…, status='active', autodraft_enrolled=True)` (any such line).
  - Deferral `line_current_year` is `CFIELD(…, status='active', crop_year=grant_year) != None` (any such line).
- **F6(c) — closed.** "the level installment on the loan record on that day" is in the declared replaced_by.
- **F7 — closed.** These factors are now labelled `parameter`: `lateness_factor`, `seasonal_factor`, `servicing_record_lookback`, deferral `casualty_relief`.
  - `servicing_record_share` is replaced by `servicing_record_treatment` (method). Its tiers are genuinely different algorithms:
    - offered − 0.05 × (count of entries), floored at 0;
    - one half of the offered discount;
    - offered − 0.05 flat, floored at 0;
    - the whole offered discount.
  - Its outcomes are distinct and ordered sensibly by record severity.
  - Counts now: LC 5 (4 param, 1 method — weekend_due_anchor, O1 unchanged); CPI 4 (2/2); autopay 4 (3/1); TL 5 (4/1); curtailment 6 (4/2); deferral 6 (5/1).
- **F8 — closed.** With the widened scope (sale and substitution releases also reach the curtailment), the casualty condition now divides the customers who reach the write, and the fall-through `P('max_ltv_after_release_pct')` is reachable.
- **O5 — closed.** The curtailment ← TL condition now names "a release for the unit whose serial number a submitted collateral release request names", the same scope as its sentence.
- **O7 — closed.** "the crop year of the grant date being its calendar year" is now in the rule.
- **O1, O2, O3, O4, O6, O8, O9 — unchanged, as claimed.** Each still holds as an observation.

### new findings (revision 2)
- **N1 — SOURCE-POLICY RED (latent; check 2, ladder face disagrees with rule face).** Three factor ladders still describe one line's own late charges, while their rules and compute now count all of the member's lines:
  - autopay `autodraft_relationship_increment` ladder: "that line carries no late charge" / "that line carries a late charge"; rule: "none of the member's operating lines carries …" / "one of the member's operating lines carries …";
  - TL `operating_relationship_adjustment` ladder: "no late charge on it" / "a late charge on it";
  - curtailment `operating_credit_points` ladder: same wording as TL.
  - Same situation: an active AutoDraft line A with no late charge, and a second line B carrying a late charge 5 months old. Ladder: 0.04 / −3 / +4. Rule and compute: 0.02 / +2 / −4.
  - The deferral `operating_credit` ladder ("an active operating line not renewed for that crop year") overlaps its first tier as stated when two lines exist; the rule ("none renewed") is unique. Recorded as an observation.
  - Bears on tasks 0 and 1 (one operating line each, so no consequence on either world).
- **N2 — observation.** "the first one the operating-line lookup lists where there are several" ties a pricing determination to display order.
- **N3 — observation.** The declared unpaid-part definition adds back only the most recent interest and principal payment returns on a bill; an earlier returned partial payment stays counted as paid.
- **N4 — observation (latent).** Under the widened scope, a substitution release reaches the curtailment, but the curtailment's prerequisite sentence waits on "the release of the unit named in a submitted collateral release request". A substitution is registered as a `collateral_substitution` request, so for that case the sentence names no state.

### charter-global status (revision 2)
- SOURCE-POLICY RED (latent): F1′ and N1.
- Factor structure: passes on counts and labels. Every computation has 4–6 factors with at least 2 parameter and 1 method (accepting O1). Every ladder has 3 or more distinct tiers stated in the rule (wording drift N1 aside).
- action_binding_and_uuids: carried forward from round 1 (task_tools.py hash unchanged).

### closing_checklist (revision 2)
Written after both revision-2 comparisons.
- Files: one-to-one with the tasks; revision 1 text left untouched; revision_2 appended to all three files.
- Scopes: pairwise disjoint and jointly complete (task 0: LC, CPI, autopay; task 1: TL, curtailment, deferral). Tools closed, uuid8s unchanged and distinct.
- Trees: each has 2 prerequisites and 2 value_input edges, a user-owned write (task 0 root; task 1 release), and no cycle; the difficulty graph is a DAG.
- Factors: every computation has 4–6 honest factors (2+ parameter, 1+ method), a self-sufficient baseline differing from gold, and every factor bears weight. Each task has multi-source and cross-difficulty factors on seeded operating rows.
- Proof fields: all world assertions true in both tasks.
- Gates: coordinator snapshot cited (not re-run by the auditor); REPLAY FAIL lines are only the verified loan_id FK-by-name artefact.
- Round-1 RED closure verified against the artifacts:
  - F2, F3, F4, F5, F6(a), F6(c), F7, F8, T0-1, T0-2, T1-1, T1-2, T1-3, O5, O7 — closed.
  - F6(b) — closed in rules and compute, but residual ladder drift N1.
  - F1 — not closed; moved to F1′.
- **Difficulty NOT closed at the charter level.** Two latent SOURCE-POLICY REDs remain: F1′ (current-status relationship test vs base "fixed at funding" and the cap clause) and N1 (three factor ladders still say "that line" while their rules count all lines). Neither changes either task's scored solution, and every per-task relationship now PASSes.

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS on its world (charter F1′, N1 latent) | PASS | PASS | PASS |
| 1 | PASS on its world (charter N1 latent) | PASS | PASS | PASS |

## revision_3

### charter_global_frozen (revision 3)
- Written 2026-10-11 ~11:57 UTC, before any revision-3 task JSON was opened.
- Inputs (sha256):
  - `equipment.extended.yaml` = `1804d773fe07b4f874a2a229df6c467ef06632bfe5995abd5a9a05b3f8c1a260` — changed, so re-derived.
  - `task_tools.py` = `4a7d5ba5…c19e` — unchanged; action_binding_and_uuids carried forward.
  - Masked views unchanged from revision 2 (`d32cc9c9…`, `777802c4…`).
  - Base copy still semantically identical to the blueprint product.
- Gate snapshot cited as supplied (REPLAY FAIL lines only the known loan_id FK-by-name artefact).
- Mechanical sweep re-run, all true:
  - compute_basis verbatim and complete; baseline.rule in rule; overwrite clauses verbatim on both sides;
  - prerequisite sentences verbatim in their own rules, resolved_by = target_tool;
  - factor bindings disjoint and existing.
- Factor labels unchanged from revision 2: LC 4 parameter + 1 method; CPI 2 + 2; autopay 3 + 1; TL 4 + 1; curtailment 4 + 2; deferral 5 + 1.

### revision-2 items re-checked
- **F1′ — closed.** The relationship-discount override now reads: "the loan received that discount when the member's operating line, the first one the operating-line lookup lists where there are several, was booked on or before the loan's funding date and had not been closed by that date, and the discount so received stays fixed at funding and counts against the cap whatever the line's status has become since".
  - This now agrees with the base sentences still in force: "The relationship discount is fixed at funding and is not removed if the operating line later closes" and "the two are added and capped at rate_discount_cap_pct".
  - The round-2 counter-example (line closed after funding) now gives cap room 0.15 under both. Merged semantics unique.
  - Compute `line_before_funding`: `EXISTS('operating') and CFIELD(opened_date) <= F('opened_date') and (closed_date == '' or closed_date > F('opened_date'))` — but see N5.
- **N1 — closed.** The ladders now say what their rules say:
  - autopay `autodraft_relationship_increment`: "none of" / "one of the member's operating lines carries a late charge …";
  - TL `operating_relationship_adjustment` and curtailment `operating_credit_points`: same wording;
  - the deferral `operating_credit` second tier now reads "but none of the member's active lines renewed for that crop year", which no longer overlaps tier 1.
- **N2 — now explicit in the declared override, as claimed.** "The first one the operating-line lookup lists" remains a display-order tiebreak, not a criterion a lender weighs; kept as an observation.
- **N3, N4, O1–O4, O6, O8, O9 — unchanged, as claimed.** Each still holds as an observation.

### new finding (revision 3)
- **N5 — SOURCE-POLICY RED (latent; check 2, compute invents a basis the rule does not state).**
  - The rule requires the line to have been "booked on or before the loan's funding date". `db_schema.json` defines `operating_lines.opened_date` as "YYYY-MM-DD; empty until booked", so applied and declined lines carry `opened_date` = "".
  - The compute compares strings: `CFIELD('operating','opened_date') <= F('opened_date')` evaluates `'' <= '2025-06-19'` as True. An unbooked line therefore counts as booked.
  - Probe on the task-0 world with its line set to `status='applied', opened_date='', closed_date=''`: `line_before_funding` = True and relationship 0.10. The rule gives "not booked", so relationship 0 and cap room 0.25. Different enrolment rates (with the gold-world inputs: 7.35 by compute against 7.35 vs 7.29 depending on cap; in general up to 0.10 apart).
  - No consequence on either task world: task 0's line was booked 2021-03-15 and is active; task 1 is not in scope.

### charter-global status (revision 3)
- SOURCE-POLICY RED (latent): N5 only.
- Factor structure passes.

### N5 correction and demonstration (appended after freeze; the frozen N5 text above is left unchanged)
- The parenthetical in the frozen N5 entry ("with the gold-world inputs: 7.35 by compute against 7.35 vs 7.29 depending on cap …") is wrong. With the gold-world inputs the reduction (0.05, no increment because the line is no longer active) sits below both caps, so the two readings coincide at 7.39.
- A world that does separate them (scratch probe, deleted at close-out):
  - task-0 loan with maturity 2031-06-19 (offered discount 0.25);
  - no late charges on the loan or the line;
  - the member's only line `status='applied', opened_date='', closed_date=''`.
- Results:
  - Compute: `line_before_funding` True, cap room 0.15, granted 0.25 → **7.29**.
  - Rule ("booked on or before the funding date" is false for an unbooked line): cap room 0.25 → **7.19**.
- N5 stands as a latent SOURCE-POLICY RED.

### closing_checklist (revision 3)
- Files: revision_3 appended to all three; earlier revisions untouched.
- Scopes, trees, factors, proof fields, tools and uuid8s: unchanged from revision 2 and re-verified. Every per-task relationship passes on both worlds (see task files, revision 3).
- Round-2 RED closure verified against the artifacts:
  - F1′ — closed.
  - N1 — closed.
  - N2 — now named in the declared override; remains an observation.
- **Difficulty NOT closed at the charter level: one latent SOURCE-POLICY RED remains, N5.** The compute treats an unbooked operating line (empty `opened_date`) as booked before funding. It changes no scored value in either task.

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS on its world (charter N5 latent) | PASS | PASS | PASS |
| 1 | PASS on its world | PASS | PASS | PASS |

## revision_4

### charter_global_frozen (revision 4)
- Written 2026-10-11 ~12:45 UTC, before any revision-4 task JSON was opened.
- Inputs (sha256):
  - `equipment.extended.yaml` = `53528bea4ce4094f7c262432fdafd5bdeff1ef41c02f7ae5b7ca4cfd3b124962` — changed, so re-derived.
  - `task_tools.py` = `4a7d5ba5…c19e` — unchanged; bindings and uuid8s carried forward.
  - Views unchanged (`d32cc9c9…`, `777802c4…`).
  - Base copy still identical to the blueprint product.
- Gate snapshot cited as supplied.
- Mechanical sweep, all true:
  - compute_basis verbatim, complete and not stale; baseline.rule in rule; overwrite clauses verbatim on both sides;
  - prerequisite sentences verbatim, resolved_by = target_tool;
  - bindings disjoint and existing.
- Factor labels and counts unchanged from revision 3.

### revision-3 item re-checked
- **N5 — closed.**
  - Autopay compute now reads `line_booked_on`/`line_closed_on` through EXISTS guards. `line_before_funding` requires `loan_funded and line_booked_on != '' and line_booked_on != None and line_booked_on <= F('opened_date') and (line_closed_on == '' or line_closed_on == None or line_closed_on > F('opened_date'))`.
  - Re-run of the round-3 probe (only line applied and unbooked, offered 0.25, clean record): `line_before_funding` False, rate **7.19** = the rule reading (was 7.29).
  - Boundary probes:
    - line closed on the funding date: False, 7.19 — "had not been closed by that date" holds.
    - line closed after funding: True, 7.29 — "stays fixed at funding … whatever the line's status has become since" holds.

### the rework's other changes, checked
Empty-value guards were added to every policy's compute. Each is listed with its rule basis and reachability:
- **Late charge.**
  - `bill_due_on_record` (missing bill → NOW) feeds weekday, month and lateness only.
  - `charge_arises` now also requires `bill_due != None`, so with no billed installment no charge is booked. That matches "against the installment most recently billed": with no such installment there is nothing to book.
- **CPI premium.** `expiry_on_record`, `maturity_on_record` (missing → NOW). A missing expiry gives 0 days since expiry, so no premium is due. A funded open loan carries both dates (base funding requires proof of insurance; maturity is set at funding), so these branches are unreachable within the policy's scope.
- **Autopay.**
  - `maturity_on_record` and `funding_on_record` (missing → NOW).
  - `rate_reduction` is now also conditioned on `loan_funded`, with compute_basis the existing reduction sentence.
  - Base `autopay_open_loan` limits enrolment to active, deferred or nonaccrual loans, all of them funded, so the guard is unreachable in scope.
- **TL release / curtailment.** `funding_on_record` is unreachable (both policies require an active, hence funded, loan). `last_due_on_record` (no billed installment → NOW → 0 days): see N6.
- **Deferral.** `next_due_on_record` (missing → NOW → 0 days → no early credit). An active loan always carries a next due date before its final bill, so this is unreachable for a grantable deferral.
- **The coordinator relayed a claim of "one new scope sentence in the enrolment rule"; it is not borne out.** The enrolment rule still has the same nine sentences as in revision 3. No sentence about unfunded loans was added. The only change is the compute guard `and loan_funded`, which no rule sentence states (observation N7, unreachable under the base gate).
- **No regression.** Every task-world figure is unchanged:
  - task 0: LC 93.54, CPI 4,692.45, autopay 7.35; all factor substitutions and baselines identical; skip-LC / skip-CPI 7.30; opening 7.29.
  - task 1: TL 41,280.53, curtailment 8,829.52, deferral 97.26; all substitutions and baselines identical; post-curtailment excess 0; opening 0 / 264.51.

### new observations (revision 4)
- **N6 — observation.** The TL release and curtailment rules are silent on a funded loan that has no billed installment yet ("since the most recent installment due date"). The guard treats it as 0 days, which gives the "otherwise" tier: the principal balance. Probe: Used Equipment loan funded 2026-05-24 with no bill → share principal 370,000.00. This is the literal reading: neither dated tier holds, so the fall-through applies. No second reading is strong enough to call RED.
- **N7 — observation.** The `loan_funded` condition on the autopay reduction has no rule sentence; it is unreachable because only funded loans can enrol.

### charter-global status (revision 4)
- No SOURCE-POLICY RED remains.
- Factor structure passes.
- Standing observations: N2, N3, N4, N6, N7, O1–O4, O6, O8, O9.

### closing_checklist (revision 4)
- Files: revision_4 appended to all three; earlier revisions untouched.
- N5 closed, verified by probe. The charter-wide guards are rule-consistent or unreachable in scope (N6 and N7 are observations). Every task-world figure, closure value and factor baseline is unchanged.
- Scopes, trees (2 prerequisites, value_input edges, user-owned write, DAG), factors (4–6, honest labels, all bearing weight against honest baselines, multi-source and cross-difficulty per task), tools and uuid8s: unchanged and re-verified.
- Proof fields: all world assertions true. Two revision-note sentences misdescribe the charter (R4-a in 0.md, R4-b in 1.md); these are observations for the reworker, not REDs.
- **No SOURCE-POLICY, SOURCE-CHAIN, SOURCE-FACTOR or SOURCE-TASK RED remains.** All four relationships pass for both tasks, and the difficulty passes the source-layer audit.
- Gates: coordinator snapshot cited (not re-run by the auditor); the REPLAY FAIL lines are only the verified loan_id FK-by-name blueprint artefact.

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |
