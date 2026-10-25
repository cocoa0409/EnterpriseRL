# Source-side notes from the KB audits — copied verbatim by the coordinator (rework input alongside render_funding_r2.md)

## From the funding KB audit (agent a0ff99cf4efd3fe3a), round 1 — verdict task0=PASS task1=PASS
**Source-side notes (none change a verdict):**
1. Three calculation documents say a figure is zero "unless a rule of this product sets" it, which hints that adjustments exist. The source's own baseline says "unless the rule below sets it", so the KB is faithful and the hint comes from the source.
2. The calculation steps that combine the results name the adjustments (allowances, credit cover, re-send/re-review/relock days, late-booking interest). That is the source rule's own wording, carried as written.
3. The payment channel charge applies to "interest collected after closing", but the shortfall rule has no channel charge. The source leaves this open; it has no effect on these seeds.
4. The set-off per diem rule points to "a prepaid interest dispute", and the refund-per-standing-day rule checks the prerequisite's ledger state. Both are the source's own text.
5. The dispute rule says a late-funding dispute is "still decided by recomputing…" and also that it "is not decided under this rule". The tension is in the source and doesn't touch the per diem overcharge branch scored here.
6. One small rendering flaw, outside both tasks' policies: the document-draw timetable says signed-package review is "0 where funds go out at signing", but its own Power of Attorney row shows 1. The figure is right and no rule changes, so it isn't marked RED.

## From the credit KB re-judge (agent a06577c8bd891b487), round 2 — cross-product note
**One cross-product note (affects neither task):** funding's `closing_cost_credit_cover_of_shortfall` looks for a credit "applied to prepaid items on the signing date". The credit rule says credits pay prepaid items "only on the disbursement date". On a dry-funding or rescission closing those dates differ, so that funding factor could never fire. The fix belongs to the funding product.
