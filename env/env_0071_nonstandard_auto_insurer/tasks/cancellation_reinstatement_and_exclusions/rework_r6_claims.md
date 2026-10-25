# Rework round 6: claims per revision_5 audit item

No scored values are given here. Task 1 is untouched.

## R5-01: refiling charged twice (reinstatement fee and fr filing fee)

**Closed.** The certificate factor of the reinstatement fee no longer prices the refiling. It is renamed rw_certificate_exposure_charge.

**What the tiers now key on.** The state liability the certificate kept while coverage was lapsed. The lapse days carry no premium, and the fr filing fee does not price this liability.

| Tier | Charge |
|---|---|
| Certificate kept in force through the lapse (still filed, no SR-26 transmitted), so the company stayed bound for every lapse day | fee_continue |
| SR-26 transmitted, but the certificate's end date falls on or after the reinstatement effective date, so the company stayed bound for part of the lapse | fee_continue_part |
| Certificate ended before coverage was restored (the new filing is charged under the fr filing fee), or no certificate | nothing |

**Removed:** the fee_refile parameter and the refiling tier. No other add-on was introduced.

**Counts and values:** the factor count is unchanged. Task 0's world takes the first tier, so its scored values do not move.

**Probes run on scratch copies:**
- SR-26 transmitted, with the certificate end after the reinstatement;
- SR-26 transmitted, with the certificate end before the reinstatement;
- no certificate.

All three evaluate.

**Sweeps clean:** proof text (tracing, factor trace, sensitivity tier, necessity, rationale) and compute_basis quotes.
