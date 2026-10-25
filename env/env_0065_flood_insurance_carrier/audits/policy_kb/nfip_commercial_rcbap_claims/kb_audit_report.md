# KB-doc policy audit — env_0065_flood_insurance_carrier / nfip_commercial_rcbap_claims (product nfipcom), round 1

Auditor: independent KB-audit agent, 2026-10-17. Per-task files: audits/runtime_context/nfip_commercial_rcbap_claims/{0,1}.md (blind_answer frozen and hashed in {0,1}.freeze.sha256 before reveal; gt_comparison appended) and audits/policy_kb/nfip_commercial_rcbap_claims/{0,1}.md.

## Step 0 — entry conditions

- Policy-side verdict: "VERDICT revision_11: task0=PASS task1=PASS / charter=CLEAN" (from the brief).
- Gate snapshot .audit_views/kb/nfip_commercial_rcbap_claims/snapshot_kb1.txt: check_docs nfipcom "DOCS OK" (65 docs; factor 28, hub 6, baseline 6, policy 16, facet 9); check_traceability "TRACEABILITY OK" (0.json 14/0, 1.json 24/0) and post-publication "TRACEABILITY OK"; other gates OK. validate_scenario reads INVALID; per the brief the filtered "required document not found" lines belong to the unpublished dwelling difficulty — noted, not judged here.
- Runtime view (0.runtime.json sha256 f5adbe7f..., 1.runtime.json sha256 57da6033...) and DB access path db_query.py supplied and used; the DB side of the blind audit is blind (tool-shaped reads only).
- Contamination: none. No forbidden file was opened before the freeze; no recursive search over tasks/ or audits/.

## Per-task part verdicts

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Task verdict |
|---|---|---|---|---|
| 0 (building POL -> building payment) | PASS — every scored argument matched blind (67880.00; 25939.64, INSURED, claim 2608274) | PASS | PASS | PASS |
| 1 (contents POL -> contents payment -> processing -> refund) | PASS — every scored argument matched blind (18000.00; 12525.56; 2026-09-04 / 7357.63; 77.11 / 1338.25 / 257.53 / 80.00 / 50.00 / 9485.73, INSURED) | RED (kb-1, kb-2) | PASS | class RED (KB-BIJECTION) |

Problem trees: both derived hop by hop from the hub prerequisite sentences and the records, every hop state-derived, none pre-solved; each tree contains a customer-owned write (the proof-of-loss signing). Fall-back numbers from the computation documents alone are definite and differ from GT (task 0: 487,666.67 / 67,880.00; task 1: 131,500.00, risk credit 7,390.61, refund 9,069.62). Every declared factor was found from the records' own words; cross-product BizFlood figures (zone-V 5% / 25000, excess attachment "No") are published in docs/bizflood, so nothing is CONDITIONAL.

## KB defects (translation layer)

- kb-1 (task 1, KB-BIJECTION, retired surface): the superseded fee/components semantics of the base cancellation clause are still stated as live rules outside the C6/C8 retirement notes — cancellation_terms_sheet_994f4234 bullet "The Federal Policy Fee and probation surcharge do not come back on a pro rata or current-term refund." and cancellation_and_refund_rules_4fbe1c20 closing sentence "The components a current-term-full or pro rata refund can return are the risk premium, ICC premium, Reserve Fund Assessment and HFIAA surcharge." Both contradict the in-force cancellation-refund rule (fees of a term that began after the cancellation took effect returned in full; this task returns 80.00 and 50.00). Reading the terms sheet literally gives 9,355.73.
- kb-2 (task 1, anti-leak, low): contents_payment_working_3350fd39 hypothetical worked figure ends "payment 18,000.00", equal to task 1's scored contents claimed_amount 18000.0.
- Wording note (no verdict): the month-band "hold" definition drops the connective "that is" in cancellation_risk_premium_credit §4 and the factor "Terms" paragraphs (current_term_risk_premium_return, endorsement_risk_premium_return, reserve_fund_assessment_return_on_cancellation); entailment unchanged.

## Source-side findings (not KB-translation defects; do not change the KB verdict)

- src-1 (nfipcom_ext_cancellation_refund, overwrite scopes, untriggered branch): overwrite 1 ("For a cancellation refund ... the refund ... is all those credits plus the premium received but not owed") and overwrite 3 (fees of a later term "returned in full" for a cancellation refund) are unconditional, while overwrite 2 says that when the current and prior terms carry more than one premium-bearing endorsement or re-rate credit "under CURRENT_TERM_FULL and PRO_RATA the Federal Policy Fee and probation surcharge are fully earned ... and the refund is the total of the credits". The compute follows overwrite 2 (out of scope: result = xr_risk + xr_base_other, no PRNO). The KB faithfully carries both (C6/C8 notes unconditional; cancellation_refund_working §B unconditional vs §C conditional), so the contradiction is visible on that branch. Both tasks sit inside the scope (one endorsement, one re-rate credit), so no scored number is affected. Nature: inconsistent overwrite scopes on the policy side.
- src-2 (computation documents naming factor quantities, inherited from baseline/rule): the baseline.rule of nfipcom_ext_building_payment and nfipcom_ext_contents_payment carries the full other-insurance method (deductible layer, sharing with the other coverage's sworn amount, share of the rest, excess test), and their rules put the BizFlood definition and the at-most-once/nil-and-refer clause beside it; the rendered computation documents (building_payment_working, contents_payment_working) therefore announce that BizFlood other insurance modifies the payment. Likewise the cancellation_credit baseline names the endorsement charges and "no re-rate credit is taken back", and the refund overwrite names the processing step ("booked when the cancellation is processed"). The KB renders these word for word (correct per Value 0); the effect is that factor discovery for these policies is signalled by the computation document rather than found only from the records.

## Closing checklist (difficulty not closed — task 1 RED)

- Audit files one-to-one with tasks: yes (revision_1, no earlier revision).
- Every normative atom of the six extended policies and their base refs located in docs/nfipcom; every prerequisite sentence verbatim, state form, only in its blocked hub; every factor ladder complete in its own document; no other problem's tool name, route or aggregated chain anywhere.
- Open: kb-1, kb-2 on the KB side; src-1, src-2 on the source side. check_docs / check_traceability not re-run (difficulty not closing; gate lines above are from the coordinator snapshot).

KB VERDICT round 1: task0=PASS task1=KB-BIJECTION RED
kb=kb-1,kb-2
src=src-1,src-2

## revision_2 — re-audit round 2 (2026-10-17T20:10Z)

### Gate first
- `tail -2 audits/policy_task/nfip_commercial_rcbap_claims/_difficulty.md`: "VERDICT revision_12: task0=PASS task1=PASS" / "charter=CLEAN" — as required.
- Newest docs/nfipcom file 2026-10-17 20:05:58Z, newer than nfipcom.extended.yaml 19:53:13Z — as required.
- Run by this auditor:
  - check_docs env/env_0065_flood_insurance_carrier nfipcom -> "[PASS] mechanical gates ... every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding" / "DOCS OK" (prerequisite edges=4, task_tools=6).
  - check_traceability tasks/nfip_commercial_rcbap_claims -> "0.json 14 0 True / 1.json 24 0 True / TRACEABILITY OK".
  - mkruntime.py -> 0.runtime.json sha256 f5adbe7f..., 1.runtime.json sha256 57da6033... (unchanged).
- Corpus hash 6925b8fd7135b4e93cd634e6739ad49096b7f56f4bfef83259bd7055fcb711df (all 65 docs re-rendered); re-read in full.
- contamination_disclosure: revision_2 runtime answers are re-derivations, not blind (source/GT revealed in revision_1).

### Round-1 items
| Item | Status | Evidence |
|---|---|---|
| kb-1 | CLOSED | cancellation_terms_sheet bullet + "Parameter meanings" and cancellation_and_refund_rules closing sentence now carry overwrite 3's scope ("... with the scoped exception for a cancellation refund ..."); C6/C8 notes scoped; fee factor documents scoped. No visible sentence contradicts the in-force fee rule. |
| kb-2 | CLOSED | contents_payment_working example now ends "payment 17,187.50"; no corpus figure equals a scored value of either task. |
| wording note (month band) | CLOSED | "that is when no loss dated after the month band ..." restored in all five places. |
| src-1 | CLOSED | Overwrites 1/2/3 and the baseline assembly now exclude each other by scope and match the compute (in scope `result`; out of scope `xr_risk + xr_base_other`); KB carries them (§B/§C, C6/C8, fee docs). |
| src-2 | not routed (coordinator stop rule; logged) | unchanged; not re-raised. |

### Regression and new-defect sweep
- Source: only the cancellation-refund overwrites, the baseline assembly sentence and the rule sentences that carry them changed. All other extended policies, factor ladders and prerequisites are as in round 1, and GT arguments are unchanged for both tasks.
- KB: rule text of every other document is unchanged.
  - New "Parameter meanings" lists on nine schedule documents restate parameter_schema descriptions plus the overwrite scoped exceptions (S3, S5, contents-minimum deductible, fees). They add no obligation or calculation.
  - Wording note only: the bullets do not name the column they describe.
  - Changed hypothetical figures are checked arithmetically and match no task value.
- Cross-product re-judged on the final corpus (all seven products published): docs/bizflood deductible_schedule still gives "BizFlood Building and Contents | 5 | 25000" and nfip_excess_attachment "BizFlood Building and Contents | No". No other product's docs state a rule on General Property Form / RCBAP claims or cancellations that conflicts (bizflood excess/commencement conditions and forceplaced owned-building factor only reference the NFIP policy). Nothing CONDITIONAL remains.
- Both tasks re-derived from the current visible corpus to the same arguments as GT (task 0: 67,880.00 / 25,939.64 INSURED; task 1: 18,000.00 / 12,525.56 / 2026-09-04, 7,357.63 / 77.11, 1,338.25, 257.53, 80.00, 50.00, 9,485.73 INSURED). All hops state-derived; no pre-solved hop.

### Per-task part verdicts (revision_2)
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Task verdict |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

### Closing checklist
- Audit files one-to-one with tasks; revision_1 text untouched, revision_2 appended in all four per-task files.
- Every normative atom of the six extended policies and their base refs is entailed by docs/nfipcom; every retired clause is marked with its exact scope; every prerequisite sentence is verbatim, state form, only on its blocked hub; every factor ladder is complete in its own document; no tool name, route or aggregated chain is stated beyond the sentences.
- Final-form gate lines placed on record above (check_docs DOCS OK; check_traceability TRACEABILITY OK).

KB VERDICT round 2: task0=PASS task1=PASS
kb=CLEAN
src=NONE
