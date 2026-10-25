# Render pre-scan findings — product vision, render round 2
Source: renderer agent a809460d215f9f785, 2026-10-20; saved verbatim by the coordinator. STOPPED before writing. Gate line read: `VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN`.
Round-1 findings 1, 2, 4, 5, 6, 7 closed; finding 3's fix placed so it creates R2-1.

- **R2-1: the "fitting follows" sentence matches the compute but is missing from `baseline.rule` (out-of-network glasses claim and out-of-network contact-lens claim).**
  - The sentence is *"A fitting line follows its claim's contact-lens line: when the contact-lens line receives no reimbursement (its benefit blocked by frequency or missing, its amount 0.00, or the line left out in lieu), the fitting line receives none either and carries the contact-lens line's remark; a fitting on a claim without contact lenses is reimbursed on its own."*
  - In `compute_basis` it is attributed to the in-lieu factor bindings (`g_lieu` and `c_lieu`).
  - But the behaviour is implemented in the non-factor `result`, for every in-lieu tier including the base tier `'none'`: `… if ((MN(g_cr, g_camt) if g_cok else 0.0) > 0 or g_cid == '') else 0.0`, and the same condition on `c_cok` and `c_camt`.
  - Neither `baseline.rule` carries the sentence. Both still say only *"the fitting is not limited separately"* and *"…oon_exam_reimbursement for a routine exam and for a fitting"*.
  - With every factor at its base value and the contact lenses blocked by frequency, the base rule therefore pays the fitting the lesser of its receipt and `oon_exam_reimbursement`, while the base compute pays 0.00.
  - The in-lieu factor would also end up describing frequency and zero-amount behaviour that has nothing to do with in-lieu. This is the same class as round-1 finding 4.
  - Likely fix: put the sentence into both `baseline.rule`s and attribute it to `result`.
- **R2-2: the contact-lens order's base rule never says what the "outside-benefit discount rate" is.**
  - `baseline.rule` uses the rate twice: *"bought at the outside-benefit discount rate off their retail charge"* (not-covered case) and *"bought at the outside-benefit discount rate off its retail charge"* (frequency case).
  - The defining sentence, *"…are bought at their retail charge less the outside-benefit discount rate, which is materials_discount_pct percent."*, is only in the full rule. It is not in `baseline.rule` and has no `compute_basis` quote.
  - So the computation document, rendered from `baseline.rule`, cannot reach a figure, even though `result` uses `P('materials_discount_pct')` (plus `k_ppct`) on those paths.
  - Likely fix: put that sentence into `baseline.rule` and attribute it to `result`.
