# KB-doc policy audit — project_engagements (product: project)

## revision_1

### freeze record (written before any source-layer read, 2026-10-18T13:05:45Z)
- runtime_context/project_engagements/0.md blind_answer frozen, file sha256=3f8ab16d907529f173312598e376ce24e7d7525dae8e1c169ea8369ab9945377
- runtime_context/project_engagements/1.md blind_answer frozen, file sha256=3d375d72be5822a615f0d572379dc76a4c2fb2b20ccc11f68612d430038a80c7
- Up to this line nothing under tasks/project_engagements/ (extended yaml, task_tools.py, tasks/*.json), plan.md, worklog.md, masked views, or audits/ (except the policy verdict tail line) was opened.

### entry conditions (Step 0, cited from the coordinator brief; auditor ran neither gate)
- Policy-side verdict tail line read: `VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN`.
- check_docs: DOCS OK; check_traceability: TRACEABILITY OK (non-OK lines: 0); check_extended / check_task_tools / replay_tasks --check / check_solvability / check_compute / check_grounding / check_cross_fire rc=0 (coordinator snapshot 2026-10-18).
- Runtime views 0.runtime.json sha256=e415d0a0f17e73a944b85ea6476a42740c1a8752acdafc521e833ef2de848fe2 and 1.runtime.json sha256=225d46ebf10a046659cd760a62889401881134d5401f262be10d06bb4e7d16dd re-hashed: match.
- docs/project: 65 files; `cat docs/project/* | sha256sum` = 1d4bc93efdaa3abd5f58d3223419eb6a48e31e5230cb07e8bc6c4e090892d709: match.
- DB access path supplied and used (tool-shaped). Entry conditions complete.

### reveal
- 2026-10-18T13:06Z: project.extended.yaml sha256=43eec9bdb4f65e545f7965bf12aaf587469d03204cdc6d82887da18692c91a3d and task_tools.py sha256=543e7e166bba6ccee087e379ace103f888cbc136b718e51bd33e42e57619c513 re-hashed: match the brief. tasks/0.json and 1.json read after the freeze.

### per-task part verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Files |
|---|---|---|---|---|
| 0 (deposit on T&M SOW-043715) | PASS (13.1 / 14077.80 = GT) | PASS | PASS | runtime_context/project_engagements/0.md, policy_kb/project_engagements/0.md |
| 1 (restart charge on SOW-044310) | PASS (50592.00 / 8205.76 / 354.87 / 3935.13 = GT) | PASS | PASS | runtime_context/project_engagements/1.md, policy_kb/project_engagements/1.md |

### closing checklist
- Audit files one per task per view; this is revision_1 (no older revision under project_engagements).
- Every normative atom of the six extended policies and the governing base policies is carried at equal strength; all seven retired clauses are rendered as retired, nothing else is retired; every factor ladder (32 factors) is carried in full in its own document and is findable from record words.
- Four prerequisite sentences, each verbatim (state form) in the blocked policy's hub only; every hop state-derived in the blind audits; no other problem's tool, route or chain anywhere.
- Gates: the auditor did not re-run check_docs / check_traceability (brief: "Do not run check_traceability yourself"); docs/project is byte-identical to the coordinator snapshot (tree sha256 1d4bc93e…2d709 re-computed at close), so the snapshot lines stand: `check_docs: DOCS OK`, `check_traceability: TRACEABILITY OK (non-OK lines: 0)`.

### policy-side notes (no KB verdict)
- N1. Generic combination sentences in the computation documents ("Where it is made up of more than one percentage…", "Any multipliers…", "Any scaling factors … any amounts added…", "Any percentage points…", "Any retainage…", the 5.0 deposit floor) come from the source rules' "The adjustments below combine in one way only…" / `result` bindings. They name no factor and fix non-commuting order; carried as the source states them. Placement note only.
- N2. Renderer note judged (change-order-fee and remobilization computes do not test fixed-fee scope; remobilization compute does not test hold > max_client_hold_days): inside each policy's own scope (fixed-fee engagement, client-caused hold longer than the hold limit) the computes coincide with the rules — `rco_ok` tests hold > limit and registration on/after resumed_date; `span_fee` for a hold under 1.5× is the class fee; `co_fee_net` tests registration. Outside that scope the policies do not apply (rules say "and only for such…"), so the compute is never the figure of record there. Both scored worlds are in scope (fixed fee; 136 > 90 days). **No rule-vs-compute case opens; not listed under src.**

### source-side items (src)
Exhaustive pass over every cross-product seed row of both tasks, judged against the published docs of the owning product (managed, hardware, security; TimeBank has no published corpus, checked against blueprint/products/timebank.yaml). Rows that match: ClearPath seat rates (189.00 × 0.95 = 179.55; 149.00 × 0.97 = 144.53), onboarding (Premier 36 months waived; Professional 120 × 75.00 = 9000.00), baseline prorations (8977.50; 17343.60, billed on the next monthly invoice), payment application by named invoice, late-fee timing (each assessed on the first first-of-month past grace), Hardware Procurement unit prices (22 − 3 points markup: 224.91, 490.28), quote totals (+15.00 handling), final invoices, hardware late fees (1.5 % → 81.19, 44.35), Sentinel MDR Standard rates (36-month 6 %, no bundle on the 2024-01-08 order date: 10.72 / 22.56), Sentinel onboarding 750.00 minimum and monthly 604.80, TimeBank block prices (3160.00; 6000.00 less 3 % = 5820.00) and grants. Rows that do not match:

- **S1 (task 0, moves gold).** ClearPath monthly fee rows of agreement f264dae4 (every `managed_monthly_fee` 8977.50, in particular INV-044031 posted 2026-10-01, which is the whole `balance_due_usd` 8977.50) are priced at the base rule (179.55 × 50). The published ClearPath monthly-fee documents put each such fee (current service month at its posting, no seat change in the month, no F3/Business Premium) under the monthly seat-pricing schedule: monthly_fee_sentinel_bundle_terms (active Sentinel MDR Standard, 36-month term, 52 enrolled endpoints ≥ 50 seats → 3.0 % off), volume_price_break_on_monthly_fees (seats 40–50: 11 × 2.0 / 50 = 0.44 % off), server_management_fee (4 servers on the Sentinel ledger → 4 × 60.00 = 240.00 flat), assembled per monthly_seat_amount §4 → RND(8977.50 × 0.9656) + 240.00 = **8908.67**. With a balance due of 8908.67 below the 8977.50 monthly seat charge, clearpath_open_balance_deposit_loading gives 2.5 points, not 5.0: deposit percentage 27.5, deposit 27.5 % × 46926.00 = **12904.65** instead of the scored 14077.80. (Holds under either reading of "current service month": the 2026-10-01 row is the current month at the frozen time.) The matching payment rows carry the same base amounts.
- **S2 (task 1, no gold move).** ClearPath monthly fee rows of agreement f75a407f (17343.60 = 144.53 × 120, 2025-08 … 2026-10) — the published schedule gives volume break (35 × 2.0 + 46 × 4.0) / 120 = 2.1167 % off → **16976.49**; no Sentinel/Continuum/M365 records. No task-1 factor reads ClearPath amounts (tier, seats and late-fee counts only), so no scored value moves.
- **S3 (both tasks, no gold move).** All four ClearPath late-fee rows are priced at the base 1.5 % of the whole balance, yet each sits in the scope of the published late-fee schedule (monthly_late_fee_assessment: the agreement's only unpaid invoice at the end of the previous day): task 0 INV-044015 2025-08-01 134.66 → **19.50** (rate 1.0 % — no late fee, 11 payments in 12 months; balance bands 10.00 + 20.00 = 30.00; recent payment 25 % + Sentinel relationship 10 % off; minimum 10.00 at 16 months); task 0 INV-044026 2026-07-01 134.66 → **29.25** (1.5 %; 45.00; 35 % off; minimum 5.00); task 1 INV-045103 2025-10-01 520.31 → **35.00** (1.25 %; 37.50; 25 % off = 28.13; tier minimum 35.00 at 3 months); task 1 INV-045108 2026-03-01 260.15 → **35.00** (1.5 %; 45.00; 25 % off = 33.75; minimum 35.00 at 8 months). The late-fee counts the project factors read are unchanged, so no scored value moves; the matching late-fee payment rows follow the same amounts.
- **S4 (task 0, cosmetic, authoring text).** tasks/0.json computations[1].factor_trace carries stale proof text: "client_standing … -> one_late_deposit_pct 20" (no such parameter; the rule takes one_late_off_pts 5.0 off deposit_pct 25) and "est_fees … (rate discount locked at step 8)" (the signature is evaluation step 19). Expected values are unaffected.

KB VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=S1,S2,S3,S4

## revision_2

### gate and snapshot (2026-10-18T16:07Z)
- Policy tail line read: `VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN` — gate met.
- `/tmp/erl0069_coord/kb_snapshot.sh project_engagements project` executed (not read): `check_docs: DOCS OK`; `check_traceability: TRACEABILITY OK (non-OK lines: 0)`; check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding / check_cross_fire rc=0; 0.runtime.json sha256=e415d0a0…848fe2, 1.runtime.json sha256=225d46eb…16dd; project.extended.yaml sha256=43eec9bdb4f65e545f7965bf12aaf587469d03204cdc6d82887da18692c91a3d; task_tools.py sha256=543e7e166bba6ccee087e379ace103f888cbc136b718e51bd33e42e57619c513; docs/project 65 files, tree sha256=1d4bc93efdaa3abd5f58d3223419eb6a48e31e5230cb07e8bc6c4e090892d709 — all identical to revision_1: seed-only round, no re-render.

### S1–S4 closure (verified through db_query.py against the published docs)
- **S1 closed.** Task 0 ClearPath monthly fees are all 8908.67 = RND(8977.50 × (1 − 0.0344)) + 240.00 (Sentinel bundle 3.0 % — active MDR Standard, 36 months, 52 enrolled ≥ 50 seats; volume break 0.44 %; 4 servers × 60.00); May 2024 payment 17886.17 = 8977.50 proration + 8908.67. The reworker kept the deposit by changing the 2026-09-24 payment on INV-044030 to `CHK 32104`, check, 8800.00. Checks of that row:
  - Rules: payment_application_rules 1 (applied to the invoice its remittance names) and 3 (partial payments accepted, rest stays open); INV-044030 posted 2026-09-01, Premier net 30 → due 2026-10-01, grace 10 days → no late fee can be assessed before 2026-11-01, none is on the ledger; far below the 60-day suspension threshold. Rule-consistent.
  - Realism: a single rounded check short-paying one invoice by 108.67 after a run of ACH payments is an ordinary AP short-pay; nothing in the managed docs or the persona contradicts it (the caller is never asked about ClearPath). Acceptable.
  - Effect: balance due 9017.34 = 8908.67 (INV-044031) + 108.67 → open-balance +5.0 (≥ 8977.50); ACH payments in six months fall from 4 to 3 (06-24, 07-24, 08-25) → still "3 to 5" → −2.5. Re-derived deposit 30 % × 46926.00 = **14077.80**, uniquely reachable (runtime_context/…/0.md revision_2); equals GT.
- **S2 closed.** Task 1 monthly fees 16976.49 (volume break 254 / 120 = 2.1167 %; no Sentinel, Continuum or M365 records); INV-045103 payment 34320.09; balance due 16976.49.
- **S3 closed.** Late fees recomputed under the published late-fee schedule match: task 0 19.50 (2025-08-01; 1.0 % — 11 payments, no late fee in 12 months; bands 30.00; 25 % + 10 % off) and 29.25 (2026-07-01; 1.5 %; 45.00; 35 % off); task 1 35.00 and 35.00 (28.13 and 33.75 below the 35.00 tier minimum at 3 and 8 months). Matching payment rows carry the same amounts. Late-fee counts unchanged.
- **S4 closed.** tasks/0.json factor_trace now reads "one_late_off_pts 5.0 taken off deposit_pct 25 = 20" and "rate discount locked at step 19"; ACH and open-balance lines updated to the round-2 records.

### regression and new-defect sweep
- Every ClearPath row of both tasks re-checked against the published managed rules (seat rates, onboarding fee / waiver, baseline prorations, monthly seat-pricing schedule and its factors, late-fee timing, scope and schedule, payment application): all match. Hardware, Sentinel, TimeBank and project rows unchanged from revision_1 and still matching.
- Scored values unchanged in both tasks (task 0: 13.1, 14077.80; task 1: 50592.00, 8205.76, 354.87, 3935.13); every factor tier re-derived from the visible surface.
- No doc of any product contains a scored value or a round-2 seed figure (9017.34, 8908.67, 8800.00, 108.67, 16976.49, 34320.09, 19.50, 29.25, 14077.80, 13.1, 50592, 8205.76, 354.87, 3935.13).
- Per-task part verdicts round 2: task 0 KB-RUNTIME PASS / KB-BIJECTION PASS / KB-EXPLICIT PASS; task 1 the same. Policy-side notes N1, N2 unchanged.

KB VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=none

## revision_3

### snapshot (executed, not read; 2026-10-18T17:32:36)
`check_docs: DOCS OK`; `check_traceability: TRACEABILITY OK (non-OK lines: 0)`; check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding / check_cross_fire rc=0; 0.runtime.json sha256=e415d0a0…848fe2; 1.runtime.json sha256=225d46eb…16dd; project.extended.yaml sha256=43eec9bdb4f65e545f7965bf12aaf587469d03204cdc6d82887da18692c91a3d; task_tools.py sha256=543e7e166bba6ccee087e379ace103f888cbc136b718e51bd33e42e57619c513; docs/project 65 files, tree sha256=1d4bc93efdaa3abd5f58d3223419eb6a48e31e5230cb07e8bc6c4e090892d709 — unchanged. docs/timebank now 63 files (tree sha256 6368ac29…). Task worlds re-queried: task 0 ClearPath balance due 9017.34, task 1 16976.49 — same as revision_2.

### TimeBank re-judge against the published docs/timebank/ (task 0 only; task 1 has no TimeBank block, order, ledger or billing row)
| Rows | Published rule | Result |
|---|---|---|
| Orders 2025-09-08 (20 h), 2026-02-02 (40 h), 2026-07-06 (20 h); all `request_type new_block`, signed | block_ordering_and_price_terms / block_price_and_invoice_schedule: list price less the size's ClearPath discount for an active agreement at rank ≥ 3; repeat-order basis only for a form quoted against a current block of the same size (repeat_block_order_signing) | 20 h: 3160.00 (0 %) ✓; 40 h: 6000.00 × 0.97 = 5820.00 (Premier, rank 5) ✓; 2026-07-06 20 h: the order form is a new-block form, not quoted against block 872d156b, so the standard rule applies → 3160.00 ✓ (the repeat-order schedule is not engaged) |
| Block invoices INV-044066 / 044067 / 044068 and their payments | invoiced on the order date; 20 h due on receipt, 40 h due in 15 days; late fee only on a first-of-month past 5 grace days | each paid in full before the next first of the month (09-12, 02-09, 07-10) → no late fee due, none posted ✓ |
| Activation / grants (2025-09-12 20 h, 2026-02-09 40 h, 2026-07-10 20 h) | activation_validity_and_cancellation: full-payment sizes activate when the invoice is paid in full; activation grants the size's hours | activation dates = full-payment dates; grants equal block hours ✓ |
| Expiry dates 2026-09-11, 2027-02-08, 2027-07-09 | 12 months for 20 h and 40 h; expiry = day before the anniversary | ✓ |
| Draws SB-4108841 12.00, SB-4111207 3.00, SB-4113920 5.00 + 3.00, SB-4114458 6.50, SB-4117733 9.00, SB-4119055 4.00 | remote_support_session_draws + remote_session_block_hours and its schedules (band, call-out/weekend, ClearPath after-hours rate, handling level, minimum) | every ticket: service_request, portal, P4, weekday 16:30 business-hours resolution, technician → minutes 720/180/480/390/540/240 already multiples of the 15-minute increment, above the 15-minute minimum, ratio 1.0, multiplier 1 (no weekend, no after-hours class, no call-out; Premier never after-hours) → hours = minutes / 60 ✓; dated the resolution date ✓ |
| Draw order and depletion | draw_order_and_overage: earliest expiry first; split at zero; depleted the same day | 2026-03-12 drawn from 872d156b (expiry 2026-09-11) before 2b3b2648; 2026-04-14 split 5.00 / 3.00, 872d156b depleted 2026-04-14 ✓; later draws from 2b3b2648 (expiry 2027-02-08) before 3fd7ac60 ✓; balances 0.00 / 17.50 / 20.00 ✓ |
| Rollover / extension | validity_extension_rollover_terms | no rollover source, no extension, nothing owed; the 2026-07-06 block was ordered 67 days before 872d156b's expiry (outside the 60-day window, and 872d156b had no hours) ✓ |
| The tickets themselves (managed ticket history) | managed ticket_labor_settlement_rules: billable out-of-scope remote labor settled from a prepaid block | `labor_route timebank`, billable minutes equal the drawn minutes ✓ |

### look-back windows that reach before the seeded history
- Task 0: prepaid-hours grants window 2025-10-15…2026-10-15 lies inside the seeded TimeBank history (first order 2025-09-08; no row implies an earlier block — first order is a new block with no rollover source). ACH six-month and ClearPath twelve-month windows lie inside the ClearPath ledger (from 2024-05); the hardware twelve-month window (from 2025-10-15) lies inside the seeded hardware history (from 2025-06). The managed late-fee schedule's 12-month payment/late-fee look-back for 2025-08-01 reaches 2024-08-01, inside the ledger.
- Task 1: the managed late-fee look-back for 2025-10-01 reaches 2024-10-01, before the agreement was signed (2025-05-12); the client holds a single ClearPath agreement (one agreement per client) and no earlier ClearPath, TimeBank or hardware record exists, so the counts (2 payments, no late fee → 1.25 %) are the complete counts. Project twelve-month windows (from 2025-10-14) lie inside the engagement and ClearPath history.
- No window is truncated by the seeded history in a way that changes a tier.

### revision_2 cross-product pass re-confirmed
- Managed, hardware and security rule sentences relied on in revision_2 re-verified present verbatim in the current published docs (Sentinel bundle 3.0 %, volume break 2.0 / 4.0, server fee 60.00, late-fee schedule scope, rate-by-record, bands, courtesies, tenure minimum, partial payments, Premier 189.00, accessory order terms, Sentinel combined discount). Every ClearPath, hardware and Sentinel row of both tasks still matches; S1–S4 stay closed.
- No doc of any product (seven corpora) contains a scored value or a round-2 seed figure (14077.80, 13.1, 50592, 8205.76, 354.87, 3935.13, 9017.34, 8908.67, 16976.49).

### src members
- None. (Cross-product seed rows re-judged in this round: TimeBank orders 3, block invoices 3, payments 3, grants 3, draws 7, tickets 6 — task 0; task 1 has no TimeBank rows. All match the published rules.)
- Per-task part verdicts round 3: task 0 and task 1 — KB-RUNTIME PASS, KB-BIJECTION PASS, KB-EXPLICIT PASS. Notes N1, N2 unchanged.

KB VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=none
