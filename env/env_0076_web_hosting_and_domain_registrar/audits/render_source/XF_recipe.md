# XF recipe — classes that renderers and KB audits found AFTER policy PASS in earlier runs

Written by the coordinator before fan-out. Instantiators: apply every point to every policy in your
extended.yaml / task_tools.py before you declare gates green. Policy auditors: check every point on
every policy; any member of any class is RED (not an observation).

## A. Computation structure (factor independence / assembly)
1. Each factor contributes on its own against a quantity the baseline (standard method) defines. No factor
   tier reads another factor's binding or output, directly or transitively — do a mechanical check of what
   each factor's bindings read, and list it in the worklog.
2. Shared record selections are plain non-factor bindings, each stated ONCE in the rule. Assembly of the
   amount lives only in plain bindings / `result`, stated ONCE, generically, without naming factor quantities.
3. Quantities and defining sentences used by only one factor belong to that factor, not to the baseline.
   Keep a defining-SENTENCE table (sentence → binding → owner: baseline | factor id).
4. No rule phrase defines a quantity "as another policy figures it"; no rule copies another policy's compute.
5. Wherever adjustments do not commute, the one generic combination sentence fixes the order
   (e.g. "replacements first, then caps, then additions, then rounding"); otherwise a second reading exists.
6. `method` factors change the SHAPE of the formula, not a multiplier or window length. Shape test: any aggregate
   of the same field counts as one input whatever its window/filter; constant multipliers are ignored. Two tiers
   FAIL if they are the same combination of the same windowed sums; a tier PASSES if it adds an input or an
   operation (floor, max/conditional pick, data-selected window, tariff parameter). A "nothing" tier fails where
   another tier is also 0 across its whole domain. Keep an all-pairs tier table with a distinguishing input.
7. Lesser-of / min / max of bounds: every factor passes T1 (on the task world, substituting its baseline alone
   moves the result) and T2 (some producible world exists where it moves the result with all other factors at
   baseline). A lesser-of spanning several lines is ONE factor owning the whole line family.
8. Tier ladders: no gaps, no overlaps; boundary equality stated; re-check every tier against the policy's own scope.

## B. Rule text ↔ compute (rule words == compute in every case)
9. Edge inputs: None / absent record / zero / negative lag / empty list / divide-by-zero — every branch has a
   rule tier. Same-day ties stated (which row a LATEST/first-match read keeps). Month-end conventions of
   whole-month/year counts vs MONTHS()/DAYS() stated and matched.
10. For every CFIELD / first-match read: probe with a decoy row (cancelled, expired, prior-term, second record)
    and with the record absent, on a scratch copy; keep the probe table in the worklog.
11. Rounding sentence in the rule == RND placement in compute; tool bodies enforce the docstring's format and
    rounding (pure-Python half-up helper as a class static method; never round(float(x),2)); amounts declared
    "positive" or references declared "on this booking" are enforced in the body.
12. `compute_basis` quotes are verbatim in their rule (check_extended does not check this — sweep in scratch).
13. No framing clause asserting a fact no record holds; no rule word for a field the records lack; a factor's
    sentences name the result they modify.
14. DSL limits (exact-value filters, windows from today, CFIELD first match, XSUM/XCOUNT over event tables
    across all holdings): when a rule needs cross-record date pairing or per-holding counts, scope the policy by
    a coarse, exact, stated record test (self-naming overwrite: "for a <x> this policy handles…, and only for
    such a <x>; every other <x> remains under the base rule" + the in-force base content restated), or key the
    read on a record tied to the event by an exact value. Never "defined in words, not priced by compute".
    Prefer small scoped surfaces; avoid policies whose tool must price every out-of-scope world.

## C. Overwrites
15. An overwrite retires only clauses that genuinely conflict; it retires something real; `replaced_by` restates the
    still-in-force content (rounding, dates, definitions) for out-of-scope cases, then names its own scope.
16. Sibling overwrites retiring the same base clause: each tail excludes BOTH its own case and the sibling's by name.
17. No undeclared departure from any in-force base sentence.

## D. Realism
18. Factors a real registrar/host would use. Registry/ICANN/CA-Browser-Forum/vendor figures only where real;
    everything else worded as Harborline's own published schedule. No loyalty/tenure/claim-count ladders invented
    for padding; flat service fees are not padded computations; a factor already embedded in a recorded amount is
    not load-bearing.
19. Cross-category seeded rows must be states the owning charter can produce, priced with the owning charter's
    formulas (account-tier discounts, ICANN fee, proration, etc.) as of each row's posting date; complete ledgers
    (every billable row charged, every renewal reproducible); every priced row's look-back window falls inside
    seeded records (seed the holding's history from its opening).
20. Trigger rule: list every event your tools write with its base `triggers`; none may land in another category.
21. "Owed at once" class: if another product's rules would make some write owed mid-conversation (and a solver may
    make it), this difficulty's scored reads must not move — key them on the record's standing as of the
    transaction's own effective date, or seed a history where nothing is owed at the opening.
22. Zero-amount edges: never route a wait through a 0.00 row when the schema says the amount is positive;
    make the edge impossible with a realistic cap or carve it out by a record test.

## E. Tools / identifiers
23. No composite multi-value string args; one enumerated arg per field, values listed as the format.
24. No concrete example values in docstrings (describe the format only); no worked example equals a scored value.
25. No factor id may be a substring of any tool name.
26. Every write tool calls ctx.create/update/delete in its own body; helpers may only compute.
27. After any change, sweep all proof/rationale text, necessity text and stated equations for stale claims.

## F. Added during env_0076
28. Half-up rounding in compute: the DSL's arithmetic is float; an exact half-cent tie can round down. Every rounding
    the rule calls "half up" adds an epsilon of 1e-9 in dollar units (1e-7 when working in cents) before rounding /
    truncating, on non-negative values; tool bodies use an exact half-up helper; keep scored/baseline/sensitivity
    figures more than 1e-6 from a half cent. The residue (true values within the epsilon below a half cent) is a
    coordinator-declared DSL-KNOWN limit, not a RED.
29. Assembly totals (sums of credits/adjustments) are defined once generically ("the credits that apply are added
    together") — never a sentence listing each factor's quantity by name; the baseline must be computable without a
    sentence that names factor quantities.
