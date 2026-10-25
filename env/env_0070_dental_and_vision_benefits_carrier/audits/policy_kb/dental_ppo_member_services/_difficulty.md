# KB-doc policy audit — dental_ppo_member_services (product "Dental PPO Plans", docs/dental) — closing

## revision_1 (2026-10-19T08:43Z)

### Entry conditions (Step 0, cited from the coordinator brief; auditor ran no gate per binding coordinator notes)
- Policy-side verdict: `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN` (audits/policy_task/dental_ppo_member_services/_difficulty.md, last line read after the blind answers were frozen).
- Gate snapshot 2026-10-19T08:30:07: `check_docs.py … dental` → `DOCS OK`; `check_traceability.py …/tasks/dental_ppo_member_services` → `0.json 26 0 True / 1.json 32 0 True / TRACEABILITY OK (non-unlock misses: 0)`; instantiate gates EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK.
- Source sha256 prefixes at audit close: extended.yaml `f298a853751a47e7`, task_tools.py `ff8127367901d52f` (equal to the snapshot); corpus title/content hash `665a95c196ff286b` unchanged from blind freeze to close, so the snapshot applies to the final form. The skill's Step-5 re-run of the two gates was not performed by this auditor because the coordinator notes forbid running any gate (tool-name leak); the snapshot lines above are the record.
- Runtime view and DB access path supplied (`.audit_views/runtime/`, `db_query.py`); DB side blind for both tasks.

### Per-task part verdicts
| Task | KB-RUNTIME (runtime_context/…/N.md) | KB-BIJECTION (policy_kb/…/N.md) | KB-EXPLICIT (policy_kb/…/N.md) |
|---|---|---|---|
| 0 | PASS — blind writes equal GT on all 18 scored arguments; 1 hop, state-derived | PASS | PASS |
| 1 | PASS — blind writes equal GT on all 25 scored arguments; 3 hops, all state-derived | PASS | PASS |

### Closing checklist
- Audit files one-to-one with tasks: runtime_context/dental_ppo_member_services/{0,1}.md, policy_kb/dental_ppo_member_services/{0,1}.md (revision_1; blind sections frozen before reveal: sha prefixes 315c32d4482330a6 / f4e3f3dd60a4a001).
- Every normative atom of the six extended policies (rules, baselines, all 30 factor ladders, 6 hubs of which 4 carry a prerequisite sentence, 19 overwrite entries across 5 retired base clauses) and of the governing base policies is entailed by docs/dental, nothing added, nothing changed in meaning.
- Every prerequisite sentence (4) verbatim, state form, in its blocked hub only; every hop resolvable from it, the depended-on hub and the records.
- Every retired base clause has a bearing document marked "Former clause, no longer in force as written", the residual carried as in force, and no undeclared retirement.
- No other problem's tool name, route, aggregated chain, task-mirroring title or computation-document modification hint anywhere in the corpus.
- No worked example or tool schema equals a scored value.

### Policy-side notes (do not change this skill's verdict)
- **src-1** (low; both tasks unaffected): `dental_evt_claim_adjudication` overwrites in all five reprocessing/estimate policies restate the residual base rule more narrowly than the clause they retire — the allowance residual omits "such a line is paid with remark PAID_ALTERNATE_BENEFIT"; the member-share residual omits "and the practice may not bill more". The KB follows the source (claim_line_adjudication_rules_e6144887 §3/§7 show both phrases only in the retired quotation), so for ordinary lines no in-force sentence assigns the alternate-benefit remark (still treated as adverse in member_appeals_policy_f880197a §2) or bars in-network balance billing.
- Cross-product conditional (not RED): task 1's grace-period reading rests on Premium Billing Accounts records (`grace_cure` payment); the billing corpus is not yet published.
- Observation only: accumulator-posting ids repeat across the two task worlds (e.g. `1a626d6f-…` in both); each world is separate, so no defect within either task.

### Coverage gap (stated, not covered elsewhere)
Base-type dental policies claimed by no difficulty and other products' corpora are outside this audit; cross-product contradictions are structurally suppressed, not proved absent.

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=src-1

## revision_2 (2026-10-19T09:51:51Z)

- Gate protocol (/tmp/erl0070_coord/kb_reaudit_gate.txt): upstream `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN` ✓; docs/dental re-rendered after it ✓.
- Snapshot (kb_snapshot.sh dental_ppo_member_services dental, 2026-10-19T09:50:50): `DOCS OK`; `0.json 26 0 True / 1.json 32 0 True / TRACEABILITY OK / non-unlock misses: 0`; check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding / check_cross_fire all OK; src sha256 `b51f17bf00364ed7 ff8127367901d52f`.
- Round-1 item: **src-1 closed** — source replaced_by residuals (10 overwrites, 5 policies) now carry the PAID_ALTERNATE_BENEFIT remark, the alternate-benefit cases and the in-network no-balance-billing clause, plus an all-cases sentence for each; KB claim_line_adjudication_rules_e6144887 §3/§7 render them faithfully, retired-clause quotations intact.
- Regression check: corpus diff vs round 1 touches only e6144887 §3/§7; task JSONs and task_tools.py unchanged; prerequisites, baselines and factor ladders unchanged in count and verbatim carriage (all four policy_source sentences still verbatim in their hubs). Targeted check sufficient per brief; no new defect.
- Per-task: task 0 RUNTIME/BIJECTION/EXPLICIT = PASS/PASS/PASS; task 1 = PASS/PASS/PASS.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_3 (2026-10-20T03:37:03Z) — cross-product re-judge (/tmp/erl0070_coord/rejudge_notes.txt)

### Inputs
- Snapshot `kb_snapshot.sh dental_ppo_member_services dental` 2026-10-20T03:31:42: `DOCS OK`; `0.json 26 0 True / 1.json 32 0 True / TRACEABILITY OK / non-unlock misses: 0`; all 7 instantiate gates OK; src sha256 `b51f17bf00364ed7 ff8127367901d52f` (unchanged since revision_2). docs/dental hash `b7dabbbf0e372487` (unchanged since revision_2).
- Published corpora read as criteria for their own rows: billing (52), dhmo (18), group (15), provider (72), ortho (46), savings (17); vision not published (0 docs) — neither world holds a vision row, so nothing is vision-conditional.
- Rows enumerated with every share finder unfiltered via db_query.py in both worlds. Other-product rows present: DHMO plans (1+1), DHMO services (2+0), billing accounts (2+2), billing transactions (102+102), billing requests (1+1), group contracts (1+1), group eligibility events (10+10), employer customer profiles. No provider, ortho, savings, vision, identity-verification or handoff rows in either world.

### Row-by-row re-derivation (as of each row's own date)
Task 0 (Bassett):
- DHMO enrollment 730905b4 (DHMO 315, individual, member only): application 2021-12-10 → effective 2022-01-01 ("first of the month following receipt") ✓; voluntary termination 2025-02-28 = last day of a month ✓; service area WA ✓.
- DHMO account 5cac8d44 (Individual Direct Bill Monthly): 38 monthly invoices 2022-01..2025-02 at 15.40 = DHMO 315 member-only rate ✓; each issued 20 days before the 1st (e.g. 2021-12-12, 2022-02-09, 2024-02-10 leap year) ✓; binder paid 2021-12-29 by card ✓, then regular card payments before each due date ✓; paid-through 2025-02-28 ✓; closure request d76ba3f2 confirmed 2025-03-04, effective/closed 2025-03-06 with no active enrollment and balance 0.00 ✓.
- DHMO services: D1110 cleaning 2024-03-12 copay 10.00 (DHMO 315 adult cleaning 10.00) and D7210 surgical extraction tooth 19 2024-09-17 copay 85.00 (DHMO 315 surgical extraction 85.00); both by the assigned PCD — the docs add the 5.00 office visit copay per primary-care visit (Article 4.7: "the scheduled copay … plus the office visit copay"), giving 15.00 and 90.00 for the two visits; no office-visit charge is seeded (**src-3**). The credit factors read only the DHMO enrollment dates and the extraction's tooth/date — no scored value moves.
- Group G-7136650 (20-49, Premier 2000, WA, contributory 75 %, new-hire wait 30 days): segment band, situs, waiting-period choice, contribution minimum, renewal 2027-01-01 / guarantee to 2026-12-31 ✓. Census 2025-01-02 (11/4/3/5 of 31) prices the 2025-03 invoice 2047.30 ✓ (issued 2025-01-30 = 30 days before 1 March ✓); Lorraine's late-entrant addition (request 2025-02-10, reported 2025-02-11, effective 2025-03-01 = first of the month after the request) ✓; with her, enrolled on 1 March = 12 member-only → 2097.55 per month ✓ for 2025-04..2026-03, all issued 30 days ahead and paid before due ✓; paid-through 2026-02-28 and balance 2097.55 at frozen time ✓. The March 2025 premium is booked as 2047.30 + a separate invoice "202503A" 50.25 (issued 2025-02-12): the total equals the docs' figure (contract rates × subscribers enrolled on the first of the month), but the billing docs state no supplementary-invoice mechanism (observation; no scored value).
- Provider side: claim lines 2025/2026 and the January estimate 17c2e8f8 record `network_status: in_network_ppo` with `provider_agreement_id: None`; the world holds no provider agreement and no practice profile ("Ashford Family Dental" not found). The dental rule fixes network status from "the treating practice's agreements in force … no agreement gives out-of-network status", and Network Participation Agreements would need a Cascade PPO Participating Dentist Agreement in force on 2026-01-12 (**src-2**). Effect: the requested-estimate worksheet takes the network status recorded on the most recently issued estimate line (§A), so the entailed answer is GT (in_network_ppo, 300.00 / 260.00); a solver who re-derives network status from agreements gets out_of_network, 50 %, 280.00 plan payment and 280.00 patient cost — three scored arguments would move. Historical lines are unaffected (re-pricing the root canals and filling at out-of-network 80 % leaves each payment at the standard-COB limit: 450.00, 450.00, 90.00; preventive 100 % either way), so the 2026 maximum postings and the initial-wait write are unchanged. The DHMO enrollment likewise has `assigned_pcd_agreement_id: None` although DHMO Article 2.4 makes activation wait on an assigned primary care dentist (same class, src-2; no scored value moves).

Task 1 (Abernathy):
- DHMO enrollment 0fa737e7: application 2022-04-12 → 2022-05-01 ✓; voluntary termination 2025-05-31 ✓. DHMO account 108db16e: 37 invoices 2022-05..2025-05 at 15.40, 20-day lead, binder 2022-04-28 ✓; paid-through 2025-05-31 ✓; closure request confirmed 2025-06-03, closed 2025-06-05 with balance 0.00 ✓. No DHMO services (credit needs none).
- Group G-7104482 (20-49, contributory 75 %, new-hire wait 60): renewal 2025-07-01 with plan change Value 1000 → Classic 1250 (R.7) and guarantee to 2026-06-30 ✓. July 2025..June 2026 invoices 1194.40 = 9×32.40 + 3×63.05 + 3×67.55 + 5×102.20 ✓, 30-day lead ✓; Corinne late entrant (request 2025-05-12 → effective 2025-06-01) ✓. June 2025 invoice 935.75 is priced at the prior plan year's Value 1000 contract rates, which no record carries — not re-derivable (observation). The Value member-only rate visible from the "202506A" invoice (26.10) rose to 32.40 at the 2025-07-01 renewal, +24.1 %, while the 20-49 renewal rate cap is 12 % ("No increase exceeds the segment's renewal rate cap", R.2) and the group docs make no exception for a plan change at renewal (**src-4**, low; no scored value moves).
- Participation: May 2025 census 19/26 = 73 % < 75 % contributory minimum, cured by the 2025-06-02 census (member-only 9 → 20/26 = 76 %) within the 60-day cure period before the 2025-07-01 renewal ✓ under the docs' cure rule.
- Grace (revision_1 conditional, now checkable): 2026-01 invoice issued 2025-12-02, unpaid at the 2026-01-01 due date → grace period from 2026-01-01, 31 days, ending at the close of 2026-02-01; cured by the 2026-01-28 `grace_cure` remittance of 1194.40 = past-due premium for begun months (the 2026-02 invoice, issued last and not yet begun, correctly left out and paid separately as regular) ✓; account active, paid-through 2026-06-30, balance 1194.40 at frozen time ✓. So on 2026-01-20/23 the account was in grace and the Group List Bill line was to be adjudicated normally — the premise of the grace-period hop holds; **conditional item closed, consistent**.

### Conclusion
- KB side: no change, no new defect (dental corpus unchanged; cross-product reading of billing, dhmo and group docs agrees with every dental premise used by the two tasks).
- Source/seed side: src-2 (missing provider agreement / practice records behind recorded network statuses and the DHMO PCD assignment — the only item with a gold-moving alternative reading, task 0 estimate network/payment/cost), src-3 (DHMO PCD visits omit the office-visit copay), src-4 (task 1 group renewal increase above the segment cap). src-1 stays closed. Observations without an id: supplementary group invoices ("A" invoices) have no doc mechanism though their totals equal the docs' monthly premium; task 1's June 2025 base invoice is not re-derivable from recorded rates.
- Per-task: task 0 RUNTIME/BIJECTION/EXPLICIT = PASS/PASS/PASS; task 1 = PASS/PASS/PASS.

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=src-2,src-3,src-4

## revision_4 (2026-10-20T05:05:30Z) — seed-only re-audit (rounds 6–7)

- Gate protocol: upstream `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN` ✓; snapshot 2026-10-20T05:03:29: `DOCS OK`; `0.json 30 0 True / 1.json 34 0 True / TRACEABILITY OK / non-unlock misses: 0`; check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding / check_cross_fire OK; src `b51f17bf00364ed7 ff8127367901d52f`. docs/dental `b7dabbbf0e372487` unchanged.
- Changed worlds re-derived blind from docs + db_query (full unfiltered finder dumps diffed against revision_1/3 reads), then GT re-read: all scored arguments of both tasks unchanged and equal to the blind answers.

### Round-3 items
- **src-2 closed.** Task 0: PPO lines 39257a25, 4b8ec330, 9643fcb5, aedb031d, a7ad6ed2 and estimate 17c2e8f8 now reference agreement 0c81cbc2 (Cascade PPO Participating Dentist Agreement, Ashford Family Dental PLLC, active, effective 2015-02-01, no termination) — in force on every date of service and on 2026-01-12 / 2026-02-24, so the base network rule now also yields in_network_ppo; the agreement-based alternative reading (out_of_network / 280.00 / 280.00) is gone. Implant line 866928ce keeps no agreement → out_of_network, matching its recorded status. DHMO PCD agreements: task 0 1dbe0b0d (Proctor District Family Dentistry, eff. 2015-09-01), task 1 6843d33b (Lincoln Avenue Dental Care, eff. 2016-04-01), both active and in force across the DHMO coverage periods (Article 2.4 activation now supported). Task 1 claim lines remain out_of_network without agreements, consistent.
- **src-3 closed.** DHMO services now 15.00 (adult cleaning 10.00 + office visit 5.00) and 90.00 (surgical extraction 85.00 + office visit 5.00) under DHMO 315, by the assigned PCD (agreement 1dbe0b0d), as Article 4.7 gives.
- **src-4 closed (to the extent records allow).** June 2025 Value 1000 member-only rate is now 28.95 (invoice 202506A); 28.95 → 32.40 at the 2025-07-01 renewal is +11.92 %, within the 12 % cap. Base invoice 1037.80 = 8×28.95 + 806.20 for the other tiers; the cap requires Value rates of at least 56.29 / 60.31 / 91.25, whose minimum total 806.05 ≤ 806.20, so the invoice is consistent with a capped renewal (the individual Value tier rates remain unrecorded — observation). Remittance 1066.75 = 1037.80 + 28.95 ✓.

### Re-pricing of every other-product row (unchanged rows re-checked against revision_3)
- New provider rows: 36-month recredentialing cycle (decisions 2024-01-18 → 2027-01-18, 2024-07-29 → 2027-07-29, 2025-03-24 → 2028-03-24) ✓; liability 1,000,000 / 3,000,000 meets the per-occurrence and aggregate minimums ✓; license and liability unexpired at each frozen time ✓; panels open ✓; WA service state ✓.
- DHMO enrollments, DHMO accounts (15.40 × 38 / 37 months, 20-day lead, binders, closures), group contracts, census/participation, group invoices 2097.55 and 1194.40, task 1 grace and cure: unchanged and still re-price as in revision_3.
- Observation carried (no id): supplementary "A" group invoices have no doc mechanism although totals equal the docs' monthly premium.
- No new defect; nothing regressed (KB unchanged; scored values unchanged).
- Per-task: task 0 RUNTIME/BIJECTION/EXPLICIT = PASS/PASS/PASS; task 1 = PASS/PASS/PASS.

KB-VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=NONE
