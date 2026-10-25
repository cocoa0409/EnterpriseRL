# KB-doc policy audit — nonowner_policies_and_renewals (product nonowner), difficulty close-out

## revision_1 (2026-10-21)

### Entry conditions (cited, not re-judged)
- Policy-side verdict: `VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN`.
- Gate snapshot, re-run at 2026-10-21T00:12:31 via kb_snapshot.sh (execute only):
  - check_docs nonowner: DOCS OK.
  - EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK, all rc=0.
  - check_traceability: TRACEABILITY OK (0 misses).
- Source sha256 is unchanged from the brief: nonowner.extended.yaml 63b0174b…d5, task_tools.py 66fd633c…8f. Corpus list-hash 96340225…f95 (63 docs), the same at freeze and at close.
- Runtime views: frozen_time and user_scenario are byte-equal to tasks/{0,1}.json, as checked after the reveal. The coordinator's "current" note held.
- DB access was through db_query.py (the runtime Engine) only. The raw initial_state was never read before the freeze.
- Order: both blind answers were frozen to disk (runtime_context/…/0.md sha 509b0d21…, 1.md sha 54d785e4…) before any source-layer read. contamination_disclosure: none.

### Per-task part verdicts

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 (insured cancellation after a late renewal) | PASS (provisional: FR figures cross-product-pending) | PASS | PASS |
| 1 (renewal offer after reinstatement and DUI realignment) | PASS | PASS | PASS |

Every blind computation equalled GT exactly. For task 0, the return amount and premium_days equal GT once the FR charter's 3 + 10 days are substituted.

### Cross-product-pending (re-judge when every product is published)
- **XP-1 (task 0, return_amount and premium_days):**
  - unearned_days_while_certified_226c1503 names "the Financial Responsibility Filings (SR-22 / FR-44) product's SR-26 transmission days plus its certificate run-off days for that certificate".
  - docs/fr is unpublished, so the figures (FR charter: sr26_transmit_within_days 3, certificate_runoff_days 10 on each Operator variant) are not yet visible.
  - At re-judge, confirm that the FR corpus states both figures for the SR-22 Operator Certificate form and that they are findable by those words.
- Billing and FR records feed several factors in both tasks: plan names, returned payments, filing status and dates. The nonowner factor docs carry all the credits and relativities themselves. The only check left for re-judge is that the billing and FR corpora do not contradict them.

### KB findings
None. All 6 extended policies, their governing base policies and the variant figures read are carried losslessly:
- every baseline is complete and hint-free;
- every factor ladder is full, including untriggered tiers;
- all 7 declared overwrites are rendered as retired, with the other clauses in force, and no undeclared retirement exists;
- all 5 prerequisite sentences are verbatim, each only in its blocked policy's hub, in its declared form (4 state, 1 action with declared fallback);
- no other problem's tool, route, aggregated chain or task-mirroring title appears.

### Source-side notes (not KB defects)
- None in the rule-vs-compute or seed-realism class: GT equals the visible-rule derivation in both tasks, and the decoy withdrawn filings and the stale term certificate field are excluded by visible rules.
- Policy-side note (Value 0, untriggered): nonowner_nonrenewal's "nonrenewal_reason list" is not enumerated in the charter (db_schema enum only). The KB mirrors the source, so this is not a source defect requiring routing.

### Closing checklist
- [x] Audit files are one-to-one with tasks 0 and 1: runtime_context/*.md (blind_answer + gt_comparison) and policy_kb/*.md (source_to_kb, kb_to_source, bijection_verdict, dependency_form).
- [x] Every normative atom is entailed, with nothing unborne or added.
- [x] Every prerequisite sentence is verbatim on its blocked side only.
- [x] Every factor ladder is full and findable from record words.
- [ ] Final cross-product re-judge (XP-1) is pending publication of docs/fr (and of auto and billing, for contradiction checks).

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=none

## revision_2 (2026-10-21) — cross-product re-judge, round 2

### Entry
- kb_snapshot re-run: DOCS OK; EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY OK (0 misses).
- Hashes unchanged: 63b0174b… / 66fd633c…, nonowner corpus 96340225…; views 575e2f88… / 4faf016a….
- Docs tree: auto, billing, fr, nonowner, physdam, rental, towing.
- Revision_1 text is preserved. There were no round-1 REDs to close, and nothing in the nonowner corpus regressed. XP-1 is closed.

### Part verdicts

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS (XP-1 closed: 3 + 10 = 13, so 162 days and 1205.23 = GT) | PASS | PASS |
| 1 | **RED — source-side S1** | PASS | PASS |

### KB findings
None (kb=CLEAN). The nonowner corpus remains a lossless rendering of its source.

### Source-side findings (every member, one pass)
- **S1 (task 1; moves every scored figure).**
  - Seeded FR-44 Operator filing c236dc0d…: status filed, sr26_date "".
  - Its backing Named Non-Owner term 1fb5c071… was cancelled for nonpayment 2026-10-10 and reinstated with a lapse (2026-10-10..2026-10-13).
  - The published FR rules (`fr/lapse_sr26_transmission_f48c5bcb` rules 1 and 4; `fr/sr26_notice_terms_5a921652`, scope of the reinstatement row) make a lapse SR-26 owed for exactly this case. Its window closed 2026-10-13, so on 2026-10-18 it is "transmitted at once on the day it is found owed".
  - The agent tool transmit_lapse_sr26_2b138773 unlocks and runs in the task-1 world (sandbox: the filing becomes cancellation_filed, SR-26 2026-10-18).
  - Doing so before the scored writes changes the re-write basis, removes the DUI-realignment trigger and the renewal prerequisite state, and zeroes every filer class. Every scored argument moves.
  - GT's rationale ("no SR-26 because the term was reinstated before one was due") contradicts the FR rule, under which only a reinstatement without lapse, or a rescission, avoids it.
- **S2 (task 1; history only, no score effect).** FR-44 c236… was requested 2026-10-01 while its backing term was pending cancellation: notice mailed 2026-09-25 and not rescinded. `fr/certificate_eligibility_and_filer_data_bcb2423e` cond. 2 allows a request only on a bound or in-force backing term.
- **S3 (task 1; history only, no score effect).** Plan 25d85cd1… bills on due day 20. The billing calendar (`billing/schedule_down_payment_and_installment_calendar_8cc9e16f`: first installment 1 calendar month after the 2026-06-02 effective date) gives day 2, and due_date_changes_used is 0. A permitted change is at most 10 days anyway (`fc752f8d`).
- **S4 (task 0; low, no score effect).** PIF plan a8ca8a85… has status current with balance −1265.17 and no installment left. `billing/delinquency_status_rule_0158e974` gives paid in full.
- **Checked consistent:** every other seeded row of another product in both tasks (FR filings and fee ledgers, billing plans, invoices, payments, returns, fees, authorization; no owner policies). The row-by-row tables are in policy_kb/0.md and 1.md revision_2.
- **Writes owed at once:** S1 is the only one that can move a scored figure. In task 0, the cancellation SR-26 becomes owed only after the final scored write (window to 2026-10-20). The release SR-26 needs a recorded release request and no tool exists for one.

### Closing checklist (revision_2)
- [x] Cross-product re-judge done; XP-1 closed.
- [x] The nonowner corpus is unchanged and faithful.
- [ ] Task 1 is blocked on source-side S1, a seeded cross-product FR row. S2–S4 are realism notes.

KB-VERDICT revision_2: task0=PASS task1=RED kb=CLEAN src=S1,S2,S3,S4

## revision_3 (2026-10-21) — re-audit round 3

### Entry
- **Gate:** `tail -1 RENDER.log` = "RENDER round 4: DOCS OK".
- **Policy line:** `VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN`.
- **kb_snapshot** 2026-10-21T20:08:11: check_docs nonowner DOCS OK; EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all rc=0; TRACEABILITY OK (0 misses).
- **Hashes:** nonowner.extended.yaml 53a9ceec…; task_tools.py 66fd633c…; nonowner corpus 1de14342… (63 docs).
- **Route** (rework_r9_claims.md): fallback charter change. The two exposure methods (late-renewal charging basis and re-write exposure basis) now read the certificate on file during the lapse by filing date and certified-through date. Task 1 was re-seeded.
- The runtime view for task 1 is stale (user_scenario). db_query and tasks/1.json were used.

### Round-2 items

| Item | Status | Evidence |
|---|---|---|
| S1 | **closed** | c236… now carries its SR-26 (10-12), and a reinstatement refiling e02f… (filed 10-15, fee 26.00 = FR refiling schedule) stands. No SR-26, fee or notice is owed at the opening. Even an SR-26 would leave the re-write flat, because the new method reads cancellation-filed certificates. Gold re-derived from the published docs is unchanged and equals GT |
| S2 | **closed** | FR-44 requested 2026-09-21 on an in-force term, before the 09-25 notice |
| S3 | **closed** | calendar 07-02 first due date; recorded due-day change to the 12th (shift 10, 1 used); every invoice, draft, return, fee and notice re-dated consistently |
| S4 | **closed** | the task-0 PIF plan reads paid_in_full |

### Regression check
- Of the 63 re-rendered docs, only the two exposure-method factor docs changed in substance. Both match the new source exactly, ladder and missing-date cases included, with no hint or pointer.
- Prerequisite sentences, retired clauses, tool docs and every other factor ladder are unchanged.
- Gold is uniquely entailed in both tasks:
  - task 0: 1449.71 / 2026-10-10 / 182; 2026-10-17 / 1205.23 / 162.
  - task 1: 439.70 / 2026-10-10 / 53; 100/300/50 / 2107.45; 64.89 / 2026-10-18 / 45 / lower_base_rate; 1765.28 / 2026-12-02 / 2027-06-02 / 182.

### Part verdicts (revision_3)

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

### New source-side notes (low; no scored figure moves; no write owed)
- **N1 (task 1).** c236…'s SR-26 was sent 2026-10-12, while the backing term was cancelled and not yet reinstated (reinstated 10-13, effective 10-14). By `fr/cancellation_sr26_transmission_47562be4` that is a cancellation SR-26, whose end date follows the cancellation schedule (`fr/cancellation_runoff_by_reason_4fd73081` nonpayment row: max(10, 30 − 2) = 28 + type 1 + VA 4 = 33, giving 2026-11-14). The seed prices it with the lapse schedule (13, giving 2026-10-25). Both dates leave the re-write flat and the refiling fee at 26.00.
- **N2 (task 1).** Final bill 1d27… shows past_due_amount 348.31 (= the whole post-credit balance). Only installment 3's 266.16 was past due on 2026-10-11, since installment 4 fell due inside the lapse. Read literally, the field makes the 10-13 reinstatement payment (266.16) short of nonowner's "every past-due amount", contradicting the seeded with-lapse reinstatement.

### Closing checklist (revision_3)
- [x] Audit files are one-to-one per task, with revisions 1–3 preserved.
- [x] Every normative atom is entailed; every prerequisite sentence is verbatim on its blocked side; every factor ladder is complete.
- [x] Cross-product rows re-judged; S1–S4 closed; no owed write moves any scored figure.
- [x] check_docs / check_traceability re-run on the final form: DOCS OK / TRACEABILITY OK.

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=N1,N2

## revision_4 (2026-10-21) — re-audit round 4

- **Gate:** `VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN`.
- **kb_snapshot** 2026-10-21T20:23:32: check_docs nonowner DOCS OK; EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all rc=0; TRACEABILITY OK (0 misses).
- **Hashes:** nonowner.extended.yaml 53a9ceec…, task_tools.py 66fd633c…, corpus 1de14342…, all unchanged (seed-only rework).
- **N1 closed:** c236… certificate end date 2026-11-14 = SR-26 date + 33-day cancellation run-off (28 + 1 + 4 + 0) under the published FR cancellation schedule.
- **N2 closed:** final bill past_due 266.16 (installment 3 only); premium 43.15 + fee 39.00 make up the 348.31 balance. The 10-13 reinstatement payment covers every past-due amount.
- **Knock-on checks:** the refiling fee stays 26.00 (half basis); the re-write exposure stays flat.
- **Gold uniquely entailed** on the new world and equal to GT:
  - task 0: 1449.71 / 2026-10-10 / 182; 2026-10-17 / 1205.23 / 162.
  - task 1: 439.70 / 2026-10-10 / 53; 100/300/50 / 2107.45; 64.89 / 2026-10-18 / 45 / lower_base_rate; 1765.28 / 2026-12-02 / 2027-06-02 / 182.
- **Writes owed:** none at the opening in either task.
- **Regression:** none.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

KB-VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=none
