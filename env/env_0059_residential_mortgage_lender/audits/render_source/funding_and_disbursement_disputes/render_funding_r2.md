# Remaining source mismatches reported by the funding renderer (agent a42998df730df58cd), render round 2 — copied verbatim by the coordinator

Rendered source: funding.extended.yaml dce3a85f0976488a276b413271ba03e5218d68800e7cec0dd4ece9e868f76f8a, task_tools.py b1cb423250eba6e808b0c4eb2ce775c85ca272000679a4166547d0ff7a553e8b. docs/funding/ republished (58 docs, DOCS OK).

**Remaining or new source mismatches (rendered as they stand):**
1. **Computation texts in the source signal that factors exist.** All four are in `baseline.rule`:
   - fm: "There is no setoff and no payment channel charge unless a rule below sets one."
   - dd: "Unless the rule below sets it, the refund per standing day is zero." and "Unless the rules below set an interest rate and interest days, the excess carries no interest."
   - rd: "Each add-on and the repeat-redraw fee is zero unless a rule below sets it."
   I carried them, changing only "below" to "a rule of this product", since "below" has no meaning in the KB. As a result, those three computation documents are not silent about factors.
2. **fm card percentage stated two ways.** `funding_ext_funding_month_interest` rule says flatly "The card convenience percentage is card_convenience_pct." The next sentence's ladder contradicts it: zero in CT, MA and ME, and card_surcharge_cap_pct (2.0) in CO. I rendered both together in the card surcharge document.
3. **dd late-funding scope.** In `funding_ext_interest_dispute_decision`, the overwrite's replacement keeps "a late-funding dispute is still decided by recomputing prepaid interest … any excess refunded as refund_issued". The rule then says "A late-funding, closing-fee or returned-wire dispute is not decided under this rule". The two sentences disagree on whether late-funding disputes fall under this policy.
