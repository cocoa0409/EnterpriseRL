# rework_claims_r5 — gap_waiver_cancellations_and_claims (policy-task audit revision_4)

## Task 1: re-treed (C1, C2, C4, C12 members on ud)

The re-tree follows the coordinator route that changes which borrower act is the customer's write.

- The Plus deductible reimbursement (`ud` policy) and its tool are retired. Its loss-date window, field/filter-swap "methods" and weekend factor are gone with it.
- Task 1 is now the Plus excluded total, the root and `owner=user`: the borrower confirms on the claim the itemized amounts that stay owed by him. It waits on a new Plus starting balance (4 factors).
  - The excluded total is never more than the starting balance. That gives the state-form edge "The Plus excluded total is not fixed until the claim carries a starting balance above 0.00."
  - The Plus uncovered deductible is the base deductible_reimbursement_basis: the deductible up to the plan maximum.
- The starting balance is split by plan so that the task scopes stay disjoint:
  - Premier keeps `gap_ext_claim_starting_balance` and its tool.
  - Plus gets `gap_ext_plus_starting_balance` and `record_plus_claim_balance_at_loss_c4d2a91e`.
  - Each tail names its sibling and restates the base for other plans.
  - Factor rules are the same as the accepted round-2 starting-balance ladders.
- Task 1 world re-seeded from origination with its owning charters. Changes:
  - A due-date change on 2025-12-10 moves the next due date 2025-12-25 → 2026-01-23, so all four starting-balance factors bear weight.
  - The Peach State proof shows a 750.00 comprehensive deductible and the insurer withheld 750.00, so the excluded total's uncovered-deductible part is above the Plus maximum.
  - The newer-policy proof added in round 4 is dropped.
  - Active duty runs 2025-11-03 to 2026-09-14 and the rate cap ends 2026-09-15, the day after, as the charter states.
  - The persona is aligned.
- All six excluded-total factors and all four starting-balance factors move their results.

## Task 0 (C11)

- C11 (task 0): the customer's recorded active-duty end is now 2026-08-19, the day before the rate-cap-ended record of 2026-08-20, as the contract charter states. The persona says she was released August 19.
- The Premier reimbursement's duty sentence now says the extension counts to the rate-cap-ended effective date, "effective the day after the duty ended".

## Task 0: NOT closed (C1, C2, C4, C12 on the Premier reimbursement)

These remain: pd window anchored on the date of loss, field/filter-swap factors labelled method, and the weekend factor reading other factors' outputs.

- **Why task 0 is blocked.** Task 0's draw (three prerequisites, counts {6,4,6,6}) needs four computing problems on one claim. In this blueprint those can only be the four claim-row money fields, so the deductible-covered computation must carry 4 or 6 factors.
- **Real terms available.** The record-backed real reimbursement terms are:
  - which accepted proof is the policy that paid;
  - which coverage's deductible applies;
  - the contract's allowed deductible;
  - the plan maximum.
- **Why those cannot fill the draw.**
  - They all act as caps on one withheld figure, and only one cap can bind.
  - Field or filter swaps are parameters, so the reimbursement has no real method.
  - A settlement-anchored window of 90 days or more cannot bind without a world in which the borrower stops paying long enough to pass the charge-off line. That breaks the excluded total's at-loss counts.
  - The starting balance has no further real convention: the base fixes interest to the date of loss and "no extension deferrals".
- **Arithmetic.** Over every arrangement of these four problems, the real pool is 18 factors against the 22 the draw needs.
- **What stands until a structural decision is taken.** The round-4 Premier factor set is kept so that the gate block stays valid. It is not claimed compliant.

## Kept and swept

- Kept: C9, C10, R2-O1, R2-O3, O6, the age-limited floor.
- Sweep: task 1 bundle regenerated (closures, edges, traces, rationale, persona, seed checks). Task 0 texts updated for C11 and the scope change. Probe table extended in plan.md.
