# Renderer notes, fleet render round 1 (saved verbatim by the coordinator from the renderer's final message; RENDER round 1: DOCS OK, 61 docs)

Four smaller items did not meet the stop bar:
- **Retail product name:** the rules say "Kestrel retail installment contract" but the compute reads only the retail category. The documents name it as "Kestrel New Vehicle Retail Installment Sale Contract", the official display name, so it can't be read as covering pre-owned contracts.
- **Two Kestrel Care plans on one VIN:** the termination maintenance credit and mileage maintenance multiplier rules don't say what happens if a VIN has both an active Platinum and an active Platinum Plus or Elite contract. The ladder and compute take the higher tier first, and the documents follow that.
- **Zero deficiency:** `fleet_ext_trac_shortfall_charge` says "the charge is then zero" when the figure comes to nothing. The docstring of `bill_trac_deficiency_eb6903d6` asks for "a positive number". This is a format line, not an effect claim, but the two pull against each other.
- **Fund movement in docstrings:** the refund and arrangement-payment docstrings say the funds are received or leave the business's account. The tool bodies only book the posting. I treated this as a description of the real-world effect, not a missing effect.
