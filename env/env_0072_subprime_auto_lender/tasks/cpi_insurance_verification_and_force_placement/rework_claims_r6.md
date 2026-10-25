# rework_claims_r6 — cpi_insurance_verification_and_force_placement (audit revision_4; coordinator route round 6)

- R4-A (cover rule and graces acted only when the refund-basis factor left its baseline): cm_refund_basis and cp_refund_basis are no longer factors.
  - The refund basis is now a plain branch: full_no_lapse when a counting proof took effect by the placement date, pro_rata_from_closure when no counting proof reaches, and pro_rata_from_proof_effective otherwise.
  - The standard method is the base rule's own accepted-proof basis by actual days: covered days from the latest reaching proof's effective date through the closed date, plus any post-closing days, with no grace.
  - Each refund factor now acts on that standard quantity by itself. Solo substitutions on both worlds are in computations.factor_sensitivity and in plan.md "Round 6 probe table".
- R4-A, refund draw kept at 4: the renewal-stretch grace is dropped, because no such stretch exists once proofs start inside the refunded period. The replacement-gap grace is now the sum of three allowances, built the same way as the accepted deductible ceilings:
  - CPI plan (cm/cp_plan_grace);
  - contract state (cm/cp_state_grace);
  - vehicle model year (cm/cp_year_grace, which reads another category).
  - Together with the coverage-counting method, that gives 3 parameter factors and 1 method factor per refund. Every tier of every ladder is reachable and distinct from its fall-through (probe table).
- R4-B (closing-month standard refunded 0.00 to everyone in scope): the closing-month standard is now the base proof basis, which is never zero when a proof reaches the period. Closure and full_no_lapse appear only as plain branches, never as the standard.
- R4-C (a second charge refundable under the kept base rule): the proofs are re-seeded so that every accepted proof starts on or after the refunded charge's period start. No earlier charge is reached by any accepted proof (probed after the re-reviews in both worlds), so the closing refund is everything the rules leave refundable.
  - Task 1's payoff moved to 2026-10-08. The payoff row was re-simulated (interest accrued from the last installment) and frozen_time moved to 2026-10-22, still inside the refund window.
  - Proof review dates and notices were re-seeded while each record was open.
  - Personas restate only the payoff and their own coverage start dates. Tool scope is unchanged: one refund write for the closing charge, with refund_basis passed in.
- Kept as before: the re-review rules (revision_4 PASS). Their factors still move the outcome solo in the re-seeded worlds. Earlier classes R2–R3 stay closed (no day basis, closing-day adjustment, minimum terms, shares, credits, tenure grading or interest). Contracts stay inside their tier limits.
