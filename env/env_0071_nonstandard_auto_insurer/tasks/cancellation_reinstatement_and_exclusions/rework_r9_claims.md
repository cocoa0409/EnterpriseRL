# Rework round 9: claims per revision_8 audit item

No scored value moved.

## R8-01(a): the reported-resident exclusion's scope beyond its latest-form compute

**Closed.** The exclusion's opening scope sentence and its first overwrite (`replaced_by`) now name exactly the resident the compute handles. That is the resident named on the term's latest Named Driver Exclusion form by signing date, when that resident is reported operating a scheduled vehicle on a claim of the term while unlisted. For every other driver, the overwrite still restates the base clause: a rated driver's exclusion returns premium, and an unlisted driver's exclusion has no premium change.

## R8-01(b): sibling overwrites deferring the old, broader set

**Closed (point 5c).** Each sibling overwrite now names exactly the cases the depended-on rule prices, and excludes the siblings' cases by name:
- the re-listing of the household resident on the term's latest claim report recording an unlisted household resident, when that resident was rated earlier in the term by a driver-added entry and is not the resident named on the term's latest form;
- the listing that precedes the exclusion of the latest form's resident, when reported operating while unlisted;
- the lift of the exclusion of the driver on the term's latest claim report recording a named excluded driver.

The re-listing's two overwrites carry the same names. The lift's opening scope sentence is narrowed to the latest report's excluded operator.

**Same-class fixes found by the sweep:**
- The re-listing now hands only the latest form's resident to the exclusion rule (compute reads the latest form, matching the exclusion's scope). It now says the listing of a resident with no driver-added entry "is not decided by this rule"; its compute charges nothing for that case.
- The lift's second prerequisite sentence and its edge condition now wait only on a resident the re-listing prices: the latest unlisted report's resident, when rated earlier in the term by a driver-added entry and not named on the latest form. Task 1's closure and rationale quote are synced.

## Exhaustive sweep

Every scope, overwrite, `replaced_by`, edge sentence, edge condition and factor sentence was checked against the compute. No sentence describes a case the compute does not price. The compute_basis, `replaced_by`, baseline and policy-source verbatim checks are all clean.
