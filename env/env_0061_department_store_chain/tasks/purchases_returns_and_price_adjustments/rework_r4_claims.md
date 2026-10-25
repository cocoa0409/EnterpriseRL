# rework r4 claims — purchases_returns_and_price_adjustments

- R3-N1 → I took the consistent-schedule route. One company sales tax schedule now holds in every passage and every seeded row: a Finch Note is a store discount, so sales tax is due only on the selling price less the notes paid. The base order charter states no tax base, so this departs from no base sentence.
  - The shelf-price correction and registry price protection tax sentences now divide by the selling price less the applied Finch Notes, with a zero-divisor guard.
  - The registry credit, note and gift card shortfall caps measure "what those tenders should have paid" through a per-policy due amount. That amount is the taxed price (selling price less the larger of applied and ledger-redeemed notes) plus the tax due on it at the rate the unit was taxed.
  - The note tax refund is the recorded tax less that tax due.
  - Task 1's note-paid purchases are seeded with tax on the price less the note, and their captures and card charges are adjusted. The rationale's statement that those purchases were correctly charged is now true under the schedule.
- R3-O1 → considered. The note tax refund is the store's separate sales-tax correction for tax figured on a price a note had already lowered. It is scoped to the undeducted-note case only; any other tax overcharge on a note-paid part stays under the base register-error rule through the shared carve-outs.
- R3-O2 → considered. The two prerequisite sentences of the gift card claim name different quantities: the money taken for the note's part, and the tax charged on it. Each resolves to exactly one policy.
- Class sweep → every passage that uses tax (scope, overwrite, formula, baseline, basis) states the same schedule. Every compute_basis quote is verbatim in its rule. No policy uses the recorded tax as owed on a note-paid part.
- Probes → on scratch copies the figures behave as the rules state:
  - a note-paid purchase taxed per the schedule yields no note or tax shortfall;
  - a unit fully paid by notes evaluates without error on both tasks;
  - the r3 probes still hold (expired second Bonus Card, closed card, closed earlier membership listed first, correctly recorded mixed-tender unit).
- Task 0 → its unit carries no Finch Note, so its world, tree and figures are unchanged; gates re-run green.
- CG-O1, CG-O5, CG-O6, CG-O8 → unchanged and considered, as in earlier rounds.
