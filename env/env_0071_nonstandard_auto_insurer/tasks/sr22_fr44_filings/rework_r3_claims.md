# rework round 3 — claims (sr22_fr44_filings)

Each revision_2 item and how it was closed. No scored values are stated here.

- F2-R1 (bodily-injury-limit filing-fee credit): struck from every fee computation (refiling, fee charged again,
  moved certificate). No limit is read by any factor, and none was replaced by a new add-on.
- F2-R2 (billing-plan filing charge): struck from every fee computation. No factor reads a billing plan. The plans
  stay in the world only as the records the fees are billed on.
- F2-R3 (one dimension charged twice): the home-state and garaging-state charges and notices that read the same field
  as the out-of-state charge are gone. Each fee and run-off computation charges filing state against the backing
  state once. The package reinstatement-window notice is gone, so the window is counted once, inside the counting
  method. The computations were re-cut onto their real dimensions (point 23):
  - how the coverage ended or was restored;
  - certificate type and backing;
  - filing state against residence or garaging state;
  - the requirement period left;
  - transfer against refiling after a lapse, read from the fee ledger.
- F2-P1 (rule against compute, zero edge): the fee charged again states that no basis is due past the late-posting
  delay, and the compute matches. The result is floored at a stated realistic minimum re-charge, so the zero edge
  (point 20) yields the minimum charge, never a negative or an unstated zero.
- F2-D1 (deadlock on a fee that can be zero, withheld or impossible): the moved-certificate wait on a standing fee
  applies only by record test:
  - the replaced certificate rests on an Owner Auto Policy term;
  - it was requested for a reason that is charged a filing fee;
  - no fee on it was reversed as withdrawn before transmission or as a duplicate request.
  Corrections and other uncharged reasons are carved out. The depended-on fee charged again never falls below its
  minimum, so the wait can always be met.
- F2-O1 (overwrite hygiene 5a): the lapse rule's suppression replaced_by restates the in-force content for:
  - an Owner Auto Policy term reinstated with or without a lapse before the SR-26;
  - a Named Non-Owner term reinstated without a lapse;
  - a rescinded cancellation.
  These still receive no SR-26 and their certificates continue.

Class sweeps:
- Every prior-filing factor in the five policies reads the fee ledger by fee_reason, counting reversed charges too.
- Every tie rule and every absent-record tier is stated.
- Every proof, rationale, closure, tracing and compute_basis text was swept for the struck factors. The prerequisite
  sentences carry no code token.
- Probes with decoys and absent records were run for every read (worklog.md, round 3).
