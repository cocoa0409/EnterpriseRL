# KB-doc policy audit — microsoft_365_subscriptions (product licensing, Microsoft 365 Cloud Subscriptions (CSP))

## revision_1

Auditor: erl-kb-doc-policy-audit agent, 2026-10-18 (independent of the renderer and of the policy-side auditor).

### Entry conditions (Step 0)
- Policy-side verdict (only the tail line was read before the freeze): `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN`.
- Gate snapshot supplied by the coordinator (2026-10-18T12:31:02, /tmp/erl0069_coord/kb_snapshot.sh): `check_docs: DOCS OK`; `check_traceability: TRACEABILITY OK (non-OK lines: 0)`; check_extended / check_task_tools / replay_tasks --check / check_solvability / check_compute / check_grounding / check_cross_fire all rc=0. Neither check was run by this auditor (per brief).
- Hashes re-measured at audit time match the snapshot: licensing.extended.yaml 0ab2f241…a2a4, task_tools.py faef8af4…1591, docs/licensing 57 files, tree 48d9fe95…db2e; runtime views 0.runtime.json fc1981eb…1eca, 1.runtime.json 9e3096d6…bec. The corpus is unchanged since the gates ran, so the snapshot lines stand as the closing record.
- Runtime view + DB access path supplied (db_query.py, tool-shaped). Blind audits are blind on the DB side. Input complete.

### Per-task verdicts

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Files |
|---|---|---|---|---|
| 0 (payment arrangement ← late charge ← reduction credit) | PASS (880.25 / 21.66 / 819.68 matched blind) | PASS | PASS | runtime_context/…/0.md, policy_kb/…/0.md |
| 1 (window cancellation ← {Sept admin fee, seat-addition charge}) | PASS (3.55 / 257.66 / 1892.41, INV-025611 matched blind) | PASS | PASS | runtime_context/…/1.md, policy_kb/…/1.md |

The blind answers were frozen to disk at 2026-10-18T12:38:57Z (sha256 0.md 4c2608e6…bfa3, 1.md a80de1b7…414c) before any source was read. contamination_disclosure: none. Every hop was state-derived; none was pre-solved. Every computation's fall-back (780.56, 41.55, 930.47; 269.28, 67.50, 1773.90) is definite and differs from gold.

### KB-side findings
None. kb=CLEAN. Weakest carriage (not RED): the cancellation cap. The computation document carries "It is never more than the charges billed for the cycle", while the prompt-cancellation document redefines "the license refund" without restating it. I judge the cap still applies to the case-A result, since the source's order clause says "the cap on the license refund applies to their result".

### Source-side items (src) — reported, not fixed

1. **reduction_credit_no_floor** (renderer note — agreed). The source baseline makes the credit "the prorated amount … less the standard license change fee of 25.00 USD", and the ClearPath Monitor tier nets 10.00. No floor is stated, and post_reduction_credit_23f8ed2c takes "a positive number". Example: on Microsoft 365 Business Basic P1M (unit 7.20), a 1-license reduction with 24 of 30 days left gives prorated 5.76, so the credit is −19.24 for a client without ClearPath and −4.24 for an active Monitor client. The rule does not say whether that floors at zero, is not posted, or becomes a charge. Not hit by task 0, where the fee is 0.00. The KB renders the source faithfully, and the openness is the source's.
2. **every_x_prerequisite_vs_latest_x_rule**. Three prerequisites wait on "every in-window reduction", "every seat addition recorded" and "the administration fee owed for every month … in force at month end". The rules that depended-on writes follow cover less than that:
   - the reduction credit and the seat charge price only "the … with the latest submission moment" in "the current term";
   - the admin-fee rule prices from the posting-day state ("purchased fewer than 30 calendar days before the posting day", "licenses … when the fee posts").
   A second uncredited reduction, an uncharged seat addition from an earlier term, or two missing months therefore has no defined amount. Also, a covered client's seat addition under the seven-day tail convention prices at 0.00 (no days, no provisioning fee), but the tool takes "a positive number", so the waited-on state "carries its partial-cycle charge" cannot be reached. Neither seed hits these cases.
3. **cancellation_baseline_license_work_hint**. The window-cancellation baseline.rule includes "Stratton Bay makes no license-work charge against the cancellation refund of a client holding a ClearPath agreement … that work being covered". Rendered as cancellation_refund_amount (5), this tells a fall-back reader that non-covered clients bear license-work charges. Only the order_reversal_fee and seat_change_reversals factors define such charges, so the computation document hints at variation. This is the source's own sentence, so it is not a KB defect.
4. **xprod_seed_managed_late_fees_t0** (cross-product seed rows). In task 0, ClearPath late fees of 39.06 sit on INV-020731 (posted 2025-09-01) and on INV-023402 (posted 2026-04-01). Each was 1.5% of 2604.00, the base rule.
   - The published managed docs put both under the ClearPath late-fee schedule: each invoice was "the agreement's only invoice with any amount unpaid at the end of the day before the assessment day".
   - That schedule's balance bands alone cap a 2604.00 balance at 27.03 (15.00 + 0.75% × 1604.00). The minimum is 5.00 (24+ months live).
   - For 2026-04-01 the rate is 1.5% (the 2025-09-01 fee is in the window) with a 10% recent-payment courtesy, giving about 24.33. For 2025-09-01 the rate is 1.25% (fewer than 10 payments) with a 10–25% courtesy, giving about 16.89–20.27.
   - The licensing escalation factor only counts these rows (one in the 12-month window), so the task-0 gold is unaffected.
5. **xprod_seed_managed_monthly_fees_t1** (cross-product seed rows). In task 1, the ClearPath Monitor monthly fees are 962.50 for 2026-09 and 1116.50 for 2026-10 (posted on the frozen day), both plain seats × 38.50.
   - The published managed scope sentence puts each under the monthly seat-pricing schedule: current service month, no seat change between the 1st and posting, no F3 or Business Premium subscription.
   - That schedule applies the Sentinel bundle credit (1.5%, 12-month term), the Continuum bundle credit (1.0%, no on-site appliance on Continuum Backup Standard) and the server management fee (2 Sentinel servers × 60.00). On my reading the October fee is about 1208.59, not 1116.50, and the agreement balance 1147.30 moves with it.
   - Licensing reads only the agreement's tier, status, seat_count and contracted_seats, so the task-1 gold is unaffected.
6. **gold_find_customers_legal_name**. Both tasks' gold first read is `find_customers(name=…)` with the full legal name ("Fenwick Hale Wealth Partners, LLC", "Granger Hollis Engineering, LLC"). The callers say only "Fenwick Hale Wealth Partners" and "Granger Hollis Engineering", and `find_customers(name="Fenwick Hale Wealth Partners")` returns "No client profile matches". This matters only if read-call arguments are scored; phone/email lookups reach the same profile.

### Closing checklist (Step 5)
- Audit files correspond one-to-one with tasks 0 and 1. This is revision_1; there are no earlier revisions.
- Every normative atom of the six extended policies and their base policies is entailed by docs/licensing. Retired clauses are written as retired with their replacements, and the other clauses stand in force. Every tier of all 29 declared factors is carried in its own document with figures. The four prerequisite sentences stand verbatim, state form, each only in its blocked hub. No route, aggregated chain or other problem's tool name appears.
- Coverage note: cross-product contradictions are outside this skill's verdict. The cross-product seed rows above were checked against the published managed docs as source-side items only.

KB VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=reduction_credit_no_floor,every_x_prerequisite_vs_latest_x_rule,cancellation_baseline_license_work_hint,xprod_seed_managed_late_fees_t0,xprod_seed_managed_monthly_fees_t1,gold_find_customers_legal_name

## revision_2

Re-audit round 2, 2026-10-18 (not blind; revision_1 text above left untouched).

### Gate
- (1) audits/policy_task/microsoft_365_subscriptions/_difficulty.md last line: `VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN` (exact).
- (2) licensing.extended.yaml mtime 2026-10-18 17:46:47; the re-rendered docs/licensing files are dated 18:04:58 (8 files; the other 49 are unchanged since 12:16). check_docs DOCS OK (below).
- An earlier round-2 request (gate revision_10, `charter=R10-1`, docs older than the yaml) was answered BLOCKED with nothing written.

### Snapshot (`/tmp/erl0069_coord/kb_snapshot.sh microsoft_365_subscriptions licensing`, executed, not read)
```
== kb snapshot microsoft_365_subscriptions / licensing @ 2026-10-18T18:05:31
check_docs: DOCS OK
check_traceability: TRACEABILITY OK   (non-OK lines: 0)
check_extended rc=0 :: EXTENDED OK
check_task_tools rc=0 :: TASK TOOL CONTRACT OK
replay_tasks rc=0 :: REPLAY OK
check_solvability rc=0 :: SOLVABILITY OK
check_compute rc=0 :: COMPUTE OK
check_grounding rc=0 :: GROUNDING OK
check_cross_fire rc=0 :: SCOPE OK
…/0.runtime.json sha256=fc1981ebedcec5cf9370b3998369f73157fba272467f65b876a49a7125a31eca
…/1.runtime.json sha256=9e3096d6368e5d8cdc6ed4f4bacead009770fd0fda1f1f867506368939c56bec
licensing.extended.yaml sha256=fb64a29060a24388f3b57fb52a9f93996efaa672e9034c2b49857e1bebd4aaa2
task_tools.py sha256=faef8af49769237d072f5b4419c073782c13255b65131f41c54ca57027e31591
docs/licensing: 57 files, tree sha256=4bb1599ae24d687f0ad844ff80d713afde265712315d9135a44b2e9f7739e649
```

### Changed documents (scanned both ways)
annual_invoice_late_charge, reduction_credit_amount, license_change_fee_by_clearpath_coverage, current_month_late_charge_in_arrangements, part_month_admin_fee, cancellation_refund_amount, seat_addition_partial_cycle_charge, whole_subscription_cancellation. Each new sentence maps to new source text, and no source change lacks a home. The three changed prerequisite sentences stand verbatim, in state form, only in their blocked hubs, and the payment-arrangement sentence is unchanged. Exact-string scans of all 57 docs found no scored value or intermediate, and each task tool name appears only in its own invocation block. task_tools.py is unchanged, so the unlock schemas are unchanged.

### Per-task verdicts (revision_2)
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS (re-derived 880.25 / 21.66 / 819.68 = gold) | PASS | PASS |
| 1 | PASS (re-derived 3.55 / 257.66 / 1892.41, INV-025611 = gold) | PASS | PASS |
No regression: every hop is still state-derived, the fall-backs are unchanged and differ from gold, and the new caps and zero-outcome tiers do not bind in either world.

### revision_1 source items: status
1. **reduction_credit_no_floor: closed.** The fee netted is never more than half the prorated amount (baseline + clearpath_change_fee), so the credit stays above 0.00.
2. **every_x_prerequisite_vs_latest_x_rule: closed.**
   - The prerequisites now wait on the latest in-window reduction, the latest seat addition and the month just ended, which are exactly what the depended-on rules price.
   - The zero-outcome cases are excepted in the sentences themselves, and the depended-on documents say "no fee is posted" and "carries no partial-cycle charge line".
   - Residual edge, not raised: an uncharged seat addition left over from an earlier term.
3. **cancellation_baseline_license_work_hint: open (unchanged, low).** cancellation_refund_amount (5) still says covered clients bear "no license-work charge". The new (4a) "Charges deducted from a cancellation refund never take, together, more than half …" also tells a fall-back reader that deductions exist, which only the factor documents define. Both are the source baseline's own sentences, so this is not a KB defect.
4. **xprod_seed_managed_late_fees_t0: closed.**
   - The ClearPath history was re-dated from signing (2024-03-11, go-live 2024-04-08). The late fees are now 16.16 (2025-09-01, INV-020205) and 24.24 (2026-04-01, INV-020254).
   - Each is the published ClearPath late-fee schedule on 2590.98, the only unpaid invoice:
     - 2025-09-01: rate 1.0% (no late fee in 12 months; ≥10 payments); balance bands 10.00 + 0.5% × 1590.98 = 17.955; 10% recent-payment courtesy; giving 16.16.
     - 2026-04-01: rate 1.5% (the 2025-09-01 fee is in the window); bands 15.00 + 11.932; 10% courtesy; giving 24.24.
     - Tenure minimum 10.00 (12–23 months).
   - Both figures rest on the reading that the same-day autopay is not counted in the 1-month window. The managed docs' wording ("entries dated fewer than N whole months before today") would also admit counting it (25%). That ambiguity is in the managed corpus, outside this difficulty's verdict, and noted only.
5. **xprod_seed_managed_monthly_fees_t1: closed.** The ClearPath Monitor fees now follow the published monthly seat-pricing schedule:
   - April 2025 – February 2026: 24 × 38.50 × (1 − 1.5% Sentinel − 1.0% Continuum) + 2 × 60.00 server fee = 1020.90.
   - After the 2026-03-01 renewal at 38.31 (−0.5% ticket volume): 1016.45.
   - 2026-09: 25 seats, 1053.81.
   - 2026-10: 29 seats, 1203.22.
   - The prorations are 38.31 × days/days-in-month (4.94, 12.77, 11.49, 3.83, 2.55); the onboarding fee is 25.00 × 24 = 600.00 (above the 495.00 minimum); the first-month baseline is 924.00; the balance is 1233.86.
6. **gold_find_customers_legal_name: closed.** Gold now looks the client up by phone 9195550231 (task 0) and by email trevor.esposito@grangerhollis.com (task 1), both stated by the callers.

### Cross-product seed re-judge (all published products: managed, licensing, security, backup, timebank, project, hardware)
- **Task 0.**
  - Licensing history is consistent with the licensing docs:
    - 2024 credit 761.69: 384.00 × 2 × 362/365, standard method, covered fee 0.00, no goodwill.
    - 2025-10-01 late charge 41.77 on INV-022314: 1.25% (one renewal) × 4050.00, giving 50.625, × 22/30 × 1.25 (the 2025-09-01 ClearPath fee) × 0.9.
    - Cycle charges 4608.00 (12 × 12 × 32.00) and 4050.00 (10 × 405.00); payments net to zero.
  - ClearPath:
    - Onboarding fee 1750.00 (the minimum; 21 × 60.00 is below it).
    - First-month proration 1996.40 (2604.00 × 23/30).
    - Monthly fees 2604.00 / 2590.98 / 2604.00. The renewal rates 123.38 (2025: −0.5% ticket volume, 5 tickets < 21 seats) and 124.00 (2026: −0.5% ticket volume + 0.5% late-fee history) follow the renewal docs.
    - Late fees as in item 4.
  - No other product records.
- **Task 1.**
  - Sentinel fee 523.10 (29 × 15.90 + 2 × 31.00). There is no ClearPath bundle discount, correctly, since the Sentinel order (2024-10-28) predates the ClearPath signing (2025-02-10).
  - Continuum fee 189.50 (2 × 59.00 + 22 × 3.25; Standard has 0% discounts).
  - TimeBank 20-Hour block 3160.00 (list; 0% ClearPath discount on the 20-Hour block); draws follow the technician ratio 1.0 with a 30-minute increment and minimum.
  - ClearPath as in item 5.
  - No project or hardware records.
- No row was found that the published docs would not produce, apart from the managed same-day-window ambiguity noted under item 4.

### Closing checklist (revision_2)
- All four audit files carry a revision_2 section; revision_1 is preserved.
- Every changed source atom has its home. Every prerequisite sentence is verbatim, in its declared form, in its blocked hub only. Every ladder is full. No route, aggregated chain or other problem's tool name appears.
- The snapshot above is the closing gate record.

KB VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=cancellation_baseline_license_work_hint
