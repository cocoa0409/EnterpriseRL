# Rework round 5 — claims (nonowner_policies_and_renewals)

Each item of the renderer pre-render scan (render_r1.md), by id, with how it was closed. No scored values appear here; the task files carry them.

## F1 — closed
- The illustrative clause naming the package re-rate realignment and a filer class is deleted from P6's rule and from its overwrite replaced_by.
- The operative "above zero" test is kept.
- A class sweep over all six rules found no other scope or overwrite sentence that names another extended policy's action or a factor quantity.

## F2 — closed
- P2's unearned days are floored at zero in both rule and compute.
- The rule states the zero case as a record test: nothing is returned and no return entry is booked.
- The cancellation tool still cancels, but books a return-premium entry only for an amount above zero. No 0.00 row is ever posted (XF20).
- A class sweep over every other day count and amount in P1 and P3–P6 found no other negative or zero case that the tools cannot book.

## F3 — closed
- Filer required-through reads (P1, P3, P4, P6) are inlined into the filer-class factor's own bindings; the plain through bindings are removed.
- `request_reason` is moved into requirement_relief.
- `offer_window_left` is now a plain standard-figure binding outside offer_lapse_window.
- A class sweep confirmed that every remaining single-factor plain binding is that factor's baseline quantity.

## Regression guard
- Not touched: task worlds, scored values, every combination sentence and its order, revision_4 closures (R3-A, R3-B, R2-A..R2-H, CG-1..CG-9) and XF1..XF23.
- Sweeps all clean.
- Gate block all OK.
