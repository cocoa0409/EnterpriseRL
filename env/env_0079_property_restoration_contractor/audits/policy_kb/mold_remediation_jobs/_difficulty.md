# KB-doc policy audit — mold_remediation_jobs / product mold

## revision_1 (2026-10-24, independent KB auditor)

Inputs: blueprint difficulty mold_remediation_jobs, product mold, M=2; policy-side verdict "VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN"; gate snapshot .audit_views/runtime/mold_remediation_jobs/kb_snapshot_r1.txt (check_docs DOCS OK; check_traceability TRACEABILITY OK, 1 miss line / 0 mentioning unlock; all other gates OK; source hashes mold.extended.yaml 2ad97845…986d, task_tools.py c4b79c1f…9846); runtime views 0.runtime.json 551938…1831461, 1.runtime.json 1e5b6d…eb9cf (re-hashed, match). check_docs / check_traceability not re-run by the auditor (coordinator-owned; check_traceability prints hidden names).

Files: runtime_context/mold_remediation_jobs/{0,1}.md (blind_answer frozen before reveal, sha256 of blind files at freeze 2d1262e3… / 0394ddba…, then gt_comparison appended); policy_kb/mold_remediation_jobs/{0,1}.md (source_to_kb, kb_to_source, bijection_verdict, dependency_form).

| Task | Runtime blind audit | Two-way scan | Dependency form |
|---|---|---|---|
| 0 (signing deposit; sampling + work-plan lines) | PASS — 450.00 / 707.96 / 2702.96 debit_card, both hops state-derived | PASS | PASS |
| 1 (insured share; haul-off line) | PASS (conditional C1-C3) — 838.00 / 1481.69 ach, hop state-derived | PASS | PASS |

Closing checklist:
- Every normative atom of the five extended policies (rules, both-way overwrites, 25 factor ladders with every tier and constant, baselines, assembly) and of the governing base policies is entailed by docs/mold; variant parameters equal value by value; retired clauses (independent-assessment clause 6; the two remediation-scope clauses) written as retired, unnamed clauses in force.
- The three prerequisite sentences stand verbatim, state form, in the blocked policies' hubs only; each hop resolvable from the depended-on hub and the records; no other problem's tool, route or aggregated chain anywhere.
- No gold value in tool schemas/docstrings or worked examples.
- Cross-product conditional (task 1 only): C1 Carrier Program Claim Billing accepts carrier payments issued directly to the company; C2 it never bills declined lines to the customer; C3 it writes off carrier program price adjustments — Insurance Claim Services charter properties, corpus not yet published.
- Auditor-view note: db_query --list prints only share read tools; the share write tool verify_customer_identity (in GT) is visible to the agent through its runtime schema, so the blind files' "no identity rule in KB" is a view gap, not a KB defect.
- Observations (no verdict effect): O1 computation docs carry the source's generic assembly sentence without "Where a schedule below applies"; O2 the share computation doc's assembly names "the coverage limit" (source: "the coverage limit it sets") without that qualifier, revealing a cap exists; fall-back still definite via its Rule sentence.

Source-side item:
- S2: base mold_evt_remediation_scope keeps params.scope_unit_rates (asbestos_sampling, supervisor_labor, debris_disposal -> tier unit rates) and formula amount = round(quantity * unit_rate, 2) un-retired while three overwrites retire "Each scope line is billed at the tier's unit rate for its code times the quantity performed…" for exactly those lines; rendered faithfully as "Rates by code: Each scope code takes the tier's own figure … supervisor labor, lead-safe setup and asbestos sampling … A line's amount is its quantity multiplied by its rate" in "Mold Remediation Scope Line and Equipment Day Billing Rules", beside that doc's own retired-clause notice. Resolved on the visible surface by the line-specific "and only for that line" sentences; no scored consequence.

KBVERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=S2

## revision_2 (2026-10-25, cross-product re-judge; published: water, mold, contents, claims, fire, account; rebuild pending — nothing in either task rests on rebuild)
Gate snapshot .audit_views/runtime/mold_remediation_jobs/kb_snapshot_r2.txt (run by this auditor, execute only): DOCS OK; TRACEABILITY OK (1 miss / 0 unlock); all other gates OK; source hashes unchanged; docs/mold 56 files, content identical to round 1.
1. Round-1 conditionals: C1 (contractor-direct: Carrier Program yes), C2 (denied line billable: no), C3 (program price write-off allowed: yes) — all resolved on the assumed tiers; task-1 share 1481.69 now unconditional. No regression; no new KB defect.
2. Re-pricing of every other-product row gold reads: task 0 water job 53c34fc8 + 5 lines, claim file 04479e28 + approval — all match. Task 1 water job 5814714c + 21 lines, claim file 5ebf1e21 + 3 approval/write-off rows + 2 deductible rows — all lines match; two mismatches (M1, M2), neither read by a scored factor. Mold-own seeded rows re-priced as well: match.
3. E5: clean in both worlds (the only owed cross-product write a solver could make mid-call, the task-0 water tear-out debris line, moves no scored read).
Observations (no verdict effect): O3 program write-off amount unconstrained by rule; O5 337.01 decline recorded only by its write-off (base-rule form); O7 task-0 water job has no equipment/monitoring lines yet.

Source-side items:
- S2 (carried from revision_1): base remediation-scope unit-rate params/formula restate the retired clause for the three overwritten lines.
- M1: task-1 water job 5814714c carries flood_cut 52 lf (2026-08-27) but no tear-out debris haul-off line, which the published water rule bills on every job with flood cut lines, yet it was invoiced on 2026-09-02 (3753.60). No scored value moves.
- M2: task-1 claim file 5ebf1e21's estimate was submitted 2026-08-31, 5 days after opening on 2026-08-26; the Carrier Program target is 3 days, and the estimating standard says "within the tier's estimate submission target days". The field isn't read by any factor.
- S3: latent cross-product conflict: the mold declined-line write-down would also prorate a claims credited-line carrier_denied_line write-off (water/rebuild credits already given), relieving the mold job twice on Carrier Program files; not engaged in either task world.

KBVERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=S2,M1,M2,S3

## revision_3 (2026-10-25)
Entry: policy_task last line "VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN" ✓. runtime_views.sh: 0/1.runtime.json hashes unchanged. kb_snapshot_r3.txt: DOCS OK; TRACEABILITY OK (1/0); all gates OK; mold.extended.yaml 81f208e0…42be (only change: one hand-off sentence in mold_ext_insured_share); task_tools.py unchanged; docs/mold 56 files, one changed (the declined-line write-down doc carries the new sentence).
- M1 closed: water debris_haul 297.50 is priced correctly under the published water rules (1 load at the Class 3 80-lf size; 238.00 × 1.25), and the invoice/balance is 4051.10.
- M2 closed: estimate submitted 08-28, within the 3-day target.
- S3 closed: the credited-value hand-off is carried losslessly; not triggered in task 1 (no water credits, no rebuild contract).
- Figures moved: none (450.00 / 707.96 / 2702.96; 838.00 / 1481.69 re-derived and unchanged).
- Own-category history rows gold reads (2025 Spot job; task-1 job's sampling, work-plan, deposit, scope, equipment and clearance lines) re-priced against the published extended docs: all match.
- No new KB defect; nothing regressed. Observation O8: the new hand-off is homed in a factor doc, but it is findable from its trigger's record words.

Source-side item still open:
- S2 (carried since revision_1, no scored effect): the base remediation-scope unit-rate params/formula restate the clause the three overwrites retire for the sampling, work-plan and haul-off lines; rendered faithfully, and resolved on the visible surface by each line's "and only for that line" sentence.

KBVERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=S2
