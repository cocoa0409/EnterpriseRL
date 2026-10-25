# Rework round 2 — claims (nonowner_policies_and_renewals)

Each round-1 audit item and how it was closed. No scored values appear here; the task files carry them.

## Charter findings
- **CG-1 (P3 cure vs fr base).** Task 1 now takes place in Virginia. The rejected filing is the insured's FR-44 Operator Certificate (carrier transfer, rejection reason policy_limits_insufficient). P3's rule states the fr cure in the fr charter's own terms: the backing term moves to that certificate's minimum backing package for the filing state (Virginia: Cardinal Point Non-Owner 100/200/50, Florida: Cardinal Point Non-Owner 100/300/50). The move P3 makes is therefore the fr cure. P4's prerequisite sentence now waits on "a package at or above the minimum backing package of every Operator certificate the named insured has requested, filed or had rejected", the fr wording. No other product's clause is overwritten.
  - Residual risk, disclosed in the worklog: the seeded request was transmitted on a term below its minimum backing package.
- **CG-2 (rate-table "methods").** Removed from P3 and P4: there is one rate table and no seasonal tables. The method in both P3 and P4 is now the filer basis. The class relativity (certificate form × points) applies:
  - by share when the requirement ends inside the rated period (months run), or
  - in full when it runs through the period, or
  - not at all.
  Each tier adds inputs or operations relative to the others.
- **CG-3 (start-date "methods", the whole class).**
  - P1's charging basis: a flat full-term charge (no day ratio), or a per-day share floored at one half (a fully earned minimum on twelve-month terms), or a per-day share.
  - P5's exposure basis: a flat whole return, or re-write days floored at 45 (or the return's days) when fewer than 60 days remain, or per-day.
  - No remaining method tier differs only by its start date. A pairwise table is in the worklog.
- **CG-4 (state-of-rejection load).** Deleted. P6's loads are now an installment service charge keyed on the billing plan's installment count and a filer handling load keyed on the certificate form backed. All other ladder keys were swept against XF17. Late-fee counts and notice counts are removed from every policy. The remaining keys are package, state, points, certificate form, lapse length, nonpayment-cancellation recency, returned-payment history, paperless delivery, billing plan, and day-based methods.
- **CG-5 / XF18 (stamp).** No rule reads `financial_responsibility_filing`; every certificate rule says so in words. In both worlds the stamp is stale ("none"), because the certificate was added after binding without an endorsement. Reading the stamp therefore gives the wrong tier.
- **CG-6 (P2 replaced_by).** The replaced_by now restates the full transaction-by-transaction formula, with no retention, for nonpayment, underwriting and conversion cancellations. It also restates the void-from-inception return.
- **CG-7 (P1 tier contradicting base nonowner_renewal).** The agent-office "bound at payment" tier is deleted. No P1 tier moves the in-force date.
- **CG-8 (certificate selection, the whole class).** Every certificate read in P1–P6 now:
  - filters to SR-22 or FR-44 Operator Certificate by variant;
  - states that FR-44 counts over SR-22;
  - fixes the read order for several filings of one form (requested, then filed, then rejected; the one recorded first within a status);
  - reads SR-26-sent certificates for Operator forms only.
  Probes with Owner, terminated, withdrawn and second-certificate decoys are recorded in the worklog.
- **CG-9 (zero-day row).** P6 tier 2 now requires the premium-written entry to record more than zero days and fewer than the term's days, in words and in compute. Probed.

## Task findings
- **T0-F1.** Closed by CG-3: P1's method is now a flat / floored / per-day charging basis.
- **T0-F2.** Closed by CG-5: the task 0 stamps are "none", so they disagree with the filed SR-22 Operator certificate that the rules read.
- **T1-F1.** Closed by CG-1.
- **T1-F2.** Closed by CG-2.
- **T1-F3.** Closed by CG-3.
- **T1-F4.** Closed by CG-4.
- **T1-F5.** Closed by CG-5.

## Observations
- **O-1:** P2's advance-notice credit was kept (it is a parameter on the short-rate retention, not a count).
- **O-2:** The mixed rating basis is gone. All rating policies rate on one table as of their own rating date.
- **O-3:** The lapse days charged under P1's flat tier rest on the stated certificate liability. P5 re-writes them only under the flat tier.
- **O-4:** The FR-44 tiers are reachable directly.
- **O-5:** The action-form fallback was kept, with its reason.
- **O-6:** Unchanged.
- **O-7:** The shared selections are now plain definitions stated once per rule.
- **O-8:** Multi-source factors now combine distinct records (certificate requirement against period dates; request reason against filing).
- **O-9:** P1's charging basis is multi-source.
- **O-10:** Unchanged (the base renewal rule governs re-tiered offers).
- **O-11:** The fr retransmission remains another difficulty's action.
- **O-12:** Unchanged.

## XF 17–19 sweep
- **XF17:** Ladder keys were checked policy by policy (see CG-4).
- **XF18:** See CG-5.
- **XF19:** Edge sentences were re-read against their conditions; none can be satisfied by a stale earlier record of another kind. The graph has no cycle or deadlock: P5 and P3 have no prerequisites, P6 waits on both, and P4 waits on P3 and P6.

All compute_basis quotes, replaced_by texts, prerequisite sentences and baseline sentences were swept verbatim against their own rules. Proof, rationale, closure and tracing texts were regenerated from the run that produced the new figures.
