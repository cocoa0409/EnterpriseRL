# XF recipe — how this scenario closes the "assembly" class and its neighbours (coordinator-written)
Every extended product in this scenario (setaside, residency, maturity so far) stopped at render on this class.
Apply ALL points to EVERY extended policy of your charter, then verify each mechanically.

1. **Baseline defines every quantity.** The baseline / "under the standard rule" paragraph defines every quantity the
   rule's combination uses, each with its standard/default value (a measured extension, a window count, a base count,
   a share, a loading, an allowance …). It never names a factor and never says "the … set out below take the place of …".
2. **Each factor owns one quantity.** A factor's text replaces only its own quantity, says what it replaces ("added to
   the <baseline-defined quantity>"), and never reads or names another factor's quantity or binding.
3. **Each factor acts on its own.** With all other factors at their defaults, each factor alone moves the result in at
   least one reachable world (solo test), and removing it changes the task's result (removal test). Where a policy is a
   genuine all-limits-must-hold gate, every limit must be a baseline-defined quantity with a default, the gate sentence
   names only those baseline quantities generically, and each limit factor's document can be read alone.
4. **Combination stated ONCE, generically, with order fixed.** "The measured quantity with every addition made and every
   deduction taken; replacements first, then caps/floors, then additions" — say the order wherever the adjustments do
   not commute (floor-then-add ≠ add-then-floor), otherwise a second reading appears. Floors/caps applied in `result`
   must be in the rule and in the baseline.
5. **No cross-policy definitions.** No rule phrase defines a quantity "as another policy figures it" or "sized by its own
   … rule".
6. **Overwrites.** A replaced_by restates the still-in-force content of the retired clause for every out-of-scope case,
   then names its own scope; it never defers to the clause it retires ("as the base rule provides"), never drops
   qualifiers of the base clause, and never points at "the … fixed below". A rule never relies on a base clause its own
   overwrite retires — restate it.
7. **Quotes.** Every compute_basis quote is verbatim in its rule (check_extended does NOT check this — sweep it with a
   scratch script). Every rounding sentence matches the RND placement.
8. **Branches.** Every branch the compute takes is stated in the rule and its ladder, and vice versa: absent record,
   None, zero, negative lag / record dated before the event, a value of another type, ties. No sentinel (999, 0) that
   the rule does not state; no computed-but-unused gate.
9. **Docstrings** state no figure, ordering or effect the body lacks.
