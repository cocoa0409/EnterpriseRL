# rework round 5 — claims (sr22_fr44_filings)

Each revision_4 item and how it was closed under XF point 27. No scored values are stated here.

- F4-1 (type and backing charged twice): one factor per computation now carries the certificate type. That factor reads the backing kind only as its evidence; no separate backing factor remains.
- F4-2 (out-of-scope backing fall-through): every "no backing term" tier is removed.
  - The state ladders end at Arizona or Ohio and the out-of-state ladders end at in-state, so every ladder has three in-scope tiers.
- F4-3 (lapse counting with one reachable tier): the lapse SR-26 method now keys on lapse length, as point 27(c) allows. Its three tiers fall inside the packages' reinstatement windows, and there is no cancellation-reason tier inside a scope that admits only nonpayment.
- F4-4 (refiling method fall-through out of scope): the refiling method's tiers are still certified, ended long before, and ended recently. All three lie inside the refiling scope; there is no "no SR-26" tier.
- F4-5 (ledger key in a method): no method reads the fee ledger.
  - The moved certificate's wait on a standing fee is a state gate on the replaced certificate's fees total.
  - The ledger is read only by the fee-charged-again cap guard.
- F4-6 (sibling timely overwrites): each SR-26 rule's timely overwrite names the other's case.
  - Day 0 is the lapse_start_date for a lapse SR-26 and the closed_date for a cancellation SR-26.
  - Every other ended-term SR-26 keeps the base window, and a late SR-26 is sent at once.
- F4-7 (counts): every drawn count is met without padding.
  - Factors are keyed only on publishable keys under point 27(a) and (c), each dimension once.
  - The fees start from flat company fees, so form is charged once.
  - The moved certificate's scope now covers any cancellation reason, which the charter genuinely produces.
  - Point 27(b) was weighed and left unused: a filing-state group would only replace the out-of-state grade.

Sweeps:
- Every compute_basis quote, baseline, overwrite, prerequisite sentence and tracing quote was re-matched verbatim.
- Every proof, rationale, closure and contract text was rewritten.
- Probes are in worklog.md (round 5).
