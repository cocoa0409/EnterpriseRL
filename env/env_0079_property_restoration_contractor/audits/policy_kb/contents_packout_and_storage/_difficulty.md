# KB doc-policy audit — contents_packout_and_storage (product contents), difficulty close-out

## revision_1 (2026-10-25)

Inputs: kb_snapshot_r1.txt (check_docs DOCS OK; check_traceability TRACEABILITY OK, 1 miss line / 0 mentioning unlock; extended/task-tool/replay/solvability/compute/grounding/cross-fire OK); runtime views 0/1 hashes match the brief; source hashes match the snapshot; policy-side verdict "VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN". Blind answers frozen before reveal (runtime_context/contents_packout_and_storage/0.md, 1.md); no contamination. check_docs / check_traceability not re-run by this auditor (brief: coordinator-run only).

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Task verdict |
|---|---|---|---|---|
| 0 | PASS (259.07 / 160.73 / 3,869.69 debit, hops state-derived) | PASS | RED (K-1) | RED |
| 1 | PASS (4,298.80 / 1,434.93 / 805.84 / 8,930.89 ach, hops state-derived) | PASS | RED (K-1) | RED |

### KB RED ids
- K-1 (KB-EXPLICIT): the baseline documents list inputs that only a factor uses, which hints at a variation that should be discovered from the records. Every member:
  1. customer_vault_storage_line_calculation_f44eae72 — "The boxes packed" row and "vault capacity" in "The tier's vault rate, period length and vault capacity" (used only by the vaults-charged factor).
  2. customer_share_amount_calculation_e158311e — "Period length" row (used only by the storage-days factor).
  3. return_truck_line_calculation_a37a5401 — "the boxes packed recorded at custody start" and "vault capacity (vault storage rate card)" in Inputs (used only by the return-loads factor).
  4. closing_payment_amount_calculation_56f5151e — "period length" row in Terms used (used only by the unpaid-storage-days factor).
  No other computation document carries an input its baseline does not use (declared-value, pack-back and furniture reset baselines checked).

### Source-side items (src)
- S-1: plain compute bindings used by exactly one factor (XF A3) — customer_vault_period capacity, boxes_packed; return_truck_loads capacity, boxes_packed; customer_share_payment period_days; closing_payment period_days. Root of K-1.
- S-2: replaced_by sibling-exclusion wording names the sibling's machinery — customer_vault_period / customer_valuation_period contents_return replaced_by ("follows that rule's own fraction", disclosing the sibling's return-fraction factor; rendered in the two return-period factor documents); pack_back_box_line / furniture_reset_line contents_return replaced_by ("… follow their own rules").
- S-3: "customer payments settling the oldest customer lines first" (customer_share_payment and closing_payment scope) — "customer lines" undefined; counting card surcharge lines flips both seeded worlds to referral (task 0: 32.72 unpaid on the 2026-08-21 line, 63 days; task 1: 53.10 on the 2026-08-07 line, 77 days). Gold and the base measure contents_msr_customer_storage_unpaid use storage/coverage lines billed to customer only.

### CONDITIONAL (cross-product figures not yet findable; not RED)
- Insurance Claim Services corpus unpublished: Direction to Pay supplement window (180 days per claims.yaml; task 0 at 184 days, task 1 at 217) and "bills denied lines to the customer" (true) — both read by the scope-overrun, declined-lines and withheld-depreciation ladders; claims rows (approvals, write-offs, ACV payments, requests) cannot be priced against published claims docs yet.
- Reconstruction corpus unpublished: task 1 contract tiers (condo_unit, substantially_complete, completion 2026-10-08).
- Published other-product rows the gold reads are producible: water job category_3 Black Water Standard (task 0); fire job moderate, Moderate Fire and Smoke Cleanup, condo unit (task 1). Unread other-category rows are RULE-2 residue.

### Observations (no verdict)
- Generic combination sentences in every computation document enumerate the adjustment kinds (percentage, factor, add, per-item amount, fraction) — the rules' own XF A2/A5 assembly sentences.
- Factor "points of judgement" negations (lining: customer-described category does not count; facility: not the loss address or branch) are derivations of the record-authority wording, not routes.

### Closing checklist
- Audit files 1:1 with tasks (runtime_context 0.md/1.md, policy_kb 0.md/1.md): yes.
- Every normative atom of the seven extended policies, their overwrites and governing base rules entailed by the contents docs; every prerequisite sentence verbatim on its blocked hub only, state form, resolvable from the depended-on hub and the records; every factor ladder complete in its own document: yes.
- No other problem's tool name, route or aggregated chain anywhere: yes.
- Outstanding: K-1 (4 documents); src S-1, S-2, S-3; conditional claims/rebuild figures until those corpora publish.

KBVERDICT revision_1: task0=RED task1=RED kb=K-1 src=S-1,S-2,S-3

## revision_2 (2026-10-25)

Entry: policy_task last line "VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN" (checked first). runtime_views.sh and kb_snapshot.sh run by this auditor (execute only) -> .audit_views/runtime/contents_packout_and_storage/kb_snapshot_r2.txt: check_docs DOCS OK; check_traceability TRACEABILITY OK (1 miss / 0 unlock); extended, task tools, replay, solvability, compute, grounding, cross-fire OK; yaml b2bba3c6…, tools 168e1fd0…; runtime views unchanged.

| Round-1 id | Status | Evidence |
|---|---|---|
| K-1 | closed | factor-only rows removed from all 4 calculation docs (vault: boxes packed / capacity; share: period length; truck: boxes packed / capacity; closing: period length); factors still name those inputs |
| S-1 | closed | capacity, boxes_packed, period_days now listed in the owning factors' bindings |
| S-2 | closed | "follows that rule's own fraction" -> "remains under that rule"; "follow their own rules" -> "remain under their own rules"; source and KB match |
| S-3 | closed | "oldest storage and declared-value coverage lines billed to customer first" in both rules and both hubs |

Regression scan: the doc delta is exactly 8 contents docs, each matching a source delta word for word. Prerequisite sentences unchanged and only on their blocked hubs. No tool name outside its own hub. Gold arguments unchanged. Blind values re-derived on the changed text (differential, with a contamination disclosure in the runtime_context files) still equal GT. No new defect.
CONDITIONAL (unchanged): the Insurance Claim Services and Reconstruction corpora are still unpublished (docs/: account, contents, fire, mold, water), so the Direction to Pay supplement window and the denied-lines-billable figures, and the task-1 rebuild contract tiers, are conditional, not RED.

KBVERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_3 (2026-10-25)

Entry: I ran kb_snapshot_r3.txt myself (execute only). check_docs DOCS OK; check_traceability TRACEABILITY OK (1 miss line / 0 mentioning unlock); every other gate OK. Sources (yaml b2bba3c6…, tools 168e1fd0…) and contents docs (tree facf284b…) are unchanged since revision_2. Every product is published: account, claims, contents, fire, mold, rebuild, water.

- (1) Conditional items, all resolved, and all equal GT:
  - Direction to Pay supplement window: 180 days (task 0 at 184 days, task 1 at 217).
  - Direction to Pay denied line billable to customer: yes.
  - Task 1 Standard Rebuild Agreement for a condo unit: producible.
- (2) Every other-product row the gold reads, re-priced against the owning product's published docs as of its posting date. No mismatch.
  - Claim files, scope approvals, the supplement and its approval, carrier_denied_line and depreciation_forfeited write-offs, contractor_direct and insured_only ACV payments, and receivables, in both tasks.
  - Task 0 water job; task 1 fire job and rebuild contract.
  - Residue recorded only: neither Direction to Pay file shows the deductible line the published rule assesses "when the file opens". Unread (RULE-2).
- (2b) Own-category history rows the gold reads reproduce this difficulty's published extended docs:
  - Task 0: coverage lines 305.28 / 267.89 and the customer vault line 431.78.
  - Insurance-billed and High-Value lines are on base.
  - The task 1 custody credit is a recorded settlement. No mismatch.
- (3) E5: no other-product write tool on the runtime surface. At rule level nothing owed at once moves a scored read: extension lead days, supplement windows and the depreciation window are past, and the rebuild final invoice is not owed at once. PASS.

| Id | Kind | Status |
|---|---|---|
| S-4 | src | new. The appositive "with its punch list still open" in the site-wait rule (contents_ext_return_truck_loads) conflicts with the published Reconstruction 10 punch-list days on task 1's dates (walkthrough 10-08, return 10-20). Reading it as a condition moves the truck line 805.84 to 735.84 and the closing payment 8,930.89 to 8,860.89. Ladder, compute and KB table key on status; the KB carries the rule verbatim, so this is not a KB defect. |

No KB defect, no regression.

KBVERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=S-4

## revision_4 (2026-10-25)

Entry: policy_task last line "VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN" (checked first). I ran runtime_views.sh and kb_snapshot.sh myself (execute only) -> kb_snapshot_r4.txt: check_docs DOCS OK; check_traceability TRACEABILITY OK (1 / 0); every other gate OK; yaml c71256c8…, tools 168e1fd0…; runtime views unchanged.

| Round-3 id | Status | Evidence |
|---|---|---|
| S-4 | closed | The rule and site_wait_charge_on_return_loads_9f2fa622 drop "with its punch list still open" and "with closing visits still being made"; the tier is keyed on status alone, which equals the ladder and compute. Task 1 contract still substantially_complete -> 35.00 per load; truck 805.84 and closing 8,930.89 unchanged. |

Regression scan: exactly 1 contents doc changed, matching the only source change. Gold amounts and seeds are unchanged. Prerequisite sentences and tool sections are unchanged. No new KB or source defect.

KBVERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=NONE
