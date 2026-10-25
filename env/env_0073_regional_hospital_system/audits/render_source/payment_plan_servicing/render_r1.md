# Renderer findings — product plan (difficulty payment_plan_servicing), render round 1
Saved verbatim by the coordinator from renderer agent ad74f586e660a0457 (2026-10-21). Scan-first STOP; no document written.
Gate read: `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN`.

## Source mismatch (blocking)
- File: `tasks/payment_plan_servicing/plan.extended.yaml`
- Policy: `plan_ext_offer_refigure` (tool `refigure_plan_offer_04613189`, which takes `term_months` as a required argument).
- Two sentences of the rule give different `term_months` whenever the offer floor applies.
  - The baseline rule (line ~2321, repeated in the `compute_basis` quotes for `financed`, `term_used` and `result`) says: "the installment is the financed amount divided by the term used, rounded half-up to the cent, never below the offer floor, which is the tier's min_monthly_payment_usd as standard; **the offer is then booked with that installment and the term used.**"
  - The overwrite `replaced_by` of the `plan_tier_and_installment` installment clause (line ~2288, carried verbatim into the rule) says: "its installment is the financed amount this rule figures divided by the term it uses, rounded half-up to the cent, never below the offer floor, **and when the offer floor applies the offer is booked with as many installments as that floor needs**".
- Why it matters: when the floor binds, the first sentence books `term_used` (compute: `term_used: MX(1, MN(tf_term, tb_term))`); the second books "as many installments as that floor needs", a different, normally smaller number, computed by no binding (compute has only `result: MX(ofloor, RND(financed / term_used + 0.000001, 2))`) and with no rounding given. The floor case is within this policy's own scope (offers whose balance fell through reductions or a dispute withdrawal can drop under the floor; the `offer_floor` factor exists so the floor matters).
- Fix belongs on the instantiate side: drop or scope the "as many installments as that floor needs" clause for re-figured offers, or make the baseline's booking sentence conditional and state how that count is figured.

## Note (renderer did not count it a defect)
In `plan_ext_assistance_pause`, the `start_idx` branch for a plan with no next due date is `MONTHS(F('first_due_date'), receipt)` with no lower bound of minus one. A receipt date more than a month before the first due date adds phantom installments to the pause window. The rule's words ("a later date before the starting date gives a negative count") reproduce this literally, and only paid-off or cancelled plans lack a next due date.

## Clean
compute_basis quotes verbatim; prerequisite sentences and replaced_by texts in their rules; superseded clauses present in base; sibling overwrites of the down-payment clause name each other; tool docstrings match bodies; no factor id inside a tool name; rule words match compute elsewhere (ties, month convention, rounding placement).
