# Rework round 10: claims per revision_9 audit item

No scored values are given here, and none moved.

## R9-01: the exclusion's full rating could reach a resident whose recorded share already embeds the tiers

**Closed with a stated record test, enforced in the compute.**

The exclusion rule now prices only the resident named on the term's latest Named Driver Exclusion form who meets all of these:
- reported operating a scheduled vehicle while unlisted;
- carries no driver-added entry on the term.

This condition appears in the scope sentence and in the first overwrite. The compute enforces it with `ex_added_n` (a COUNT of the resident's driver-added entries): a resident with any such entry is charged no listing premium.

**Residents outside the test** (anyone once rated on the term by a driver-added entry) are excluded under the base clause. The `replaced_by` restates that clause:
- a driver rated immediately before the exclusion has premium returned;
- an unlisted driver has no premium change;
- in either case this rule charges no listing premium.

**Sibling and edge sentences now name the narrower case:**
- The re-listing's and the lift's overwrites name the exclusion's case with the same test.
- The re-listing's hand-off sentence names both routes: the exclusion rule when the resident carries no driver-added entry, the base clause otherwise.
- The lift's form gate and its edge condition now wait only on a latest form whose resident passes the test, so the lift never waits on a form no tool prices.
- Task 1's closure, the read necessity and the rationale quote are synced to the new wording.

**Probe:** the world still prices Brianna. A copy in which she carries a driver-added entry gives no listing premium.

## Last sweep: factor tiers already embedded in a recorded figure

None found on any in-scope world:
- **Re-listing:** prices from the recorded share and carries only what changed since it was rated.
- **Lift:** three share-basis tiers. A driver excluded before ever being rated starts from the base rate. A driver rated and then excluded has his recorded share divided by his then-relativities, so only what changed since is re-rated. With no exclusion entry, the term-premium share is used.
- **Exclusion:** rates only residents with no rated share.
- **Term computations:** start from the recorded premium. Their factors are transaction methods or charges that no recorded figure carries.

**Verbatim checks clean:** compute_basis, replaced_by, baseline and policy_source.
