# KB verdict — bed_hold_and_leave_reservations (product bedhold)

## revision_1 (2026-10-23)

Entry conditions: policy-side `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN`; gate snapshot re-run 2026-10-23T04:57:49 via /tmp/erl0074_coord/kb_snapshot.sh — EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK; [check_docs bedhold] DOCS OK; [check_traceability] TRACEABILITY OK (0 misses). Runtime views sha256 967ee5a3…0955 / 8bedf6a7…65b7; extended yaml 4718b6c8…cdbda; task_tools 788ee1d3…cd4f4; docs/bedhold 50 files tree 88bc62df190873bb. Blind audits frozen before reveal; no contamination.

| Task | Runtime blind audit | Two-way scan | Dependency form |
|---|---|---|---|
| 0 (therapeutic closing ← opening, stay) | PASS — 9,118.20 / 6,663.30 / 4,720.20, days 26/19/15, order {A,B}→C, all = GT | PASS | PASS |
| 1 (hospital closing ← opening) | PASS — 7,715.40 / 4,059.90, days 22/13, order ho→hc, all = GT | PASS | PASS |

Closing checklist: audit files one per task (runtime_context/…/task{0,1}.md, policy_kb/…/task{0,1}.md); every prerequisite sentence verbatim in its blocked hub only (tc_hub ×2, hc_hub ×1), state form, resolvable from the depended-on hub's definition + ledger; every factor ladder (to 4, hs 6, tc 5, ho 5, hc 6) carried tier by tier in its own document, reachable by the record words (isolation_placement, rate_notice_delivered_date, return_date/release_date, payer_reserved entries) or the result's name; fall-backs definite and different; retired clause carried as retired; no tool/route/aggregation beyond the sentences; check_docs / check_traceability lines above.

Focus checks requested:
- Unlock schemas: each hub names its own tool and the correct unlock path (post_* → unlock_agent/call_agent; sign_* → unlock_user); parameter tables, receipts and errors equal task_tools.py.
- Doc examples vs scored values: no example or table equals a scored value or mirrors a task world. Observations only: payer_reserved_day_limits' hypothetical "12 per hospitalization | 9 | 3" shares figures with task 1's intermediates in different roles under a different limit; hs_rate's hypothetical 60 notice days equals the unpublished private figure (hs result N-independent in task 0).
- Factor docs: none names another factor or the computation document; each names the result it modifies.
- Fall-back test: to 11,336.00, hs 10,464.00, tc 8,284.00, ho 10,900.00, hc 7,412.00 — computable from the computation doc alone, definite, ≠ answer.
- Owed-at-once writes: (i) bedhold base day-counting rule calls reversals owed (task 1: 09-06..09-08 payer-covered days on the opening entry, 10-15..10-17 after return; task 0: 07-28..07-31 after the July return) — no published document exposes a tool for a reversal, so none can be made mid-conversation (had one been made, task 1's opening would read 19 charged days); (ii) published medicare/medicaid/ancillary/therapy writes land only in their own tables, while every scored read is holding-scoped bedhold ledger/reservation + the private agreement — none can move; Ruth holds no record in those products, Harold's medicaid case (Nov patient pay open) cannot touch bedhold reads; (iii) private writes — **conditional** (private unpublished).

Conditional (private / trust unpublished):
- C1: rate-change notice days (60 on every private tier) is read by every *_rate_binding factor as "the agreement's rate-change notice days" but is on no record and in no published document; task 0's closing charge (4,720.20) depends on it (task 0's opening holds for N ≥ 48, its stay for any N; task 1 holds for N ≥ 44). The private corpus must render it for the Private Long-Term Care Room tier in words a reader can link to the agreement's rate notice. Task 0's private ledger (398.00 from 2026-10-13 = 2026-08-14 + 60) corroborates it.
- C2: the private corpus's isolation-billing tier and "current agreement" selection must agree with bedhold's restatement in the *_iso documents.

Source-side problems (do not change the KB verdict):
- S1 (rule ≠ compute, all five policies, *_isolation_rate): the rule sentence "the agreement having recorded the center's infection-control move before the leave" reads as a condition, but the compute (to/hs/tc/ho/hc_dep_tier) tests only isolation_placement, the agreement's tier and the room held — no date test. Both task worlds have the move before the leave, so no scored value moves; domain-wide, a placement recorded after the leave is priced at the isolation tier by compute and at the room's own tier by the text.
- S2 (wording gap, all *_rate_binding): neither rule nor documents state in words where a rate notice delivered on or after the 2026-07-01 schedule date falls; compute puts it in row 1 (DAYS(schedule, notice) + N > 0). Both task worlds sit on that unstated case (notices 2026-08-14, 2026-08-31). The natural reading ("fewer than the notice days before") gives the GT; the alternative "otherwise" reading gives 9,464.00 / 6,916.00 / 4,863.00 (task 0) and 8,008.00 / 4,214.60 (task 1). The private charter's rate_effective_basis (later_of_schedule_date_and_notice_plus_notice_days) closes it once rendered.
- S3 (assembly hints in the baseline, XF A3 class): each policy's generic combination sentence ("each schedule rate is first taken to the applicable percent, any per-day credit is then subtracted … the days not charged at the end of the entry are its last days") must live in the computation document, so every baseline document announces that percents, per-day credits and end-of-entry exclusions exist; the hospital opening rule's sentence further names a factor quantity ("as many as the larger of those held before the notice and those payer-covered"), which the KB renders generically ("more than one ground"). Source-originated; not a rendering addition.
- S4 (parameter naming): `payer_days_never_billed_to_resident` is False on every tier while its description ("Whether reserved days the payer pays are ever billed to the resident") and the base rule ("never billed") mean the opposite of its name; the KB follows the description (payer_day_coverage_tiers "… ever billed to the resident | No").

KB VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=S1,S2,S3,S4

## revision_2 (2026-10-23, re-audit round 2)

Entry: RENDER.log tail "RENDER round 2: DOCS OK"; kb_snapshot 2026-10-23T06:25:36 — EXTENDED/TASK TOOL CONTRACT/REPLAY/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK; [check_docs] DOCS OK; [check_traceability] TRACEABILITY OK (0 misses). Hashes: runtime views unchanged (967ee5a3…0955 / 8bedf6a7…65b7); extended yaml f9fc40ef…b2de (was 4718b6c8…); task_tools unchanged 788ee1d3…; docs/bedhold 50 files, tree 24cc3f6db0001c26 (was 88bc62df190873bb).

| Item from revision_1 | Status |
|---|---|
| KB items | none were RED in revision_1; no regression on the round-2 corpus |
| S1 isolation move-date clause not computed | closed — rule, ladder and compute (last_room_change_date ≤ departure) agree; all five *_iso docs carry it with every tier and the date boundary |
| S2 post-07-01 rate notice unstated | closed — row 1 "or on or after" in rule/ladder and all five *_rate docs; D-case list correct |
| S3 combination sentence in baseline docs | decided (placement); unchanged |
| S4 payer_days_never_billed_to_resident naming | BLUEPRINT-KNOWN; unchanged |
| Example observations (payer-limit 12/9/3 row; 60-day rate example) | gone; no example equals a scored value or mirrors a task world |
| C1 rate-change notice days (private, unpublished) | still conditional |

Per task: task 0 runtime PASS (9,118.20 / 6,663.30 / 4,720.20, unchanged GT) / bijection PASS / dependency PASS; task 1 runtime PASS (7,715.40 / 4,059.90) / bijection PASS / dependency PASS. Revision_2 runtime sections are non-blind re-derivations (disclosed). New source items: none.

KB VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=none

## revision_3 (2026-10-23, round 3 — cross-product re-judge)

Entry: all seven corpora published (docs/private 69 files, docs/trust present). kb_snapshot 2026-10-23T10:12:51 — EXTENDED/TASK TOOL CONTRACT/REPLAY/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK; [check_docs] DOCS OK; [check_traceability] TRACEABILITY OK (0 misses). Hashes unchanged since revision_2: runtime views 967ee5a3…0955 / 8bedf6a7…65b7; extended yaml f9fc40ef…b2de; task_tools 788ee1d3…; docs/bedhold tree 24cc3f6db0001c26 (no bedhold document changed). Scratch: /tmp/erl0074_kbaudit_bedhold/r3/.

| Item | Status |
|---|---|
| C1 rate-change notice days | settled: docs/private publish 60 days on every tier with the later-of rule; GT values follow |
| C2 private isolation billing tier / agreement selection | settled: consistent with the bedhold *_iso documents |
| Round-2 items (S1, S2 closed; S3 placement; S4 BLUEPRINT-KNOWN) | unchanged; bedhold corpus unchanged (tree 24cc3f6db0001c26) |
| Cross-product seeded rows | task 0: agreement + 32 private ledger rows, 31 OK, 1 not producible (S6); task 1: agreement (S5) + 14 private rows OK + medicaid case/request + 15 medicaid rows OK; tables in policy_kb/…/task{0,1}.md revision_3 |
| Owed-at-once writes | none can move a scored read: no published tool of any other product writes bedhold tables or the agreement fields the bed-hold factors read. Owed candidates found (task 0 additional deposit 420.00, customer-paid; task 1 agreement closing, no tool) touch nothing read |

New source/seed items:
- **S5** (task 1, load-bearing, plausible): the private corpus says a converted agreement with no private balance or deposit left is closed. Harold's agreement has had both at 0.00 since 2026-06-25 but is seeded payer_converted. Both bed-hold factors that read the agreement depend on that status: closed, the values would be 8,802.20 / 4,634.50 instead of 7,715.40 / 4,059.90. No tool can close it mid-conversation.
- **S6** (task 0, ledger exactness, not load-bearing): Ruth's 2026-07-10 payment 8ddea75c (11,904.00) names charge c0daf344, whose open balance after the 07-08 credit was 2,688.00. The private posting rule applies a payment only up to the open balance. Under the docs, the August charge's 7,296.00 remainder is past due, and the monthly late-charge rows it would draw are missing. No bed-hold computation reads it, and no tool posts late charges.
Observations (not routed): O1 the private corpus gives no precedence between the isolation and notice-hold charge bases; O2 the Medicaid tier's entry wording ("no spouse … in the community") versus the case's spouse representative (the placement rule followed); O3 the Medicaid ceiling versus "unchanged" for a month with no day in the centre.

KB VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=S5,S6

## revision_4 (2026-10-23, round 4)

Entry: RENDER.log tail "RENDER round 3: DOCS OK"; kb_snapshot (round 4) — EXTENDED/TASK TOOL CONTRACT/REPLAY/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK; [check_docs] DOCS OK; [check_traceability] TRACEABILITY OK (0 misses). Hashes: runtime views unchanged; extended yaml f9fc40ef…b2de and task_tools 788ee1d3… unchanged; docs/bedhold tree 24cc3f6db0001c26 unchanged; docs/private and docs/medicaid identical to the round-3 dumps. tasks/{0,1}.json rewritten 2026-10-23 10:43 (seed rework, round 8). Scratch /tmp/erl0074_kbaudit_bedhold/r4/.

| Item from revision_3 | Status |
|---|---|
| S5 Harold's converted agreement with nothing left (should be closed) | closed: the May charge's 384.00 remainder after the deposit application keeps the agreement open; payer_converted is what docs/private produce; gold unchanged |
| S6 Ruth's July payment above the open balance | closed: 2,688.00 = open balance; August paid in full plus the July re-bill; no past-due month, no late charge owed; account 16,716.00 reconciles |
| Observations O1–O3 | unchanged; not routed |
| KB items / bedhold corpus | none open; corpus unchanged (tree 24cc3f6db0001c26) |
| Cross-product rows | task 0: agreement + 33 private rows OK; task 1: agreement + 14 private rows + Medicaid case, request and 15 ledger rows OK |
| Owed-at-once writes | none can move a scored read |
| Gold | unchanged in both tasks; no re-derivation needed |

KB VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=none
