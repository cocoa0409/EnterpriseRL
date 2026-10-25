# Rework round 9 — claims (renderer source scan render_r1)

- D1: closed — the returned-payment-fee relief no longer recomputes the late-fee relief or carries its parameters; it waits in state form on the late-fee relief owed on the plan's latest late fee (which takes a last remaining courtesy waiver first when above 0.00) and then checks only the plan's courtesy limit; the one-waiver cases give a single end state, including the case where the late-fee relief works out to 0.00.
- D2: closed — the late-fee level tiers partition the plan's late-fee record exactly at six and twelve months; no "months back" wording remains and every other ladder was re-checked.
- D3: closed — each factor that needs a month window or a day span carries that convention in its own sentence; convention sentences outside factors remain only where a non-factor quantity uses them.
- D4: closed — the reset's method factor owns each tier's interest-free part and payments; the payment is assembled by one generic sentence, and no split-payment quantity or tier formula sits outside the factor.
- D5: closed — a payment dated on or after the billing date bars the split reset, in the rule and the compute alike.
- D6: closed — the one-penalty limit's own sentence carries the grace-period definition its compute uses.
