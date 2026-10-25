# Rework round 7: claims per render_r1 findings

No scored value moved.

## F1: lift standard figure vs relativities outside the factors

**Closed.** The standard lift premium now names the state and platform-use relativities as plain parts of the standard, applied to the standard lift share and rounded to the cent, "with no other relativity". With every factor at its baseline, the compute now matches the baseline sentence.

## F2: "the listing never takes effect on or before the date of loss"

**Closed in both policies, reported-resident exclusion and re-listing.** The report-date tier and the processing-date tier now read "the later of the report date (or the processing date) and the day after the reported date of loss". The standard listing date states the same. The compute takes the fewer of the two day counts, so the stated invariant now holds on a zero-lag report.

## F3: insured-request daily basis with no re-written entry

**Closed.**
- The whole-entry tier now requires that the re-written entry exists.
- The fall-through now states that it covers "a reinstatement whose re-written premium of 0.00 was not booked".
- Same-date re-written entries are stated as taken together, which matches the compute's SUM.

## F4: relativities when the resident has no entry

**Closed across the class (reported-resident exclusion and lift).** The age-class, relationship and violation-points sentences now each say "or no such entry on the term, takes relativity 1", matching the compute's defaults. The re-listing rule already scopes out residents with no driver-added entry.

## F5: "a Named Driver Exclusion form on file" vs the latest form only

**Closed.** The re-listing now counts every form on file naming the resident, not just the latest one, which matches the lift's second prerequisite sentence.

## F6: SUM over same-date entries vs "the one entered first"

**Closed.**
- The re-listing (recorded share, points now) and the reported-resident exclusion (points) now read the most recent entry's own type as well as its date, so the read picks out a single entry, the one the tie rule names.
- The lift's share and points now use LATEST, which keeps the first entered on a tie.
- The reinstatement's read of the return entry now states its tie.

## F7: lift waits on forms no tool can endorse

**Closed.** The lift's form gate now waits only on the term's latest Named Driver Exclusion form by signing date, and only when that form names a household resident reported operating a scheduled vehicle while unlisted. These are exactly the forms the reported-resident exclusion handles, so no deadlock is possible. The condition text and task 1's closure, rationale and read necessity are synced to the new sentence.

## Probes and sweeps

Probes (all evaluate as stated):
- zero-lag report for the re-listing and for the exclusion: listing from the day after the loss;
- an older form naming the re-listed resident: not re-listed;
- a lift with no exclusion entry: relativities 1;
- an insured-request cancellation whose reinstatement date is later than its effective date, with no re-written entry booked: current-rate basis.

Sweeps clean: compute_basis quotes, replaced_by, baseline and policy_source sentences, and factor independence.
