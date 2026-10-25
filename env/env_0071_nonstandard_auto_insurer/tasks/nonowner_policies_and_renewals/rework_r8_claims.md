# Rework round 8 — claims (nonowner_policies_and_renewals)

Each item of the renderer's second scan (render_r2.md), by id. No scored values appear here, and none moved.

## Items
- **F4: closed.**
  - The six unused params are deleted from nonowner_ext_late_renewal_written and nonowner_ext_reinstatement_rewritten.
  - A class sweep of every policy found no other unused param or binding.
- **F5: closed.**
  - The four filer readings now state the compute's reading order exactly: status preference first, then the required-through test, the first recorded within a status, and FR-44 over SR-22 when both count.
  - The four readings are late_filer_change, rerate_filer_class, offer_filer_class and increase_filer_class.
  - The certificate-release clause behind late_released_form now states its own order and qualification test.
  - compute_basis quotes are updated verbatim.

## Regression guard
- No compute, world or scored value changed.
- All earlier closures are untouched.
- Gate block all OK.
