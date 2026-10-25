# KB-layer audit — employer_program_settlement_and_changes (product program), closing checklist

## revision_1 (2026-10-23)

### Entry conditions (cited from `/tmp/erl0077_coord/kb_snapshot.sh employer_program_settlement_and_changes program`, 2026-10-23T05:12:22)
- `check_docs.py program => DOCS OK`; coordinator's post-publication `check_traceability.py employer_program_settlement_and_changes => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)` (not re-run by the auditor, per brief).
- EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (0.json 23/23, 1.json 388/388), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Docs: 55 files in docs/program; runtime views 0 = d4834b0d7aa65077, 1 = 7e52c1a390562bef.
- Policy verdict: `VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN`.
- DB access path: db_query.py tool-shaped finders (blind on the DB side for both tasks).

### Per-task part verdicts
| Task | Runtime blind audit | Two-way scan | Dependency form |
|---|---|---|---|
| 0 (SLA claim ← per-worker billing-error credit) | PASS (3030.38 / 320.11 derived blind, identical to GT) | PASS | PASS |
| 1 (termination notice ← return late charge ← shortfall late charge) | PASS (362.06 / 1659.45 / 25115.65, due 2026-12-04, derived blind, identical to GT) | PASS | PASS |

Every factor ladder (28 factors over 5 policies) is carried in full in its own document, findable from record words; every computation document yields a definite fall-back different from the answer (0.00, 106.25, 156.01, 575.23, 17700.00 — each equal to the GT baseline_result); all three prerequisite sentences stand verbatim, state form, on the blocked side only. Cross-product reads (paycard: Payroll Card Program record, funding returns) rest on published corpora; nothing depends on unpublished disburse/access/card docs. Seeded history re-priced spot-checked against the published rules (task 0 SLA credits 91.64 and 327.62; task 1 SLA credits 714.46 and 1015.51 and late charge 35.11) — all reproduce.

### KB defects (renderer's)
None.

### Renderer notes in render_r1.md — classification
1. Zero termination fee booked as a 0.00 line — **src (S-1)**. The KB carries both source sentences faithfully (monthly_program_invoice "A line that comes to zero is not billed"; written_termination_notice "its amount is fixed and billed on the day the notice is accepted"; tool effect "bills the early termination fee as one invoice line"). The conflict is source-side: the extended replaced_by and the tool body (`ctx.create(... amount=amt ...)` unconditionally) vs. the in-force base clause, on Starter/Growth (0 fee months) or when no 30-day period is left. Untriggered in both tasks.
2. No platform-fee line on Starter/Growth (0.00 platform fee is not billed) — **src (S-2)**. The SLA rule's credit base and "pointing to that month's platform_fee line", and the claim tool's required `related_entry_id`, assume a line that the base rule never bills on those tiers, while covered_fee_lines can still give a positive credit there; the rule states no outcome. KB mirrors the source; untriggered.
3. Whole-month look-back windows — **not a KB defect; source residue noted as S-3 (low)**. The KB sentence "A whole month from an entry date is reached on the same day of the month as that entry date" (8 factor docs) is the ordinary meaning of "whole months have passed", is the rule set's own explicit convention for other counts, and matches the compute; it does not close the month-end sub-case (entry on the 29th–31st against a shorter month), which the source rules also leave unstated (XF B1 class). No seeded date in either task lies near such an edge.
4. Two bindings (returned amount; first day of the claim month) defined in a factor document's prose — **not a defect**. Each is used by one factor only and the KB defines it in that factor's document, which is the XF A4 placement; the only mismatch is hidden meta `covers`, which is not a criterion.

### Source-side items (instantiator's)
- S-1 (low, untriggered): ETF of 0.00 — extended replaced_by + sign_termination_notice_c67c1163 body always book an `early_termination_fee` line, against the in-force program_evt_monthly_invoice clause "A line that comes to zero is not billed"; no declared overwrite or carve-out.
- S-2 (low, untriggered): program_ext_sla_claim_credit on a tier whose platform fee is 0.00 (Starter, Growth) — the credit must point to "that month's platform_fee line" that the base never bills; rule and tool give no outcome for that world.
- S-3 (low, untriggered, coordinator may accept as residue): month-end convention for "fewer than N whole months have passed to today" windows (shortfall/return frequency, prior charges, liable history, returned payments, breach recurrence/relief, ETF line window) and for the day-of-month whole-month counts is not stated in the rules (XF B1).

### Policy-side design notes (no verdict)
- N-1: computation documents carry the rule's generic assembly sentence (XF A2/A3), which tells a reader that adjustments exist; source-mandated, not a rendering addition.
- N-2: the three sibling paycard-scope replaced_by texts sit in the card_bundle_depth factor doc, the SLA computation doc and the termination_bundle factor doc; source text, no tool/route/factor named; placement only.

### Closing checklist
- Audit files one-to-one with tasks: runtime_context/…/0.md, 1.md (blind_answer frozen before reveal; gt_comparison appended), policy_kb/…/0.md, 1.md (source_to_kb, kb_to_source, bijection_verdict, dependency_form). No contamination.
- Final-form gates: check_docs DOCS OK and check_traceability TRACEABILITY OK as cited above (docs unchanged since the snapshot: hash fbc72b9a3a5191be read before and after the audit).

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=S-1,S-2,S-3

## revision_2 (2026-10-23, re-audit after RENDER round 2)

### Entry conditions
- `tail -n 1 audits/render_source/employer_program_settlement_and_changes/RENDER.log` = `RENDER round 2: DOCS OK`.
- Snapshot re-run by this auditor (`/tmp/erl0077_coord/kb_snapshot.sh employer_program_settlement_and_changes program`, 2026-10-23T05:54:51):
  - `check_docs.py program => DOCS OK`
  - `check_traceability.py employer_program_settlement_and_changes => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`
  - EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 23/23, 1.json 388/388); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK
  - source sha256 8edfe41cb636 0afad5185ffe 267211c2dabb 69a9f9ceede7
  - runtime views unchanged (d4834b0d7aa65077, 7e52c1a390562bef)
- Docs: 55 files, content hash ecd4e7fd2a924db1. I diffed them against the round-1 text capture: 24 hunks, all listed in 0.md/1.md revision_2.

### Round-1 items
- S-1 (zero ETF line): CLOSED. Rule, replaced_by and tool body (no line at 0.00, with a zero receipt) all agree with the base rule "A line that comes to zero is not billed"; the docs carry it.
- S-2 (no platform-fee line): CLOSED. A rule sentence and the compute gate `platform_lines > 0 and platform_net > 0` say no credit is given; the SLA computation doc carries it.
- S-3 (month-end whole-month convention): CLOSED in every rule that counts whole months, and in the 12 docs that render them. Checked against the DSL `MONTHS`/`within_months`.

### New and regression checks
- New source content, the 25.00 de minimis on the shortfall late charge and in the return policy's prerequisite sentence, is carried losslessly. The prerequisite sentence is verbatim and single-homed.
- GT, seeds and scored values are unchanged (both tasks re-derived against the new text).
- No KB defect found. Notes N-1 and N-2 are unchanged and carry no verdict.

| Task | Runtime | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

Contamination disclosure: revision_2's runtime check is a re-derivation by an auditor who had already seen the source in revision_1, not a fresh blind audit.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_3 (2026-10-23, cross-product re-judge after every product published)

### Entry snapshot (re-run by this auditor: `/tmp/erl0077_coord/kb_snapshot.sh employer_program_settlement_and_changes program`, 2026-10-23T06:59:03)
- `check_docs.py program => DOCS OK`
- `check_traceability.py employer_program_settlement_and_changes => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`
- EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE: all OK
- source sha256 8edfe41cb636 0afad5185ffe 267211c2dabb 69a9f9ceede7 (= revision_2)
- program docs 55 files, content hash ecd4e7fd2a924db1 (= revision_2)
- runtime views unchanged
- Published corpora: access 57, card 59, disburse 59, loan 16, paycard 47, program 55, save 16.

### (1) CONDITIONAL figures
None were graded CONDITIONAL in revision_1 or revision_2. Every cross-product input (paycard program record; paycard funding returns) already rested on the published paycard corpus. Re-read against the paycard docs:
- package names "Paystride Paycard Program Standard/Advantage" fall in the "any other package" tier of card_bundle_depth and termination_bundle;
- "a funding return pointing to it" (funding_payments rule 5) is the row kind returned_payment_history_charge_form counts.

All five scored figures stand: 3030.38, 320.11, 362.06, 1659.45, 25115.65.

### (2) Other-product seeded rows, re-priced
Inventory of seeded tables:
- Task 0: customers, program_* tables, paycard_programs (1).
- Task 1: customers, program_* tables, paycard_programs (1), paycard_funding (125).

No access, card, disburse, save or loan rows are seeded in either world. The Access plans behind the deduction schedules, the card accounts, the kit orders and task 0's paycard funding ledger are absent. These are rows no gold step reads, the accepted residue.

**Task 0, paycard program 0d63eee0**
- Standard package; signed 2026-05-29; launched 2026-06-12, on the 10th business day, within the Standard launch target of 10; live.
- Funding method employer ACH credit, accepted under Standard.
- Program-side reads agree: July–September platform fee lines carry the 15 percent bundle discount (launched by 1 July, still open); June is undiscounted.
- funding_balance 7304.00 has no ledger behind it (residue).
- No finding.

**Task 1, paycard program 48a27548 (Advantage), program record**
- Signed 2025-02-24; launched 2025-03-21, the 19th business day, within the Advantage target of 20; live.
- ACH debit authorization accepted; entry threshold 250 met (382+ cards).
- Program side: the April 2025 onward platform fee lines at 2360.00 carry the 20 percent bundle discount; January–March 2025 at 2950.00.

**Task 1 funding ledger: what reconciles**
- All 125 rows re-priced against monthly_fee_schedule, program_fee_billing, funding_deadlines_and_methods, funding_payments, funding_charges_schedule, payroll_batch_loading, prefunding_reserve, reserve_standards, program_lifecycle, late_funding_fee_debits and lateness_timing_charge.
- Running balance reconciles exactly to the record's funding_balance 24710.50.
- 42 regular batches, every 14 days, on business days. Each receipt is an ACH debit initiated exactly 2 business days before the pay date (Advantage lead), holidays included (e.g. 2025-11-25 for 11-28, 2025-12-23 for 12-26). Each equals its batch, except the launch receipt, which carries a 32000.00 prefund.
- The 5 percent reserve of the 3-batch average holds after every batch.
- 19 monthly_program fees (199.00) and 19 active_card fees (0.45 × the month's largest batch card count), one per month from 2025-03 to 2026-09, none missing.
- Funding return c327e0ca (2026-08-21, of receipt 9ee08949): returned_funding fee 30.00 (Advantage), pointing to it and carrying its pay date.
- One return in 90 days, under the Advantage suspension count of 3. The negative balance lasted 1 business day, under the period of 5. Status live is consistent.

**Task 1 funding ledger: findings**
- **S-4 (task 1, paycard ledger incomplete):** the late funding fee for the 2026-08-21 regular batch 7100752c is missing.
  - Two funding receipts are booked for pay date 2026-08-21: 9ee08949, an ACH debit on 08-19 that was returned, and 50283945, a wire on 2026-08-24 11:20 whose `pay_date` is 2026-08-21.
  - The published paycard rules take a batch's funding arrival as "the latest entry date among the funding receipts booked for its pay date" (lateness_timing_charge).
  - The Advantage deadline is 2026-08-20 15:00. So the batch's funds arrived after the deadline, and for a batch that is not the most recent the base rule restated in late_funding_fee_debits applies: "the batch is charged the package's late funding fee", 50.00.
  - The paycard restoring-wire hub confirms the paycard corpus treats such a batch as one whose funds arrived after its deadline, since it waits on "the late funding fee owed for every regular payroll batch whose funds arrived after its funding deadline".
  - No `late_funding` fee row exists, so the seeded wire is not a state the published rules produce as it stands.
  - Two readings both fail. The wire is not a restoring payment: the restoring-wire tool books receipts "tied to no pay date", and its amount equals the returned 400251.22 rather than reserve less balance. If it is treated as batch funding, the 50.00 fee is missing.
  - Secondary plausibility point: both the return and the batch carry entry_time 00:00 on 08-21. If the return preceded the 06:00 posting, "a batch the balance cannot cover posts no load until it is funded" would put the batch on 08-24.
  - Not gold-moving: returned_payments_method counts only `paycard_funding_return` rows, and termination_bundle reads status, launch date and package.
- **S-5 (task 1, paycard fee debits misdated):** monthly fees are debited "on the fifth business day of the following month" (monthly_fee_schedule; program_fee_billing (c)).
  - June 2025 fees (199.00 and 175.50, 390 cards) are dated 2025-07-07, but 4 July 2025 is a Federal Reserve holiday, so the 5th business day is 2025-07-08.
  - August 2025 fees (199.00 and 188.10, 418 cards) are dated 2025-09-05, but 1 September 2025 is Labor Day, so the 5th business day is 2025-09-08.
  - The other 17 months are dated correctly, including 2026-07-07 (3 July 2026 is a Federal Reserve business day) and 2026-09-08.
  - Not gold-moving.
- **S-6 (task 1, own product, found while cross-checking program rows priced from paycard):** the August 2025 invoice lines (platform_fee bc61e2f9, sponsored_instant_fees c762079e, sponsored_nbd_fees 3345d84e) are dated 2025-09-03.
  - The invoice is "issued on the tier's invoice issue business day of the following month" (3rd); with Labor Day on 1 September 2025 that is 2025-09-04.
  - Due dates (2025-10-18) follow the seeded entry date.
  - Every other program invoice line and settlement date in both worlds checks: invoice dates, due dates, deduction delivery leads, schedule due dates, notice cure dates.
  - Not gold-moving: the termination fee-lines window starts 2026-07-21, and no factor reads 2025 entry dates at day precision.

### (3) Owed-at-once writes of other products mid-conversation
The only other-product reads behind scored figures are paycard_programs status, launch_date and variant_name (both tasks) and paycard_funding `paycard_funding_return` rows (task 1).

Task 1 paycard writes the published docs could call owed today:
- the missing late funding fee of S-4, booked with debit_program_fee_609ed260; it adds a `paycard_fee_debit` row, not read;
- a restoring wire: restoration reserve 5 percent × average regular batch in the 3-month look-back ≈ 20188.81, against a balance of 24710.50, so the restoring payment is 0.00 and nothing is owed;
- suspension: 1 return in 90 days, under the count of 3; no negative balance; not owed;
- reinstatement: not suspended, so not owed;
- termination: the employer keeps the program.

Task 0 paycard writes:
- the unseeded monthly fees could be debited, but they change no read field;
- no suspension can be owed (Standard: 2 returns in 90 days, or a balance negative for more than 3 business days; none recorded).

Access, card, disburse, save and loan hold no records for these employers or their workers in either world, so no write of theirs can touch a scored read.

**Result: no member of this class.**

### Verdict
- KB defects: none. All three parts PASS for both tasks; nothing regressed since revision_2.
- Source-side items (instantiator's, seed-only, none gold-moving): S-4, S-5, S-6.

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=S-4,S-5,S-6

## revision_4 (2026-10-23, short KB confirm after SEED-ONLY rework)

### Entry
- policy_task tail = `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN`.
- Snapshot re-run by this auditor (`/tmp/erl0077_coord/kb_snapshot.sh employer_program_settlement_and_changes program`, 2026-10-23T11:04:24):
  - `check_docs.py program => DOCS OK`
  - `check_traceability.py employer_program_settlement_and_changes => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`
  - EXTENDED, TASK TOOL CONTRACT, REPLAY (0.json 23/23, 1.json 389/389), SOLVABILITY, COMPUTE, GROUNDING, SCOPE: all OK
- Hashes:
  - source sha256 8edfe41cb636 0afad5185ffe 267211c2dabb d713fb33fefb; only the 4th, the task bundle, changed since revision_3;
  - program docs ecd4e7fd2a924db1, unchanged;
  - runtime views unchanged.

### Changed rows: diff of the task 1 runtime returns against the revision_3 captures
- program_settlements: byte-identical.
- paycard_funding, 125 → 126 rows:
  - ADDED 233056e8: `paycard_fee_debit`, fee_type `late_funding`, 50.00 (Advantage late funding fee), entry 2026-08-24, the day the wire funds arrived, pointing to batch 7100752c and carrying its pay date 2026-08-21;
  - CHANGED: June 2025 monthly_program and active_card fees 2025-07-07 → 2025-07-08;
  - CHANGED: August 2025 fees 2025-09-05 → 2025-09-08;
  - no row removed.
- program_billing, August 2025 invoice lines bc61e2f9, c762079e, 3345d84e:
  - entry date 2025-09-03 → 2025-09-04, due 2025-10-19 (+45);
  - their payments are dated 2025-09-24, 20 days after the invoice, as in every other month and before the due date.
- paycard program record: funding_balance 24710.50 → 24660.50, so it again equals the recomputed running balance of the 126-row ledger.
- Agreement receivables unchanged (8894.80 / 130421.60).

### Closure
- S-4 CLOSED: the late funding fee owed on the 2026-08-21 batch is now in the ledger at the package figure.
- S-5 CLOSED: both months' fees fall on the 5th business day.
- S-6 CLOSED: the August 2025 invoice lines carry the 3rd business day after Labor Day, and their due dates follow.

### What the changed rows touch
- The 5 percent reserve still holds after every batch; the smallest margin is above 4000 even with the 50.00 removed.
- The restoring payment is still 0.00: balance 24660.50 against a restoration reserve of about 20188.81.
- Suspension: 1 return in 90 days and no negative balance today, so none is owed.
- Status live, launch date and package are unchanged, so card_bundle_depth and termination_bundle are unaffected.
- returned_payments_method still counts 3 returns, since the added row is a fee debit, not a return.
- termination_fee_lines window entries (2026-08-05 / 09-03 / 10-05) unchanged.
- No 2025 entry date is read at day precision by any factor.
- Scored values and baseline_results unchanged: 3030.38 / 320.11 / 362.06 / 1659.45 / 25115.65; 0.00 / 106.25 / 156.01 / 575.23 / 17700.00.
- No new owed-at-once write.

### Verdict
No KB defect; no new source item; nothing regressed.

KB-VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=NONE
