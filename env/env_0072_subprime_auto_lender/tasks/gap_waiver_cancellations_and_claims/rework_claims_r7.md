# rework_claims_r7 — gap_waiver_cancellations_and_claims (coordinator's final ruling on task 0; task 1 untouched)

## Placement

Task 0 keeps its four Premier claim figures with the counts the ruling placed:

| Policy | Factors |
|---|---|
| Premier deductible reimbursement | 4 |
| Premier starting balance | 6 |
| Premier excluded total | 6 |
| Worksheet benefit | 6 |

Task 1 and its policies (Plus starting balance, Plus worksheet benefit) are not changed; its bundle is byte-identical to round 6.

## Premier deductible reimbursement (C1, C2, C4, C12)

Rebuilt with four factors. There is no claim window, no weekend factor, no duty extension, and no factor reads another factor's output.

- **Baseline.** The lowest of:
  - the withheld deductible;
  - the latest accepted proof's lower deductible (when above 0.00);
  - the plan maximum.
- **`pd_policy_at_loss` (parameter).** Which proof gives the deductible:
  - the settling insurer's latest accepted proof;
  - else the latest proof naming the settling insurer (rejected or not), whose declarations show the policy that paid;
  - otherwise the latest accepted proof.
- **`pd_paying_coverage` (parameter).** Collision, comprehensive, or the lower of the two.
- **`pd_contract_allowance` (parameter, cross-difficulty CPI).** The borrower maximum deductible of the plan the tracking record now carries:
  - Plan C–F: 1,000.00;
  - Plan A/B: 500.00;
  - no tracking record: none.
- **`pd_allowance_test` (method, shape change).**
  - Withheld deductible above the borrower maximum, and a proof names the settling insurer: also never more than the allowance (cap).
  - Withheld deductible above the borrower maximum, and no proof names the settling insurer: nothing (void).
  - Otherwise: the allowance does not enter.
- **Known coupling, disclosed.** The allowance amount (`pd_contract_allowance`) enters only through the method's cap tier. The method's own conditions read the records directly.
- **Edge.** The excluded total's action-form edge fallback reason now cites the void case instead of a window.

## Premier starting balance (6)

The four accepted factors are kept, and two are added.

- **`bl_placed_premiums` (parameter).** Force-placed premiums the tracking record added to the contract balance, which the signed schedule leaves out:
  - net of refunds credited;
  - all, when nothing was credited;
  - none.
- **`bl_account_interest` (method).** Uses the contract's latest payment:
  - Made on or before the loss and left interest unpaid: the carried unpaid interest plus the interest accrued from that payment to the loss.
  - Made on or before the loss and covered its interest: the accrued interest only.
  - Otherwise: none.
  
  The accrual is on the contract's principal balance at the rate in force on the date of loss: the capped rate while the SCRA cap is in effect, otherwise the original rate.
- The rule's no-interest sentence and the overwrite tail are restated to match.

## Worksheet benefit

The age-limited value floor keeps its shape, with the line moved to 36 months, so that the re-seeded world's 30 months in force sit on a tier:
- under 24 months: 80%;
- 24 to 35 months: 70%;
- 36 months or more: no floor;
- baseline: 60% under 36 months.

## C11 — task 0 re-seeded from origination

Every contract row is producible by the published contract documents.

- **Contract, vehicle and tracking record.**
  - Ohio contract signed 2024-02-05; book value 13,500.00.
  - The tracking record opens on Plan C and is re-banded to Plan B at a placement on the trade-in value.
  - Backend 2,590.00, within Tier 2's 20%.
- **Due-date change.** Within Tier 2's limits: 19 days, 5 installments paid, current.
- **Extensions.**
  - First extension after 13 installments paid (seasoning allowance one); Tier 2's first fee waived.
  - Second extension more than 12 months later (spacing allowance one); fee 25.00, with no handling or review charge.
- **Late charges.** At the product's 5% with the first-delinquency reductions. The base is the scheduled installment, except on the next-due installment carrying partial credit from a payment on or before its due date.
- **No returned payment.**
- **SCRA cap.** From the 2025-06-02 duty start (request signed 2025-06-05, before any payment at the old rate). Installment reduction per the published formula. The cap ends the day after the 2026-08-31 duty end.
- **Pre-loss partial payment.** A payment of 150.00 on 2026-07-28 left interest unpaid.
- **Proofs.** The Keystone Prairie proof (collision 1,000.00) is rejected for a deductible too high; Buckeye Heritage proofs are accepted.
- **Service contract.** DriveSure Powertrain Plus, refunded per the published refund calculation within 30 days.
- **Personas, reads, traces, closures, seed checks and rationale** are rebuilt.

## Kept

C9, C10, R2-O1, R2-O3, O6, the age floor (now on a 36-month line), the duty/cap alignment.
