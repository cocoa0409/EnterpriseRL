# rework_claims_r11 — cpi_insurance_verification_and_force_placement (audit revision_9: R9-A)

- R9-A (no tie rule for the out-of-scope reading): in both refunds' tail reading sentence, which appears in rule, replaced_by and compute_basis alike, the reading now says: "where two accepted proofs share that date the one recorded first counts". This is exactly what the compute does. LATEST keeps the first-recorded row on equal policy_effective_date, and the effective-date and expiration-date reads use the same pick, so both read the same proof.
  - Probed on both worlds: two accepted proofs share an effective date before the placement, one expiring before it and one after. Recorded in either order, the first-recorded one decides the out-of-scope refund, as the sentence states.
- Tie sweep over all five policies:
  - Re-review picks already state "by review date (where two entries share that date, the one recorded first counts)", and their later "most recent one" phrases refer back to that pick.
  - Each refund's charge pick sums every capitalised charge of the latest billing period, so equal starts form one charge.
  - Inside the refund scope each channel holds at most one accepted proof, so the per-channel pick has no tie.
  - The remaining "latest / earliest" phrases name dates, not record picks.
  - No other unstated tie was found.
- Minimal edit only: no compute, world, tool or task change; every figure, standard result and solo sensitivity is unchanged. Gates 7/7.
