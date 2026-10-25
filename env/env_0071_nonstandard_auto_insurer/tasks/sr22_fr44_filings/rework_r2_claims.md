# rework round 2 — claims (sr22_fr44_filings)

Each round-1 audit item and how it was closed. No scored values are stated here.

- F-G1 (owner SR-26 rule selected the latest removal or exclusion, compute gave removals priority; tie unstated):
  the removal SR-26 policy is gone. Its successor, the owner-term SR-26 rule, reads one record per question — the
  owner term's cancellation_reason, closed_date, garaging_state and package — keyed by the certificate's own
  auto_policy_id. No first-match or latest-of-two-kinds selection remains. Every same-day tie rule is stated: fee
  charges, reversals and new-business premiums.
- F-G2 (the comparison sentence kept closed_date without naming the removal case): the lapse rule's replaced
  comparison, not-before and timely sentences now say outright that an Owner Auto Policy term keeps its closed_date.
  The owner-term rule states its own timing explicitly (no earlier than the closed_date, within the stated days,
  day 0 counting) and does not defer to a retired base clause. There is no removal reading left.
- F-G3 (overwrite of the owner-term-only filer_rated sentence that never conflicted): removed. filer_rated is
  inherited and appears in the task 0 contract as not engaged.
- F-G4 (docstrings claimed billing-plan postings): every fee tool's docstring now says the charge is recorded on
  the filing's fee ledger and that nothing else is posted. No tool writes another category.
- F-G5 (the late-posted fee sentence named "a certificate" but meant the filing being priced): the sentence now
  names "the filing it is posted on, when that filing's Owner Auto Policy backing term has been cancelled". The
  edge condition matches it word for word.
- F-G6 (household same-type rule against the base certificate selection): the household policy is removed. The
  new state_change refiling keeps the replaced certificate's own form and type for the same filer, so no type
  selection departs from base.
- F-G7 (refiling continuity fall-through out of scope): the continuity ladder now has three in-scope tiers. Its
  zero tier, an end date more than the stated days before the refiling, is reachable. The same ladder shape is
  used in the moved certificate rule.
- F-G8 (removal counting fall-through out of scope): removed with the policy. The owner-term counting falls through
  on underwriting cancellations, or on nonpayment after the window, and both are in scope (probed).
- F-G9 (19 unreal factors): every struck ladder is gone. All factors now key on certificate form and type, filing
  state against residence or garaging state, the backing package (reinstatement window, bodily-injury limit), the
  plan type, the reason and state of the coverage end, the backing term's state, refiling after a lapse, and the
  certificate's own fee ledger and SR-26 dates. The notice and fee schedules are worded as Cardinal Point's own.
  None charges for a correction.
- F-G10 (bounds after striking): every computation carries its drawn 4–6 real factors, with at least two
  parameter factors and one method factor. Each task has a multi-source and a cross-difficulty factor (gate-checked).
- Proof-text findings (task 0 tracing payment count; task 1 factor card, trace and tracing copy figures): all
  tracing, factor_trace, closure, contract and rationale texts were rewritten from the round-2 gate recomputation
  and swept for stale ids, numbers and policy names.
- Observations: O-G1 — no gold value sits on a half-cent. O-G2 — no seeded row falls on a window anniversary. O-G4
  and O-G5 — the fee-basis credit is stated as a basis, not a return. The late fee no longer prorates a fully earned
  fee, and its scope state (charges reversed for company_error) is one the base reversal rule produces.
  O-G6 — the window tier is probed on a ten-day package. O-0-1/O-1-1 — the personas' company-side line is
  contentless.
