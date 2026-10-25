# XF recipe — coordinator checklist for extended policies (env_0074)

Defect classes that, in earlier runs, passed the policy audit and were then caught by the renderer or the KB audit,
each costing a full rework → re-audit → re-render → KB re-audit loop. Instantiators apply every point to every
extended policy before declaring gates green; policy auditors check every point on every policy — **any member is RED,
not an observation**. This file states classes only; it holds no scenario content and no scored value.

## A. Factor independence and assembly
1. Every declared factor contributes on its own against a quantity the **baseline** defines. No factor tier reads another
   factor's binding, tier or output — check this mechanically and transitively over the compute.
2. Record selections shared by several factors are **plain non-factor bindings** stated once in the rule; `result`
   assembles the amount. No result is assembled inside a factor binding.
3. The assembly sentence is stated ONCE, generically, in the rule, and never names factor quantities
   ("the points from the four schedules below are added…" is the defect). Factor-only quantities belong to that factor;
   the baseline defines no quantity that only a factor uses.
4. Where adjustments do not commute, the generic combination sentence still fixes the order ("replacements first, then
   caps, then additions") — otherwise a second reading of the result exists.
5. No rule phrase defines a quantity "as another policy figures it"; no factor is gated through another factor
   ("only when the X schedule applies").
6. Two acceptance tests for every factor — T1: on this task's world, substituting the factor's baseline alone moves the
   scored result. T2: some producible world exists where the factor moves the result with every other factor at
   baseline. Computations shaped like min/max of several caps fail T1/T2 easily: only one cap binds at a time.
7. Method factors change the formula's **shape**, not a multiplier or a window length. Shape test: count any aggregate of
   the same field as one input whatever its window or filter, ignore constant multipliers; a pair of tiers FAILS if it
   is the same combination of the same windowed sums, PASSES if one tier adds an input or an operation (floor,
   max/conditional pick, data-selected window, tariff parameter). A "nothing" tier fails where another tier is also 0 on
   its whole domain. Keep a pairwise tier table with a distinguishing input for every pair.
8. Fall-through tiers: no gaps, no overlaps, and an explicit tier for the absent record.

## B. Rule text == compute, in every case
9. Every `compute_basis` quote is verbatim in its own rule (check_extended does not check this — sweep it with a
   scratch script).
10. The rule's rounding sentence matches the RND placement in the compute exactly.
11. Edge branches are stated in the rule and computed identically: absent record, None, zero divisor, negative lag,
    empty list, same-day ties (which row a LATEST/first-match read keeps), month-end conventions for whole-month /
    whole-year counts vs MONTHS().
12. Probe every CFIELD / first-match / LATEST read with a decoy row on a scratch copy: a cancelled, voided, reversed,
    prior-period, second or absent record. Keep the probe table in your worklog.
13. No framing clause asserts a fact that no record holds; no rule word names a field the records lack.
14. Coordinator routes are record tests or state-form waits, never "if policy X would compute …".

## C. Overwrites
15. `replaced_by` restates the still-in-force content of the retired clause for out-of-scope cases (including its
    rounding, dates and definitions) and then names its own scope ("for a … this policy …, and only for such a …;
    every other … remains under the base rule").
16. Never retire a clause that does not conflict; never leave an overwrite that retires nothing; never contradict an
    in-force base clause without an overwrite; never defer to a base clause your own overwrite retires.
17. Sibling overwrites retiring the same base clause each exclude both their own case and the sibling's case by name.
18. Any departure from a base sentence is declared.

## D. Tools and docstrings
19. Docstrings carry no concrete example values (describe the format only) and claim no effect the body lacks; no
    docstring names another tool or carries an ordering word.
20. No factor id is a substring of any tool name.
21. No composed multi-value string arguments: one enumerated argument per field, values listed as a format.
22. Every write tool calls ctx.create/update/delete in its own body (helpers may only compute values).
23. task_tools.py imports no datetime/time/random/uuid/secrets (substring-matched anywhere in the file); do date maths
    with a pure-Python ordinal-day helper written as a class static method (a module-level function counts as a tool).
24. `frozen_time` is `YYYY-MM-DD HH:MM:SS <TZ>` (no ISO `T`).
25. List every event your tools write with its base `triggers`; none may land in another category.
26. Check the schema's field meanings before writing a 0.00 row (amount fields declared positive cannot hold 0.00).

## E. Realism (the scenario definition makes realism the first priority)
27. Federal / state program figures and rules (Medicare Part A SNF benefit, Medicaid patient pay and PNA, trust fund
    rules under 42 CFR 483.10(f)(10), bed-hold and discharge notice rules) are the real rules — never invented company
    "relief", "allowance" or "loyalty" factors on top of a government-set amount. Company-set items (private rates,
    ancillary price schedules, private bed-hold charges, late charges, deposits) are the operator's own published
    schedules and must look like what a real SNF operator publishes.
28. No tenure / loyalty / claim-count ladders, no geographic tiers by ZIP digit, no invented statutes. Flat service
    charges (returned-payment fee, late charge) are not padded computations. A factor already embedded in a recorded
    amount (a recorded rate, a recorded patient pay) is not load-bearing.
29. Every seeded cross-category row is a state the owning charter can produce, priced with that charter's own
    formulas as of the row's posting date; ledgers are complete (every billable row billed, every periodic entry
    reproducible from the records); every priced row's look-back window falls inside the seeded records (seed a holding's
    history from its start).
30. A write that another product's rules call owed at once (a solver could make it mid-conversation) must not move this
    difficulty's scored reads: key such reads on a record's standing as of the transaction's own effective date, or
    seed a history where nothing is owed at the opening.

## F. DSL limits — routes that passed before
31. The compute DSL filters by exact values only; time windows run from today; XSUM/XCOUNT run over event tables across
    all of a customer's holdings; CFIELD gives the first match. A rule pairing two records by date ("within N days of
    the other record") cannot be computed: scope the policy, via a self-naming overwrite, to a coarse exact record test
    (e.g. exactly one live holding of a kind), and use a two-date DAYS test inside the scope; out of scope the base
    clause is restated verbatim and computed exactly. State tie rules.
32. Keep scoped surfaces small; avoid policies whose tool must price every out-of-scope world.
