# Policy-task audit — sr22_financial_responsibility_filings / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), revision 1. Freeze time: 2026-10-05 ~10:55 UTC, before any task's GT was revealed. Nothing in this section is derived from a revealed GT.
- Frozen inputs (sha256 verified by the auditor against the conductor's MANIFEST.sha256 and against the live files under `env/env_0035_personal_auto_insurance_carrier/tasks/sr22_financial_responsibility_filings/`):
  - `sr22.extended.yaml` 9a95697fafade40508cc5960afafb5fa5a1880b368737ded2dd15322e7e3505c
  - `task_tools.py` 956f5105f00f53ef9fa62c7ea38324120998931e41a9b7b04b1d05735880e3bf
  - `task_0.view.json` 101f23e71dbe30c083633182075782da8e86123dec8ecc1bab6cbbf3b9cce0dd, `task_1.view.json` d05bea04f547ce585b4f3ad357d29438ced845f7474d180e636401f9dab11339 (frozen_time, user_scenario, initial_state only)
- Permitted: blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/sr22.yaml`, and the variant tables of `products/auto.yaml` and `products/billing.yaml` for CPARAM reads), the extended charter, the tool module, the two views, `erlbench/`, and the DSL evaluator in `skills/erl-task-instantiate/scripts/check_compute.py` (read for the semantics of COUNT/XCOUNT/XLATEST/MONTHS/DAYS/within_months only).
- Masked and unread at freeze: `tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), the difficulty `worklog.md`, the scenario `worklog.md`, every other audit directory.
- Entry conditions (Step 0): gate snapshot `/tmp/erl35_views/sr22_financial_responsibility_filings/GATES.txt` supplied with commands and output lines — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability deferred (KB unpublished). Masked views and hashes supplied. Input complete.
- Base copy: lines 1-863 of `sr22.extended.yaml` diff against `blueprint/products/sr22.yaml` — identical except one trailing blank line. Verbatim.

### policy_conflict_scan

Seven extended policies, one target tool each:

| policy | target_tool (owner) | computes | prerequisite edge |
| --- | --- | --- | --- |
| sr22_ext_reinstatement_filing_charge | restore_certificate_19610618 (agent) | reinstatement_charge | [] |
| sr22_ext_vehicle_amendment_charge | amend_certificate_vehicles_869f2144 (agent) | vehicle_amendment_charge | -> reinstatement (value_input, restored_today) |
| sr22_ext_address_amendment_charge | amend_certificate_address_1c393d15 (agent) | address_amendment_charge | -> vehicle (value_input, amended_today) |
| sr22_ext_release_notice_charge | request_filing_release_10a5eab7 (user) | release_charge | -> address (value_input, amendments_on_release_day) |
| sr22_ext_corrected_refiling_charge | submit_filing_correction_4a6499e2 (user) | refiling_charge | [] |
| sr22_ext_policy_number_amendment_charge | amend_certificate_policy_9772f7fb (agent) | policy_amendment_charge | -> corrected refiling (value_input, refiled_today) |
| sr22_ext_name_amendment_charge | amend_certificate_name_9daa06e9 (agent) | name_amendment_charge | -> policy number (value_input, name_amended_today) |

- Subjects/triggers: each extended policy governs a distinct business event (sr22_reinstatement_filing, sr22_amended_filing x4 split by amendment reason, sr22_release, sr22_refile) plus its own transmission and fee rows. The four amendment policies share `sr22_amended_filing` but are split by reason (vehicle / address / policy number / name) and by target tool; no two compute the same quantity.
- Eligibility/time anchors: every extended policy inherits the base gates untouched — `before_sr26_effective` (reinstatement), `filing_open_for_amendment` (status filed/accepted, all amendments), `requirement_ended` (release, day 0 = required_through_date, request from day 1), `correction_in_time` (refile, day 0 = response_date, inclusive at day 10). No extended rule restates or narrows them. Base lifecycle: release only from `accepted`; refile only from `rejected`; reinstatement only from `cancel_notified`.
- Action parameters/terminal states: each tool writes one status change (or none) + one transmission row + one fee row; amendment tools add one amendment row. Compatible with the base event definitions, except the two inherited-provision gaps recorded as observations O1/O2 below.
- Cross-category read boundaries: reads billing (billing_ledger, billing account autopay, plan params) and auto (policies, auto_transactions, auto_change_requests, package params) only through CFIELD/CPARAM/XCOUNT/XLATEST scoped to the customer (auto/billing holding) — consistent with the `cross_category` declarations.
- Scope exclusivity and completeness (from the auditor's own tree walk in each task file, not from the masked charter_scope): task 0 = {reinstatement, vehicle, address, release}; task 1 = {corrected refiling, policy number, name}. Pairwise disjoint; union = all 7 extended policies. Complete.

### rule_compute_equivalence

Checked every compute binding against a verbatim `compute_basis` quotation and swept every rule sentence back to a binding. Findings:

- reinstatement: all 18 bindings have verbatim bases. Rule "A window of a number of months covers the entries dated less than that many whole months before today" = evaluator `_within` (0 <= MONTHS < n). `days_to_sr26` returns 0 when no SR-26 date (`... if F('sr26_effective_date') else 0`) — the rule is silent on that case; unreachable at this write (reinstatement exists only while cancel_notified with a date). Observation only.
- vehicle: 16 bindings, all quoted; `vehicle_report_delay` reads XLATEST over all history guarded by `replacements_1m >= 1` — equals the rule's "the vehicle replacement recorded within the past month".
- address: 15 bindings, all quoted; `move_effective` is the latest garaging change by recorded_date, guarded by `garaging_changes_1m` — equals "the latest garaging change recorded within the past month".
- release: 10 bindings, all quoted.
- corrected refiling: 12 bindings, all quoted; "rounded up to the cent" = `ceil(x*100)/100`.
- policy number: 18 bindings, all quoted; "the named insured's policy in force today" = CFIELD status='in_force' (first match; unique in task 1's world).
- name: 10 bindings, all quoted.
- Every `factors[].ladder` tier is a sentence of its `rule` and a branch of its `decides` binding, and vice versa (21+ ladders checked; no tier lives only in compute).
- No rule sentence promises a quantity compute omits (closing exclusion sentences — "State reinstatement fees are not part of this charge", "A release requested before the requirement has ended is declined", etc. — are scope statements, not quantities).

Result: PASS.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are unique across the 7 policies; no tool is claimed twice.
- Docstrings: grep for before/after/first/then/prior/until/once/already over `task_tools.py` hits only the module docstring line 6 ("agent has already worked out"), not any tool docstring. No tool names another tool or states a sequence position. No tool judges eligibility or a prerequisite (function bodies contain no conditional other than the case_number/driver routing in `submit_filing_correction_4a6499e2`, which routes the field written, not a gate).
- uuid8s: 19610618, 869f2144, 1c393d15, 10a5eab7, 4a6499e2, 9772f7fb, 9daa06e9 — no shared prefix, no sequence, no reuse. Observation O6: `19610618` is all-decimal and reads as a calendar date (1961-06-18); not demonstrably batch-derived.

Result: PASS (one observation).

### prerequisite_graph

- `prerequisite` is filled on all 7 policies (`[]` on reinstatement and corrected refiling).
- Edges: vehicle->reinstatement, address->vehicle, release->address, policy_number->corrected_refiling, name->policy_number. Every `problem` is an extended policy id of this file, none self-referencing, none a base policy. Graph = two chains, acyclic.
- Every `policy_source` is verbatim locatable in the blocked policy's own `rule` (checked by string search on all five).
- `form: state` on all five; no `fallback_reason` (correct, none is action-form).
- `resolved_by` = the depended-on policy's `target_tool` on all five, and each tool's runnable effect makes the stated state hold (reinstatement transmission row; vehicle_change amendment row with source_transaction_id; address_change amendment row; corrected_refiling transmission row; policy_number_change amendment row with source_transaction_id and filing.policy_id updated).
- `kind: value_input` on all five; each `gate` is a real binding of the blocked compute (restored_today, amended_today, amendments_on_release_day, refiled_today, name_amended_today).
- `condition` fidelity — observation O3: three conditions add a conjunct the sentence does not carry: vehicle edge "...and the filing status reads accepted"; policy-number edge "...and the filing status reads filed or accepted"; name edge "...and the filing certifies that policy". The address edge drops the sentence's scope "wherever the certificate lists vehicles". In no world of this difficulty does the added conjunct diverge from the sentence (the resolving tool makes both true at once), so no consequence is demonstrable.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any prerequisite text.

Result: PASS (observation O3).

### prerequisite_sentences

Four-point test per edge:

1. vehicle -> reinstatement: "A vehicle amendment charge is fixed only after every SR-26 cancellation transmitted on the filing is followed on the filing's record by a reinstatement transmission." Connective "only after"; waits on a record-visible state (sr22_transmission rows of type sr26_cancellation / reinstatement); no tool, id or snake_case token; "every" = open set stated open. Single write bringing the state about: only `restore_certificate_19610618` writes a reinstatement transmission. Derivation: sentence + the filing's ledger (SR-26 row with no later reinstatement row) + the reinstatement rule ("a reinstatement filing restores each certificate on it that is still cancel_notified") -> the reinstatement filing. One reading. PASS.
2. address -> vehicle: "An address amendment charge is not fixed until every vehicle endorsement recorded on the certified policy within the past month carries its vehicle amendment on the filing's record wherever the certificate lists vehicles." Connective "not ... until"; state = amendment rows (reason vehicle change) on the filing's record; open set. Only `amend_certificate_vehicles_869f2144` writes a vehicle_change amendment. The vehicle rule's first sentence ("A vehicle amendment reports to the ordering state one vehicle endorsement of the certified policy") supplies the one-per-endorsement mapping; the tool docstring scopes "vehicle endorsement" to added/replaced/removed (garaging changes are not vehicle endorsements; `find_auto_transactions` lists them separately). One reading. PASS.
3. release -> address: "A release notice is not transmitted until every garaging change recorded on the certified policy within the past month carries its address amendment on the filing's record wherever the certificate's amendment rules require address amendments." Connective "not ... until"; state = address_change amendment rows; open set; scope clause matches `amendment_on_address_change`. Only `amend_certificate_address_1c393d15` writes it. The address rule ("reports ... the household's new mailing address") makes one amendment per move, not per garaging row; a reader who wanted one amendment per garaging row would find no endorsement parameter on the tool to tie it to. Observation O4: "carries its address amendment" is possessive per garaging change; a per-row reading is weaker but not excluded by the sentence alone.
4. policy number -> corrected refiling: "A policy-number amendment charge is fixed only after every state rejection recorded on the filing is answered on the filing's record by a corrected refiling transmission." "only after"; state = corrected_refiling transmission rows; only `submit_filing_correction_4a6499e2` writes one. PASS.
5. name -> policy number: "A name amendment charge is not worked out until every policy bound for the named insured after the certificate was requested is named on the filing's record by a policy-number amendment." "not ... until"; state = policy_number_change amendment rows; only `amend_certificate_policy_9772f7fb` writes one. PASS.

- No rule carries a second wording of its dependency, a tool name or another problem's id; no depended-on rule restates the sentence.
- Undeclared cross-problem orders: none found. The value-coupling sentences ("rides in the envelope of a reinstatement transmission sent today", "a reinstatement transmission sent today", "amendments entered on the filing's record today", "a corrected refiling sent today", "another amendment entered today") are tier conditions without ordering connectives and each is subsumed by a declared edge chain.
- Base ordering sentence: base `sr22_amendments` "An amendment is transmitted only while the filing status is filed or accepted." states an order (reinstatement/refile before amendment). It does not ground any edge alone — each blocked extended rule carries its own prerequisite sentence. Observation O5 (per the skill's rule for base sentences).

Result: PASS (observations O4, O5).

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- `sr22_evt_fees`: "A new filing carries the certificate's filing_fee" — not touched by any extended policy (no request write in this difficulty). "A corrected refiling after a rejection carries refiling_fee_after_rejection" — overwritten by corrected refiling (declared). "an amendment carries amended_filing_fee" — overwritten by vehicle/address/policy/name (declared). "a reinstatement filing carries reinstatement_filing_fee" — overwritten by reinstatement (declared). "a release notice carries release_filing_fee" — overwritten by release (declared). "a fee of 0.00 is not assessed" — overwritten by release and corrected refiling (declared, "at 0.00 where the sum is zero"); NOT overwritten by vehicle, policy-number or name amendments (finding G4). "A lapsed certificate needs a new filing..." — untouched. "Each fee is assessed once per occurrence and billed to the policy's billing account as a filing fee tied to the assessment." — inherited by all; the tools never write the billing posting (observation O1).
- `sr22_amendments`: "The amendment carries amended_filing_fee, once per amendment." — overwritten by all four amendment policies (declared). Gate sentence and certified-fact list inherited and honoured. "A change that the certificate does not certify needs no amendment." — restated consistently ("A vehicle change on a certificate that does not list vehicles needs no amendment and carries no charge"; same for address).
- `sr22_reinstatement_filing_rule`: "carrying reinstatement_filing_fee" overwritten (declared); time gate inherited.
- `sr22_release_rule`, `sr22_transmission_and_response`, `sr22_sr26_cancellation`, `sr22_agg_policy_filings`: no sentence handles a scored quantity differently; inherited. `sr22_agg_policy_filings` "switched off when the last of them is released or lapses" — the release tool does not switch `auto_policies.financial_responsibility_filing` off (observation O2).
- Disguised forms: no anonymous intermediate replaces a base value without declaration (every intermediate sits on a declared replaced_by sum); no 0/1 multiplier; no dropped base branch. No author language calls the base output a "wrong value".

Finding G4 (below) is the only undeclared deviation.

### factor_ladders

Per policy (label p = parameter, m = method; MS = multi-source; XD = cross_difficulty category):

| policy | factors | p / m | MS factors | XD |
| --- | --- | --- | --- | --- |
| reinstatement | restoration_rate (p, MS: sr22_ledger + billing_ledger, XD billing), restoration_courtesy (p, XD auto), restoration_cure_path (m, MS: auto policy cancel date + billing ledger fee + billing account autopay, XD billing), restoration_mailing (p, MS: variant method + filing SR-26 date), restoration_plan (p, XD billing), restoration_schedule_check (p, XD auto) | 5/1 | 3 | billing, auto |
| vehicle | vehicle_amendment_rate (p), vehicle_line_basis (m, XD auto), vehicle_report_lateness (p, XD auto), vehicle_amendment_envelope (p, MS variant + ledger), vehicle_amendment_standing (p, MS returned + notice rows, XD billing) | 4/1 | 2 | auto, billing |
| address | address_amendment_rate (p), address_vehicle_basis (m, XD auto), address_report_lateness (p, XD auto), address_reprint (p, MS filing date + variant), address_notice_check (p, MS auto txn + billing notice, XD billing) | 4/1 | 2 | auto, billing |
| release | release_clearance (p, MS SR-26 rows + reinstatement rows), release_clearance_basis (m, XD auto), release_confirmation_copies (p), release_envelope (p, MS variant + ledger) | 3/1 | 2 | auto |
| corrected refiling | correction_rate (p), correction_speed (m), corrected_refiling_delivery (p, MS variant + auto_change_requests, XD auto), corrected_refiling_handling (p, XD auto) | 3/1 | 1 | auto |
| policy number | policy_change_rate (p), policy_change_courtesy (p, XD auto), policy_change_timing (m, XD auto), policy_change_envelope (p, MS), replacement_plan_check (p, XD billing), limits_recertification (p, MS two policies' packages, XD auto) | 5/1 | 2 | auto, billing |
| name | name_amendment_rate (p), pending_version_basis (m, MS filing status + ledger), name_amendment_envelope (p, MS), identity_reverification (p, MS ledger + variant) | 3/1 | 3 | none |

- Declared counts: every policy 4-6 factors, >=2 parameter, >=1 method. Every ladder has three stated tiers, pairwise disjoint as stated, each tier stated in the rule with its value or method, each implemented in its `decides` binding. Each factor's `decides` is an input, never `result`; bindings disjoint across factors of one policy. Every fall-through tier equals the factor's `baseline`, and every `baseline` is what `baseline.rule` states (rate = the certificate's fee, every adjustment absent -> 0 or "as it stands").
- Labels: correction_speed and address_vehicle_basis are plainly methods (day-proration; per-vehicle additive). The other five method factors (cure_path, vehicle_line_basis, release_clearance_basis, policy_change_timing, pending_version_basis) select a fraction together with a rounding direction (floor to dollar / ceil to dollar / none); the rounding direction is an algorithmic change, so the label is not demonstrably dishonest. Observation O7.
- Ladder reality — failures (findings G1-G3 below): variant-dependent inversions for in-state certificates in four rate ladders (G1); the address reprint ladder's paper-mail conjunct is universal at the address-amendment write and its electronic tier is unreachable (G2); the correction-rate ladder's customer-code conjunct is universal at the customer-owned corrected-refiling write and its Cardinal-code fall-through is unreachable (G3).
- Ladder reality — passes: tenure courtesies, rush/courier mailing tied to a short SR-26 or policy-end window, enclosure-vs-certified-mail envelopes, late-reporting charges keyed to endorsement effective vs recorded date, limits re-certification on a package change, identity re-verification after an identity-mismatch rejection, repeat-correction pricing — each is a condition personal-auto filing operations plausibly weigh and an outcome they plausibly publish. Weaker but not demonstrably unreal (recorded as observation O8): restoration_plan (installment interval on a reinstatement filing charge), vehicle_amendment_standing (billing standing on a vehicle amendment), address_notice_check (move during a cancellation-notice period), release_clearance "reinstatement sent today" tier, corrected_refiling_delivery (courier because the certified policy ends soon).

### findings

**G1 — SOURCE-FACTOR RED (unreal ladder: tier outcomes inverted for in-state certificates).**
- Symptom: four rate ladders whose tiers reference a certificate fee publish, for the four in-state variants, prices no filing operation would publish.
- Root cause: the ladder mixes fixed constants (`K(...)`) with variant fees (`P(...)`) whose in-state values (amended_filing_fee 0.00, filing_fee 25.00) fall outside the constants' order.
- Evidence (variant table lines 105-108, 159-162, 321-324, 375-378; params of each policy):
  - `restoration_rate` (reinstatement): tier 1 "reinstatement transmission within 24 months **and** a returned payment within 12 months" -> `P('filing_fee')` = 25.00 for in-state; tier 2 "reinstatement within 24 months and **no** returned payment" -> `repeat_restore_rate` = 30.00. The customer with a bounced payment pays 5.00 less than the clean-billing customer.
  - `vehicle_amendment_rate` (in-state SR-22 Owner, FR-44 Owner): no amendment in 12 months -> 10.00; exactly one -> `amended_filing_fee` = 0.00; two or more -> 20.00. The second amendment of the year is free, the first costs 10.00.
  - `policy_change_rate` (all in-state): 7.50 / 0.00 / 22.50, same inversion.
  - `name_amendment_rate` (all in-state): "another amendment entered today" (bundled) -> 5.00 while the unbundled standard is 0.00 — the bundled price exceeds the standalone price.
- Demonstrated consequence: each named tier is a treatment no personal-auto carrier publishes for customers in that situation (the skill's "a tier's value ... that no such business would publish"). Struck under the counting rule, `name_amendment_charge` keeps 3 factors (< 4) — see task 1. On OOS certificates (both tasks' worlds) the same ladders are monotone (35/30/25; 10/15/20; 7.50/15/22.50; 5/20/15), so neither task's scored value is affected.
- Affected: `sr22.extended.yaml` factors restoration_rate (line 989), vehicle_amendment_rate (1212), policy_change_rate (1987), name_amendment_rate (2184) and their rule sentences. Bears on task 0 (restoration_rate, vehicle_amendment_rate) and task 1 (policy_change_rate, name_amendment_rate).

**G2 — SOURCE-FACTOR RED (address_reprint: a conjunct holds of every customer who reaches the write; one tier unreachable).**
- Evidence: address amendments exist only where `amendment_on_address_change: true` — variants rank 3 and 4 (lines 241, 295) — and both carry `transmission_method: paper_mail` (lines 219, 273). Every other variant has `amendment_on_address_change: false` (lines 133, 187, 349, 403), and the rule says "A move on a certificate whose amendment rules do not require address amendments needs no amendment and carries no charge."
- Consequence: the tier-1 conjunct "with a certificate sent by paper mail" holds of every customer who reaches `amend_certificate_address_1c393d15`; the tier "reprint_age_months or more with a certificate sent electronically -> electronic_reissue_charge" can never be taken. The live ladder is two tiers (>= 36 months -> 4.00; otherwise 0). Struck, `address_amendment_charge` keeps 4 factors (bounds still met).
- Affected: factor address_reprint (line 1472) and its rule sentence (1355-1357). Bears on task 0.

**G3 — SOURCE-FACTOR RED (correction_rate: a conjunct holds of every customer who reaches the write; fall-through unreachable).**
- Evidence: the policy's only write is `submit_filing_correction_4a6499e2`, `owner="user"`, "Submit the customer's own corrected detail", whose `corrected_item` is "exactly one of: full_name ... date_of_birth ... license_number ... case_number" — the four customer-correctable codes (`customer_correctable_rejections`, line 226/280). The rule itself sends company codes elsewhere: "Cardinal corrects and refiles on its own when the code is one Cardinal corrects"; no agent tool exists for that path.
- Consequence: "the latest rejection code is one the customer must correct" holds of every customer reaching this write; the fall-through tier "a code Cardinal corrects -> refiling_fee_after_rejection" (the baseline) is never taken. The live ladder is two tiers (>= 2 rejections -> 20.00; exactly 1 -> 10.00). Struck, `refiling_charge` keeps 3 factors (< 4) — see task 1.
- Affected: factor correction_rate (line 1781), rule sentence lines 1728-1732, tool contract line ~150. Bears on task 1.

**G4 — SOURCE-POLICY RED (latent; undeclared deviation from an inherited base sentence).**
- Evidence: base `sr22_evt_fees`: "a fee of 0.00 is not assessed". Release and corrected refiling declare the overwrite ("at 0.00 where the sum is zero"); vehicle, policy-number and name amendment policies do not, while their tools always book a fee row ("records one filing charge ... in the amount given").
- Consequence (same situation, two conclusions): an in-state SR-22 Owner certificate (electronic), a vehicle addition, exactly one amendment in 12 months, no replacement/late report/billing issues -> vehicle_amendment_charge = 0 + 0 + 0 + 0 = 0.00. Inherited base: not assessed (no fee row). Extended + tool: "booked once per vehicle amendment" -> a 0.00 fee row. The same holds for policy-number (7.50/0.00 rate tier, no replacement-timing/plan/limits charges, electronic) and name (0.00 rate, accepted status, electronic, no identity rejection).
- Not reachable in either task's world (all four amendment sums there are non-zero). Bears on no task's scored solution.

**Observations (no demonstrable consequence on a scored solution).**
- O1: base "billed to the policy's billing account as a filing fee tied to the assessment" (and the `sr22_fee_assessed -> billing:billing_fee_charged` trigger) is never executed — no tool writes billing_ledger and erlbench executes no triggers. Terminal states omit the billing posting.
- O2: base `sr22_agg_policy_filings` "switched off when the last of them is released" — `request_filing_release_10a5eab7` leaves `auto_policies.financial_responsibility_filing` true.
- O3: prerequisite `condition` strengthenings (see prerequisite_graph).
- O4: possessive "carries its address amendment" per garaging change (see prerequisite_sentences).
- O5: base amendment gate states a cross-problem order; each extended edge has its own sentence.
- O6: uuid8 `19610618` reads as a calendar date.
- O7: five method factors are fraction-plus-rounding-direction selectors.
- O8: weaker-realism conditions listed under factor_ladders.
- O9 (realism of prerequisite settings, judged against personal-auto practice):
  - vehicle <- reinstatement and policy-number <- corrected refiling: realistic — a carrier cannot amend a certificate the state shows as cancelled-pending or rejected (the base status gate agrees).
  - address <- vehicle and name <- policy-number: plausible — an amended owner certificate prints the full vehicle schedule and the policy number, so printing the address or name amendment on a stale schedule/policy number would be wrong. Real carriers would usually carry all changed facts on one amended certificate rather than sequence separately priced amendments.
  - release <- address: weakest. A release/SR-26 at the end of a requirement does not, in practice, depend on the state holding the driver's current address; the only business rationale is that the state's release confirmation goes to the address on file. Not unreal enough to demonstrate a consequence.
  - Base realism (task-0 shape): in practice the SR-26 form is itself the instrument that ends an SR-22; this charter models SR-26 (cancellation) and "release notice" as distinct, which makes "reinstate, then release" (two filings and two charges to end a filing whose requirement already ended) the charter-correct path where a real carrier would simply let the pending SR-26 stand. This is the scenario constitution's model, applied consistently; recorded, not red-lit.
  - Policy-number amendment timing: real carriers make the policy-number amendment (or new SR-22) effective on the replacement policy's start date; the tool moves `sr22_filings.policy_id` immediately, so a bound-but-not-in-force policy is certified from today. The charter has no amendment effective date, so no scored consequence.
  - Variant prerequisite settings (sr22_eligible false on Plus/Preferred/Premier; financial_responsibility_plan_allowed false on Direct Bill Monthly; state limits OH/IN/KY/WV/TN/MO 25/50/25, IL 25/50/20, MI 50/100/10, VA 50/100/25, FR-44 VA 100/200/50; IL SR-26 lead 15 days): consistent with real-world practice.

## closing_checklist

Written after the reveal of both tasks (2026-10-05 10:56 UTC). Everything above this heading was written before any GT was opened and has not been edited since.

- Files: `0.md`, `1.md` correspond one-to-one with tasks 0 and 1; `_difficulty.md` alongside. Revision 1, no older revision exists. Not every comparison section carries a PASS: both tasks are SOURCE-FACTOR RED.
- Coverage: all 7 extended policies are covered; task scopes (task 0: reinstatement, vehicle, address, release; task 1: corrected refiling, policy number, name) are pairwise disjoint and match the revealed `charter_scope` exactly. Task tools and GT are closed: every GT write uses the policy's own target tool, and the auditor's blind write sequences equal GT in every argument, owner, order and terminal state. uuid8s are independent and unreused (observation O6 only).
- Trees: task 0 has 3 prerequisite problems with 3 value_input edges; task 1 has 2 with 2. Each has a customer-owned write (release; corrected refiling). No cycle; the difficulty graph is two disjoint chains.
- Factors: every declared factor of both tasks bears weight against an honest baseline on its world, and every baseline-alone number (25.00, 15.00, 15.00, 0.00; 0.00, 15.00, 15.00) is definite and differs from gold. **Not met**: ladder reality — G1 (four rate ladders inverted for in-state certificates), G2 (address_reprint: paper-mail conjunct universal, electronic tier unreachable), G3 (correction_rate: customer-code conjunct universal, fall-through unreachable). After striking, task 1's refiling_charge and name_amendment_charge each keep 3 factors (< 4).
- Policy self-consistency: G4 (latent undeclared deviation from "a fee of 0.00 is not assessed" for the vehicle, policy-number and name amendments) bears on no task's scored solution.
- Gates: the auditor does not re-run gates (Step 0). The artifacts are unchanged since the gate snapshot (`sr22.extended.yaml` 9a95697f..., `task_tools.py` 956f5105... re-verified at reveal), so the snapshot stands for the final form; check_traceability is still deferred to KB publication.
- GT comparison: blind derivations equal GT figure for figure — task 0: 33.85 / 33.75 / 21.00 / 10.25; task 1: 32.50 / 19.25 / 9.25; every factor_sensitivity and baseline_result; every prerequisite_closure edge, skip value and resolution order.

**Difficulty result: does not pass the source-layer audit.** Task 0: SOURCE-FACTOR RED (G1, G2). Task 1: SOURCE-FACTOR RED (G1, G3; refiling and name computations fall below 4 surviving factors). Problem tree, unique solution and per-world policy self-consistency PASS for both tasks.

## revision_2

### charter_global_frozen (revision 2)

- Re-audit requested by the conductor (round 2). Written before any round-2 task JSON was opened. Revision 1 text above is left untouched.
- Inputs verified by the auditor (sha256, view = live file): `sr22.extended.yaml` f33a442e1f55b14da8df8493eaeda674cfc6bac3fad3138470ecca7e698fc3b5 (changed from 9a95697f...), `task_tools.py` ca2c20fce4e073dbda31a4fecdb45559427a4deade29a8ec728996e614fe8aa6 (changed from 956f5105...), `task_0.view.json` 101f23e7... and `task_1.view.json` d05bea04... (byte-identical to round 1). Gate snapshot `/tmp/erl35_views/sr22_financial_responsibility_filings.r2/GATES.txt`: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred. Input complete.
- Because both shared inputs changed, every charter-global section is re-derived in full below rather than carried forward.
- contamination_disclosure: the auditor read the round-1 GT of both tasks (revision 1 comparison). The task views are unchanged, so the auditor knows the round-1 scored values. The round-2 derivation was recomputed independently from the round-2 charter with the gate's own DSL evaluator; where a round-2 value equals a round-1 value, that is a recomputed fact and not a reuse of revision 1. The round-2 task JSONs stay masked until both task files' revision_2 frozen sections are on disk.
- Diff scope (round 1 -> round 2): base section lines 1-868 unchanged (still verbatim against `blueprint/products/sr22.yaml`). `task_tools.py`: only `restore_certificate_19610618` renamed `restore_certificate_8ba85022`, body and docstring unchanged. Extended charter: restoration_rate ladder; vehicle, policy-number and name standard rates moved to new constants (`standard_change_rate`, `standard_policy_change_rate`, `standard_name_rate` = 15.00, "on every certificate type"); address_reprint ladder now age-only; correction_rate ladder rebuilt on the rejected transmission's kind; release prerequisite sentence reworded; three prerequisite `condition` texts trimmed; reinstatement `target_tool` renamed.

### policy_conflict_scan (revision 2)

Same seven policies and five edges; scopes unchanged and disjoint (task 0: reinstatement, vehicle, address, release; task 1: corrected refiling, policy number, name); all base gates still inherited untouched. No new overlap. PASS.

### rule_compute_equivalence (revision 2)

Re-swept every binding of the changed policies:
- reinstatement `restore_rate` = "the certificate's reinstatement_filing_fee plus bounce_restore_surcharge / plus repeat_restore_surcharge / reinstatement_filing_fee" — verbatim in rule and compute_basis.
- vehicle/policy/name rate bindings now `K('standard_*_rate')` on the fall-through; the rule says "which is standard_change_rate on every certificate type" (resp. standard_policy_change_rate, standard_name_rate) and the fall-through sentences name the same constant. The baseline rules repeat the same sentence.
- address `address_reprint_charge`: "reprint_age_months or more carry full_reprint_charge, at least partial_age_months but fewer than reprint_age_months carry partial_reissue_charge, and fewer than partial_age_months carry none" = compute.
- corrected refiling: new binding `rejected_version_kind` = LATEST transmission_type ("the rejected transmission is the latest transmission on the filing's record"); `refile_rate` = repeat if >= 2 rejections, first if exactly one and kind 'original', else refiling_fee_after_rejection — matches the three rule sentences. Observation O11: the refiling policy's `inputs.history` still lists a `latest response_code` read that no binding uses any more (descriptive metadata only).
- Every ladder tier still appears in its rule and its `decides` binding and vice versa. PASS.

### action_binding_and_uuids (revision 2)

`(target_tool, computes)` still unique. New uuid8 `8ba85022` is fresh (no shared prefix with 869f2144, 1c393d15, 10a5eab7, 4a6499e2, 9772f7fb, 9daa06e9). The extended charter references only `restore_certificate_8ba85022` (vehicle edge `resolved_by` updated). Docstrings unchanged: no ordering words, no tool names. **O6 closed.** PASS.

### prerequisite_graph (revision 2)

Five edges, same targets, all `form: state`, `kind: value_input`, gates real bindings, `resolved_by` = depended-on target tool; acyclic. `policy_source` verbatim in each blocked rule (re-checked by string search). Conditions:
- vehicle edge: "Every SR-26 cancellation transmission on the filing's record is followed on that record by a reinstatement transmission." = the sentence. Status conjunct removed.
- address edge: now carries "wherever the certificate lists vehicles". = the sentence.
- release edge: "...an amendment entry with the reason address change entered no earlier than the recording date of the latest garaging change ... wherever the certificate's amendment rules require address amendments." = the new sentence.
- policy-number edge: status conjunct removed. = the sentence.
- name edge: "Every auto policy of the named insured issued after the filing's requested date is the source policy of an amendment entry with the reason policy number change." The "certifies that policy" conjunct is gone. Residual wording difference ("issued" for "bound"; an amendment row records the issuing transaction, not a policy) is no stronger or weaker on any world of this difficulty (the bound policy's issue date is its bind date). Residual observation O3'.
**O3 closed** (O3' residual, no consequence). PASS.

### prerequisite_sentences (revision 2)

- Release sentence reworded: "A release notice is not transmitted until the filing's record shows an address amendment entered no earlier than the recording date of the latest garaging change recorded on the certified policy within the past month, wherever the certificate's amendment rules require address amendments." Four-point test: "not ... until"; record-visible state (one address_change amendment row with an entry date compared with one recording date); no tool/id/token; scope stated. Exactly one write of this difficulty (`amend_certificate_address_1c393d15`) brings it about. The per-garaging-row reading is gone: one amendment entered on or after the latest recording date satisfies it. **O4 closed.**
- The other four sentences are unchanged and keep their revision-1 single readings (re-read in the new file). No second wording, no tool name, no undeclared cross-problem order added by the rework. O5 (base gate ordering sentence) unchanged by design. PASS.

### override_declarations (revision 2)

- The four amendment policies still declare overwrites of "The amendment carries amended_filing_fee, once per amendment." and "an amendment carries amended_filing_fee"; the move of vehicle/policy/name standards from the certificate's `amended_filing_fee` to 15.00 constants is exactly what those declarations replace, so it is a declared override (in-state certificates, whose base amended_filing_fee is 0.00, now pay a standard 15.00 for these three amendment kinds).
- G4 re-check ("a fee of 0.00 is not assessed", still not overwritten by the amendment policies): the smallest reachable sums are now vehicle 5.00 (first rate 10.00, removal tier floor(10/2)), policy number 4.00 (7.50 less 20 % = 6.00, later-start tier floor(4.80)), name 2.00 (bundled 5.00, pending tier floor(2.50)), address 2.00 (bundled 5.00, no-garaging tier floor(2.50)). No amendment sum can be 0.00, so the inherited base sentence and "booked once per ... amendment" can no longer give two different conclusions. **G4 closed.**
- Reinstatement smallest sum 6.00 (15.00 x 0.8 = 12.00, half floor) — non-zero. Release and corrected refiling keep their declared "at 0.00 where the sum is zero". O1/O2 unchanged (blueprint-rooted). PASS.

### factor_ladders (revision 2)

- Counts unchanged (6/5/5/4/4/6/4; >= 2 p and 1 m each), labels unchanged, fall-throughs = baselines, baselines = `baseline.rule` values.
- **G1 re-check:**
  - restoration_rate: fee + 10.00 / fee + 5.00 / fee. In-state (fee 15.00) 25.00 / 20.00 / 15.00; OOS (25.00) 35.00 / 30.00 / 25.00. Monotone everywhere, and a bounced payment now always costs more.
  - vehicle 10.00 / 15.00 / 20.00, policy number 7.50 / 15.00 / 22.50, name 5.00 (bundled) / 15.00 / 20.00 — constants independent of certificate type, monotone.
  - **G1 closed.**
- **G2 re-check:** address_reprint tiers by certificate age only (>= 36 months 4.00; 12-35 months 2.00; < 12 months 0). No conjunct holds of every customer reaching the write; all three tiers reachable (filings of any age can need an address amendment); outcomes distinct. Reissuing an older certificate in full is a plausible reason to charge. **G2 closed.** The factor is now single-source (evidence [date]); the multi-source requirement is met at task level by other factors.
- **G3 re-check:** correction_rate tiers are now ">= 2 rejections -> 20.00; exactly one rejection of the original certificate -> 10.00; exactly one rejection of a later transmission (e.g. an amendment) -> refiling_fee_after_rejection". No tier conditions on the rejection code any longer, so nothing restates the customer-owned write's scope. The fall-through is reachable through the customer tool: an amendment sent while the filing is `filed` and rejected for a customer-correctable code (e.g. name_mismatch after a name amendment) gives status rejected, one rejection, latest transmission an amendment, and the customer corrects through `submit_filing_correction_4a6499e2`. Pricing a corrected original (the state holds no certificate at all) above a corrected amendment (the earlier certificate stays on file) is a plausible business distinction. **G3 closed.** Observation O10: the fall-through path is narrow under the base lifecycle (an amendment rejected on an `accepted` filing has no `accepted -> rejected` transition, so it reaches this write only from `filed`), but it exists.
- O7 and O8 unchanged (not reworked, as declared).

### findings (revision 2)

- G1, G2, G3, G4: closed (evidence above).
- O3, O4, O6: closed (O3' residual wording on the name edge, no consequence).
- O1, O2, O5, O7, O8, O9: unchanged, as the reworker declared; still observations.
- New: O10 (narrow but reachable correction-rate fall-through), O11 (stale `inputs.history` entry on the corrected refiling policy). No new RED-grade defect found in the charter or the tool module.

### closing_checklist (revision 2)

Written after the round-2 reveal (12:26 UTC); the revision_2 charter-global sections above were written before it.
- Files: `0.md` and `1.md` each carry revision_1 (untouched) and revision_2; every revision_2 comparison carries PASS.
- Coverage: all 7 extended policies covered; scopes disjoint and complete. Tools and GT closed: blind round-2 sequences equal GT exactly. uuid8s independent; `8ba85022` is new.
- Trees: task 0 has 3 prerequisites / 3 value_input edges, task 1 has 2 / 2. Each has a customer-owned write. The difficulty graph is acyclic (two chains).
- Factors: 6/5/5/4 and 4/6/4 factors, each with >= 2 parameter and 1 method. Per task >= 1 multi-source and >= 1 cross-difficulty factor. Every ladder has three distinct, reachable, real tiers (G1-G3 closed). Every factor bears weight against an honest baseline. Baseline-alone numbers 25.00, 15.00, 15.00, 0.00 / 0.00, 15.00, 15.00 are definite and differ from gold.
- Policy self-consistency: G4 closed (no amendment sum can reach 0.00); remaining items are observations O1, O2, O3', O5, O7-O11.
- Gates: the conductor's round-2 snapshot is all green, with traceability deferred to KB publication. Artifacts re-verified at reveal: `sr22.extended.yaml` f33a442e..., `task_tools.py` ca2c20fc....

**Difficulty result (revision 2): PASS** — both tasks PASS on all four relationships; every round-1 RED closed; no regression; no new RED.
