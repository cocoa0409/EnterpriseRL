# XF recipe — coordinator-binding checklist (env_0082)

Every point below is a defect class that renderers, KB audits or validate_scenario found AFTER policy PASS in earlier runs. Instantiators apply every point to every extended policy and tool; policy auditors check every point on every policy — **any member is RED, not an observation**. Contains no scenario content.

## A. Factor independence and assembly
A1. Every factor contributes on its own against a quantity the baseline (standard method) defines. No factor tier reads another factor's binding or output, directly or transitively; no factor acts only through another factor's tier. Keep a "what each factor reads" table in your worklog.
A2. Assembly lives only in plain (non-factor) bindings and `result`, stated ONCE, generically, without naming any factor's quantity ("the adjustments below are applied to the standard amount" — not "the transfer fee from the move schedule is added after the tier discount").
A3. Wherever adjustments do not commute, the generic combination sentence still fixes the order ("replacements first, then caps, then additions"); otherwise a second reading exists.
A4. A quantity (and its defining sentence) used only by one factor belongs to that factor; the baseline defines only what the standard method uses. Keep a defining-SENTENCE table (sentence → owner) in your worklog.
A5. Shared record selections are plain non-factor bindings stated once in the rule. No rule phrase defines a quantity "as another policy figures it"; no convention sentence serves several factors.
A6. Acceptance tests per factor: T1 — on the task world, substituting this factor's baseline alone moves the result. T2 — some producible world exists where this factor moves the result with every other factor at baseline. (Coordinator may accept T2-only failures when T1 holds and the tier acts on a baseline quantity.)
A7. Splitting one charge into two factors that multiply (qty × price) fails independence; a lesser-of spanning several lines is ONE family factor. Lesser-of / greater-of computations: only one bound binds at a time — state T1/T2 for each cap.
A8. baseline.params lists agree with the baseline paragraph in both directions.

## B. Method shape, ladders, wording
B1. A `method` factor changes the formula SHAPE (adds an input or an operation: floor, max/conditional pick, data-selected window, tariff parameter), never just a multiplier or a window length. Aggregates of the same field count as one input whatever the window or filter; constant multipliers are ignored. A pair of tiers FAILS if they are the same combination of the same windowed sums, or coincide on their reachable domain; a "nothing" tier fails where another tier is also 0 across its whole domain. Give a pairwise tier table with a distinguishing input per pair.
B2. Ladder tier TEXT names exactly what rule and compute use (which date, which record, which field: "the tier on the bill-credit posting date", not "the subscriber's tier").
B3. Tier tables are complete: no gaps, no overlaps, boundaries stated (≤ vs <), and an absent-record tier for every read.
B4. Every arithmetic sentence has exactly one grouping ("the lesser of A and B, less C" is ambiguous — rewrite).
B5. Every MX(0,…) floor, MN cap and RND the compute applies is stated in the rule words. Rule words == compute in EVERY case, including edges.

## C. Rule == compute at the edges (probe table required)
C1. For every CFIELD / first-match / aggregate read, probe on a scratch copy with: a decoy row (cancelled, voided, expired, prior-term, other utility account), a second matching record, and the absent record. Each needs a rule tier and the compute must agree. Also None, zero-division, empty list, date-difference and negative-lag edges.
C2. Same-day tie rule stated wherever LATEST/first-match could see two rows on one date.
C3. Month-end conventions: whole-month/year counts vs MONTHS() — state the convention the compute uses.
C4. Count entries vs periods exactly as the rule says; every exclusion the rule names (cancelled accounts, reversed credits) is in the compute.
C5. DSL limits (frozen): aggregate windows run from today in whole months; filters match exact values only; CFIELD gives the first match; XSUM/XCOUNT run over EVENT tables aggregated across all the customer's holdings; no holding count; no tool-arg-driven selection. Routes that passed: key the read on a record tied to the event by an exact value; scope the policy by a coarse exact record test via a self-naming overwrite (out of scope = the base rule restated verbatim); a stated, realistic, computed referral for the residue. Do NOT build out-of-scope fallback computes that must price every other world (they loop). Pairing across two records by date window cannot be computed — scope instead.
C6. A rule word for a field the records lack is a defect; framing clauses must not assert facts no record holds.

## D. Rounding
D1. Compute RND is float round(): for half-up use RND(x + 0.000000001, 2) on non-negative values; tool bodies use an exact Decimal-free pure-Python half-up helper (class static method). Keep every scored / baseline / sensitivity figure > 1e-6 away from a half cent. (Residue within 1e-9 below a half cent is DSL-KNOWN.)
D2. The rule's rounding sentence matches the RND placement in the compute (per line vs on the total; before vs after fees).

## E. Overwrites
E1. An overwrite has no scope field. `replaced_by` restates the in-force content for every out-of-scope case and names its own scope: "for a <record> this policy <acts on>, and only for such a <record>; every other <record> remains under the base rule, which reads: …". It must not drop conditions, rounding, dates, definitions of the retired clause.
E2. Retire only clauses that actually conflict; an extended rule contradicting an in-force base clause MUST declare an overwrite.
E3. Sibling overwrites retiring the same base clause: each tail excludes both its own case and the sibling's case by name.
E4. A rule never defers to a base clause its own overwrite retires; no stale names of removed rules or tiers anywhere (rule, rationale, closure text).
E5. Every `compute_basis` quote is verbatim in its rule (check_extended does not check this — run a scratch sweep).

## F. Prerequisites, waits, writes
F1. Every prerequisite edge is engaged and unmet at the opening AND satisfiable by its resolver in every engaged world. State-form waits on record-visible states.
F2. Floors never create an amount the rule does not owe. Exact 0.00 cases are carved out of a wait by a record test (de minimis), or use the action form with a valid fallback_reason. Check db_schema field meanings ("positive") before writing a 0.00 row.
F3. Owed-write check: if another product's published rules make some write owed at once (so a solver could make it mid-conversation), key your reads on the record's standing as of the transaction's own effective date, or seed a world where nothing is owed at the opening.
F4. Trigger rule: list every event your tools write with its base `triggers`; none may land in another category.
F5. Account-wide benefit / discount / credit-application rules in the blueprint bind every product: comply in every discount stack and every seeded row; one price whatever pays.

## G. Tools and loader
G1. frozen_time `YYYY-MM-DD HH:MM:SS <TZ>`. No "import datetime", "from datetime", "import time", "random.", "uuid.", "import secrets" anywhere in task_tools.py (substring match). Date maths via a pure-Python ordinal-day helper as a class static method (module-level helpers are treated as tools).
G2. Every rw="write" tool calls ctx.create/update/delete in its own body (helpers may compute, never write).
G3. Docstrings: no concrete example values (formats only); every claim the docstring makes is enforced by the body (rounding, "positive", reference checks, the 0.00 path); the body adds no condition the docstring and rule omit.
G4. No composite multi-value string args; one enumerated arg per field.
G5. No factor id may be a substring of any tool name.

## H. Seeds
H1. Every seeded row of ANOTHER category is a state its base charter (and, once published, its docs) can produce, priced with that charter's own formulas; read the owning charter.
H2. Seeded history rows of your OWN category follow your extended rules too (they carry no effective date) — price them with them.
H3. Ledgers complete: every billable row billed, every credit applied, every periodic reconciliation reproducible from the records; every priced row's look-back falls inside seeded records (seed holdings from their signing/opening).
H4. Persona never names the recipient, amount or tier the rules decide; persona names unique across the scenario (use your band).
H5. Examples in docstrings and docs never mirror task seeds or equal scored values.
