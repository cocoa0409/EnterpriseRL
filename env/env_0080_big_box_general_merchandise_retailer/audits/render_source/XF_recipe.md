# XF recipe — env_0080 coordinator checklist (binding on every instantiator, reworker, policy auditor and renderer)

Each point below is a defect class that, in earlier pipelines, slipped past the gates and the first policy audit and was only found by renderers / KB audits. **Instantiators: apply every point to every extended policy before calling a task done. Policy auditors: check every point on every policy; any member is RED, not an observation. Renderers: scan the source against every point FIRST; on any mismatch report it quoted and STOP before writing any document.**

## A. Factor structure and independence
1. Every factor contributes on its own against a quantity the baseline defines. No factor binding, tier or effect reads another factor's binding or output, directly or transitively (do a mechanical read-set check per factor). No factor is gated through another factor ("only via the renewal rate", "only once the other tier applies").
2. Assembly lives only in plain bindings / `result`, and the rule states the combination ONCE, generically, without naming any factor's quantity (never "the points from the four schedules below are added", never "credits after the rate has been applied"). Where adjustments do not commute, the generic sentence still fixes the order ("replacements first, then caps, then additions").
3. A quantity (and its defining sentence) used by only one factor belongs to that factor, not to the baseline or the standard method. Keep a defining-SENTENCE table: sentence → which binding/factor uses it.
4. A record selection shared by several factors is a plain non-factor binding stated once in the rule; factors read that binding, never each other.
5. No rule phrase defines a quantity "as another policy figures it"; no policy copies another policy's compute.
6. Two acceptance tests for every factor. T1: on the task world, substituting this factor's baseline alone moves the result. T2: some producible world exists where this factor moves the result with all other factors at baseline. Lesser-of / greater-of caps: only one cap binds at a time — use ONE family factor owning the whole cap family, plus other real levers that pass T1/T2. Splitting one charge into two multiplying factors (seats × price) fails independence.
7. A `method` factor changes the formula SHAPE: a tier adds an input or an operation (floor, max/conditional pick, data-selected window, tariff parameter). Swapping a multiplier or a window length is a `parameter`, not a method. Aggregates of the same field count as one input whatever their window/filter; constant multipliers are ignored. Give a pairwise tier table with a distinguishing input for every pair; tiers that coincide on the reachable domain FAIL; a "nothing" tier fails where another tier is also 0 across its domain.
8. Every ladder ≥ 3 tiers, no gaps, no overlaps, explicit absent-record tier. Ladder TEXT says exactly what rule and compute use (which record's tier, as of which date — e.g. "the membership tier on the order's fulfilment date", not "the member's tier").
9. No factor id may be a substring of any tool name (check_docs fails "hub repeats hidden factor name").

## B. Rule == compute, in every case
10. Rule words == compute on every input, including edges: absent record (state its tier), None, zero division, negative lag, empty list, cancelled / voided / expired / second / prior-term decoy rows, same-day ties (state the tie rule; LATEST keeps the first row), month-end conventions of whole-month counts vs MONTHS(), date-difference boundaries (inclusive/exclusive stated). Keep a probe table: every CFIELD / first-match / aggregate read × {decoy row, absent record, second record} run on a scratch copy.
11. Rounding: the rule's rounding sentence matches the RND placement exactly. "Half up" is computed as RND(x + 0.000000001, 2) on non-negative values; tool bodies use an exact half-up helper (decimal.Decimal with ROUND_HALF_UP is allowed) written as a class static method — never bare round(float(x), 2). Keep every scored, baseline and sensitivity figure more than 1e-6 away from a half cent; the residue within 1e-9 below a half cent is DSL-KNOWN.
12. Every arithmetic sentence has exactly one reading ("the lesser of A and B less C" is two readings — rewrite).
13. Every `compute_basis` quote is verbatim in its rule (check_extended does NOT check this — sweep it with a scratch script).
14. No rule word for a field the records lack; no framing clause asserting a fact no record holds.
15. No worked example / docstring example equal to a scored value.

## C. Overwrites
16. Overwrites have no scope field. `replaced_by` names its own scope ("for a … this policy handles, and only for such a …") and restates the in-force content of the retired clause (rounding, dates, definitions, exclusions) for every out-of-scope case. A tail like "every other … remains under the base rule" must exclude a sibling policy's case by name if a sibling retires the same clause.
17. No overwrite that retires nothing or retires clauses that never conflicted; no extended rule contradicting an in-force base clause without an overwrite; no rule deferring to a base clause its own overwrite retires.
18. Account-wide benefit rules in OTHER charters (membership delivery benefit and its stacking; cardholder discount taken last and extended return days; one fee per event) bind every product's extended pricing and seeded rows; an extended overwrite cannot retire another charter's sentence. One price whatever pays.
19. For DSL limits (filters match exact values; windows run from today; CFIELD gives first match; no holding count across tables), use a coarse exact record-test scope declared through a self-naming overwrite; out of scope the base rule is restated verbatim and computed exactly; keep scoped surfaces small and avoid tools that must price every out-of-scope world. State routes as record tests, never "if policy X would compute …".

## D. Prerequisite edges
20. Every edge is engaged and unmet at the opening AND satisfiable by its resolver in every engaged world. The resolver's rule settles every case inside the wait. Floors never create an amount where the rule owes nothing; carve exact 0.00 cases out of a wait with a record test (de minimis threshold stated verbatim in the rule AND in the waiting prerequisite sentence) or use the action form with a valid fallback_reason. Check the frozen schema's field meanings (e.g. "positive") before writing a 0.00 row.
21. Owed-write class: a write that another product's published rules call owed at once can be made mid-conversation by a solver and move this difficulty's scored reads. Key such reads on the record's standing as of the transaction's own effective date, or seed a world where nothing is owed at the opening.

## E. Tools
22. frozen_time is `YYYY-MM-DD HH:MM:SS <TZ>` (no ISO "T"). task_tools.py contains none of the substrings: "import datetime", "from datetime", "import time", "time.time(", "date.today(", ".utcnow(", "import random", "random.", "import uuid", "uuid.", "import secrets". Date maths with a pure-Python ordinal-day helper written as a class static method (a module-level helper function is treated as a tool).
23. Every write tool calls ctx.create/update/delete in its own body (helpers may compute values only).
24. Tool bodies enforce what their docstrings declare (format, rounding, positivity, "a row of this order", reference checks); docstrings claim no effect the body lacks; no concrete example values in docstrings — describe the format only.
25. No composed multi-value string args; one enumerated arg per field.
26. Trigger rule: list every event your tools write with its base `triggers`; none may land in another category.

## F. Seeds and realism
27. Every seeded row of another category is a state its owning charter produces: price it with the owning charter's formulas (member delivery benefit, cardholder discount last, fee caps at minimum due, plan price bands, return windows), with complete ledgers (every charge has its statement, every return its refund rows) and with every priced row's look-back inside the seeded history (seed from the holding's opening).
28. Realism bar: factors a real big-box retailer, its card-issuing bank or its plan administrator actually uses; real statute/network figures only (Reg Z / FCBA, card-network rules, state plan-cancellation practice worded as the company's own schedule); geographic or legal tiers real or worded as the company's own schedules; flat service fees are not padded into computations; a factor already embedded in a recorded amount is not load-bearing; no invented entitlements.
29. Unread cross-product rows cannot be seeded (the replay closure rejects rows no gold step reads) — accepted residue, not a defect.
30. Persona: identifiers from the assigned band only; never discloses a fractional answer; full names unique across difficulties.
