# KB-layer audit — difficulty prepaid_maintenance_plans (product maintenance) — closing checklist

## revision_1 (2026-10-22)

### Entry conditions (Step 0)
- Policy-side verdict supplied: `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN`.
- Entry snapshot (`/tmp/erl0075_coord/kb_snapshot.sh prepaid_maintenance_plans maintenance`, 2026-10-22T07:47:34), re-run on the final form at 2026-10-22T10:09:11 with identical lines:
  - `check_docs.py maintenance => DOCS OK`
  - `check_traceability.py prepaid_maintenance_plans => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)` (coordinator-run; the auditor did not run it)
  - EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK (7/7)
  - docs: 57 files in docs/maintenance; source sha256 19abc6277d2f 8d7ce9149aa2 c691d3388058 dbddb991606c
  - runtime views: 0.runtime.json 37aa24ccd9ba0646, 1.runtime.json 956a573324e31c4e
- DB access was tool-shaped (db_query.py share finders, KB_search, unlock_*), so the blind phase is blind on the DB side.
- Published products at audit time: maintenance, warranty, loaner. Not published: purchase, service, vsc, gap.

### Per-task part verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Blind = GT |
|---|---|---|---|---|
| 0 (Fleet 12-Visit addendum, Lakeview) | PASS | PASS | PASS | 43130 / 498.96 / 331.89 / 515.57 and all addendum args; tree of 3 state-derived hops; order move → total-loss → fleet cancel → addendum |
| 1 (Plus 8-Visit replacement purchase, Marchetti) | PASS | PASS | PASS | 421.05 / 269.50 and all contract args; 1 state-derived hop |

Files: runtime_context/prepaid_maintenance_plans/{0,1}.md (blind_answer frozen; sha256 f66317ea… / 6d45f4b4… at 10:04:37Z, before the reveal); policy_kb/prepaid_maintenance_plans/{0,1}.md.

### Closing checklist
- Audit files correspond one-to-one with tasks 0 and 1. This is revision_1; there is no earlier revision.
- Every normative atom of maintenance.extended.yaml is entailed by docs/maintenance with nothing added, dropped or changed in meaning. This covers 10 base policies, 3 measures, 6 variants × 47 parameters, 6 extended policies, 26 factors with full ladders, and 7 retired clauses each carried as no longer in force in its declared scope.
- Each of the 4 prerequisite sentences stands verbatim, in state form, only in its blocked hub:
  - fleet_addendum_signing ×2
  - total_loss_cancellation_desk ×1
  - retail_replacement_purchase_contract ×1

  Each is resolvable from the depended-on desk's "stands cancelled" / "stands on the replacement unit" effects and the records.
- No other problem's tool name, route, aggregated chain or task-mirroring title.
- Each computation document yields a definite fall-back that differs from the answer: 35514 / 343.00 / 448.34 / 1029.00 / 214.20 / 699.00. Each factor is findable from record words.
- No worked example or unlock schema carries a scored value or intermediate (exact-string scan over all published docs).

### KB defects (renderer's): none.

### Source-side items (instantiator's): none weight-bearing.
- Policy-side note only: the loss_replacement compute counts total-loss cancellation entries without visibly restricting them to the plan named on the most recent signed total-loss request. This depends on the DSL holding scope and is value-neutral here, since there is a single total-loss request.

### CONDITIONAL (re-judge once purchase and service are published)
- C-0a: closed Fleet agreement KCV-26-30418 has no purchase_transactions rows.
- C-1a: closed retail deal KTD-23-30962 has no purchase_transactions rows.
- C-0b / C-1b: plan-ledger redemption ROs (task 0: RO 367813…368664; task 1: RO 354207/357733/361180) have no service_ro_lines rows.
- C-0c / C-1c: all service-tier, opened-date, late-fee, RO-line, deal-status and delivery figures read by the factors.

None of these moves a tier in either world under the visible rules. Whether the seeded rows are states the purchase and service rules produce can only be judged after those docs publish. Warranty-side rows (FCM terms and the Basic voided on salvage) are consistent with the published warranty docs.

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_2 (2026-10-22, re-audit round 2: cross-product re-judge; every product published)
- Snapshot (`/tmp/erl0075_coord/kb_snapshot.sh prepaid_maintenance_plans maintenance`, 2026-10-22T12:20:18):
  - `check_docs.py maintenance => DOCS OK`
  - `check_traceability.py prepaid_maintenance_plans => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`
  - EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK
  - docs/maintenance 57 files; source sha256 19abc6277d2f 8d7ce9149aa2 c691d3388058 dbddb991606c (identical to revision_1); runtime views 37aa24ccd9ba0646 / 956a573324e31c4e (identical)
- Round-1 REDs: none to close. Regression: none, since the maintenance corpus and source are byte-identical to revision_1. No new KB defect.
- **CONDITIONAL figures:** all re-judged against the published purchase and service docs, and all hold:
  - every service line re-prices exactly (rate 158.00, Net 30 discounts 15% / 18%, shop supplies 5%, hazardous waste 4.95, 2025-07 late fee 25.00);
  - every posting on the two delivered deals re-prices exactly;
  - the Net 30 entry is met by 11 registered units;
  - the Gold tier rests on unread history (accepted residue).
- **Round-1 cross-product notes:**
  - C-0b / C-1b are closed with no mismatch: plan-paid ROs are "never billed here".
  - C-0a is confirmed as source member S-0b.
  - C-1a: the 2023 deal's missing transactions are unread residue (outside every window), but its seeded hold_expires_date mismatches (S-1a).
- **Owed-at-once writes of other products:** the only one is the service early-payment discount on RO 362877 (4.17, S-0a). Booking it cannot move any scored read. The Highlander's base late balance fee is assessable but permissive and touches no read. Nothing else is owed (no service late fee, no fleet late fee, no fleet incentive, no doc-fee correction, no warranty/loaner/GAP/VSC write).
- **COUNT-scope note:** settled as not a member. The sandbox COUNT is scoped to the target holding, and the holdings (3f4887c1; c7bc80bd) are exactly the plans the rules name (the most recent signed total-loss / sold-or-traded request), so the note is withdrawn.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Scored values moved by any cross-product mismatch? |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | no (43130 / 498.96 / 331.89 / 515.57 stand) |
| 1 | PASS | PASS | PASS | no (421.05 / 269.50 stand) |

### KB defects (renderer's): none.

### Source members (instantiator's, seed realism; all three are non-moving)
- **S-0a** (task 0, service): the early-payment discount of 4.17 owed on RO 362877 since its 2026-09-30 ACH payment in full (15 days, inside the 15-day Net 30 ACH window) is not booked. Rate: 2.5% (Fleet VPA unit) + 0.5% (tenure) = 3.0%, on 139.13.
- **S-0b** (task 0, purchase): the closed Fleet VPA KCV-26-30418 carries no purchase_transactions. Missing:
  - the reservation deposit of 2026-07-29;
  - the 2026-08-06 contract-date postings (vehicle_price 52480.00, electronic filing fee 18.00, state title/registration and sales tax);
  - the deposit application on 2026-08-12;
  - the payments clearing the balance before closing on 2026-09-08.

  These rows would sit inside the 3-month bonus window; the bonus stays at the 1-month tier (30.00) from the Tacoma's 2026-10-03 charge.
- **S-1a** (task 1, purchase): KTD-23-30962 `hold_expires_date` is 2023-03-18 with 0 extensions. The rule gives 2023-03-16 (reserved 2023-03-11 + 5); the field is read by no computation.

### Accepted residue (unread; not RED)
- Warranty coverages beyond the read FCM/Basic rows.
- Service history behind the Gold tier and before the 12-month windows.
- The 2023 RAV4 deal's transactions.
- The other fleet units' purchase deals.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=S-0a,S-0b,S-1a

## revision_3 (2026-10-22, re-audit round 3: seed-only confirm)
- Snapshot (2026-10-22T12:39:14):
  - `check_docs.py maintenance => DOCS OK`
  - `check_traceability.py prepaid_maintenance_plans => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`
  - EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK
  - sha256: 19abc6277d2f (extended.yaml, unchanged), 8d7ce9149aa2 (task_tools.py, unchanged), 5e2cd8109130 (tasks/0.json, changed), f6c9983b0a96 (tasks/1.json, changed)
  - docs/maintenance 57 files, unchanged; runtime views 37aa24ccd9ba0646 / 956a573324e31c4e
- All checks went through db_query.py on the rebuilt worlds and against the published service and purchase docs.
- **S-0a closed:** the early-payment discount credit of 4.17 is now booked on RO 362877 line A, dated 2026-09-30, against its labor charge. open_balance is 672.60.
- **S-0b closed:** KCV-26-30418 now carries its deposit, contract postings (52480.00 / 18.00 / 3936.00 / 85.50), the deposit application, and an ACH payoff of 54019.50 that leaves the balance at 0.00 at closing. The trade-in fields were cleared consistently.
- **S-1a closed:** KTD-23-30962 hold_expires_date is 2023-03-16.
- **No new defect, no regression:** the same-class neighbours were re-checked (other fleet invoices: no discount owed and no late fee; holds on the other deals: correct; no new owed write). Every scored figure re-derives unchanged: 43130 / 498.96 / 331.89 / 515.57 and 421.05 / 269.50.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=NONE
