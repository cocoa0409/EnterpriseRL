# Rework round 7 — claims (nonowner_policies_and_renewals)

The revision_6 item, by id, with how it was closed. No scored values appear here; the task files carry them.

## Charter finding (revision_6)
- **R6-A** (P1 returned-payment change not exact): closed by striking the factor (XF22, removing beats adding).
  - An exact now ÷ offer needs the count of returns in the offer's own twelve-month window. The compute DSL cannot form it:
    - windows are anchored at the processing date;
    - filters are exact values only;
    - only the latest row is readable.
  - No exact record test exists in the records either.
  - P1's rule words and compute are now identical and exact. Its 4 factors are filer change, lapse, plan change and charging basis, each acting only on what the recorded offer premium does not embed (XF26 kept).
  - The draw (task 0 [5,4]) lets the author assign the counts. The 5 now goes to the return, which gains a point-23 dimension on a short-rate return: the plan multiplier of the retention.
  - Every combination sentence is unchanged and keeps its order.
  - Probes in the worklog cover the aged-out and two-post-offer worlds, both now equal to gold, plus plan decoys for the new multiplier.
  - Class pass over the other policies: no other member.

## Tasks
- **Task 0:** the world is unchanged. Scored values moved only because the fix requires it, and the proof text is rebuilt.
- **Task 1:** untouched.

## Regression guard
- All earlier closures are untouched: CG-1..CG-9, R2-A..R2-H, R3-A, R3-B, F1–F3, R5-A, XF1..XF26.
- Sweeps are clean and the gate block is all OK.
