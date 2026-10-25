# Rework round 3 — claims (nonowner_policies_and_renewals)

Each revision_2 item and recipe point, by id, with how it was closed. No scored values appear here; the task files carry them.

## Charter findings (revision_2)
- **R2-A**: closed. The paperless credit is struck as a whole factor from P1, P3 and P4. No add-on replaces it.
- **R2-B**: closed. Struck:
  - P2 advance-notice cut;
  - P6 installment service charge;
  - P6 filer handling load.
  P2 now uses term origin, a ledger dimension already in the records. P6 rates the moved package once, less the ledger's unearned premium, so each dimension is charged once.
- **R2-C**: closed. Every tier is reachable in its own policy's scope:
  - scoped lapse ladders in P1 and P5;
  - P5's universal nonpayment ladder is struck;
  - P1's dead floor tier is replaced by a reachable certified-days tier.
- **R2-D**: closed. Every period the rules use is defined with its included and excluded ends in words: P1, P3, P4, P5 and P6.
- **R2-E**: closed. The "or none" wording is removed from P1 and P5. An unrecorded required-through date is stated outright, and so is a missing certificate, so each tier has exactly one booking date.
- **R2-F**: closed. Task 1 is re-seeded as a producible Virginia DUI realignment, with the FR-44 filed on a term the fr charter and nonowner eligibility allow. The fee is billed per fee_billing_rule, and no SR-26 is sent because the term was reinstated inside the window. P3 realigns the package.
- **R2-G**: closed. Every method is a shape change. The pairwise table is in the worklog.
- **R2-H**: closed. Each policy has one generic combination sentence that names no factor quantity.
- **O2-1**: closed. P5's re-write days can no longer exceed the days remaining.
- **O2-2**: unchanged and unreachable. A nonpayment return is always booked mid-term.

## Task findings (revision_2)
- **T0-R2-1** (R2-A): closed.
- **T0-R2-2** (R2-B): closed. P2 keeps four factors.
- **T0-R2-3** (R2-C): closed.
- **T1-R2-1** (R2-F): closed.
- **T1-R2-2** (R2-E): closed.
- **T1-R2-3** (R2-G): closed. P3's method realises a shape tier on the task 1 world.
- **T1-R2-4** (R2-C): closed.
- **T1-R2-5** (R2-A): closed.
- **T1-R2-6** (R2-B): closed.

## XF recipe points 20–23
- **XF20**: P6 books nothing for a nil charge, and P4's action edge waits only on an owed charge. P5's nil case is unreachable.
- **XF21**: every look-back window falls inside the seeded records. The billing history is seeded from inception, and the ledger return and Statement of No Loss belong to the term itself.
- **XF22**: nothing was added in place of struck factors. Method tiers change shape, not dimension.
- **XF23**:
  - Every factor is keyed on a rate-filing dimension and applied to a premium-derived amount, stated as company relativities. No statute is cited.
  - Premium for no-exposure days is struck: the P5 fully earned minimum and the P1 half-term floor. Lapse days are charged only while a filed certificate ran.
  - Residual risk (returned-payment relativity) is disclosed in the worklog.

## Regression guard
- Earlier constraints are kept:
  - CG-1..CG-9 and XF1..XF19;
  - frozen_time format;
  - task_tools forbidden substrings;
  - write tools write in their own body;
  - no factor id inside a tool name;
  - no docstring example values.
- Task 0's round-3 values (re-priced from revision_2 once the paperless credit was struck) did not move when the P1 method tiers were changed afterwards; they differ from the revision_2 values.
