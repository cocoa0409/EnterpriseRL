# rework_claims_r11 — gap_waiver_cancellations_and_claims (KB audit kb_round1: S1, S2, P1)

No scored figure, sensitivity or trace changed. tasks/1.json and task_tools.py are byte-identical to round 10. In
tasks/0.json, three things changed: the CPI tracking rows (S2), the CPI read notes and rationale lines that describe
them, and the seed-consistency check for the March claim (S1).

## S1 — the March claim's withdrawal

- In the gap charter, `gap_claim_withdrawn` targets `gap_addenda`. It is a status transition (claim_open → active),
  and `gap_activities` has no withdrawal event type, so a withdrawal leaves no activity row.
- The seeded state can therefore be produced in this order:
  1. The 2026-03-16 claim opened the addendum (claim_open).
  2. Its withdrawal returned the addendum to active.
  3. The 2026-08-19 claim was filed on the active addendum and opened the claim_open status the addendum shows now.
- The March claim's seed-consistency check now states this. No row was changed.

## S2 — CPI tracking after the policy on file expired

- The Buckeye Heritage policy on file expired 2026-09-18 with no acceptable replacement; the Keystone Prairie proof
  had been rejected for its deductible.
- Under the published lapse and timing standards in docs/cpi:
  - the tracking record now stands in lapse notice, with lapse date 2026-09-18;
  - a first lapse notice was mailed 2026-09-21, inside the 5-day first-notice period;
  - the second notice falls due no earlier than 2026-10-06, and placement can come no earlier than 2026-10-21. Both
    are after the frozen time, so neither is seeded.
- No computation reads the tracking status or the lapse notice, so every figure is unchanged.

## Bounded pass over cross-category rows (both worlds)

- **Contract and VSC rows.** These were already checked in kb_round1 and are unchanged: late charges, extension fees,
  SCRA caps and end dates, due-date changes, payment allocations, and the VSC refunds.
- **CPI rows, re-checked one by one against docs/cpi.**
  - Plan on opening and on placement, by the value bands.
  - Proof acceptance and rejection order on open records, including the deductible ceiling and the 15-day expiry test.
  - Deficient-proof, lapse, placement and cancellation notice timing.
  - Coverage reach-back of at most 30 days.
  - Premiums and refunds.
  - The policy on file matching the latest accepted proof.
- **Result.** Task 1 is producible as seeded. Task 0 needed only the S2 change.
- **Recovery and deficiency.** No rows are seeded in either world.

## P1 — factor independence in the Premier deductible reimbursement

- `pd_proof_standing` now decides only which review results count, with no reference to the insurer another factor
  selects:
  - any result counts, when the settling insurer's latest proof was rejected for its deductible;
  - no proof counts, when it was rejected for any other reason;
  - otherwise only accepted proofs count.
- How the insurer and the proof standing combine is now one plain sentence outside the factors. It includes the
  fallback to the policy on file's latest accepted proof.
- `pd_policy_at_loss` and `pd_allowance_test` each own their count of proofs naming the settling insurer. There is
  no longer a binding they share.
- Each factor still moves the result on its own on task 0, and its tiers are unchanged. check_compute confirms the
  same expected value, baseline and per-factor sensitivities.
