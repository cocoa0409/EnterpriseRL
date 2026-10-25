# Rework round 2: claims per round-1 audit item

No scored values are given here. "NC/RE/IC" = nonpay cancel return / lapse re-write / insured-request return (task 0);
"AD/EX/AB" = household re-listing / exclusion return / exclusion lift (task 1).

## Charter-global (_difficulty.md)

- CG-01 (two tiers, one method: daily basis). Closed for the whole class. RE's daily basis now has three methods, each a different
  formula: a return entry lower than the prorated current rate means charges were withheld, so the current rate / term_days applies;
  an entry that is not lower gives entry amount / premium_days; no entry gives premium-written / term_days. IC: a re-written entry
  effective on the recorded reinstatement date gives entry / premium_days; changes on the term give current rate / term_days;
  otherwise premium-written / term_days. Pair test run on scratch worlds (with change rows and without).
- CG-02 (rw_restart_date_rule label). Struck. The reinstatement effective date is now plain rule text (later of latest payment and
  latest attested statement, plus the base offset), not a factor. RE's new method factor is rw_rewritten_days_rule: certificate
  run-off overlap, cancellation-filed certificate end date, or the reinstatement date. These are three different anchors.
- CG-03 (email tier, constant-shift pair). Struck. ex_effective_date_rule tiers: a re-listing entry later than both form dates
  (anchor = that entry), a mailed form (signing + mail_receipt_days vs requested), or otherwise later of signing and requested.
  Only the base's delivery methods are used.
- CG-04 (ic_reinstatement_recapture reads ic_rw_eff). Closed. The recapture reads the term's own reinstatement fee entry
  (auto_premium_transactions, fee row effective date) through its own binding. No factor reads another factor's binding in any
  policy (swept in all 32 factors).
- CG-05 (processing_lag_days dropped). Closed. NC restates the base sentence verbatim, including "with processing_lag_days added".
- CG-06 (unreachable tiers). Closed for the class. ad back-charge start, ad loss-cause and ab excluded-operation factors are
  struck. Every surviving ladder's fall-through is reachable inside the policy's own scope. Probes covered never listed, removal
  after the report, no collision report, and a comprehensive-only report.
- CG-07 (back-charging a denied period). Closed. The re-listing now takes effect on the claim's report date after a removal (or
  on the day after the loss when never listed), and the rule says the listing never takes effect on or before the date of loss.
  Physdam's coverage decision therefore still reads the resident as unlisted at the loss.
- CG-08 (replaced_by drops in-force content). Closed. NC and IC replaced_by sentences restate the underwriting cancellation's
  transaction-by-transaction computation in full. The EX replaced_by restates the effective date of an exclusion of any other
  driver and the removal return. Sibling overwrites name each other's case.
- CG-09 (same-day ties). Closed for every first/latest read. Each rule states a tie: requests by received date, forms by signing
  date, driver entries by change effective date, claim reports by report date ("the one entered first"), several payments on
  the latest posting date (they count as posted that day), statements by signing date, certificates with the same status (the one
  entered first), and the first plan entered. Probed with decoys: second same-day request, second form, two same-day payments,
  certificates filed plus SR-26'd, and two statements (task 0 now seeds an older statement as a live decoy).
- CG-10 (unreal outcomes). Closed. Every listed factor is removed, with no new company add-on in its place: lapse-length,
  filer, short-remainder and returned-payment loads; SR-26 handling and short-notice charges; points/loss-involvement
  retentions; late-endorsement credit; household-frequency, vehicle-value and late-report loads; schedule-change load; loss-payee
  notice. Real keys used: certificate run-off days (SR-26 liability), short rate vs pro rata by request reason, fully earned on a
  total loss, minimum-earned acquisition and installment-plan charges, pro rata of the remainder only from the reinstatement
  (lapse days uncharged), the base reinstatement fee, driver class by age x relationship, violation points, chargeable collision
  reports, platform use, pro rata from the exclusion effective date, and back-charge from the date the resident became an
  operator known to the company. Honest flag: the term-level computations cannot carry 4-6 real factors in this charter. These
  factors are company schedules kept for the factor floor and keyed on the record's own facts, not on other drivers or desk
  events: rw_delinquency_relativity, rw_plan_relativity, ic_reinstatement_recapture, ad_household_return_rel,
  ex_elected_exclusion_retention, ex_youthful_driver_retention, ex_backcharged_listing_retention (nc_delinquency_retained_pct
  stays the company's filed earned-premium schedule, as the audit observed).
- CG-11 (no multi-source factor in task 1). Closed. ad_driver_class_rel (age from the resident's entry x relationship x
  processing date), ad_listing_start_rule (resident's entry type and date vs claim report date vs loss date) and
  ab_lift_share_basis are genuine multi-source factors.
- CG-12 (rule word vs compute). Closed. AB no longer counts changes. Every claim count is filtered by event_type
  physdam_claim_reported, the named driver and the term, which matches the rule's words "claim reports of the term naming the
  driver". Rule words were re-read against compute for all 6 policies; IC's total-loss tier now says "the coverage entered first when the
  term has more than one", matching its single-coverage read (as the plan reads already did).
- CG-13 (edge sentence weaker than condition). Closed. The AB edge to the re-listing is gone. EX's sentence now carries the date
  ("a driver-added entry for that driver dated after the claim's date of loss"), the same as its condition, so an old pre-removal
  entry does not satisfy it.
- CG-14 (stamp agrees with tier). Closed for NC/RE/IC run-off tiers. Each tier requires both the stamp (term written to back
  sr22/fr44) and a backed certificate's status. Probed: stamp none with a filed certificate, stamp sr22 with no certificate, and
  stamp sr22 with SR-26 only each select a different tier, so the stamp alone does not decide.
- CG-15 (counted/not-counted, month-end). Closed. Every "calendar days from A to B" sentence states which end is counted. Whole
  months state the month-end convention (a missing day number completes on the first of the next month). Ages state birthday
  completion and the 29 February convention.
- CG-16 (cap deadlock). Closed. AB's sentence carves out a form whose endorsement would take the excluded count past the
  package's maximum while the lifted driver still counts, so the lift is not blocked when the endorsement cannot run first.
- CG-17 (assembly names factor-only quantity). Closed. Every assembly sentence is generic: "those that settle the days... those
  stated as a percentage... those stated as an amount", "the relativities", "the load percentages, a credit counting as a
  negative load", "the retained percentages".

## Task 0 (0.md)

- 0.1 (rw factors do not survive). Closed. RE rebuilt with 5 factors (2 methods, 3 parameters). Each moves the result on this
  world. The class-change credit reads the named insured's certificate date of birth (the world's insured was re-aged so the
  class changes inside the term).
- 0.2 (ic factors do not survive). Closed. IC has 6 factors: earned-premium method, daily basis, run-off, acquisition, plan,
  recapture. SR-26 and short-notice charges are gone, and the recapture reads its own fee entry. The earned-premium method's
  total-loss tier is not marked cross-difficulty, because task 0 seeds no physical damage coverage.
- 0.3 (stamp reaches nc runoff). Closed by the CG-14 change (stamp AND certificate status), with probes.
- 0.4 (inclusive short-notice exposure). Closed. The short-notice charge is struck, and every remaining day count states its ends.
- 0.5 (processing_lag_days). Closed by CG-05.
- 0.6 (pending 14 days, statement before cancellation). Partly closed. The frozen date moved earlier, the payment and statement
  moved to just after the cancellation date, and the statement's lapse period starts on the cancellation effective date. A
  pending term after its effective date is what makes the nonpayment cancellation owed now, so that part is kept.
- 0.7 (charge stack on a short reinstatement). Closed in substance. Only the reinstatement fee, pro rata of the remainder from
  the reinstatement (no premium for lapse days) and the flagged schedules remain. The persona's go-ahead still authorises the reinstatement.

## Task 1 (1.md)

- 1.1 (edges carry weight only through a struck factor). Closed. The tree is rebuilt as a chain. The exclusion return reads the
  share the re-listing writes (skip -> the return falls to zero), and the lift waits on the endorsement through a state gate.
- 1.2 (ex factors do not survive). Closed. EX has 5 factors: an effective-date method (re-listing anchor / mail / otherwise) and
  four retentions. Each moves the result. Three retentions are flagged under CG-10.
- 1.3 (ad factors do not survive). Closed. AD has 6 factors: listing start, driver class, points, chargeable collision,
  platform use, return-to-household. Each moves the result. The report-date start resolves CG-07.
- 1.4 (ab below bounds). Closed. AB has 6 factors: share basis, recent exclusion, points, chargeable collision, platform use,
  class-change credit. Each moves the result. The schedule-change load and notice charge are gone.
- 1.5 (no multi-source factor). Closed by CG-11.
- 1.6 (violation_points observation). The term's violation_points is now the named insured's own (the only rated driver at the
  last rating). Wendell is removed from the world.
