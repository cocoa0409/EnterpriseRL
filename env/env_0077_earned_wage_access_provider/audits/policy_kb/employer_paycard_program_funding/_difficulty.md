# KB-layer audit — employer_paycard_program_funding (product paycard, M=2)

## revision_1

- Auditor: independent KB-layer auditor; blind answers frozen 2026-10-23T01:25-01:27Z, source revealed 01:35Z.
- Entry snapshot (/tmp/erl0077_coord/kb_snapshot.sh employer_paycard_program_funding paycard, 2026-10-23T01:21): `check_docs.py paycard => DOCS OK`; `check_traceability.py employer_paycard_program_funding => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`; EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 54/54, 1.json 63/63); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; docs/paycard 47 files, sha prefixes ccc500ad4d68 edc5cf3b484f 08696a741764 78306732c47b; runtime views 0 a245b6b1f9286b62, 1 eb302384baaecdbf. Policy verdict `VERDICT revision_1: task0=PASS task1=PASS charter=CLEAN`. Docs unchanged during the audit (concatenated sha ce6dd8eb9f9b8ade at start and end); gates not re-run (no change, and check_traceability is coordinator-only per brief).
- Claimed scope: blueprint claim of this difficulty (category paycard; event types incl. paycard_funding_receipt, paycard_fee_debit, paycard_reinstate, paycard_termination_notice) = the four extended policies audited.

| Task | Runtime blind | Bijection | Dependency form | Verdict |
|---|---|---|---|---|
| 0 (restoring wire <- late funding fee) | PASS (90.00 / 22058.21 = GT) | PASS | PASS | RED — KB-1 only |
| 1 (termination notice <- reinstatement) | PASS (48.60 / 407.50 = GT) | PASS | PASS | PASS |

### KB defects (renderer)
- **KB-1** docs/paycard/repeated_lateness_multiplier_f09c7d7b.json, closing line "A hypothetical late-fee charge of 60.00 multiplied by 1.5 is 90.00." — a worked-example figure equal to task 0's scored late funding fee (fee_amount_usd 90.0). Leak-hygiene class (doc worked examples never reuse scored values); semantics and ladder otherwise exact. No other example/schema figure equals a scored value (checked 90.00, 22058.21, 48.60, 407.50, balances and ids).

### Source-side items (instantiator)
- None. Seeds checked against the published extended rules: every historical priced row reproduces (task 0: 07-31 late fee 75.00, 09-16 restoring wire 189301.19; task 1: 04-24 reinstatement fee 61.75, 08-25 wire 125216.56, 10-19 wire 138614.75, kit fee 75.00; monthly fees per schedule); balances replay to the record (7494.13, 24290.66).

### Notes (no verdict)
- N-1 Computation documents carry the source rule's generic assembly sentence ("... multipliers ... amounts added ... before the rounding") — XF A2 design, only legitimate home; accepted residue.
- CONDITIONAL: the Access-bundle/retention x0.8 tiers (task 0 late fee; task 1 reinstatement fee and ETF) rest on program_agreements rows (program product docs unpublished). Re-judge once program is published.
- Policy-side: task 1's reinstatement wait "once its funding balance has been restored" is satisfied with zero margin (balance 24290.66 = restoration reserve 24290.65875 -> 24290.66); every reading (restoration reserve, base reserve, non-negative balance) agrees, so the solution stays unique.

### Closing checklist
- Audit files 1:1 with tasks: runtime_context/<D>/0.md, 1.md; policy_kb/<D>/0.md, 1.md — yes.
- Every normative atom of the four policies entailed by docs/paycard; both prerequisite sentences verbatim, state form, only on the blocked side; every factor ladder complete and findable from record words; no other problem's tool, route or chain stated — yes.
- Open: KB-1.

KB-VERDICT revision_1: task0=RED task1=PASS kb=KB-1 src=NONE

## revision_2

- Coordinator gate: `RENDER round 2: DOCS OK`. Snapshot re-run (execute-only): DOCS OK; TRACEABILITY OK (misses 0; non-unlock 0); 7 instantiation gates OK; source hashes and runtime-view hashes unchanged; docs/paycard 47 files, corpus sha now 22a0bab52806ab8f.
- KB-1 closed (example now 58.40 x 1.5 = 87.60); no figure equal to a scored value anywhere in the corpus.
- Round-2 changes are confined to hypothetical worked examples (verified by text diff / read of all 47 docs); every new example re-computed and correct; no normative change, so no regression and no new defect.
- Re-audit blindness: not blind (auditor saw GT in revision_1; disclosed in runtime_context revision_2); acceptable because the visible normative surface is identical to the one the revision_1 blind answer was frozen on.
- CONDITIONAL items unchanged (Access x0.8 tiers rest on the unpublished program product).
- Source-side items: none.

| Task | Runtime | Bijection | Dependency form | Verdict |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_3 — cross-product re-judge

- Snapshot re-run (execute-only): `check_docs.py paycard => DOCS OK`; `check_traceability ... => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`; EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; source sha prefixes and runtime-view hashes unchanged; docs/paycard 47 files, sha 22a0bab52806ab8f (unchanged since revision_2). Published corpora: program 55, access 57, card 59, disburse 59, save 16, loan 16, paycard 47.
- No round-2 RED was open; nothing regressed (paycard corpus byte-identical to revision_2).

### (1) CONDITIONAL figures re-judged
- Product identity: program_tier_lineup "The Paystride Earned Wage Access Program Agreement is offered in six tiers" (Starter, Growth, Professional, ...), so the rows 'Paystride Program Professional' (task 0) and 'Paystride Program Growth' (task 1) are the agreement the paycard factor docs name; fee models employer-paid / employer-sponsored / worker-paid are the program docs' own (employer_price_schedule, termination_fee_monthly_charge_lines).
- Status 'live' with a go-live date: program_lifecycle_and_termination "the program goes live when the first payroll file validates"; nothing in the program, access, card, disburse, save or loan docs conditions "live" on any record absent here.
- Task 0 late fee x0.8 (live today, go-live 2026-10-09 on/before pay date 2026-10-09, employer_sponsored) -> **PASS**. Task 1 reinstatement x0.8 (live, worker_paid) and ETF retention x0.8 (live, go-live 2026-10-19 = 0 whole months) -> **PASS**. All four scored figures (90.00, 22058.21, 48.60, 407.50) are final.

### (2) Other-product seeded rows, re-priced (exhaustive: every finder run with empty filters in both worlds)
Each world holds exactly one other-product row, its program_agreements row; program_billing, program_census, program_settlements, program_change_requests, access_*, card_*, disburse_*, save_*, loan_* are empty.
| World | Field | Published rule | Result |
|---|---|---|---|
| 0 | tier Professional, eligible_headcount 342 | band 250-999 (program_tier_lineup) | OK |
| 0 | term 36, signed 2026-08-10, renewal 2029-08-10 | renewal = signed + term (one_agreement_per_employer); min term 24 | OK |
| 0 | configured_cap_percent 50 | Professional 10-50, multiple of 5, default 50 | OK |
| 0 | payroll_group_count 2 | 4 included, no additional-groups line | OK |
| 0 | remittance ach_debit_authorization | allowed (deduction_and_remittance_timetable) | OK |
| 0 | receivables 0.00; no billing rows | invoice in arrears; Aug-Sep not live/suspended/terminating -> no platform fee; implementation fee waived (term 36 >= 36); October billed in November | complete |
| 0 | go-live 2026-10-09 vs 30-business-day target | missed target credit = 10% of implementation fee = 10% of 0.00 (waived) -> nothing to seed | OK |
| 1 | tier Growth, eligible_headcount 161 | band 50-249 | OK |
| 1 | term 24, signed 2026-09-08, renewal 2028-09-08 | renewal rule; min term 12 | OK |
| 1 | configured_cap_percent 40 | Growth default 40 | OK |
| 1 | payroll_group_count 1, ach_debit_authorization | 2 included; allowed | OK |
| 1 | receivables 0.00; no billing rows | September not live; Growth platform fee 0.00; implementation fee 500.00 waived (term 24 >= 24); go-live credit 0% | complete |
- Paycard ledgers (own product, re-checked against all published docs): every monthly fee on the 5th Fed business day of the next month (July: 3 July 2026 is a Fed business day, so 7 July is correct), amounts per package; kit fee/shipping per Standard tariff; returned funding fees per package; late fee (task 0, 2026-07-31) 75.00 and reinstatement fee (task 1, 2026-04-24) 61.75 reproduce the extended rules; every historical restoring wire reproduces exactly; balances replay to 7494.13 and 24290.66; no regular batch other than task 0's 2026-10-09 batch was funded after its deadline (checked against business-day deadlines incl. Memorial Day, Juneteenth, Labor Day).
- Accepted residue (rows no gold step reads, cannot be seeded): the workers' card accounts and card loads behind each batch's card_count and behind the active-card fee counts (card product); census rows and Access plans of the live agreements (program/access products). Gold reads only card_count on paycard batch rows and the agreement's status/go-live/fee model.
- Observation (not a finding): task 0 regular batch with pay date 2026-06-19 (Juneteenth, a Fed holiday) posted that day from funds received 2026-06-18; no published rule bars a holiday pay date and the batch is priced by nothing scored.

### (3) Owed-at-once writes from other products
- program: invoice lines are billed monthly in arrears on the issue day (nothing due on 2026-10-13 or 2026-10-20); suspension needs a past-due schedule/shortfall (none); a fee-model or access-percentage change takes effect only on a future pay period (status and fee_model unchanged today); termination notice is the employer's own act (not requested). None can move the agreement's status, go-live date or fee model mid-conversation.
- card: refused-load credit-backs and card-side writes need card accounts/loads (none exist); card account opening writes no paycard funding row.
- access / disburse / save / loan: no holdings in either world; nothing owed.
- Result: no mid-conversation write of another product can move any scored read (late-fee counts, reinstatement-fee counts, funding balance, program status, agreement status/go-live/fee model).

| Task | Runtime | Bijection | Dependency form | Cross-product | Verdict |
|---|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS | PASS |

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=NONE
