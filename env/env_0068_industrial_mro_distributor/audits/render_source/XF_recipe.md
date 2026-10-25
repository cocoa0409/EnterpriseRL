# XF recipe — recurring source-side defect classes (coordinator checklist, env_0068)

Every point below has, in earlier runs, been missed by the policy audit and then surfaced at render or KB audit,
costing a full rework → re-audit → re-render loop. Apply every point to every extended policy before declaring
gates green. For auditors: any member of any class below is RED, not an observation.

1. Factor independence. Every declared factor contributes on its own against a quantity the baseline (standard
   method) defines. No factor tier reads another factor's binding or output, transitively (check mechanically what
   each factor reads). A quantity only one factor uses belongs to that factor, not to the baseline.
2. Assembly. Combining factor contributions lives only in plain bindings / `result`, stated ONCE generically in the
   rule without naming the factor quantities ("points from the four schedules below are added…" is the defect).
   Never assemble the result inside a factor binding. A record selection several parts share is a plain non-factor
   binding stated once in the rule. No factor is gated through another factor.
3. Order. Wherever adjustments do not commute, the generic combination sentence still fixes the order
   (e.g. "replacements first, then caps, then additions"); otherwise a second reading of the scored number exists.
4. No rule phrase defines a quantity "as another policy figures it"; each quantity is defined where it is used.
5. Overwrites. An overwrite must retire a clause that genuinely conflicts (never nothing, never a non-conflicting
   clause). Its `replaced_by` restates the still-in-force content of the retired clause for every out-of-scope case
   and names its own scope ("for a line this policy reprocesses…, and only for such a line; every other line remains
   under the base rule"). Sibling overwrites retiring the same clause each exclude BOTH their own and the sibling's
   case by name. An extended rule never defers to a base clause its own overwrite retires. An extended rule that
   contradicts an in-force base clause without an overwrite is RED; so is any undeclared departure from a base sentence.
6. Every `compute_basis` quote is verbatim in its rule (check_extended does not check this — run a scratch sweep).
7. The rule's rounding sentence matches the RND placement in the compute exactly.
8. Every effect a tool docstring claims exists in the tool body; no docstring or param description carries a concrete
   example value (describe the format only) — an example equal to a scored value is a gold leak.
9. Edges stated in the rule and matching the compute: same-day ties (which row LATEST/FIRST picks), month-end
   conventions of whole-month/whole-year counts vs MONTHS(), negative lags, absent-record branches, zero-division
   branches, None values.
10. Every exclusion/filter the rule states (e.g. cancelled or reversed records) is in the compute, and every filter
    the compute applies is stated in the rule.
11. Method tiers change the formula's shape (not a swapped multiplier or window length) and no two method tiers
    coincide on their reachable domain — keep a pairwise table with a distinguishing input.
12. The compute DSL cannot window one record's date against another record's date (pairing two holdings by date).
    Scope such a rule via a self-naming overwrite to a case with exactly one candidate record (count = sum of
    exact-status counts) and use a two-date DAYS test inside the scope.
13. Seeded rows of another category must be states that category's charter can produce (its statuses, fees, rates,
    trades); price them by that charter's rules.
