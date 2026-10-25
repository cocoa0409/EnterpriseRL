# Rework round 3: claims per revision_2 audit item

No scored values are given here. NC/RE/IC = nonpayment return / lapse re-write / insured-request return (task 0);
AD/EX/AB = re-listing / exclusion return / exclusion lift (task 1).

## Rating basis (XF23/XF24, closes R2-04/R2-05/R2-06 as a class)

- Every amount now comes from a company-filed rating plan, and the rules call those numbers company-filed relativities.
- **Term rating (NC, RE, IC):**
  - Plain relativities read off the term: term base rate, vehicle, package, state and points.
  - Factor relativities read from records:
    - certificate form and certificate type, from the certificate the term was written to back;
    - payment plan, from the billing plan;
    - nonpayment history, from the notices of cancellation for nonpayment (applied only to a term reinstated with a lapse).
- **Driver rating (AD, EX, AB):**
  - Plain relativities: driver base rate, package and state.
  - Factor relativities: age class (date span), relationship, violation points (from the entry), and accidents and platform use (from claim reports).
- Seeds were re-priced to match both plans:
  - task 1: term premium, Brianna's binding share and her removal return;
  - Marcus is now excluded from the start of the term, so he has no share and no return.
- check_extended rejects factors read only from term fields, so the package, state, term-points and vehicle relativities are plain parts of the standard rating, not factors.

## Charter-global items

- **R2-01** (ic daily basis T2/T3). Struck as a factor. The daily basis is now a plain binding: the current rate built on the term rating, divided by term days.
- **R2-02** (ex mail vs otherwise was a constant shift). The mailed tier now counts the form as received on the earlier of signing plus mail days and the processing date. That adds an input and an operation; pair-tested against the e-signature tier and the listing-anchor tier.
- **R2-03** (ic earned-premium labelled method). Replaced by ic_retained_pct, labelled parameter. It reads the request reason and the days in force (the short-rate table).
- **R2-04, R2-05, R2-06** (realism, charging one dimension twice, add-ons). Every listed member is struck and nothing new was added in its place:
  - the total-loss tier, class-change credit, delinquency retention and relativity;
  - the plan relativity as an add-on, and the installment charge at the insured request;
  - the elected, youthful and back-charged retentions, the return-to-household relativity;
  - the recent-exclusion and recorded-share points loads, and the reinstatement recapture.

  Acquisition (minimum earned) is withheld only once, at the insured request. The nonpayment return is pure pro rata, as the base says. The exclusion return keeps nothing.
- **R2-07** (zero-amount edges). No write tool books a 0.00 premium row. RE carves out a term recorded as cancelled with no return entry. IC and AB wait on record states. The endorsement tool no longer hard-codes "rated".
- **R2-08** (unreachable elected-exclusion fall-through). Struck together with the factor.
- **R2-09** (two terminal states). Closed by the rules:
  - EX now overrides the base clause "when the driver was unlisted, there is no premium change" for a resident reported operating while unlisted. Such a resident is excluded only on the listing the company makes.
  - EX's prerequisite sentence now holds back the endorsement itself, not only its return.
  - AD lists the resident whether or not an exclusion form is on file.
  - The endorsement tool records prior status from the share it is given, so an unlisted driver is handled faithfully.
- **R2-10** (transaction-date read). The read is struck: no exclusion factor reads a transaction date any more.
- **R2-11** (negative-day case). The brief-rating retention is struck. The remaining day counts state which end is counted and never go below zero.
- **R2-12** (multi-source factor in task 1). ad_listing_start_rule tests two records in every tier that is not the fall-through: the entry against the claim report, and the claim's loss against the term effective date. The lift's share basis reads the exclusion entry together with the package.
- **R2-13** (IC assembly named a factor). The assembly sentence is now generic: relativities, then days, then percentages, then amounts.

## Task findings (revision_2)

- **0.1, 0.2, 0.3** (factors surviving in task 0 below bounds).
  - NC has 4 factors, RE 5, IC 6.
  - All are keyed on records: run-off, certificate form and type, payment plan, nonpayment history, re-written days bounded by the days the return gave back, request reason, and acquisition by days in force.
  - Each one moves its result on the world. All gates are green.
- **1.1** (two terminal states). Closed by R2-09.
- **1.2, 1.3** (EX below bounds; no multi-source factor).
  - EX has 6 factors: the effective-date method plus the driver-rating relativities of the share it returns.
  - Multi-source is covered by R2-12.
- **1.4** (AD and AB counts). AD has 6 factors and AB has 5, all record-keyed.
- **1.5** (economics). The company no longer keeps premium for excluded days: the exclusion return is pro rata of the share the listing charged.
