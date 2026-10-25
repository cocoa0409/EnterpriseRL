# render_r2 — auto (Owner Auto Policy), cancellation_reinstatement_and_exclusions

RENDER round 2: STOPPED (source re-scan, before any document was written)

Gate checked: `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN`.
Source re-scanned: auto.extended.yaml (sha256 prefix d0d842f3b14c7243) and task_tools.py (unchanged).
No document was written.

## render_r1 items: all closed (each verified against the rule words and the compute)

- F1 closed. The baseline now reads "the standard lift share multiplied by the state and platform-use
  relativities stated above and rounded to the cent ... with no other relativity". With every factor at
  its baseline this equals `ab_share` / `result`.
- F2 closed in both policies. The report-date and processing-date tiers take "the later of ... and the
  day after the reported date of loss", and compute applies `MN(DAYS(...), DAYS(ex_loss|ad_loss, ...) - 1)`.
  The stated invariant now holds when a claim is reported on the date of loss.
- F3 closed. The whole-entry tier now requires "the term carries the re-written premium entry for that
  reinstatement", and the fall-through names the 0.00 case. Both match `ic_daily` / `ic_whole`.
- F4 closed. Each relativity sentence now says "or no such entry on the term, takes relativity 1".
  This matches the defaults in compute (age 99, relationship '', points 0).
- F5 closed. `ad_form_name: COUNT(... excluded_driver_name=ad_name)` now matches "a Named Driver
  Exclusion form on file".
- F6 closed for the exclusion and re-listing reads, which now filter on the most recent entry's own
  event type. Non-blocking note: the lift's `ab_vpts` is still a SUM over `event_type='auto_driver_excluded'`
  on `ab_ex_date`. A tie there would need two exclusion entries for one driver on one date, so it is
  practically unreachable. It is noted only because rework_r7_claims.md says the lift's points now use LATEST.
- F7 closed. The form gate is now scoped to the term's latest form, and only when that form names a
  resident reported while unlisted. Those are exactly the forms auto_ext_reported_resident_exclusion handles.

## G1 (blocking; it existed in round 1 and I missed it then) — the lift's second prerequisite waits on every unlisted resident, but the re-listing rule prices only the resident on the latest report

auto_ext_exclusion_lift_premium, prerequisite sentence (state form):
> "The additional premium for lifting a named driver exclusion is not fixed until every household resident reported operating a scheduled vehicle on a claim of the term while unlisted, other than one named on a Named Driver Exclusion form on file, carries a driver-added entry dated after the claim's date of loss."

auto_ext_household_resident_relist, the only policy that books that entry:
> "The resident concerned is the driver named on the claim report of the term with the latest report date that records the person operating the vehicle as an unlisted household resident; when two such reports carry the same report date, the one entered first on the claim file is taken; that report's report date and date of loss, and the resident's most recent entry on the term by change effective date ... supply every date, date of birth, relationship and violation points read below."

Compute:
- `ad_name: XLATEST('physdam','physdam_claim_events','driver_name', date_field='entry_date', auto_policy_id=HID, event_type='physdam_claim_reported', driver_household_status='unlisted_household_resident') or ''`
- `ad_report` and `ad_loss` are the same XLATEST read, without any driver filter.

The re-listing rule's own overwrite (replaced_by) also claims every such resident:
> "For a household resident reported operating a scheduled vehicle on a claim of the term while unlisted, and only for that resident, the listing takes effect on the date set below and the additional premium is the re-listing premium worked out below"

Consider a term with two different residents recorded as unlisted operators on its claim reports:
R1 on the earlier report and R2 on the latest, with R1 named on no exclusion form. The lift's gate
needs R1 to carry a driver-added entry dated after R1's own claim's date of loss. The re-listing rule
and compute only ever pick R2's report: the resident, the dates and the reads are all keyed to the
latest report. Nothing, in words or in compute, prices R1's listing date or R1's premium. The same
gap appears when the latest unlisted report names a resident who is on a form (exempt) and an earlier
report names R1, who is not.

Two readings follow, and neither is stated:
- (a) Apply the re-listing method to R1 using R1's own report. Compute cannot produce that figure.
- (b) Treat R1 as unpriced. Then the lift waits on a state that no priced write brings about. This is
  a deadlock on a reachable world (XF 12: no words-only case; XF 19: no deadlock), the same class as
  render_r1's F7.

Fix on the source side (either one):
- Scope the lift's second prerequisite sentence the same way F7 was closed. For example: "...not fixed
  until the household resident on the term's latest claim report recording an unlisted household
  resident, unless named on a Named Driver Exclusion form on file, carries a driver-added entry dated
  after that claim's date of loss". Sync the edge condition to match.
- Or key the re-listing reads per resident (each resident's own latest unlisted report), so that every
  resident the gate names has a priced write.

Everything else re-scanned clean, including the nonpayment return, the lapse reinstatement (the return
entry tie is now stated: "the one entered first when two share the latest transaction date", matching
`rw_ret_pd: LATEST(... date_field='transaction_date' ...)`), and the insured-request return.
