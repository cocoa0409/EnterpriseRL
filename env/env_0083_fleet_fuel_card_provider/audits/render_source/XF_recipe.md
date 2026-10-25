# XF recipe — defect classes found AFTER policy PASS in earlier runs (coordinator file, env_0083)

Read in full. Instantiators apply every point to every extended policy and tool before declaring gates green.
Policy auditors check every point on every policy: **any member of any class below is RED, not an observation.**
Renderers scan the source for every class FIRST; on any mismatch they report it quoted and STOP before writing any doc.

## A. Factor independence and assembly (the XF class)
A1. Every factor contributes on its own against a quantity the baseline (the standard method) defines. No factor tier reads another factor's binding or output; no factor is gated through another factor (e.g. a grace period that acts only via a renewal rate).
A2. Assembly (how the factor outputs combine into `result`) lives only in plain bindings / `result`, and the rule states it ONCE, generically, without naming any factor's quantity. Wherever the adjustments do not commute, that generic sentence still fixes the order ("replacements first, then caps, then additions"), so only one reading exists.
A3. A quantity or defining sentence used by only one factor belongs to that factor, not to the standard method. Keep a defining-SENTENCE table in the worklog: each defining sentence of the rule → which plain bindings / factors use it.
A4. A record selection shared by several factors is a plain non-factor binding stated once in the rule; no factor binding is read by a plain binding.
A5. No rule phrase defines a quantity "as another policy figures it" or "as policy X would compute"; cross-policy dependencies are record tests or state-form waits.
A6. Two acceptance tests for every factor. T1: on the task world, substituting this factor's baseline alone moves `result`. T2: some producible world exists where this factor moves `result` with every other factor at baseline. A factor acting only through other factors' outputs fails T2. Route: the standard method defines the quantity at a stated default; other factors narrow or widen it from records; the pricing factor acts on that baseline-defined quantity.
A7. Method shape. A `method` factor changes the formula's SHAPE, never just swaps a multiplier or a window length. Shape test: count any aggregate of the same field as ONE input whatever its window or filter, ignore constant multipliers; a pair of tiers FAILS if it is the same combination of the same windowed sums; it PASSES if one tier adds an input or an operation (floor, max / conditional pick, data-selected window, tariff parameter). A "nothing" tier fails where another tier is also 0 across its whole domain. Keep a pairwise method-tier table with a distinguishing input for every pair.
A8. A lesser-of / greater-of spanning several lines or caps: ONE family factor owns the whole family on every path; never split it over two factors.
A9. Splitting one charge into two factors that multiply (count × price) fails independence (the other is 0 at baseline). Keep one family factor and add a real lever passing T1/T2.
A10. Ladder tier TEXT says exactly what the rule and compute use (which date, which record, which status — "the tier on the transaction date", not "the account's tier" if compute reads today's). Arithmetic sentences have ONE grouping: never "the lesser of A and B less C"; write "A less C, or B less C, whichever is lower" or equivalent.
A11. No factor-naming sentences in the standard method; no factor's ladder names or describes another factor.

## B. Rule words == compute, in every case
B1. Every rule sentence is computed, and every compute branch is stated in rule words — including MX(0,…) floors, MN caps and RND placement. The rounding sentence states exactly where RND sits.
B2. Edge inputs each have a stated rule tier and a probe: absent record, zero count, empty list, negative or zero balance, divide by zero, None dates, negative date differences.
B3. Same-day ties: state the tie rule (LATEST keeps the first row on a tie).
B4. Month-end / whole-month and whole-year counts vs MONTHS(): state the convention and make compute match it.
B5. For EVERY CFIELD / first-match / LATEST read: probe with a decoy row (cancelled, expired, reversed, second card, second program, other account) on a scratch copy; list each in the probe table with the result.
B6. A rule word for a field the records lack is RED (no "the fleet's usual site" unless a field holds it).
B7. Every `compute_basis` quote is verbatim in its rule (check_extended does NOT check this — sweep with a scratch script).
B8. `baseline.params` agrees with the baseline paragraph in both directions.
B9. Framing clauses assert no fact that no record holds.
B10. SUM / COUNT filters (status, reason, product code, network) match the rule's words exactly.
B11. Ladders cover their domain exactly once: no gaps, no overlaps, every boundary's inclusivity stated.
B12. Scope wording vs all-holdings sums: if the rule says "this card program", compute must not sum across programs (and vice versa).

## C. Overwrites
C1. Overwrites have no scope field. A narrower `replaced_by` must restate the in-force content for out-of-scope cases and then name its own scope ("for a … that this policy prices, and only for such a …; every other … remains under the base rule, which …").
C2. Never retire nothing, and never retire a clause that does not conflict.
C3. `replaced_by` never drops still-in-force parts of the retired clause (rounding, dates, definitions, posting days, conditions).
C4. Sibling policies retiring the same clause: each tail excludes BOTH its own case and the sibling's case by name, so neither pulls the other back under base.
C5. Any extended rule contradicting an in-force base sentence declares the overwrite (an undeclared departure is RED).
C6. An extended overwrite cannot retire another charter's sentence; account-wide rules (tier benefits, rebate basis, no-stacking, late-fee basis) bind every product's pricing.

## D. Seeds
D1. Every seeded row of ANOTHER category is a state its owning charter can produce, priced with that charter's own formulas, statuses and timings.
D2. Seeded history rows of your OWN category follow your extended rules too (they carry no effective date): price them with your extended rules, not a base clause your overwrite retires.
D3. Complete ledgers: every posted transaction billed on its cycle's statement, every statement paid or open per the terms, every fee assessed where the rules assess it, every periodic rebate reproducible from the records. Every priced row's look-back falls inside seeded history (seed accounts and programs from their opening).
D4. Owed-write check: if another product's rules make some write owed at once (a solver could make it mid-conversation), key your reads on the record's standing as of the transaction's own effective date, or seed a world where nothing is owed at the opening.
D5. Rows no gold step reads cannot be seeded (replay closure).

## E. Tools
E1. No concrete example values in docstrings (formats only). A docstring describes every path the body takes (including a 0.00 path) and claims no effect the body lacks.
E2. Bodies enforce the docstring's format, sign and rounding (exact half-up helper, positivity, reference format) — never business eligibility.
E3. No composite multi-value string args; one enumerated arg per field.
E4. No factor id may be a substring of any tool name.
E5. Every write tool calls ctx.create / update / delete in its OWN body. No datetime / time / random / uuid / secrets imports; date maths through a pure-Python ordinal-day helper written as a class static method (a module-level helper is treated as a tool).
E6. Trigger rule: list every event your tools write with its base `triggers`; none may land in another category.
E7. The tool contract can express every write the rule requires (and nothing it forbids).

## F. Rounding
F1. Half-up via RND(x + 0.000000001, 2) on non-negative values in compute; tool bodies use an exact Decimal half-up helper (class static method). Keep every scored / baseline / sensitivity figure > 1e-6 away from a half cent. The residue (values within 1e-9 below a half cent) is DSL-KNOWN — not a RED.

## G. Edges and waits
G1. Every prerequisite edge is engaged and unmet at the opening AND satisfiable by its resolver in every engaged world.
G2. Floors never create an amount where the rule owes nothing. Exact 0.00 cases are carved out of a wait by a record test (a de minimis threshold stated verbatim in the rule AND in the waiting prerequisite sentence), or the action form is used with a valid fallback_reason.
G3. In an action-form wait, the resolver's rule settles EVERY case inside the wait (including "nothing owed, nothing booked").
G4. No rule states a cross-problem order that grounds no declared edge.

## H. DSL-limit routes (coordinator rulings from earlier runs)
Accepted: scope via a self-naming overwrite `replaced_by` to a single-holding world stated as a coarse exact record test with no purpose clause (out of scope restated verbatim under base and computed); key a read on a record tied to the event by an exact value; a month window plus a two-date DAYS test for the boundary band; a count bounded to a look-back from today plus a stated, realistic referral.
Rejected: a multi-record case defined in words that compute does not price; a pricing method switched by an incidental COUNT; "first listed".
