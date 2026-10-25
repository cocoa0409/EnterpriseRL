# rework_claims_r10 — cpi_insurance_verification_and_force_placement (audit revision_8: R8-A, R8-B; coordinator ruling)

- R8-B (scope count described as being about proofs that count): the scope sentence of both refund rules and the shared hand-off now state a plain record test with no purpose clause: the rule applies only on a tracking record on which no verification_source holds more than one accepted cpi_proof_verified entry. Nothing claims the count is about proofs that count for the period. Both task worlds sit inside the test after their re-reviews, with realistic channels: task 0 has an agent-call original proof, a feed policy and an uploaded binder; task 1 has a feed original proof, a faxed policy and an uploaded binder.
- R8-A (out-of-scope compute differed from the restated base text):
  - The tail now restates the base refund clauses verbatim: refunded only once, full_no_lapse, the proof clause and the closure clause.
  - The base text is silent on three points, so one reading is stated for each:
    - the proof it reads is the accepted proof with the latest policy_effective_date, whatever its channel;
    - "with no gap" means that proof took effect on or before the placement_effective_date and expires on or after it;
    - when the proof and closure clauses both apply, the charge is refunded once for every day either gives, with the basis named accordingly.
  - The out-of-scope compute is exactly that reading, with no expiry condition on the proof clause. It now applies whenever the hand-off condition fails, that is, when the record test fails or no accepted proof counts.
  - Probed against an independent reading of the text on both worlds (plan.md "Round 10 probe table B"); amount and basis agree in every case:
    - the auditor's case (two feed proofs, the latest expired before the period);
    - two pre-placement proofs with a gap;
    - a latest proof running past the placement date;
    - a second upload starting at or after the closed date;
    - binder and policy on one channel;
    - no accepted proof;
    - one proof per channel with none counting.
- Kept: the R6-A and R6-B closures, channel-blind selection inside the scope, every factor draw, every scored figure, standard result and solo sensitivity (plan.md "Round 10 probe table A"). Gates 7/7.
