# Renderer findings — product setaside, render round 1 (agent aa8d23fece403171d, 2026-10-15T12:50Z)
Saved verbatim by the coordinator from the renderer's final report (source-mismatch sections only).

## Source mismatch (the "assembles several factor quantities" class)

It affects `setaside_ext_reserve_tax_projection`, `setaside_ext_reserve_hazard_projection` and `setaside_ext_reserve_flood_projection`.

Each rule has an assembly sentence that combines several factor quantities, and none of it is in `baseline.rule`:
- **Tax:** "The next tax year's tax is the tax year's tax increased by the assessment allowance percentage and then increased by the exemption allowance amount." and "The projected annual property tax blends the two years over the twelve months after the review: it is the tax year's tax times one less the next-year share, plus the next tax year's tax times the next-year share."
- **Hazard:** "The renewal hazard premium is the current hazard premium increased once by the hazard renewal loading, which is the sum of the premium-change loading, the occupancy loading and the appraisal loading … applied once to the current hazard premium" and "it is the current hazard premium times one less the hazard renewal share, plus the renewal hazard premium times the hazard renewal share, plus the hazard pay-plan fee."
- **Flood:** the same pair, with "the residence loading" in place of the occupancy loading and no fee.

The two assembly quantities are plain bindings (`next_year_tax`/`renewal_prem` and `result`), so the computation document must carry them. But `baseline.rule` says only "The projected annual property tax is the tax year's tax …" (and the same for the current hazard or flood premium). So the computation document would have to name the factor-only quantities (assessment allowance, exemption allowance, loadings, share), or the factor documents would have to name each other.

On top of that, these factors only work through another factor. `tu_assess` and `tu_exempt` change the result only when `tu_span`'s share is above zero. Likewise `hu_change`/`hu_occ`/`hu_appraisal` need `hu_span`, and `fu_change`/`fu_residence`/`fu_appraisal` need `fu_span`.

The tax rule also contradicts itself, because its baseline sentence is embedded in it. It says both "The projected annual property tax is the tax year's tax, which is the sum of … paid or received" and that it "blends the two years", with `tu_basis` giving a different tax year's tax.

**Held back (15 docs):** the three computation documents, plus `tu_assess`, `tu_exempt`, `tu_span`, `hu_change`, `hu_occ`, `hu_appraisal`, `hu_span`, `fu_change`, `fu_residence`, `fu_appraisal` and `fu_span`.

## Lesser observation

`setaside_ext_returned_tax_refund` says "The credit references the reserve's payment of the overpaid installment". It doesn't say which payment is meant when more than one paid installment of the tax year is overpaid.

## check_docs at stop
DOCS NOT OK — 97 failures, all from the held-back projection documents (uncovered compute bindings, 0 computation/factor docs for the three projection policies, their constants undocumented). No leak, tool, prerequisite, retired-clause or tier-value failures.
