# XF / source-hygiene recipe (coordinator, env_0066)

Renderers and KB auditors in past runs found every class below AFTER policy PASS, in almost every extended product.
Each costs rework -> policy re-audit -> re-render -> KB re-audit. Apply every point to EVERY extended policy in your charter
(reworkers), and check every point on every policy (policy auditors: any member is RED, not an observation).

1. Assembly sentences. No rule sentence assembles several factor quantities by name ("the amounts from the schedules below are
   added...", "credits apply after the surcharge..."). Each factor contributes on its own against a quantity the baseline
   (standard method) defines. Assembly lives only in plain bindings / `result`, stated ONCE, generically, without naming any
   factor's quantity.
2. Non-commuting order. Wherever adjustments do not commute, that one generic combination sentence still fixes the order in
   words that name no factor quantity (e.g. "replacements first, then caps, then additions"); otherwise a second reading appears.
3. Factor independence (transitive). No factor's tiers read another factor's binding or output; no result is assembled inside
   a factor binding; no factor is gated through another factor. A record selection several factors share is a plain non-factor
   binding stated once in the rule.
4. Ownership. A quantity only one factor uses belongs to that factor, not to the standard method. No rule phrase defines a
   quantity "as another policy figures it".
5. compute_basis quotes. Every quote is verbatim in its own rule (check_extended does NOT check this; sweep it with a script).
6. Ties. Wherever a read picks the latest / earliest / first record, the rule states what happens on a same-date tie, and it
   matches what the DSL does (LATEST keeps the first row).
7. Counting conventions. Whole-month / whole-year / day counts: the rule states the convention (month-end, inclusive/exclusive
   ends, negative lag) and it matches MONTHS()/DAYS() exactly.
8. Every branch both ways. Every branch the compute takes (absent record, zero, None, negative difference, out-of-scope case)
   is stated in the rule, and every rule branch is in the compute. An "otherwise the base sentence applies" scope must be
   reachable in compute or stated as outside this policy's tool.
9. Base clauses. An extended rule that contradicts an in-force base clause declares an overwrite with a scoped replaced_by
   that restates every still-in-force part of the retired clause for out-of-scope cases and names its own scope (and any
   sibling policy's case retiring the same clause). A rule never defers to a base clause its own overwrite retired. No
   overwrite retires nothing or a clause that never conflicted.
10. Rounding. The rule's rounding sentence matches the RND placement in the compute.
11. Tools. A docstring claims only effects the tool body has; no concrete example values (formats only); no ordering words
    ("before", "after", "ahead of", "toward the ...") that restate another problem's dependency.
12. Proof text. design_rationale, prerequisite_closure, factor_trace labels, step numbers and persona timing agree with the
    current artifacts; every stated equation recomputes.
