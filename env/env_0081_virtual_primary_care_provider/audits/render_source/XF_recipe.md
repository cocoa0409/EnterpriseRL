# XF recipe — coordinator checklist of defect classes (env_0081)

Every class below was found by renderers, KB audits or cross-product re-judges in earlier runs AFTER the policy audit had passed. Instantiators apply every point to every extended policy before declaring green. Policy auditors check every point on every policy: any member of any class is RED, not an observation. Renderers scan for them first and STOP on any member. KB auditors label a member found at their layer `src=`.

This file holds no scored value and names no task world.

## A. Computation structure (factors, baseline, assembly)

- **A1 Factor independence.** No factor reads another factor's output, tier or binding, and none is gated through another factor ("only when factor X applies"). No plain binding of the baseline reads a factor-owned binding. Keep a transitive factor-reads table in the worklog.
- **A2 Assembly sentences.** The computation document / baseline paragraph never names a factor's quantity. It states one generic combination sentence. Where the adjustments do not commute, that sentence must fix the order ("replacements first, then caps, then additions, then rounding"). Otherwise a second reading appears.
- **A3 Defining sentences.**
  - A quantity or definition used by only one factor lives in that factor, not in the baseline.
  - `baseline.params` lists exactly what the baseline paragraph uses, in both directions.
  - Keep a defining-sentence table (sentence → which policy/factor owns it → which compute line uses it).
- **A4 Result named.** Every factor document names the result it modifies. No sentence asserts "factor X and factor Y together …" (cross-factor framing).
- **A5 Family factor.** A lesser-of/greater-of that spans several lines or components is owned by ONE factor across the whole line family. Never split one charge into two factors that multiply (e.g. units × price): at baseline the other is 0, so independence fails.
- **A6 Method shape test.** Count any aggregate of the same field as one input, whatever its window or filter, and ignore constant multipliers.
  - A pair of tiers FAILS if it is the same combination of the same windowed sums. A window shifted by one month over the same field is the SAME input.
  - A pair PASSES if one tier adds an input or an operation: a floor, a max/conditional pick, a data-selected window, or a tariff parameter.
  - A "nothing" tier fails where another tier is also 0 across its whole domain.
  - Give an all-pairs tier table, with the distinguishing input per pair.
- **A7 T1/T2 for min/max shapes.** These apply to any computation shaped as the min/max of bounds, or to caps and floors.
  - T1: on the task world, substituting the factor's baseline alone moves the scored result.
  - T2: some producible world exists in which the factor moves the result with every other factor at baseline.
  - Only one cap can bind at a time; design so each cap passes T1/T2.
- **A8 Not already inside a recorded amount.** A factor whose effect is already embedded in a recorded amount is not load-bearing and is X4 of the realism bar. Examples: a recorded allowed amount, a recorded patient responsibility, a recorded price_paid, a recorded payroll contribution, a recorded pbm_patient_pay.
- **A9 Ladder wording.**
  - A factor ladder's tier text says exactly what rule and compute use: which record's tier or status, and as of which date (the charge date, the visit date, today).
  - Every arithmetic sentence has ONE grouping. "The lesser of A and B less C" is forbidden; write "the lesser of A and (B less C)" or restructure.
- **A10 Names.** No factor id may be a substring of any tool name (check_docs fails with no rendering fix).

## B. Rule == compute in every case

- **B1 Edges.** Probe every rule and its compute with these inputs:
  - None / absent record;
  - 0.00;
  - negatives;
  - zero-division;
  - an empty list;
  - same-day dates;
  - month-end and leap-day dates;
  - negative lags (an event before its reference date);
  - an amount exactly at a threshold.

  The words and the compute must give the same answer in every one of these cases.
- **B2 First-match / selection reads.** State the selection rule and the tie rule ("latest by date; same-day ties: the row listed first").
  - Probe every read against a decoy and against an absent record. Decoys include: a cancelled / refunded / voided / reversed row, a prior-period row, another visit or prescription of the same patient, a second coverage, a terminated enrollment, a superseded claim.
  - Keep the probe table in the worklog.
  - SUMs of credits, refunds or charges filter by event type and reason explicitly.
- **B3 Month conventions.** A whole-month or whole-year count vs MONTHS(): state the month-end convention. A whole-month count plus a part-month factor on the same date is ONE convention, not two factors.
- **B4 Rounding.**
  - Compute uses RND(x + 0.000000001, 2) on non-negative values.
  - The rounding sentence's placement matches the compute order ("round each line, then sum" vs "sum, then round").
  - Tool bodies use an exact Decimal ROUND_HALF_UP helper defined as a class static method, never round(float).
  - Every scored, baseline and sensitivity figure stays more than 1e-6 away from a half cent.
  - Values within 1e-9 below a half cent are DSL-KNOWN residue, not a defect.
- **B5 compute_basis quotes.** Every compute_basis quote is verbatim in its rule. check_extended does not check this, so run a scratch sweep.
- **B6 Record-backed words.** No rule word for a field the records lack. No framing clause asserts a fact that no record holds (e.g. "the patient was told", "the clinician intended").
- **B7 DSL limits — accepted routes.**
  - Accepted:
    - key the read on a record tied to the event by an exact value: the visit_id the charge names, the claim_id the remittance names, the rx_id of the fill;
    - a coarse exact scope test stated as a plain record test with no purpose clause;
    - single-record scope with a stated, realistic, computed referral for the rest;
    - a look-back window from today stated in days or whole months;
    - XSUM/XCOUNT over event tables (they aggregate across all of the patient's holdings).
  - Rejected:
    - "the multi-record case is defined in words but not priced";
    - a pricing method switched by an incidental COUNT;
    - "first listed" as a business rule;
    - any rule phrased "if policy X would compute …". Phrase dependencies as record tests or state-form waits.
- **B8 Scoped surfaces.** Keep scoped surfaces small. Out of scope, the base rule is restated verbatim and computed exactly. Avoid policies whose tool must price every out-of-scope world.
- **B9 Tool contract.** The tool's arguments and body can express every write the rule requires, and refuse what the rule forbids. A docstring never adds a condition the rule lacks, and the body enforces every docstring contract: format, rounding, positivity, "a charge on this visit", references existing.

## C. Overwrite hygiene

- **C1 Declare overwrites.** Every extended rule that contradicts an in-force base clause (a product-charter rule, a parameter meaning, an event policy) declares a scoped overwrite.
- **C2 replaced_by.** replaced_by restates the in-force content for out-of-scope cases verbatim, including rounding, dates and definitions, and names its own scope.
- **C3 Sibling overwrites.** Where two policies retire the same base clause, each tail excludes BOTH its own case and the sibling's case by name. Otherwise each pulls the other back under base.
- **C4 Retired clauses.** A rule never defers to a base clause that its own overwrite retires. No stale names of removed rules or factors anywhere: proofs, rationale, docstrings.

## D. Trees, edges, owners

- **D1 Edges bear weight.** Every prerequisite edge is engaged and unmet at the opening, AND satisfiable by its resolver in every engaged world. The resolver's rule settles EVERY case inside the wait (e.g. "no refundable line ⇒ settled with nothing owed, no line booked").
- **D2 Zero amounts.** Floors never create an amount where the rule owes nothing. A 0.00 edge is carved out of the wait by a record test (a de minimis test such as "open amount ≥ X", chosen so every tier prices ≥ 0.01), stated verbatim in the rule AND in the waiting prerequisite sentence. Or use the action form with a valid fallback_reason. Check the schema's field meanings: an amount field may be documented as positive.
- **D3 "Owed at once".** If another product's rules make some write owed at once that a solver could make mid-conversation, and it would move your scored reads, then do one of these:
  - key your reads on the record's standing as of the transaction's own effective date;
  - seed a history in which nothing is owed at the opening.
- **D4 Trigger rule.** List every event your task tools write, with its base `triggers`. None may land in another category unless that consequence is part of your tree and declared.
- **D5 Persona.**
  - The opening request is the ROOT problem only. It never asks for a prerequisite's write.
  - It never names a recipient, amount or code that the rules decide.
  - It states only identifiers from the band.
- **D6 owner=user.** Follows owner_ruling.md.

## E. Tools and validate_scenario

- **E1 What validate_scenario checks.**
  - frozen_time is formatted `YYYY-MM-DD HH:MM:SS <TZ>` (no ISO 'T').
  - task_tools.py contains none of these substrings: "import datetime", "from datetime", "import time", "time.time(", "date.today(", ".utcnow(", "import random", "random.", "import uuid", "uuid.", "import secrets".
  - Date maths uses a pure-Python ordinal-day helper defined as a class static method; a module-level function counts as a tool.
  - Every rw="write" tool calls ctx.create/update/delete in its own body.
- **E2 Docstrings.** No concrete example values in docstrings or parameter descriptions; describe the format only. A docstring example equal to a scored value is a published leak.
- **E3 Arguments.** No composed multi-value string args. Use one enumerated arg per field, with values listed as a format.

## F. Seed realism and cross-product consistency

- **F1 Other categories' rows.** Every seeded row of ANOTHER category is a state that category's base charter can produce. It is priced with that charter's own formulas as of the row's posting date:
  - membership tier prices and included-visit benefits;
  - the visit / lab payment-path order (employer plan first, then included membership benefit, then the patient's choice);
  - employer-plan pricing;
  - pack credit pricing;
  - payer benefit figures on the coverage;
  - the rx cash formulary price by level and days supply.

  Read the binding account-wide rules in each charter and comply in every discount stack and every seeded row.
- **F2 Complete history.**
  - Ledgers are complete: every completed visit charged per its path, every refund pointing at the exact line it settles, every claim with its remittance and statement where the charter produces them.
  - Every priced row's look-back falls inside seeded history (seed holdings from their opening).
  - Dates are real business days where the charter says so.
- **F3 Single reading.** No world admits two readings. Examples: a denial with two qualifying codes, two coverages both "primary", a visit that is both late-cancelled and no-show.
- **F4 Examples.** Worked examples in documents use figures, codes, panels, drugs and dates unlike any task world.
