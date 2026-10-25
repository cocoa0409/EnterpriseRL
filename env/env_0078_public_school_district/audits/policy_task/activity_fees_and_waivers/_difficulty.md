# Policy-task audit — activity_fees_and_waivers / charter-global

## revision_1

## charter_global_frozen
- Freeze time 2026-10-24T18:15:45Z (file mtime), auditor: independent policy-task auditor (erl-task-policy-audit), coordinator brief /tmp/erl0078_coord/audit_common.txt.
- Hashes (recomputed, match the gate snapshot): activity.extended.yaml sha256 62ec6daa0c573559…, task_tools.py sha256 d3761ce488813298…; views 0.view.json 0cfc93123f48d647…, 1.view.json 6398ba87349c9fb1….
- Read for this section: blueprint/blueprint.yaml, blueprint/db_schema.json, blueprint/share_tools.py (function list and finder docstrings), blueprint/products/activity.yaml, the enroll.yaml withdrawal sentence (line 965) and the meals.yaml effective-date parameters (lines 47–111), tasks/activity_fees_and_waivers/activity.extended.yaml, task_tools.py, audits/render_source/XF_recipe.md, audits/render_source/owner_ruling.md.
- Masked and not read before the freeze: tasks/*.json (all GT fields), plan.md, worklog.md. Nothing in this section comes from a revealed GT.
- Entry conditions (step 0): gate snapshot /tmp/erl0078_coord/snap_activity_fees_and_waivers_r1.txt shows all 7 gates OK (EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING, SCOPE). Masked views come with hashes. Input complete.
- Base copy: every base key of activity.extended.yaml (category … policies) equals blueprint/products/activity.yaml (structural equality checked with a script). Verbatim.
- Mechanical sweep (scratch script, B5): every compute_basis value, every baseline.rule sentence, every prerequisite policy_source and every overwrite replaced_by is verbatim in its own policy's rule. Every superseded_clause is verbatim in the named base policy rule. Every compute binding has a compute_basis entry.

### policy_conflict_scan
Six extended policies:

| policy | subject | target_tool (owner) | trigger | prerequisite |
|---|---|---|---|---|
| activity_ext_waiver_carryback | activity_fee_credit on participation_fee | post_waiver_carryback_credit_28598765 (agent) | state_due | [] |
| activity_ext_leaving_credit | activity_withdrawal + credit on participation_fee | withdraw_activity_participant_4832a954 (user) | on_request | ← waiver_carryback (value_input, state) |
| activity_ext_trip_deposit_carryback | credit on trip_deposit | post_trip_deposit_carryback_be9ee37d (agent) | state_due | [] |
| activity_ext_trip_balance_carryback | credit on trip_balance | post_trip_balance_carryback_344bb0f3 (agent) | state_due | [] |
| activity_ext_trip_cancellation | activity_registration_cancel + credit on trip_balance | cancel_trip_registration_89918908 (user) | on_request | ← balance carry-back (vi), ← deposit carry-back (vi) |
| activity_ext_trip_deposit_release | credit on trip_deposit | post_trip_deposit_credit_5c7503cc (agent) | on_request | ← trip_cancellation (state_gate), ← deposit carry-back (vi) |

- Overlapping subjects. Three carry-backs retire the same base sentence of activity_evt_fees ("A meal status determined after a fee posted does not change that fee."). Each replaced_by names its own fee component and the siblings' components by name, and restates the in-force posting-date rule for every other fee (C2 holds). trip_cancellation and trip_deposit_release both retire two activity_refund_credits sentences. Each tail names the sibling schedule, restates full cancellation credit for non-trip types, and restates the standing trip schedule (with rounding) for cleared trips (C1/C2 hold). leaving_credit retires the window/injury sentence for every cleared withdrawal. For a cleared trip, the participation fee is 0.00 and posts nothing, so leaving_credit books nothing there and the standing trip schedule restated by the trip policies governs. No two policies credit the same (source entry, credit_reason) for the same event.
- Triggers / time anchors. The carry-backs read no clock (their computes contain no NOW), so the scored value does not depend on when they are posted. leaving_credit, trip_cancellation and trip_deposit_release read the call date (NOW / end_date).
- Cross-category read boundaries. meals.variant_name and meals.benefit_effective_date (all six policies). enroll.status/withdrawal_date (leaving_credit). enroll.entry_type/entry_date (both trip-cancellation policies). Each is declared in cross_category, and each is reachable through find_meal_accounts / find_enrollments.
- Scopes. Two tasks claim {waiver_carryback, leaving_credit} and {trip_deposit_carryback, trip_balance_carryback, trip_cancellation, trip_deposit_release}. That is pairwise disjoint and jointly complete over the six policies (agrees with SCOPE OK).
- Observation (not demonstrable on either task). A district-initiated cancellation of an unsettled, uncleared trip at the balance due date (base activity_trip_rules: "the trip is then cancelled for the student under activity_refund_credits") falls under the trip-policy replaced_by ("For a trip registration cancelled before clearance, …"). But the trip cancellation schedule's own text says "The cancellation is the family's own decision". Which schedule prices a non-family cancellation is left open.

### rule_compute_equivalence
Sentence-by-sentence sweep for every policy. The rule → compute direction holds except for the defects below. The compute → rule direction: no compute binding without a rule basis (mechanical).
- **Defect (P1).** In waiver_carryback, trip_deposit_carryback and trip_balance_carryback, the "elapsed / lead days used / days spent" sentence is framed "when the meal status took effect". Its second branch is "for a student not yet cleared [when the status took effect] … from the registration date". The computes test `not F('clearance_date')`, i.e. not cleared *now*. A registration cleared after the status took effect therefore falls to the "otherwise 0" branch in compute and to the registration-date branch in the rule. See findings P1.
- **Defect (P2).** All three carry-back rules open with "A participation fee / trip deposit / trip balance posted while the student held no qualifying meal status is carried back … only when …", and say every other fee keeps its posting-date waiver. No compute tests that condition: carryback_share / dep_share / bal_share test only the current tier and the window. See findings P2.
- **Defect (P3).** waiver_carryback subtracts only free/reduced waiver credits ("the free_meal_waiver and reduced_meal_waiver credits already posted on that fee are then subtracted"). It never subtracts a household_cap credit on the same fee. See findings P3.
- Observation. waiver_carryback.waivers_posted sums free/reduced credits over the whole participation, with no source_activity_ledger_id filter. The rule says "on that fee". Under base posting rules all components post on the registration date with the same status, so no reachable world separates the two readings. Observation only.
- Rounding (B4). Every result is RND(x + 0.000000001, 2) on a non-negative value. The rule says "rounded once, at the end, to the nearest cent with half a cent rounding up" (the point is stated). The tool bodies use the exact Decimal ROUND_HALF_UP static helper `_Cents.of`.
- Day/week conventions (B3). "calendar days from X to Y" = DAYS(X, Y). "whole weeks (calendar days divided by 7, rounded down)" = int(MX(0, DAYS)/7). Both are stated and match.
- B7. Every rule term maps to a field: benefit_effective_date ("date the current meal status took effect"), entry_date ("first day of attendance"), entry_type enum {new_to_district, returning_student, re_entry}, end_date ("cancellation date recorded"), received_date, document_date.

### action_binding_and_uuids
- Each (target_tool, computes=credit_amount) is claimed by exactly one policy (6 tools, 6 policies).
- No docstring names another tool or a sequence position. Two docstrings carry state-describing wording. cancel_trip_registration says "cancels … before clearance" and withdraw says "after the clearance date". Both are lifecycle/date conditions of the object itself, not a tool order: observation.
- uuid8s 28598765, 4832a954, be9ee37d, 344bb0f3, 89918908, 5c7503cc. They are pairwise unrelated: no shared prefix, no sequence, no copied tail.
- Tool bodies do not validate any prerequisite. No tool reads a ledger or status before writing; each only checks argument format and then ctx.create / ctx.update (B6 holds). The user tools book the credit together with the by:user transition. Under owner_ruling (a) these are accepted: the family's withdrawal of a cleared student, and the family's own cancellation of a registration.

### prerequisite_graph
Edges: waiver_carryback→leaving_credit (value_input, gate offsets_posted), trip_balance_carryback→trip_cancellation (vi, tc_bal_credits), trip_deposit_carryback→trip_cancellation (vi, tc_dep_credits), trip_cancellation→trip_deposit_release (state_gate, activity_participations.status), trip_deposit_carryback→trip_deposit_release (vi, rl_dep_credits).
- Every policy has prerequisite filled. Every problem points at an extended policy of this file, never at itself. The graph is acyclic.
- Every policy_source is verbatim in the blocked policy's own rule. form=state on all five edges; no fallback_reason (none needed).
- The gate bindings exist in the blocked compute and are the inputs the effect names. resolved_by equals the depended-on target_tool. Each "…or the schedule owes none" condition matches the rule (an open set, stated open). No authoring-viewpoint phrasing.

### prerequisite_sentences
- leaving_credit: "The credit for leaving a participation is fixed only after the participation fee carries every waiver carry-back credit owed under the fee waiver carry-back schedule." Connective "only after". Record-visible state: a free/reduced waiver credit against the participation-fee entry. No tool, id or snake_case token. Only waiver_carryback's rule books a free/reduced credit on a participation fee; the trip carry-backs are restricted by their own rules to trip_deposit/trip_balance. One reading.
- trip_cancellation: "The cancellation credit on a trip balance is fixed only after the balance carries every balance carry-back credit the trip carry-back schedule owes." and "Before the cancellation credit on a trip balance is worked out, the trip deposit must already carry each deposit carry-back credit owed on it, because family payments reach the balance only after the deposit." Each state is singled out by one rule (balance part / deposit part).
- trip_deposit_release: "A deposit release credit is not booked until the trip registration shows status withdrawn with no clearance date and its cancellation date recorded." Two tools can set status withdrawn, the cancel tool and the withdraw tool, because neither checks status. By the rules, only trip_cancellation covers a registration cancelled before clearance; leaving_credit's rule covers only "the family's withdrawal of a cleared student". One reading via the rules: observation, not RED. The second sentence ("not worked out until the trip deposit carries every deposit carry-back credit …") resolves to the deposit carry-back alone.
- No depended-on rule restates a sentence. No rule states an undeclared cross-problem order. ("Family payments … are applied to the trip deposit first and then to the trip balance" is a payment-allocation rule, not an order between problems. It fills base activity_payments_and_installments' "oldest open fee first" tie, since both post on the registration date, and does not conflict with it.)

### override_declarations
Sweep of each base_policy_refs sentence:
- activity_evt_fees. S1 posting, S2 late fee, S4 waivability, S6 due days: followed. S3 waiver on the posting date: followed for fees outside the carry-backs. S5 ("A meal status determined after a fee posted does not change that fee."): retired by three declared overwrites with scoped tails.
- activity_agg_household_fee_cap. Followed by the leaving/cancel/release nets, which subtract household_cap credits. **Not followed by waiver_carryback**: see P3 (an undeclared conflict with base event field activity_fee_credit.amount "never more than the source charge net of earlier credits").
- activity_refund_credits. S1 (net of waiver and cap credits, rounding; never on late fee or equipment): followed. S2 full cancellation: retired for trips only (declared ×2, non-trip restated). S3 cut: untouched. S4 window/injury: retired (declared, leaving_credit). S5 uniform: followed (leaving credit is on the participation fee only). S6 trip schedule: retired for pre-clearance trip cancellations (declared ×2, cleared-trip schedule restated with rounding). S7 refund by check within 30 days: inherited (not owed at once).
- activity_equipment, activity_trip_rules, activity_payments_and_installments: followed. trip_rules S3 "A student holding a Free Meal Status tier travels on a full waiver": consistent.
- Disguised forms. Anonymous intermediate: none beyond P2/P3. 0/1 multiplier: the carry-back share "0" tier (F3). Dropped branch: none.

### factor_ladders
Declared counts per policy (parameter / method / multi-source / cross_difficulty), and then the tests:

| policy | factors (effect) | P/M | cross_difficulty |
|---|---|---|---|
| waiver_carryback | carryback_share_tier (P), posting_gap_taper (P), elapsed_count_rule (M), carryback_season_length (P) | 3/1 | meals ×3 |
| leaving_credit | leaving_share_tier (P), notice_share_tier (P), used_weeks_rule (M), season_week_count (P), hardship_credit_tier (P) | 4/1 | enroll, meals |
| trip_deposit_carryback | deposit_share_tier (P), deposit_gap_taper (P), lead_used_rule (M), deposit_lead_tier (P) | 3/1 | meals ×3 |
| trip_balance_carryback | balance_share_tier (P), balance_gap_taper (P), balance_due_tier (P), balance_spent_rule (M), balance_lead_tier (P) | 4/1 | meals ×4 |
| trip_cancellation | schedule_base_rule (M), departure_share_tier (P), documentation_share_tier (P), medical_addition_tier (P), hardship_addition_tier (P), arrival_addition_tier (P) | 5/1 | meals, enroll |
| trip_deposit_release | release_share_tier (P), release_doc_tier (M), release_medical_tier (P), release_hardship_tier (P), release_arrival_tier (P) | 4/1 | meals, enroll |

- Structure that holds. Every ladder has three tiers stated in the rule and the same three branches in the decides binding. Bindings are disjoint between factors. No factor binding reads another factor's binding (A1 reads table: each factor re-derives its own effective date / statement date). decides is never result. Fall-through = baseline in every factor.
- Method shapes (A6), all pairs:
  - elapsed_count_rule / lead_used_rule / balance_spent_rule: DAYS(clearance, eff) vs DAYS(registration, eff) vs 0 (distinct input fields): pass.
  - used_weeks_rule: statement date vs enrollment withdrawal date vs 0: pass.
  - release_doc_tier: received_date vs document_date start: pass.
  - schedule_base_rule: **fail**, all three tiers coincide (F2).
- **A1/A7 class (F1), all members.**
  - (a) The ratio-denominator factors are carryback_season_length, season_week_count, deposit_lead_tier and balance_lead_tier. Each enters only as (L − used)/L, and the baseline sets used = 0, so each gives 1 for every L. None can move the result with the other factors at baseline (T2 fails), and none contributes on its own against the baseline quantity.
  - (b) The additive factors are hardship_credit_tier, medical_addition_tier, hardship_addition_tier, arrival_addition_tier, release_medical_tier, release_hardship_tier and release_arrival_tier. At baseline the multiplicative part equals the whole net (shares 100, nothing outright), and the result is MN(net, net + net·add%). Any addition is absorbed by the cap, so T2 fails.
- **Scope tier (F3).** The "0" tier of carryback_share_tier, deposit_share_tier and balance_share_tier ("no Free or Reduced-Price tier OR … outside the … window") is the complement of each policy's own opening scope sentence ("… carried back … only when the student's meal account shows a Free Meal Status or Reduced-Price Meal Status tier that took effect after … and no more than … days after it"). No customer who reaches the write sits on it, and the tools reject credit_amount ≤ 0. The ladders divide customers into two tiers (Free / Reduced), not three.
- **Realism (F4).** Judged per factor against what a Texas ISD publishes:
  - Real: carryback_share_tier's Free/Reduced split (TEC 11.158, base percentages), leaving_share_tier (base window / injury-before-midpoint / none), departure_share_tier and release_share_tier (refund by notice date), and schedule_base_rule's dimension (an unpaid balance is reversed, a paid part is refunded on the schedule). That last one is real, but its ladder is fake (F2).
  - Plausible, kept: elapsed_count_rule (a waiver starting mid-season prorated to the part left).
  - Invented / padding: posting_gap_taper, deposit_gap_taper, balance_gap_taper, balance_due_tier, lead_used_rule, deposit_lead_tier, balance_spent_rule, balance_lead_tier, notice_share_tier, used_weeks_rule + season_week_count (stacked on the flat injury credit), hardship_credit_tier, documentation_share_tier, medical_addition_tier, hardship_addition_tier, arrival_addition_tier, release_doc_tier, release_medical_tier, release_hardship_tier, release_arrival_tier.
  - Details are in finding F4.
- Labels. The method factors change the counting input; the parameter factors substitute numbers. Labels are honest.

### findings
Every item below is RED unless marked observation. A charter-level RED is demonstrated here on a constructed world; the task files demonstrate what each costs their own world.

**P1 — SOURCE-POLICY RED (rule vs compute, "not yet cleared" timing), 3 members: waiver_carryback.elapsed_days, trip_deposit_carryback.lead_days_used, trip_balance_carryback.bal_days_spent.**
- Symptom: the rule frames the count at the moment the status took effect; the compute tests clearance as of now.
- Evidence (waiver_carryback):
  - The rule: "The carry-back covers the part of the season left when the meal status took effect … for a student already cleared when the status took effect the elapsed days are … from the clearance date …, for a student not yet cleared they are the calendar days from the registration date to that date, and otherwise they are 0."
  - The compute: `elapsed_days: DAYS(F('clearance_date'), …) if (F('clearance_date') and elapsed_effective_on > F('clearance_date')) else (DAYS(F('registration_date'), …) if ((not F('clearance_date')) and …) else 0)`.
- Demonstration: High School UIL Athletics, fee 85.00 posted and registered 07-16, Reduced-Price effective 07-25, cleared 08-03 (after the status).
  - Rule: not yet cleared when the status took effect, so elapsed = DAYS(07-16, 07-25) = 9. The posting gap is 9 ≤ 10, so the taper is 100. The credit is 85×50%×100%×(84−9)/84 = 37.95.
  - Compute: clearance_date present, so the registration branch is false, then 0, giving 85×50%×100%×1 = 42.50.
  - The two values differ. The same shape holds in the two trip carry-backs ("for a registration not yet cleared").
- Tasks: no consequence on task 0 (cleared before the status took effect) or task 1 (never cleared). Recorded once here.

**P2 — SOURCE-POLICY RED (rule condition with no compute), 3 members: waiver_carryback, trip_deposit_carryback, trip_balance_carryback.**
- The rule's first sentence limits the carry-back to a fee "posted while the student held no qualifying meal status", and says "every other fee keeps the waiver of the student's meal status on its posting date". The share bindings test only the current tier and the window.
- Demonstration: fee 85.00 posted 09-01 with a reduced_meal_waiver 42.50 already on it (the student held Reduced-Price at posting), then Free Meal Status effective 09-15, student cleared 09-03.
  - Rule: no carry-back (the fee keeps its posting-date waiver), so 0.
  - Compute: share 100, gap 14 → taper 75, elapsed 12, giving 85×1×0.75×72/84 − 42.50 = 12.14.
- Tasks: none (both fees were posted with no waiver credit).

**P3 — SOURCE-POLICY RED (undeclared conflict with a base field rule), 1 member: waiver_carryback.**
- Base event activity_fee_credit.amount: "Credit, positive USD, never more than the source charge net of earlier credits."
- The carry-back result is `MX(0, fee_amount × … − waivers_posted)`, and household_cap credits are not subtracted.
- Demonstration: fee 85.00 with a household_cap credit 40.00 (the household was past the 300.00 cap), Free Meal Status effective 5 days after posting, before clearance.
  - Compute (per-season type, elapsed 5 from the registration date): 85×100%×100%×79/84 − 0 = 79.94, which exceeds the 45.00 net of earlier credits.
  - Base: at most 45.00.
- No overwrite names that base clause. Trip fees never carry cap credits, so only this policy is affected. Tasks: none (no cap credit seeded).

**P4 — SOURCE-POLICY RED (false framing, B8), leaving_credit.**
- The rule says "the latest physician_injury_statement … is dated no more than midpoint_days calendar days after the clearance date (the season midpoint)" with midpoint_days = 42, while the same rule says "the season counts … season_weeks_per_school_year weeks otherwise" (36).
- For Cheer and Dance Team (per school year, injury_credit_pct 50): cleared 08-03, statement dated 09-30 (58 days, week 8 of the 36-week season), notice 10-15.
  - Reading "dated no more than 42 days": leaving share 0.
  - Reading "before the season midpoint" of the stated 36-week season (126 days): leaving share 50.
  - The two readings give two credits.
- Tasks: none (task 0 is per-season, 12 weeks, where 42 days is the midpoint).

**P5 — SOURCE-POLICY RED (XF A2 assembly naming factor quantities), all 6 policies.** Each rule's single order sentence names the factor quantities it assembles:
- waiver_carryback: "… multiplied by the carry-back share, then by the share of the fee carried back, then by the part of the season the carry-back covers".
- leaving_credit: "… by the leaving share, then by the notice share, then by the unused part of the season; the hardship credit share … is then added".
- trip_deposit_carryback: "… by the deposit carry-back share, then by the deposit taper, then by the part of the trip lead time …".
- trip_balance_carryback: "… by the balance carry-back share, then by the balance taper, then by the balance due-date share, then by the part of the lead time …".
- trip_cancellation: "… multiplied by the departure share and then by the documentation share; the medical, hardship and arrival additions … are then added".
- trip_deposit_release: "… by the release share and then by the release documentation share; the release medical, hardship and arrival additions … are then added".

Each baseline.rule repeats the assembly sentence plus a sentence naming every factor quantity's default. So the computation document cannot be rendered without naming every factor (A2/A3/A10). This bears on both tasks' rendered surface.

**F1 — SOURCE-FACTOR RED (A1/A7: no contribution against the baseline quantity), 11 members.**
- (a) carryback_season_length, season_week_count, deposit_lead_tier, balance_lead_tier.
  - Each enters only through `(L − used)/L`, and every baseline.rule fixes used at 0 ("the carry-back covers the whole season", "no weeks of the season count as used", "no lead days count as used", "no days of the balance lead time count as spent").
  - With every other factor at baseline, any L gives 1, so the factor cannot move the result in any world.
- (b) hardship_credit_tier, medical_addition_tier, hardship_addition_tier, arrival_addition_tier, release_medical_tier, release_hardship_tier, release_arrival_tier.
  - With every other factor at baseline, the multiplicative part is the whole net (leaving: net×100%×100%×1; cancellation: share_base = net, outright 0, shares 100; release: net×100%×100%).
  - The result `MN(net, net + net×add%)` = net for every add% ≥ 0, so T2 fails.
- Per-task T1 is shown in the task files.

**F2 — SOURCE-FACTOR RED (unreal ladder: tiers coincide), trip_cancellation.schedule_base_rule.**
- `sb_reaching = MN(tc_bal_net, MX(0, sb_payments − tc_dep_net))` always lies in [0, tc_bal_net]. Then `share_base = sb_reaching if 0 < sb_reaching < tc_bal_net else (0 if sb_reaching ≤ 0 else tc_bal_net)` equals sb_reaching on all three branches: 0 → 0, interior → itself, upper end → tc_bal_net = sb_reaching.
- All three tiers select one method ("the schedule shares act on the payments reaching the balance"). It is one plain binding written as a three-tier ladder. It is the policy's only method factor, so trip_cancellation has no valid method factor.

**F3 — SOURCE-FACTOR RED (scope-restating tier), carryback_share_tier, deposit_share_tier, balance_share_tier.**
- The "0" tier condition is the complement of the policy's own scope sentence. It holds of no customer who reaches the write (the tools reject credit_amount ≤ 0), so each ladder has two real tiers (Reduced 50 / Free 100), fewer than three.

**F4 — SOURCE-FACTOR RED (realism: invented tapers, shares and additions no Texas ISD publishes).** Judged one by one:
- posting_gap_taper / deposit_gap_taper / balance_gap_taper (100/75/50 by days from posting to the status's effective date). The effective date is the district's own determination date (meals benefit_effective_basis = determination_date, determined within 10 operating days). So the taper cuts the TEC 11.158 waiver for the time School Nutrition took to decide. No district publishes a waiver that shrinks with its own processing time, and the 30-day window already bounds retroactivity.
- balance_due_tier (75/50 when the status took effect near or after the balance due date): invented second time-decay on the same date.
- lead_used_rule, balance_spent_rule, deposit_lead_tier (28/14 cap/floor), balance_lead_tier (35/21). These prorate a trip deposit/balance waiver by "lead time used" before the trip. The trip has not happened and the student receives the whole trip, so there is no consumed share to prorate. The cap/floor day counts are invented.
- notice_share_tier (100/50/0 by days from the physician statement to the family's notice): an invented taper stacked on the base injury credit.
- used_weeks_rule + season_week_count. A weeks-used proration stacked on the base's flat injury_credit_pct (whose "before the midpoint" test already is the district's proration). F2 says "A flat fee stays flat; don't stack percentage discounts on it".
- hardship_credit_tier (+20%/+10% of the net fee on leaving), hardship_addition_tier (+6/+3%) and release_hardship_tier (+8/+4%). Each is a second meal-status benefit stacked on the TEC 11.158 waiver the fee already carries. No district publishes a "hardship add-on" to a withdrawal or cancellation credit.
- arrival_addition_tier (+4% new_to_district / +2% re_entry) and release_arrival_tier (+6/+3%): a cancellation bonus for being new to the district is not a dimension any district weighs for a trip refund.
- documentation_share_tier (75/50 by statement age) and release_doc_tier (count from receipt when received more than 2 days after the date on it, 80/60). These penalise a family for the age of a doctor's note; the receipt-grace start-date method is invented.
- medical_addition_tier (+10/+5%) and release_medical_tier (+20/+10%). A documented medical reason is a real refund exception, but districts grant it as a release of the nonrefundable part, not as a percentage add-on scaled by the note's age.

**F5 — SOURCE-FACTOR RED (factor floor after striking).** Counting only factors that pass F1–F4:
- waiver_carryback: elapsed_count_rule (M) only (carryback_share_tier struck by F3) → 0 P / 1 M.
- leaving_credit: leaving_share_tier (P) → 1 P / 0 M.
- trip_deposit_carryback: none.
- trip_balance_carryback: none.
- trip_cancellation: departure_share_tier (P) → 1 P / 0 M.
- trip_deposit_release: release_share_tier (P) → 1 P / 0 M.

Every policy is below the floor of 4–6 factors with ≥ 2 parameter and ≥ 1 method.

Observations (no demonstrated consequence):
- O1. leaving_credit books a positive credit after the window with no injury statement (hardship share only) under credit_reason injury_credit with end_reason family_withdrawal, which mislabels the credit reason.
- O2. The non-family cancellation schedule is ambiguous (policy_conflict_scan).
- O3. LATEST physician-statement reads have no same-date tie rule.
- O4. The cancel/withdraw docstrings carry lifecycle wording ("before clearance", "after the clearance date").
- O5. The release-hop resolves through the rules, though two tools can write status withdrawn.
- O6. waivers_posted has no source filter (unreachable divergence).

## closing_checklist
Not reached: the four relationships do not all PASS (charter REDs P1–P5 and F1–F5; both tasks SOURCE-FACTOR RED and SOURCE-POLICY RED via P5). Per-task results, written after both reveals:
- 0.md: problem tree PASS; unique solution PASS (every GT value matches the frozen derivation); factors RED; policy RED (P5).
- 1.md: problem tree PASS (3 prerequisite problems, 3 value_input edges, owner=user cancellation); unique solution PASS (all four values match); factors RED; policy RED (P5).
- Already true: scopes disjoint and jointly complete, graph acyclic, uuid8s independent, tools do not judge prerequisites.
- The instantiation gates were not re-run (no final form yet).

VERDICT revision_1: task0=RED task1=RED charter=P1,P2,P3,P4,P5,F1,F2,F3,F4,F5

## revision_2

## charter_global_frozen (revision_2)
- Freeze time: see the file mtime of this section's write (before any r2 task file and before any r2 GT/worklog read). Auditor: independent policy-task auditor.
- Entry: `grep -v '^\s*$' worklog.md | tail -n 1` = "REWORK round 2: gates 7/7 green". The snapshot was run by me: /tmp/erl0078_coord/snap_activity_fees_and_waivers_r2.txt shows all 7 gates OK.
- Hashes: activity.extended.yaml 2ff8db85d7cfdbe5…, task_tools.py f55de4805696d360…; views r2/0.view.json cf68e386fac4cff9…, r2/1.view.json f3341034b40ec34b…. Both the charter and the tools changed (r1: 62ec6daa… / d3761ce4…), so every charter-global section is re-derived in full below. Nothing is carried forward.
- Read for this section: the extended section (all six new policies), task_tools.py, blueprint products activity/enroll (transfer windows lines 189–215, 736–760)/music (usage fee lines 33–73, 287–330, 599–650), db_schema, XF_recipe.md, owner_ruling.md, and realism_bar.md including AMENDMENT 1.
- Not yet read: tasks/*.json, the worklog claims section, plan.md.
- Base copy: verbatim (structural equality).
- Mechanical sweep: every compute_basis value, baseline sentence, policy_source and replaced_by is verbatim in its own rule. Every superseded_clause is verbatim in its base policy. Every binding has a basis.

### Round-1 RED items: status by construction
The rework replaced all six round-1 policies:
- waiver/trip carry-backs, leaving credit, trip cancellation and deposit release are gone;
- new: activity_ext_uil_packet_fee, activity_ext_uil_travel_fee, activity_ext_arts_packet_fee, activity_ext_arts_travel_fee, activity_ext_arts_late_fee, activity_ext_arts_first_installment.

Per round-1 item:
- P1, P2, P3, P4: closed (their policies and bindings no longer exist; no new carry-back/leaving logic).
- P5 (assembly naming factor quantities): closed. Every new order sentence is generic ("Adjustments in this schedule are applied in this order: amounts are added together first, the shares are then applied one after the other …"; installment: "the amounts due up front are set aside from the plan total first …"), and each baseline.rule is one sentence naming no factor.
- F1 (no contribution against baseline): closed in kind. No ratio-denominator factor and no cap-absorbed addition remains. Additive amounts add outside any cap, the shares multiply a total the baseline defines, and every factor moves the result with the others at baseline (T2 holds; checked per factor).
- F2 (coinciding tiers): closed (schedule_base_rule gone). The new method factors are checked in A6 below.
- F3 (scope tier): closed (no ladder has a tier equal to the policy scope's complement).
- F4/F5 (realism/floor): re-judged from scratch below under realism_bar.md. Some new members are raised.

### policy_conflict_scan
| policy | computes / tool (owner) | trigger | prerequisite |
|---|---|---|---|
| uil_packet_fee | participation_fee_amount / submit_uil_packet_8c6962d4 (user) | on_request | [] |
| uil_travel_fee | travel_fee_amount / post_uil_travel_fee_ebd1d9ff (agent) | on_request | ← uil_packet (vi, gate tv_permission_count) |
| arts_packet_fee | participation_fee_amount / submit_arts_packet_1cf2bbdb (user) | on_request | [] |
| arts_travel_fee | travel_fee_amount / post_arts_travel_fee_8b3017ab (agent) | state_due | ← arts_packet (vi, at_permission_count) |
| arts_late_fee | late_fee_amount / post_arts_late_fee_733500d1 (agent) | state_due | ← arts_packet (vi, lt_packet_on) |
| arts_first_installment | payment_amount / pay_arts_first_installment_d908e75f (user) | on_request | ← arts_packet, ← arts_travel, ← arts_late (vi ×3) |

- Overlaps. Four sibling overwrites retire activity_evt_fees S1 (posting on the registration date). Each tail names its own roster-opened type and the sibling type's schedules, and restates catalogue posting for every other participation (C1/C2 hold). activity_evt_fees S2 (late fee) is retired by uil_packet and arts_late_fee, each naming the other (C2 holds). activity_payments S2 is retired by arts_first_installment, with the standing plan restated (C1 holds).
- In force and inherited: evt_fees S3–S6 (meal-status waivers on the posting date, waivability, due days), the household cap, clearance (packet + fees settled or first installment paid), and payments S1/S3. No new rule contradicts them.
- Scopes. Task 0 = {uil_packet, uil_travel}; task 1 = {arts_packet, arts_travel, arts_late, arts_first_installment}. Pairwise disjoint and jointly complete.
- Cross-category reads: enroll grade_level/variant_name (5 policies), music variant_name/status/school_year (3 arts policies). Both are reachable (find_enrollments, find_instrument_checkouts) and declared.

### rule_compute_equivalence
- Sentence-by-sentence sweep. Rates, level amounts, shares, the join/term prorations (B1 edges: "on or after" spring start = `>= 0`; "after" first practice = `> 0`; whole weeks = int(DAYS/7), capped at 100), booking/rush/lateness thresholds (strict/inclusive bounds match their sentences), the instrument first-match with its status filter and stated tie rule, the installment due-date count (MONTHS(NOW, end)+1 matches "monthly due dates from the first installment through plan_end_date, same day of the following months"; the month-end days 29–31 have no stated convention, observation), the floor-to-cent divisions and the half-up up-front parts. All are equivalent in both directions.
- Rounding: RND(x+1e-9, 2) on non-negative values, and the rounding point is stated. The tools use the Decimal half-up static helper.
- Observation (B7-adjacent): the level tiers read "a student at an elementary/middle school campus". The compute reads the participation's campus, the rule does not say whose campus, and the enrollment campus can differ after a mid-year transfer. In both task worlds they agree.

### action_binding_and_uuids
- Six (tool, computes) pairs, one per policy. uuid8s 8c6962d4, ebd1d9ff, 1cf2bbdb, 8b3017ab, 733500d1, d908e75f are independent.
- No docstring carries an ordering word or names another tool (grep of before/after/first/then/once/until/prior: no hit).
- The tool bodies check only the amount and method format; none reads a prerequisite record (B6 holds).
- owner=user:
  - submit_uil_packet and submit_arts_packet: ruling (d), the parent's signature on the parent permission, code of conduct and overnight travel permission, and the rule states it is the family's own submission.
  - pay_arts_first_installment: ruling (b), the online portal payment, declared by scoped overwrite ("is paid by the parent or guardian themselves online").
  - All three are accepted.

### prerequisite_graph / prerequisite_sentences
- Edges: uil_packet→uil_travel; arts_packet→arts_travel; arts_packet→arts_late; arts_packet, arts_travel, arts_late→arts_first_installment. Acyclic. All form=state; gates exist in the blocked computes; resolved_by = depended-on target_tool. Conditions "… or that schedule owes none" are open sets stated open.
- Sentences (connectives "only after", "not … until", "Before … must already", "fixed only after"):
  - "The travel fee is posted only after the participation's records log carries the overnight travel permission form from the parent's signed packet."
  - "The Fine Arts travel fee is not posted until …"
  - "The Fine Arts late registration fee is fixed only after the records log shows the date the parent's signed packet was received."
  - "The first installment is fixed only after the participation fee from the parent's signed packet stands …"
  - "Before the first installment is worked out, the ledger must carry the travel fee the Fine Arts travel fee schedule owes once the overnight permission is on file."
  - "The first installment is not worked out until the ledger carries any late registration fee …"
- The single resolving writes: the overnight-permission/document state is written by the packet tool of the matching type. The UIL and arts packet tools both record the form, but each rule restricts it to its own type. Travel and late fee entries are written by their own tools.
- Observation: the installment's travel sentence carries "once the overnight permission is on file", which restates when the travel schedule owes (the travel policy's own gate). It is not a second edge, and the hop is declared separately.

### override_declarations
Activity_evt_fees, activity_agg_household_fee_cap, activity_clearance_requirements, activity_trip_rules, activity_agg_multi_holding, activity_refund_credits, activity_equipment and activity_payments_and_installments were swept sentence by sentence. Only the three sentences named above are handled differently, and each is declared with scoped tails. Disguised forms:
- the travel and late gates (`if permission_count > 0 else 0`; `if lt_in_scope else 0`) are 0/1 multipliers, but each is stated in the rule ("posted only after …"; "only when its signed packet is received more than … days after the roster date");
- no dropped branch.

### factor_ladders (structure)
Declared: uil_packet 4 (3P/1M), uil_travel 5 (4P/1M), arts_packet 5 (4P/1M), arts_travel 6 (5P/1M), arts_late 5 (4P/1M), arts_first_installment 4 (3P/1M).
- Every ladder has three tiers stated in the rule and branches equal to the tiers. Bindings are disjoint. No factor binding reads another factor's binding (A1 reads table: each re-reads its own grade/variant/date). Fall-through = baseline. decides ≠ result.
- A6, method pairs:
  - uil_join_tier / uil_trip_season_rule / membership_term_rule / trip_term_rule: flat 50 vs whole-week proration vs 100. The proration coincides with 100 only for roster dates whose remaining whole weeks reach 40 (early August), not on the whole domain. Pass.
  - lateness_charge_rule: weeks × rate vs flat + per-day vs flat. Pass.
  - travel_placement_rule: whole net vs net ÷ pre-trip due dates vs 0. Pass.
- A7: plan_count_tier is a lesser-of (due dates vs installment_count). T1 and T2 hold. No other min/max.
- A3 (defining sentence used by one factor only): "The team's overnight trip for the 2026-27 school year is on robotics_trip_date …" (plain binding tv_trip_date, used only by booking_lead_tier's bindings) and "The ensemble's spring overnight trip … is on band_trip_date …" (plain at_trip_date, used only by late_booking_tier). See finding A3.

### realism (realism_bar.md R1–R6 / X1–X4), per factor
| policy | factor | shape | grade |
|---|---|---|---|
| uil_packet | uil_rate_tier | activity × grade band | R1 |
| | uil_level_tier | campus level × grade | R1 |
| | uil_enrollment_tier | non-resident / employee-child transfer | R1 (residence, employee keys) |
| | uil_join_tier | spring flat / weekly proration by roster date | R3 |
| uil_travel | uil_travel_rate_tier, uil_trip_level_tier, uil_residence_tier | as above on the travel fee | R1 |
| | uil_trip_season_rule | prorates ONE overnight trip's fee by roster date | **X1 + B8** (RED, see TS) |
| | booking_lead_tier | +20/+10 by permission-received → trip-date lead days | R6 candidate (needs tag/minimality; graded after the claims read) |
| arts_packet | arts_rate_tier, arts_level_tier (beginner method book / 7–8 discount), arts_residency_tier | | R1 |
| | membership_term_rule | | R3 |
| | instrument_program_tier | +20/+10 on the ensemble fee for holding a district instrument | **X3/X2** (RED, see IN) |
| arts_travel | arts_travel_rate_tier, arts_trip_group_tier, arts_travel_residency_tier | | R1 |
| | trip_term_rule | prorates the single spring trip's fee by roster date | **X1 + B8** (RED, TS) |
| | late_booking_tier | +20/+10 by packet-received → trip lead days | R6 candidate |
| | instrument_haul_tier | +25/+10 to carry a district instrument on the trip | R6 candidate |
| arts_late | lateness_charge_rule | late fee by days late (flat / +1 a day / weekly) | R2 |
| | late_level_tier | −4/−2 off a late fee by grade | **X1** (cuts on penalty fees) RED |
| | late_residency_tier | 150% / 50% of a late fee by transfer type | **X1** (percentage cut/uplift on a penalty fee) RED |
| | concert_rush_tier | second lateness surcharge (received → concert) on the same flat late fee | **X2** (stacked on the packet-received date already used by lateness_charge_rule) RED |
| | fitting_tier | +5/+3 on a LATE FEE for holding a district instrument | **X1/X3** RED (a penalty priced by instrument type; music base: the usage fee "covers routine maintenance") |
| arts_first_installment | plan_count_tier | number of installments within the plan window | R5 |
| | travel_placement_rule | trip fee due before the trip, by days to the trip | R2 |
| | plan_lead_tier | 50/25% of the participation fee up front by roster → first-installment days | R6 candidate |
| | late_placement_tier | late fee up front by its posting date → concert days | R6 candidate |

### findings (revision_2)
**TS — SOURCE-FACTOR RED (realism X1; false framing B8), uil_travel_fee.uil_trip_season_rule, arts_travel_fee.trip_term_rule.**
- Each rule names exactly one overnight trip ("The team's overnight trip for the 2026-27 school year is on robotics_trip_date …"; "The ensemble's spring overnight trip … is on band_trip_date …"). It then charges a roster date on or after spring start "the spring trips only" / "the spring trip only, a flat 50 percent", and prorates fall joiners by weeks to the last school day.
- A spring joiner travels on the whole (only) trip, so there is no consumed share. The "spring trips only" wording asserts fall trips no record or sentence holds.
- Two readings for a January joiner: 50% (the share sentence) vs 100% (the travel fee covers the single trip the student takes; base parameter "Overnight … travel fee per participation"). This removes the only method factor of each travel computation.

**IN — SOURCE-FACTOR RED (X3/X2), arts_packet_fee.instrument_program_tier.**
- The music base charter already prices a district instrument: "The usage fee posts on the checkout date at usage_fee … the fee covers routine maintenance and the year-end cleaning". Large Instrument Usage usage_fee is 125.00.
- An ensemble-fee "instrument program amount" keyed on the same checkout charges that dimension a second time for no stated service.

**LF — SOURCE-FACTOR RED (X1/X2/X3), arts_late_fee: late_level_tier, late_residency_tier, concert_rush_tier, fitting_tier.**
- A late registration fee is a penalty. The bar names "Hardship shares or percentage cuts on penalty fees" as X1, so grade-band and transfer-type discounts or uplifts on it are X1.
- concert_rush_tier stacks a second lateness surcharge on the same packet-received date (X2).
- fitting_tier prices a penalty by instrument type, and "fitting" falls under the maintenance the usage fee covers (X1/X3).
- Once struck, the computation keeps one honest factor (lateness_charge_rule).

**A3 — SOURCE-POLICY RED (XF A3), 2 members.**
- tv_trip_date (uil_travel_fee) and at_trip_date (arts_travel_fee) are plain bindings whose defining sentence is used only by booking_lead_tier / late_booking_tier respectively.
- Rendered as plain computation-document content, they disclose the booking factor's input outside its own document.

**B8 — SOURCE-POLICY RED (false framing with a second reading), uil_travel_fee.uil_trip_level_tier "(day trips)".**
- "minus uil_elem_travel_discount for a student at an elementary campus … (day trips)" asserts that elementary teams travel on day trips, while "The team's overnight trip … is on academics_trip_date otherwise" and the fee is the overnight travel fee.
- Reading A: an elementary student owes (95 − 40) × shares. Reading B: no overnight travel, so the fee "works out to 0.00 posts nothing".
- Neither task is affected (task 0 is a middle school student).

**RO — SOURCE-POLICY RED (XF B7/C4), the "roster-opened" scope of uil_packet_fee, uil_travel_fee, arts_packet_fee, arts_travel_fee, arts_late_fee and arts_first_installment.**
- Every new overwrite scopes itself to a participation "that the director's roster opens". No activity_participations field records who opened a participation, and the rule states no record test.
- The only record signature is "registered with no fee entries", which the rule never states. Which charter governs therefore rests on the caller's word.
- In both tasks the persona states it ("put her on the robotics team roster"; "the band director added Elin"), so neither task is moved. Recorded once here.

Observations: month-end due dates (no 29–31 convention); whose campus the level tiers read; the installment travel sentence's "once the overnight permission is on file".

### R6 grading (AMENDMENT 1), done after the freeze of 0.md/1.md r2, against the claims section "REWORK round 2 claims (final)"
- **booking_lead_tier** (uil_travel; tagged R6; key: overnight_travel_permission received_date vs the trip date).
  - Cond. 1–4 hold: recorded key; round +20/+10; no base conflict; not a named X1 (this is the family's late paperwork, not a desk-posting delay).
  - Cond. 5: no other factor of the travel computation uses that date.
  - Cond. 6: even with TS struck, honest = 3, so 2 slots; 1 is used.
  - → `R6-WAIVED (BLUEPRINT-KNOWN)`, observation.
- **late_booking_tier** (arts_travel; R6; packet received date vs trip date): same grading → `R6-WAIVED (BLUEPRINT-KNOWN)`.
- **instrument_haul_tier** (arts_travel; R6; instrument_checkouts variant).
  - Cond. 1–4 hold. Carrying a large instrument on the trip is a distinct service, not one the music usage fee covers ("routine maintenance and the year-end cleaning").
  - Cond. 5–6 hold (honest 3 with TS struck, so 3 slots; 2 used).
  - → `R6-WAIVED (BLUEPRINT-KNOWN)`.
- **instrument_program_tier** (arts_packet; tagged R6) → **RED, condition 5 (X3)**.
  - The district instrument is already priced by a recorded amount: the music usage fee, which posts on the checkout date and covers the instrument's maintenance and cleaning.
  - The ensemble "instrument program amount" re-charges the same checkout for no service the rule names. See finding IN.
- **concert_rush_tier** (arts_late; tagged R6) → **RED, condition 5 (X2)**.
  - It is a second lateness surcharge on the same packet-received date that lateness_charge_rule already prices, stacked on the same late fee.
- **fitting_tier** (arts_late; tagged R6) → **RED, conditions 3 and 2**.
  - Instrument fitting falls under the routine maintenance the in-force music base clause says the usage fee covers.
  - A late registration penalty priced by instrument type is not a plausible district figure.
- **Untagged factors the claims count as honest:**
  - late_level_tier and late_residency_tier: **RED, X1**. These are grade-band and transfer-type cuts/uplifts on a penalty fee, the named "percentage cuts on penalty fees" mechanism. As R6 they would also fail condition 4.
  - uil_trip_season_rule and trip_term_rule: **RED, X1 + B8** (finding TS). As R6 they would fail condition 2/5: the share has no consumed part to prorate, and the "spring trips only" wording is false framing.
  - plan_lead_tier and late_placement_tier (installment): accepted as R2 timing schedules (down-payment share by roster → first-payment days; late-fee placement by days to the concert). Read as untagged R6, they meet conditions 1–6 (honest 2, so 2 slots). Not RED.

**FL — SOURCE-FACTOR RED (floor after the strikes).**
- uil_travel_fee keeps 4 (3 P + 1 R6-waived) with **0 method**.
- arts_travel_fee keeps 5 with **0 method**.
- arts_late_fee keeps 1 (lateness_charge_rule).
- arts_packet_fee keeps 4 against its drawn 5. The realism bar fixes drawn counts as not waivable, and the missing slot is IN.
- uil_packet_fee and arts_first_installment meet the floor.

### Final sweep of every class raised in any revision, across the whole r2 charter
- P1 class (rule vs compute date/time selection): none. The lateness, booking, rush, lead and placement day counts all match their sentences.
- P2 class (rule condition with no compute): none in the scored paths.
  - Observation UL: the UIL packet rule promises "posts late_registration_fee only when its packet is submitted more than uil_late_packet_days calendar days after the roster date", but no tool or compute posts a UIL late fee. A world with a packet more than 14 days late has no in-scope write. Not engaged (task 0 is 8 days).
  - Observation WV: base S3 meal-status waivers on schedule-posted fees remain owed at posting, and no tool of this difficulty posts them. Both task students are Paid.
- P3 class (base field-limit conflict): none. Every posted fee is positive "before waivers". Installment nets are taken per entry.
- P4 / B8 class (false framing): TS ("spring trips only"), B8 ("(day trips)"). The rationale parentheticals "(the beginner method book)" and "(the beginner group travels a shorter route)" create no second reading: observation.
- P5 / A2 (assembly naming factors): none.
- F1 / A1 / A7 (no contribution against the baseline; caps absorbing): none.
- F2 / A6 (coinciding tiers): none.
- F3 (scope tier): none.
- F4 / realism: TS, IN, LF, as graded.
- F5 / floor: FL.
- A3: two members (A3).
- B7 / C4: RO.

VERDICT revision_2: task0=RED task1=RED charter=TS,IN,LF,FL,A3,B8,RO

## revision_3

## charter_global_frozen (revision_3)
- Written before any r3 task section, before the round-3 worklog claims and before any task JSON.
- Entry checks:
  - worklog last line = "REWORK round 3: gates 7/7 green".
  - I ran the snapshot: /tmp/erl0078_coord/snap_activity_fees_and_waivers_r3.txt, 7/7 OK.
- Hashes:
  - activity.extended.yaml e46310739e96c6e6… and task_tools.py 0040d1ba3cee1ae1…: both changed since r2, so every charter-global section is re-derived.
  - Views r3/0 cf68e386fac4cff9… and r3/1 f3341034b40ec34b… are byte-identical to r2: same worlds and personas.
  - realism_bar.md is unchanged since r2 (b877e5f9…, mtime 21:19), and I applied its AMENDMENT 1 as read in r2.
- Base copy: verbatim.
- Mechanical sweep: compute_basis, baseline sentences, policy_sources and replaced_by are all verbatim in their rules. Every superseded clause is verbatim in base. Every binding has a basis.

### What changed in the charter
- Every overwrite scope is now the record test "a … participation for the 2026-27 school year whose registration date is after 2026-08-03" (was "roster-opened").
- UIL and Fine Arts late-registration fees for those participations are replaced by "posts no late registration fee", and activity_ext_arts_late_fee is removed.
- New activity_ext_arts_attire_fee (post_arts_attire_fee_5e2c9a17, agent, state_due), which prices the uniform_package component.
- The installment now reads the attire package instead of the late fee (attire_placement_tier replaces late_placement_tier).
- arts_packet: instrument_program_tier is replaced by arts_campus_tier (+10 Hollis MS / +20 Calloway Creek HS, by the enrollment record's campus).
- Both travel fees: the single-trip/term share is replaced by a four-trip schedule (uil_trip_share_rule, arts_trip_share_rule), with the booking amounts timed to the next trip on or after the received date.
- The "(day trips)" parenthetical is removed. The join/membership shares gain a 28-day grace after first practice.

### Status of the round-2 RED items
- **RO: closed.** The scope is a stated, coarse record test on activity_participations.registration_date and school_year (B7/C4 satisfied).
- **B8: closed.** "(day trips)" is gone, and no remaining framing clause produces a second reading. The rationale parentheticals are gone.
- **A3: closed.** tv_trip_1..4 / at_trip_1..4 are each read by two factors (the trip share and the booking amount), so they are legitimately plain. plan_total is shared with the baseline sentence. The sweep finds no single-factor plain binding.
- **IN: closed.** instrument_program_tier was removed. The replacement arts_campus_tier is R1 (campus key) and does not touch the instrument dimension.
- **LF: closed.** activity_ext_arts_late_fee and its four X1/X2/X3 factors are removed. The replacement late-fee clause posts nothing for these participations (declared in both packet overwrites, naming each other).
- **TS: not closed (changed form), see TR.** The single-trip proration is gone, and a per-trip schedule over four published trip dates is a real R2 shape. But the new ladder breaks the factor structure.
- **FL: not closed.** It follows from TR and AT below.

### policy_conflict_scan
| policy | computes / tool (owner) | trigger | prerequisite |
|---|---|---|---|
| uil_packet_fee | participation_fee_amount / submit_uil_packet_8c6962d4 (user) | on_request | [] |
| uil_travel_fee | travel_fee_amount / post_uil_travel_fee_ebd1d9ff (agent) | on_request | ← uil_packet (vi) |
| arts_packet_fee | participation_fee_amount / submit_arts_packet_1cf2bbdb (user) | on_request | [] |
| arts_travel_fee | travel_fee_amount / post_arts_travel_fee_8b3017ab (agent) | state_due | ← arts_packet (vi) |
| arts_attire_fee | uniform_package_amount / post_arts_attire_fee_5e2c9a17 (agent) | state_due | ← arts_packet (vi, ap_packet_count) |
| arts_first_installment | payment_amount / pay_arts_first_installment_d908e75f (user) | on_request | ← packet, travel, attire (vi ×3) |

- Five sibling overwrites retire evt_fees S1. Every tail names both programs' schedules and restates catalogue posting for every other participation. The arts tails name the packet, travel and concert-attire schedules (C1/C2 hold).
- Two siblings retire evt_fees S2, each naming the other and restating the base late fee for every other registration.
- payments S2 is retired with the standing plan restated.
- Inherited and consistent:
  - evt_fees S3/S4: the meal-status waivers; uniform_package_waivable is true for Fine Arts.
  - The household cap: uniform packages and travel never count.
  - refund_credits S5: a uniform package is never credited after clearance.
  - Clearance.
- Scopes: task 0 {uil_packet, uil_travel}; task 1 {arts_packet, arts_travel, arts_attire, arts_first_installment}. Disjoint and complete.

### rule_compute_equivalence
- The trip shares match the rule. ts_left counts trips with DAYS(registration, trip) ≥ 0, i.e. "on or after". The shares are 100 / n×100/4 / n×single_pct.
- The booking/rush/attire-placement next-event selection is "the first … on or after that date", and the "none remaining → nothing" branches match.
- The join grace (`> join_grace_days`) matches "more than join_grace_days calendar days after". The other r2 equivalences carry over unchanged (the same sentences and bindings).
- Observations:
  - The level tiers of uil_packet/uil_travel/arts_travel still read the participation's campus, while arts_packet and arts_attire read the enrollment record's campus. Each rule says which, and both campuses agree in both worlds.
  - Month-end due dates (29–31) have no stated convention.

### action_binding_and_uuids
- Seven distinct pairs, one per policy. The new uuid8 is 5e2c9a17 and is independent.
- No ordering words in the docstrings.
- Tools validate only the amount and method format and read no prerequisite. The attire tool books fee_component uniform_package in its own body (B6 holds).
- owner=user: packet submissions under ruling (d); the online payment under ruling (b), declared.

### prerequisite_graph / prerequisite_sentences
- Edges: uil_packet→uil_travel; arts_packet→arts_travel; arts_packet→arts_attire; packet, travel, attire→installment. All form=state, acyclic. Gates exist; the open-set conditions are stated open.
- New sentences:
  - "The concert attire package is not ordered until the participation's records log shows the date the parent's signed packet was received."
  - "The first installment is not worked out until the ledger carries the concert attire package the Fine Arts concert attire schedule owes."
- One resolving write each.
- The r2 observation that the installment's travel sentence restated the travel gate is closed: "once the overnight permission is on file" was removed.

### factor_ladders and realism (R1–R6 / X1–X4)
| policy | factor | shape | grade |
|---|---|---|---|
| uil_packet | rate, level, enrollment | | R1 |
| | uil_join_tier | | R3 |
| uil_travel | rate, trip level, residence | | R1 |
| | uil_trip_share_rule | travel fee by trips remaining | dimension R2, ladder defective (**TR**) |
| | booking_lead_tier | | R6 candidate |
| arts_packet | rate, level, campus (new), residency | | R1 |
| | membership_term_rule | | R3 |
| arts_travel | rate, group, residency | | R1 |
| | arts_trip_share_rule | | ladder defective (**TR**) |
| | late_booking_tier, instrument_haul_tier | | R6 candidates |
| arts_attire | attire_rate_tier (band 40 / choir 30 / catalogue), attire_level_tier (−15 beginner grade 06, +20 HS formal), attire_campus_tier (+5 Hollis, +10 Mesquite Ridge) | | R1 |
| | rental_term_rule | prorates the attire package by registration term | **AT** (RED) |
| | concert_order_tier | rush-order surcharge by days from packet receipt to the next concert | R6 candidate |
| arts_first_installment | plan_count_tier | | R5 |
| | travel_placement_rule | | R2 |
| | plan_lead_tier | | R2 (as in r2) |
| | attire_placement_tier | attire due up front by days to the next concert | R2 timing, pass |

- A6 / fall-through check: every factor's fall-through tier equals its baseline except the two trip-share rules (script sweep: baseline value vs the last ladder tier, per factor).
- A1/A7: no cap absorbs an addition. The attire result is not capped; MX(0, …) clamps only the pre-share sum. T2 holds per factor.

### findings (revision_3)
**TR — SOURCE-FACTOR RED (fall-through ≠ baseline; tiers coincide), uil_travel_fee.uil_trip_share_rule and arts_travel_fee.arts_trip_share_rule.**
- The ladders read:
  - tier 1 "all four of the team's trips fall on or after the registration date" → 100;
  - tier 2 "two or three" → "that number of trips out of four";
  - fall-through "otherwise" → "uil_single_trip_pct / arts_single_trip_pct percent for each trip on or after the registration date".
- Yet each factor's `baseline` is `trip_share: "100"`, the value of tier 1, not of the fall-through. The rule's standard computation ("The scheduled travel fee is travel_fee …") is also 100%, so the fall-through tier is not the baseline. That violates "every factor's fall-through tier is that baseline". For n = 1 the fall-through gives 30, against 100 at baseline.
- Tier 1 also coincides with tier 2's method on its own domain (4 × 100/4 = 100), so "trips remaining out of four" is one method written as two tiers (A6: the tiers coincide on the reachable domain).
- Consequence: each travel computation's only method factor fails the structure test.
- Realism note: a per-trip travel schedule keyed on published trip dates is itself an acceptable R2 dimension. The defect is the ladder, not the dimension.

**AT — SOURCE-FACTOR RED (realism X1 + false framing; conflict with the base meaning), arts_attire_fee.rental_term_rule.**
- The base charter defines the component this policy prices as "uniform_package_fee: Student-kept apparel package charged per participation". activity_refund_credits says it is "ordered in the student's name" and "never credited after clearance".
- The new rule nevertheless applies "A rental-term share … a registration date on or after attire_spring_start pays the spring-semester share, a flat attire_spring_pct percent; … prorated by whole weeks …".
- A student-kept attire package is bought whole, so there is no rental term to prorate. The "rental" wording asserts a lease the base meaning denies.
- A January joiner pays half for a whole outfit (the half-price outfit is what no district publishes). This is the attire computation's only method factor.

**FL — SOURCE-FACTOR RED (floor after the strikes).**
- uil_travel_fee keeps rate/level/residence (R1) + booking (R6-candidate) with 0 method.
- arts_travel_fee keeps 3 R1 + 2 R6-candidates with 0 method.
- arts_attire_fee keeps 3 R1 + 1 R6-candidate with 0 method and is below its 5.
- uil_packet (4), arts_packet (5) and arts_first_installment (4) meet the floor.

Observations: the campus source differs by policy (stated in each rule); month-end due dates.

### Post-freeze notes (revision_3, written after reading "REWORK round 3 claims" and after the reveal at 23:16Z)
- **TR scope correction.** The claims argue A6 passes for the trip shares: tier 2 adds an input (the count) to tier 1's constant, and the reachable values 100 / 50–75 / 0–30 are distinct. That argument holds under XF A6's own PASS clause ("It PASSES if one tier adds an input or an operation"), so the "tiers coincide" half of TR is withdrawn. TR stands on its other half, which the claims do not address. In both ladders the fall-through tier ("otherwise" → single_trip_pct per remaining trip) differs from the factor's declared baseline (`trip_share: "100"`, which is tier 1's value and the rule's standard travel fee). The skill requires every factor's fall-through tier to be its baseline.
- **AT stands.** The claims grade rental_term_rule as an R3 proration "re-tiered inside the scope". But the priced component is the base's "Student-kept apparel package", "ordered in the student's name". R3 accepts prorations of time-based charges; a purchased outfit has no term. The rule's "rental-term" wording asserts a lease the base meaning denies.
- **R6 grades (AMENDMENT 1), unchanged from r2:**
  - booking_lead_tier, late_booking_tier, instrument_haul_tier: `R6-WAIVED (BLUEPRINT-KNOWN)`. Conditions 1–6 hold; condition 6 is still satisfied with TR struck (honest 3 → 2 slots; 1 used in UIL travel, 2 in arts travel).
  - concert_order_tier (claimed R2): accepted as an R2 timing schedule on a goods fee (rush order before the next concert); as untagged R6 it would also meet conditions 1–6.
  - plan_lead_tier and attire_placement_tier: R2. plan_count_tier: R5.
- **Final sweep of every class raised in any revision** (r1 P1–P5, F1–F5; r2 TS, IN, LF, A3, B8, RO, FL; r3 TR, AT), across the whole r3 charter:
  - P1 (rule-vs-compute timing): none.
  - P2 (rule condition with no compute): none (the attire gate is implemented; "posts no late registration fee" needs none). Observation WV: base meal-status waivers on schedule-posted fees, not engaged.
  - P3: none.
  - P4/B8 (false framing): AT's "rental-term" only.
  - P5/A2: none.
  - F1/A1/A7: none.
  - F2/A6: none (see TR correction).
  - F3 (scope tier): none. Every join/membership/rental "otherwise" tier is reachable inside the "registered after 2026-08-03" scope (the 28-day grace).
  - F4/realism: TR (structure), AT.
  - IN, LF, A3, B8, RO: closed, no member left.
  - FL: persists through TR and AT (uil_travel, arts_travel and arts_attire keep no valid method).

VERDICT revision_3: task0=RED task1=RED charter=TR,AT,FL

## revision_4

## charter_global_frozen (revision_4)
- Written before the round-4 claims and before any task JSON.
- Entry checks: worklog last line = "REWORK round 4: gates 7/7 green". I ran the snapshot: /tmp/erl0078_coord/snap_activity_fees_and_waivers_r4.txt, 7/7 OK.
- Hashes:
  - activity.extended.yaml fece691fecf2e5ea… (changed since r3); task_tools.py 0040d1ba3cee1ae1… (unchanged since r3, so action_binding_and_uuids carries forward on that hash).
  - Views r4/0 cf68e386fac4cff9… and r4/1 f3341034b40ec34b… are unchanged.
- realism_bar.md was updated (23:20Z, AMENDMENT 2: split prorations; the meal forecast shape; component exclusions vs X3). I read it in full and none of its three rulings is engaged by this charter.
- Base verbatim. The mechanical sweep is clean: basis/baseline/policy_source verbatim; every binding has a basis; no single-factor plain binding (plan_total is shared with the baseline); every factor's fall-through equals its baseline.

### What changed (diffed against the r3 reading)
- The params of uil_packet, uil_travel, arts_packet, arts_travel and arts_first_installment are identical to r3, and so are their factor lists and ladders. The exception is the two trip-share ladders, re-ordered: tier 1 "one or none" → single_trip_pct per trip; tier 2 "two or three" → n/4; fall-through "otherwise" → 100. Rule sentence and compute were re-ordered to match.
- activity_ext_arts_attire_fee:
  - rental_term_rule is removed;
  - new order_timing_tier (parameter): +individual_order_add (12) for a registration after arts_winter_order_date 2026-11-15, +winter_order_add (8) after arts_group_order_date 2026-09-15 and on or before 11-15, 0 otherwise;
  - concert_order_tier became rush_order_rule (method): fewer than 14 days from the packet to the next concert = rush_base_add 10 + rush_day_rate 2 per day short of 14; 14–27 days = 8; otherwise nothing;
  - the assembly sentence is generic ("amounts are added together first, never below 0.00, any further amounts are then added to that total …").

### Status of the round-3 RED items
- **TR: closed.**
  - Each trip share's fall-through tier ("otherwise … the full travel fee is due (100 percent)") now equals its declared baseline 100 and the rule's standard travel fee.
  - Compute `ts_left * single if ts_left <= 1 else (ts_left*100/4 if ts_left <= 3 else 100)` matches the re-ordered sentence.
  - A6 passes: tier 1 multiplies the count by a published per-trip percent, tier 2 divides the count by four, and the fall-through is constant.
  - Realism: R2/R3, a travel fee by the published trips remaining.
- **AT: closed.** No proration of the student-kept package remains. The two new attire factors:
  - **order_timing_tier.** R2, a published timing table keyed on the participation's recorded registration date against two published order dates: the group order, the winter re-order, and individual orders after that. A late joiner's outfit is ordered individually at a higher cost, which is a real ordering practice.
    - It does not contradict the base meaning ("Student-kept apparel package … ordered in the student's name").
    - X2: it is the only factor of this computation on the registration date.
  - **rush_order_rule.** R2, rush shipping by the days from the recorded packet received date to the next published concert.
    - A6: base + per-day vs flat vs nothing (it adds an input and an operation).
    - X2: it is the only factor on the packet date in this computation.
    - X4: figures are round, and the maximum is 10 + 2×14 = 38.
  - The method floor of the attire computation is now met: 4 P + 1 M.
- **FL: closed.** Every computation meets its floor and drawn count:
  - uil_packet 4 (3P/1M);
  - uil_travel 5 (4P/1M, booking R6-waived);
  - arts_packet 5;
  - arts_travel 6 (late booking and haul R6-waived);
  - arts_attire 5 (4P/1M);
  - arts_first_installment 4.

### Re-derived checks on the changed parts
- policy_conflict_scan:
  - Scopes are unchanged (task 0 {uil_packet, uil_travel}; task 1 {arts_packet, arts_travel, arts_attire, arts_first_installment}), disjoint and complete.
  - The attire overwrite tail is unchanged and still names both programs' schedules.
  - Base S4 (Fine Arts uniform package waivable), the cap exclusion of uniform packages and refund S5 are all in force with no conflict.
- rule_compute_equivalence (attire):
  - "after arts_winter_order_date" = `DAYS(winter, reg) > 0`; "after group … on or before winter" = the next branch with `> 0`.
  - The rush per-day sentence "rush_day_rate for each day short of rush_short_days" = `(rush_short_days − rr_days) × rate`, with "fewer than 14" as `< 14`.
  - The no-concert branch matches.
  - The order sentence (pre-share sum clamped at 0, then additions) = `MX(0, rate+level+campus) + order + rush`.
- prerequisite_graph / sentences: unchanged, with one resolving write per state.
- Realism sweep, all factors: R1 rates/levels/campus/residency; R3 join and membership; R2 trip shares, order timing, rush, plan lead and the placements; R5 plan count; R6-WAIVED booking_lead_tier, late_booking_tier, instrument_haul_tier (conditions 1–6 hold as graded in r2/r3, condition 6 with 4 honest per travel computation). No X1–X4 member found. AMENDMENT 2 rulings: no split proration, no meal forecast, no component exclusion in play.

### Observations (carried)
- The level tiers of the packet/travel policies read the participation's campus, while the campus and attire tiers read the enrollment campus. Each rule says which, and the two agree in both worlds.
- Month-end due-date convention.
- Base refund S5's rationale "ordered in the student's name at clearance" vs the attire schedule's ordering and rush timing measured from the packet's receipt. No normative conflict (no credit is computed here); render-surface note only.
- WV: meal-status waivers on schedule-posted fees, not engaged (both students are Paid).

### Post-freeze (revision_4): claims read and GT revealed at 23:27:26Z, after the r4 freeze (23:27:19Z)
- The round-4 claims (TR, AT, FL, 0.md#1–2, 1.md#1–4) agree with the closures I re-derived above. The claims add no item that the frozen derivation did not cover.
- Both tasks' GT matches the frozen r4 derivations value for value (see 0.md / 1.md r4).
- **Final sweep of every class raised in any revision** (r1 P1–P5, F1–F5; r2 TS, IN, LF, A3, B8, RO, FL; r3 TR, AT), across the whole r4 charter:
  - P1/P2/P3: no member. WV is an observation, not engaged.
  - P4/B8/AT (false framing; prorating a student-kept good): no member. The only prorations left are of time-based charges (membership/join shares by registration date; travel by the published trips remaining).
  - P5/A2: the assembly sentences are generic.
  - F1/A1/A7: every factor contributes against the baseline quantity, and no cap absorbs an addition.
  - F2/A6: every method's tiers differ in input or operation.
  - F3 and TR (scope tier; fall-through ≠ baseline): no member; the script sweep shows every fall-through equals its baseline.
  - F4/TS/IN/LF (realism): no X1–X4 member. The three R6 factors meet conditions 1–6: `R6-WAIVED (BLUEPRINT-KNOWN)`.
  - A3: no single-factor plain binding.
  - RO: record-test scope.
  - F5/FL: every floor and drawn count is met.

## closing_checklist (revision_4)
- The per-task files correspond one-to-one with tasks 0 and 1. _difficulty.md sits alongside them. revision_1–4 are preserved in order, each new derivation frozen before its comparison.
- Six extended policies are fully covered. The task scopes are disjoint ({uil_packet, uil_travel} / {arts_packet, arts_travel, arts_attire, arts_first_installment}).
- Task tools and GT are closed. The uuid8s are independent and frozen.
- Problem trees:
  - task 0: 1 prerequisite problem, 1 value_input edge, user write = packet;
  - task 1: 3 prerequisite problems, 5 value_input edges, user writes = packet and payment;
  - no cycles, and the difficulty-wide graph is acyclic.
- Factors: every computation declares a self-sufficient baseline and 4–6 factors. Each has at least 2 parameter and at least 1 method; each task has a multi-source factor (rate tiers) and a cross-difficulty factor (enroll). Every ladder has three tiers stated in its rule, distinct outcomes, and the fall-through equal to the baseline. Every factor bears weight on its world, and each baseline alone differs from gold.
- Gates on the final form: /tmp/erl0078_coord/snap_activity_fees_and_waivers_r4.txt, 7/7 OK (coordinator-run snapshot script, executed by me).
- Remaining observations (not RED): R6-WAIVED ×3 (BLUEPRINT-KNOWN); campus source per rule; month-end due-date convention; refund S5's "ordered … at clearance" rationale vs the attire timing; WV not engaged; zoned campus for an out-of-district residence.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

## charter_global_frozen (revision_5)
- Written before the round-5 claims and before any task JSON.
- Entry checks: worklog last line = "REWORK round 5: gates 7/7 green". I ran the snapshot: /tmp/erl0078_coord/snap_activity_fees_and_waivers_r5.txt, 7/7 OK.
- Hashes: activity.extended.yaml e104b76c3eba8bd9… (changed since r4); task_tools.py 0040d1ba3cee1ae1… (unchanged, so action_binding_and_uuids carries forward on that hash). Views r5/0 cf68e386… and r5/1 f3341034… are unchanged.
- This round's items are the renderer's scan-first findings, audits/render_source/activity_fees_and_waivers/render_r1.md: F1 (RED), F2 (low), F3 (low). Read in full. I read no other difficulty's render_source subdirectory.
- Base verbatim. Mechanical sweep clean: basis/baseline/policy_source/replaced_by verbatim; every binding has a basis; plan_total is the only plain binding used by one factor, and it is shared with the baseline sentence.
- Params of all six policies are identical to r4, value for value (compared against the r4 listing). The factor lists are unchanged.

### Audit-miss disclosure
Renderer F1 is a rule/compute divergence in activity_ext_arts_first_installment. It existed in my revision_2, _3 and _4 readings, and my rule_compute_equivalence passed it. Those PASS conclusions on that point were wrong. F2 (Sunflower ECC counted as elementary) was also present since r2 and was not caught. F3 I had recorded only as an observation ("whose campus"), not as a two-reading defect.

### Renderer items: closure check
- **F1: closed.**
  - New rule sentence: "Each fee is the latest entry of its fee component on the participation's ledger by posted date, the one recorded first when two share that date, and its net is that entry less the free_meal_waiver, reduced_meal_waiver and household_cap credits posted on it, never below 0.00".
  - Compute: `fi_*_entry = LATEST(… activity_ledger_id …, fee_component=…)`; `fi_*_fee = SUM(amount, …, activity_ledger_id=fi_*_entry)` (that single entry); `fi_*_credits` = the three credit_reason-filtered SUMs on `source_activity_ledger_id=fi_*_entry`; `fi_*_net = MX(0, fee − credits)`. This matches the sentence for all three components.
  - Tie: the DSL LATEST keeps the first row met on equal keys (strict `>`), which is "the one recorded first".
  - Absent entry: no entry gives net 0, consistent with "or that schedule owes none".
  - A billing_correction or other non-listed credit no longer lowers the net, as the rule says.
- **F2: closed.** Sunflower Early Childhood Center is removed from the elementary list in level_amount and trip_level_amount, which now read the five elementary schools named in blueprint.yaml line 5.
- **F3: closed.** The rules now say "for a participation at an elementary/middle school campus whose student's enrollment record shows grade …" (uil_packet, uil_travel, arts_travel), and the ladders say "the participation's campus is …". arts_packet and arts_attire keep "the campus on the student's district enrollment record". Every campus read now names its record, matching its compute (F('campus') vs CFIELD('enroll','campus',…)).

### New-defect / regression check on the changed parts
- The installment's baseline sentence and plan_total are unchanged in meaning (participation + travel + attire nets). The factors are unchanged.
- No other policy reads ledger credits.
- Prerequisite sentences and the graph are unchanged. Scopes are unchanged and disjoint.
- Realism grades are unchanged from r4 (R1/R2/R3/R5; R6-WAIVED booking_lead_tier, late_booking_tier, instrument_haul_tier). No X1–X4 member.

### Class sweep (renderer F1 is XF B1/B2: a read with no stated selection rule), all members, whole charter
- Ledger/records-log LATEST reads, each with a stated selection:
  - overnight permission "the received date of the latest overnight_travel_permission";
  - packet "the latest received date among the activity_document_received entries";
  - attire posting date "its posting date";
  - the three installment fee entries (now stated).
  All are dates or ids with a stated tie rule. Pass.
- Music CFIELD: "status checked_out (the first such checkout when several are on record)", with a status filter and a stated selection. Pass (observation: "first" has no stated order key).
- **Enrollment CFIELD reads: member found (EN).**
  - Every `CFIELD('enroll', <field>, student_id=…, school_year=…)` read takes the first matching row, with no status filter and no stated selection. Members:
    - uil_packet ar_grade, lv_grade, en_type;
    - uil_travel tr_grade, tl_grade, tn_type;
    - arts_packet ea_grade, el_grade, cp_campus, rs_type;
    - arts_travel ar_grade, tg_grade, tr_type;
    - arts_attire ak_grade, ag_grade, ac_campus.
  - The rules say "the student's district enrollment record for the school year", as if there were one. The enroll base charter produces two for one school year: "A student who withdrew may be registered again in the same school year with entry_type re_entry".

**EN — SOURCE-POLICY RED (XF B2: second record for the same school year, no stated selection), 16 reads in 5 policies (listed above).**
- Demonstration: a 2026-27 Fine Arts band student (grade 07) withdrawn on 2026-10-01 from a Non-Resident Transfer record at Hollis MS, then re-registered on 2026-11-02 as re_entry, Attendance Zone, at Ridgecrest MS after moving into the district.
  - Reading the withdrawn record: residency share 150 and campus program amount +10 (Hollis).
  - Reading the current record: residency 100 and campus 0.
  - The participation fee differs (e.g. (75 − 10 + 10) × 150% vs (75 − 10) × 100%).
- The rule's wording does not pick one, and the compute's first-match order is storage order.
- Neither task is affected: each student has one 2026-27 enrollment record. Task 0's 2025-26 record is excluded by school_year.

### Sweep of every class raised in any revision (r1 P1–P5, F1–F5; r2 TS, IN, LF, A3, B8, RO, FL; r3 TR, AT; r5 renderer F1–F3, EN)
- P1/P2/P3: no member.
- P4/B8/AT: no member.
- P5/A2: no member.
- F1/A1/A7: no member.
- F2/A6: no member.
- F3/TR (fall-through = baseline in every factor, script sweep): no member.
- F4/TS/IN/LF (realism): no member.
- A3: no member.
- RO: no member.
- F5/FL: floors met.
- Renderer F1/F2/F3: closed.
- B2 selection class: **EN** (16 reads).

### Post-freeze (revision_5): claims read and GT revealed at 00:07:42Z, after the r5 freeze (00:07:34Z)
- The round-5 claims cover F1, F2 and F3 and agree with my closure checks above. The claims do not raise the enrollment-record selection (EN); it is a new member of the renderer-F1 class, found in this round's class sweep.
- Both tasks' GT matches the frozen r5 derivations value for value. Task values, sensitivities and skip effects are unchanged from r4.
- Per-task status: EN is engaged in neither world (one 2026-27 enrollment record per student), so it is a charter-only RED and the tasks pass. The closing checklist of r4 stands for everything except EN.

VERDICT revision_5: task0=PASS task1=PASS charter=EN

## revision_6

## charter_global_frozen (revision_6)
- Written before the round-6 claims and before any task JSON.
- Entry checks: worklog last line = "REWORK round 6: gates 7/7 green". I ran the snapshot: /tmp/erl0078_coord/snap_activity_fees_and_waivers_r6.txt, 7/7 OK.
- Hashes: activity.extended.yaml dab248c303c40c97… (changed since r5); task_tools.py 0040d1ba3cee1ae1… (unchanged, so action_binding_and_uuids carries forward). Views r6/0 cf68e386… and r6/1 f3341034… are unchanged.
- Rulings are unchanged: realism_bar.md (mtime 2026-10-24 23:20, AMENDMENTS 1–2), owner_ruling.md and XF_recipe.md.
- Base verbatim. Mechanical sweep clean: basis/baseline/policy_source/replaced_by verbatim; every binding has a basis.

### What changed since r5
- The params of all six policies are identical to r5 (per-policy sha prefixes ecf11ff0 / f4823c50 / c9206bb7 / 3ea2ba6e / 9a4f4fe6 / 4720c789 match r5).
- The installment's factors are byte-identical to r5 (eb164cd9). The other five policies differ only in the ladder `when` text that names the enrollment record.
- All 16 enrollment reads now carry `status='enrolled'`. The rule sentences and ladder texts say "the student's district enrollment record in status enrolled for the school year"; every enrollment-record mention in a ladder carries the status.
- Every result, share, tier and placement binding is otherwise as in r5 (re-read line by line).

### Status of the round-5 RED item
**EN: closed.**
- Each `CFIELD('enroll', …, school_year=…, status='enrolled')` read (all 16, in uil_packet ×3, uil_travel ×3, arts_packet ×4, arts_travel ×3, arts_attire ×3) is now unique by the enroll base dedup: "A student is registered only when the student has no other enrollment for the same school year in status provisional or enrolled" (`max_open_enrollments_per_student_per_school_year: 1`). At most one record per student and year can be enrolled.
- A withdrawn first record and a re_entry second record can no longer both be selected; only the enrolled one is read.
- Absent case: no enrolled record (provisional, or withdrawn with no re-entry) gives 'none', so every enrollment-keyed tier falls through to its baseline. That is stated by the same sentences ("… otherwise"). Rule and compute agree.
- Observation: a provisional student pays the default tiers.

### Regression / new-defect check
- Scopes, prerequisite graph and sentences are unchanged.
- Every factor's fall-through still equals its baseline.
- No single-factor plain binding (plan_total is shared with the baseline).
- Realism grades are unchanged from r4/r5 (R1/R2/R3/R5; R6-WAIVED booking_lead_tier, late_booking_tier, instrument_haul_tier). No X1–X4 member.
- Renderer F1/F2/F3 closures hold. The installment net sentence and compute are unchanged; there is no Sunflower in the elementary lists; the campus reads name their record.

### Sweep of every class raised in any revision
Classes: r1 P1–P5, F1–F5; r2 TS, IN, LF, A3, B8, RO, FL; r3 TR, AT; r5 renderer F1–F3, EN.
- B2 selection reads:
  - enrollment: status-filtered and unique;
  - music: status filter plus "the first such checkout" (observation, carried);
  - ledger and log LATEST: stated, with a tie rule.
- No member of any class remains.

### Post-freeze (revision_6): claims read and GT revealed at 01:10:11Z, after the r6 freeze (01:10:04Z)
- The round-6 claims (EN, all 16 reads; the rules, ladders and cross_category reads updated; probes with a withdrawn decoy) agree with the closure check above. The claims raise nothing the frozen check did not cover.
- Both tasks' GT matches the frozen r6 derivations value for value. Writes, owners, order, reads, trees, skip effects, expected values, baselines and sensitivities are all unchanged from r5.

## closing_checklist (revision_6)
The r4 checklist stands, with EN now closed:
- One file per task.
- All six policies covered, with disjoint scopes.
- Uuid8s independent.
- Trees: task 0 has 1 prerequisite problem and 1 value_input edge; task 1 has 3 prerequisite problems and 5 value_input edges. A user write in each; the graph is acyclic.
- Every computation has 4–6 factors with at least 2 parameter and at least 1 method; every fall-through equals its baseline; every factor bears weight; each baseline alone differs from gold.
- Gates on the final form: snap_activity_fees_and_waivers_r6.txt, 7/7 OK.

Observations, not RED:
- R6-WAIVED ×3 (BLUEPRINT-KNOWN).
- A provisional student takes the default enrollment tiers.
- The music "first such checkout" has no order key.
- Month-end due dates.
- The refund S5 "ordered … at clearance" rationale vs the attire timing.
- WV is not engaged.
- A zoned campus is recorded for an out-of-district residence.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7 (seed-only round: KB auditor item S1)
- Entry checks: worklog last line = "REWORK round 7: gates 7/7 green". I ran the snapshot: /tmp/erl0078_coord/snap_activity_fees_and_waivers_r7.txt, 7/7 OK.
- Byte-identity: activity.extended.yaml dab248c303c40c97… and task_tools.py 0040d1ba3cee1ae1… both equal r6. Every charter-global section and the uuid section carry forward on those hashes; nothing is re-derived.
- Views:
  - r7/0.view.json cf68e386… is unchanged.
  - r7/1.view.json went from f3341034… to f359c32d….
  - A field-by-field diff of r6/1 against r7/1 shows exactly one change: instrument_checkouts d7032204-11c9-4802-98ac-56973f025ef0.due_back_date, 2027-05-27 → 2027-05-21.
  - frozen_time, user_scenario and every other row are identical.
- **S1: closed.**
  - The owning music charter has due_back_date "05-21" for Large Instrument Usage (Tuba, Cello, String Bass) (blueprint/products/music.yaml line 310; all five school-year types are 05-21, Summer 08-07).
  - The published KB docs/music/due_back_dates_and_late_return_charges_28fe31fa.json lists "Large Instrument Usage … | May 21" and "The five school-year usage types share the due-back date of May 21".
  - The re-seeded 2027-05-21 matches both (XF E1).
- No movement:
  - No extended policy reads due_back_date (0 occurrences in activity.extended.yaml); the instrument tiers read only variant_name, status and school_year.
  - Task 1's frozen derivation therefore stands as in r6: packet 75.00, travel 107.00, attire 62.00, first installment 225.25, with the same tiers and sensitivities.
  - Task 0 is untouched.
- No regression: the class sweep result of r6 carries forward on the identical charter and tools.
- GT check (read after the section above was on disk): both tasks' writes, owners, expected values, baselines and sensitivities are identical to r6. tasks/1.json initial_state carries due_back_date 2027-05-21.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN
