# Renderer findings — product estimate (difficulty good_faith_estimates_and_disputes), render round 1
Saved verbatim by the coordinator from renderer agent a2f5ec4fd36290891 (2026-10-21). Scan-first STOP; no document written.
Gate read: `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN`.

## 1. Policy `estimate_ext_surgical_balance`: a quantity only one factor uses sits in the baseline (A.4)
File: `tasks/good_faith_estimates_and_disputes/estimate.extended.yaml`
- The compute line `implant_total: SUM(... service_code='V2787') + SUM(... 'V2788') + SUM(... 'C1713') + SUM(... 'C1776')` is a plain binding, not one of the factor's bindings.
- Factor `implant_share` lists only `bindings: [premium_lens_lines, other_implant_lines, implant_share]`.
- The total is used in exactly one place: `balance_figure: aid_price - deposits_held + implant_share * implant_total - ...`. With the factor at its baseline value of 0 (`implant_share: '0'`), that term disappears, so `implant_total` matters only when the factor applies.
- The rule defines it in its own sentence, outside both `baseline.rule` and the factor's ladder sentence: "For the pre-service balance, the implant total is the sum of the Riverbend facility lines of the current version coded V2787 or V2788 (premium intraocular lenses) or C1713 or C1776 (other above-standard implants), the above-standard implants the package excludes and bills at actual charges less the uninsured discount."
- Why it can't be rendered around: the computation document would have to claim `implant_total` and define a quantity its own calculation never uses, which breaks the rule that it stays silent about variations. Putting the definition in the implant factor's document instead would split the binding's coverage from its prose.
- Suggested fix: move `implant_total` into the `implant_share` factor's bindings and put its defining sentence inside the "Implant share of the pre-service balance" sentence. The other four policies don't have this problem: their only factor-read plain bindings are the shared award and slot reads, which the result-side bindings also use.

## 2. All five tools in `task_tools.py`: the docstring claims rounding the code doesn't do (recipe 21)
- Every `amount` argument says: "the value is rounded half-up to the cent when recorded".
- Every body does `paid = round(float(amount), 2)` (or `fee = round(float(amount), 2)`). Python's `round` isn't half-up: `round(10.125, 2)` returns `10.12`, where half-up gives `10.13`. The compute avoids this with `RND(x + 0.000001, 2)`; the tool bodies don't.
- Fix: either change the docstring or make the bodies round half-up.

## 3. Smaller gap
`estimate_ext_surgical_deposit`, factor `moved_booking_points`: the rule says "three or more versions add ten percentage points, exactly two add five, and one adds none", but a count of zero has no rule sentence (the compute gives 0). Probably unreachable for a priced surgery package, but an unstated tier edge (recipe 6 and 13).

## Clean
compute_basis quotes, both prerequisite sentences and every replaced_by verbatim; superseded clauses verbatim; sibling overwrites exclude each other; 12-month look-back and month convention match compute; same-day tie stated; no factor id inside a tool name; no forbidden imports.
