# Policy-task audit — setaside_property_charges_and_repairs / charter-global

## charter_global_frozen
- Auditor: erl-task-policy-audit (independent of the instantiator). Revision 1. Frozen 2026-10-15T07:16Z, before any task GT was read.
- sha256 prefixes (re-checked against the gate snapshot): `setaside.extended.yaml` d3ff387b446136f6; `task_tools.py` 8ce0084dd64aa89b; masked views `0.json` 703dba21d1e564f9, `1.json` f9cb88f03b2d8403.
- Read: `blueprint/{blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml}` (cross-category enums/params only), the extended charter, `task_tools.py`, the two masked views (frozen_time, user_scenario, initial_state), `erlbench/` and the `skills/erl-task-instantiate/scripts/check_compute.py` DSL semantics (MONTHS, `_within`, LATEST, CFIELD, XCOUNT).
- Masked / unread at freeze: `tasks/setaside_property_charges_and_repairs/tasks/*.json` in full (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure). No recursive search was run over `tasks/`.
- Entry conditions (Step 0): gate snapshot `snapshot_r1.txt` supplied: extended / task-tool contract / replay --check / solvability / compute / grounding / cross_fire all OK. Traceability shows only the tool-name provenance miss for `update_reserve_flood_ec384f8d` ("non-tool_name misses: 0"). validate_scenario is INVALID only on "required document not found" (pre-render). Both are pre-render items, not audit findings. Masked views and hashes were supplied. Entry accepted.
- The base section of the charter (lines 1-1487) is byte-identical to `blueprint/products/setaside.yaml` (`diff` empty).

Policy ids used below: P1 `setaside_ext_reserve_tax_projection` (agent, `update_reserve_tax_b755da65`), P2 `setaside_ext_returned_tax_refund` (user, `return_tax_refund_0b9f20b8`), P3 `setaside_ext_reserve_hazard_projection` (agent, `update_reserve_hazard_5ea539e7`), P4 `setaside_ext_reserve_flood_projection` (agent, `update_reserve_flood_ec384f8d`), P5 `setaside_ext_returned_hazard_premium` (user, `return_hazard_premium_b6a621c2`), P6 `setaside_ext_returned_flood_premium` (user, `return_flood_premium_57ae44ac`).

### policy_conflict_scan
- Subjects: P1/P3/P4 share `setaside_charges_updated` but compute different fields (`annual_property_tax`, `annual_hazard_premium`, `annual_flood_premium`) through different tools. P2/P5/P6 share `setaside_refund_credit` / `credit_amount` but each is scoped "only for such a refund/premium" by refund kind (property tax / hazard / flood), and each `replaced_by` sends the other two kinds to "the rule written for it". These are mutually exclusive and compatible.
- Eligibility inherited from base `setaside_evt_refund` (active status, `refund_once`, credit <= original disbursement) is not weakened by any extended rule or tool. The tools validate nothing (see check 3). Base `setaside_charge_review` "updated only from a ... bill on file" is honoured by the `setaside_request_id` argument plus each projection's "the review takes it from ..." sentence.
- Time anchors: projections read "the twelve months before the review" on `request_date`. Refund rules read "the handling date". The single clock is `frozen_time`. No conflict.
- Cross-category reads: residency (status, absence_start_date, events), maturity (status, resolution_deadline, successor_intent, variant_name, appraisal), payoff (status, good-through), jumbo (advance_type ledger, appraised_value_at_closing). All enums exist in `db_schema.json` (`corporate_advance_property_tax`, `corporate_advance_insurance`, `inspection_fee`, `nonoccupancy_confirmed`, `absence_monitoring`, `overdue`, `closed`, `due_and_payable`, `extension_period`, `sell_property`, `deed_in_lieu`, `retain_property`, `terms_issued`, `accepted`, `Death of Last Surviving Borrower`).
- Scope: six extended policies. The blind expectation is task 0 = {P2 root, P1} and task 1 = {P6 root, P5, P3, P4}. That is pairwise disjoint and jointly complete. It is confirmed against `charter_scope` only after the reveal, in the task files.
- Inherited base clause with no tool: `setaside_charge_review` says "when the updated charges leave the balance projected to cover fewer than low_balance_notice_months months of the charges the set-aside pays, the borrower receives a low-balance notice". No task tool sends a notice, so the clause cannot become a scored write. Observation O-1.

### rule_compute_equivalence
- Mechanical sweep (scratch script): every `compute_basis` value of all six policies is a verbatim substring of its own `rule`. Every sentence of every `baseline.rule` is a sentence of its `rule`. Every overwrite `replaced_by` is verbatim in its rule.
- Manual sweep, per policy:
  - P1: windows (12/24 months on `request_date`) ✓. Previous year = 24-month paid less 12-month paid ✓. Corrected / single / sum bases ✓. Restoration / inflation / zero ✓. Exemption full / half / zero ✓. Installment-count / month-proration / zero share ✓. Blend and single half-up rounding ✓ (RND is Python `round`; no .5-cent tie arises on either world).
  - P2: overpayment ✓. Reserve period left ✓. Horizon to deadline / good-through / reserve-left ✓. Half-year blocks `int((h+5)/6)` and year blocks `int((h+11)/12)` ✓. Renewal-date / quarter-block / prorated insurance ✓ (`MONTHS(NOW,last_due)+12` = whole months to the anniversary). Cushion ✓. Floor ✓. Retention ✓.
  - P3/P4: pay-plan / carry-forward / latest-paid ✓. Change loading ✓. Occupancy/residence loading ✓. Appraisal loading ✓ (tier 2 "exceeds ... by no more than" means value > closing, which matches `ap_val > ap_close` in the elif). Fee ✓. Share ✓. The three loadings are summed and applied once ✓.
  - P5/P6: withdrawn term, cancellation date, days and months in force ✓. Flat / short-rate (P5) and flat / duplicate-coverage (P6) / by-days ✓. Horizon, insurance mode, cushion, floor and retention ✓.
- No compute branch lacks a rule sentence, and no rule tier lacks a compute branch.
- Edge left implicit: P3/P4 `share` falls to the installment tier when a withdrawn bill exists but no paid bill does. The rule is silent on that case. It is not reached on either world. Observation O-2.

### action_binding_and_uuids
- `(target_tool, computes)` pairs are all distinct: (b755da65, annual_property_tax), (0b9f20b8, credit_amount), (5ea539e7, annual_hazard_premium), (ec384f8d, annual_flood_premium), (b6a621c2, credit_amount), (57ae44ac, credit_amount).
- uuid8s b755da65, 0b9f20b8, 5ea539e7, ec384f8d, b6a621c2, 57ae44ac: distinct, no shared prefix, no sequence or adjacency pattern.
- Function bodies validate nothing. There is no status check, no dedup check, no prerequisite check and no refusal path. Each does one find, one create/update and returns a receipt. So the tool layer judges no prerequisite.
- Docstrings name no other tool, carry no example values (so no gold leak), and state no sequence position.
- Ordering words do occur, but each describes the tool's own action or its cause: "after a review of the ... bills on file", "Afterwards the reserve shows ...", "the figure held before the update" (all three update tools), and "after a policy term the reserve had paid was cancelled" (`return_hazard_premium_b6a621c2`, `return_flood_premium_57ae44ac`). None of them leaks an edge. Observation O-3 lists the full class.

### prerequisite_graph
- `prerequisite` is filled everywhere: P1, P3 and P4 have `[]`.
- Edges: P2←P1 (action, gate `tax_on_file`); P5←P3 (action, `haz_on_file`); P5←P4 (action, `flood_on_file`); P6←P4 (action, `flood_on_file`); P6←P3 (action, `haz_on_file`); P6←P5 (state, `reserve_balance`).
- Every `problem` is an extended id in this file, none is a base id and none is a self-reference. The graph is acyclic: topological order P1→P2 and {P3, P4}→P5→P6.
- Every `policy_source` is verbatim in the blocked policy's own rule (mechanical check: True for all six edges).
- `fallback_reason` is present exactly on the five action-form edges and absent on the state edge.
- Every `gate` names an existing compute binding of the blocked policy, and every `kind` is `value_input`.
- `resolved_by` equals the depended-on policy's `target_tool` in all six edges. Each resolver changes the gated binding: the update tools rewrite the figure; the hazard return raises `setaside_balance`.
- `condition` wording matches the sentence strength. No authoring-viewpoint phrasing appears.

### prerequisite_sentences
- P2: "The kept amount of a returned property tax refund is not worked out until the annual property tax on file has been reviewed against every property tax bill received since it was last set."
  - Connective "not ... until". Action form. No tool, id or snake_case token.
  - Fallback test: the update leaves no record-visible state other than the changed figure. The `setaside_charges_updated` event writes no ledger row (`triggers: []`). The fallback stands.
  - Derivation: "annual property tax on file ... reviewed against ... bills" → P1 ("sets the annual property tax ... whenever the property tax bills on file are reviewed") → `update_reserve_tax_b755da65`. Single reading.
- P5 (two sentences) and P6 (first two sentences) apply the same pattern to hazard and flood. They lead to P3 and P4 respectively, with a single reading each, and the fallbacks stand on the same grounds.
- P6 third sentence: "The kept amount of a returned flood premium is fixed only after the reserve's payment of every withdrawn hazard insurance term carries a refund credit."
  - State form, worded in table terms (refund credit referencing the payment = `setaside_transactions.event_type=setaside_refund_credit`, `source_txn_ref`).
  - Exactly one write of this difficulty brings it about. P5's rule credits "the reserve's payment of the withdrawn hazard term". P2 credits a tax payment and P6 a flood payment. The base refund rule has no tool here.
  - Derivation: withdrawn hazard bill → its payment → P5 → `return_hazard_premium_b6a621c2`. Single reading.
- Strength note: the sentence says "every withdrawn hazard insurance term", while P5 credits only "the withdrawn hazard insurance bill on file with the latest due date". With two paid withdrawn hazard terms on file, no write of the charter could satisfy the gate. Neither world has a second one, so there is no consequence. Observation O-4.
- No depended-on rule restates any of these sentences. No rule states a cross-problem order outside the declared edges (keyword sweep over before/after/until/first/then/once). No base sentence grounds an edge.

### override_declarations
- `setaside_charge_review` (P1, P3, P4), sentence by sentence:
  - S1 "reviewed every ... and whenever a new bill is received ... only from the evidence named": followed.
  - S2 "updated only from a ... bill on file": followed.
  - S3 "annual property tax is the sum ... / hazard premium is the billed_amount of the current hazard policy term / flood ... current flood policy term": each clause is overwritten by its own policy, declared, and scoped to Summit reserves.
  - S4 "never changes a Partially Funded LESA's ... never adds funds": followed (the tools touch only the figure).
  - S5 low-balance notice: inherited (see O-1).
- `setaside_evt_refund` (P2, P5, P6):
  - R1 "the refunded amount is credited back ... referencing the original disbursement in source_txn_ref, and is reversed from the HECM loan balance": the amount is overwritten and declared in all three. `source_txn_ref` is followed. The HECM reversal does not apply to Summit (the base refund trigger maps HECM only; the tools post nothing to the loan).
  - R2 "only while active": inherited.
  - R3 refunds after close: not applicable.
  - R4 "never exceeds the original disbursement ... at most once": inherited. The kept amount is at most the overpayment or unearned premium, which is at most the disbursement.
- No undeclared override, anonymous intermediate, 0/1 multiplier or dropped branch was found.

### factor_ladders
| policy | factor | label | tiers (values / methods) | multi-source tiers | cross-difficulty |
|---|---|---|---|---|---|
| P1 | tu_basis | method | corrected installment / single installment / sum | ✓ (withdrawn ∧ received bills; count ∧ none-withdrawn) | – |
| P1 | tu_assess | parameter | 6 / 2 / 0 % | ✓ | – |
| P1 | tu_exempt | parameter | 77.00 / 38.50 / 0 | ✓ (profile status ∧ residency event) | residency |
| P1 | tu_span | method | paid/2 / month proration / 0 | ✓ (variant param ∧ bill count) | – |
| P2 | tr_horizon | method | deadline / good-through / reserve-left | tier 1 single record | maturity (+payoff) |
| P2 | tr_taxneed | method | half-year / year blocks / prorated | ✓ | – |
| P2 | tr_insneed | method | renewal dates / quarter blocks / prorated | single source | – |
| P2 | tr_cushion | parameter | 2 / 1 / 0 months | tier 1 ✓; tier 2 one profile row | residency |
| P2 | tr_floor | parameter | 0 / 25 / 50 | single record | maturity |
| P2 | tr_retain | parameter | 1 / 0.5 / 0 | ✓ (two advance types; none ∧ fee) | – (jumbo is not a difficulty) |
| P3 | hu_plan, hu_change, hu_occ, hu_appraisal, hu_fee, hu_span | M, P, P, P, P, M | sum / carry-forward / latest; 8/4/0; 10/5/0; 6/3/0; 32/12/0; replacement-month / installment-count / 0 | hu_occ t1 ✓, hu_appraisal ✓, hu_change ✓ | hu_occ residency, hu_appraisal maturity |
| P4 | fu_plan, fu_change, fu_residence, fu_appraisal, fu_span | M, P, P, P, M | same shapes; residence 20/10/0 | fu_residence t1 ✓, fu_appraisal ✓ | residency, maturity |
| P5 | hr_basis, hr_horizon, hr_insneed, hr_cushion, hr_floor, hr_retain | M, M, M, P, P, P | flat / short-rate / days; …; cushion 2/1/0; floor 0/25/50; retain 1/.5/0 | hr_cushion t1 ✓, hr_retain ✓ | maturity, residency |
| P6 | fr_basis, fr_horizon, fr_insneed, fr_cushion, fr_floor, fr_retain | M, M, M, P, P, P | flat / duplicate-coverage (fee 50 then days) / days; …; cushion 3/1/0 | fr_cushion t1 ✓, fr_retain ✓ | maturity, residency |

- Counts per policy: P1 4 (2P/2M); P2 6 (3P/3M); P3 6 (4P/2M); P4 5 (3P/2M); P5 6 (3P/3M); P6 6 (3P/3M). All are within 4-6, each has ≥2 parameter and ≥1 method, and each has ≥3 tiers with distinct outcomes.
- `decides` is never `result`. Binding sets are disjoint within each policy. Every tier is stated in the rule with its condition and value or method, and every tier is implemented in compute. The fall-through of every factor equals its `baseline` binding, and that binding is what `baseline.rule` states.
- Labels are honest: method tiers change the algorithm (block counting, basis, renewal-date counting); parameter tiers change a number.
- Realism, charter level:
  - Strong: tu_exempt is the CA $7,000 homeowners' exemption × ~1.1% levy. tu_assess restoration mirrors Prop 8 restoration and inflation mirrors the Prop 13 2% cap. The release floor 50 matches the RESPA $50 surplus threshold. Full retention under corporate advances matches the "surplus only to a current borrower" practice. Short-rate on insured-requested cancellation is standard. The NFIP Federal Policy Fee ($50) being fully earned on duplicate-coverage cancellation is accurate. The horizon running to the due-and-payable resolution deadline is reasonable.
  - Weaker, observations only: O-5 (tr_retain/hr_retain/fr_retain tier 2: an occupancy-inspection fee halves the surplus the borrower keeps; it is proprietary but weakly grounded); O-6 (P5 estate cushion 2 months vs P6 estate cushion 3 months for the same reserve and situation; 3 months exceeds the conventional 2-month escrow cushion); O-7 (`installments_per_year: 2` is a fixed constant for a 38-state servicer, although the task 1 seed itself is an annual-bill SC property). None of these changes a scored value in a way that can be shown wrong against a written schedule.
- The world-specific realism of the occupancy/residence loadings (hu_occ, fu_residence) is judged per task. See `1.md`.

### findings
Charter-global REDs: none.

Observations (no rework demanded by the audit):
- O-1: the base low-balance-notice clause is inherited with no tool (affects both tasks; no scored write).
- O-2: P3/P4 share tier is silent when withdrawn bills exist without any paid bill (not reached).
- O-3: ordering words in docstrings. The full class is: `update_reserve_tax_b755da65`, `update_reserve_hazard_5ea539e7` and `update_reserve_flood_ec384f8d` ("after a review", "Afterwards", "before the update"); `return_hazard_premium_b6a621c2` and `return_flood_premium_57ae44ac` ("after a policy term ... was cancelled"). None names a tool or a sequence position.
- O-4: P6's "every withdrawn hazard insurance term" is broader than what P5 can credit (latest withdrawn term only). Not reached on task 1's world, which has one withdrawn hazard term.
- O-5 / O-6 / O-7: realism notes above.
- O-8: action-form fallbacks are justified (no record-visible state), so this is not a defect.

## closing_checklist
Written after both reveals (2026-10-15T07:19Z). The section above was frozen before any reveal (sha256 prefix c28337182b77221c) and is unchanged.
- Per-task files: `0.md` and `1.md` correspond one-to-one with tasks 0 and 1, and this file sits alongside them. This is the first revision, so there are no older revisions.
- Comparison results:
  - task 0: PASS.
  - task 1: Policy, Chain and Task PASS; **SOURCE-FACTOR RED** (F-T1-1, vacancy double-loading in hu_occ / fu_residence on the seeded vacancy-rated replacement terms).
  - Therefore the difficulty does not close in this round.
- Coverage and scope: `charter_scope` is task 0 = {P1, P2} and task 1 = {P3, P4, P5, P6}. The scopes are pairwise disjoint and jointly cover all six extended policies. Task tools are closed to GT. All six uuid8s are independent.
- Trees:
  - task 0: n = 1, with 1 value_input edge and a user root.
  - task 1: n = 3, with 5 value_input edges and P5/P6 user-owned.
  - The difficulty-wide graph is acyclic.
- Factors:
  - Counts are within bounds and every factor bears weight on its task's world.
  - Every baseline is honest, and every fall-back figure differs from gold (11,507.90 / 703.10 / 2,820.00 / 1,445.00 / 2,446.42 / 1,424.71).
  - Realism fails on task 1 only (F-T1-1).
- Gate re-run on the final form: not applicable. The artifacts are unchanged since snapshot_r1 (hashes d3ff387b446136f6 / 8ce0084dd64aa89b re-checked). The difficulty awaits rework of F-T1-1.

task0=PASS task1=SOURCE-FACTOR RED
charter=CLEAN

## revision_2
### charter_global_frozen (r2)
- Re-audit after rework. Written 2026-10-15 before either task's revision-2 GT was read.
- Inputs:
  - Charter `setaside.extended.yaml` e9c7f87f71c06423 (changed from d3ff387b446136f6).
  - `task_tools.py` 8ce0084dd64aa89b (unchanged).
  - Gate snapshot `snapshot_r2.txt`: all gates OK. Traceability shows only the unlock tool-name miss; validate is INVALID only on pre-render documents. Entry accepted.
- The charter hash changed, so every charter-global check was re-derived in full on the current text. No round-1 copy of the charter was kept, so this is a fresh derivation, not a diff.
- Mechanical re-run, all six policies, no issue:
  - base section identical to `blueprint/products/setaside.yaml`
  - every `compute_basis` value verbatim in its rule
  - every `baseline.rule` sentence in its rule
  - every edge `policy_source` verbatim in the blocked rule
  - `fallback_reason` present exactly on action-form edges
  - every `replaced_by` verbatim in its rule
- Params, factor ladders, baselines and the key compute bindings were re-read. They are identical in content to round 1: P1–P5 rules and computes behave identically (task 0 recomputes to the same figures: 11,167.44 / 688.61 and the same factor sensitivities); occ_pct, cushion_m, unearned, ins_part and result expressions are unchanged.
- **The only change found:** P6's state-form prerequisite sentence. It is now "The kept amount of a returned flood premium is fixed only after the reserve's payment of the latest withdrawn hazard insurance term carries a refund credit." The edge `condition` now reads "The reserve's payment of the withdrawn hazard insurance bill with the latest due date has a refund credit on the reserve referencing that payment."
- §policy_conflict_scan, §rule_compute_equivalence, §action_binding_and_uuids, §prerequisite_graph and §override_declarations: conclusions unchanged from round 1 (re-derived; same results).
- §prerequisite_sentences: the P6 state edge was re-tested.
  - Connective "only after"; state form; worded in table terms; no tool or id.
  - Its strength now equals what the resolver can bring about: P5 credits "the withdrawn hazard insurance bill on file with the latest due date".
  - Exactly one write (P5) brings it about. Single reading: latest by due date, the only date a withdrawn bill carries that the rules use.
  - The sentence and the condition agree. **O-4 is closed.**
- §factor_ladders: unchanged (same counts, labels and tiers).
  - O-5, O-6, O-7 stand.
  - O-1, O-2, O-3 stand.
  - O-8 stands (the fallbacks are justified).
- Charter-global REDs: none.

### closing_checklist (r2)
Written after the revision-2 reveals (2026-10-15T12:03Z). The charter-global part of §revision_2 was frozen before them.
- Per-task files: `0.md` and `1.md` each carry revision_2 and correspond one-to-one with the tasks. The revision-1 text is untouched.
- Comparison results:
  - task 0: PASS (carried forward, GT unchanged).
  - task 1: PASS (F-T1-1 closed).
- Scope: `charter_scope` is {P1, P2} for task 0 and {P3, P4, P5, P6} for task 1. The scopes are disjoint and jointly cover all six extended policies. Task tools are closed to GT. The six uuid8s are independent and unchanged.
- Trees:
  - task 0: n = 1, one value_input edge, user root.
  - task 1: n = 3, five value_input edges, P5/P6 user-owned.
  - The difficulty graph is acyclic.
- Factors:
  - Every computation has 4–6 factors (≥2 parameter, ≥1 method). Each task has multi-source and cross-difficulty factors, and their rows are seeded.
  - Every factor bears weight against an honest baseline.
  - Fall-backs differ from gold: 11,507.90 / 703.10 / 2,820.00 / 1,445.00 / 3,150.35 / 1,457.53.
  - Realism holds on both worlds after the rework.
- Gates on the final form: `snapshot_r2.txt` (2026-10-15T11:59:37Z) on charter e9c7f87f71c06423, tools 8ce0084dd64aa89b and view 4cb3497566b2fe76.
  - EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING and SCOPE are all OK.
  - Only pre-render items remain open: the unlock tool-name traceability miss and validate's "required document not found".
- Round-1 REDs: F-T1-1 closed. Observation O-4 closed. No new defect and no regression.
- Open observations (no rework demanded): O-1, O-2, O-3, O-5, O-6, O-7, O-8, O-T0-1, O-T1-1, O-T1-2, O-T1-3, O-T1-4.

VERDICT revision_2: task0=PASS task1=PASS charter=CLEAN

## revision_3
### entry (r3)
- Gate: `tail -1 tasks/setaside_property_charges_and_repairs/worklog.md` printed exactly "REWORK round 3: gates 7/7 green". Proceeded.
- I ran `/tmp/erl0064_coord/snapshot.sh setaside_property_charges_and_repairs 3` (snapshot_r3.txt, 2026-10-15T15:32:01Z). Results:
  - EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE (branches 91.00, steps 16.00, history_rows_max 16, branches_max 125), GROUNDING and SCOPE are OK.
  - TRACEABILITY is now fully OK (0.json 18/0, 1.json 26/0).
  - validate_scenario is INVALID. I re-ran `erlbench.validate.validate_scenario` to see why: 20 errors, all "required document … not found" in other difficulties (maturity ×6, payoff ×8, hecm ×6). There are 0 errors for this difficulty. Not a red for this audit.
- Hashes vs snapshot_r2:

| file | r2 | r3 | status |
|---|---|---|---|
| `0.json` view | 703dba21d1e564f9 | 703dba21d1e564f9 | unchanged |
| `1.json` view | 4cb3497566b2fe76 | 7639ed76bc536d19 | changed |
| `task_tools.py` | 8ce0084dd64aa89b | 8ce0084dd64aa89b | unchanged |
| `setaside.extended.yaml` | e9c7f87f71c06423 | 2c1f5c8ba18672c6 | changed |

- Also read: `audits/render_source/setaside_property_charges_and_repairs/render_r1.md`. It is renderer findings only and carries no scored values.

### charter_global_frozen (r3)
Frozen before any revision-3 GT was read. The charter changed, so every charter-global check was re-derived in full.

- **Mechanical re-run, all six policies, no issue:**
  - base section identical to the blueprint
  - every compute binding has a `compute_basis` value, verbatim in its rule
  - every `baseline.rule` sentence is in its rule
  - every baseline param is declared
  - every edge `policy_source` is verbatim in the blocked rule, with `fallback_reason` exactly on action-form edges
  - every `replaced_by` is verbatim in its rule
  - no duplicated rule sentence
- **What changed:**
  - P5 and P6 rule and compute are byte-identical to r2 (sha prefixes bb5c648f699c/28d938dc4110 and f0d85f1ef46e/6a5618f9d8f5).
  - P2's compute is identical; one rule sentence changed (render_r1 "lesser observation"): "The credit references the reserve's payment of the overpaid installment, and where more than one paid installment of the tax year is overpaid, the reserve's payment of the paid property tax bill with the latest due date; it is dated the handling date." It is now unique when several installments are overpaid. Closed.
  - P1, P3 and P4 were restructured (below).

**render_r1 class ("assembles several factor quantities"), item by item:**

| render_r1 item | status (r3) | evidence |
|---|---|---|
| Tax assembly sentences absent from `baseline.rule` | CLOSED | `baseline.rule` now carries the tax year's tax (sum of paid+received), "The next tax year's tax is the tax year's tax increased by the assessment allowance percentage and then increased by the exemption allowance amount; the assessment allowance is the standard increase percentage and the exemption allowance is zero.", the next-year share (whole months from the latest-due paid bill / 12, clamped 0–1), and "The projected annual property tax is the tax year's tax times one less the next-year share, plus the next tax year's tax times the next-year share." Each is stated once and is generic. |
| Hazard / flood assembly absent from baseline | CLOSED | `baseline.rule` carries the current premium (latest-due paid bill), the renewal premium with "the standard renewal increase plus" the three loadings (each zero at baseline), the hazard fee zero (hazard only), the renewal share "one half", and the blend sentence. Each is stated once. New constants: `standard_renewal_increase_pct` 4.0 and `default_renewal_share` 0.5, both in baseline.params. |
| Factors acting only through another factor's zero share | CLOSED | Every baseline share is now non-zero by construction: month basis (tax), one half (hazard, flood). Independence probe (each factor alone at gold, all others at baseline; it must differ from the all-baseline figure): task 0 P1 10,822.81 / 11,565.44 / 11,533.50 / 11,622.98 vs 11,527.08; task 1 P3 all six ≠ 2,876.40; task 1 P4 all five ≠ 1,473.90. Every projection factor now moves a baseline-defined quantity on its own. |
| Tax rule self-contradiction ("is the tax year's tax, which is the sum…" vs "blends") | CLOSED | The sentence "The projected annual property tax is the tax year's tax …" is gone. The projected tax is defined once (the blend). "The tax year's tax is the sum …" is the baseline, and tu_basis tiers replace it ("Where …, the tax year's tax is …"; fall-through "Otherwise … the sum"). This is the standard baseline-then-ladder form, used by every quantity in the charter. |
| P2 overpaid-installment reference | CLOSED | See above. |

**rule_compute_equivalence (r3), new or changed bindings:**
- P1: `span_paid_due` = latest-due paid bill ✓. `span_share` tiers: installment count / annual block / month basis ✓. Annual block = `DAYS(last received bill's due, NOW) >= 0` ↔ "one when the due date of the most recently received property tax bill is on or before the review date" ✓. `assess_pct` = restoration / 0 when the value is falling / standard ✓.
- P3/P4: `share` fall-through `K('default_renewal_share')` ✓. `renewal_prem` includes `K('standard_renewal_increase_pct')` ✓.
- No compute branch lacks a rule tier, and no tier lacks a branch.

**factor_ladders (r3):**
- P1 still has 4 factors (2P/2M); P3 has 6 (4P/2M); P4 has 5 (3P/2M).
- New ladders:
  - tu_assess = restoration 6% / zero (value already falling) / standard 2%.
  - tu_span = installment count / annual block (1 or 0) / month basis.
  - hu_span and fu_span = replacement month / installment count / one half.
- Tiers are distinct. Every fall-through equals its factor `baseline`, which equals what `baseline.rule` states.
- Labels are honest: tu_span tiers are three different share algorithms.
- Realism:
  - A 2% standard tax increase and a 4% renewal trend are ordinary escrow-analysis assumptions.
  - "No increase when the assessed value is already falling" and "a once-a-year bill already due puts the whole next-year bill inside the coming twelve months" (annual block) are sound. The annual block also answers O-7 for annual-bill jurisdictions in tier 2.
  - A one-half renewal share for an unknown renewal date is a neutral midpoint assumption.
- **Prerequisite graph and sentences:** unchanged from r2. All edges and sentences are verbatim, the graph is acyclic, and O-4 stays closed.
- **Override declarations:** unchanged. The three overwrites still quote base S3 clauses and are scoped to Summit reserves.

### findings (r3, charter-global)
- No charter-global RED.
- **New observation O-R3-1:** projections are no longer fixed points on off-tree figures.
  - Under r2, the off-tree projections on each world gave exactly the on-file figure (task 0: hazard 2,866.00, flood 0.00; task 1: tax 7,594.00). The r3 baselines add a time-driven drift (standard increase × non-zero share), so they no longer do:
    - task 0 hazard → 2,994.97 (on file 2,866.00)
    - task 1 tax → 7,745.88 (on file 7,594.00)
  - Gold stays uniquely entailed, for two reasons:
    1. Neither tree's root states a sentence waiting on those reviews.
    2. The charter's own staleness test ("reviewed against every … bill received since it was last set") is met for both figures: no hazard bill since 2025-07-21 in task 0, and no tax bill since 2025-10-20 in task 1.
  - An agent that reviews an unrequested, untriggered charge would change the root:
    - task 0: P2 → 699.36
    - task 1: P5/P6 → 2,808.00 / 1,415.89
  - I recorded this as an observation, because the reading needs a review that no rule or bill triggers. It is listed so later rounds keep the trigger-based staleness criterion intact.
- Carried observations: O-1, O-2, O-3, O-5, O-6, O-8.
- O-7 is softened: the annual-block tier handles one-bill-a-year jurisdictions. `installments_per_year` 2 remains in tiers 1 and 3.

### closing_checklist (r3)
Written after the r3 reveals (2026-10-15T15:37Z). The charter-global r3 part above was frozen before them.
- Per-task files carry revision_3. Older revisions are untouched.
- Results: task 0 PASS; task 1 PASS. Both GTs match the blind r3 derivation figure for figure.
- render_r1 items:
  - The three assembly / baseline gaps are closed.
  - Factor-only-through-share is closed (independence probes pass on both worlds).
  - The tax self-contradiction is closed.
  - The P2 reference ambiguity is closed.
- Prior closures still hold: F-T1-1 and O-4.
- No new RED and no regression in scores, trees, factors or bindings. New observation O-R3-1 (off-tree projection drift; gold still unique by the charter's trigger-based staleness test).
- Scope:
  - task 0 = {P1, P2}; task 1 = {P3, P4, P5, P6}. Disjoint, and together they cover all six policies.
  - uuid8s unchanged.
  - The graph is acyclic.
  - Trees: n = 1 with 1 value_input edge; n = 3 with 5 value_input edges. User-owned writes are present in both.
- Factors:
  - All computations have 4–6 factors (≥2P / ≥1M).
  - Multi-source and cross-difficulty factors are present per task.
  - Every factor bears weight against an honest, baseline-defined quantity.
  - Fall-backs ≠ gold: 11,527.08 / 703.10 / 2,876.40 / 1,473.90 / 3,150.35 / 1,457.53.
- Gates on the final form (snapshot_r3): all OK including TRACEABILITY. validate INVALID only from other difficulties' unrendered documents (0 errors here).
- Open observations: O-1, O-2, O-3, O-5, O-6, O-7 (softened), O-8, O-T0-1, O-T1-1, O-T1-2, O-T1-3, O-T1-4, O-R3-1.

VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN
