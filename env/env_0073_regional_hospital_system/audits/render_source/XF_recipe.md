# XF recipe — source-layer defect classes that renderers and KB auditors found AFTER policy PASS in earlier runs

Coordinator file. Every instantiator applies every point to every extended policy before calling its gates green; every policy auditor checks every point on every policy, and **any member is RED, not an observation**. Renderers scan the source for every point FIRST and STOP (quote, write no doc) on any hit.

## A. Factor independence and assembly
1. Each factor contributes on its own against a quantity the baseline defines. No factor tier reads another factor's binding or output, transitively (check mechanically: list what each factor's bindings read, follow every plain binding down to records/params).
2. Shared record selections are plain non-factor bindings stated ONCE in the rule; `result` (or plain bindings) assembles the amount. No result is assembled inside a factor binding.
3. The assembly sentence is stated once, generically, without naming any factor's quantity ("the adjustments described below are applied to the standard figure" — not "the charity percentage and the prompt-pay discount are added"). But wherever adjustments do not commute it still fixes the order in generic words ("replacements first, then caps, then additions").
4. A quantity only one factor uses belongs to that factor, not to the baseline. The baseline is self-sufficient (standard method + default values) and silent about variations. No factor is gated through another factor; no single convention sentence serves several factors (each factor states its own).
5. No rule phrase defines a quantity "as another policy figures it". Coordinator routes and cross-policy waits are record tests or state-form waits, never "if policy X would compute …".

## B. Rule words == compute, in every case
6. Every edge input has a rule sentence and the compute agrees with it: absent record, None, zero division, negative lag / date before anchor, empty list, credit in a negative balance, 0.00 results.
7. Same-day ties: state the tie rule (LATEST keeps the first row in file order — say which row wins in business words).
8. Whole-month/year counts vs MONTHS(): state the month-end convention the compute uses. Entries are not periods.
9. XCOUNT/XSUM filters carry every exclusion the rule states (cancelled, voided, reversed, prior-term rows) and nothing the rule does not.
10. The rule's rounding sentence matches the RND placement in compute exactly (what is rounded, when, to what).
11. `compute_basis` quotes are verbatim substrings of the rule (check_extended does NOT check this — sweep them with a scratch script).
12. No rule word refers to a field the records lack; no framing clause asserts a fact no record holds.
13. Tier ladders: no gaps, no overlaps, boundaries stated with their figures; every tier re-checked against the policy's own scope, not only this world.

## C. Method factors
14. A `method` tier changes the formula's shape, not a multiplier or a window length. Structural test: any aggregate of the same field counts as one input whatever its window or filter; constant multipliers are ignored. A pair of tiers FAILS if it is the same combination of the same windowed sums; it PASSES if one tier adds an input or an operation (floor, max/conditional pick, data-selected window, tariff parameter). A "nothing" tier fails where another tier is also 0 across its whole domain. Provide an all-pairs tier table with a distinguishing input for every pair.

## D. Overwrites
15. An overwrite retires exactly the base clauses that conflict — no overwrite that retires nothing, none that retires clauses never in conflict, and no extended rule contradicting an in-force base clause without an overwrite.
16. `replaced_by` restates the still-in-force content of the retired clause for out-of-scope cases (rounding, dates, definitions included) and names its own scope: "for a <X> this policy handles …, and only for such a <X>; every other <X> remains under the base rule". Sibling overwrites of the same clause each exclude both their own case and the sibling's case by name.
17. A rule never defers to a base clause its own overwrite retires. Undeclared departures from a base sentence are RED.

## E. Tools, schema, runtime
18. task_tools.py: no `datetime`/`time`/`random`/`uuid`/`secrets` imports or tokens anywhere (validate_scenario rejects them); do date maths with a pure-Python ordinal-day helper as a class static method (a module-level helper is treated as a tool). Every write tool calls ctx.create/update/delete in its own body.
19. frozen_time is `YYYY-MM-DD HH:MM:SS <TZ>` (no ISO 'T').
20. No factor id may be a substring of any tool name.
21. No concrete example values in docstrings (describe the format only) — a docstring example once equalled gold. Docstrings claim only effects the body performs.
22. No composed multi-value string args; one enumerated arg per field.
23. No task tool writes a row of an event whose base `triggers` land in another category. List every event your tools write with its base triggers.
24. Check the frozen db_schema field meanings before any route (e.g. a field documented "positive" cannot take a 0.00 row).

## F. Seed realism (cross-product)
25. Every seeded row of another category is a state the owning charter can produce, priced with that charter's formulas as of the row's posting date (discounts, AGB, contractual adjustments, installments, fees), with complete ledgers: every billable row billed, every periodic review reproducible, every liability posting backed by its claim/remit, every status reached by the owning charter's lifecycle.
26. Every priced row's look-back window falls inside seeded records (seed the holding's history from its start).
27. Federal/program rules (No Surprises Act, IRS 501(r), HIPAA right of access, Medicare/Medicaid/ACA appeal rules, payer contracts) are carried with their real figures; Riverbend's own schedules are worded as Riverbend's own. No invented statutes, no loyalty/tenure ladders a real hospital would not use.
