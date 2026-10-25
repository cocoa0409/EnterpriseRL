# Coordinator rework checklist (env_0065) — classes that recurred across past runs

Close each class across the WHOLE charter (every computation, every ladder, every read), not just the instance an audit quoted. Record a table per class in your worklog.

## A. Factor structure (renderers found these after policy PASS in every past run)
1. Every factor contributes on its own against a quantity the baseline (standard method) defines. A quantity only one factor uses belongs to that factor, not to the baseline.
2. Assembly lives only in plain bindings / `result`, stated ONCE in the rule in generic words that name no factor quantity ("the adjusted amounts are combined …"), never "plus the X allowance, the Y relief and the Z credit".
3. Where adjustments do not commute, that one generic sentence still fixes the order in kind-neutral words a reader can apply (e.g. "replacements first, then limits, then additions"), or a second reading appears.
4. No factor's tiers read another factor's binding or output (check transitively; table: factor → fields/bindings read). A record selection shared by several factors is a plain non-factor binding stated once in the rule.
5. No factor is gated through another factor; no rule phrase defines a quantity "as another policy figures it"; no result is assembled inside a factor binding.
6. `method` changes the formula's shape; a multiplier/rate/day-count/window swap is a `parameter`. Tiers must not coincide on their reachable domain: pairwise tier table with one distinguishing input per pair. A tier condition that every customer reaching the write meets is not a tier.
7. Baselines are self-sufficient and coherent: one figure, one fall-back, no two readings.

## B. Rule ↔ compute
8. Every branch, condition, floor, cap and record scope the compute takes is stated in the rule, and vice versa.
9. `compute_basis` quotes are verbatim in their rule — `check_extended` does not check this: sweep them with a scratch script.
10. Rounding: the rule's rounding sentence states exactly what the compute does, at the same placement (half-up vs Python round() differ on ties — make them agree and probe a tie).
11. Undefined terms ("the re-rating date", "the term") are defined in the rule as the compute reads them.

## C. Reads and probes
12. Every first-match / latest / aggregate read is scoped to exactly the record the rule names (this policy, this claim, this term, this address), with a decoy probe (cancelled, voided, expired, second record, earlier cycle) and an absent-record tier. List the probe table.
13. A prerequisite sentence's literal scope must equal its declared condition, and the condition must be genuinely unmet at the opening (no earlier cycle, paid-off loan or cancelled record that literally satisfies it; no condition that is vacuously true before an in-task write).

## D. Base and overwrites
14. Every departure from a base sentence is a declared `overwrite`; its `replaced_by` restates the still-in-force content for out-of-scope cases and names its own scope ("for a … this policy handles, and only for such a …"); sibling overwrites of one clause each exclude both cases by name.

## E. World and realism
15. Seeded cross-category rows are figures their owning base charter would actually produce (recompute them with that charter's rule), consistent in time.
16. Realism: factors are rules a real flood insurer applies. For NFIP lines, FEMA sets premium, fees, credits and refunds — a WYO company cannot add or remove days or amounts of federal premium for its own servicing reasons. Use real Flood Insurance Manual / SFIP rules applied to recorded fields (cancellation reason → refund method and claim-paid bar; primary residence → HFIAA surcharge / policy fee tier; probation surcharge; waiting-period basis and its statutory exceptions; endorsement pro rata over the remaining term; statutory renewal cap by building category; EC applied only when it lowers the premium; refund payee by premium payor; RFA on premium). A company schedule may govern only what the carrier really controls.

## F. Proof text
17. After every change, sweep design_rationale, prerequisite closure, necessity text, probe figures and trace arithmetic for statements made stale.
