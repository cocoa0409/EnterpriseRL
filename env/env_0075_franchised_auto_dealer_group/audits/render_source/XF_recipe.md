# XF recipe — coordinator checklist (env_0075)

Every point below is a class that renderers and KB auditors caught AFTER a policy PASS in earlier runs. Instantiators design against every point; policy auditors check every point on every policy (any member is RED, not an observation); renderers scan the source against it first and STOP on any member.

## A. Factor structure
1. Factor independence: each factor contributes on its own against a quantity the baseline (computation document) defines. No factor tier reads another factor's binding, tier or output — check transitively, mechanically. No factor is gated through another factor ("only acts through X's tier").
2. Shared record selections used by several factors are plain non-factor bindings stated ONCE in the rule; `result` assembles the amount.
3. Assembly lives only in plain bindings / `result`, stated ONCE, generically, without naming factor quantities. Where adjustments do not commute, the generic combination sentence still fixes the order (e.g. "replacements first, then caps, then additions, then rounding").
4. A quantity only one factor uses belongs to that factor's text, not to the baseline. No rule phrase defines a quantity "as another policy figures it".
5. Method factors change the formula SHAPE (an added input or operation: floor, max/min pick, data-selected window, a different base), never swap a multiplier or window length. Count any aggregate of the same field as one input whatever its window/filter and ignore constant multipliers: two tiers that are the same combination of the same sums FAIL. A "nothing" tier fails where another tier is also 0 over its whole domain. Give an all-pairs tier table with a distinguishing input per pair. Parameter factors select values, not methods.
6. Two acceptance tests per factor: T1 on the task world, substituting that factor's baseline alone moves the result; T2 some producible world exists where that factor alone moves the result with every other factor at baseline. Min/max-of-caps shapes need both (only one cap binds at a time).
7. No factor id may be a substring of any tool name.

## B. Rule == compute, at every edge
8. Two-way: every promise in the rule (quantities, windows, filters, branches, order, caps, rounding) is in compute and vice versa; the rounding sentence matches the RND placement.
9. Probe table (scratch copy of the DB) for EVERY CFIELD / first-match read and every XSUM / XCOUNT: decoy rows (cancelled, voided, reversed, expired, prior-term, second holding/second record), absent record, None, zero division, negative lag, same-day tie (state the tie rule; LATEST keeps the first row), month-end conventions of whole-month/year counts vs MONTHS(), empty lists, credits exceeding balances. Every branch has a stated rule tier.
10. `check_extended` does not verify `compute_basis` quotes: sweep that every quote is verbatim in its rule.
11. No framing clause asserts a fact no record holds; no rule word names a field the records lack.
12. DSL limits: XSUM/XCOUNT run over event tables across ALL the customer's holdings; CFIELD gives the first match; filters are exact-value; windows run from today. Routes that pass: key the read on a record tied to the event by an exact value; a coarse exact scope test stated as a plain record test (no purpose clause) via a self-naming scoped overwrite; a two-date DAYS test. Out of scope: base text restated verbatim and computed exactly — keep scoped surfaces small; avoid policies whose tool must price every out-of-scope world.

## C. Overwrite hygiene
13. An overwrite retires only clauses that genuinely conflict; the `replaced_by` sentence names its own scope ("for a … this policy …, and only for such a …") and restates the still-in-force content (rounding, dates, definitions, payee) for out-of-scope cases. Sibling overwrites of the same clause each exclude the other's case by name.
14. No extended rule contradicts an in-force base clause without an overwrite; no rule defers to a base clause its own overwrite retires; no undeclared departure from a base sentence.

## D. Prerequisites & uniqueness
15. Prerequisite sentences are record tests / state-form waits; never "if policy X would compute …".
16. "Owed at once" writes: if another product's published rules make some write owed at once (e.g. a cancellation refund, a recall remedy, a reinstatement), a solver may make it mid-conversation and move this difficulty's reads. Key such reads on the record's standing as of the transaction's own effective date, or seed a history where nothing is owed at the opening.

## E. Tools & seed
17. Docstrings / param descriptions: format only, NO concrete example values; every claimed effect exists in the body. One enumerated arg per field — no composite multi-value string args.
18. Trigger rule: list every event your tools write with its base `triggers`; none may land in another category; within-category triggered consequences are booked as the base says.
19. db_schema field meanings bind: purchase / loaner / service money rows are > 0.00 (a waived charge is never posted); only refund-calculation and denied-claim rows may be 0.00.
20. Cross-category seeded rows must be states the owning charter can produce, priced with the owning charter's formulas (doc fee, deposits, labor/parts discounts, shop fees, plan prices, VSC/GAP prices and refunds), with complete ledgers (every billable row invoiced/paid as that charter does it) and every priced row's look-back inside seeded records (seed each holding from its sale/opening). Unread cross-product rows cannot be seeded (replay closure) — accepted residue.
21. Persona full names are identifiers (use your surname band).

## F. Realism bar
22. Every factor is one a real franchised dealer, F&I product administrator, OEM warranty/recall program or lender would use; amounts rooted in the contract/price/charter; statutory figures real (Magnuson-Moss, NHTSA recall remedy, state doc-fee caps, FTC Used Car Rule) or worded as the company's own schedule/contract term.
23. Flat service charges (returned-payment fee, late fee, doc fee) are not padded computations; fees/day counts keyed only on publishable keys are fine at 4–6 factors.
24. A factor already embedded in a recorded amount (recorded price, recorded refund due, stamped field) is not load-bearing.
25. Every prerequisite situation of a task's world is a state real dealership operations produce; no real-world wait (diagnosis, delivery, payment clearing, lender funding, OEM review) as a prerequisite.

## G. Proof text
26. After any change, sweep design_rationale, prerequisite_closure, necessity text and trace arithmetic for stale claims (removed tiers, old figures).
