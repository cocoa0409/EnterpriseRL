# KB doc-policy audit — managed_services_agreements (product managed, ClearPath Managed IT Services)

## revision_1 (2026-10-18)

### Entry conditions (Step 0)
- Policy-side verdict (tail line only, read before the freeze): `VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN`.
- Gate snapshot from the brief (coordinator, 2026-10-18T12:31:08): check_docs DOCS OK; check_traceability TRACEABILITY OK (0 non-OK lines); check_extended / check_task_tools / replay_tasks --check / check_solvability / check_compute / check_grounding / check_cross_fire rc=0; managed.extended.yaml 1a19b120...; task_tools.py 819877d3...; docs/managed 83 files, tree 63af8913....
- Runtime views 0.runtime.json (ef9a8412...) and 1.runtime.json (d4a72b4f...) verified; DB reached only through `db_query.py` tool-shaped calls (blind on the DB side). Inputs complete.

### Per-task verdicts
| Task | Runtime blind audit | Two-way scan | Dependency form |
|---|---|---|---|
| 0 (Bellwood, early termination notice) | PASS — blind 140.00 / 124.82 / 4686.16 / 15656.52 and the four state-form edges equal GT | PASS | PASS (notes N1, N2) |
| 1 (Calloway & Drummond, Essentials -> Standard) | PASS — blind 8.71 / 308.55 (105 min) / 362.50 (120 min) / 95.44, 2026-11-01 and the three state-form edges equal GT | PASS | PASS |

Files: runtime_context/managed_services_agreements/{0,1}.md (blind_answer frozen before reveal, gt_comparison appended); policy_kb/managed_services_agreements/{0,1}.md.

### Findings
- KB items: none.
- Dependency-form notes (placement class, not RED): N1 exit_fee_months_and_amount_6bd0c46a assembly sentence names "the monthly basis", a quantity only the exit billing-basis factor document defines; N2 monthly_basis_of_exit_fees_24f0ac7e uses the tenure schedule's term "exit-fee percentage". Neither states a figure, a tier or a pointer; both factors are findable from the records without them.
- Source-side item:
  - S1 (low, non-normative text, no scored effect): lifecycle transition suspended -> active "Service is reinstated after every past-due invoice and the reinstatement fee are paid." (blueprint/products/managed.yaml:20 and managed.extended.yaml:20) contradicts the rule (managed_late_fee_and_suspension / managed_ext_reinstatement_charge: reinstatement is recorded once every past-due invoice is paid, and the fee is invoiced on the reinstatement date). The KB follows the rule.
- Policy-side note (not listed as src): the renewal record's term end date is stated by no rule (only start, length, seats); the initial-term convention in managed_onboarding_and_go_live is the visible basis and gives 2027-09-30 uniquely in task 0.
- Cross-product seed spot-check: task 1's historical labor rows (217.00, 180.19, 331.25), task 0's historical monthly fees, late fees and service credits, and both clients' Sentinel / Continuum rates recompute from the published managed, security and backup documents. No seed row found that the published documents would not produce.
- Leak check after reveal: no scored value or intermediate in any docs/managed title or content, nor in the eight unlock invocation blocks; coincidental figures 140.00 (Schedule E Premier remote rate), 121.52 and 119.04 (upgraded Standard term table) are published product figures.

### Closing checklist (Step 5)
- Audit files correspond one-to-one with tasks 0 and 1; revision_1 is the first revision.
- Every normative atom of the four + four extended policies and their base policies is entailed by docs/managed; every prerequisite sentence (ET1-ET3, MF1, UP1-UP3) stands verbatim, in state form, only in its blocked hub, and every hop resolves from it, the depended-on hub and the records; every factor ladder (43 factors) is carried in full in its own document.
- check_docs re-run on the final form 2026-10-18: `DOCS OK` (mechanical gates PASS; manual bijection judged above). check_traceability not re-run, as the brief instructs; the snapshot line `TRACEABILITY OK (non-OK lines: 0)` is on record. Hashes of the extended YAML, task_tools.py and the KB tree are unchanged since the snapshot.
- Coverage gap stated: unclaimed base products' corpora (licensing, hardware, security, backup) were read only for tier features and are outside this audit.

KB VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=S1

## revision_2 (2026-10-18, cross-product re-judge after all seven products were published)

### Snapshot and hashes
`/tmp/erl0069_coord/kb_snapshot.sh managed_services_agreements managed` (executed, not read; output 2026-10-18T17:27:55):
- check_docs: DOCS OK. check_traceability: TRACEABILITY OK (non-OK lines: 0).
- check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire: all rc=0.
- 0.runtime.json ef9a8412...; 1.runtime.json d4a72b4f...; managed.extended.yaml 1a19b120...; task_tools.py 819877d3...; docs/managed 83 files, tree 63af8913....

All are unchanged since revision_1, so the revision_1 blind answers, GT comparisons, two-way scans and dependency-form judgements stand (appended as revision_2 in each per-task file). The cross-product re-judge of the managed corpus against the six sibling corpora found no contradiction and no new KB defect. Sibling documents read ClearPath records only for their own products' figures and state no rule about any ClearPath fee, rate, notice, reinstatement, labor or tier change. Nothing regressed.

### Exhaustive pass over every cross-product seed row
I called every finder by client for both tasks: security (subscriptions, endpoint changes, billing, incidents, IR ledger, change requests), backup (plans, device changes, billing, recovery events, DR ledger, change requests), licensing (subscriptions, license changes, billing, change requests), TimeBank (blocks, hours ledger, billing, orders), hardware (orders, billing, returns, client requests), project (engagements, billing, milestones, work logs, change orders) and handoffs. TimeBank, hardware, project, incidents, recovery events, DR ledger and Sentinel/Continuum change requests have no rows for either client. Each row present was recomputed against its owning product's published documents, including look-back windows reaching before the seeded history.

Consistent with the published rules (no finding):
- **Task 0, Sentinel MDR Advanced 2704cf16.** Rates 14.95 / 29.14: list price less the 36-month 6 %. No bundle, because ClearPath was applied, not active, on the 2024-08-05 order, and rank 3 is below 4. Onboarding fee max(10 x 45, 1250) = 1250 on the order date. Term 2024-09-01..2027-08-31. The first monthly fee is October 2024, the month after activation. Fees 745.22 (44 workstations + 3 servers), 805.02 from 2025-06 (snapshot after the 2025-05-12 additions) and 790.07 from 2026-02 (after the 2026-01-20 retirement); all above the 41-endpoint floor. Every invoice paid before its due date; the 2026-10 fee is open and not yet due, so the balance is 790.07. IR ledger 2024-2025 cycle: grant, forfeit (rollover 0 %), grant.
- **Task 0, Continuum BDR a5c4379d.** Rates 113.05 / 13.30 / 3.56: list less 5 %, no bundle (ClearPath not active on the order date). Onboarding fee max(195 x 3, 750) = 750. Entry gate met (3 items, 1+ server, HIPAA covered). Term 2024-09-03..2027-09-02. The first fee is October 2024. Fee 3 x 113.05 = 339.15 (floor 3). BDR grants 0 failover days, matching dr_days_balance 0. All invoices paid on time.
- **Task 0, Microsoft 365.** F3 dc9c62ce: P1Y annual 8 x 8.00 x 12 = 768.00, renewed 2025-11-01 at the current price list, window reopened 2025-11-01 00:00. Business Premium 95bc5998: 48 x 22.00 x 12 = 12672.00, renewed 2026-03-01. Signed order forms precede each purchase; term dates follow the published convention; payments fall within net 30. Administration fees for every month through 2026-08 correctly not posted (ClearPath Standard active, covering Microsoft 365 administration: 0 %). Cancelled F3 daddac31: P1M price 8.00 x 1.2 = 9.60, cycle charge 48.00, cancelled 2026-06-12 inside the 168-hour window; it was cancelled before month end, so no administration fee is owed for June.
- **Task 1, Sentinel MDR Advanced d7433820.** 12-month list rates 15.90 / 31.00; no bundle (Essentials, rank 2). Onboarding fee 1250 on the order date. 28 workstations enrolled while deploying, above the 24-endpoint activation threshold. Term 2025-11-01..2026-10-31. The first fee is December 2025; 28 x 15.90 = 445.20 monthly. IR grant at activation; the anniversary is not yet reached.
- **Task 1, Continuum Backup Plus 271fabeb.** Rates 75.05 / 10.93 / 3.56 (list less 5 %, no bundle). Onboarding fee max(95 x 1, 250) = 250. Term 2024-06-15..2027-06-14. The first fee is July 2024; 75.05 monthly (floor 1). All paid on time.
- **Managed-side look-backs.** Every window the managed factors read (12 / 24 / 6 / 3 months; go-live tenure) lies inside the seeded managed history of each agreement (go-live 2024-10-01 and 2024-06-01).

### Source-side items (src)
- **S1** (carried from revision_1; low, non-normative): lifecycle text "Service is reinstated after every past-due invoice and the reinstatement fee are paid." (blueprint/products/managed.yaml:20 and managed.extended.yaml:20) contradicts the rule, which invoices the fee on the reinstatement date.
- **S2** (task 0, security seed, missing rows): the Sentinel IR ledger of 2704cf16 stops at the 2025-09-01 grant. Published rule (security/ir_hours_ledger): "At activation and on each anniversary of the term start date, the subscription is granted the tier's annual included incident response hours"; at a contract year's end unused hours beyond the rollover share "are forfeited". MDR Advanced has 10 hours and a 0 % rollover. The 2026-09-01 anniversary, before the frozen time of 2026-10-08, should show a forfeiture of 10 hours for contract year 2025-09-01 and a grant of 10 hours for contract year 2026-09-01. The ledger shows this pattern for 2024 -> 2025 but not for 2025 -> 2026. ir_hours_balance (10.0) is the same either way; no managed value reads it.
- **S3** (task 1, backup seed, entry gate): Continuum Backup Plus plan 271fabeb protects 1 item (contracted_servers 1, protected_count 1, one server CDA-FS01). Published entry gate (backup/tier_entry_requirements): Continuum Backup Plus "Minimum protected items at order: 3"; ordering_rates_and_tier_changes: "at least the tier's minimum protected items at order". Under the published backup documents this plan could not have been ordered. Not scored: the relationship courtesy reads only its status (active).
- **S4** (task 0, licensing seed, missing rows): no administration-fee entry for service month 2026-09 on the active subscriptions 95bc5998 (Business Premium, 48 licenses) and dc9c62ce (F3, 8 licenses).
  - licensing/monthly_administration_fee_invoicing: the previous month's fee "is invoiced on the first day of each calendar month ... on every ... subscription whose status was active or suspended at the end of that month".
  - licensing/clearpath_coverage_share_of_admin_fee: the 0 % share applies only to an agreement that is "active or notice given" on the posting day. On 2026-10-01 Bellwood's ClearPath agreement was suspended (since 2026-09-14), which falls under "any other agreement, or none — no reduction".
  - Both fees (amounts per the administration-fee schedule) were therefore owed on 2026-10-01, before the frozen time. No managed value reads them; the managed factors read license_qty and status only.
- **S5** (task 0, licensing seed, wrong amount): the cancelled F3 P1M subscription daddac31 carries refund credit 68fa7332 of 44.80 (2026-06-12) and a residual payment a6b4ed36 of 3.20 (2026-06-26).
  - Under the published licensing documents the cancellation falls in the cancellation schedule (whole_subscription_cancellation: P1M, window refunds yes).
  - The cancellation date 2026-06-12 is 2 days after the window opened (2026-06-10). prompt_cancellation_refund_basis case A therefore applies: "refunded as never used ... the cycle amount per license times the licenses refunded, with no day count" = 9.60 x 5 = 48.00, within the 48.00 ceiling.
  - No deductions apply: ClearPath Standard was active and covers Microsoft 365 administration on 2026-06-12, so no order-reversal or seat-change charge; Continuum protects no Microsoft 365 user; no administration fee was billed.
  - The published refund is 48.00, and the 3.20 residual payment would not arise. 44.80 = 9.60 x 5 x 28 / 30 is the schedule's standard day-count reading without the prompt-cancellation factor. No managed value reads the cancelled subscription (excluded by status).

None of S1-S5 changes a scored value or a factor tier of either task. The GT recomputation in revision_1 and the snapshot's check_compute and replay_tasks are unaffected.

KB VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=S1,S2,S3,S4,S5

## revision_3 (2026-10-18, seed-only re-check of S2-S5)

- Gate: `audits/policy_task/managed_services_agreements/_difficulty.md` ends with `VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN`.
- Snapshot `/tmp/erl0069_coord/kb_snapshot.sh managed_services_agreements managed` (executed, not read; output 2026-10-18T17:57:23):
  - check_docs DOCS OK; check_traceability TRACEABILITY OK (0 non-OK lines); the seven other gates rc=0.
  - Runtime views ef9a8412... / d4a72b4f...; managed.extended.yaml 1a19b120...; task_tools.py 819877d3...; docs/managed 83 files, tree 63af8913....
  - Everything is unchanged, so this round is seed-only with no re-render.
- **S2 closed (task 0, Sentinel IR ledger 2704cf16).** New rows 525c9a9e (forfeit 10 h, contract year 2025-09-01) and c25cc990 (grant 10 h, contract year 2026-09-01). This matches security/ir_hours_ledger (anniversary grant; 0 % rollover on MDR Advanced, so the unused 10 h are forfeited). ir_hours_balance stays 10.0.
- **S3 closed (task 1, Continuum Backup Plus 271fabeb).** Workstations CDA-WS-PRINC01 and CDA-WS-CAD02 are now protected from 2024-06-15, so protected_count is 3, meeting the 3-item entry gate. Every monthly fee is now 96.91 = 1 x 75.05 (billed servers max(1, ceil(0.8 x 1)) = 1) + 2 x 10.93, matching backup/monthly_plan_fee. All are paid before due except the open 2026-10 fee, so the balance is 96.91. The onboarding fee of 250.00 is unchanged and still correct.
- **S4 closed (task 0, licensing).** Administration fees for 2026-09 posted 2026-10-01 on new invoices: Business Premium 95bc5998 76.80 (INV-018201) and F3 dc9c62ce 14.00 (INV-018214). Recomputed from the published licensing documents:
  - Share 100 %, because ClearPath was suspended on the posting day.
  - Business Premium: 1.50 x 90 % (volume, 48 licenses) + 0.25 upkeep (baseline plan; Sentinel MDR Advanced includes identity threat detection) = 1.60 per license.
  - P1Y terms of 365 days get no commitment adjustment; there is no Continuum bundle (no Microsoft 365 users protected) and no part-month reduction.
  - 48 x 1.60 = 76.80; F3: 8 x (1.50 + 0.25) = 14.00.
  - Subscription balances 76.80 / 14.00 match.
- **S5 closed (task 0, cancelled F3 P1M daddac31).** Refund credit 68fa7332 is now 48.00 (prompt cancellation case A: 9.60 x 5, within the 48.00 ceiling, no deductions). The 3.20 residual payment is gone, and the balance is 0.00.
- **No new defect.** I re-queried every cross-product finder for both clients. Row counts equal revision_2 except the intended changes: IR ledger +2; licensing billing -1 / +2; Continuum device changes +2. No TimeBank, hardware or project rows. No managed factor reads any changed field: Continuum bundle and relationship courtesy read plan status and tier, not workstation counts, and CSP/frontline read license quantity and status, not the ledger.
- **No moved scored value.** GT for task 0 (140.00 / 124.82 / 4686.16 / 15656.52) and task 1 (308.55, 105 min / 362.50, 120 min / 8.71 / 95.44, 2026-11-01) and every baseline_result are identical to revision_1. The revision_1 blind derivation from the visible surface still reaches them uniquely.
- S1 is carried as BLUEPRINT-KNOWN (base lifecycle text, not routed) and is not an open src item.

KB VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=none
