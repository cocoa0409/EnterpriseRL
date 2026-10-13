# Policy-task audit — respite_and_trial_stays / charter-global

## charter_global_frozen

- Round: 1. Auditor: independent erl-task-policy-audit run (not the authoring agent). Freeze time: 2026-10-05T09:04:35Z (UTC wall clock of the audit host).
- Frozen inputs (sha256, recomputed by the auditor and equal to the coordinator's MANIFEST and to the originals under `tasks/respite_and_trial_stays/`):
  - `respite.extended.yaml` 5f8151821b3394633d4857724f2d3510049129bc75f1bacc8bb9d57387b94032
  - `task_tools.py` 533ef723545183f085475fc3f0d6ffea8b6702947fc2caa882fda9e217b822a3
- Base section check: lines 1-1121 of `respite.extended.yaml` are byte-identical to `blueprint/products/respite.yaml` (diff shows only the trailing blank line) — the base copy is verbatim.
- Read for this section: `blueprint/` (blueprint.yaml, products/respite.yaml, products/entrance.yaml variant parameters, products/independent.yaml returned_payment_fee, share_tools.py), the view directory `audits/_views/policy_task/respite_and_trial_stays/` (extended charter, task_tools.py, MANIFEST).
- Masked and not read when this section was written: `tasks/respite_and_trial_stays/tasks/*.json`, `tasks/respite_and_trial_stays/worklog.md`, every `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`. This section contains nothing derived from a revealed GT.
- Entry conditions (Step 0): gate snapshot supplied in the brief (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred because the KB is not yet published); masked views and hashes supplied. Entry conditions met; the deferred traceability gate is noted, not counted as a defect of this audit.

### policy_conflict_scan

Extended policies (6): `respite_ext_relevel_credit` (respite_credit / credit_amount / `credit_relevel_nights_cb1c5023`), `respite_ext_relevel_segment` (respite_nightly_charge / segment_amount / `charge_relevel_segment_3be81426`), `respite_ext_signed_extension` (respite_extension + respite_nightly_charge / extension_charge / `sign_stay_extension_37758bab`, owner=user), `respite_ext_returned_payment_fee` (respite_addon_charge / fee_amount / `post_returned_payment_fee_57d4cb7a`), `respite_ext_medication_setup` (respite_addon_charge / setup_amount / `post_medication_setup_fee_0971281c`), `respite_ext_advance_payment` (respite_payment / amount / `pay_stay_advance_b4214d09`, owner=user).

Overlapping subjects and how they separate:
- respite_credit: relevel_credit (reason level_change_adjustment) vs base cancellation (cancellation_reversal), stay_billing (early_departure), billing_corrections (billing_error). Distinct credit reasons; no shared quantity.
- respite_nightly_charge: relevel_segment (basis level_change), signed_extension (basis extension on a signed request), base booking_terms (planned_stay), base stay_billing overstay (extension at nightly_rate_locked, "without an extension"). The overstay clause is a different trigger (no request); no overlap with a signed extension.
- respite_addon_charge: returned_payment_fee (addon_code returned_payment) vs medication_setup (addon_code medication_setup) vs base addons (other codes). Disjoint codes.
- respite_payment: advance_payment vs base payments_and_refunds/prepayment. Base check-in floor ("Check-in is allowed only when respite_msr_paid_before_arrival is at least the minimum-stay charge.") is not overwritten and stays a floor; the advance (which exceeds or equals it in ordinary cases) is the amount the extended rule says is paid "Before a booked stay begins". No conflict in conclusion; see observation O5.
- Triggers / time anchors: extension cutoff, annual-nights limit, max extensions, max stay, in_stay-only level change, booked-only advance ("Before a booked stay begins") all inherited unchanged.
- Cross-category read boundaries: all reads are of the customer's own `independent_residencies` (status, move_in_date, community_name, account_balance), `independent_ledger` (independent_payment_return within 12 months) and `entrance_agreements` (status) plus the entrance plan's variant parameters contract_type / care_fee_discount_pct / rent_discount_pct (blueprint/products/entrance.yaml: LifeChoice plans fee_for_service 10/10, LifeCare plans lifecare 100/25). Each read is declared in that policy's `cross_category`.

Scope partition (derived from the `prerequisite` graph only; the masked `charter_scope` is compared after reveal in the task files): tree A = {signed_extension <- relevel_segment <- relevel_credit}; tree B = {advance_payment <- returned_payment_fee, advance_payment <- medication_setup}. The two trees share no policy and together cover all six extended policies, so two tasks of one tree each are mutually exclusive and jointly complete.

No conflict found that yields two conclusions in one situation except F1 and F2 below.

### rule_compute_equivalence

Sweep of every binding of every extended policy against its `compute_basis` and the rule; each binding below was matched to a verbatim rule sentence and back.

- relevel_credit: seg_end / night_price / new_rate / review_gap / band_excess (`F('care_points') - (P('care_points_min') - 1)` equals "exceed the highest score of the band below the new stay type" because the AL respite bands are contiguous 0-25 / 26-50 / 51-75) / il_tenure / review_window / band_tolerance / absorbed_nights / relevel_nights (arrival tier `DAYS(check_in, seg_end) + 1 - absorbed`, lower-rate tier `DAYS(eff, seg_end)` = "from the night after ... both counted", default `DAYS(eff, seg_end) + 1`) / result (one rounding, half up) — all equivalent. **Exception F2**: `seg_amount` / `seg_nights` are `SUM(... segment_end_date=seg_end)` over every nightly charge sharing the latest end date, while the rule says "that segment's amount divided by its nights".
- relevel_segment: relevel_nights (latest level_change_adjustment credit nights), booked_rate, care_increase, seg_last, post_nights, pre_nights (`MX(...,0)`; the floor is carried by "the re-leveled nights that fall before the level effective date", which can never be negative), pre_share 1/2 / 3/4 / 1, plan_cover_pct, campus_pct, loyalty_pct, standing_pct, billed_relevel_nights (`n - n//7` / `n - 1` / `n`), increase_nights (`billed - pre*(1-share)`), increase_billed (sequential reductions), result (one rounding) — equivalent both ways.
- signed_extension: req_date / req_registered (latest pending stay_extension request), added_nights, added_night_rate three tiers, care_increase, cover then campus on the care increase, billed_added_nights, notice_days / surcharge (<=3 -> 15, 4-7 -> 8, else 0), loyalty on the night charges only, surcharge on all added nights, one rounding — equivalent.
- returned_payment_fee: statutory_fee (FL tiers 25 / 30 / max(40, 5% rounded), TX 30, NC 25, else stay type fee), courtesy_pct (XCOUNT independent_payment_return within 12 months), lp_courtesy_pct, item_charge (latest stay payment instrument), handling (<=7 -> 10, 8-14 -> 5), result — equivalent. Observation O3 on `ret_amount` summing by posting date.
- medication_setup: planned_nights, packaging (`ceil(n/14) * 60` / 55 / fee), lp_discount_pct, profile_pct, early_pct, rush, result — equivalent.
- advance_payment: advance_nights, receipts three methods, relief_pct (rent_discount_pct), deferral_pct, early_pct, il_balance / standing_pct, fees_returned / fees_setup / fees_other ("every add-on and fee posted on the stay", cancellation fees included), result (floor 0, one rounding) — equivalent.
- Every factor's ladder: each tier named in `factors[].ladder` is a rule sentence and a branch of its `decides` binding, and each branch is a stated tier (checked for all 32 factors). No tier lives only in compute.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are six distinct pairs, one per policy; no tool is claimed twice.
- Docstrings: none names another tool, none states a position in a sequence among this difficulty's writes. The only ordering word is in `charge_relevel_segment_3be81426`: "charged at a care level after a level change" — it refers to the base level-change event already on the stay record, not to any write of this difficulty (observation O1).
- Tool bodies: each body reads the stay row, creates one ledger row from the supplied arguments and adjusts `account_balance`; `sign_stay_extension_37758bab` additionally marks the request signed, moves `planned_departure_date` and `extensions_count`. No body checks a policy condition, refuses, errors or hints on an unresolved prerequisite.
- uuid8 tails: cb1c5023, 3be81426, 37758bab, 57d4cb7a, 0971281c, b4214d09 — pairwise distinct, no shared prefix, no arithmetic progression, no common stem with a changed tail. Pass.

### prerequisite_graph

| blocked policy | problem | kind | gate (binding exists?) | form | resolved_by = depended-on target_tool? |
| --- | --- | --- | --- | --- | --- |
| relevel_segment | relevel_credit | value_input | relevel_nights (yes) | state | credit_relevel_nights_cb1c5023 (yes) |
| signed_extension | relevel_segment | value_input | added_night_rate (yes) | state | charge_relevel_segment_3be81426 (yes) |
| advance_payment | returned_payment_fee | value_input | fees_returned (yes) | state | post_returned_payment_fee_57d4cb7a (yes) |
| advance_payment | medication_setup | value_input | fees_setup (yes) | state | post_medication_setup_fee_0971281c (yes) |

- `prerequisite` is filled on all six policies (`[]` on relevel_credit, returned_payment_fee, medication_setup). Every `problem` is an extended policy id of this file, none a base policy, none self. Graph: extension -> segment -> credit; advance -> fee; advance -> setup — acyclic.
- Every `policy_source` is verbatim in its own policy's `rule` (extended yaml lines 1313, 1531, 2076, 2077).
- No action-form edge, so no `fallback_reason` is required or present.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field.
- `condition` vs sentence: edges 1, 3, 4 state the same check at the same strength. **Edge 2 is narrower than its sentence — F1.**
- `effect`: each named binding is genuinely moved by the resolving write (relevel_nights reads the credit's nights; added_night_rate switches on a level_change latest segment; fees_returned / fees_setup sum the posted add-ons).

### prerequisite_sentences

Four-point test per edge:

1. segment <- credit: "A level-change segment is fixed only after the stay's records carry a level-change adjustment credit for the nights being re-leveled." — ordering connective "only after"; record-visible state (a credit with reason level-change adjustment on the stay ledger); no tool, policy id, snake_case token or row id; strength equals condition. Writes of this difficulty that create a level_change_adjustment credit: only `credit_relevel_nights_cb1c5023` (share tools write only verification / handoff). Derivation: sentence -> look for the rule that posts a level-change adjustment credit -> relevel_credit's rule ("the level-change credit is posted against the segment being re-leveled") -> its tool. Single reading. Pass.
2. extension <- segment: "Where the stay type on record differs from the stay type the stay was booked as, added nights are not booked until the stay's records carry a level-change segment billing the stay type on record." — "not ... until"; record-visible state (a level-change nightly charge segment whose stay type billed equals the stay record's type); clean of names. Only `charge_relevel_segment_3be81426` writes basis level_change. Derivation: stay type on record vs booked type (planned_stay segment's tier_billed / nightly_rate_locked) -> rule that charges a level-change segment -> relevel_segment. Single reading of the action; but the sentence's state is existence while the declared `condition` is "latest nightly charge is a level_change segment" — F1.
3. advance <- fee: "The advance is fixed only after the stay's records carry a returned-payment fee for every returned payment on the stay." — "only after"; record-visible; clean; one writer. Pass.
4. advance <- setup: "The advance is not worked out until the stay carries its medication setup charge whenever the stay type includes medication administration and the physician's report is on file." — "not ... until"; record-visible, conditioned exactly as `condition`; clean; one writer. Pass.

- Depended-on rules do not restate the sentences (relevel_credit, returned_payment_fee and medication_setup rules never mention the blocked policy).
- Value-binding sentences in the blocked rules ("The re-leveled nights of the segment are the nights of that level-change adjustment credit", the added-night-rate tier sentence, "plus every add-on and fee posted on the stay") are the value_input bindings, not second wordings of the dependency.
- No extended rule states a cross-problem order that grounds no declared edge. Orders stated against non-problems: medication_setup "once the physician's report for the stay is on file" (health-documents record, no write of this difficulty), advance "Before a booked stay begins" (check-in, no write of this difficulty), relevel_credit "the stay record already shows the new stay type" (base level-change record). None is a problem of this charter.
- No base rule sentence grounds an edge.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- relevel_credit:
  - level_change_rules S1 (bands from latest assessment) follows; S2 "the stay type changes from the assessment date: the remaining nights of the current segment are credited ..." — both clauses named in `overwrite` (two entries). The lower-rate tier ("from the night after the level effective date") also departs from "the stay type changes from the assessment date", which is named as superseded, but `replaced_by` quotes only the arrival-review sentence (observation O2); merged semantics remain unique because the extended rule states all three tiers. S3 (only between the three AL types, only in_stay) follows; S4 (trial stay no change) follows.
  - stay_billing_and_extension, cancellation, billing_corrections: govern other credit reasons; follow.
- relevel_segment: level_change_rules S2 last clause ("the same nights are charged ... at the new level's nightly_rate published on the booking date") named and replaced. booking_terms "nightly_rate_locked ... applies to every night of the stay, extensions included" is not named; the segment frames its charge as the locked rate on every night plus a care increase, and base itself already priced re-leveled nights by level_change_rules S2 (specific) rather than booking_terms (general), so no defensible second reading arises (observation O4). stay_billing follows.
- signed_extension: stay_billing S1 named and replaced; booking_terms "applies to every night of the stay, extensions included" named and replaced; stay_billing cutoff / count / max nights / open-status sentences, annual-nights limit and level_change_rules follow.
- returned_payment_fee: addons "a returned payment carries returned_payment_fee referencing it" named and replaced; rest of addons follows.
- medication_setup: addons "medication_setup_fee once per stay where medication_administration_included is true" named and replaced; rest follows.
- advance_payment: prepayment_and_check_in S1 named and replaced; check-in floor, health documents, nurse assessment and payment-status sentences follow; payments_and_refunds follows. The superseded S1 was the prose definition of "the minimum-stay charge" that S2 still uses; the base `formula.minimum_stay_charge` keeps it defined (observation O5).
- Disguised forms: no anonymous intermediate override, no 0/1 multiplier, no dropped base branch found. No author note in the charter calls a base output a "wrong value".

### factor_ladders

| policy | factor | label | decides | tiers | multi-source tier(s) | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| relevel_credit | relevel_start | method | relevel_nights | 3 | tier 1 (stay type rate, ledger segment price, stay dates/points, IL, EFA) | - |
| relevel_credit | arrival_review_window | parameter | review_window | 3 | IL status + IL move-in (one residency row) | independent |
| relevel_credit | band_tolerance | parameter | band_tolerance | 3 | EFA status + plan contract type | entrance |
| relevel_credit | screened_nights_absorbed | parameter | absorbed_nights | 3 | IL row + stay row (distinct records) | independent |
| relevel_segment | pre_assessment_share | parameter | pre_share | 3 | - | - |
| relevel_segment | life_plan_care_cover | parameter | plan_cover_pct | 3 | EFA + plan | entrance |
| relevel_segment | on_campus_courtesy | parameter | campus_pct | 3 | IL row + stay row | independent |
| relevel_segment | residency_loyalty | parameter | loyalty_pct | 3 | - | independent |
| relevel_segment | account_standing | parameter | standing_pct | 3 | payment rows + return rows | - |
| relevel_segment | weekly_increase_nights | method | billed_relevel_nights | 3 | - | - |
| signed_extension | added_night_rate_source | parameter | added_night_rate | 3 | latest segment + level-change segment rows | - |
| signed_extension | added_night_care_cover | parameter | plan_cover_pct | 3 | EFA + plan | entrance |
| signed_extension | added_night_campus_courtesy | parameter | campus_pct | 3 | IL row + stay row | independent |
| signed_extension | billed_added_nights | method | billed_added_nights | 3 | - | - |
| signed_extension | short_notice_surcharge | parameter | surcharge | 3 | request row + stay row | - |
| signed_extension | added_night_loyalty | parameter | loyalty_pct | 3 | - | independent |
| returned_payment_fee | statutory_service_charge | method | statutory_fee | 4 | - | - |
| returned_payment_fee | resident_first_return_courtesy | parameter | courtesy_pct | 3 | IL row + IL ledger rows | independent |
| returned_payment_fee | life_plan_return_courtesy | parameter | lp_courtesy_pct | 3 | EFA + plan | entrance |
| returned_payment_fee | bank_return_item_charge | parameter | item_charge | 3 | - | - |
| returned_payment_fee | pre_arrival_handling | parameter | handling | 3 | return row + stay row | - |
| medication_setup | packaging_method | method | packaging | 3 | - | - |
| medication_setup | life_plan_setup_discount | parameter | lp_discount_pct | 3 | EFA + plan | entrance |
| medication_setup | pharmacy_profile_reduction | parameter | profile_pct | 3 | - | independent |
| medication_setup | early_booking_reduction | parameter | early_pct | 3 | - | - |
| medication_setup | rush_packaging | parameter | rush | 3 | health-doc date + stay arrival | - |
| advance_payment | advance_nights | parameter | advance_nights | 3 | stay return rows + stay dates / IL ledger | independent |
| advance_payment | receipts_counted | method | receipts | 3 | - | - |
| advance_payment | life_plan_advance_relief | parameter | relief_pct | 3 | EFA + plan | entrance |
| advance_payment | residency_deferral | parameter | deferral_pct | 3 | - | independent |
| advance_payment | early_booking_relief | parameter | early_pct | 3 | - | - |
| advance_payment | account_standing_relief | parameter | standing_pct | 3 | IL balance + IL ledger rows | independent |

Counts per policy (factors / parameter / method): relevel_credit 4/3/1; relevel_segment 6/5/1; signed_extension 6/5/1; returned_payment_fee 5/4/1; medication_setup 5/4/1; advance_payment 6/5/1. All within 4-6 with >=2 parameter and >=1 method. Every tree carries multi-source and cross-difficulty factors (tree A: screened_nights_absorbed, on_campus_courtesy; tree B: advance_nights, account_standing_relief; cross categories independent and entrance in both trees).

- `decides` is an input binding (never `result`) for all 32 rows; binding sets are disjoint within each policy.
- Every fall-through equals the factor's `baseline`, and every `baseline` equals what that policy's `baseline.rule` states for that input (standard method: effective-date count; full care increase; locked added-night rate; stay type fee; stay type setup fee; minimum stay and payments less returns; every courtesy / relief / surcharge absent).
- Each `baseline.rule` is self-sufficient and every sentence of it is a sentence of the policy's `rule`; `baseline.params` (nightly_rate / returned_payment_fee / medication_setup_fee / minimum_stay_nights) are the parameters it uses.
- No two tiers of one ladder select the same value or method. Label honesty: the method ladders each contain at least one tier that changes the algorithm (arrival-review recount; proportional weekly reduction; Florida amount-tiered statute; fourteen-night cycles; guaranteed-funds-only receipts), while some of their other tiers differ from one another only by a constant (observation O6). The parameter ladders change numbers only.
- Industry realism: statutory returned-check charges (Florida 25/30/max(40, 5%), Texas 30, North Carolina 25), bank item pass-through, rush pharmacy packaging, cycle packaging, early-booking discounts, full prepayment and guaranteed funds after a bounced payment, Life Plan discounts and resident courtesies are recognisable practices. Observation O7 notes the weakest conditions (arrival-review window keyed on independent living tenure; band tolerance keyed on the Life Plan contract type; payment-count courtesy); none is a condition that holds of every customer reaching the write, and none could be demonstrated to be something no operator weighs, so none is a red light.

### findings

**F1 — SOURCE-POLICY RED (charter-global; bears on task 0's tree, no consequence on task 0's scored values).**
- Symptom: the declared `condition` of the edge signed_extension -> relevel_segment is narrower than its prerequisite sentence.
- Evidence: sentence (extended yaml line 1531 / 1549): "added nights are not booked until the stay's records carry a level-change segment billing the stay type on record." `condition` (line 1550-1551): "The stay's latest respite_nightly_charge entry is a level_change segment whose tier billed equals the stay type on record."
- Demonstrated consequence: a stay re-leveled from Standard to Enhanced (credit + level-change segment posted) and then extended once (`sign_stay_extension_37758bab` posts an extension segment with tier_billed = Enhanced, now the latest nightly charge), and a second extension request is registered. Sentence: the records carry a level-change segment billing the stay type on record -> no prerequisite, book the added nights. Declared condition: the latest nightly charge is an extension, not a level_change segment -> prerequisite unmet, resolved_by `charge_relevel_segment_3be81426`. Two different problem trees and write sequences in one situation.
- Root cause: the condition copies the first tier of the added-night-rate selection ("where that segment is a level-change segment and ...") instead of the gate sentence.
- Affected: `respite_ext_signed_extension.prerequisite[0].condition`. Task 0 cites this; in task 0's world both readings coincide (see 0.md).

**F2 — SOURCE-POLICY RED (charter-global; no consequence on task 0's scored values).**
- Symptom: compute of `respite_ext_relevel_credit` prices the segment from every nightly charge sharing the latest end date, not from "that segment".
- Evidence: rule (line 1154): "The price charged per night by the segment being re-leveled is that segment's amount divided by its nights." Compute (lines 1176-1177): `seg_amount: SUM('respite_ledger','amount', event_type='respite_nightly_charge', segment_end_date=seg_end)`, `seg_nights: SUM(... 'nights' ..., segment_end_date=seg_end)`.
- Demonstrated consequence: a stay re-leveled once (planned_stay 14 nights 3346.00 ending 10-07 and a level-change segment 14 nights 3730.03 ending 10-07) that is re-leveled a second time while in_stay (base level_change_rules S3 allows any change between the three AL types while in_stay). Rule: latest segment = the level-change segment, price 3730.03 / 14 = 266.43. Compute: (3346.00 + 3730.03) / 28 = 252.72. Different credit for the same nights.
- Root cause: the latest segment is identified by its end date, and two segments can share one.
- Affected: `respite_ext_relevel_credit.compute.seg_amount / seg_nights`. In task 0's world only one nightly charge exists at the credit's handling time, so the scored credit is unaffected.

Observations (no demonstrated consequence; not grounds for rework):
- O1: `charge_relevel_segment_3be81426` docstring contains "after a level change"; it orders against the base level-change record, names no tool and states no sequence among this difficulty's writes.
- O2: relevel_credit's second `overwrite` names the superseded clause "the stay type changes from the assessment date" but its `replaced_by` quotes only the arrival-review sentence, while the lower-rate tier ("from the night after the level effective date") also departs from it.
- O3: returned_payment_fee `ret_amount` sums every returned-payment entry posted on the latest return date; the rule says "the amount of the stay's latest returned-payment entry". The two differ only if two returns post on one date, where the rule itself does not single out one entry.
- O4: relevel_segment does not name booking_terms "applies to every night of the stay, extensions included" in `overwrite` while signed_extension does for the analogous rate change; base already prices re-leveled nights by level_change_rules S2, so no second defensible reading was found.
- O5: the superseded prepayment sentence was the prose definition of "the minimum-stay charge" that the inherited check-in sentence still uses; `formula.minimum_stay_charge` keeps it defined.
- O6: in several method ladders two tiers differ only by a constant (weekly_increase_nights / billed_added_nights: "one night not billed" vs "every night billed"; statutory_service_charge: Texas 30 / North Carolina 25 / stay-type fee; packaging_method: short pack 55 / stay-type fee 85). Each ladder still has a genuinely algorithmic tier and no two tiers share an outcome.
- O7: weakest real-world conditions: arrival_review_window keyed on independent living tenure, band_tolerance keyed on the Life Plan contract type, account_standing rewarding two payments over one. Recorded as a realism observation only.

## closing_checklist

Written after both reveals (2026-10-05T09:07:41Z onward). Everything above this heading was frozen before any task JSON was opened (sha256 of this file at freeze: ab672ceee9e30104e7681d86aff0b99628774358976e2d328cb932a4e3d155e2, one in-place count correction "26 -> 32 factors" made before the freeze hash).

The difficulty is **not closed**: not every task passes all four relationships.

| item | status |
| --- | --- |
| one audit file per task (0.md, 1.md) plus this file; round 1, no older revision | done |
| every comparison section carries PASS | no — 0.md: SOURCE-POLICY RED (charter F1/F2, no consequence on its GT) + SOURCE-FACTOR RED (T0-F1); 1.md: SOURCE-FACTOR RED (T1-F1) |
| extended policies fully covered; scopes pairwise disjoint | yes — revealed `charter_scope`: task 0 = {relevel_credit, relevel_segment, signed_extension}, task 1 = {returned_payment_fee, medication_setup, advance_payment}; same as the partition derived blind in § policy_conflict_scan |
| task tools and GT closed; uuid8s independent | yes (§ action_binding_and_uuids; each task's GT uses only its own three task tools) |
| each tree: 1-3 prerequisite problems, >= max(n-1,1) value_input edges, an owner=user write, acyclic; whole-difficulty graph acyclic | yes (n = 2, 2 value_input edges, user root, in both trees; the two trees share no node) |
| every computation: self-sufficient baseline, 4-6 factors (>= 2 parameter, >= 1 method), every factor bears weight against an honest baseline, whole baseline differs from gold | yes for all six computations (figures in 0.md / 1.md § factor_weight, matching GT) |
| near-miss per computation | no — present only in the extension (task 0) and the advance (task 1); T0-F1, T1-F1 |
| charter self-consistency | no — F1, F2 (charter-global SOURCE-POLICY RED) |
| blind derivation lands on GT | yes — every write, argument, owner, order and scored value of both tasks matched exactly |
| instantiation gates re-run on the final form | not run by this audit (the skill has the auditor cite, not run, gates); the round-1 snapshot in the brief is all green |

## revision_2

### charter_global_frozen (round 2)

- Round 2 re-audit, same independent auditor as round 1. Written 2026-10-05T09:55Z (UTC host clock), before any round-2 task JSON was opened. Nothing in this section is derived from a round-2 GT.
- Shared inputs changed, so the charter-global sections are re-derived, not carried forward: `respite.extended.yaml` 5f815182... -> 6ba8798e9e21c5c4057626919c0ccb021bcfc59385a2214ce6a1f7e09f237faf; `task_tools.py` 533ef723... -> dd586f0093890d2188a92d40c539ea2a5356cf66a141db6e780481b004939131. Both recomputed by the auditor, equal to the coordinator's MANIFEST and to the originals under `tasks/respite_and_trial_stays/`.
- Base section: lines 1-1121 still byte-identical to `blueprint/products/respite.yaml` (diff shows only the trailing blank line).
- contamination_disclosure: the auditor read the round-1 task JSONs (GT, design_rationale, closures) during round 1. The round-2 charter-global checks rest on the charter, schema and tool contracts only, but the auditor is not naive to the round-1 design.
- Entry conditions: the round-2 gate snapshot in the coordinator message is all green (traceability deferred, KB not published); rebuilt masked views with hashes supplied. Met.

### what changed in the charter and tools (located by re-reading every extended policy against the round-1 text)

1. relevel_credit: new rule sentence "The segment being re-leveled is the one nightly charge entry with the basis, the first night and the stay type billed of that latest nightly charge segment, so a segment that merely ends on the same night is never part of it."; compute adds `seg_basis`, `seg_start`, `seg_tier` (LATEST of the latest nightly charge) and `seg_amount` / `seg_nights` now SUM over `charge_basis=seg_basis, segment_start_date=seg_start, tier_billed=seg_tier`; three new compute_basis entries quote the new sentence. The second `overwrite` now quotes the lower-rate sentence in `replaced_by` as well.
2. relevel_segment: new `overwrite` naming booking_terms "applies to every night of the stay, extensions included", replaced by "The level-change segment charges every re-leveled night at the nightly rate locked at booking and adds the care increase billed for the re-leveled nights."
3. signed_extension: `prerequisite[0].condition` now reads "Where the stay type on record differs from the tier billed by the stay's planned_stay segment, the stay ledger carries at least one respite_nightly_charge entry with charge_basis level_change whose tier billed equals the stay type on record."
4. `charge_relevel_segment_3be81426` docstring: "charged at a care level after a level change" -> "charged at the care level a level change placed the guest in".
5. No other change found. The rules, computes, factors, baselines and prerequisites of returned_payment_fee, medication_setup and advance_payment are the round-1 text; the line count grows by exactly the lines of items 1-2 (2271 -> 2284).

### round-1 charter findings — closure check

- **F1 closed.** Sentence: "added nights are not booked until the stay's records carry a level-change segment billing the stay type on record." Condition: "... the stay ledger carries at least one respite_nightly_charge entry with charge_basis level_change whose tier billed equals the stay type on record", gated by the same "stay type on record differs from the booked type" clause. Both are existence conditions of the same strength. Re-run of the round-1 situation (re-level, one extension, then a second extension request): sentence met, condition met; one tree.
- **F2 closed.** Re-run of the round-1 situation (planned_stay 14 nights 3346.00 ending 10-07, a level-change segment 14 nights 3730.03 ending 10-07, then a second re-level): latest nightly charge = the level_change segment (basis level_change, start 2026-09-24, tier Enhanced); SUM over that basis+start+tier = 3730.03 / 14 = 266.43 = the rule's "that segment's amount divided by its nights". The planned_stay row (basis planned_stay) is excluded. Collision check: two nightly charge rows sharing basis, first night and tier would need two level-change segments re-leveling to the same tier from the same first night. A second arrival review changes the tier, and a lower-rate re-level starts the night after a later effective date, so no reachable world was found where they collide. Rule and compute agree.
- Rule/compute equivalence of the new bindings: `seg_basis` / `seg_start` / `seg_tier` each quote the new sentence. All four LATEST calls share filter and date field, so a posting-date tie resolves to the same row in each.

### re-derived charter-global checks (round 2)

- policy_conflict_scan: unchanged conclusions from round 1 § policy_conflict_scan; scope partition (tree A = credit, segment, extension; tree B = fee, setup, advance) unchanged. New point: both relevel_segment and signed_extension now supersede the same booking_terms clause "applies to every night of the stay, extensions included", each with its own `replaced_by`. Their subjects are disjoint (re-leveled nights vs added nights). The base overstay sentence ("charged the extra nights as an extension segment at nightly_rate_locked") and the planned-stay sentence keep the locked rate for every other night, so the merged semantics stay unique (observation O8).
- rule_compute_equivalence: re-checked for the changed policy (above); the other five are textually unchanged from round 1, so the round-1 sweep holds.
- action_binding_and_uuids: six distinct `(target_tool, computes)` pairs; uuid8s unchanged and independent. Docstrings: the only remaining words from the ordering list are "first and last night" / "first night of the segment" (nouns naming a date field). No docstring names another tool or a sequence. Tool bodies unchanged apart from the docstring and still check nothing.
- prerequisite_graph: same four state-form value_input edges, same gates, same resolvers, acyclic. Edge 2's condition now matches its sentence (F1 closed); edges 1, 3, 4 unchanged and matching.
- prerequisite_sentences: all four `policy_source` sentences unchanged and verbatim in their rules; four-point test as in round 1; one writer per waited-on state.
- override_declarations: O2 closed (lower-rate tier now quoted in `replaced_by`); O4 closed (segment names the booking_terms clause). No new undeclared override found.
- factor_ladders: factor declarations unchanged (32 factors; per-policy counts as round 1). Round-1 observations O6 and O7 still stand.

### findings (round 2, charter-global)

- F1: closed. F2: closed. O1, O2, O4: closed.
- O3, O5, O6, O7: still stand as observations (unchanged text). The reworker kept them with reasons; none had a demonstrated consequence.
- O8 (new, observation): two policies supersede the same base clause with different replacements. Their scopes are disjoint, so no second reading results.
- No new charter-global red light.

### closing_checklist (round 2)

Written after both round-2 reveals. Not closed: task 1 carries a new red light.

| item | status |
| --- | --- |
| per-task files with revision_2 appended, round-1 text untouched | done |
| every comparison PASS | no — 0.md round 2: PASS on all four; 1.md round 2: SOURCE-FACTOR RED (T1-R2-F1, seeded rescinded Entrance Fee Agreement outside the Harbor View rescission period) |
| round-1 REDs closed | F1, F2, T0-F1 closed; T1-F1 closed on the score side but its fix introduced T1-R2-F1 |
| extended policies covered, scopes disjoint | yes (`charter_scope` unchanged: task 0 = tree A, task 1 = tree B) |
| task tools / GT closed; uuid8s independent | yes |
| trees: n = 2, 2 value_input edges, user root, acyclic | yes, both tasks |
| factors: counts, weight against honest baselines, whole baseline != gold, near-miss per computation | yes for all six computations |
| seeded cross-difficulty rows consistent with their charters | no — T1-R2-F1 |
| blind derivation lands on GT | yes, both tasks, every write and value (round-2 derivation discloses prior round-1 GT exposure) |
| no regression | none found: all scored values, trees and factor figures equal round 1 |
| gates on final form | round-2 snapshot from the coordinator all green (traceability deferred); not re-run by the auditor |

## revision_3

### charter_global (round 3) — carried forward

- `respite.extended.yaml` 6ba8798e9e21c5c4057626919c0ccb021bcfc59385a2214ce6a1f7e09f237faf and `task_tools.py` dd586f0093890d2188a92d40c539ea2a5356cf66a141db6e780481b004939131 were recomputed by the auditor. Both are equal to the round-2 hashes and to the originals under `tasks/respite_and_trial_stays/`. Every charter-global section of § revision_2 is therefore carried forward by reference, not re-derived: F1 and F2 closed, O1/O2/O4 closed, O3/O5/O6/O7/O8 still observations, no charter-global red light.
- contamination_disclosure: the auditor has seen the round-1 and round-2 GT of both tasks.

### closing_checklist (round 3)

Written after both round-3 reveals.

| item | status |
| --- | --- |
| per-task files with revision_3 appended; rounds 1-2 text untouched | done |
| every comparison PASS | yes — 0.md round 3 PASS on all four; 1.md round 3 PASS on all four |
| round-2 REDs closed | T1-R2-F1 closed (rescission on day 4 of the 7-day Harbor View period; refund and closing dates consistent with the entrance charter) |
| no regression | none: charter, tools and task-0 view unchanged by hash; every GT write, argument, factor figure, baseline, closure edge and order in both tasks equals round 2 |
| extended policies covered; scopes disjoint | yes (task 0 = credit, segment, extension; task 1 = fee, setup, advance) |
| task tools / GT closed; uuid8s independent | yes |
| trees: 1-3 prerequisite problems (n = 2), >= max(n-1,1) value_input edges (2), owner=user write (root), acyclic; difficulty graph acyclic | yes |
| computations: self-sufficient baseline, 4-6 factors with >= 2 parameter and >= 1 method, each factor bearing weight, whole baseline != gold, near-miss per computation, multi-source and cross-difficulty evidence seeded and charter-consistent | yes, all six computations |
| blind derivation lands on GT | yes, both tasks (rounds 2-3 disclose prior GT exposure; the round-1 derivation was blind and matched exactly) |
| instantiation gates on final form | coordinator's round-3 snapshot all green (traceability deferred until the KB is published); not re-run by the auditor |

Open observations (no rework required): O3, O5, O6, O7, O8, O-T0-1, O-T0-3, O-T0-4, O-T1-1, O-T1-3, O-T1-4, O-T1-R3-1.

**The difficulty passes the source-layer audit as of round 3.**

## revision_4

### charter_global (round 4)

- Hashes recomputed by the auditor. `respite.extended.yaml` 6ba8798e9e21c5c4057626919c0ccb021bcfc59385a2214ce6a1f7e09f237faf is unchanged, so § revision_2 policy_conflict_scan, rule_compute_equivalence, prerequisite_graph, prerequisite_sentences, override_declarations and factor_ladders are carried forward by reference. `task_tools.py` changed: dd586f00... -> ccfe2d5dbe8a8464e0b101f1413e159e89d9184a4f147957744eb67021fe3158 (equal in the view and in `tasks/respite_and_trial_stays/`). § action_binding_and_uuids is re-derived below.
- contamination_disclosure: prior GT exposure (rounds 1-3).

### action_binding_and_uuids (round 4, re-derived)

- Module imports: only `from erlbench import ToolContext, tool` (parsed with `ast`). No `datetime`, no `time`, no other real-clock source; the only date source in any body is `ctx.now()`, as before.
- Six functions with the same names, uuid8s, decorators (`owner`/`rw`) and signatures as round 2. The bodies of credit, segment, returned-payment fee, medication setup and advance payment were compared statement by statement with the round-1/2 text in this audit's record: identical. Their docstrings carry no ordering word other than the date-field nouns ("first night", "first and last night").
- `sign_stay_extension_37758bab`: the outer docstring, parameters and written fields are unchanged (request -> signed; one respite_ledger row with event_type respite_nightly_charge, charge_basis extension, tier_billed = stay variant, segment_start_date = old departure, segment_end_date = new departure - 1 day, nights = added; stay planned_departure_date, extensions_count + 1, account_balance). Only the date arithmetic changed: `date.fromisoformat` / `timedelta` became two nested pure-integer helpers, `_day_number` (civil-from-days) and `_ymd` (its inverse). Equivalence was checked by executing the two helpers as extracted from the file (no repository file written). The `_ymd(_day_number(d)) == d` round trip and the day-to-day step of 1 hold for every date from 1900-01-01 through 2099-12-31 (0 mismatches over 73,200 days, leap days included). For this difficulty's extension (old departure 2026-10-08, request 2026-10-15) they give 2026-10-08 .. 2026-10-14, 7 nights, the same as round 1-3. For an empty or malformed date both old and new code raise ValueError. Behaviour is identical.
- No body checks a policy condition, refuses or hints. The tool layer still judges no prerequisite.
- The nested helpers' docstrings are internal and are not part of the tool contract text.

### closing_checklist (round 4)

| item | status |
| --- | --- |
| revision_4 appended to all three files; earlier revisions untouched | done |
| round-3 REDs | none existed. The round-4 change (real-clock `datetime` import replaced by pure-integer date helpers in `sign_stay_extension_37758bab`) is verified: no real-clock import remains, and the behaviour is identical (0 mismatches 1900-2099; this task's segment 2026-10-08..2026-10-14, 7 nights) |
| tool contract unchanged | yes — names, uuid8s, owners, signatures, outer docstrings and written fields identical; the other five bodies are unchanged statement by statement |
| no regression | none: charter and both task views unchanged by hash; every GT write, argument, factor figure, baseline, closure edge and order equals round 3 in both tasks |
| every comparison PASS | yes — 0.md and 1.md round 4 PASS on all four relationships |
| gates on final form | coordinator's round-4 snapshot all green (traceability not yet runnable while the KB renders); not re-run by the auditor |

Open observations unchanged from round 3 (none requires rework). **The difficulty passes the source-layer audit as of round 4.**
