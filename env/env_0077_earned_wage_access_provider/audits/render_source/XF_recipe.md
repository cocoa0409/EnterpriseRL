# XF recipe — classes found by renderers / KB audits AFTER policy PASS in earlier runs (coordinator file, env_0077)
Applies to every extended policy of every difficulty. Instantiators apply every point before declaring green; policy auditors check every point on every policy — any member of any class is RED, not an observation. List ALL members of a class in one pass.

## A. Factor independence and assembly
A1. Every declared factor contributes on its own against a quantity the baseline defines. No factor tier reads another factor's binding or output, directly or transitively (keep a factor-reads table, transitive). No factor is gated through another factor ("grace only via the renewal rate").
A2. Assembly lives only in plain bindings / `result`, stated ONCE in the rule, generically, without naming factor quantities ("the adjustments below are applied in the order: replacements first, then caps, then additions" — never "the points from the four schedules are added").
A3. Wherever adjustments do not commute, that generic combination sentence still fixes the order; otherwise a second reading exists.
A4. A quantity (or defining sentence) used by only one factor belongs to that factor, not to the baseline / computation method. Keep a defining-sentence table: every defined term → the sentence that defines it → who uses it.
A5. Shared record selections are plain non-factor bindings stated once in the rule; results are never assembled inside a factor binding. No rule phrase defines a quantity "as another policy figures it".
A6. Method shape: a `method` factor must change the formula's shape. Count any aggregate of the same field as one input whatever its window/filter; ignore constant multipliers. A pair of tiers FAILS if it is the same combination of the same windowed sums; it PASSES if one tier adds an input or an operation (floor, max/conditional pick, data-selected window, tariff parameter). A "nothing" tier fails where another tier is also 0 across its whole domain. A "method" whose multiplier is fixed by the policy is a constant. Keep an all-pairs tier table with a distinguishing input for each pair.
A7. min/max (lesser-of / greater-of) shapes: for every factor state T1 (on the task world, substituting this factor's baseline alone moves the result) and T2 (some producible world exists where this factor moves the result with all other factors at baseline). A lesser-of spanning several lines is owned by ONE factor for the whole line family.
A8. No factor id may be a substring of any tool name (check_docs fails with no rendering fix).

## B. Rule vs compute (two-way correspondence)
B1. Rule words == compute in EVERY case, including edges: None / absent record, zero division, 0.00, negative lag, empty list, date differences, same-day ties (state the tie rule: which row LATEST/first-match keeps), month-end conventions for whole-month/year counts vs MONTHS(), inclusive/exclusive window ends.
B2. Every CFIELD / first-match read: probe it with a decoy (cancelled / reversed / returned / expired / prior-pay-period / second record) and with the absent record on a scratch copy; keep the probe table in your worklog. Every read has a stated absent-record tier.
B3. Tier ladders: no gaps, no overlaps; every tier re-checked against the policy's own scope, not only the task world.
B4. Rounding: the rule's rounding sentence matches the RND placement in the compute exactly. Half-up ruling for this run: compute uses RND(x + 0.000000001, 2) on non-negative values; tool bodies use an exact Decimal half-up helper (class static method, ROUND_HALF_UP); every scored / baseline / sensitivity figure is kept more than 1e-6 away from a half cent. The residue (values within 1e-9 below a half cent) is DSL-KNOWN and not a defect.
B5. Every compute_basis quote is verbatim in its rule (check_extended does not check this — sweep it with a scratch script).
B6. No rule word for a field the records lack; no framing clause asserting a fact no record holds.
B7. DSL limits (no holding count; XSUM/XCOUNT run over EVENT tables aggregated over all the customer's holdings; time windows run from today; filters match exact values; CFIELD gives the first match; no tool args in compute). Accepted routes: key the read on a record tied to the event by an exact value; scope the policy to a holding unique by its own charter or to "exactly one live X" (count = sum of exact-status counts) through a self-naming overwrite; a two-date DAYS test for windows; out of scope the base rule is restated verbatim and computed exactly. Rejected: a multi-record case defined in words that the compute doesn't price; pricing switched by an incidental COUNT; "first listed". Keep scoped surfaces small; avoid policies whose tool must price every out-of-scope world.

## C. Overwrites and base clauses
C1. An overwrite's replaced_by restates the still-in-force content for out-of-scope cases, then names its own scope ("for a transfer this policy reprices…, and only for such a transfer; every other … remains under the base rule, which reads: …"). Never "every other … remains under the base rule" while retiring the whole clause.
C2. No overwrite that retires nothing, or retires clauses that never conflicted; no extended rule that contradicts an in-force base clause without a declared overwrite; no undeclared departure from a base sentence.
C3. Sibling overwrites of the same base clause: each tail excludes both its own case and the sibling's case by name.
C4. replaced_by tails never drop rounding, dates, definitions or caps of the retired clause.

## D. Tools and task JSON
D1. Tool bodies enforce what their docstrings claim (format, rounding, "positive", "a deposit on this booking", effects). Docstrings carry NO concrete example values (describe the format only) — an example equal to a scored value is published in the KB.
D2. No composed multi-value string args ("a=X,b=Y"): one enumerated arg per field, values listed as format.
D3. Every rw="write" tool calls ctx.create/update/delete in its own body; date maths by a pure-Python ordinal-day helper as a class static method; task_tools.py contains none of: "import datetime", "from datetime", "import time", "time.time(", "date.today(", ".utcnow(", "import random", "random.", "import uuid", "uuid.", "import secrets".
D4. frozen_time formatted `YYYY-MM-DD HH:MM:SS <TZ>` (no ISO 'T').
D5. Persona full names are identifiers: never reused across tasks or difficulties (stay inside your surname band).
D6. After any change, sweep ALL proof / rationale / necessity / prerequisite_closure text and every stated equation for stale claims.

## E. Problem tree and writes
E1. Trigger rule: list every event your tools write with its base `triggers`; none may land in another category. Conditional triggers (access_transfer / disburse_payout → card:card_load when the destination is the worker's Paystride card): your tools may write only rows for which the trigger does not fire.
E2. "Owed at once" class: a write that another product's published rules call owed at once (and that a solver could make mid-conversation) must not move this difficulty's scored reads — key every such read on the record's standing as of the transaction's own effective date, or seed a history where nothing is owed at the opening.
E3. An edge must be engaged and unmet at the opening AND satisfiable by its resolver in every engaged world; the resolver's rule settles EVERY case inside the wait (e.g. "nothing owed ⇒ settled, no line booked").
E4. Zero amounts: never add a floor that creates an amount where the rule owes nothing; carve exact 0.00 cases out of a wait by a record test (amount fields are "always greater than zero" in this schema — check field meanings before any route).
E5. owner=user writes: audits/render_source/owner_ruling.md.

## F. Realism (the user's top priority)
F1. Factors are dimensions a real EWA / payroll-card / pay-disbursement program actually prices, limits or credits on (plan tier, transfer speed, destination type, pay frequency, employer fee model, program size band, network/ATM channel, in-network vs out-of-network, card status, Reg E timelines…), worded as Paystride's own published schedule where not an industry/regulatory figure. No invented padding, no loyalty/tenure ladders without a real basis.
F2. Regulatory / network figures must be real (Reg E 12 CFR 1005.18 and 1005.11 timelines and liability caps, NACHA return/reversal windows, Visa rules, state EWA statutes only where they truly exist with the real figure). If unsure, word it as Paystride's own schedule, never as a law.
F3. Flat service fees (instant-transfer fee, replacement-card fee, ATM fee) are not padded computations; a factor already embedded in a recorded amount is not load-bearing.
F4. Cross-category seeded rows must be states the owning charter (with the owning difficulty's published extended rules where they apply) produces, priced as of each row's posting date: fee amounts, statuses, destinations, timelines. Complete ledgers: every billable row invoiced/settled as the charter says, every periodic review/recovery reproducible from the records; every priced row's look-back falls inside seeded records (seed the holding's history from its opening).
F5. Worked examples (docs) and docstrings never reuse seeded figures / names / scored values.
