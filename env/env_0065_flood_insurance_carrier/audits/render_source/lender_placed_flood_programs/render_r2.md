# Renderer source-scan findings — product forceplaced, render round 2 (renderer agent a69f629b3390c47b0)
Saved verbatim by the coordinator from the renderer's final message (STOPPED, 0 docs written). Round-1 items F1–F6 were all found closed. New mismatches, all in tasks/lender_placed_flood_programs/:

**N1 – An extended rule contradicts in-force base clauses with no overwrite (forceplaced_ext_renewal_premium, rule).**
- The extended rule says: "Every certificate of the program whose current term expires today renews today, unless it carries a cancellation entry or acceptable borrower evidence has been received for it, and all renewals booked on one day take the same program renewal rate per 100."
- It conflicts with these in-force base sentences, none of which any overwrite retires:
  - forceplaced_renewal: "...when no acceptable borrower evidence has been received by then and the loan is still serviced by the lender with the building in a Special Flood Hazard Area..." and "A certificate whose program is terminated does not renew."
  - forceplaced_program_termination: "...when runoff_certificates_honored is true the certificates already issued stay in force to their expiration and do not renew..."
- The "unless" list is exhaustive. So a run-off certificate on a terminated Residential Mandatory Amount program, expiring today with no cancellation entry and no evidence, renews under the extended rule and does not renew under the base rule.
- Severity: latent, since it needs a terminated program in a seed. It is still a direct textual conflict.

**N2 – The renew tool's docstring claims an effect the body lacks (`renew_certificate_c91c4d46`).**
- The docstring says: "One call records the renewal of the named certificate with the balances reported for the loan, the mandatory purchase amount, the building limit, the program renewal rate applied, the new term dates and the premium..."
- The body stores no rate on the renewal entry (there is no such field), and the billing entry does not carry it either. `rate` only feeds `ctx.make_id(...)` and the reply string ("at renewal rate {rate:.4f} per 100").
- Severity: low.

**N3 – Sibling scope sentences claim more than each other's own scope (placement, renewal and commercial, first rule paragraph).**
- renewal: "a new placement on the Residential Mandatory Amount or the Commercial Building tier is priced by its own placement schedule"
- placement: "a renewal on that tier and a placement on the Commercial Building tier are priced by their own schedules"
- commercial: "a placement or a renewal on the Residential Mandatory Amount tier is priced by its own schedule"
- The placement and commercial schedules each limit their own scope to the placement "on the loan named on the most recently mailed first notice ... and only for such a placement", and leave every other certificate premium under the base formula. So a placement on either tier on any other loan is "priced by its own placement schedule" in one hub and "the base formula" in the other.
- Severity: low, wording-level.
