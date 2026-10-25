# XF recipe — source-side defect classes (env_0069)

Coordinator-maintained checklist. These are defect classes that renderers and KB auditors have repeatedly found AFTER a
policy-side PASS. Instantiators: apply every point to every extended policy before declaring gates green. Policy auditors:
check every point on every policy; any member of any class is RED (not an observation).

## A. Factor independence and assembly (the "XF" class)
1. Every factor contributes on its own against a quantity the baseline (standard method) defines. No factor's tier
   condition, value or method reads another factor's binding or output, directly or transitively (check mechanically:
   list what each factor binding reads, follow every binding it reads, and confirm no other factor is reached).
2. Record selections shared by several factors are a plain non-factor binding stated once in the rule; `result`
   assembles the amount. No result is assembled inside a factor binding.
3. The assembly sentence lives only in the rule's plain combination statement, stated ONCE generically, without naming
   the factor quantities ("the adjustments below are applied to the standard amount" — not "the points from the four
   schedules below are added"). No factor is gated through another factor.
4. Where adjustments do not commute, that generic combination sentence still fixes their order
   ("replacements first, then caps, then additions"), or a second reading appears.
5. A quantity only one factor uses belongs to that factor's own sentences; the baseline paragraph defines only what the
   standard method uses. No rule phrase defines a quantity "as another policy figures it" (never "if policy X would
   compute …"; use a record test or a state-form wait instead).
6. A `method` factor's tiers change the shape of the formula (how the quantity is computed), never just swap a multiplier
   or a window length; a `parameter` factor's tiers select a value. Give a pairwise tier table with a distinguishing input:
   no two tiers may coincide on their reachable domain (e.g. d×n vs d once when n=1 is all the domain holds).
7. No factor id may be a substring of any tool name (check_docs then fails on "hub repeats hidden factor name").

## B. Rule == compute in every case
8. Rule words == compute in every case, both directions: every quantity, window, filter, branch, ordering, cap and
   rounding the rule promises is in compute, and nothing compute does is absent from the rule.
9. Every `compute_basis` quote is verbatim in its own rule (check_extended does NOT check this — run a scratch sweep).
10. The rule's rounding sentence matches the RND placement in compute (what is rounded, when, to what).
11. Same-day ties: wherever LATEST/first-match could meet two rows on one date, the rule states the tie rule and compute
    implements it.
12. Whole-month / whole-year counts: the rule's month-end convention matches what MONTHS()/DAYS() computes.
13. Absent-record, None, zero-division and negative-lag branches: every read has its absent-record case stated in the
    rule with a tier, and compute implements it.
14. Every CFIELD / first-match / XLATEST read is probed with a decoy row (cancelled, voided, expired, prior-term or second
    record) on a scratch copy; the rule alone excludes the decoy.
15. DSL limits: filters match exact values; aggregate windows run from today. A pairing across two records' dates
    (e.g. "within N days of the other contract") cannot be computed — scope the policy via a self-naming overwrite to the
    single-record case and use a two-date DAYS test inside the scope; never describe a multi-record case in words that
    compute does not price.

## C. Overwrite hygiene
16. `replaced_by` restates the still-in-force content of the retired clause for out-of-scope cases and names its own scope
    ("for a <record> this policy handles …, and only for such a <record>; every other <record> remains under the base
    rule"). Overwrites have no scope field — an unscoped retirement makes the KB mark the base rule dead everywhere.
17. Sibling overwrites of the same base clause each exclude both their own case and the sibling's case by name.
18. No overwrite that retires nothing or retires a clause that never conflicted; no rule that defers to a base clause its
    own overwrite retires; no extended rule that contradicts an in-force base clause without an overwrite; no undeclared
    departure from any base sentence.

## D. Tools, seeds and text
19. Docstrings carry no concrete example values (describe the format only) — a docstring example equal to a gold value is
    published in the KB. A docstring claims no effect the body lacks.
20. Cross-product seeded rows (rows of another category's product) are states the owning charter can produce and are
    priced with the owning charter's own formulas (fees, shares, proration, rates as that product's rules compute them),
    with the servicing/supporting records that charter implies (signed requests, invoices, ledgers) present.
21. Factors, tiers and legal/geographic schedules are ones a real MSP / Microsoft CSP / hardware reseller / PS firm actually
    uses; legal tiers are real or worded as the company's own schedule. Re-check each tier against the policy's own scope.
22. After any change, sweep all proof text (design_rationale, prerequisite_closure, necessity, trace arithmetic) for
    claims made stale.

## E. Added 2026-10-18 (coordinator, from prior-run lessons; applies from the next round)
23. Method-shape test (structural): count any aggregate of the same field as ONE input whatever its window or filter,
    and ignore constant multipliers. Two method tiers FAIL if they are the same combination of the same windowed sums;
    they PASS only if one adds an input or an operation (floor, max/conditional pick, data-selected window, tariff
    parameter). A "nothing" tier fails where another tier is also 0 across its whole reachable domain. Give an all-pairs
    table per method factor.
24. Trigger rule: no task tool may write a row of an event type whose base `triggers` land in another category. List every
    event your tools write together with its base triggers; none may cross into another category.
25. Complete ledgers: every billable row of every seeded holding is invoiced, every invoice balance is backed by its
    invoice and payment rows, every count (seats, endpoints, protected items, hours) is reproducible from its ledger, and
    every periodic charge in the seeded window is present.
26. Plain (non-factor) bindings never read factor-owned bindings; no rule word refers to a field the records lack; each
    factor's sentences name the result quantity it modifies.
