# rework round 4 — claims (sr22_fr44_filings)

Each revision_3 item and how it was closed under the coordinator's point-24/25 ruling. No scored values are stated here.

- F3-R1 (remaining requirement days): struck from all five computations with no replacement. No rule or compute reads required_through_date for a figure.
- F3-R2 (prior-filing reason): struck from all five computations with no replacement. No figure reads filing_reason or fee_reason.
  - The same class was swept: the ledger fee-basis credit, the posting-delay method and the date-gap continuity and standing credits are gone too.
  - The fee ledger is read only for the fee-charged-again cap (fees reversed less fee standing) and for whether a fee stands on a replaced certificate before a move is priced as a transfer.
- F3-B (factor counts): met by re-treeing, not padding. The two SR-26 rules are now split by how coverage was restored:
  - the lapse SR-26: any backing term reinstated with a lapse;
  - the cancellation SR-26: any backing term cancelled and not reinstated. It has a new tool and a renamed policy id.

  Every factor is keyed on one publishable key, each dimension once:
  - how coverage ended or was restored (the counting and fee methods);
  - the company's state schedule, grouped FL/VA, TX/GA, AZ/OH;
  - certificate form, keyed honestly on the backing term's financial_responsibility_filing;
  - certificate type;
  - backing type;
  - the filing state against the backing term's state (out of group / same group / in-state).

  Channel is not used, because the base fixes electronic transmission. The fees take their method from the certificate's standing with the state.
- F3-D1 (late SR-26): both SR-26 rules restate the base timely clause. An SR-26 missed within its window is still owed, is sent at once, and its certificate end date counts from its actual transmission. Every wait on an SR-26 is satisfiable. The fee charged again keeps its minimum and its cap stays above zero within its scope, so the standing-fee wait is satisfiable too.
- O3-1 (docstring applicability): the fee-charged-again docstring now covers a filing whose charges were all reversed.

Class sweeps:
- Owner terms reinstated with a lapse now receive the lapse SR-26. The replaced_by restates the cases that still get none.
- Every compute_basis quote, baseline, overwrite clause, prerequisite sentence and tracing quote was re-matched verbatim.
- Every proof, rationale, closure and contract text was rewritten for the new factors and the renamed tool and policy.
- Probes with decoy and absent records, late SR-26s, ties and the cap and minimum edges are in worklog.md (round 4).
