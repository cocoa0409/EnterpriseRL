# KB-doc policy audit — recovery_repossession_and_reinstatement (product recovery)

## kb_round1 — blind freeze
1879b29b4260edb6e0ade23c3df03647566ab91d9cf507a47fdd5200707cc8e1  runtime_context/recovery_repossession_and_reinstatement/0.md (frozen 2026-10-20T11:45:48, before reveal)
5ebee7f8998a9fc6d75334d599065d4fdcd3326b8ae7d83fd6405751ba578351  runtime_context/recovery_repossession_and_reinstatement/1.md (frozen 2026-10-20T11:45:48, before reveal)

## kb_round1 — entry conditions (Step 0)
- Policy-side verdict: `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN` (brief).
- Coordinator gate snapshot (2026-10-20T11:39:06): every gate green and the source hashes match. I re-ran `/tmp/erl0072_coord/kb_snapshot.sh recovery_repossession_and_reinstatement recovery` (execute only) at 2026-10-20T11:49:01:
  - DOCS OK
  - TRACEABILITY OK, 0 misses
  - EXTENDED OK
  - TASK TOOL CONTRACT OK
  - REPLAY OK
  - SOLVABILITY OK
  - COMPUTE OK
  - GROUNDING OK
  - SCOPE OK
  - yaml a3e3835d...bc1497d
  - task_tools 15618792...7a2c
  - I did not run check_traceability myself.
- Runtime view hashes verified (0: cd8ae5a4...e393, 1: 3bf5a978...1c). The DB was queried only through `db_query.py` (share finders + KB_search). It was not read raw.
- Input completeness note: the `--list` view exposes the read finders only. Write share tools (`verify_customer_identity`) and the unlock/handover wrappers were not visible, so the blind audit read the task-tool contracts from the hub invocation blocks. This is not a KB finding.

## kb_round1 — results
| Task | runtime (blind vs GT) | bijection | dependency_form |
|---|---|---|---|
| 0 | PASS (604.00 / 45 / 0.00 / 1897.00; fall-back 600.00 / 15 / 2259.00, all equal to GT) | PASS | PASS |
| 1 | PASS (101.00 / 297.00; fall-back 175.00 / 311.00, equal to GT) | PASS | PASS |

## KB defects
None.

## Source-side items (rule-vs-compute or seed defects the KB cannot fix)
None.
- **Compute vs rule.** All five compute blocks agree with their rules:
  - posted_open subtracts both waived and settled amounts; the `inputs.history` list omits the waived sum, but the compute includes it, so this is authoring metadata only.
  - The business-day conversion re-derives correctly for Monday, Thursday, Saturday and Sunday mailings.
  - The weekend clock shifts, the ≤30-day grace window, the per-day keyless additions, and the floors and roundings all agree.
- **Seeds.** I checked the cross-category seeds against the published contract docs, and every one reproduces:
  - late charges (5.0% of the scheduled payment; GA signed before 2023-07-01, so the product percent applies);
  - certified-funds-only status (2 fee-bearing returns in 12 months at Tier 5);
  - the SCRA cap rows (effective on the active-duty start date; ended the day after the end date; the payment reduction recomputes to 152.29);
  - the right-to-cure amounts and deadlines and the assignment dates;
  - the earlier case's reinstatement payment (1140.27) and expense settlement (829.00 = 434.00 + 275.00 + 6 × 20.00);
  - the earlier notice (1849.27, 26 days);
  - task 1's notice (775.56, 15 days, mailed within 3 business days with Columbus Day skipped);
  - the contract status repossessed on the recovery date; neither contract charged off.

## Policy-side notes (do not change the verdict)
- **N1. Generic assembly wording in computation docs.** The source's own `rule` / `compute_basis.result` sentences name the kinds of adjustment:
  - agency: "any limit ... any reduction ... any added charges";
  - surrender: "any reduction and any credits";
  - redemption and reinstatement: "the days not charged ... its day rate together with any per-day addition";
  - sale period: "plus every addition of days that applies".
  The computation documents carry these verbatim, and the worked illustrations restate them. This wording fixes a non-commuting order, so it is a placement-class item only (stop rule), not a KB finding.
- **N2. Open boundary on a voluntary surrender with no transport row (task 1).** The base expense rule charges transport "for every method except impound_release", while the class definition of the surrender fee reads "(transport arranged by the company)". The case carries no transport row, no tool posts transport, and the GT expects none. Neither the corpus nor the source closes whether a transport fee is owed; it is not load-bearing.
- **N3. Conditional on cpi (unpublished).** Neither customer has an insurance tracking record, although the background says every financed vehicle has one. For task 1, the vehicle release after reinstatement needs accepted insurance proof on that record. No scored figure or write depends on it. Re-check when cpi publishes. Nothing here depends on gap.
- **N4. Incidental hypothetical number.** The PA storage example "66.00" (3 × 22.00) in `state_storage_day_rates_reinstatement` equals task 0's intermediate book-value reduction. It is not a gold argument and not a leak.

## Closing checklist
- One-to-one audit files exist: `runtime_context/.../{0,1}.md` (blind answers frozen with hashes above before the reveal, gt_comparison appended) and `policy_kb/.../{0,1}.md`.
- Every normative atom of the difficulty's source is entailed by `docs/recovery`. Every prerequisite sentence is verbatim, in state form, on its blocked hub only. Every factor ladder is complete and findable from record words. No tool name, route or chain goes beyond those sentences.
- Gates re-run on the final form: see the entry conditions above.
VERDICT kb_round1: task0=PASS task1=PASS kb=CLEAN src=none

## revision_2 — kb_round2 (2026-10-21): cross-product re-judge, all products published
### Entry
- `/tmp/erl0072_coord/kb_snapshot.sh recovery_repossession_and_reinstatement recovery`, run at 2026-10-21T00:07:30, reports every gate green: DOCS OK; TRACEABILITY OK, 0 misses; EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
- The hashes are unchanged: yaml a3e3835d...bc1497d, task_tools 15618792...7a2c.
- No file in docs/recovery or docs/contract is newer than round 1. The cpi corpus (46 docs) and the gap corpus (59 docs) are newly published.
- The revision_1 blind answers stand unedited.
- I did not run check_traceability myself and edited nothing.

### Conditional figures from round 1, settled
- N3 (cpi) is now settled. The published cpi standard `tracking_records_per_contract` says: "Every contract the company books opens one insurance tracking record on its contract date".
  - Neither world has one: `find_cpi_coverages` returns no records for either customer. This is a seed item (S2 below).
  - No scored figure reads cpi. The only cpi-dependent condition on the path is the release of a reinstated vehicle ("only when accepted proof of the borrower's own physical-damage insurance is on the contract's insurance tracking record"). Release is not a write in either task, so S2 is not load-bearing.
- Nothing else was conditional, and nothing depends on gap.
- The rules in other products that read recovery records are listed below. None applies on these cases, and none changes a scored figure:
  - cpi: reach date by repossession date; no CPI premium billed while repossessed;
  - gap/vsc: cancellation on repossession sale;
  - dealer: early-default chargeback within 120 days;
  - deficiency: account opening on sale.

### Disclosure: correction of round 1
Round 1's seed note O3 checked the late charges against the base 5.0% rate only, and the returned-payment fees against the tier fee only. It did not apply the published contract factor documents. Those were already published in round 1, so this was an incomplete check on my side:
- `autopay_late_charge_relief`;
- `first_delinquency_late_charge_relief`;
- `late_charge_amount_computation` (combined reduction percent);
- `restriction_review_charge`;
- `subsequent_return_charge`;
- `bank_charge_recovery_on_returns`;
- `failed_payment_offset`;
- `returned_payment_fee_computation`.

Round 1's "all reproducible" is withdrawn for the members listed under S1.

### Exhaustive cross-category seed pass (every non-recovery row in both worlds, plus the recovery rows that carry contract figures)
How I checked: I simulated each contract ledger under `payment_posting_and_application` (actual/365, interest start at the latest non-returned payment, the order of application, the installment-credit rule) and under `returned_payment_reversal`, and computed every fee under the published fee documents. Scratch scripts: /tmp/kbaudit_recovery_0072/sim.py and lc.py.

**World 0 (Calvin Pemberton, contract a7f73cd4, WI, Tier 5)**

| # | Row(s) | Published-doc check | Result |
|---|---|---|---|
| 1 | customer 11cd528f (SCRA active 2023-08-13 to 2025-03-12) | consistent with `servicemember_rate_cap` | OK |
| 2 | contract booking terms | inside Tier 5 limits, WI has no APR ceiling: score 497, APR 23.49, 48 months, 11200.00, vehicle age 9; scheduled 361.99 ≈ amortized payment | OK |
| 3 | contract principal_balance 3588.19, next_due 2026-07-12, partial credit 0, unpaid interest 0 | reproduced by the simulation | OK |
| 4 | certified_funds_only true | 2 fee-bearing returns in 12 months, Tier 5 count 2 | OK |
| 5 | status repossessed, repossession_date 2026-10-04 | `default_statuses_and_charge_off`; not charged off (99 days past due) | OK |
| 6 | fees_due_usd 54.30 | sum of seeded late charges; published rules give 5.43 + 11.76 + 16.29 = 33.48 | **S1** |
| 7 | servicing events: rate_cap_applied 2023-08-13 (6.0%, 209.70) and rate_cap_ended 2025-03-13 (23.49%, 361.99) | effective on start date; ended the day after the end date; reduction 10448.87 × 17.49 / 1200 = 152.29 | OK |
| 8 | service request scra_rate_cap, signed 2023-08-09 | contract predates service; request in time | OK |
| 9 | 39 posted payments (installments, reinstatement 2025-07-08, MoneyGram 2026-01-20 and 2026-04-21) | interest and principal split of all 39 reproduces exactly; the reinstatement covers 3 installments and next due moves to 2025-07-12 | OK (the fee portions are noted in #14) |
| 10 | returns 2026-01-14 and 2026-04-15 (autopay, NSF) | reversal restores exactly; no late charge, since each installment was repaid within grace | OK |
| 11 | returned-payment fee 2026-01-14, 25.00 | 25.00 + restriction 5.00 − autopay offset 5.00 = 25.00 | OK |
| 12 | returned-payment fee 2026-04-15, 25.00 | 25.00 + subsequent 5.00 + restriction 10.00 − autopay offset 5.00 = **35.00** | **S1** |
| 13 | late charges 2025-04-23, 2025-05-23, 2025-06-23, 2026-07-23, 2026-08-23, 2026-09-23, each 18.10 | 5.0% × 361.99 less the combined autopay and first-delinquency reductions, which gives **5.43, 9.95, 14.48, 5.43, 11.76, 16.29** (reductions 70%, 45%, 20%, 70%, 35%, 10%) | **S1** (all six) |
| 14 | fee_paid 2025-07-08 54.30 (and fees_applied 54.30 in the 1140.27 reinstatement payment); fee_paid 2026-04-21 25.00 (fee portion of 386.99) | follow from #12 and #13; under the rules the fees are 29.86 and 35.00 | **S1** (derived) |
| 15 | fee_paid 2026-01-20 25.00 | matches #11 | OK |
| 16 | right-to-cure notice 2025-06-11 stated 760.18; right-to-cure notice 2026-09-10 stated 760.18 | fees due on the mailing date under the rules: 15.38 and 17.19, giving 739.36 and 741.17 | **S1** (derived) |
| 17 | old-case NOI 2025-07-01 stated 1849.27 (sale period of 26 days) | the 26 days reproduce; the amount under the rules is 1824.83 (fees 29.86) | **S1** (derived, amount only) |
| 18 | CPI tracking record | absent; the published cpi standard requires one per contract | **S2** |
| 19 | dealer_agreement_id None | no published rule requires the field; closure omission of an unrelated holding | note N5 |
| 20 | gap / vsc / deficiency holdings | none; all optional or post-sale | OK |

**World 1 (Agnieszka Kowalczyk, contract b5f88e7d, GA, Tier 5)**

| # | Row(s) | Published-doc check | Result |
|---|---|---|---|
| 21 | customer 2de4a5ab (no SCRA) | none applies | OK |
| 22 | contract booking terms | inside Tier 5 limits: score 503, APR 24.49, 48 months, 10800.00 ≤ 115% × 9400.00, age 10; scheduled 355.03 ≈ amortized payment | OK |
| 23 | principal 3513.40, next_due 2026-08-22, certified_funds_only false, repossessed 2026-10-10 | reproduced by the simulation; the 1 return falls outside the 12 months | OK |
| 24 | fees_due_usd 35.50 | published rules give 5.33 + 9.76 = 15.09 | **S1** |
| 25 | 38 posted payments | interest and principal split of all 38 reproduces exactly | OK |
| 26 | return 2024-11-25 (autopay, NSF) | reversal exact; repaid 2024-12-01 within grace | OK |
| 27 | returned-payment fee 2024-11-25, 25.00 | 25.00 + restriction 5.00 + GA bank-charge recovery for ACH 2.50 − autopay offset 5.00 = **27.50** (GA cap 30.00) | **S1** |
| 28 | fee_paid 2024-12-01 25.00 (fee portion of the 380.03 MoneyGram) | follows from #27 | **S1** (derived) |
| 29 | late charges 2026-09-02 and 2026-10-03, each 17.75 | GA contract signed before 2023-07-01, so 5.0% applies, less reductions of 70% and 45%, which gives **5.33 and 9.76** | **S1** (both) |
| 30 | NOI 2026-10-13 stated 775.56 (15 days) | the 15 days reproduce; the amount under the rules is 710.06 + 15.09 + 30.00 = 755.15 | **S1** (derived, amount only) |
| 31 | CPI tracking record | absent | **S2** |
| 32 | dealer_agreement_id None | as #19 | note N5 |

### Load-bearing assessment
S1 and S2 touch no scored argument of either task:
- The agency fee reads class, state, book value, keys and weekday.
- The sale period reads state, SCRA rows, the count of notices, the mailing lag and the certified-funds flag. The flag depends on the count of returns, not on fee amounts.
- The stated 0.00 reads the reinstatement count.
- The redemption, surrender and reinstatement expense payments read recovery rows only.

The gold arguments 604.00 / 45 / 0.00 / 1897.00 and 101.00 / 297.00 are unchanged under the published contract, cpi and gap rules. The KB-side verdicts therefore stay PASS, and S1 and S2 are reported as seed defects the KB cannot fix.

### Source-side items (one exhaustive list)
- **S1. Contract fee rows that the published contract fee rules cannot produce.**
  - Direct members: late charges #13 (6 rows) and #29 (2 rows); returned-payment fees #12 and #27.
  - Derived members: fees_due #6 and #24; fee_paid / fees_applied #14 and #28; right-to-cure stated amounts #16 (2 rows); NOI stated amounts #17 and #30.
  - Root cause: the seeded late charges use the flat 5.0% with no autopay or first-delinquency reduction, and the seeded returned-payment fees use the flat tier fee with none of the restriction, subsequent-return, bank-charge-recovery or autopay-offset terms.
  - Not load-bearing in this difficulty.
- **S2. No CPI insurance tracking record on either contract.** This contradicts the published `tracking_records_per_contract` ("Every contract the company books opens one insurance tracking record on its contract date"). It is not load-bearing; the only touch point is the vehicle release after reinstatement in task 1, which is not a scored write.

### Notes
- N1, N2 and N4 from round 1 stand.
- N3 is resolved into S2.
- N5: dealer_agreement_id is None on both contracts. No published rule requires it, so this is a closure note only.

### Round-2 results
| Task | runtime | bijection | dependency_form |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |
VERDICT kb_round2: task0=PASS task1=PASS kb=CLEAN src=S1,S2

## revision_3 — kb_round3 (2026-10-21): S1 closure check after the seed-only rework
### Entry
- Gate: `audits/policy_task/recovery_repossession_and_reinstatement/_difficulty.md` tail = `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN`.
- `kb_snapshot.sh`, run at 2026-10-21T01:00:45, reports every gate green: DOCS OK; TRACEABILITY OK, 0 misses; EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
- The source hashes are unchanged: yaml a3e3835d...bc1497d, task_tools 15618792...7a2c.
- Runtime views re-hashed, both unchanged: 0 = cd8ae5a4...e393, 1 = 3bf5a978...901e1c.
- docs/recovery and docs/contract are unchanged since round 2. The cpi and gap corpora were re-rendered.
- A fresh visible-context derivation via db_query.py (/tmp/kbaudit_recovery_0072/r3/w{0,1}.txt) was frozen in runtime_context revision_3 before the GT was revealed.
- I did not run check_traceability myself and edited nothing.

### S1: one exhaustive pass over every cross-category row (fresh worlds)
The ledgers were re-simulated with sim.py and lc.py on the new rows.

**World 0**

| Round-2 member | Now | Published-doc value | Closed? |
|---|---|---|---|
| #13 late charges 2025-04-23, 2025-05-23, 2025-06-23, 2026-07-23, 2026-08-23, 2026-09-23 | 5.43, 9.95, 14.48, 5.43, 11.76, 16.29 | same | yes (6/6) |
| #12 returned-payment fee 2026-04-15 | 35.00 | 35.00 | yes |
| #11 returned-payment fee 2026-01-14 (was already OK) | 25.00 | 25.00 | no regression |
| #6 fees_due_usd | 33.48 | 5.43 + 11.76 + 16.29 | yes |
| #14 reinstatement payment 2025-07-08 and its fee_paid | 1115.83 (interest 555.84, principal 530.13, fees 29.86); fee_paid 29.86 | 1085.97 + 29.86 | yes |
| #14 MoneyGram 2026-04-21 and its fee_paid | 396.99 (fees 35.00); fee_paid 35.00 | 361.99 + 35.00 | yes |
| #15 MoneyGram 2026-01-20 and its fee_paid (were already OK) | 386.99 / 25.00 | same | no regression |
| #16 right-to-cure 2025-06-11 / 2026-09-10 | 739.36 / 741.17 | same | yes (2/2) |
| #17 old-case NOI 2025-07-01 | 1824.83, 26 days, deadline 2025-07-27 | same | yes |

**World 1**

| Round-2 member | Now | Published-doc value | Closed? |
|---|---|---|---|
| #27 returned-payment fee 2024-11-25 | 27.50 | 27.50 | yes |
| #28 MoneyGram 2024-12-01 and its fee_paid | 382.53 (fees 27.50); fee_paid 27.50 | 355.03 + 27.50 | yes |
| #29 late charges 2026-09-02 / 2026-10-03 | 5.33 / 9.76 | same | yes (2/2) |
| #24 fees_due_usd | 15.09 | same | yes |
| #30 NOI 2026-10-13 | 755.15, 15 days, deadline 2026-10-28 | 710.06 + 15.09 + 30.00 | yes |

All S1 members are closed.

**Rows OK in round 2, re-verified with no regression**
- The 39 + 38 posted payments: every interest and principal split still reproduces. Final principal is 3588.19 and 3513.40, matching the contract records. next_due is 2026-07-12 and 2026-08-22.
- Both returns reverse exactly.
- certified_funds_only (True / False), the SCRA servicing rows and the service request (identical), the customers, the booking terms, and the repossessed status and dates.

**Recovery rows**
- Both worlds' recovery_cases are identical to round 1.
- The current-case activity rows are identical except the task-1 NOI stated amount, which is now 755.15 (above).
- The old case's 434.00 fee, 275.00 transport and 829.00 settlement are unchanged.
- Task-0 recovery figures are unchanged: expenses_outstanding 1005.00, the 8-day notice stated 0.00.

### Regression and new-defect check
- GT computations and call arguments are unchanged: 604.0 / 45 / 0.0 / 1897.0 and 101.0 / 297.0. Baselines are unchanged: 600 / 15 / 2259 and 175 / 311.
- db_closure_matches_initial_state is true for both tasks.
- No stale pre-rework figure appears in either task JSON.
- None of the reworked rows feeds a scored figure. The certified-funds count is unchanged, since it counts returns, not fee amounts.
- KB: no recovery or contract doc changed. The re-rendered cpi and gap docs name no recovery tool or payment, and their repossession-reading rules are the same set as in round 2.
- No new defect found.

### S2
S2 (no CPI insurance tracking record on either contract) is **accepted residue (coordinator decision)**. The frozen replay closure gate rejects seeded rows that no gold step reads, and no scored figure reads a CPI record. It is recorded as accepted, not as an open item. N1, N2, N4 and N5 stand as notes.

### Round-3 results
| Task | runtime (fresh derivation vs GT) | bijection | dependency_form |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |
VERDICT kb_round3: task0=PASS task1=PASS kb=CLEAN src=none
