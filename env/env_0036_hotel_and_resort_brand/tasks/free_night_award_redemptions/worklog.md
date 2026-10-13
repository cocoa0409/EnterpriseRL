# free_night_award_redemptions — per-difficulty worklog

## Step 0 — draw (scripts/draw_counts.py --tasks 2)

```
{"task": 0, "key": "env_0036_hotel_and_resort_brand/free_night_award_redemptions/0", "prerequisite_problems": 2, "problems": 3, "factor_counts": [6, 4, 5]}
{"task": 1, "key": "env_0036_hotel_and_resort_brand/free_night_award_redemptions/1", "prerequisite_problems": 2, "problems": 3, "factor_counts": [5, 5, 6]}
```

## Round 0 finding (kept for the record)

The certificate charter's write surface carries few numbers. `certificate_apply` and `certificate_release`
send any non-zero top-off to the loyalty account (`loyalty_points_redeem` / `loyalty_points_redeposit`), so
Principle D bars every task tool from writing a non-zero top-off. What is left is the points price
carried on award history records (hold / release / loss), the award's night, and award dates (expiry,
closed). The only customer-owned write in this product is applying an award ("the choice of which
award to spend on which stay is the member's own"), and a seeded award becomes usable during the call
only through a release. Round 0 stopped and reported this.

## Round 1 decision (orchestrator: route around inside the write domain, never ask)

Closest established rule: the skill allows a version-update override of any base clause when the
override names the sentence it replaces (`overwrite`), and it measures difficulty in factors that are
"tier or card-specific terms as real programmes publish them". So the six computations are built as
one coherent extended programme — **Ashbury Award Price Protection & Replacement terms** — layered on the
award-chart price and the replacement-validity rule, with every departure from base declared clause by
clause:

* award-chart night price (category row x season column) — real chart mechanics; the season column is a
  factor, the standard column is the computation document's default;
* award share of a forfeited night (cap / top-off / uncapped) — the base top-off formula read backwards;
* cancellation timing (how close to arrival a late cancellation was recorded) — "cancellation timing
  forfeits";
* member recognition by elite tier, elite nights this year, co-brand card, tenure, past relocations —
  "tier or card-specific terms";
* repeat-return behaviour read from the award's own history;
* rebooking protection: the price recorded on an award's return caps the price of its next hold within a
  window (late-cancel return) or carries the walked night's discount (relocation return);
* replacement validity: months by tier, by delay of the return, by past relocations, by tenure and
  stays, and an end-of-month convention for premier cardholders.

No GT path writes a non-zero top-off: every release and every apply in gold writes 0 top-off, every hold
price in gold sits at or below the applied award's cap, and the tools fix top-off at 0 internally.
No `certificate_expire` problem is claimed: in task 1 the expiry that follows a late relocation return
is the system's own transition (lifecycle `issued -> expired, by: system`), so it is not a desk
obligation left hanging.

## Scope plan (principle C)

| task | story | tree (depended-on first) | draw -> factor counts |
|---|---|---|---|
| 0 | late cancellation of a two-award resort stay; rebook the same resort | forfeit first-night award -> return later-night award -> member applies it to the new stay (root, user) | forfeit 4, return 5, apply 6 |
| 1 | hotel relocated (walked) an 85K award stay; award never came back and is past its date | return the award from the relocated stay -> reissue replacement -> member applies replacement (root, user) | return 5, reissue 6, apply 5 |

Tools (uuid8 drawn once each, frozen):
`forfeit_late_cancel_award_5a86721d`, `release_later_night_award_2a59ee43`, `apply_returned_award_7b7c21ba` (user),
`release_relocated_award_8143384d`, `reissue_replacement_award_0d99e6ce`, `apply_replacement_award_003026b1` (user).

Task 0 occupies: certificate_forfeit (late cancel), certificate_release (late-cancel later night),
certificate_apply (returned award). Task 1 keeps: certificate_release (relocation),
certificate_issue (reissue), certificate_apply (replacement) — disjoint policies and tools.

## Task 0 — closed

Story: Natalie Sorensen (Platinum Elite, Ashbury Rewards Card) cancelled her two-award Naples resort stay
74379163 two days before arrival (after the 3-day resort deadline); neither award was settled. She asks to
use her award on her December booking 74412638 at the same resort.

Tree: certificate_ext_late_cancel_loss_value (forfeit 25K, 4 factors) -> certificate_ext_late_cancel_return_protection
(return 35K, 5 factors) -> certificate_ext_returned_award_rebook_price (member applies 35K, 6 factors, root, user).
Edges: rebook <- return (value_input, ap_protected; skip -> 36,750 instead of 34,750); return <- forfeit
(state_gate, award status).

Gold: 23,500 / 38,000 / 34,750; baselines 35,000 / 30,000 / 35,000; every factor bites (see tasks/0.json).

Revisions during authoring:
- check_solvability: blueprint action_bindings require reservation_id on forfeit/release and loyalty_member_id on
  apply -> added those Id-class parameters to the tools (docstrings updated, contract gate re-run OK).
- check_compute: "history not load-bearing" for the loss value (LATEST is not zeroed and the cap path gives the same
  share) -> the top-off paid is now read from the loyalty ledger (deducted less returned for the award), a real
  reconciliation; the rebooking window became a 3-calendar-month COUNT of return records -> COMPUTE OK.
- replay: empty-string foreign keys counted as dangling -> empty *_id fields dropped from seed rows.

Gate block (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
CACHE-DIFF INFO, SCOPE OK.

Manual checks: prerequisite sentences pass the four-point test (connectives 'only after' / 'not ... until';
record-visible states; no code tokens; scope = the returned award / the first-night award of the same reservation);
the two directions differ (a price "is fixed only after", a return "is not made until"). The persona raises no
prerequisite and no extra ask; her last reaction answers the application. All writes happen at one frozen_time;
nothing waits on a real-world event.

## Task 1 — closed

Story: Marisol Quintero (Titanium Elite, Ashbury Rewards Premier Card) was walked from the Maui resort stay
74370651 on 2026-07-03; her 85K award FNA64390418 (expiry 2026-07-09) was never returned. She asks to use the
award from the Maui trip on her December booking 74413275 (Ashbury Grand San Francisco), keeping this year's
85K award untouched.

Tree: certificate_ext_relocation_return_protection (return, 5 factors) -> certificate_ext_relocation_replacement_validity
(reissue, 6 factors, date result) -> certificate_ext_replacement_hold_price (member applies the replacement, 5 factors,
root, user). Edges: validity <- return (value_input, rq_return_date); hold <- validity (state_gate, replaced award reference).

Gold: 32,500 / 2028-03-31 / 47,750; baselines 70,000 / 2027-04-05 / 60,000; every factor bites.

Revisions: once_per_occasion binds issue_source to a system value -> seeded the member's 2024 walk and its
replacement pair (FNA64107752 -> FNA64129903, outside every window, also a near-miss for the walks count);
replay closure missed the 2024 award history -> the award-history read is by customer.

Expiry after the return: the Maui award, past its expiry, becomes expired through the system's own transition
(lifecycle `issued -> expired, by: system`); no desk expiry problem is claimed.

## Difficulty-level closure

* Policies: 6 extended policies, each claimed by exactly one task (task 0: loss value, late-cancel return, returned
  award rebook price; task 1: relocation return, replacement validity, replacement hold price); tools pairwise disjoint.
* Every tree: 2 prerequisite problems (= draw), 1 value_input edge (>= max(n-1,1)), one owner=user write.
* Factor counts: task 0 {6,4,5}, task 1 {5,5,6} = draws; each policy >= 2 parameter and >= 1 method factor;
  multi-source and cross-difficulty factors in both tasks; suite history_rows_max 9, branches_max 89.
* Prerequisite sentence directions: two affirmative ("only after"), two negated ("not ... until").
* No gold write carries a non-zero top-off; no write lands in another category; no handoff in gold.
* Traceability gate skipped (published KB not rendered yet), as instructed.

Final gate block (difficulty-wide): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK,
GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.

## Rework round 2 — audit env/env_0036_hotel_and_resort_brand/audits/policy_task/free_night_award_redemptions/

Plan, one finding at a time (no regression of the passing problem trees):
- G-1: the cancellation-timing ladder is recut on reachable lead days (arrival date / day before / two days
  before, the last only possible at resort brands); task 0 world moves to a cancellation recorded the day before
  arrival so the customer sits on a reachable middle tier and the fall-through is reachable by others.
- G-2: no stays factor survives in P3; P5's stays factor counts nights credited (XSUM of nights) and says so.
- G-3 (a) P1 reliefs struck; P1 becomes a pure award-mechanics valuation: night season, the chart's season step by
  category band, the award's share against its cap, and top-off reconciliation from the loyalty ledger (top-off
  deducted for the forfeited night's reservation less any returned). (b) P2 repeat-returns struck, replaced by the
  member's elite tier. (c) P4 placements struck, replaced by this year's elite nights. (d) P5 moves struck,
  replaced by the length of the walked stay. (e) P3 lead and stays struck, replaced by co-brand card and elite
  nights; P6 lead struck, replaced by elite tier. Kept families are the ones the audit accepted as real (chart
  season steps, cap/top-off share, walk compensation by tier and walked-stay length, replacement goodwill months by
  tier/tenure/delay, card-holder and elite-night benefits, points nights on the same reservation).
- G-4: P4 declares the override of the base "released award whose expiry date has already passed ... expires on the
  day it is released" sentence: an award returned from a relocated stay after its expiry stands returned until its
  replacement is deposited and is then closed by the system's own expiry; never reinstated for a stay.
- O-1 scope split (P3 excludes a replacement's first hold, P6 covers it), O-4 boundary wording, O-5 docstring,
  O-6 condition aligned, O-7 "reference" not "number", T1-O1 walks wording; O-2/O-3/O-8 recorded below.

### Round 2 closure (finding -> change)

- G-1 (P2 timing ladder unreachable fall-through): tiers recut on reachable lead days — arrival date or later /
  the calendar day before arrival / two or more days before (reachable where the deadline is further out, e.g. the
  3-day resort deadline). Task 0's cancellation moved to 2026-09-17 (day before arrival), middle tier; baseline is the
  night's own chart price (reachable). `close_cancel_days` removed.
- G-2 (night credits counted as postings): P3's stays factor struck (G-3e); P5 stays extra now sums nights
  (XSUM nights) and the rule says "adds up the nights of the stay night credits ..., card anniversary night credits not
  counted", thresholds in nights (40 / 20). Task 1: 52 nights -> +2.
- G-3 (a) P1 reliefs struck; P1 = night season, chart season step by category band, award share against the cap,
  top-off reconciliation from the loyalty ledger (deducted for the forfeited night's reservation less returned).
  Task 0 world rebuilt: category-7 resort, 40K first-night award topped off 10,000 (and earlier topped off and refunded
  on a timely-cancelled stay), 85K second-night award, Platinum + Premier Card member. (b) P2 repeat-returns struck,
  replaced by elite tier. (c) P4 placements struck, replaced by this year's elite nights. (d) P5 moves struck,
  replaced by walked-stay length. (e) P3 lead and stays struck, replaced by co-brand card and elite nights; P6 lead
  struck, replaced by elite tier.
- G-4 (undeclared override): P4 now declares the override of base "A released award whose expiry date has already
  passed therefore expires on the day it is released ...; it is never reinstated for a new stay." — an award back from a
  relocated stay after its expiry stands returned, unusable, until its replacement is deposited, and the system's expiry
  run then closes it; tool docstring updated; P5's condition reads "stands returned".
- O-1: P3 states it covers a replacement once it has come back from a cancelled stay; P6 states it prices a
  replacement's first hold. O-4: P4 says "the short-delay days or fewer". O-5: apply_replacement certificate_id
  docstring no longer alludes to issuance. O-6: P5 condition aligned with its sentence. O-7: P6 sentence and closure say
  "reference". T1-O1: P4 counts relocations compensated "the posting for this relocation included".
- O-2 (top-off hard-coded 0): kept by design — loyalty triggers bar non-zero top-off writes; every gold hold price is
  within the applied award's cap (task 0 58,250 <= 85,000; task 1 46,500 <= 85,000) and no released award carries a
  top-off. O-3 (CFIELD keyed by status/plan): DSL cannot take the target reservation as a parameter; each world holds
  exactly one confirmed Reward Night Rate reservation. O-8: realism observations accepted by the audit, no change.
- Own-history reads that the history-zero floor could not move (LATEST only) replaced by chart prices of the
  reservation (P2, P4) — the base hold price is that chart price — so no factor rests on an unmovable read.

New gold: task 0 40,000 / 62,500 / 58,250; task 1 34,000 / 2028-04-30 / 46,500 (replacement fna_1f9bdadf5ca0,
FNA64071328). Every factor bites; baselines 60,000 / 50,000 / 60,000 and 70,000 / 2027-04-05 / 60,000.

Final gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (history_rows_max 9,
branches_max 89), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK. Traceability skipped (no published KB).

## Rework round 3 — revision_2 findings

Judgement calls (no explicit skill route):
- R2-F1: a top-off reconciliation is one rule, not a ladder; it stays as plumbing (its near-miss — the top-off
  refunded on another stay — is kept). P1 needs a fourth real factor. The only further real determinant of what a
  late-cancelled award night "costs" is the hotel's cancellation-window practice (charge depends on how late the
  cancellation was; same-day cancellations are charged as no-shows). P1's quantity is therefore stated as the
  late-cancellation charge the forfeited award settles (base booking Reward Night Rate penalty basis
  first_night_points: the charge is the first night's points price), with a timing method: the day before arrival ->
  the award's share (the top-off is forfeited separately); two or more days before (only inside a longer resort
  deadline) -> the award's share less one season step; otherwise (arrival date or later) -> the whole night price,
  which is the base penalty and the computation document's default.
- R2-F2: P6 walk protection recut by where the replacement is used: the walked hotel itself -> the night is priced
  at the walked-night protected price; another hotel of the same brand -> the night less the whole walked-night
  discount; otherwise (another brand) -> the night less half the discount (the standard, now in the baseline). Every
  tier reachable; task 1's December stay moves to an Ashbury Resort & Spa hotel (same brand, other hotel).
- R2-F3: the presence conjunct is dropped from the ladder; the "return must exist" guard lives in plumbing (the
  delay is counted to the award's return from the relocated stay).
- R2-F4: P2's night reduction reads the elite night credits posted in the last twelve calendar months from the
  ledger (stay and card anniversary credits; year-end resets are not credits): near-misses are the credit 13 months
  back and the membership's this-year field.

### Round-3 closure list
- R2-F1 (P1, task 0): loss_topoff_reconciliation removed. Top-off netting is now plumbing
  (`lv_topoff = lv_ded_res - lv_ret_res`; rule: "top-off deducted for or returned on any other reservation
  of the award never counts"), which keeps the 74340918 near-miss (counting it gives 30,000). New fourth
  factor loss_cancellation_timing (method; day before -> award's share; two or more days -> share less
  one season step; otherwise, arrival date or later -> whole night price, the factor baseline). Task 0:
  day-before tier, 40,000 kept; baseline 50,000. Files: certificate.extended.yaml, tasks/0.json.
- R2-F2 (P6, task 1): walk protection keyed on where the replacement is used (same hotel -> protected
  price; another hotel of the same brand -> whole discount; another brand -> standard half, now in the
  baseline rule and factor baseline). The relocated-return COUNT is a plumbing guard on the protected-price
  read. Task 1 December stay 74413275 moved SFGRD Ashbury Grand -> PSRSP Ashbury Resort & Spa (category 7,
  peak, tax 15%) and the persona now names Palm Springs; value 46,500 -> 28,500 (baseline 46,500,
  all-baseline 42,000). Files: certificate.extended.yaml, tasks/1.json.
- R2-F3 (P5, task 1): delay-extra conjunct removed from the rule, ladder and bindings; the COUNT of
  relocated returns guards the return-date read (plumbing; based on the prerequisite sentence). Value
  2028-04-30 unchanged; the value_input edge still holds (with no return the delay cannot be computed).
  Also fixed the stale "expiry 2028-03-31" in the night_date tracing. Files: certificate.extended.yaml, tasks/1.json.
- R2-F4 (P2, task 0): the night reduction reads the ledger: elite night credits posted fewer than twelve
  whole months before the return (thresholds 60 / 30). Task 0: 72 -> upper, 62,500 kept. Near-misses are
  the 2025-08-23 and earlier credits, the 2026-01-01 year-end reset, and the membership's this-year field
  52 (reading 52 gives 63,500). Files: certificate.extended.yaml, tasks/0.json.
- O-9: P2 now states its scope: only a later-night award whose expiry date has not passed is returned
  under this rule. No base sentence is overridden.
- O-10: the P1 middle-band sentence now reads "Unless the category band sets another size, one season
  step of the award chart is the middle-band step." (verbatim in the baseline).
- Passed items not regressed. P3 and P4 are untouched; P5/P6's other factors and P1/P2/P3 values are
  unchanged. All gates re-run green.

## Rework round 4 — revision_3 findings (task 0 / P1 only; task 1 PASS, untouched)

Judgement (R3-F2, no adjudication available). I searched real Free Night Award forfeiture practice for a
fourth determinant of a forfeited award's points value:
- Cancellation timing is not one. Every late cancellation forfeits the award whole (base
  certificate_forfeiture; booking_late_cancellation_penalty "the points or the Free Night Award paying the
  first night are retained"), and the group charter has no resell credit.
- Tier, card and tenure are reliefs on a measurement and were struck in round 1.
- Room type is ruled out: base eligibility allows standard rooms only.
- Brand charts and promotional pricing would contradict loyalty_award_redemption.
- A top-off limit tier is unreachable.

What the award chart itself publishes is a category x season table with category-banded season steps.
The category row is a real, published determinant of the night's price, and the solver must find it on
the chart. It is the same kind of factor as the step band the audit already accepted. So the fourth
factor is loss_night_category (parameter: categories 1-8 -> that category's standard-season price; the
baseline and fall-through are the category-4 price, stated as "Unless the award category recorded on the
cancelled reservation sets another price, the late-cancellation loss value is the category-4
standard-season price of the award chart"). This mirrors the accepted middle-band step default.
The timing factor is removed entirely.

### Round-4 closure list
- R3-F2: loss_cancellation_timing removed (no resale tier). New fourth factor loss_night_category
  (parameter). P1 is now 3 parameter factors (category, season, step band) + 1 method (share). The step band
  reads its own category binding (`lv_band_cat`), so each binding belongs to one factor. Task 0: category 7
  -> 60,000; category baseline gives 5,000. The value stays 40,000; all-baseline is 25,000.
  Near-miss unchanged (74340918 top-off and return).
- R3-F1: the arrival-date "whole night, top-off included" tier is gone. The rule now reads consistently
  with base certificate_forfeiture "Top-off points added to a forfeited award are lost with it": the loss
  value is the award's share apart from the top-off, "which are lost with the award and recorded on the
  loss entry as its top-off". This matches what forfeit_late_cancel_award_5a86721d writes. Nothing is
  counted twice.
- O-11: closed with the tier; no "handled as a no-show" text remains, and the loss reason stays
  cancelled_after_deadline as P1's scope says.
- Not regressed: P2-P6 compute, values and task 1 untouched; task 0 P2/P3 unchanged.
  Booking cross-category reads for P1 narrowed back to award_category and award_season.
- Files: certificate.extended.yaml (P1), tasks/0.json (computations[0], evaluation_criteria[3]/[8]
  text, design_rationale). Gates all green.

## Rework round 5 — revision_4 findings (orchestrator final decision: re-frame what P1 scores; task 1 frozen)

Why P1's factor list could not be patched:
- As framed, P1 scored a "loss value". That is a measurement written only on the loss record. Its only
  real determinants are the chart (category, season, step) and what the award covered (share, top-off).
- The base already prices the night by category and season (certificate_redemption_eligibility), so
  under an honest baseline only season (with an explicit standard-season default) and the share survive.
  That is 2 factors.
- Member-standing reliefs on a statement number were struck in round 1 (G-3 a): they change nothing the
  member owes or receives.
- The DSL also forbids any other policy reading P1's number. SUM/COUNT/LATEST are scoped to the
  computation's target holding, and X* reads only other categories.
- The tree cannot drop the forfeiture either. I checked every base gate on the return and on the
  application (status, earliest unpaid night, award cap, expiry, room, adults, season, brand, channel,
  group). None of them gives a second certificate prerequisite in this story. A swap off a confirmed
  reservation is barred by base release; extensions and reissues are barred for guest cancellations.
  So the late-cancel tree must stay forfeit -> return -> apply.

Redesign (P1's quantity re-framed so that it has a consequence; tree depth and edges unchanged):
- P1 now scores the stay's protected value: the points value at which the late-cancelled stay stays
  protected. It is set from what the forfeited award carried for the night, apart from the top-off,
  which is lost with the award per base certificate_forfeiture.
  - Honest baseline: the chart's standard-season price for the recorded category. The chart is named
    and nothing is resolved by an "unless" clause.
  - Factors: season (parameter; standard default); award share (method; this reservation's net top-off,
    with the 74340918 near-miss kept); stay length, i.e. nights booked on the cancelled reservation
    (parameter; same kind as the walked-stay length the audit accepted); stay night credits in the last
    twelve months, card credits excluded (parameter; same kind as the stays extra of P5).
  - Category and step band are plumbing again; the step is "the gap between neighbouring seasons on the
    award chart".
- P2 consumes it. The fall-through timing tier (a resort late cancellation two or more days out) now
  protects the returned night at the stay's protected value read from the first-night award's loss
  record, instead of the night's chart price. P2's baseline.rule states exactly that.
  - To read that record, P2's computation is scoped to the first-night award dc3f7067. It is the same
    cancelled reservation, and P6 already uses a target holding other than the written award.
  - The read sits inside the fall-through branch, so the day-before gold path is unchanged: P2 stays
    62,500 and P3 stays 58,250.
- Task 0 values:
  - P1: 50,000 off-peak; share 40,000; -1,000 (2 nights) and -2,000 (47 stay credits) = 37,000.
    Substitutions: 47,000 / 47,000 / 38,000 / 39,000; all-baseline 60,000.
  - P2: 62,500; timing baseline 29,500; all-baseline 37,000.
  - P3: unchanged.
- Seed consistency (base certificate_issuance): task 0's member reached 50 elite night credits on
  2026-07-10, so I added the 2026 milestone 40K award FNA64273851 (issued 2026-07-13, unused).
  - Observation, not acted on per the orchestrator: task 1's member (71 credits in 2026) has the same gap.
    I did not touch task 1.
- Task 1: world, P4-P6 text and GT untouched. P4-P6 re-evaluate to 34,000 / 2028-04-30 / 28,500. The
  bytes of 1.json differ only because replay_tasks rewrites db_closure in set order; the content hash
  without db_closure is stable.

### Round-5 closure list
- R4-F1 (P1 category factor vs. an honest baseline): category is no longer a factor. The baseline names
  the chart and prices by the recorded category; P1 now scores the stay's protected value.
  Files: certificate.extended.yaml (P1), tasks/0.json.
- R4-F2 (P1 step band vs. an honest baseline): step band is no longer a factor. The step is chart
  plumbing, stated once, with no "unless" default. Same files.
- P1 floor: 4 real factors (season, share, stay length, stay nights; 3 parameter + 1 method), each
  load-bearing against the honest baseline.
- P2 text changed: fall-through tier, baseline.rule, compute/history read.
  task_tools.py: forfeit docstring now names the stay's protected value.
