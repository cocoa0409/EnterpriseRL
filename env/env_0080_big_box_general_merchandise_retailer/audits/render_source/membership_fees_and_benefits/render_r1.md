# Renderer notes, membership render round 1 (saved verbatim by the coordinator from the renderer's final reply; agent acaaa9337b6ef60d9; DOCS OK)

**Points for the coordinator (none blocked the render):**
1. **Business payment-hold rate.** The rule says the order's fulfilled date must fall before the date the held fee "settled". It doesn't say what happens if that fee has not settled yet. The calculation treats an unsettled fee as still inside the hold. I kept the source wording as it stands.
2. **Two quantities filed with the calculation, used by one factor.** In the three Cash reversal policies, the units on the return and the return or refund date are listed as plain bindings, but only one factor uses each. Their defining sentences come from the factor text, so I explained them in the factor documents and left them in the calculation document's metadata, as the gate requires.
3. **Zero refunds can't be booked.** Both cancellation tools reject a refund amount that isn't positive. The rules allow the refund to come out at zero ("never below zero"), and a cancellation with a zero refund then can't be completed through these tools.
