# XF_recipe.md — coordinator checklist of defect classes (env_0079)

Written by the coordinator BEFORE fan-out. It restates no skill rule; it lists defect classes that, in earlier runs,
passed the instantiate gates and the policy audit and were only caught at render or KB-audit time, each costing a
rework -> policy re-audit -> re-render -> KB re-audit loop. Instantiators apply every point to every extended policy;
policy auditors check every point on every policy, and any member found is RED, not an observation. Renderers
scan the source against it FIRST and stop before writing on any mismatch.

## A. Factor independence and assembly
A1. Every factor contributes on its own against a quantity the standard method (baseline) defines. No factor's tiers,
    bindings or value read another factor's binding or output, directly or transitively. Keep a mechanical table:
    factor -> every binding it reads (transitively) -> owner of each binding (baseline / plain / this factor).
A2. Assembly (how adjusted quantities combine into `result`) lives only in plain non-factor bindings and `result`, and
    the rule states it ONCE, generically, without naming any factor's quantity ("the adjusted amounts are then combined
    as follows: ..."). A record selection several factors share is one plain binding stated once in the rule.
A3. A quantity or defining sentence only one factor uses belongs to that factor's ladder, not to the baseline. Keep a
    defining-SENTENCE table: every rule sentence -> owner (baseline / plain binding / factor X / prerequisite).
A4. No rule phrase defines a quantity "as another policy figures it"; no factor acts only through another factor's tier
    ("grace only via the renewal rate"); no gate of the form "every window met" spanning several factors.
A5. Wherever adjustments do not commute, the generic combination sentence fixes the order ("replacements first, then
    caps, then additions, then rounding") so the text has exactly one reading.
A6. Factor acceptance tests: T1 — on the task world, substituting that factor's baseline alone moves `result`;
    T2 — some producible world exists where that factor moves `result` with every other factor at baseline.
    For min/max-of-bounds computations: derive one cap; one family factor owns a whole line family; never split one
    charge into two factors that multiply (count x price) — the other is 0 at baseline.
A7. Method shape: a `method` tier changes the formula's SHAPE, never just a multiplier, rate or window length.
    Test: aggregates of the same field count as one input whatever their window/filter; constant multipliers are
    ignored; a pair of tiers FAILS if it is the same combination of the same windowed sums; it PASSES if one tier adds
    an input or an operation (floor, max/conditional pick, data-selected window, tariff parameter). A "nothing" tier
    fails where another tier is also 0 across its whole domain. Keep an all-pairs tier table with a distinguishing input.
A8. Ladder tier TEXT says exactly what rule and compute use (which record, which date: "the job's tier on the charge
    date" vs "today's tier"), and inclusive/exclusive boundaries; no gaps, no overlaps, a defined fall-through tier.
A9. No arithmetic sentence with two groupings ("the lesser of A and B less C"): rewrite to one reading.
A10. No factor id may be a substring of any tool name (check_docs then fails with no rendering fix).

## B. Rule == compute, in every case
B1. Rule words equal compute in every world, including edges: absent record (None), zero, negative balance, empty
    list, zero-division, negative date lag, same-day dates. For EVERY read state the absent-record outcome in the rule.
B2. Decoy probe table: probe every CFIELD / first-match / LATEST read on a scratch copy with a decoy row (cancelled,
    voided, expired, prior-term, second record, other job of the same loss) and with the record absent; record results.
B3. Same-day ties: state the tie rule wherever LATEST/first-match could see two rows on one date.
B4. Whole-month/year counts: state the month-end convention and make it equal MONTHS()/DAYS() behaviour; state day-count
    inclusivity.
B5. Rounding: the rule's rounding sentence matches the RND placement in compute exactly. Where the rule says half up, use
    RND(x + 0.000000001, 2) on non-negative values; tool bodies use an exact Decimal half-up helper (class static method),
    never round(float) under a "half up" docstring; keep every scored, baseline and sensitivity figure more than 1e-6 away
    from a half cent. The residue (values within 1e-9 below a half cent) is DSL-KNOWN, not a defect.
B6. Every `compute_basis` quote is verbatim in its rule (check_extended does not check this — sweep it on a scratch copy).
B7. Compute DSL limits: filters match exact values only; aggregate windows run from today; CFIELD is first match;
    XSUM/XCOUNT run over EVENT tables across all the customer's holdings; there is no holding count and no tool argument
    in compute. Do not write rules the DSL cannot compute. Accepted routes: key the read on a record tied to the event by
    an exact value; scope the policy to a coarse exact record test (e.g. exactly one live job of that kind) stated with no
    purpose clause, out-of-scope cases restated verbatim under the base rule; a stated, realistic referral for the residue.
    Rejected routes: "multi-record case defined in words, compute doesn't price it"; pricing switched by an incidental count.

## C. Overwrites
C1. Every extended rule that contradicts an in-force base sentence declares an overwrite; an overwrite retires only
    clauses that genuinely conflict and never retires nothing. An undeclared departure from a base sentence is RED.
C2. `replaced_by` restates every still-in-force part of the retired clause (rounding, invoicing dates, definitions,
    exclusions) for cases outside this policy, and names its own scope: "for a <object> this policy <does>, and only
    for such a <object>; every other <object> remains under the base rule". Sibling overwrites of one clause each exclude
    both their own case and the sibling's case by name.
C3. A rule never defers to a base clause its own overwrite retires.

## D. Tools
D1. No concrete example values in docstrings or parameter descriptions (a published example once equalled a gold answer);
    describe the format only.
D2. Every effect a docstring claims, the body performs; every format, rounding, sign/positivity and reference constraint a
    docstring states, the body enforces.
D3. No composed multi-value string arguments ("a=X,b=Y"); one enumerated argument per field, values listed as format.
D4. Every write tool calls ctx.create/update/delete in its OWN body (helpers may compute values only).
D5. Forbidden tokens anywhere in task_tools.py source (validate_scenario rejects them): "import datetime", "from datetime",
    "import time", "time.time(", "date.today(", ".utcnow(", "import random", "random.", "import uuid", "uuid.",
    "import secrets". Do date maths with a pure-Python ordinal-day helper written as a class static method (a module-level
    helper function is treated as a tool).
D6. frozen_time is written "YYYY-MM-DD HH:MM:SS <TZ>" (never an ISO 'T').
D7. List every event your tools write with its base `triggers`; none may land in another category.
D8. A tool contract must be able to express every write the rule requires (no rule demanding a row shape no tool can write).

## E. Realism (restoration contractor)
E1. Factors are levers a real restoration contractor's program uses: price-list line items and units (Xactimate-style
    schedules worded as the company's own), IICRC S500/S520 water category/class and drying standards, equipment
    per-day rates and caps, monitoring cadence, carrier program fee schedules, deductible handling, mortgagee loss-draft
    and two-party check practice, AOB / direction-to-pay rules, supplement practice, storage vault periods. No loyalty,
    tenure, claim-count or invented "relief" ladders. Geographic or legal tiers are real (state as it really is) or
    worded as the company's own schedules; never invent statute figures. Re-check every tier against the policy's own scope.
E2. Seeded rows of OTHER categories are states their owning charter can produce (its tiers, statuses, trades, windows),
    priced with the owning charter's own formulas (base rates and rules; a deductible as the claims charter books it;
    a carrier payment as routed by its arrangement) — never round invented amounts.
E3. Complete ledgers: every billable row the charter would book is booked and invoiced as the charter says; every
    priced row's look-back falls inside seeded records (seed a job's history from its dispatch/opening/signing);
    periodic events (storage periods, equipment days, monitoring visits) are reproducible from the records.
E4. Flat service charges (late fee, card surcharge, returned-payment fee) are not padded computations. A factor already
    embedded in a recorded amount (a recorded contract sum, a recorded approved amount) is not load-bearing.
E5. Owed-write class: if another product's rules call some write "owed at once" and a solver could make it mid-call,
    it must not move this task's scored reads — key such reads on the record's standing as of the transaction's own
    effective date, or seed a world where nothing is owed at the opening.
E6. Zero-amount waits: a floor never creates an amount where the rule owes nothing. Carve an exact 0.00 case out of a
    wait with a record test (de minimis) stated verbatim in the rule AND the waiting prerequisite sentence, or use the
    action form with a valid fallback_reason. Read the db_schema field meanings (e.g. "positive") before designing.
E7. Every prerequisite edge is engaged and unmet at the opening AND satisfiable by its resolver in every engaged world;
    the resolver's rule settles every case inside the wait.
E8. Keep scoped surfaces small; avoid a policy whose tool must price every out-of-scope world.
E9. Account-level rules in the frozen base that bind every product (e.g. a service agreement's discount, response credit
    or priority-rate rule that applies to all jobs of the customer) must be complied with in every pricing stack and
    every seeded row; an extended overwrite cannot retire another charter's sentence.

## F. Customer's own write (owner=user)
F1. The customer's write is a real act of the customer over their own affairs, as the frozen charter assigns it:
    (a) a by:user lifecycle step the charter marks as the customer's (signing an authorization, release or contract
        handed over to the customer) together with its same-category consequence the charter groups with it;
    (b) the customer's own payment, completed by the customer through the secure payment channel (staff never take card
        numbers) — stated in the policy's own rule and visible in the persona;
    (c) the customer's own deposit or instruction the charter recognises.
    A label-only "the customer places the order" is not accepted.
