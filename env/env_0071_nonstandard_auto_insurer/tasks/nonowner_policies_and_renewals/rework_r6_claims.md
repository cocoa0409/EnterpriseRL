# Rework round 6 — claims (nonowner_policies_and_renewals)

Each revision_5 item, by id, with how it was closed. No scored values appear here; the task files carry them.

## Charter finding (revision_5)
- **R5-A** (XF26, P1 factors embedded in the recorded renewal premium): closed.
  - P1's standard figure is now the renewal term's recorded full-term premium (the renewal offer).
  - P1 keeps 5 factors, all point-23 keys, and each acts only on what that premium does not embed:
    - filer change: a requirement added, or a certificate released, after the offer's issue date;
    - the renewal term's own lapse;
    - returned-payment change: a payment returned after the issue date;
    - plan change since the offer;
    - the late-renewal charging basis (the transaction's own method).
  - The rate table, state and points class are removed from P1.
  - The combination sentence is unchanged and keeps its order.
  - Class pass over P2–P6: no other member.

## Task findings (revision_5)
- **T0 (R5-A):** closed. Task 0's world has the events the factors need:
  - the SR-22 transfer after the offer date;
  - a second returned payment after the offer date, with the certified-funds restriction it triggers;
  - the recorded offer premium re-derived on the offer-date records.
  - Every P1 factor bears weight. Reading the recorded premium with lapse and plan alone no longer gives gold.
- **Task 1:** PASS in revision_5; untouched.

## Observations
- O5-1, O5-2: carried.
- The SR-22 fee timing on the backing plan is disclosed in the worklog.

## Regression guard
- All earlier closures are untouched: CG-1..CG-9, R2-A..R2-H, R3-A, R3-B, F1–F3, XF1..XF26.
- Sweeps are clean, probes are recorded in the worklog, and the gate block is all OK.
