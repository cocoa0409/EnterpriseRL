# Policy-task audit — contents_packout_and_storage / charter-global

## revision_1

## charter_global_frozen
- freeze: 2026-10-23 21:25 UTC; auditor: independent policy auditor (erl-task-policy-audit).
- `tasks/contents_packout_and_storage/contents.extended.yaml` sha256=23d633e2ca6e78548c01b45db08238ec9de3085fbc20bb66b6bd91ed6a1315c0; `task_tools.py` sha256=506c4e03d5c501124b6e8efff1250b8bad27403001a2a89f099ae2fae3778d35 (both match `.audit_views/policy/contents_packout_and_storage/snapshot_r1.txt`).
- Built from the charter, blueprint (blueprint.yaml, products/*.yaml, db_schema.json, share_tools.py), the tool module, XF_recipe.md and identifier_bands.md only. No task JSON, worklog.md or plan.md read; nothing here derives from a revealed GT.
- Entry conditions (Step 0): snapshot_r1.txt carries the 7 instantiation gates, all green (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK); check_traceability deferred by the coordinator; masked-view hashes 0.json abb70fea…ca39, 1.json d9049312…f3ca recomputed and equal.
- Base copy: the 10 base keys of the extended file are value-identical to `blueprint/products/contents.yaml` (YAML-parsed comparison; differences are line-folding only).
- Policy short names used below: VP = contents_ext_customer_vault_period, VC = contents_ext_customer_valuation_period, SP = contents_ext_customer_share_payment, PB = contents_ext_pack_back_box_line, FR = contents_ext_furniture_reset_line, TL = contents_ext_return_truck_loads, CP = contents_ext_closing_payment.

### policy_conflict_scan
| subject | base policy | extended | conclusion |
|---|---|---|---|
| contents_storage_charge (vault, customer-billed, Partial/Full) | contents_evt_storage, contents_signing_and_custody, contents_return | VP | three declared overwrites; out-of-scope lines restated; compatible except CG-C2 gap |
| contents_storage_charge (valuation, Partial/Full with declared value and box count) | contents_evt_storage, contents_return | VC | two declared overwrites; CG-C2 gap |
| contents_pack_back_charge pack_back_box / furniture_reset | contents_return | PB, FR | declared sibling overwrites naming each other and TL; compatible |
| contents_pack_back_charge truck_trip (return loads) | contents_return **and contents_evt_packout_and_cleaning** | TL | overwrite names only contents_return; departure from contents_evt_packout_and_cleaning undeclared → CG-C1-TL |
| contents_customer_payment (insurance-funded Partial/Full, in_custody/return_scheduled) | contents_evt_customer_payment | SP | amount fixed, posted in full, surcharge under base — compatible; but the base storage referral sentence is not addressed → CG-REF |
| contents_customer_payment (insurance-funded Partial/Full/HV/Commercial, returned/invoiced) | contents_evt_customer_payment | CP | same; CG-REF |
| SP vs CP | — | — | disjoint by status set; each names the other in its scope sentence |
| VP vs VC | — | — | different charge codes and tools; VP's secured-section read of coverage-line quantity is the job's declared value, which a new VC line does not change once any coverage line exists (in a world with no coverage line yet, a VC write before VP would move VP's secured add — no edge orders them; not engaged in either task world) |
| cross-category reads | — | VP/VC water_category, policy_state; SP/CP claims arrangement params, payments, approvals, requests; PB/FR/TL rebuild property_type/status/substantial_completion_date, fire smoke_severity | read-only; rebuild reads keyed by loss_address first-match → CG-B2-REBUILD |
Task scopes: task 0 claims {SP, VP, VC}; task 1 claims {CP, PB, FR, TL} (derived from the trees walked in 0.md/1.md and the `prerequisite` graph) — pairwise disjoint and jointly covering all 7 extended policies.

### rule_compute_equivalence
Mechanical sweep: every `compute_basis` quote of all 7 policies is verbatim in its rule (0 misses); every `baseline.rule` is a rule sentence; every overwrite `superseded_clause` is verbatim in its base rule and every `replaced_by` is verbatim in the extended rule; every `policy_source` is verbatim in its own rule. Every factor ladder tier is stated in the rule and is a branch of its `decides` binding (read tier by tier for all 41 factors); no rule tier lives only in compute.
Sentence-level departures (rule ≠ compute in some producible world, or rule silent where compute decides):
- SP and CP `requested_end = XLATEST(... claims_storage_extension_request, related_job_id=HID)` reads only the latest request by request_date, while the rule says "no storage extension request for this job asking for a later end date is recorded": with an earlier request asking a later date and a later request asking the same/earlier date, the rule takes the request tier (or "nothing is added"), compute takes the approved-end tier; same-day requests have no tie rule → CG-B2-REQ.
- PB, FR, TL read "the company's rebuild contract at the job's loss address" through `CFIELD('rebuild', …, loss_address=…)` (first match); the rule never says which contract when the customer holds two at the address (a declined proposal is cancelled, rebuild charter lifecycle) → CG-B2-REBUILD.
- VP/VC share "the days from the period's first day to the scheduled return date" — compute uses the exclusive difference; the rule states no inclusivity → CG-B4.
- VC `value_covered` divides by `boxes_packed`; a recorded 0 raises in compute, the rule's scope says only "whose boxes packed are recorded" (observation O-1).
- PB/FR floor protection/runners: a substantial completion recorded after the returned date (negative lead) falls in no rule tier; compute gives 0 (observation O-2; not producible while base contents_return requires the rebuild to be substantially complete before scheduling the return on these tiers).
- Rounding: every result is `RND(x + 1e-9, 2)` on a non-negative value, matching "rounded once to the cent, half up" (residue DSL-KNOWN).

### action_binding_and_uuids
- (target_tool, computes): VP charge_customer_vault_storage_2f9c3128/amount; VC charge_declared_value_coverage_b3c8ef16/amount; SP pay_contents_customer_share_24e82212/amount; PB charge_pack_back_boxes_26b5c86b/amount; FR charge_furniture_reset_9904d302/amount; TL charge_return_truck_loads_2b0047ce/amount; CP pay_contents_closing_balance_f918d993/amount — each claimed by exactly one policy.
- Tool bodies: each validates only date format / tender enum / positive amount, performs ctx.create + ctx.update in its own body, rounds through the Decimal half-up static helper; no status, period or prerequisite judgement; no forbidden tokens (D5 sweep clean); no example values in docstrings (D1); no composed arguments (D3); docstrings carry no ordering word about other actions ("first day" and "after the line" describe the tool's own fields).
- D8 gap: SP and CP both say "a credit card payment carries its surcharge as its own line under the base payment rule", and the pay tools say "A credit card payment's surcharge is not part of this payment", but no task or share tool books a contents_card_surcharge line → CG-D8.
- uuid8s 2f9c3128, b3c8ef16, 24e82212, 26b5c86b, 9904d302, 2b0047ce, f918d993: all distinct, no shared prefix beyond one hex digit, no sequence; four of seven begin with "2" (observation O-3, not a demonstrated batch derivation).

### prerequisite_graph
- `prerequisite` filled on all 7 (VP, VC, PB, FR, TL `[]`). Edges: VP→SP, VC→SP (value_input, gate customer_lines); PB→CP, FR→CP, TL→CP (value_input, gate excess_share). Every `problem` is an extended policy id of this file; no self-edge; acyclic (two stars).
- form `state` on all 5 edges; no `fallback_reason` (correct, none is action form).
- `resolved_by` equals the depended-on policy's target_tool on all 5; `gate` bindings `customer_lines` (SP) and `excess_share` (CP) exist in the blocked compute.
- `condition` vs sentence: SP/VP "Every storage period … whose first day is on or before today and after the approved storage end date … has a vault_storage line billed to customer" = sentence + SP's own definition "A storage period falls to the customer when its first day falls after the approved storage end date" (equal strength). SP/VC condition says "declared value above zero"; the sentence says "a job carrying a declared value", and base contents_signing_and_custody says a decliner "declares 0.00" (observation O-4: the sentence is literally broader than the condition on a 0.00 job; VC's scope excludes such jobs so no resolver exists there). CP conditions "dated its returned date" match "owed for its return".
- `effect` texts: CP edges claim weight "with the supplement window passed" — true only when CP's excess tier is engaged and insurer-side charges exceed the approved scope; elsewhere the edge carries no weight through `excess_share` (it can still move `proceeds_share` T1 on a denied/withdrawn file). Per-world weight is shown in each task file.
- No authoring-viewpoint wording in any `prerequisite` field.

### prerequisite_sentences
| edge | sentence (own rule) | connective | waited-on state | single resolving write | derivation |
|---|---|---|---|---|---|
| VP→SP | "The customer's share is fixed only after every storage period of the job that falls to the customer and has begun carries its vault storage line." | only after | vault storage line on each begun customer period (charge rows) | VP's tool (only write booking vault_storage billed to customer) | sentence + charge rows show the missing period; VP's rule "prices the vault storage line of a storage period billed to the customer" names the write |
| VC→SP | "Before the customer's share is figured, every storage period that has begun on a job carrying a declared value must carry its declared-value coverage line." | before | coverage line on each begun period | VC's tool | sentence + rows + VC's rule |
| PB→CP | "The closing payment is not figured until the job carries the pack-back box line owed for its return." | not until | pack-back box line | PB's tool | ditto |
| FR→CP | "The closing payment is not taken until the furniture reset line owed for the return stands on the job." | not until | furniture reset line | FR's tool | ditto |
| TL→CP | "The closing payment is fixed only after the truck loads that brought the contents home stand on the job as a move-back line." | only after | move-back truck line | TL's tool (the packout truck_trip lines are contents_packout_charge, a different line) | ditto |
Four-point test passes on all five (no tool name, policy id, snake_case token or row id; state form). No second wording of any dependency elsewhere in the blocked rules; the depended-on rules (VP, VC, PB, FR, TL) do not restate the sentences; no rule states a cross-problem order that grounds no edge (checked all 7 rules; PB/FR/TL "charged once the job is in returned status" waits on a system transition, not a problem). No base sentence grounds an edge.
E7 (satisfiable in every engaged world): VP and VC price only "the storage period … that contains the day the line is charged"; SP's sentences demand a line on **every** begun customer period. In a producible world where an earlier customer period (or coverage period) also lacks its line, no extended rule prices that line, and the base storage rule's own first-day billing has been retired for such lines by VP's/VC's overwrites, so the wait cannot be satisfied → CG-E7. Not engaged in task 0 (P5 lines seeded).

### override_declarations
Sentence-by-sentence over every `base_policy_refs` entry (finding half only; consequences in task files):
- VP × contents_evt_storage: status sentence followed; period/first-day/vault-rate×count clause → declared; climate/oversized sentence untouched (out of scope); bill_to sentences followed (scope restates them); due-days/referral sentence untouched and not addressed (see CG-REF via SP/CP); declared-value sentence → VC. VP × contents_signing_and_custody: "vault count in force on the first day" → declared; vault-count-at-custody sentence followed. VP × contents_return: "storage stops accruing…" → declared (replaced_by gap CG-C2). VP × contents_evt_packout_and_cleaning: crate line rates followed (read only).
- VC × contents_evt_storage: valuation sentence → declared (replaced_by scope gap CG-C2). VC × contents_return: declared. VC × signing/packout: followed.
- SP × contents_evt_customer_payment: "posted in full to the one job they name", surcharge, refund sentences followed; SP × contents_evt_storage: bill_to followed; referral sentence not addressed (CG-REF); SP × contents_evt_insurance_payment: "customer-billed storage … never paid from insurance proceeds" followed (SP posts no insurance proceeds); SP × one_job_per_address: followed. The storage-tail charge is consistent with claims_storage_coverage ("storage after the approved end date is billed to the customer under the contents storage rules"), so not an undeclared override.
- PB, FR × contents_return: "Pack-back is billed per box and per furniture item reset at the tier's rates…" → declared by each, sibling cases named. FR × contents_evt_storage: oversized storage lines read only.
- TL × contents_return: declared overwrite of the pack-back sentence, which governs boxes and furniture, not trucks (retires nothing for TL's line). TL × contents_evt_packout_and_cleaning: "Truck trips are billed per load …" and "Amounts are quantity times unit rate, rounded to the cent, half up." — TL prices a truck_trip line as loads × (fee × air-ride % × state factor + per-load adds) + oversized move: **undeclared** → CG-C1-TL. TL × contents_signing_and_custody: vault capacity read, followed.
- CP × payment/storage/insurance/custody/adjustment/one-job: followed, referral not addressed (CG-REF).
- Disguised forms checked: no 0/1 multiplier on a base-fixed amount; no dropped base branch except as named; no anonymous intermediate overriding a base quantity beyond those declared.

### factor_ladders
Structure only (weight per world lives in 0.md / 1.md). Every ladder has three disjoint tiers with a defined fall-through equal to its baseline, every tier is in the rule and in the `decides` binding, every value is a charter param. Columns: label | tiers (T1/T2/T3) | XF A7 / label test | realism (E1) | survives.

VP (declared 6: 4 parameter, 2 method; cross-difficulty water, claims)
| factor | label | tiers | test | realism | survives |
|---|---|---|---|---|---|
| vaults_billed_count | method | ceil((B−S)/cap)≥1 / ceil(B/cap) / recorded V | T1 vs T2 adds input S + floor; T2 vs T3 different source (box_count vs vault_count); T1 vs T3 different | disposal right-sizing real; T2 bills fewer vaults than recorded in use (O-5) | yes |
| contaminated_lining | parameter | 12% / 6% / 0 | K values | IICRC category → lined vaults, company schedule | yes |
| facility_schedule | parameter | 1.15 / 1.08 / 1 | K | company facility schedule by state | yes |
| secured_section | parameter | 22 / 12 / 0 | K | yes | yes |
| crate_racking | parameter | n×14 / n×18.5 / 0 | same shape, rate differs | yes | yes |
| return_period_share | method | d/30 / 15/30 / 1 | **T2 vs T3 FAIL** (both constant multipliers of the same full-period amount) | prorated last period with a half-period minimum is real | no (CG-A7) |
Surviving 5 (4 parameter, 1 method) — meets the floor.

VC (declared 6: 4 parameter, 2 method; water, claims)
| covered_value_basis | method | DV(B−S_signed)/B / DV(B−S_pending)/B / DV | **T1 vs T2 FAIL** (same field item_count, filter only) | **T2 unreal** (CG-VC-REAL) | no |
| contaminated_coverage_loading | parameter | 0.20 / 0.10 / 0 | K | yes | yes |
| crated_items_rider | parameter | 0.08 / 0.05 / 0 | K | yes | yes |
| electronics_items_rider | parameter | 0.06 / 0.03 / 0 | K | yes | yes |
| coverage_facility_schedule | parameter | 1.12 / 1.06 / 1 | K | yes | yes |
| coverage_return_share | method | d/30 / 15/30 / 1 | **T2 vs T3 FAIL** | yes | no |
Surviving 4 parameter, **0 method** → CG-COUNT.

SP (declared 4: 2 parameter, 2 method; claims ×3)
| counted_payments_basis | method | P−R−S / P−S / P | **T1 vs T2 FAIL** (R and P are both contents_payments.amount); **T3 collapse** (S is 0 on T3's whole domain; the ladder equals P−R−S in every world) | — | no |
| insured_proceeds_pass_on | parameter | insurer-side balance / MN(insured-only, balance) / 0 | **label dishonest**: tiers select different computations (adds MN and an input), not a number → CG-LABEL | real pass-on practice; overlaps CG-SP-OVERLAP | no |
| declined_lines_share | parameter | MX(0,W−Sup) / W / 0 | **label dishonest** (adds an input and floor) | real (claims_evt_writeoff) | no |
| uncovered_storage_days | method | line×days-after-requested/30 / line×days-after-approved/30 / 0 | data-selected window (different date field) → pass | real (claims_storage_coverage) | yes |
Surviving **1** factor (0 parameter) → CG-COUNT.

PB (declared 6: 5 parameter, 1 method; rebuild ×2, fire)
| boxes_brought_back | method | B−S_signed / B−S_pending / B | **T1 vs T2 FAIL** (same field) | real | no |
| unit_carry | parameter | 15% / 8% / 0 | K | real | yes |
| new_floor_protection | parameter | 1.40 / 0.70 / 0 per box | K | real | yes |
| wardrobe_hanging | parameter | n×4.25 / n×5.50 / 0 | rate | real | yes |
| high_value_condition_check | parameter | n×6.50 / n×8.75 / 0 | rate | real | yes |
| odor_barrier_bagging | parameter | 1.85 / 1.10 / 0 | K | real | yes |
Surviving 5 parameter, **0 method** → CG-COUNT.

FR (declared 6: 5 parameter, 1 method; rebuild ×2, fire)
| pieces_set_basis | method | F+crates / F+electronics / F | **T1 vs T2 FAIL** (both SUM(contents_charges.quantity) by code); **T3 collapse** into either | **unreal**: electronics dropped whenever a crate exists (CG-FR-REAL) | no |
| reset_unit_carry | parameter | 15% / 8% / 0 | K | real | yes |
| reset_floor_runners | parameter | 2.10 / 1.05 / 0 | K | real | yes |
| odor_film_unwrap | parameter | 4.50 / 2.75 / 0 | K | real | yes |
| oversized_set_crew | parameter | n×120 / 145 / 0 | rate | real | yes |
| second_reset_crew | parameter | 4.10 / 3.25 / 0 | K | real | yes |
Surviving 5 parameter, **0 method** → CG-COUNT.

TL (declared 6: 5 parameter, 1 method; claims, rebuild ×2)
| return_load_count | method | ceil((B−S)/cap)≥1 / ceil(B/cap) / recorded V | pass (as VP) | baseline "one load for each vault" (O-6) | yes |
| air_ride_truck | parameter | 12% / 8% / 0 | K | real | yes |
| state_trip_schedule | parameter | 1.10 / 1.05 / 1 | K | real | yes |
| rebuild_site_wait | parameter | 35 / 15 / 0 | K | final_invoiced tier vs the rule's own reason "crews are still finishing" (O-7) | yes |
| unit_delivery_access | parameter | 45 / 30 / 0 | K | real | yes |
| oversized_move_truck | parameter | n×140 / 165 / 0 | rate | real | yes |
Surviving 6 — meets the floor.

CP (declared 6: 3 parameter, 3 method; claims ×4)
| closing_charge_lines | parameter | L+S / S / 0 | **label dishonest** (tiers choose which sums join); as a method it fails A7 (same field contents_charges.amount; T3 collapse — the ladder equals L+S in every world) | — | no |
| approved_scope_excess | method | MX(0,I−A−Sup) / MX(0,I−A) / 0 | pass (adds requests input; T3 domain not zero for T2) | real; overlaps CG-CP-OVERLAP | yes |
| insured_proceeds_closing | parameter | MX(0, lines−postings) / MN(insured-only, MX(0,scope−postings)) / 0 | **label dishonest** | real; CG-A9 member | no |
| owed_compensation_netting | method | C+G / G / 0 | **T1 vs T2 FAIL** (both contents_payments.amount); T3 collapse | — | no |
| storage_beyond_approval | method | as SP uncovered (vault or climate) | pass | real | yes |
| declined_lines_closing | parameter | MX(0,W−Sup) / W / 0 | **label dishonest** | real | no |
Surviving 2 (0 parameter) → CG-COUNT.

Per task: task 0 tree (VP, VC, SP) and task 1 tree (PB, FR, TL, CP) each carry ≥1 multi-source factor (SP declined_lines_share; CP approved_scope_excess) and ≥1 cross-difficulty factor (water/claims; rebuild/fire/claims) — subject to the strikes above.

Factor-reads table (XF A1; transitive): every factor of every policy reads only its own bindings plus baseline/plain inputs (VP: vaults_billed ← box_count, vault_count, capacity; share ← period_days; SP/CP: each claims factor ← its own CFIELD/CPARAM/XSUM bindings; FR second_reset_crew ← its own duplicate furniture sum). No factor reads another factor's binding or output. Assembly lives in plain bindings (per_vault_rate, per_box_rate, per_piece_rate, per_load_rate, coverage_rate) and `result` → A1 pass; A2 fails on wording (CG-A2). A5 order stated in every per-unit-rate sentence. A10: no factor id is a substring of any task or share tool name.

### findings
Each finding: verdict — symptom — root cause — evidence — demonstrated consequence — artifact/location — tasks.

**CG-A7 SOURCE-FACTOR RED (XF A7, method shape).** Members: VP.return_period_share (T2 15/30 vs T3 1 — the same full-period amount times two constants); VC.coverage_return_share (same); VC.covered_value_basis (T1 vs T2 differ only in the authorization_status filter of SUM(item_count)); SP.counted_payments_basis (P−R−S vs P−S on the same contents_payments.amount field; the "otherwise" tier is the other formulas at zero, so the ladder is one formula P−R−S); PB.boxes_brought_back (signed vs pending filter); FR.pieces_set_basis (crate vs electronics_item filter on contents_charges.quantity; T3 collapse); CP.owed_compensation_netting (C+G vs G on contents_payments.amount; one formula C+G). Consequence: these factors are not method factors in the XF sense and do not count toward the floors (CG-COUNT). Location: `factors[]` and the matching rule sentences of VP, VC, SP, PB, FR, CP. Tasks 0, 1.

**CG-LABEL SOURCE-FACTOR RED (mislabelled effect).** Factors labelled `parameter` whose tiers select different computations rather than a number: SP.insured_proceeds_pass_on, SP.declined_lines_share, CP.closing_charge_lines, CP.insured_proceeds_closing, CP.declined_lines_closing. Evidence: ladder values `insurer_side_balance` vs `MN(insured_only_paid, insurer_side_balance)`; `MX(0, denied_writeoffs - supplement_requested)` vs `denied_writeoffs`; `late_fee_lines + surcharge_lines` vs `surcharge_lines`; etc. Tasks 0, 1.

**CG-COUNT SOURCE-FACTOR RED (floors after the tests).** Surviving factors: VC 4 parameter / 0 method; SP 1 factor / 0 parameter; PB 5 / 0 method; FR 5 / 0 method; CP 2 / 0 parameter. VP (5; 1 method) and TL (6; 1 method) meet the floor. Tasks 0 (VC, SP), 1 (PB, FR, CP).

**CG-VC-REAL SOURCE-FACTOR RED (unreal tier).** VC tier "when no signed disposal authorization lists an item and the job's disposal authorizations pending signature list at least one item, the value covered is the declared value times the boxes packed less the items those pending authorizations list" removes from declared-value coverage items that are still in the company's custody ("they stay inventoried until the owner signs", contents_evt_packout_and_cleaning) and still compensable (contents_evt_custody_credit: only "Items listed on a signed disposal authorization are never compensated"; with coverage "the cap is replaced by the item's share of the declared value"), while signed-but-unhauled items, which are never compensated, stay covered in full (T3). PB's own rule states pending items "stay in storage". Consequence: on any job with a pending authorization the customer is charged coverage on a smaller value than the company remains liable for — a treatment no contents program publishes. Not engaged in task 0's world (no pending authorization). Location: VC rule, `value_covered`, factor covered_value_basis.

**CG-FR-REAL SOURCE-FACTOR RED (unreal tier).** FR "when they carry no crate and at least one electronics item, the pieces set are the furniture items plus the electronics items, because electronics are placed and reconnected" — the stated reason holds equally when a crate exists, yet T1 (any crate) sets furniture + crates and drops every electronics item. Consequence on task 1 in 1.md (T1-5). Location: FR rule, `pieces_set`.

**CG-SP-OVERLAP SOURCE-POLICY RED (same amount charged twice).** On a Homeowner Direct Pay file SP T1 adds "the whole insurer-side balance", which already contains the insurance-billed vault line whose tail `uncovered_storage_days` adds again and every carrier-denied line that `declined_lines_share` adds again. Demonstration (task 0 world with the claim's arrangement set to Homeowner Direct Pay, a state the claims charter produces): proceeds 11125.00 + declined 245.00 + uncovered 72.50 → payment 12810.21 against a job balance of 12492.71 after the two lines — the payment exceeds the whole balance by exactly 245.00 + 72.50 and leaves a credit balance the base hands to a human. Location: SP rule (insured-proceeds, declined-lines and uncovered-storage sentences). Not engaged in task 0 (Direction to Pay).

**CG-CP-OVERLAP SOURCE-POLICY RED (storage tail on top of the full excess).** CP T2 of approved_scope_excess carries every insurer-side charge above the approved contents scope; storage_beyond_approval then adds the tail of the last insurance storage line although the carrier receivable (claims charter: scope less payments and write-offs) still counts that scope as payable. Consequence on task 1 in 1.md (T1-4: 107.50 over-collection). Location: CP rule.

**CG-C1-TL SOURCE-POLICY RED (undeclared override).** Base contents_evt_packout_and_cleaning: "Truck trips are billed per load and the inventory report once per job." … "Amounts are quantity times unit rate, rounded to the cent, half up." (and its status sentence for packout lines). TL books a truck_trip line priced loads × (fee × (1 + air-ride %) × state factor + site wait + access) + oversized move, in returned status. TL's only overwrite retires contents_return's pack-back sentence, which governs boxes and furniture, not truck lines. Consequence in 1.md (T1-1). Location: TL `overwrite`, rule.

**CG-A9 SOURCE-TASK RED (two-grouping arithmetic sentences).** Members: (a) VP "the line amount is the per-vault rate times the vaults billed, plus any per-crate racking charge, times the share of the period billed" ((V×n+R)×s vs V×n×s+R) — consequence in 0.md (T0-1); (b) CP "the lesser of those payments and the approved contents scope less the insurance postings" (MN(I, A−P) vs MN(I, A)−P) — consequence in 1.md (T1-2); (c) lower-weight members whose second reading is dimensionally incoherent: VC "the declared value times the boxes packed less the items listed …, divided by the boxes packed", VP/TL "the boxes packed less the items listed …, divided by the tier's vault capacity". Location: rule sentences quoted (and the identical `replaced_by` text of VP).

**CG-B4 SOURCE-TASK RED (day-count inclusivity).** VP and VC: "the share is the days from the period's first day to the scheduled return date divided by the tier's period length" — no inclusivity stated; compute counts exclusively. Consequence in 0.md (T0-2).

**CG-B2-REQ SOURCE-POLICY RED (latest-only request read).** SP and CP read the extension request through XLATEST; the rule speaks of any recorded request for a later date. Probe (task 0 world + request 2026-08-20 asking 2026-09-17 and request 2026-08-25 asking 2026-09-14): rule gives 435 × 2/30 = 29.00 → payment 3491.71; compute gives 72.50 → 3535.21. No same-day tie rule. Not engaged in either world (no requests seeded).

**CG-B2-REBUILD SOURCE-POLICY RED (first-match rebuild read, no selection rule).** Six read sites (PB property_type, substantial_completion_date; FR the same two; TL status, property_type) read "the company's rebuild contract at the job's loss address" by first match; a customer may hold a cancelled proposal and a live contract at one address (rebuild lifecycle proposed→cancelled). With the cancelled row first, TL's site wait is 0 instead of the live contract's tier and floor protection/runners are 0. Not engaged in task 1 (one contract).

**CG-E7 SOURCE-CHAIN RED (resolver cannot settle every engaged case).** SP's sentences require a line on every begun customer period; VP and VC price only the period containing the charge day; an earlier unbooked customer period has no pricing rule (base first-day billing retired by VP/VC overwrites for these lines). Not engaged in task 0.

**CG-REF SOURCE-TASK RED (base referral sentence unaddressed).** Base contents_evt_storage: "customer-billed storage left unpaid longer than the tier's referral days is referred to a human collections manager as not covered by policy" (blueprint summary: "customer storage long past due … handed to a human representative"). SP and CP fix a payment amount on jobs carrying long-unpaid customer storage without stating whether the referral applies first; both task worlds seed such storage. Consequences in 0.md (T0-3, anchor-dependent) and 1.md (T1-3, any anchor). The base text also leaves the count's anchor (first day vs due date) open (O-8).

**CG-C2 SOURCE-POLICY RED (replaced_by scope gaps).** VP's contents_return replaced_by says "a declared-value coverage line follows its own share rule" for every coverage line, but VC's share rule covers only Partial/Full jobs with a declared value and recorded boxes (High-Value and Commercial coverage lines have no such rule); VC's contents_evt_storage replaced_by keeps the base clause only for "declared-value coverage on every other tier", leaving a Partial/Full coverage line VC does not price (boxes not recorded) under neither text. Not engaged in either task world.

**CG-A2 SOURCE-POLICY RED (assembly names factor quantities).** The combination sentences name factor-owned quantities: VP ("vaults billed", "per-crate racking charge", "share of the period billed"), VC ("value covered", "every loading and rider", "coverage facility factor", "share of the coverage period"), SP ("customer payments counted"), PB ("boxes brought back", "the per-item charges are the hanging and condition-check charges"), FR ("pieces set", "the per-item crew charge is the oversized set charge"), TL ("return loads", "oversized move charge"); the same text recurs in each `replaced_by`. CP's combination sentence is generic. Tasks 0, 1.

**CG-D8 SOURCE-POLICY RED (no tool for a write the rule requires).** SP/CP require a credit card payment's surcharge "as its own line under the base payment rule"; no task or share tool books contents_card_surcharge. Not engaged (both personas pay by debit/ACH).

Observations (no demonstrated consequence): O-1 VC zero-box division; O-2 negative completion lead; O-3 uuid leading digit; O-4 "carrying a declared value" vs 0.00; O-5 VP/TL T2 bills fewer vaults/loads than recorded when no disposal occurred (base: vaults "may later be added"); O-6 "one load for each vault" baseline; O-7 TL final_invoiced site-wait tier; O-8 referral anchor; a COUNT of disposal_haul lines also counts a haul line later credited in full ("stands").
E5 (owed-write class): no agent-available write (task tools, verify, transfer) is a write another charter calls owed at once that moves a scored read — pass. E9: no account-level rule binds contents pricing — pass.

## closing_checklist
Not reached in revision_1: neither task passes all four relationships (see 0.md and 1.md `## findings`). Recorded for the next round: per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; scopes {SP, VP, VC} and {CP, PB, FR, TL} are disjoint and cover all 7 extended policies; each tree has 2 or 3 prerequisite problems, all value_input, one owner=user root, acyclic graph; every declared factor bears weight on its task's world and every whole-baseline fall-back differs from gold (435.00, 204.00, 1336.25; 3484.80, 880.40, 645.00, 3260.00); GT values equal the auditor's frozen derivations on every scored argument. Gates were not re-run by the auditor (coordinator-owned).

VERDICT revision_1: task0=RED task1=RED charter=CG-A7,CG-LABEL,CG-COUNT,CG-VC-REAL,CG-FR-REAL,CG-SP-OVERLAP,CG-CP-OVERLAP,CG-C1-TL,CG-A9,CG-B4,CG-B2-REQ,CG-B2-REBUILD,CG-E7,CG-REF,CG-C2,CG-A2,CG-D8

## revision_2

## charter_global_frozen (revision_2)
- freeze: 2026-10-24 ~14:15 UTC, before any round-2 task JSON was opened (task 0 and task 1 revision_2 derivations frozen first). Auditor as in revision_1.
- Entry: worklog last line reads `REWORK round 2: gates 7/7 green`; /tmp/erl0079_coord/snapshot.sh contents_packout_and_storage 2 run by this auditor → `.audit_views/policy/contents_packout_and_storage/snapshot_r2.txt`: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; views 0.json 95899b2e…f365, 1.json bd130763…6915 (recomputed, equal).
- Hashes changed (contents.extended.yaml 23d633e2… → 022d9283…539d; task_tools.py 506c4e03… → ecfd1a37…e194) → every charter-global section re-derived in full. Base copy still value-identical to blueprint/products/contents.yaml.
- Contamination note for this round: see 0.md / 1.md revision_2 disclosures (one figure per task seen in the worklog before the freezes).

### mechanical sweep (revision_2)
compute_basis quotes 0 misses (7 policies); every baseline.rule, superseded_clause (in base) and replaced_by (in rule) verbatim; every policy_source verbatim in its own rule; no factor id inside any tool name; no forbidden token; uuid8s unchanged. Tools: both pay tools now take surcharge_amount and book the contents_card_surcharge line in the same body (rejects a non-zero surcharge on any other tender) → D8 closed.

### policy_conflict_scan / override_declarations (revision_2)
- VP, VC: overwrites as revision_1; replaced_by texts now name the sibling's priced lines and keep the base text for every line the rule does not price → CG-C2 closed.
- PB, FR: sibling overwrites of the pack-back sentence, naming each other and the truck line.
- TL: now declares "Truck trips are billed per load and the inventory report once per job." and "Amounts are quantity times unit rate, rounded to the cent, half up." with scoped replaced_by; the retire-nothing contents_return overwrite is gone. **Residual**: the same base policy's first sentence "The job must be in authorized, in_custody or return_scheduled status when a packout, cleaning or disposal line is charged." is not overwritten, while TL's own replaced_by ("every other packout, cleaning or disposal line amount …") classes the move-back truck line as one of those lines and TL charges it "once the job is in returned status" → CG-C1-TL remains open (one member).
- SP, CP: scope now excludes Homeowner Direct Pay and accounts with customer storage unpaid past the referral days (oldest-first allocation, counted from each period's first day) → CG-REF closed at the rule level; worlds checked in 0.md/1.md.
- **New — CP rebuild suspension storage**: "Storage while the owner's rebuild stood suspended for a past-due draw is the owner's delay, not the carrier's: the closing payment carries the job's most recent vault, climate vault and oversized item storage lines billed to insurance_claim … times the suspended days", counted only for suspensions on or before the approved storage end date. Those days lie in periods base contents_evt_storage bills to insurance_claim ("A storage period whose first day falls on or before the approved storage end date … is billed to insurance_claim"), and claims_storage_coverage says the carrier pays storage through the approved end date ("the end date is set or moved only when the carrier confirms it in writing"). No overwrite is declared and no claims sentence lets the company shift carrier-approved days to the insured → CG2-SUSP. Also its second tier ("such a suspension date and no resumption date") cannot hold for any job in CP's scope: every CP tier requires the rebuild to be substantially_complete/final_invoiced/closed before the return (contents_return), which a suspended, never-resumed contract cannot reach (rebuild_overdue_draws: work resumes when the draw is paid).

### rule_compute_equivalence (revision_2)
- VP/VC fraction: "counted from the period's first day through the scheduled return date with both of those days counted" = `return_offset % period_days + 1` → CG-B4 closed.
- SP/CP extension request: "the one for this job that asks for the latest end date" = XLATEST ordered by requested_storage_end_date → CG-B2-REQ closed (probe: two requests → rule and compute agree).
- PB/FR/TL/CP rebuild reads: status-priority chain closed → final_invoiced → … → proposed, cancelled excluded = the stated "furthest along" rule → CG-B2-REBUILD closed. Residual tie: two contracts in the same status at one address (e.g. two closed contracts from separate losses — rebuild_agg_one_contract_per_address bars only two open ones) → first match, no tie sentence (CG2-B3).
- SP/CP awaiting contents_added request: `XLATEST(... 'claim_request_id', date_field='request_date')` — two such requests on one date have no tie sentence (CG2-B3).
- SP/CP floor: the rule defines the standard share/closing payment "never below zero" and then adds the carried amounts "to the standard … before its rounding"; compute floors only the final total. With customer payments above the customer lines (a payment is "posted in full as tendered"), the rule floors the standard part at 0 before adding, compute nets the credit against the carried amounts → CG2-B1-FLOOR.
- VC: zero-box guard and "above zero" scope stated (O-1, O-4 closed). PB/FR negative completion lead stated (O-2 closed).
- A9 sweep: every former two-grouping sentence now fixes its order ("taking …, dividing that difference …"; "the lesser of two amounts, the first being … the second being …") → CG-A9 closed.

### prerequisite_graph / prerequisite_sentences (revision_2)
Edges unchanged in shape (VP→SP, VC→SP on customer_lines; PB, FR, TL→CP on excess_share), all state form, resolvers = target tools, acyclic. SP's sentences now wait on "the storage period running today", which is exactly what VP and VC price → CG-E7 closed. Four-point test passes on all five; one resolving write each; no second wording; docstrings silent on sequence.

### factor_ladders (revision_2)
All-pairs method table (XF A7):
| policy.factor | T1 | T2 | T3 | pairs |
|---|---|---|---|---|
| VP.vaults_billed_count | ceil((B−S)/cap)≥1 | ceil(B/cap) | recorded V | pass (input S + floor; different source) |
| VC.electronics_coverage_schedule | DV × 0.06/100 | n_elec × 1.75 | none | pass (different input: declared value vs item count; T3's partner tiers are non-zero on their own domains) |
| SP/CP overrun | MX(0, W−A−R_await) | MX(0, W−A) | none | pass (adds request input) |
| SP/CP insured proceeds | MX(0, lines−postings) | MN(I, MX(0, A−WO−postings)) | none | pass |
| PB.high_value_condition_check | n × 0.25 h × tech hourly rate | n × 8.75 | none | pass by the A7 letter (tier tariff parameter contents_tech_hourly_rate); observation O-r2-2 |
| FR.second_reset_crew | n × 0.2 h × tech hourly rate | n × 3.25 | none | pass by the A7 letter; O-r2-2 |
| TL.return_load_count | as VP | | | pass |
| CP.owed_compensation_netting | C + G | MN(G, goodwill cap) | none | **FAIL**: base contents_evt_adjustment ("Goodwill credits on one job may not exceed the tier's goodwill credit cap in total") makes MN(G, cap) = G in every producible world, so T1/T2 are sums of the same contents_payments.amount field |
Parameter-labelled factors: every tier selects a number (K value, a count of days, a fraction, an amount from records substituted into one formula) → CG-LABEL closed.
Realism re-check (E1): VP/VC unchanged ladders real; VC furniture rider and value-rated vs scheduled electronics are company schedules; PB heavy-box, FR uncrating per crate real; TL site-wait tiers now carry their reasons (O-7 closed); **CP rebuild_suspension_storage unreal as stated (CG2-SUSP)**. O-r2-2: the hourly tiers of PB's condition check and FR's second crew price above the standard tier per unit (17.10 vs 8.75 per item; 13.68 vs 3.25 per piece) while every other volume tier of this charter is a discount — not a demonstrated defect.
Counts after strikes: VP 5p/1m, VC 5p/1m, SP 2p/2m, PB 5p/1m, FR 5p/1m, TL 5p/1m, CP 2p/2m (netting and suspension struck) → CG-COUNT closed. Factor-reads table: no factor reads another factor's binding (A1 pass).
A2 (assembly wording): the combination sentences are now ordered and mostly generic, but five still name factor-owned quantities: VP "any per-crate amount is added", VC "any electronics coverage is added to that product", PB "every amount figured on wardrobe boxes, high-value items or large boxes is added", FR "every crew, oversized or crate amount is added", TL "any oversized amount is added". SP and CP are generic.

### findings (revision_2)
Status of every revision_1 RED:
| id | status | evidence |
|---|---|---|
| CG-A7 | **open, 1 member** | CP.owed_compensation_netting (no-op cap); all other former members removed or rebuilt and pass |
| CG-LABEL | closed | all parameter tiers select numbers; proceeds/overrun labelled method |
| CG-COUNT | closed | counts above |
| CG-VC-REAL | closed | pending tier removed; signed items leave coverage |
| CG-FR-REAL | closed | pieces = furniture; crates priced by their own uncrating factor |
| CG-SP-OVERLAP | closed | HDP out of scope; overrun on non-storage work; task worlds end with balance = carrier receivable + carrier storage |
| CG-CP-OVERLAP | closed for the tail; see CG2-SUSP for the new storage shift | task 1 terminal check |
| CG-C1-TL | **open, 1 member** | base status sentence not overwritten (above) |
| CG-A9 | closed | ordered sentences |
| CG-B4 | closed | both days counted |
| CG-B2-REQ | closed | latest end date read |
| CG-B2-REBUILD | closed | status priority; residual same-status tie → CG2-B3 |
| CG-E7 | closed | running-period sentences |
| CG-REF | closed (rule); worlds pass under the storage-only reading (O-r2-1) | 0.md / 1.md |
| CG-C2 | closed | replaced_by texts |
| CG-A2 | **open, 5 members** | listed above |
| CG-D8 | closed | surcharge booked by the pay tools |
New in revision_2:
- **CG2-SUSP SOURCE-POLICY RED** — CP shifts carrier-approved, insurance-billed storage days to the customer for a rebuild suspension, without an overwrite of the base bill_to sentence and against claims_storage_coverage; its no-resumption tier is unreachable in CP's scope. Consequence in 1.md (T1-r2-2).
- **CG2-B1-FLOOR SOURCE-POLICY RED** — SP and CP: the "never below zero" standard amount vs the compute's single final floor differ whenever customer payments exceed the customer lines. Probe (task 0 world + an extra 2000.00 customer payment): rule 0 + 2717.50 = 2717.50, compute 1869.69. Not engaged in either task world.
- **CG2-B3 SOURCE-POLICY RED** — no tie sentence for (a) two contents_added requests on one request_date (SP, CP), (b) two rebuild contracts in the same status at one address (PB property_type and completion date, FR the same two, TL status and property type, CP suspension and resumption dates). Not engaged.
Observations: O-r2-1 surcharge-inclusive reading of "customer lines"; O-r2-2 hourly tiers dearer than standard tiers; O-3, O-5, O-6 carried; heavy-box charge counts large boxes packed, including any later listed for disposal.
E5: no agent-available write moves a scored read (pass). E9: pass.

## closing_checklist (revision_2)
Not reached: task 1 RED; task 0 RED only on the disputed XF E3 residue. Gates re-run on the final form by the coordinator script (snapshot_r2.txt, 7/7 OK). GT equals the auditor's frozen revision_2 derivations on every scored argument in both tasks.

VERDICT revision_2: task0=RED task1=RED charter=CG-A7,CG-C1-TL,CG-A2,CG2-SUSP,CG2-B1-FLOOR,CG2-B3

## revision_3

## charter_global_frozen (revision_3)
- freeze: 2026-10-24 ~18:50 UTC, before the round-3 task JSONs were opened. Worklog last line `REWORK round 3: gates 7/7 green`; /tmp/erl0079_coord/snapshot.sh contents_packout_and_storage 3 run by this auditor → snapshot_r3.txt: 7/7 gates OK; views 0.json 95899b2e…f365 (unchanged), 1.json 09d89478…5da1.
- contents.extended.yaml changed (022d9283… → 2937d2ed…cdb9e) → charter sections re-derived; task_tools.py unchanged (ecfd1a37…e194) → the revision_2 tool conclusions (D1–D8 pass, surcharge booked by the pay tools) carry forward on that hash.
- Coordinator ruling applied: other-category rows no gold step reads are accepted residue; scored cross-category reads checked for producibility and justifying rows in 0.md / 1.md revision_3 (all pass).

### sweep (revision_3)
Base copy value-identical; compute_basis, baseline, superseded_clause and replaced_by verbatim (0 misses); policy_source verbatim; no factor id inside a tool name. Factor labels: VP 5p/1m, VC 5p/1m, SP 2p/2m, PB 5p/1m, FR 5p/1m, TL 5p/1m, CP 3p/3m.

### status of the revision_2 REDs
| id | status | evidence |
|---|---|---|
| CG-A7 (CP netting) | closed | T1 C+G vs T2 MN(G, own charges) — T2 adds the contents_charges input and a lesser-of pick that binds on producible worlds (goodwill ≤ tier cap on a job whose customer-billed storage, surcharges and late fees total less, e.g. all storage carrier-billed); T3 nothing |
| CG-C1-TL | closed | third TL overwrite supersedes "The job must be in authorized, in_custody or return_scheduled status when a packout, cleaning or disposal line is charged." for the move-back truck line only; the amount replaced_by now reads "every packout, cleaning or disposal line amount is still …", so the truck line is no longer classed among them |
| CG-A2 | closed | combination sentences: "any amount figured per item" (VP, TL), "any amount figured per item or on the declared value" (VC), "every amount figured per item" (PB), "every amount figured per item or per crew" (FR); SP/CP generic |
| CG2-SUSP | closed | suspension sentences, bindings and rebuild read removed from CP; task 1 rebuild row carries no suspension dates |
| CG2-B1-FLOOR | closed | SP/CP: carried amounts added "before its rounding and before its floor at zero" = single final MX(0, …) |
| CG2-B3 | closed | (a) contents_added request = highest supplement_number (XMAX, then XLATEST filtered on it; supplement_number is a file-wide sequence per db_schema); (b) rebuild reads filtered to the job's claim file and address, plus the status order, with the stated one-contract-per-claim-file-and-address practice |

### new-defect scan (revision_3)
- CP prompt_payment_discount (new parameter): tiers 2% (≤ 10 days after the returned date) / 1% (≤ 30) / 0, on "the lines billed to customer less the customer payments posted to the job, never below zero". Ladder disjoint, values charter params, label honest, T1/T2 moving tests pass. But the rule creates a reduction of what the customer owes that no write records: no task or share tool books a discount, contents_payments.adjustment_reason admits only billing_error, duplicate_line and goodwill, and the account definition ("charges and refunds raise it, customer payments, insurance postings and credits lower it") gives a discount no way to lower the balance. The discounted amount therefore stays due on the job after the closing payment and the carrier's remaining payments (task 1: 47.20), so the job cannot reach the zero balance contents_invoicing closes on, and contents_evt_late_fee applies to the residue → **CG3-DISC SOURCE-POLICY RED** (XF D8: the rule requires a write no tool can express; E4/E1: a discount the ledger does not carry is not a treatment a business publishes).
- CP netting T2 realism ("a courtesy on the customer's own charges and never relieves the carrier"): plausible; no finding.
- SP/CP supplement sentence: "the most recent supplement request is the one carrying the highest supplement number on the file" followed by "the most recent contents_added supplement request" — read with compute as the highest-numbered contents_added request; a reader who takes "most recent" file-wide would treat a later-numbered price_variance request as making no contents_added request "the most recent". Not engaged in either world (observation O-r3-1).
- Rebuild read: "the company keeps one rebuild contract per claim file and address, added scope … written as a change order" is a company-practice statement the rebuild charter does not itself make (rebuild_agg_one_contract_per_address bars only a second open contract); it sets the tie aside rather than ruling it. Not engaged (observation O-r3-2). A self-pay job matches self-pay rebuild rows only when both store the empty claim reference the same way (observation O-r3-3).
- A1/A5/A7/A9/B4/B5/C1/C2/E5/E7/E9 re-checked on every policy: no new member. Observations carried: O-r2-1, O-r2-2, O-3, O-5, O-6.

### findings (revision_3)
- **CG3-DISC SOURCE-POLICY RED** — symptom: CP fixes a payment 47.20 below the customer's ledger share with nothing booking the difference. Root cause: the prompt-payment discount sentence of contents_ext_closing_payment with no credit write in rule, tool or adjustment enum. Evidence and consequence: 1.md T1-r3-1. Affects task 1.

## closing_checklist (revision_3)
Not reached: task 1 RED on CG3-DISC. Task 0 passes all four relationships. Gates 7/7 on the final form (snapshot_r3.txt). GT equals the frozen revision_3 derivations on every scored argument in both tasks.

VERDICT revision_3: task0=PASS task1=RED charter=CG3-DISC

## revision_4

## charter_global_frozen (revision_4)
- freeze 2026-10-24 ~23:55 UTC, before round-4 task JSONs were opened. Worklog last line `REWORK round 4: gates 7/7 green`; snapshot_r4.txt (run by this auditor): 7/7 gates OK; views 0.json 95899b2e…f365, 1.json 41b06f73…dc3.
- contents.extended.yaml changed (2937d2ed… → dba941b4…d674) → charter re-checked; task_tools.py unchanged (ecfd1a37…) → tool conclusions carried forward.
- Sweep: base copy identical; compute_basis / baseline / superseded_clause / replaced_by / policy_source verbatim (0 misses); no factor id inside a tool name; counts VP 5p/1m, VC 5p/1m, SP 2p/2m, PB 5p/1m, FR 5p/1m, TL 5p/1m, CP 3p/3m.

### status of the revision_3 RED
| id | status | evidence |
|---|---|---|
| CG3-DISC | closed | prompt-payment discount removed (rule, params, bindings, factor). Replacement withheld_depreciation_carry: T1 billable arrangement + contents depreciation_forfeited write-offs → those write-offs (claims_evt_depreciation_release: "Once the window has passed without a request, the withheld depreciation is written off as depreciation_forfeited and becomes the customer's own responsibility on tiers where denied amounts are billable to the customer"); T2 contents depreciation releases issued insured_only → those releases; T3 0. Every carried amount now matches a recorded amount the ledger or the carrier side carries; task 1 ledger closes to zero once the carrier pays its receivable and approved storage |

### class sweep (payment differs from the ledger share with nothing recording the difference), all policies
- SP/CP standard amounts now count customer payments net of refunds (base account: refunds raise the balance) and CP nets billing_error/duplicate_line credits → consistent with the account definition.
- SP/CP declined lines: only an undecided (named by no approval) most-recent price_variance request contests write-offs; a decided request's approval already enters the approved scope → no double relief.
- CP insured proceeds exclude depreciation releases, which the depreciation factor carries → disjoint.
- CP netting T2 (lesser of goodwill and the customer's own charges): where it binds, the excess goodwill stays a credit on the ledger, handled under the base refund rule; nothing unrecorded.
- PB boxes brought back floored at zero (rule and compute).
- No remaining member found. Observations O-r4-1 (carrier-side corrections netted from the customer; ledger still closes) and O-r4-2 (SP does not carry forfeited depreciation; not engaged).

### new-defect scan (revision_4)
- withheld_depreciation_carry: parameter (tiers select an amount from distinct record sets substituted into one sum), ladder disjoint (a release needs a timely request, which bars forfeiture on the same coverage part), multi-source (arrangement parameter + write-offs / payments), cross-difficulty claims, own bindings (A1), moves the task-1 result (8312.89 under its baseline), realistic and charter-grounded (E1).
- "the most recent supplement request of a reason is the one of that reason carrying the highest supplement number on the file" → O-r3-1 closed.
- A2/A5/A7/A9/B1–B5/C1/C2/D1–D8/E5/E7/E9 re-checked across the 7 policies: no new member. Observations carried: O-r2-1, O-r2-2, O-r3-2, O-r3-3, O-3, O-5, O-6, O-r4-1, O-r4-2.

### findings (revision_4)
None.

## closing_checklist (revision_4)
- Per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; revisions 1–4 preserved in order; both revision_4 comparison sections PASS.
- Extended policies fully covered: task 0 {customer_vault_period, customer_valuation_period, customer_share_payment}, task 1 {pack_back_box_line, furniture_reset_line, return_truck_loads, closing_payment} — pairwise disjoint, jointly complete; task tools closed over GT; uuid8s independent and frozen.
- Trees: task 0 two prerequisites (2 value_input), task 1 three (3 value_input); each root is an owner=user payment; the difficulty's prerequisite graph is acyclic.
- Every computation declares a self-sufficient baseline and six (SP four) factors meeting the parameter/method floors, at least one multi-source and one cross-difficulty factor per task; every factor bears weight on its world; whole-baseline fall-backs differ from gold (435.00, 177.70, 1152.19; 3088.80, 880.40, 645.00, 2413.10).
- Instantiation gates re-run on the final form: snapshot_r4.txt, 7/7 OK.
- Coordinator ruling applied: other-category rows no gold step reads are accepted residue; every scored cross-category record is producible with justifying rows seeded and read by gold.
- Observations recorded (no RED): O-r2-1, O-r2-2, O-r3-2, O-r3-3, O-r4-1, O-r4-2, O-3, O-5, O-6.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

## charter_global_frozen (revision_5)
- freeze 2026-10-25 ~02:25 UTC, before round-5 task JSONs were opened. Worklog last line `REWORK round 5: gates 7/7 green`; snapshot_r5.txt (run by this auditor): 7/7 gates OK; views unchanged (0.json 95899b2e…, 1.json 41b06f73…). contents.extended.yaml 65e96761623f31288dc43255361fd45c589eaf5022fbee7bf8225f7bf5cfea1a and task_tools.py 168e1fd03b338bc7d60080a5a16a25712e74687138d3fff73b8566e0e38156e3 changed → re-checked.
- Added inputs (coordinator): render_r1.md (renderer findings S1, S2, S3, secondary C1, notes) and realism_bar.md (R1–R5, X1–X4, R6, RULE-1..5), applied here.

### status of the renderer findings
| item | status | evidence |
|---|---|---|
| S1 (SP plain bindings carrying factor-owned sentences) | closed | denied_writeoffs, declined_share now bindings of declined_lines_contest (baseline adds declined_share '0'); insurer_storage_lines, uncovered_share of uncovered_storage_days (baseline adds uncovered_share '0'); SP plain bindings are period_days, customer_lines, surcharge_lines, payments_posted only; no binding owned twice; no factor reads another's binding (A1 sweep 0) |
| S2 (CP, same) | closed | same move into declined_lines_dispute / unpaid_storage_tail; CP plain bindings period_days, customer_lines, other_customer_lines, payments_posted, corrections |
| S1/S2 class across all 7 policies | closed | plain bindings elsewhere: VP rates/counts and assembly; VC standard (incl. value_covered, a baseline sentence) and coverage_rate; PB standard boxes_back and per_box_rate; FR reset_rate, pieces_set, per_piece_rate; TL fee/capacity/counts and per_load_rate — none names a factor-owned quantity |
| S3 (five charge tools: repeat call raised the balance) | closed | each body now looks up the deterministic line id and returns status already_booked with the unchanged balance before any create/update; docstrings state exactly that (D2) |
| S3 note (pay ids) | closed | both pay tools salt the id and confirmation with the job's count of customer payments; a second real payment posts its own row |
| C1 (TL overwrites retiring non-conflicting parts) | closed | superseded clauses are now the fragments "Truck trips are billed per load" and "Amounts are quantity times unit rate" (verbatim in base), with scoped replaced_by. The third overwrite retires the single status clause; it conflicts only for the move-back truck line, and its replaced_by keeps the gate for every packout, cleaning and disposal line, the scoped pattern C2 prescribes. Accepted, not a member |
| rounding-epsilon / base vault-capacity-0 notes | no change needed | renderer-side and frozen-base observations |

### realism_bar.md pass (all 7 policies, every ladder)
- RULE-1: task 0 reads water and claims; task 1 reads rebuild and claims (claimed siblings) ✓. RULE-2 ✓ (records unchanged since revision_4). RULE-3 n/a (claims). RULE-4: REWORK round 5 carries no figures ✓. RULE-5 n/a (no account reads).
- X1 none. X2: no two discounts/caps stacked on one amount; no charge split into two factors that always sum back. X3: none (recorded approvals and write-offs are read as caps or carried amounts, not as factors embedded in an amount). R6: none used.
- **X4 "larger scope priced lower"** — every volume ladder checked at its threshold:
  | ladder | below threshold | at threshold | verdict |
  |---|---|---|---|
  | VP crate racking (4) | 3 × 18.50 = 55.50 | 4 × 14.00 = 56.00 | ok |
  | FR uncrating (4) | 3 × 28.00 = 84.00 | 4 × 22.00 = 88.00 | ok |
  | FR oversized set (2) | 145.00 | 2 × 120.00 = 240.00 | ok |
  | TL oversized move (2) | 165.00 | 2 × 140.00 = 280.00 | ok |
  | FR second crew (25 / 40) | 0 / 39 × 3.25 = 126.75 | 25 × 3.25 = 81.25 / 40 × 0.2 × tech rate (≥ 502.40) | ok |
  | PB condition check (25) | 24 × 8.75 = 210.00 | 25 × 0.25 × tech rate (≥ 413.13) | ok (O-r2-2 stands) |
  | VC crate / furniture riders, TL air ride, VP secured add | percentage or add rises with the tier | — | ok |
  | **PB wardrobe hanging (20)** | 19 × 5.50 = 104.50 | 20 × 4.25 = 85.00 | **X4** |
  | **PB heavy-box handling (60)** | 59 × 1.25 = 73.75 | 60 × 0.95 = 57.00 | **X4** |
  | **VC electronics coverage (8)** | 7 × 1.75 = 12.25 | declared value × 0.06% (below 12.25 whenever the declared value is under 20,416.67, e.g. 10,000.00 → 6.00) | **X4** |
  These three ladders were present before realism_bar.md existed (rounds 2–4 passed them under XF E1); they surface now under the bar's X4 and are not a regression of this round.

### new-defect scan (revision_5)
Base copy identical; compute_basis / baseline / superseded_clause / replaced_by / policy_source verbatim (0 misses); factor ids not in tool names; forbidden tokens absent; tools perform their docstrings (D2), write in their own bodies (D4), judge no prerequisite (the already_booked lookup is an idempotence check on the tool's own row, not a policy judgement). Factor counts unchanged (VP 5p/1m, VC 5p/1m, SP 2p/2m, PB 5p/1m, FR 5p/1m, TL 5p/1m, CP 3p/3m). No new member of any XF class beyond CG5-X4.

### findings (revision_5)
- **CG5-X4 SOURCE-FACTOR RED (realism_bar X4; XF E1)** — three ladders price a larger scope lower at their volume threshold, because the volume rate replaces the standard rate on every unit: PB.wardrobe_hanging ("when the wardrobe box quantities … total at least the wardrobe volume threshold, each wardrobe box carries the volume hanging charge"), PB.heavy_box_handling ("… each large box carries the volume heavy-box charge"), VC.electronics_coverage_schedule ("… the electronics coverage is the declared value times the electronics value rider percentage …" against "the number of electronics items times the per-item electronics rider" below the threshold). Engaged in task 1 (heavy-box tier, 1.md T1-r5-1); not engaged in task 0.

## closing_checklist (revision_5)
Not reached: task 1 RED on CG5-X4 (realism_bar X4, newly applied). Renderer findings S1, S2, S3 (+ payment-id note) and C1 closed; gates 7/7 on the final form (snapshot_r5.txt); GT equals the frozen revision_5 derivations on every scored argument.

VERDICT revision_5: task0=PASS task1=RED charter=CG5-X4

## revision_6

## charter_global_frozen (revision_6)
- freeze 2026-10-25 ~02:50 UTC, before round-6 task JSONs were opened. Worklog last line `REWORK round 6: gates 7/7 green`; snapshot_r6.txt (run by this auditor) 7/7 gates OK; views unchanged; contents.extended.yaml 1e5ae8ce8da96a81612651f5830361fe50e2f5208379bd04701359be06b5a705 (changed), task_tools.py unchanged (168e1fd0…).
- Sweep: base copy identical; compute_basis / baseline / superseded_clause / replaced_by / policy_source verbatim (0 misses); factor ids not in tool names; binding ownership unchanged from revision_5 (no double ownership; A1 0). Counts: VP 5p/1m, VC 5p/1m, SP 2p/2m, PB 3p/3m, FR 5p/1m, TL 5p/1m, CP 3p/3m.

### status of CG5-X4
| member | status | evidence (threshold probes) |
|---|---|---|
| PB.wardrobe_hanging | closed | graduated: first 20 boxes at 5.50, each beyond at 4.25 → 19: 104.50, 20: 110.00, 21: 114.25 (rule, compute and ladder agree) |
| PB.heavy_box_handling | closed | graduated: first 60 at 1.25, each beyond at 0.95 → 59: 73.75, 60: 75.00, 61: 75.95 |
| VC.electronics_coverage_schedule | closed | value-rated tier "never less than the per-item electronics rider times one item fewer than the electronics rated threshold" = MX(DV × 0.06/100, 7 × 1.75) → 7 items 12.25, 8+ items ≥ 12.25 at any declared value (5000: 12.25; 24000: 14.40) |
Class sweep re-run on every ladder of the 7 policies (revision_5 table plus the three rebuilt): no charge falls when the quantity crosses a threshold. CG5-X4 closed.

### new-defect scan (revision_6)
- Relabels: wardrobe_hanging and heavy_box_handling now `method`. T1 (graduated: threshold × standard + excess × volume) vs T2 (count × standard) adds the threshold input and an intercept → passes XF A7. Honest label. Observation O-r6-1: T1 and T2 together are one graduated schedule (min(n, T) × standard + max(0, n − T) × volume) stated as two tiers; the factor still moves its result (task 1: 4212.40 under its baseline) and its tiers differ in shape.
- Electronics floor sentence has one grouping ("the per-item electronics rider times one item fewer than the electronics rated threshold" = rider × (threshold − 1)); no A9 member.
- realism_bar: graduated rates and a minimum are R1/R3 shapes; no X1–X4 member; no R6 waiver; RULE-1/2/4 honoured.
- No regression of renderer closures (S1/S2 ownership, S3 tool bodies unchanged by hash, C1 overwrites unchanged).

### findings (revision_6)
None.

## closing_checklist (revision_6)
- 0.md / 1.md correspond one-to-one with tasks/0.json and tasks/1.json; revisions 1–6 preserved; both revision_6 comparisons PASS.
- Scopes {VP, VC, SP} and {PB, FR, TL, CP} disjoint and complete; tools closed over GT; uuid8s independent.
- Trees: 2 and 3 value_input prerequisites, owner=user roots, acyclic graph.
- Factors: counts within floors in every computation; every factor bears weight on its world; fall-backs differ from gold (435.00, 177.70, 1152.19; 3088.80, 880.40, 645.00, 2413.10); realism_bar R1–R5 shapes only, no X1–X4, no R6; RULE-1/2/4 honoured.
- Renderer findings S1, S2, S3, C1 closed (revision_5) and intact.
- Gates re-run on the final form: snapshot_r6.txt, 7/7 OK.
- Observations (no RED): O-r2-1, O-r2-2, O-r3-2, O-r3-3, O-r4-1, O-r4-2, O-r6-1, O-3, O-5, O-6.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

## charter_global_frozen (revision_7)
- freeze 2026-10-25 ~03:25 UTC, before round-7 task JSONs were opened. Worklog last line `REWORK round 7: gates 7/7 green`; snapshot_r7.txt (run by this auditor) 7/7 gates OK; views unchanged; contents.extended.yaml b2bba3c6ef191d39cb917f9a7df89d4a1c1cb96497c5638d4d4f63ab546d00f8 (changed); task_tools.py unchanged (168e1fd0…).
- Items verified: KB audit revision_1 src S-1, S-2, S-3 (K-1 = KB consequence of S-1). Base copy identical; compute_basis / baseline / superseded_clause / replaced_by / policy_source verbatim (0 misses); no binding owned by two factors.

### status of the KB-surfaced source items
| item | status | evidence |
|---|---|---|
| S-1 (plain bindings read by exactly one factor, XF A3) | closed | capacity and boxes_packed now belong to vaults_billed_count (VP) and return_load_count (TL); period_days to uncovered_storage_days (SP) and unpaid_storage_tail (CP). Reader sweep over every remaining plain binding of the 7 policies: each is read by result, by another plain binding, by a factor baseline (recorded_vaults in VP/TL), or by a plain binding and a factor (VC declared_value) — except VP/VC period_days, read in compute only by the return-share factor. That one is not a member: the rule's own scope sentence ("the period being billed is the storage period, counted in whole periods of the tier's period length from the custody start date") uses it to fix the billed period, i.e. the scored storage_period_start argument, so the standard method needs it (and the KB audit found no hint in those documents) |
| K-1 (KB documents listing factor-only inputs) | cause closed | source no longer lists those quantities as baseline-owned; re-render is renderer-side |
| S-2 (replaced_by naming sibling machinery) | closed | VP: "a declared-value coverage line that the declared-value coverage rule prices remains under that rule"; VC: "a vault storage line that the customer vault storage rule prices remains under that rule"; PB/FR: the sibling return lines "remain under their own rules" — no sibling factor or fraction named; C2 sibling naming kept; other replaced_by texts name no machinery |
| S-3 (undefined "customer lines" in the referral scope) | closed | SP/CP: "customer payments settling the oldest storage and declared-value coverage lines billed to customer first" — matches the scope's own test and contents_msr_customer_storage_unpaid; no other rule uses "customer lines". Closes observation O-r2-1 |

### new-defect scan (revision_7)
No compute changed (values recomputed identical in both worlds); no factor added or reshaped; counts unchanged (VP 5p/1m, VC 5p/1m, SP 2p/2m, PB 3p/3m, FR 5p/1m, TL 5p/1m, CP 3p/3m). realism_bar: R1–R5 shapes only, no X1–X4, no R6; RULE-1/2/4 honoured. Prior closures intact (CG5-X4 graduated ladders and floor, renderer S1/S2/S3/C1, CG3-DISC ledger closure).

### findings (revision_7)
None.

## closing_checklist (revision_7)
- 0.md / 1.md one-to-one with tasks; revisions 1–7 preserved; both revision_7 comparisons PASS (below in each task file).
- Scopes disjoint and complete; trees 2 and 3 value_input prerequisites with owner=user roots, acyclic; factors within floors, all bearing weight, fall-backs ≠ gold; realism_bar satisfied; gates 7/7 on the final form (snapshot_r7.txt).
- Observations carried (no RED): O-r2-2, O-r3-2, O-r3-3, O-r4-1, O-r4-2, O-r6-1, O-3, O-5, O-6 (O-r2-1 closed).

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

## revision_8

## charter_global_frozen (revision_8)
- freeze 2026-10-25 (round 8), before round-8 task JSONs were opened. Worklog last line `REWORK round 8: gates 7/7 green`; snapshot_r8.txt (run by this auditor) 7/7 gates OK; views unchanged; contents.extended.yaml c71256c8c4134311253424f443ca2d0a2c3bf9104e0d7f42dfd9154ba04c180b (changed); task_tools.py unchanged. Item verified: KB re-judge revision_3 src S-4 and its class. Base copy identical; compute_basis / baseline / replaced_by / policy_source verbatim (0 misses).

### S-4 and class (appositives reading as extra conditions)
- S-4 closed. TL now reads: "Delivering to a property whose rebuild the company has not yet closed out costs crew waiting time, and the wait charge is keyed on the contract's status alone: when … substantially_complete status, each return load carries the open-site wait charge; when it is in final_invoiced status, each return load carries the invoiced-site wait charge; in any other status, or with no company rebuild contract read at that address, no wait charge applies." Both appositives ("with its punch list still open", "with closing visits still being made") are gone; rule = compute_basis = ladder = compute (status only).
- Class sweep (my own, every rule sentence of the 7 policies, clauses introduced by ", with / while / as / which / because / once / after / before / unless / where / except / whose / being / having", plus parentheses):
  - Operative and matching compute: VC/PB "except that items listed on signed disposal authorizations …"; SP prerequisite "when it falls to the customer"; the scope condition "while no storage line billed to customer … has stayed unpaid …"; PB graduated "as many … as that threshold …"; SP/CP "before its rounding and before its floor at zero".
  - Reasons and explanations that add no condition: "because the coverage is the customer's own election", "because they are never compensated", "which the insured pays the company from", "as the line amount".
  - No parentheses in any rule.
- Topic sentences before ladders also checked: "Newly finished floors are protected while boxes come back" (PB) and "Floor runners are laid under every piece set on newly finished floors" (FR) lead into explicit ladders whose second tier ("more than the fresh-finish days … settled-finish …") states the treatment of older finishes outright, so neither restricts a tier. The same holds for "Carrier money is the insured's to pass on where the carrier does not pay the company", "Large households take a second reset crew" and "Unit deliveries need elevator or stair booking". Not members (observation O-r8-1 for the two floor topic sentences).
- No compute changed; values recomputed identical in both worlds; counts unchanged. realism_bar (incl. RULE-6/7): no factor changed shape; no X1–X4; no R6; no factor acts only through others' outputs (A4/A6 unchanged). Prior closures intact.

### findings (revision_8)
None.

## closing_checklist (revision_8)
As revision_7, re-confirmed on charter c71256c8…: scopes disjoint and complete; trees, owners and graph unchanged; factors within floors and bearing weight; fall-backs ≠ gold; realism_bar satisfied; gates 7/7 (snapshot_r8.txt). Observations carried: O-r2-2, O-r3-2, O-r3-3, O-r4-1, O-r4-2, O-r6-1, O-r8-1, O-3, O-5, O-6.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN
