# XF / render-surfaced defect recipe (coordinator checklist, env_0072)

Every point below has, in earlier runs, been found by a renderer or KB auditor AFTER the policy audit
passed, and each cost a full rework -> policy re-audit -> re-render -> KB re-audit loop. Instantiators:
design against every point before writing. Policy auditors: check every point on every extended policy;
any member is RED, not an observation.

## A. Factor independence and assembly (the XF class)
1. Every factor contributes ON ITS OWN against a quantity the baseline (standard method) defines. No factor
   tier reads another factor's binding, output, or tier; check what each factor reads, transitively.
2. Shared record selections used by several factors are plain NON-factor bindings, stated once in the rule.
   A plain binding never reads a factor-owned binding.
3. Assembly (how factor contributions combine into the result) lives only in plain bindings / `result`,
   stated ONCE, generically, without naming factor quantities.
4. The generic combination sentence still FIXES THE ORDER wherever adjustments do not commute
   ("replacements first, then caps, then additions"); otherwise a second reading exists.
5. A quantity only one factor uses belongs to that factor, not to the baseline. The baseline is
   self-sufficient: the standard method and default values, silent about every variation.
6. No rule phrase defines a quantity "as another policy figures it"; no factor is gated through another
   factor; no single convention sentence serves several factors.
7. No factor id may be a substring of any tool name (check_docs fails "hub repeats hidden factor name").

## B. Method factors and tiers
8. A `method` tier changes the formula SHAPE, not a multiplier. Shape test: any aggregate of the same field
   counts as one input whatever its window/filter; constant multipliers are ignored. A pair FAILS if both
   tiers are the same combination of the same windowed sums; it PASSES if one tier adds an input or an
   operation (floor, max/conditional pick, data-selected window, tariff parameter). A "nothing" tier fails
   where another tier is also 0 across its whole domain. Provide an all-pairs tier table with a
   distinguishing input for every pair.
9. Tiers neither gap nor overlap over the policy's own scope (re-check against scope, not just the world).
10. Factors a real program would use (no loyalty/tenure/claim-count inventions); geographic or legal tiers
    are real law or worded as the company's own schedules. Federal/state statutory items follow the real rule.

## C. Rule words == compute, at every edge
11. Every rule sentence matches the compute exactly, including at edge inputs: None/absent record,
    zero, negative balances, empty lists, division by zero, date difference of 0 or negative lag.
12. Every first-match read (CFIELD/LATEST) and every aggregate is probed with a decoy row (cancelled,
    voided, reversed, expired, prior-term, second record) on a scratch copy; list the absent-record case of
    every read with its rule tier. Same-day ties: state which row wins (LATEST keeps the first row).
13. Month-end and whole-month/year counts: the rule's wording of the count matches MONTHS()/DAYS() exactly.
14. Rounding: the rule's rounding sentence matches the RND placement in compute.
15. Entries are never counted as periods (or vice versa) unless the rule says so.
16. Every `compute_basis` quote is VERBATIM in its rule (check_extended does not check this — sweep it).
17. Framing clauses assert no fact that no record holds; every rule word for a field names a field the
    records actually carry.

## D. Overwrites
18. An overwrite retires only clauses that genuinely conflict; it never retires nothing.
19. `replaced_by` names its OWN scope and restates the in-force content for out-of-scope cases (do not just
    say "every other ... remains under the base rule" if the retired clause carried parts still in force:
    rounding, dates, definitions, invoicing).
20. Sibling overwrites retiring the same base clause: each tail excludes both its own case and the sibling's
    case by name.
21. A rule never defers to a base clause its own overwrite retires; an extended rule never contradicts an
    in-force base clause without an overwrite.
22. Any departure from a base sentence is declared.

## E. Prerequisites and DSL routes
23. Coordinator/rework routes are phrased as record tests or state-form waits, never "if policy X would
    compute ...".
24. Pairing rules across two holdings / dates across two records cannot be computed (filters are exact-value,
    windows run from today, CFIELD is first match, no holding count). Route: scope via a self-naming
    overwrite to a single-record case keyed by an exact value; out of scope gets the BASE figure, computed.
25. No 0.00 edge on a prerequisite: make it impossible with a realistic cap, or carve it out with a record
    test; check db_schema field meanings (e.g. "positive" amounts) before any route.
26. Trigger rule: list every event your tools write with its base `triggers`; none may land in another
    category (unconditional cross-category triggers mean that event is not yours to write).

## F. Seeds and docstrings
27. Cross-category seeded rows are states the owning charter can produce, priced with the OWNING charter's
    formulas (base rate, fee shares, servicing records), with complete ledgers (every billable row posted,
    every periodic review reproducible) and every priced row's look-back inside seeded records (seed the
    holding's history from origination).
28. No concrete example values in tool docstrings or parameter descriptions (describe the format only);
    a docstring never claims an effect the tool body lacks.
29. Stale proof text: after any change, sweep design_rationale, prerequisite_closure, necessity text and
    every stated equation for claims made stale.

## G. Renderers
30. Scan the source FIRST; on any mismatch with points 1-29, report it quoted and STOP before writing any doc.
31. No worked example whose figures equal a scored value; no factor document names or describes another
    factor; base text (including stale parameter descriptions) is carried verbatim; no file outside
    docs/<product>/.
