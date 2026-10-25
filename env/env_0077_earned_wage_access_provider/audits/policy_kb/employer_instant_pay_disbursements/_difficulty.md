# KB-layer audit — employer_instant_pay_disbursements (product disburse), closing checklist

## revision_1 (2026-10-23)
Auditor: erl-kb-doc-policy-audit, independent of the renderer and the policy auditor. Brief: /tmp/erl0077_coord/kbaudit.md (followed line by line).

### Entry conditions (kb_snapshot.sh 2026-10-23T05:34:37, cited not re-run)
- `check_docs.py disburse => DOCS OK`; 59 files in docs/disburse.
- `check_traceability.py employer_instant_pay_disbursements => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)` (coordinator's post-publication run).
- Instantiation gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (0.json 27/27, 1.json 28/28), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Source sha256 (extended.yaml, task_tools.py, 0.json, 1.json): d2f0f6cc199a 71cf5918daf4 caeea6f41b87 e3d1dbe9fa03. Runtime views: 0 c13138418241ffc9, 1 68ebb99cd882651c.
- Policy-side verdict: `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN`.
- Claimed scope: categories [disburse], 12 event types of the claim; M=2.
- Blind freezes: runtime_context/.../0.md sha256 b2ca6ef8…6033c27, 1.md sha256 a21139ab…c16ff81, written before any source/GT read. DB side blind (db_query.py tool-shaped returns only).
- contamination_disclosure: blueprint `summary` text adjacent to the claim was on screen (charter policy ids only, no figures/factors/tools); no effect judged.

### Per-task verdicts
| task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 (Kittredge Hall closure: 7.90, 28.41) | PASS | PASS | PASS |
| 1 (Larkspur funding deposit: 6.77, 2050.00, 1700.00, 966.06) | PASS | PASS | PASS |

### Difficulty-wide sweeps
- Variant figures: all 48 parameters × 6 tiers compared with the tariff/limit/prefund/returns/fee-credit/term/portal/delivery tables — no mismatch.
- Base policies (disburse_agg_multi_holding, disburse_evt_payout, disburse_card_destination, disburse_evt_fees, disburse_ewa_bundle, disburse_evt_prefund, disburse_evt_returns_recalls, disburse_evt_fee_credits, disburse_volume_review, disburse_lifecycle, 8 measures, lifecycle transitions): every in-force clause carried; no added obligation.
- Retired surface (8 distinct superseded clauses, all marked "no longer in force", none dropped, none retired without an overwrite): evt_fees §1 (tier for fees), §4 (monthly platform fee), §5 early-closure part; ewa_bundle full-month reduction, Payroll Card "no discount here"; prefund Article 3 (auto replenishment); lifecycle T5 (closure/recall roles), T6 (settings change). In-force remainders of the same policies kept as clauses in force.
- Prerequisite sentences: 5 edges, all state form, each verbatim and single-homed on its blocked side; no other policy's document carries one.
- Tool names: each of the 6 task tools appears only in its own invocation document.
- Leak check: no scored value (7.90, 28.41, 6.77, 2050, 1700, 966.06, 189.43) in any doc or unlock schema.
- Cross-product: factors read only program and paycard records (both published); seeded rows are states those products' published rules produce (agreements live, renewal = signed + term, headcount within program tier band; paycard program opens in contracted status). No figure depends on the unpublished access/card corpora — nothing CONDITIONAL.

### KB defects (renderer)
None.

### Source-side items (instantiator)
None.

### Observations (policy-side / base, no verdict effect)
- O1 (base, verbatim): service_status_and_closure_rules T4 "an early closure fee applies under the fee terms" points at the §5 early-closure part that disburse_ext_early_closure_fee retired; the base sentence is in force and rendered as it stands (coordinator-logged base class).
- O2 (parameter_schema): the tariff's column definition of the EWA bundle discount ("for a month the employer's Earned Wage Access program was live on every day") is the parameter_schema meaning, which describes the retired full-month rule; it labels a figure, the factor docs state the application rule. Carried verbatim.
- O3 (base): the only business-day definition ("Monday through Friday excluding Federal Reserve holidays") sits in the recall-window rule; task 1's fee debit day 2026-04-03 is Good Friday, a business day under that definition. KB faithful to the source.
- O4: two scope sentences in factor docs refer to the other platform-fee policy's rule ("reduced under the rule for completed billing months" / "for the closing month"); source-verbatim overwrite text, not a rendering addition.

### Closing
All M=2 tasks have frozen blind_answer + gt_comparison and source_to_kb / kb_to_source / dependency_form; all three parts PASS per task. Gate lines as in the entry snapshot (check_traceability not re-run per brief).

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_2 (2026-10-23, cross-product re-judge; revision_1 text untouched)
Entry snapshot re-run (kb_snapshot.sh 2026-10-23T06:58:54): `check_docs.py disburse => DOCS OK`; `check_traceability.py employer_instant_pay_disbursements => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`; EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; 59 files in docs/disburse; source sha256 d2f0f6cc199a 71cf5918daf4 caeea6f41b87 e3d1dbe9fa03 (unchanged from revision_1); runtime views c13138418241ffc9 / 68ebb99cd882651c (unchanged). Corpora now published: program 55, paycard 47, access 57, card 59, save 16, loan 16 docs.

### (0) Round-1 REDs
None existed; nothing to close. No regression: sources and docs/disburse are byte-identical to revision_1, so all six scored values (7.90, 28.41; 6.77, 2050.00, 1700.00, 966.06) and every revision_1 part-verdict stand.

### (1) CONDITIONAL figures
None were graded CONDITIONAL in revision_1 (no factor reads access, card, save or loan records). Nothing to re-judge.

### (2) Seeded rows of other products, re-priced against their published docs
Seeded tables. Task 0: customers 1, program_agreements 1, paycard_programs 1 (+ disburse rows). Task 1: customers 1, program_agreements 1 (+ disburse rows). No access, card, save or loan row and no program or paycard ledger row (billing, settlements, census, change requests, funding, kits) is seeded in either world.
- T0 program_agreements 375fa562… (Paystride Program Growth, live): headcount 228 is inside the Growth band 50–249 (program_tier_lineup); 36-month term ≥ Growth minimum 12 (term_renewal_and_termination_schedule); renewal 2028-02-03 = signed 2025-02-03 + 36 months (one_agreement_per_employer Clause 2); go-live 2025-03-10 after signing; access percentage 40 = Growth default, inside 10–50 and a multiple of 5 (access_percentage_and_change_limits); 1 payroll group ≤ 2 included (employer_price_schedule); remittance ach_debit_authorization is Growth's only allowed method (deduction_and_remittance_timetable); fee_model employer_paid valid; both receivables 0.00, consistent with no seeded schedule. No renewal has fallen due (renewal date in the future); no termination notice. Consistent.
- T0 paycard_programs dfa39930… (Standard, contracted, signed 2026-10-06): opens contracted with zero funding balance and zero kit inventory (one_program_per_employer Clause 2), as seeded; employer_ach_credit is an accepted Standard method (funding_deadlines_and_methods); contracted -> live only when the first payroll batch posts (program_lifecycle L1), so no launch_date is correct with no batch on record. The 10-business-day launch target is a Paystride commitment, not a status change. Monthly program fees are billed only for months the program was live or suspended (program_fee_billing (c)), so a contracted program owes no fee and a zero funding ledger is complete. Consistent.
- T1 program_agreements bc4d6ee9… (Paystride Program Professional, live): headcount 310 is inside 250–999; 24-month term ≥ Professional minimum 24; renewal 2027-04-21 = signed 2025-04-21 + 24 months; access 50 = Professional default and maximum; 3 payroll groups ≤ 4 included; ach_debit_authorization allowed; employer_paid; receivables 0.00. Consistent.
- Disburse ledgers reconcile to the service records (T0 2359.03, T1 190.19). Every payout goes to an external debit card or a bank account, so no card load (card product) is implied. No per-disbursement fee is owed (payout positions are inside the Growth 500 and Core 100 allowances). T1's balance first fell below the 250.00 alert on 2026-04-02; on that day a replenishment debit was already barred by the floor gate, and the March platform fee was not due until 2026-04-03, so the opening state is one the published rules produce.
- Accepted residue (brief): census, billing and deduction-schedule rows behind the live agreements, the workers' Access plans, the payees' card accounts and the paycard entry-threshold cardholder count are not seeded. No gold step reads them.

### (3) Writes another product's docs call owed at once that could move scored reads
This difficulty's scored computations read only these fields from other products: program status, go_live_date, renewal_date, fee_model, variant_name, eligible_headcount, payroll_group_count, remittance_method; paycard status, signed_date. None of these can be moved mid-conversation by a write that is due at once in either world:
- program suspension needs an item past due for the suspension period, and none is seeded;
- rebanding needs 3 consecutive out-of-band censuses, and none is seeded;
- renewal is a future date in both worlds;
- termination, fee-model, payroll-group and remittance changes are employer requests, not owed writes;
- the paycard launch needs a posted batch, suspension applies only to a live program, and a contracted program owes no monthly fee.
Card, access, save and loan rules that mention instant pay disbursements (card load fees, card tier reviews, card pay periods, load reversal debits) act on card accounts, and none is seeded. Finding: none.

### Verdict
KB defects: none. Source items: none. Observations O1–O4 of revision_1 unchanged.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE
