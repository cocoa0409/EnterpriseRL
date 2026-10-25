# render_r1 — auto (Owner Auto Policy), cancellation_reinstatement_and_exclusions

RENDER round 1: STOPPED (source scan, before any document was written)

Gate checked: `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN`.
Source: tasks/cancellation_reinstatement_and_exclusions/auto.extended.yaml plus task_tools.py.
No document was written. docs/auto/ and .doc_render_staging/auto/ were not created.

Every finding below is a place where the rule's words and the compute give different results, or where
the rule contradicts itself, on an input the charters allow. A render would have to choose one
reading, which means rendering around a source defect. The quotes are verbatim.

---

## F1 — auto_ext_exclusion_lift_premium: the computation document's sentence says "no relativity", but two relativities sit outside every factor and still apply (a binding on the wrong side of the factor line)

Rule / baseline.rule sentence:
> "The standard lift premium is the lift share multiplied by the calendar days from the lift effective date to the expiration date, the effective date counted and the expiration date not counted, and divided by term_days, with no relativity; it is rounded once, at the end, to the nearest cent, half up."

The rule sentence that conflicts with it:
> "The lift share is the company's filed driver rating of the driver as the driver now stands: the share basis below multiplied by the state relativity (state_rel_high for a term garaged in Florida or Georgia, state_rel_mid in Arizona, Texas or Virginia and 1 elsewhere), by the platform-use relativity of the company's filed driver rating (drv_platform_rel_two for at least two claim reports ... , drv_platform_rel_one for one and 1 for none) and by the age-class, relationship, violation-points, accident and occasional-operator relativities below"

Compute:
- `ab_state_rel: K('state_rel_high') if (ab_state == 'FL' or ab_state == 'GA') else (K('state_rel_mid') if (ab_state == 'AZ' or ab_state == 'TX' or ab_state == 'VA') else 1.0)`
- `ab_plat_rel: K('drv_platform_rel_two') if ab_plat >= 2 else (K('drv_platform_rel_one') if ab_plat == 1 else 1.0)`
- `ab_share: RND(ab_basis * ab_state_rel * ab_plat_rel * ab_rel_rel * ab_age_rel * ab_pts_rel * ab_acc_rel * ab_occ_rel, 2)`

`ab_state`, `ab_state_rel`, `ab_plat` and `ab_plat_rel` belong to no declared factor. So the computation
document has to claim them. But that same document renders baseline.rule, which says "with no
relativity". With every factor left at its baseline, compute still multiplies the share by the
state relativity and the platform-use relativity. Hypothetical witness: a Florida-garaged term,
full_term_premium 1000.00, no platform-use reports. baseline.rule gives a share of 250.00. Compute
with all factors at baseline gives 270.00 (250.00 multiplied by 1.08).
The fall-back test cannot give a single answer: either the computation document drops two live
relativities, or it contradicts its own sentence.
Fix on the source side (either one): make the state and platform-use relativities part of
baseline.rule (as auto_ext_reported_resident_exclusion does with "drv_base_rate multiplied by the
package and state relativities"), or declare them as factors.

## F2 — auto_ext_reported_resident_exclusion and auto_ext_household_resident_relist: "never on or before the date of loss" is false when the report date (or processing date) is the date of loss (zero lag)

auto_ext_reported_resident_exclusion rule:
> "Listing effective date of such a resident: when the resident's most recent entry on the term is dated before the report date, the listing takes effect on the report date, the day the company learned the resident was operating a scheduled vehicle; when the resident has no entry on the term and the reported date of loss is on or after the term effective date, it takes effect on the day after the reported date of loss; otherwise it takes effect on the processing date. The listing never takes effect on or before the date of loss, so the coverage decision on that loss still reads the resident as unlisted."

Compute: `ex_start: ex_rep_start if (ex_last_date != '' and ex_last_date < ex_rep_start) else ((ex_loss if ex_loss >= ex_term_eff else NOW) if ex_last_date == '' else NOW)`

auto_ext_household_resident_relist rule:
> "Listing effective date of a re-listed resident: when the resident's most recent entry on the term is a driver-removed entry dated before the report date, the listing takes effect on the report date, the day the company learned the resident was again operating a scheduled vehicle; when the resident's most recent entry is a driver-added entry dated after the reported date of loss, the resident is already listed again and nothing is charged; otherwise the listing takes effect on the processing date. The listing never takes effect on or before the date of loss, so the coverage decision on that loss still reads the resident as unlisted."

Compute: `ad_days: DAYS(ad_report, ad_exp) if (ad_last_type == 'auto_driver_removed' and ad_last_date < ad_report) else (0 if (ad_last_type == 'auto_driver_added' and ad_last_date > ad_loss) else DAYS(NOW, ad_exp))`

The physdam charter allows a claim report whose entry date equals the date of loss. It only sends
reports made more than late_report_review_days after the loss to review. In that case the
report-date tier, and the processing-date tier when the claim is processed the same day, set the
listing on the date of loss. That breaks the sentence "The listing never takes effect on or before
the date of loss". One reader charges from the report date. Another moves the listing to the day
after the loss. The listing premiums differ by one day.
Fix on the source side: either state the zero-lag case and price it (for example, "the later of the
report date and the day after the date of loss"), or delete the sentence that claims the invariant.

## F3 — auto_ext_insured_request_cancel_return (ic_daily_basis_rule): absent re-written entry when the reinstatement date is after the cancellation effective date

Rule:
> "when the recorded reinstatement_date is after the cancellation effective date, the re-written days never having begun, that re-written entry's whole amount is unearned and is returned in place of the daily basis multiplied by the days returned; otherwise the daily basis is the current full-term rate divided by term_days."

Compute:
- `ic_daily: ic_rw_amt / ic_rw_pd if (ic_rw_eff != '' and ic_rw_eff <= ic_eff and ic_rw_pd > 0) else (0.0 if (ic_rw_eff != '' and ic_rw_eff > ic_eff and ic_rw_amt > 0) else ic_rate / ic_tdays)`
- `ic_whole: ic_rw_amt if (ic_rw_eff != '' and ic_rw_eff > ic_eff and ic_rw_amt > 0) else 0.0`

The second tier's words depend only on the reinstatement date being after the cancellation
effective date. Compute also requires a booked re-written entry (`ic_rw_amt > 0`). A reinstatement
with lapse whose re-written premium is 0.00 books no entry. The lapse-reinstatement rule says "a
re-written premium of 0.00 is not booked", for example after a nonpayment cancellation whose return
was 0.00 and so "the re-written days are zero". In that world the words return the whole amount of
an entry that does not exist (0.00, so nothing is booked). Compute instead returns the full-term
rate divided by term_days multiplied by the days returned. The two numbers are different.
Fix on the source side: give the rule an explicit absent-entry case that matches compute, or make
compute follow the words.

## F4 — auto_ext_reported_resident_exclusion: resident with no entry on the term, so age-class, relationship and violation-points relativities read an entry that does not exist (absent record)

Rule:
> "the entry named is the driver's most recent entry on the term (when two share a change effective date, the one entered first is taken), and the rating date is that report's report date."
> "Age-class relativity of the resident's rating share, under the company's filed driver rating, by the driver's age in whole years on the rating date named above ... from the date of birth on the entry named above"
> "Relationship relativity ... by the relationship on the entry named above"
> "Violation-points relativity ... by the driver_violation_points on the entry named above"

The listing ladder itself names the case "when the resident has no entry on the term". Compute
handles it silently:
- `ex_dob: LATEST('auto_policy_changes','driver_date_of_birth', date_field='change_effective_date', driver_name=ex_name) or ''`
- `ex_age: int(MONTHS(ex_dob, ex_report) / 12) if ex_dob != '' else 99`
- `ex_relship: LATEST('auto_policy_changes','driver_relationship', date_field='change_effective_date', driver_name=ex_name) or ''`

With no entry, compute gives age 99 (relativity 1), relationship '' (relativity 1) and points 0
(relativity 1). The rule never says what applies when there is no entry. For a never-listed
resident, which is the plain unlisted case, the exclude_reported_resident tool also writes an empty
date of birth and relationship. A reader may take the resident's real age or relationship from
elsewhere and apply the youth or relative relativity. Compute applies 1.
Fix on the source side: state the no-entry case in each of the three relativity sentences (for
example, "a resident with no entry on the term takes relativity 1"), or read these facts from a
record that always exists.

## F5 — auto_ext_household_resident_relist: "a Named Driver Exclusion form on file" versus a read of the latest form only (decoy row)

Rule:
> "A resident named on a Named Driver Exclusion form on file is listed and excluded under the exclusion rule instead and is not re-listed under this rule, and a resident with no driver-added entry on the term carries no share for this rule to re-rate."

Compute:
- `ad_form_name: LATEST('auto_policy_documents','excluded_driver_name', date_field='document_date', event_type='auto_exclusion_form_signed') or ''`
- `ad_share: 0.0 if (ad_name == ad_form_name or ad_rate_date == '') else RND(ad_rec_share * ad_age_rel * ad_pts_rel * ad_acc_rel * ad_plat_rel, 2)`

Consider a resident named on an earlier form while a later form names someone else. The words
exclude that resident from re-listing. Compute re-lists the resident and prices them. The policy
6 prerequisite sentence carries the same "on file" wording ("other than one named on a Named
Driver Exclusion form on file"), so the two sides disagree on that world as well.

---

## Secondary (same class, rarer worlds; worth fixing in the same pass)

### F6 — same-day tie stated as "the one entered first is taken", but SUM adds every row on that date
auto_ext_reported_resident_exclusion:
> "the entry named is the driver's most recent entry on the term (when two share a change effective date, the one entered first is taken)"
`ex_vpts: SUM('auto_policy_changes','driver_violation_points', driver_name=ex_name, change_effective_date=ex_last_date)`

auto_ext_household_resident_relist:
> "the resident's most recent entry on the term by change effective date (when two of the driver's entries share a change effective date, the one entered first is taken)"
`ad_rec_share: SUM('auto_policy_changes','driver_term_premium', driver_name=ad_name, change_effective_date=ad_last_date)`
`ad_pts_now: SUM('auto_policy_changes','driver_violation_points', driver_name=ad_name, change_effective_date=ad_last_date)`

If two of the driver's entries share the latest date, compute adds their points or shares. That
can happen with the exclusion tool's own driver-added and driver-excluded pair when the listing
and exclusion dates coincide. The words take one entry.

### F7 — possible deadlock (XF 19) between the lift's form gate and the exclusion rule's "latest form" scope
auto_ext_exclusion_lift_premium prerequisite sentence:
> "The additional premium for lifting a named driver exclusion is fixed only after every Named Driver Exclusion form on file for the term has its exclusion endorsement recorded, apart from a form whose endorsement would take the currently excluded drivers past the package's maximum number of excluded drivers while the driver being lifted is still counted among them."

auto_ext_reported_resident_exclusion:
> "The form handled is the term's latest Named Driver Exclusion form by signing date (when two forms share the latest signing date, the one entered first is taken)"

An older unendorsed form, under a newer endorsed one, is endorsed by no policy that has a tool. The
exclusion rule handles only the latest form, and no other exclusion tool exists. Unless the
max-excluded exception applies, the lift waits forever on that world.

---

Checked and found consistent (no finding): the run-off, SR-26 transmission-day, acquisition and plan
charges in auto_ext_nonpay_cancel_return; the effective-date, re-written-day, fee-basis, lapse,
certificate exposure, form, type and out-of-state charges in auto_ext_lapse_reinstatement_rewrite;
the run-off, transmission, retained-percentage and plan charges in auto_ext_insured_request_cancel_return.
The first-match certificate_runoff_days and sr26_transmit_within_days reads on "filed" certificates
are uniform across fr tiers (10 and 3), so a tie there is immaterial.
