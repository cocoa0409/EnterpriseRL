# XF recipe — classes that renderers / KB audits found AFTER policy PASS in earlier runs (coordinator-owned, run-level)

Every point applies to every extended policy of every difficulty. For a policy auditor, any member of any class is RED, not an observation. For an instantiator, every point is a pre-green check, and its table goes into your worklog.

## A. Factor independence and assembly (the class that hit every product in recent runs)
A1. Each declared factor contributes on its own against a quantity the BASELINE defines. A factor tier may never read another factor's binding, tier or output, directly or transitively. Keep a factor-reads table (transitive) in the worklog.
A2. Assembly lives only in plain (non-factor) bindings and `result`. The rule states it ONCE, generically, and never names a factor's quantity ("the adjustments described in the schedules are applied to the standard amount in this order: …", not "the sibling discount and the subsidy copay are added …").
A3. A quantity or defining SENTENCE that only one factor uses belongs to that factor, never to the baseline or the computation document. Keep a defining-sentence table: sentence → which bindings/factors use it.
A4. No rule phrase defines a quantity "as another policy figures it". Shared record selections are a plain binding stated once in the rule.
A5. Wherever adjustments don't commute, the generic combination sentence still fixes the order ("replacements first, then caps, then additions, then rounding"). Never let two orders give two readings.
A6. Method shape (all-pairs table in the worklog). Count any aggregate of the same field as ONE input whatever its window or filter, and ignore constant multipliers. A pair of tiers FAILS if both are the same combination of the same windowed sums. It PASSES if one tier adds an input or an operation (floor, max/conditional pick, data-selected window, published parameter). A "nothing" tier fails where another tier is also 0 across its whole domain. A "method" whose multiplier the policy fixes is a constant, not a method. Tiers that coincide on their reachable domain fail; give each pair a distinguishing input.
A7. Lesser-of / greater-of shapes (caps, floors): state, for every factor, T1 (on the task world, substituting this factor's baseline alone moves the scored result) and T2 (some producible world exists where this factor moves the result with every other factor at baseline). Only one cap binds at a time. Never split one charge into two multiplying factors (rate × count): the other is 0 at baseline. One factor owns a whole line family.
A8. A factor already embedded in a recorded amount (a recorded tuition rate, a recorded fee) is not load-bearing. Two factors that cancel exactly on the task world are not allowed.
A9. Factor ladder tier TEXT says exactly what the rule and compute use. If compute reads "the meal status on the charge date", the ladder can't say "the child's meal status". Every arithmetic sentence has exactly one grouping: rewrite "the lesser of A and B less C" so that only one reading remains.
A10. A factor document must be able to name the result it modifies without naming any other factor.

## B. Rule vs compute at the edges
B1. Rule and compute agree at every edge input: None/absent record, 0 rows, 0.00 amounts, negative balances, zero-division, empty lists, same-day ties, a date-difference of 0 / negative lag, a month-end, a leap day, the first/last day of a window.
B2. Every first-match / CFIELD / LATEST read has a decoy table: a cancelled, voided, reversed, returned, withdrawn, prior-year or prior-semester record, a second child or second holding, plus an absent-record probe. The rule states the selection (status filter, date window, tie rule: e.g. "the most recent by posted date; on the same date, the later-recorded row") and compute does exactly that.
B3. Whole-month / whole-year / school-day / operating-day counts: state the convention (calendar vs billing month; school days per the district calendar; inclusive/exclusive ends) and compute does the same. MONTHS() and DAYS() month-end behaviour must match the sentence.
B4. Rounding. Compute uses RND(x + 0.000000001, 2) on non-negative values. Tool bodies use an exact Decimal ROUND_HALF_UP helper, written as a class static method, never round(float). Keep every scored, baseline and sensitivity figure more than 1e-6 away from a half cent. Residue within 1e-9 below a half cent is DSL-KNOWN. The rule's rounding sentence states WHERE rounding happens (per line / per child / per month / on the total) and matches compute and the order sentence.
B5. Every `compute_basis` quote is verbatim in its rule (check_extended does not check this). Run a scratch sweep and record it.
B6. The tool body enforces what the docstring states: format, rounding, "positive" amounts, "a payment on this enrollment" references, enumerations. Every rw="write" tool calls ctx.create/update/delete in its own body.
B7. A rule word for a field the records lack is a defect. Every rule term maps to a schema field or a binding.
B8. Never add a framing clause asserting a fact no record holds.

## C. Overwrites (scoped retirements of base clauses)
C1. Overwrites have no scope field. A `replaced_by` must restate the in-force content for every out-of-scope case and name its own scope ("for a … this policy …, and only for such a …; every other … remains under …" WITH the in-force content restated, rounding and dates included).
C2. Sibling overwrites retiring the same base clause: each tail excludes both its own case AND the sibling's case, by name.
C3. An extended rule may not contradict an in-force base clause without a declared overwrite. It may not defer to a base clause its own overwrite retires.
C4. Out-of-scope fallbacks: keep scoped surfaces small. Avoid policies whose tool must price every out-of-scope world; prefer an exact, coarse, stated record test with no purpose clause.

## D. Prerequisite edges
D1. Every edge is engaged and unmet at the opening. It must also be satisfiable by its resolver in EVERY engaged world: the resolver's rule settles every case inside the wait, including "nothing owed → settled, no line booked".
D2. Zero-amount waits: never add a floor that creates an amount where the rule owes nothing (no 0.01 floors). Carve exact-0.00 cases out of the wait by a record test stated verbatim in the rule AND in the waiting prerequisite sentence (a de minimis test such as "open balance ≥ X"). Otherwise use the action form with a valid fallback_reason. Check the frozen schema's field meanings ("always positive") before you propose a 0.00 row.
D3. The "owed at once" class. If another product's published corpus calls a write "owed at once" (e.g. a base trigger after a withdrawal or a status change), a solver can make it mid-conversation, and that write can move this difficulty's scored reads. Key every such read on the record's standing as of the transaction's own effective date, or seed a history where nothing is owed at the opening.
D4. Trigger rule: no tool of yours writes a row of an event whose base triggers land in another category, unless that consequence is part of the tree and declared.

## E. Seeds and cross-product rows
E1. Every cross-category seeded row (another claimed difficulty's category, for the same household) is priced and statused exactly as the OWNING base charter would produce it as of that row's posting date. That covers fees, waivers, meal-status prices, sibling positions, statuses and dates. Ledgers are complete: every billable month billed, every payment's allocation reproducible. Every priced row's look-back falls inside the seeded records, so seed holdings from their opening. Rows no gold step reads can't be seeded (the replay closure gate); that residue is accepted.
E2. Worked examples, docstrings and unlock schemas carry no concrete values that equal a scored value, and no task's codes, names or dates.
E3. No composed multi-value string args. Use one enumerated arg per field, with values listed as the format.

## F. Realism (the user's top priority)
F1. Factors are dimensions a real US public school district publishes. Examples: sliding-fee or subsidy schedules, sibling discounts, free/reduced meal status, NSLP/SBP federal prices, CEP, walk-zone distance, hazardous routes, McKinney-Vento/IEP, UIL rules, Texas Education Code deadlines, fee-waiver eligibility, refund schedules by notice date, late-pickup fee schedules, household fee caps. Figures are real federal/state figures, or worded as the district's own board-approved fee schedule with plausible numbers.
F2. Never invent a mechanism or entitlement a district would not have. No padding factors. A flat fee stays flat; don't stack percentage discounts on it.
F3. Prerequisite situations really occur at a district family-services desk, with plausible record histories (dates on school days, carryover periods, notice windows).
F4. Federal/state rules are applied as written (USDA SP 46-2016 unpaid meal charges: no meal denied for unpaid balance, no added fees; 7 CFR 245 carryover / adverse action; TEC citations as the base gives them).
