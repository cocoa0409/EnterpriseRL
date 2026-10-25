# KB doc-policy audit — orthodontic_benefits (product ortho, "Orthodontic Benefit Riders") — difficulty close-out

## revision_1

Auditor: independent KB auditor. Brief entry conditions on record: policy-side `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN`; gate snapshot 2026-10-19T17:31:32 — `check_docs.py ... ortho` -> `DOCS OK`; `check_traceability.py .../orthodontic_benefits` -> `0.json 22 0 True / 1.json 19 0 True / TRACEABILITY OK (non-unlock misses: 0)`; instantiate gates EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK. Gates not re-run by the auditor (coordinator notes, binding: the snapshot is authoritative and running gates leaks tool names); final form unchanged since the snapshot (last ortho doc mtime 17:30:26 < 17:31:32; source sha256 prefixes re-checked 7fb0c4d97ce747af / ae8fd16b76be984b; corpus prefix f95a665e3febf6b8).

| Task | Runtime blind audit | Two-way scan | Dependency form | Files |
|---|---|---|---|---|
| 0 (carried first payment <- transfer recognised fee) | PASS — all values equal GT (1331.22; 237.92; position 5, 2026-12, practice); hop state-derived | PASS | PASS | runtime_context/orthodontic_benefits/0.md, policy_kb/orthodontic_benefits/0.md |
| 1 (member repayment <- takeover re-establishment) | PASS — all values equal GT (2971.21, 23; 368.43 vs initial payment); hop state-derived | PASS | PASS (S1 source-side) | runtime_context/orthodontic_benefits/1.md, policy_kb/orthodontic_benefits/1.md |

Closing checklist:
- Audit files one-to-one with tasks 0 and 1; blind answers frozen with hash lines before reveal; no contamination.
- Every normative atom of the four extended policies (rules, overwrites, baselines, all factor ladders incl. untriggered tiers, prerequisites, tool contracts) and of the base policies they govern has an equivalent home; retired surface correct for all six overwrites; nothing added; no world state written as policy.
- Both prerequisite sentences stand verbatim, state form, in the blocked policy's hub only; each hop resolvable from the depended-on rule's own words and the records; each task tool named only in its own hub; no route, chain or task-mirroring title.
- Every factor document carries its full ladder with figures and is findable from the record words its tier rests on (cross-product factors name "Dental PPO Plans" and the claim-line codes / coverage start they read).

Source-side items (KB renders them faithfully; not KB defects):
- S1 — takeover rule (`ortho_ext_waiting_takeover_fee`): "the fee of the practice now treating the patient" is a plain quantity only factors use, and the assembly sentence names it ("added back as its share of the fee of the practice now treating the patient"); its definition sentence also names two factor subjects. This forces covered_treatment_fee_calculation (the baseline document) to define the moved-case fee and to state that a kept-whole part exists. Detail in policy_kb/orthodontic_benefits/1.md.

Non-blocking notes (no id; no wrong number results): N1 generic assembly sentences in all four computation documents name the kinds of adjustment (source's own `result` sentences); O1 progress-share sentence does not anchor which entry's planned months (baseline anchors the establishment entry); O2 `ortho_takeover_basis` parameter description not narrowed by the proration overwrite (specific exception carried); O3 tenure reduction scoped "for the recognised covered-treatment fee" while scored months_remaining also depends on it.

Coverage note: only the ortho product claimed by this difficulty is audited; cross-product contradictions are outside this skill's range (vision not yet published).

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=S1

## revision_2

Cross-product re-judge (coordinator round 2; /tmp/erl0070_coord/rejudge_notes.txt). Snapshot cited (run by `/tmp/erl0070_coord/kb_snapshot.sh orthodontic_benefits ortho`, 2026-10-20T03:41:00): `DOCS OK`; `0.json 22 0 True / 1.json 19 0 True / TRACEABILITY OK / non-unlock misses: 0`; EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; src sha256 7fb0c4d97ce747af ae8fd16b76be984b. Ortho corpus unchanged (f95a665e3febf6b8). Published other products: dental 73, billing 52, provider 72, dhmo 18, group 15, savings 17 docs; vision 0 (not published).

Round-1 status: no RED to close; S1 is a coordinator DECISION (placement-only), not re-raised; no regression and no new KB defect.

### Exhaustive pass over every other-product row in the two task worlds (read via db_query.py)
Rows present: dental_plans (w0 2, w1 2), dental_claim_lines (w0 5, w1 7), dental_accumulator_postings (w0 5, w1 0), billing_accounts (1 each), billing_transactions (w0 78, w1 106), provider_agreements (1 each), provider_payment_events (w0 1, w1 2), customers. No rows in dhmo, group, savings, vision, estimates, appeals, coverage/billing/provider requests, disputes, identity verifications or handoffs.

Re-derived and consistent with the published docs: dental enrollment effective dates (15th-of-month cutoff: 2023-11-20 -> 2024-01-01; 2022-06-08 -> 2022-07-01); one-plan-one-tier per account; premiums (Plus 1500 member-and-children 86.71 + Family 1500 rider 12.60 = 99.31 from 2024-01; Premier 2000 member-and-children 110.03, + 12.60 from rider effective 2025-01 = 122.63); payments before due date, paid-through dates, balances; claim-line coinsurance (preventive 100 in and out of network on Plus 1500 / Premier 2000), deductible waived on preventive, member share (OON submitted - plan; in-network allowed - plan); accumulator postings (Plus 1500 annual maximum applies to preventive -> every w0 paid line posts its plan payment on the decision date; Premier 2000 does not -> no w1 postings; no pediatric EHB treatment because both enrollments are individual_application, not exchange); provider agreement types, effective dates (first of month after decision), turnaround, liability limits; remittances on the 7-day run cycle summing the in-network lines. Allowed amounts are record-level (no per-code fee schedule is published) and are not re-derivable.

Members the owning docs would not produce:

| id | Row(s) | What the published docs give | Moves a scored value? |
|---|---|---|---|
| S2 | w0 dental_claim_line 7e039e9a (Aksel, D0330 2026-10-06, Engstrom, PAID 118.00); collateral: accumulator posting 47274d96 (118.00), remittance 2e20c067 (196.00) | Dental PPO Plans frequency schedule: Plus 1500 "Full-mouth series or panoramic film interval (months) 60", counted "from the last paid one"; the D0330 of 2025-07-28 (6e0ed449, paid 96.00) is the last paid one -> line denied for the frequency limit, plan payment 0.00; no 118.00 posting; remittance 78.00 | **Yes — task 0** carried payment: records offset 196.00 -> 0.00 ("an evaluation line (D0150) only ... nothing"); amount 237.92 -> **355.52** |
| S3 | w1 dental_claim_line cb196395 (Joanna, D0150 2026-09-15, Hennessey, PAID 78.00) and 9dd40dc3 (Joanna, D0330 2026-11-10, Hennessey, PAID 92.00); collateral: remittances 277a4d19 (78.00) and 2f2d8001 (92.00) | Premier 2000 "Oral evaluations per benefit period 2" (D0120 2026-01-08 and D0150 2026-03-12 already paid) -> D0150 of 2026-09-15 denied; Premier 2000 panoramic interval 36 months after the paid D0330 of 2026-03-12 -> D0330 of 2026-11-10 denied; neither remittance would exist | **Yes — task 1**: takeover allowed_case_fee 2971.21 -> **3049.21** (no paid D0150 records visit); repayment 368.43 -> **340.51** (fee change and no paid D0330 progress record); months_remaining 23 unchanged |
| S4 | w0 16 and w1 22 billing_invoice_issued rows dated the 12th for coverage months following 28/29/30-day months (e.g. INV for 2026-03 dated 2026-02-12, docs 2026-02-09; 2026-12 dated 2026-11-12, docs 2026-11-11); w1 has no invoice for coverage month 2026-12 although its issue date 2026-11-11 precedes frozen_time 2026-11-20 | Premium Billing Accounts schedule: Direct Bill Monthly invoice lead time 20 calendar days before the due day 1 | No |
| S5 | provider_agreements b3224697 (Engstrom: credentialing_decision_date 2018-04-02, recredential_due_date 2027-05-01) and 1d597c16 (Hennessey: 2015-03-18, 2027-04-01) | Recredentialing cycle 36 months; "A completed recredentialing refreshes the license, liability and decision dates on file" -> a due date of 2027-05-01 / 2027-04-01 implies decision dates 2024-05-01 / 2024-04-01; the stale decision dates would otherwise put the due dates in 2021 / 2018 and end both agreements by credentialing lapse | No (the record's due date and status govern; both agreements in force on every relevant date) |

Earlier "conditional" items: none were recorded in revision_1. Vision-dependent items: none (no vision rows in either world).

Closing: KB parts unchanged — runtime PASS, bijection PASS, dependency form PASS for both tasks. S2 and S3 are seed misses that move scored values (if the seeds are corrected to what the dental documents produce, the GT values move as stated); S4 and S5 are non-moving seed misses.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=S2,S3,S4,S5

## revision_3

Gated seed-only re-audit (/tmp/erl0070_coord/kb_reaudit_gate.txt). Upstream `tail -n 1 .../policy_task/orthodontic_benefits/_difficulty.md` = `VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN` (as required). Snapshot `/tmp/erl0070_coord/kb_snapshot.sh orthodontic_benefits ortho` 2026-10-20T04:34:36: `DOCS OK`; `0.json 22 0 True / 1.json 19 0 True / TRACEABILITY OK / non-unlock misses: 0`; EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; src sha256 7fb0c4d97ce747af ae8fd16b76be984b. docs/ortho unchanged (f95a665e3febf6b8); runtime views identical to the task JSONs' user_scenario / frozen_time.

Blind re-derivation (frozen in runtime_context revision_3 before reveal) on the changed worlds: task 0 move fee 1331.22, payment 237.92 (position 5, 2026-12, practice); task 1 takeover fee 2971.21 with 23 months, repayment 368.43 against the initial payment — all equal to GT; no scored value moved.

Previous-round items:
| id | Status | Evidence (db_query.py, revision_3 dumps) |
|---|---|---|
| S2 | closed | w0: line 6e0ed449 (D0330 2025-07-28) and posting 72fec732 removed; D0330 7e039e9a of 2026-10-06 is the first paid panoramic (Plus 1500 interval 60 months) -> payable; postings 52 / 61 / 78 / 118 = plan payments on decision dates; remittance 196.00 = 78 + 118 |
| S3 | closed | w1: 2026 evaluations D0150 03-12 and D0150 09-15 (2 = Premier 2000 limit); D0120/D0274 now 2025-11-04 (one each in 2025); prior D0330 2023-08-15 -> D0330 2026-11-10 beyond the 36-month interval; remittances 78.00 (09-25) and 92.00 (11-13) |
| S4 | closed | every invoice now dated 20 calendar days before the 1st of its coverage month (w0 39, w1 54 invoices, zero mismatches); w1 2026-12 invoice present (2026-11-11, 122.63, unpaid, not yet due) and balance_due 122.63 = invoices less payments, as "The balance due" defines; w0 next invoice 2027-03-12 is after frozen_time |
| S5 | closed | Engstrom decision 2024-05-01 -> due 2027-05-01; Hennessey decision 2024-04-01 -> due 2027-04-01 (36-month cycle) |

Full re-price of every other-product row in both worlds against the published docs: premiums 99.31 (Plus 1500 member-and-children 86.71 + rider 12.60) and 110.03 / 122.63 (Premier 2000 member-and-children, + rider from 2025-01); payments before each due date, paid-through dates, balances; claim lines (frequency and interval limits, preventive coinsurance 100 in and out of network, deductible waived, member share rule, timely filing, coverage in force); accumulators (Plus 1500 posts preventive, Premier 2000 does not, no pediatric EHB on non-exchange enrollments); dental enrollment effective dates; provider agreement terms, liability limits, 7-day remittance runs. No member the owning docs would not produce. No dhmo, group, savings or vision rows (vision still unpublished; nothing conditional).

No new defect, nothing regressed; S1 remains a coordinator DECISION and is not re-raised.

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=NONE
