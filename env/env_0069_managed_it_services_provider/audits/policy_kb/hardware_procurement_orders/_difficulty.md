# KB doc-policy audit — hardware_procurement_orders (product hardware, Hardware Procurement)

## revision_1

Auditor: erl-kb-doc-policy-audit sub-agent (2026-10-18). It is independent of the renderer and of the policy-side auditor. This is the first KB audit of this difficulty; no prior revision exists.

### Step 0 — entry conditions (cited, not re-run)
- Policy-side verdict tail line (the only audits/ content read before the freeze): `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN`.
- Coordinator gate snapshot 2026-10-18T11:00:36: check_docs `DOCS OK`; check_traceability `TRACEABILITY OK (non-OK lines: 0)`; check_extended / check_task_tools / replay_tasks --check / check_solvability / check_compute / check_grounding / check_cross_fire all rc=0.
- Re-hashed at close and unchanged since the snapshot: hardware.extended.yaml 4c40c1e1...d47d1d, task_tools.py 565f6102...b379e63, docs/hardware sorted-concatenation b7d1ae34...4281c (68 files). The documents did not change during the audit, so the snapshot lines stand as the final-form gate record. Per the brief, check_traceability was not re-run by the auditor.
- Runtime views: 0.runtime.json f27e6651...; 1.runtime.json 5857e2dc... (both re-hashed, matching). DB accessed only through db_query.py tool-shaped calls. The blind audit is clean on the DB side.
- Input complete.

### Per-task part verdicts
| Task | Runtime blind audit | Two-way scan | Dependency form | Files |
|---|---|---|---|---|
| 0 | PASS (543.07 / 5080.40 / 1258.06 and the 3-problem chain derived blind, all equal to GT) | PASS | PASS | runtime_context/.../0.md, policy_kb/.../0.md |
| 1 | PASS for the hardware corpus (718.97 / 2110.35 / 2700.20 and the 4-problem tree derived blind, all equal to GT). The re-issue total and deposit were narrowed to 4 candidates, one of which is GT 8586.26 / 3968.92; the choice rests on XP-1 below | PASS | PASS | runtime_context/.../1.md, policy_kb/.../1.md |

### Pending cross-product item (not a hardware KB defect; not a src item)
- **XP-1** (task 1; also the non-binding tenant-administration branch of task 0). Several hardware factors read ClearPath tier coverage switches from the managed charter: `technical_account_manager`, `dedicated_account_manager` (re-issue rush charge); `network_device_management_included` (re-issue bench staging rate); `m365_administration_included` (staged security preparation). No published corpus currently states those values for any ClearPath tier: there is no docs/<ClearPath> on disk, the agreement record has no coverage field, and the system background lists tier names only. The hardware documents carry the full ladders and name the attribute and product in the charter's own words, so the defect is not on the hardware side. Before the scenario is closed, the cross-product re-judge must confirm that the ClearPath corpus, once rendered by `managed_services_agreements`, publishes for ClearPath Professional: "named client success manager: yes", "named technical account manager: no", "firewall, switch and wireless configuration changes: covered", "Microsoft 365 tenant administration: covered" (and the same switches for every tier). It must also confirm that a reader can match that wording to these hardware sentences. Until then, task 1's re-issue total and approval deposit are not uniquely determinable at runtime.

### Notes (no verdict impact)
- N1: the docstrings of `sign_quote_approval_0590c0d2` and `sign_build_approval_1b1ae884` name a second source for hardware_order_id ("the quote issue receipt" / "the quote re-issue receipt"). The hubs name only the hardware order lookup. Same identifier, so there is no semantic loss.
- N2: the endpoint deposit's fixed order says "the deposit-required test ... comes first and no adjustment changes it". The computation document carries "comes first" and "no deposit is invoiced on a quote total below the deposit threshold". The "no adjustment changes it" half is entailed rather than restated. It does not bind in task 0 (5080.40 >= 5000.00).
- Policy-side notes: none found.

### Closing checklist
- [x] The audit files correspond one-to-one with tasks 0 and 1. Each has a frozen blind_answer (freeze hashes recorded) followed by gt_comparison, source_to_kb, kb_to_source, bijection_verdict and dependency_form.
- [x] Every normative atom of the structured source is entailed by docs/hardware: 8 base policies plus 2 aggregates/measures, 7 extended policies, 7 baselines, 35 factors with every tier, 3 retired clauses carried as retired for exactly their declared scopes, and 48 x 6 variant parameters. No unsourced claim was found.
- [x] All 5 prerequisite sentences are verbatim, in state form, only in their blocked hubs, and each hop resolves from the depended-on hub and the records.
- [x] No other problem's tool name, route, aggregated chain or task-mirroring title was found. No example figure equals a scored value.
- [x] Gate lines on record (snapshot, documents unchanged).
- [ ] XP-1 cross-product re-judge pending, once the ClearPath corpus renders.

XP-1 PENDING (cross-product, outside this skill's detection range): task1 re-issue total / approval deposit need ClearPath Professional's CSM/TAM and network-device coverage published in the ClearPath corpus.
KB VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=none

## revision_2

Round 2 re-audit (2026-10-18), requested after docs/managed (83 docs) and docs/licensing (57 docs) were published. revision_1 above is left untouched.

### Entry check
docs/hardware is unchanged: sorted-concatenation sha256 b7d1ae341a5bf2f34b893a8dd9349c1620cd9b0319cd50cf3570b90a0564281c, 68 files. hardware.extended.yaml is 4c40c1e11afdb94bcbce714e49a91930ede13ecea409c12223e5614dceb47d1d and task_tools.py is 565f6102036cdea86b10ae070733ec4ceeb8ca99ce7eff165aa4d8596b379e63, both unchanged. This revision is not blind (GT known since revision_1), as disclosed in the runtime files.

### XP-1 — closed
`docs/managed/tier_entitlements_matrix_ea1be37e.json` publishes, for every tier and matching `blueprint/products/managed.yaml` row by row, four entitlements:
- Microsoft 365 tenant administration
- firewall, switch and wireless configuration changes
- named client success manager
- named technical account manager

It uses the same phrases as the hardware factor docs, and it is the #2 KB_search hit (after the hardware factor doc) for the record words. ClearPath Professional reads CSM Yes, TAM No, network device changes Yes, tenant administration Yes. With that, task 1's re-issue total pins to 8586.26 and the approval deposit to 3968.92 from the visible surface alone. Task 0's security-preparation branch is resolvable too, and does not bind (no active E5). No conflicting statement exists in docs/managed or docs/licensing.

### Cross-product seed re-judge — source-side items
- **S1 (task 0; managed seed).** ClearPath monthly fee posted 2026-10-01, INV-310217, billing_period 2026-10, amount 2689.45, with the agreement balance_due of 2689.45. October 2026 is the current service month at frozen time 2026-10-07, and the scope conditions hold, so the published monthly seat-pricing schedule governs. `monthly_fee_csp_licensing_terms` gives 1.5 percent off for 19 active Business Premium licenses against 19 seats; no other credit or flat charge applies. The fee the rules produce is 2649.11, not 2689.45. Scored impact: none (the hardware endpoint relief reads seat rate x seat count, not the ledger fee).
- **S2 (tasks 0 and 1; managed seed).** Every seeded ClearPath late fee lies in the scope of the published late-fee schedule (`monthly_late_fee_assessment`): it was the agreement's only unpaid invoice at the end of the day before assessment. Yet each was booked at the base 1.5 percent amount. Under the schedule (balance bands, rate by payment record, recent-payment courtesy, tenure minimum, no relationship courtesy) the amounts are:
  - task 0: 2025-10-01 INV-310119 is 13.84 (seeded 40.34); 2026-06-01 INV-310175 is 20.75 (seeded 40.34);
  - task 1: 2025-09-01 INV-311141 is 18.08 (seeded 57.33); 2026-02-01 INV-311176 is 27.12 (seeded 57.33); 2026-07-01 INV-311211 is 27.12 (seeded 57.33).

  The payment rows that settle those invoices (2729.79 x2; 3879.18 x3) carry the same discrepancy. Scored impact: none. The hardware factors count late-fee entries by posting date, and the published rules post the same entries on the same dates.
- All other cross-product seed rows are consistent with the published owning-product rules:
  - ClearPath rates, term discounts, onboarding waiver, term dates, prorations, tier changes and their rates/effective dates, pre-current-month monthly fees, late-fee timing;
  - Microsoft 365 prices, cycle charges, renewal and expiry, auto-renew, the absence of administration fees under ClearPath tenant-administration coverage;
  - the Quick Start Project deposit.
- Hardware's own seed rows, including the HQ-053118 deposit of 2568.56, also agree with docs/hardware.

### Per-task part verdicts (revision_2)
| Task | Runtime | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS (now unconditional; XP-1 closed) | PASS | PASS |

kb: no hardware KB defect; nothing regressed (docs/hardware byte-identical to revision_1). src: S1, S2 (seed rows the published managed rules would not produce; no scored value moves).

KB VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=S1,S2

## revision_3

Round 3, a seed-only confirm (2026-10-18). revisions 1-2 above are left untouched.

**Gate.** The policy-side tail line reads exactly `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN`. (The earlier round-3 dispatch was BLOCKED on `VERDICT revision_6: task0=RED:T0-R6-F1 ...`; nothing was written then.)

**Snapshot.** Output of `/tmp/erl0069_coord/kb_snapshot.sh hardware_procurement_orders hardware`, run 2026-10-18T16:05:31:
- check_docs: DOCS OK
- check_traceability: TRACEABILITY OK (non-OK lines: 0)
- check_extended rc=0 EXTENDED OK; check_task_tools rc=0 TASK TOOL CONTRACT OK; replay_tasks rc=0 REPLAY OK; check_solvability rc=0 SOLVABILITY OK; check_compute rc=0 COMPUTE OK; check_grounding rc=0 GROUNDING OK; check_cross_fire rc=0 SCOPE OK
- 0.runtime.json sha256=f27e6651...8ce3; 1.runtime.json sha256=5857e2dc...cee
- hardware.extended.yaml sha256=4c40c1e11afdb94bcbce714e49a91930ede13ecea409c12223e5614dceb47d1d (unchanged)
- task_tools.py sha256=565f6102036cdea86b10ae070733ec4ceeb8ca99ce7eff165aa4d8596b379e63 (unchanged)
- docs/hardware: 68 files, tree sha256=b7d1ae341a5bf2f34b893a8dd9349c1620cd9b0319cd50cf3570b90a0564281c (unchanged; no re-render)

**S1: closed.** Every task-0 ClearPath monthly fee now matches the published monthly-fee rules applied at its posting day: 2649.11 from 2025-04 with the CSP 1.5 percent credit; 2689.45 for 2025-02/03; 1623.36 in the Essentials era. revision_2 had scoped S1 to the 2026-10 fee only. The event-time reading (the same one used for S2) covers all fees from 2025-04, which is what the re-seed carries. See policy_kb/0.md revision_3.

**S2: closed.** The five ClearPath late fees and their settling payments now equal the published schedule:
- task 0: 13.68 and 20.53 (recomputed on the corrected 2649.11 balance);
- task 1: 18.08, 27.12 and 27.12.

Scope and timing are unchanged.

**No moved scored value.** GT is unchanged (task 0 543.07 / 5080.40 / 1258.06; task 1 718.97 / 2110.35 / 8586.26 / 3968.92). Every hardware factor input drawn from ClearPath rows is unchanged: tier, seats, rate, late-fee posting dates, task 1's latest monthly fee 3821.85. Each value is still uniquely reachable from the visible surface.

**No new defect, nothing regressed:**
- The hardware KB and source are byte-identical to the earlier revisions.
- The licensing, project and hardware seed rows are unchanged.
- XP-1 remains closed.

KB VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=none

## revision_4

Round 4: cross-product re-judge with every product published (2026-10-18). revisions 1-3 above are left untouched.

**Snapshot.** Output of `/tmp/erl0069_coord/kb_snapshot.sh hardware_procurement_orders hardware`, run 2026-10-18T17:35:12:
- check_docs: DOCS OK
- check_traceability: TRACEABILITY OK (non-OK lines: 0)
- check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding / check_cross_fire: all rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK)
- 0.runtime.json f27e6651...8ce3; 1.runtime.json 5857e2dc...cee
- hardware.extended.yaml 4c40c1e11afdb94bcbce714e49a91930ede13ecea409c12223e5614dceb47d1d (unchanged)
- task_tools.py 565f6102036cdea86b10ae070733ec4ceeb8ca99ce7eff165aa4d8596b379e63 (unchanged)
- docs/hardware: 68 files, tree b7d1ae341a5bf2f34b893a8dd9349c1620cd9b0319cd50cf3570b90a0564281c (unchanged)

Published corpora on disk: backup 17, hardware 68, licensing 57, managed 83, project 65, security 20, timebank 63.

**Re-judge (details in policy_kb/0.md and 1.md, revision_4).**
- **Project rows** (task 1, d4f3564d): class band, pricing model, validity, 50 percent fixed-fee deposit, net-15 payment, kickoff lead time with the holiday calendar, and status are all consistent with docs/project.
- **Licensing rows** (task 0, Business Premium and E5): prices, cycle charges, renewal and expiry, auto-renew, payment terms, and no administration fee under ClearPath tenant-administration coverage are all consistent with docs/licensing.
- **TimeBank rows:** none in either world (no blocks, no order forms). The same holds for Sentinel and Continuum.
- **ClearPath rows:** unchanged since revision_3 and still consistent with docs/managed (governing sentences re-verified in the current corpus).
- **Look-back windows:**
  - Every ClearPath late-fee window (12 / 3 / 1 months) and every tenure count lies inside the seeded history (task 0 go-live 2024-03-11, earliest window start 2024-10; task 1 go-live 2023-11-13, earliest window start 2024-09). The same holds for the hardware 12-whole-month late-fee windows.
  - ClearPath renewal look-backs apply only at renewal, after the frozen time in both tasks (term ends 2027-03-10 and 2026-11-12), and no pre-renewal row is required.
- **No conflict with the hardware docs** from any newly published corpus. TimeBank's installation schedules read hardware order types, consistent with hardware's "onsite installation is never part of an order".

**revision_3 conclusions hold.** S1 and S2 closed; XP-1 closed; no scored value moved (task 0 543.07 / 5080.40 / 1258.06; task 1 718.97 / 2110.35 / 8586.26 / 3968.92), and each is still uniquely reachable from the visible surface. No new defect; nothing regressed. src members: none.

KB VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=none
