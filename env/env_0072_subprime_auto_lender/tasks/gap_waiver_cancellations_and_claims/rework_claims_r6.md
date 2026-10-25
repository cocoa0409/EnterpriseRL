# rework_claims_r6 — gap_waiver_cancellations_and_claims (policy-task audit revision_5 and the coordinator's structural ruling)

## Task 1 — closed items

- C13 (eu <- bp edge was a decorative cap):
  - The root of task 1 is now the Plus worksheet benefit (`gap_ext_plus_worksheet_benefit`, tool `accept_plus_claim_benefit_e7b3150d`, owner=user: the borrower accepts the worksheet benefit on his claim).
  - The benefit is the Plus starting balance, less the base loan-to-value excess, less the Plus excluded total itemized in place (its six factors unchanged), less the insurer's net settlement. The waited-on starting balance is therefore the benefit's first term and every cent of it moves the result; skipping the starting balance changes the scored figure.
  - The cap sentence is gone.
  - Declared overwrites:
    - Carried from the excluded total: the excluded-items, service-contract-refund and force-placed-premium overwrites.
    - New: the ACV/deductible-covered clause, mirroring the Premier benefit, with sibling-naming tails. The Premier benefit's tail now names the Plus worksheet benefit.
  - The `gap_ext_plus_excluded_amounts` policy and its tool (`record_plus_claim_exclusions_41771560`) are retired. No rule or bundle refers to them.
- C11 (task 1 due-date change beyond Tier 3's 20-day shift) and contract-doc pricing: the task 1 world is re-seeded from origination, with every contract row priced by the contract product's published documents.
  - Contract and due date:
    - The contract is signed 2023-11-24 in GA.
    - Due-date change on 2024-06-03 moves the next due date 18 days, from 2024-06-10 to 2024-06-28 (5 installments paid, current, within the 20-day shift and the per-12-months and lifetime counts).
  - Extensions:
    - Two one-installment extensions, 2025-03-03 and 2026-03-30. The first comes after 12 installments were paid (seasoning allowance); the second comes more than 12 months after the first (spacing allowance one) and at least 180 days later. Every allowance and tier limit is met.
    - Each carries the Georgia charge of 20.00, with no collections-handling or extended-deferral review charge and no late charge to credit.
  - SCRA rate cap:
    - The contract date precedes the duty start. The request is signed within the window and no interest was charged above the cap since the duty start.
    - The installment is reduced by the principal × (APR − cap) / 1200.
    - The cap ends 2026-09-15, the day after the 2026-09-14 duty end.
  - Late charges are at Georgia's 4.0% (contracts signed on or after 2023-07-01), with the first-delinquency reductions (50 / 25 / none). There is no autopay reduction: payments are ACH self-service.
  - No returned payment is seeded.
  - VSC:
    - The service contract is DriveSure Gold (48 months and 48,000 miles, within its entry gate).
    - Its total-loss refund is computed per the published refund calculation and issued within 30 days.
  - CPI rows follow the CPI charter.
  - Settlement and persona:
    - Settlement ACV 12,400.00 with a 750.00 comprehensive deductible withheld (the proof on file); the vehicle is a 2020 Chevrolet Colorado.
    - The persona is aligned with the customer's recorded duty dates.
  - All four starting-balance factors and all six benefit factors move their results.

## Task 0 — the world-type ruling is not implemented (blocker)

- In this difficulty's claimed gap events, each addendum offers only these computable writes:
  - the claim row's four figures (starting balance, excluded total, deductible covered, benefit);
  - a cancellation (effective date);
  - a refund (amount).
- The cancellation request carries no computed field: its status and timestamps come from `ctx.now`.
- A refund on a paid-off contract is the only cancellation-side money write, so an early-payoff or trade-in world yields one rich refund problem plus a thin effective-date problem per addendum. It cannot carry four problems, three of them at 6 factors.
- Problems on two addenda cannot be linked: the base `gap_agg_contract_portfolio` states "A benefit is computed from the records of the addendum's own contract only; losses, balances and refunds of the borrower's other contracts are never combined with it".
- So no tree with four computing problems at counts [6,4,6,6] exists here except the claim world. There the deductible-covered figure cannot honestly reach 4 or 6 factors (rework_claims_r5).
- Task 0 is left as in round 5 (Premier reimbursement and its C1/C2/C4/C12 members unchanged), pending a decision only the coordinator can take (a change of draw, scope or blueprint).
- Its world was not re-priced against the contract documents. Its extensions (before 12 installments paid, two within 12 months) and its late charges (no relief reductions) would also need a re-seed from origination once its structure is settled.

## Kept and swept

- Kept: C9, C10, R2-O1, R2-O3, O6, the age-limited floor, the duty/cap alignment (task 0 duty end 2026-08-19; task 1 2026-09-14 / 2026-09-15).
- Sweep: task 1 bundle fully regenerated (persona, reads, traces, closures, edge, rationale, seed checks); task 0 scope text updated; probe table extended in plan.md.
