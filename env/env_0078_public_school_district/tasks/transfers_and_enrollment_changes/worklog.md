# worklog — transfers_and_enrollment_changes (enroll)

## REWORK round 2 — working notes (2026-10-24)
- Inputs read in full: audits/policy_task/transfers_and_enrollment_changes/{_difficulty.md,0.md,1.md}, audits/render_source/{realism_bar.md,XF_recipe.md,owner_ruling.md}. Files on disk = audited revision_1 (sha256 19a56d19f365c70e / 0ec8c84ea220751e).
- Dimension inventory (why the floor cannot be met with R1-R5 factors alone in this charter): the only numeric write
  events are the Pre-K (Tuition-Based) ledger rows; the type has one price (monthly_tuition 498.00), a flat late fee,
  full-month credits and a 14-day notice rule. Real, record-readable dimensions: repeat lateness, days past due (R2),
  an annual late-fee cap (R5), de minimis / whole-month scope (R5), Creek Kids Club funding / start-month proration /
  household combined-tuition cap / number of household children in Creek Kids Club (R1/R3/R5, care records), the
  pay-in-full offer and its timing window (R5/R2), plan terms (installment bands R5, down payment, meal-status extra
  installment R1), the meal-status basis month (R4/R3). The household's other Pre-K enrollments and the employee
  flag are not readable by the compute contract (coordinator ruling: no household-row targeting). About 21 such
  factors exist against the drawn 33; the remainder are R-shaped floor-fill factors, each listed in the claims.
- Plan: strike every X1-X4 factor; rebuild every ladder from the inventory; fix every structural finding; re-seed.
- r2: extended policies regenerated from /tmp/.../r2/spec_*.py (r1 copy kept in scratch)
- r2 worlds: T0 frozen 2026-12-17 (Nov+Dec unpaid, Oct 8 check, Nov late fee 40.00, Lucia wraparound start 12-16 CCS, Mateo in After-School Care); T1 basis on file 2026-12-17, Oct 5 check, late fees 35.00/50.00

## REWORK round 2 claims
- C-F1 (invented factors): every struck factor is removed, not reworded — AutoPay reductions/terms, entry-cohort/new-family, payment-window discounts, tenure/continuing-family, good standing, awaiting-determination, approval-letter reach, determination-window, status-level and repeat additions to the reversal, CCS hardship percentage on the late fee, advance_rate_basis, start-share taper, dual-program AutoPay, CCS cap share, plan-fee ACH half, eligibility-move/cohort/tenure plan reductions. Ladders rebuilt from R1–R5 shapes (list per policy in each task's design_rationale section "Realism record").
- C-F2 (floor): counts are back at the draw (6/5/4 and 6/4/4/4) with R-shaped factors; the dimension inventory at the top of this worklog shows the charter has ~21 published dimensions against 33 drawn slots, so the remaining slots are filled with R-shaped keys (payment method, months in arrears, Creek Kids Club children count, registration lead, payment gap) named as floor-fill in both dossiers — coordinator ruling requested on those, nothing X1–X4 kept.
- C-F3 (gating): scope guards of the basis-month credit, reversal and waiver now read the raw meal status / raw eligibility credits in plain bindings, never a factor's output; with any factor at baseline every other factor still moves its result (factor_sensitivity rows).
- C-F4 (unreachable tier): advance_rate_basis removed; months are priced at the most recent billing month's charge as a plain read; credits later received stay a credit balance refunded under the refund rule (also C-P9).
- C-P1 (assembly sentences): every combination sentence is now generic ("first replacements, then multipliers, then additions, then the limit"), order kept, no factor quantity named.
- C-P2 ("continuing family"): the term and every tenure factor are gone.
- C-P3 (framing clauses): "while the application was being determined", "waited on its determination" and "AutoPay household" are gone; every remaining condition is a stated record test.
- C-P4 (late-fee handling time): the overwrite's replaced_by fixes the fee on the records as they stand on the day the desk assesses it; the payment-window factor is gone.
- C-P5 (two due days): one due-day definition only — day tuition_due_day of the billing month.
- C-P6 (payment-method narrowing): declared scoped overwrite of enroll_tuition_payments_and_refunds in both payment policies, one shared replaced_by naming both portal-only cases and keeping every other payment on all accepted methods.
- C-P7 (sentence broader than resolver): the late-fee wait now names only the enrollment's most recent billing month, the month the late-fee rule assesses.
- C-P8 (plan ledger closure): no plan fee, no uncredited reductions; the rule states the installments together equal the open balance.
- C-P9 (advance does not settle months): prepaid months are priced at the most recent charge; later credits become a credit balance refunded under the refund rule, stated in the rule.
- C-P10 (one-factor sentences in the baseline): baselines now hold only the default sentence; due day and month selections are plain intro sentences used by several bindings.
- C-P11 (shared selections twice): the late-fee count/total and open balance are read once per factor in its own bindings (A1) and the plain selections (most recent billing month, its charge) are stated once in the intro.
- C-P12 (tie rule): every "most recent" read selects by billing_month, unique per enrollment for charges and late fees; no payment-date first-match read remains except the payment-gap factor's latest posted date (same-day payments give the same month count).
- T0-1: tenure removed (C-P2). T0-2: handling time fixed (C-P4). T0-3: seeded October/November late fees recomputed under the revised schedule on their posting days. T0-4: C-P9 closed. T0-5: C-F1/F2/F4 as above. T0-6: proof figures rewritten for the world of each step (open balance 1036.00 -> 1096.00 -> 1031.00, recomputed).
- T1-1: tenure removed. T1-2: framing clause removed; the fee-timing factor is a stated day count between two record dates. T1-3: plan fee and reductions removed (C-P8). T1-4: C-F1/F2/F3 as above.
- O-1..O-7: observations; O-2 residue (balance_at_notice null on benefit notices) left as is, unread by any formula.
- XF recipe re-check (scratch sweep.py / xf.py / crossfire.py): 0 non-verbatim basis quotes, 0 factor ids inside tool names, all prerequisite sentences verbatim, every factor reads only its own bindings, every other state_due policy owes 0.00 on both tasks' opening and terminal worlds (the late-fee rule's December figure in task 1 is not owed: one late fee per billing month already stands), all scored/baseline/sensitivity figures > 1e-6 from a half cent.
REWORK round 2: gates 7/7 green

## REWORK round 3 — working notes (XF pre-green tables; figures live in the tasks' computations and design_rationale)
Inputs read in full: audits/policy_task/transfers_and_enrollment_changes/_difficulty.md (revision_1 + revision_2 + closing checklist), 0.md, 1.md (both revisions); audits/render_source/realism_bar.md incl. AMENDMENT 1, XF_recipe.md, owner_ruling.md. Generator: scratch spec files -> enroll.extended.yaml (base section verbatim, blueprint untouched).

Draw (multiset): task 0 [6,5,4] -> combined credit 6, late fee 5, advance 4; task 1 [6,4,4,4] -> plan 6, basis credit 4, reversal 4, waiver 4.

Realism re-tag (every factor; R6 = AMENDMENT 1, record key in brackets):
- P2 late fee: repeat_lateness_schedule R1 | days_past_due_schedule R2 | yearly_late_fee_cap R5 | paper_payment_schedule R6 [payment_method of enroll_tuition_payment rows] | unpaid_month_method R6 [the month's tuition left unpaid = lesser of the month's charge and the open balance]. Struck/removed: late_fee_scope_rule (gating), months_in_arrears_schedule (X2). R6 need: drawn 5 - honest 3 = 2.
- P1 combined credit: wraparound_funding_tier R1 | care_month_proration R3 | combined_tuition_cap R5 | creek_kids_children_tier R6 [count of the household's care_enrollments in status active] | wraparound_registration_lead R6 [care registration_date -> start_date] | account_standing_reduction R6 [whole months of arrears]. R6 need: 6 - 3 = 3.
- P3 advance: pay_in_full_offer R1 | offer_timing_window R2 | arrears_offer_reduction R6 [whole months of arrears] | creek_kids_household_reduction R6 [count of active care_enrollments]. R6 need: 4 - 2 = 2.
- P4 basis credit: basis_month_convention R3 | basis_arrears_tier R6 [whole months of arrears] | basis_paper_tier R6 [payment_method] | household_size_tier R6 [count of the household's meal_accounts in status active]. Removed: basis_move_lead (X2). R6 need: 4 - 1 = 3.
- P5 reversal: credited_share_reversal R3-type | reversal_paper_tier R6 [payment_method] | reversal_arrears_tier R6 [whole months of arrears] | reversal_household_tier R6 [active meal_accounts count]. Removed: fee_status_timing (X2). R6 need: 3.
- P6 waiver (renamed enroll_ext_late_fee_transition_waiver; scope = eligibility credit on the month's charge, no meal-status test): standing_part_rule (mechanics) | courtesy_waiver_schedule R6 [count of the enrollment's late fee rows] | waiver_paper_tier R6 [payment_method] | waiver_household_tier R6 [active meal_accounts count]. Removed: meal_status_sliding_scale (X1 named), waiver_arrears_tier (would stack with the courtesy late-fee count, X2). R6 need: 3.
- P7 plan: plan_length_schedule R5 | down_payment_terms R5 | meal_status_extra_installment R1 | paper_down_addition R6 [payment_method] | closing_account_down R6 [enrollment variant_name State-Eligible + transfer_effective_date -> plan day] | household_size_installments R6 [active meal_accounts count]. Removed: arrears_down_addition, payment_gap_down_addition (X2 with down_payment_terms). R6 need: 6 - 3 = 3.
- Why no R1-R5 factor can take an R6 slot (all seven): the enroll charter prices Pre-K tuition by one flat monthly_tuition; campus level, grade band and plan are single-valued for tuition-based Pre-K; the sibling position and district-employee/residence flags sit on sibling enrollments or the customers row, which the frozen DSL cannot read (and the run-wide ruling forbids targeting the household row); a meal-status share on a late fee or late-fee credit is X1 (hardship share on a penalty fee); a second timing window or proration on dates another factor already uses is X2; the honest dimensions left are exactly the R1-R5 tags above.
- R6 conditions 2-5 for every R6 row: round district figures (2.00-25.00, 3 %); no federal/state rule or in-force base clause touched (no meal charge is involved; P2's add-ons price the late fee under its declared overwrite; the base is silent on bundle credits, late-fee reversals/waivers, prepay discounts and plans); none is loyalty, tenure, continuing family, AutoPay, new-family/re-entry, frequent-booking, a hardship share on a penalty fee (P5/P6 keys are payment method, arrears, late-fee count and household size, never a status or income test), an uplift beyond the charge (every credit is limited to its charge or fee) or a desk-posting-delay add-on (paper schedules count paper payments in the school year, never a posting lag); X2/X3: one factor per key per computation, none re-prices a recorded amount.

A1 factor-reads (transitive, xf.py): every factor reads only its own bindings and baseline quantities; assembly only in plain bindings.
A2/A5 order sentences (generic, order kept): P2 "first replacements and additions, then the limit"; P1 "replacements, multipliers, additions and reductions (floor 0), limit"; P3 "price months, replacements, multipliers, reductions of the discount (floor 0), take off" (the discount is the baseline's standard discount); P4/P5 "method, additions, limit"; P6 "additions to the standard waiver, then the limit"; P7 "set-asides (never above the open balance), installment count, divide and add".
A6 method shapes (all pairs pass): P2 unpaid_month_method pct x charge / flat parameter / nothing; P1 combined_tuition_cap excess with remittance input / excess without / nothing; P3 pay_in_full_offer half of one month (no months input) / nothing / pct x months x charge; P4 convention whole-or-half pick on the effective day / daily on a 30-day month / nothing; P5 whole fee / fee x credits / charge / nothing; P6 fee less credits / nothing (credits cover the fee) / whole fee; P7 down payment pct x open balance / that late fee / nothing.
A7 T1/T2: every factor moves its scored result alone on its task world (factor_sensitivity rows). T2 with all others at baseline holds on the task world for every factor except yearly_late_fee_cap (world: earlier fees in the year within one standard fee of the cap) and standing_part_rule (world: credits leaving less than the standard waiver), both producible. No base x rate split (P6 now has a flat standard baseline); no factor gates another (P2 scope rule removed; P3 baseline carries the standard discount). No two factors cancel on either world.
B1 edge probes: no charge in the month (MC 0) -> P2 owes nothing, arrears 0, no division; month fully paid / fee already posted / before the offset day -> P2 owes nothing; open balance <= 0 -> P2 nothing, P7 no plan; set-asides above a small balance -> capped at the open balance; months not yet posted 0 -> P3 = open balance; advance on or before the due day -> full discount; registration after start -> no lead; start in a later month -> share 0; DC status dated after the month -> 0 (floor); credits >= charge -> whole fee reversed (no division); credits >= fee -> waiver acts on nothing; no meal account / inactive account -> P4 nothing; first-month charge posted after day 5 -> due 5 days after posting (no instant lateness).
B2 decoy/absent table: charge/fee reads select by billing_month (one row per enrollment per billing month, grain) - decoys: earlier months, the November fee; absent -> 0/None, guarded. Care reads select the student's care enrollment by plan Pre-K Wraparound and status active (one non-closed enrollment per student per school year) - decoys: the sibling's After-School seat, a withdrawn/ended seat; absent -> scope 0. Rate basis: the seat's latest tuition charge of the month by posted date. Meal reads select the student's account in status active (one per student) - decoys: inactive/closed accounts, the sibling's account (household-size counts only). Counts: care_enrollments / meal_accounts in status active only.
B4 rounding sweep (hc.py): every scored, factor-baseline and all-baseline figure of both tasks more than 1e-6 from a half cent (the task 1 plan all-baseline that sat on a half cent is gone); only an unrecorded deletion-run counterfactual touches a half cent.
B5 sweep (sweep.py): 0 non-verbatim compute_basis quotes, 0 unquoted bindings, 0 factor ids inside tool names, all prerequisite sentences verbatim.
Cross-fire (crossfire.py): every other-task state_due policy owes 0.00 on both opening and terminal worlds (P2 now guards an already-posted month).
E1 seeds: late fees recomputed by the revised schedule as of their posting days (task 0 October/November; task 1 November/December); task 0's October check covers October and its fee; task 1's August (posted 08-20) is due 08-25 and was paid 08-21; task 1 benefit notices carry balance_at_notice 0.00.
Tools: credit_prek_late_fee_waiver_decba573 docstring/receipt reworded to the eligibility-transition waiver (no hardship wording); contracts unchanged.

## REWORK round 3 claims
- C-F1 (realism): every factor re-tagged R1-R5 or R6 (table above); X1-named meal_status_sliding_scale removed; X2 members (P2 arrears, P4 move lead, P5 fee timing, P7 arrears and payment gap) removed; P6 recast as an eligibility-transition waiver with no meal-status test.
- C-F2 (floor): drawn counts met as multisets (6/5/4 and 6/4/4/4) with R6 at exactly drawn minus honest per computation; check_extended/check_compute green.
- C-F3 (gating A1/A7/A10): P2 scope rule removed (state guard is a plain record test); P3 baseline now carries the standard discount so timing and account-standing act on a non-zero quantity; P6 base x rate split replaced by a flat standard waiver limited by the standing part.
- C-F4: stays closed (no unreachable non-baseline tier; P1 funding tiers all reachable within scope).
- C-F5 (fall-through = baseline): P1 cap ladder ends "otherwise nothing is added" = baseline; P2 cap ladder ends "no earlier late fee -> not limited" = baseline no_cap, middle tier restricted to earlier fees above zero.
- C-P1 (A2): P3 order sentence names only the baseline's discount and generic steps.
- C-P2..C-P12: remain closed (no tenure/continuing wording, no framing clauses, handling time stated, declared overwrites, plan ledger closure, P3 R2, baselines, single selections, billing_month tie rule).
- C-P13 (first-month due day): due day = day 5, or 5 days after a charge that posts after day 5, stated in P2's overwrite and month sentence and in P3's window; task 1 August needs no fee.
- C-P14 (A9): child counts read care_enrollments (one per child) in status active, not tuition rows; P4/P5 arrears worded "on the day the credit/reversal is posted", matching compute.
- C-P15 ("may"): P7 extra installments are a rule ("has the plan spread over"), no family choice.
- C-P16 (P5 selection): R0 and R1 both read the late fee posted for the most recent billing month (the latest month carrying a tuition charge); P6 uses the same selection.
- O-1: billing_correction kept (enum has no closer reason). O-2: task 1 benefit notices now carry balance_at_notice 0.00. O-3: intra-call docstring ordering words kept. O-4..O-7: superseded by the R-tag table. O-r2-1: kept (proration convention keyed on the status source, R3). O-r2-2: cap renamed "combined Pre-K and wraparound tuition cap", defining clause unchanged.
- T0-1..T0-4, T0-6: remain closed (figures re-derived for the new seed in prerequisite_closure).
- T0-5 / T0-r2-1: closed by C-F1/F2/F3/F5 above on all three computations (new factor_sensitivity rows).
- T1-1..T1-3: remain closed.
- T1-4 / T1-r2-4: closed by C-F1/F2/F3 (P6 split removed; P4/P5/P6/P7 re-tagged and refilled).
- T1-r2-1: closed by C-P15 (installments fixed by rule; persona needs no choice line).
- T1-r2-2 (half cent): verified (the plan all-baseline was exactly a half cent); every scored/baseline/sensitivity figure now > 1e-6 from a half cent (hc.py sweep).
- T1-r2-3 (E1 / C-P13): verified; due-day rule fixed so August owes nothing, and every seeded late fee in both tasks recomputed to the revised schedule as of its posting day.
- Floor-fill ruling (AMENDMENT 1): applied as tagged; no factor struck as X1 by name survives.
- Run-wide ruling (household row): every computation targets the enrollment; household counts read other categories' holdings only.
- Gate block: check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire run after the last write.
REWORK round 3: gates 7/7 green

## REWORK round 4 — working notes (late-fee policy only; figures live in the tasks)
Read in full: _difficulty.md revision_3 (charter_global_frozen, structure, factor_ladders, findings, closing checklist, VERDICT task0=RED task1=PASS charter=C-F6,C-F7), 0.md and 1.md revision_3 (incl. O-T1-r3). Both findings verified against the r3 charter before changing it: days_past_due_schedule priced the day the desk posts the single fee (R0 sets only an earliest day); unpaid_month_method added a percentage of the tuition charge to the flat fee (odd-cent seeds).
P2 enroll_ext_late_fee_assessment, drawn 5 (multiset unchanged; R6 = 5 - 2 honest = 3):
- repeat_lateness_schedule R1 (kept) | yearly_late_fee_cap R5, now the method factor (tiers: limit nothing / yearly_cap less earlier fees / not limited — differ by an input and an operation, A6; fall-through = baseline no_cap) | paper_payment_schedule R6 [payment_method] (kept, R6-WAIVED in r3) | unpaid_month_schedule R6 [the month's tuition left unpaid = lesser of the month's charge and the open balance] — flat round amounts, no percentage of any price | multi_program_household_cut R6 [count of the household's care_enrollments in status active] — flat round reduction taken off after the limit.
- Removed: days_past_due_schedule (X1 desk-posting-delay) and the percentage tier of the unpaid-month method (X2 percentage stack, R6 cond. 2).
- Why no R1-R5 factor takes the three R6 slots: the only R2 timing for an unpaid month is the posting day (X1); an R3 proration of the fee applies only to half-month charges and would re-price the posted proration (X3); a meal-status cut on a late fee is X1; campus, grade band and plan are single-valued for tuition-based Pre-K; sibling position and the employee/residence flags are unreadable (sibling holdings, customers row); a second cap would break A7 (one binding cap).
- R6 conditions 2-5: round figures (5.00-15.00); no base clause or federal/state rule touched (the late-fee sentence is under the declared overwrite); none is a named X1 mechanism (no posting-day key, no hardship/status test, no loyalty/tenure/new-family/AutoPay key); one factor per key in P2; nothing re-prices a recorded amount.
- Order sentence kept and extended in the same order: replacements and additions, then the limit, then reductions (floor 0.00 only where the fee owes nothing below it), then rounding. The reduction after the limit lets the cap and the reduction both move the fee (T1), every factor moves alone (T2; the cap on a world with earlier fees near yearly_cap). No two factors cancel.
- Class sweep across all 7 policies: no other factor is keyed on the day a desk posts a write (P3's window is the family's payment day, P7's closing schedule the plan day the parent pays, P1's lead the care registration/start dates); no other percentage of another price is stacked on a flat fee (P3's standard discount and P7's down payment act on tuition/balance, not on a flat fee).
- Seeds recomputed as of their posting days with the r4 schedule: task 0 October and November fees (only Mateo's Creek Kids Club enrollment active then) and the October check that pays October and its fee; task 1 November and December fees (no Creek Kids Club enrollment). Task 1 changes only through those two seeded rows and the figures that follow from them (all four computations, closure figures, rationale); its charter policies are unchanged.
- Re-checks: hist.py (seeded fees = schedule on their days), evalc.py (commute: late fee and credit in either order give the same figures; deletion runs recorded), hc.py (no scored, factor-baseline or all-baseline figure within 1e-6 of a half cent, including deletion runs), t2.py, sweep.py (0 non-verbatim quotes, 0 factor ids in tool names), xf.py (no factor reads another's binding), crossfire.py (every other-task state_due policy owes 0.00 on both worlds).

## REWORK round 4 claims
- C-F6: closed — the percentage tier is gone; the unpaid-month schedule adds flat round amounts only; no late-fee seed carries odd cents.
- C-F7: closed — days_past_due_schedule removed; no P2 factor depends on the day the fee is posted (class swept across all seven policies, no other member).
- C-F2 (P2 member): closed — P2 carries its drawn five factors with a method factor (yearly cap), R6 at drawn minus honest.
- T0-r3-1: closed by C-F6/C-F7/C-F2 on the scored late fee; task 0 figures, traces, closure and rationale recomputed.
- O-T1-r3: closed — task 1's seeded November/December late fees recomputed as of their posting days; its four computations, closure figures and rationale follow; no task 1 policy changed.
- C-F1, C-F3, C-F4, C-F5, C-P1..C-P16, T0-1..T0-6, T0-r2-1, T1-1..T1-4, T1-r2-1..T1-r2-4: remain closed (re-checked by the sweeps above; no change to P1, P3-P7 rules).
- O-1, O-3, O-r2-1: carried; O-2, O-r2-2: remain closed; R6-WAIVED factors of P1, P3-P7 unchanged.
- Run-wide ruling (household row): every computation still targets the enrollment.
- Gate block run after the last write: check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire.
REWORK round 4: gates 7/7 green

## REWORK round 5 — working notes (renderer scan-first findings render_r1.md F1–F7)
Read in full: audits/render_source/transfers_and_enrollment_changes/render_r1.md (the only file). Each finding was checked against enroll.extended.yaml before editing; all seven hold. Task worlds and every scored figure are unchanged (COMPUTE OK on the unchanged declared figures); only rule text, two compute guards and one tool docstring line changed.
- F1 verified: the P7 meal-status sentence named the plan-length schedule. Fixed: the sentence now says only "has the plan spread over free_extra more installments"; the order sentence (same order) now says "then the number of installments is fixed as the sum of the installment counts". Class sweep: no other factor sentence names another factor (only baseline quantities such as tuition_late_fee, credit_standard and the standard discount).
- F2 verified: P6's plain intro sentence named the standing-part rule. Fixed: the intro now limits the waiver to "that late fee" and covers "all or part" of it; the standing-part sentence alone states the limit to the part still standing. Class sweep: no other plain/computation sentence names a factor.
- F3 verified: "pays that late fee" had two readings. Fixed: "pays the amount of that late fee as posted, whatever credits stand against it" in the rule and the ladder, matching compute. Class sweep: the P5 and P6 late-fee reads are already pinned to "the late fee posted for that billing month".
- F4 verified: the convention named sources, not tiers, and left the carryover tiers unplaced. Fixed: each branch names its tiers. Household Application, Reduced-Price Meal Status and both Prior-Year Carryover tiers take the whole/half-month branch; Direct Certification and Categorical Eligibility take the calendar-day branch; every other tier gets nothing. The scope sentence names Free Meal Status / Reduced-Price Meal Status tiers.
- F5 verified: the full-reversal tier and the limit can reverse the whole fee. Fixed: "is reversed in whole or in part" in P5 R0, and "Post the reversal of all or part of" in the reversal tool's docstring. Class sweep: P6 now says "all or part of the late fee ... is waived".
- F6 verified: "the part of the month's tuition still unpaid" was defined only inside a factor sentence but was used by the plain guard. Fixed: one plain sentence in P2 defines the open balance and the unpaid part; the guard (lf_unpaid) and the factor quote it; the schedule sentence now only states its tiers.
- F7 verified: a status effective in the month after a short basis month gave half by the 31-day offset. Fixed: "took effect in a month after the basis month" is tested by MONTHS(first of basis month, effective date) >= 1, both in the convention and in the scope test, so such a child gets nothing and no additions. The calendar-day branch is capped at month_days_convention days, so a status from before the month credits the whole month. Probes (scratch probe.py): effective the next month -> 0.00; carryover tier effective before the month -> whole month; Direct Certification mid-month -> by calendar days; Paid -> 0.00.
- Re-checks after the edits: sweep.py (0 non-verbatim quotes), xf.py (no factor reads another's binding), crossfire.py (0.00 everywhere), hc.py (no half cents), hist.py (seeded late fees unchanged).

## REWORK round 5 claims
- F1: closed — the meal-status sentence names no other factor; the order sentence states that the installment counts are added (order kept).
- F2: closed — the plain waiver sentence limits to the late fee only; the standing-part sentence alone carries the part-still-standing limit.
- F3: closed — the one-late-fee down payment is pinned to the fee as posted, whatever credits stand against it, in the rule and the ladder.
- F4: closed — the basis-month convention names every meal tier per branch, carryover tiers included.
- F5: closed — the reversal rule and tool say "in whole or in part" / "all or part"; the waiver wording follows.
- F6: closed — the unpaid part and the open balance are defined once in a plain sentence used by both the guard and the schedule.
- F7: closed — "after the basis month" is a month test in both the convention and the scope; the calendar-day credit is capped at the whole month.
- Policy-audit items (revision_4 CLEAN): all remain closed; no factor, tag, count, world or scored figure changed.
REWORK round 5: gates 7/7 green

## REWORK round 6 — working notes (renderer scan-first findings render_r2.md)
Read in full: audits/render_source/transfers_and_enrollment_changes/RENDER.log, render_r1.md (F1-F7, closed in round 5 and confirmed closed by render_r2), render_r2.md.
- R2-F1 verified: enroll_ext_eligibility_month_credit.baseline.params listed month_days_convention. Only the basis_month_convention factor reads that key (its calendar-day tier); the baseline rule ("The basis-month credit is 0.00, the basis month remaining owed.") and every plain binding ignore it. Fixed by a metadata-only edit: baseline.params is now []. The regenerated yaml differs from the previous one in that line only, so no rule, compute, task world or scored figure changed.
- Class sweep across all seven policies' baseline.params:
  - The own-param keys credit_standard, school_year_billing_months and plan_installments_standard are each used by their baseline sentences.
  - The late fee's tuition_late_fee and tuition_due_day are type parameters, used by its baseline sentence and its plain month/guard sentences.
  - The reversal and the waiver list [].

## REWORK round 6 claims
- R2-F1: closed. The basis-month credit's baseline.params is [], and month_days_convention stays only in the basis_month_convention factor. No other policy lists a factor-only key.
- render_r1 F1-F7: remain closed (confirmed by render_r2; source unchanged apart from R2-F1).
- Policy-audit items (revision_5 CLEAN): all remain closed. No factor, tag, count, world or scored figure changed.
REWORK round 6: gates 7/7 green

## REWORK round 7 — working notes (policy audit revision_6, C-F8)
Read: _difficulty.md revisions 4-6 (new since my round-4 read; earlier revisions read in rounds 2-4), 0.md and 1.md revisions 4-6. C-F8 verified: P3's baseline paragraph names offer_pct while baseline.params listed school_year_billing_months; P6's baseline paragraph names waiver_standard while baseline.params was empty.
Fix, metadata only (the regenerated yaml differs from the previous one only in these baseline.params lines; no rule, compute, world or scored figure changed). Every policy's baseline.params now equals exactly the keys its baseline paragraph names:
- P1 enroll_ext_combined_program_credit: [credit_standard] (paragraph "... is credit_standard for the month.") - unchanged.
- P2 enroll_ext_late_fee_assessment: [tuition_late_fee] (paragraph "The late fee is the type's tuition_late_fee."). tuition_due_day was dropped: it lives in the plain due-day sentence and the guard (O-r6-1).
- P3 enroll_ext_advance_payment: [offer_pct] (paragraph "... less the standard discount of offer_pct percent of those months at that charge."). school_year_billing_months was dropped: it lives in the plain months-not-yet-posted sentence (O-r6-1).
- P4 enroll_ext_eligibility_month_credit: [] (paragraph names no key) - unchanged since round 6.
- P5 enroll_ext_late_fee_share_reversal: [] ("The reversal is 0.00.") - unchanged.
- P6 enroll_ext_late_fee_transition_waiver: [waiver_standard] ("The waiver is waiver_standard.").
- P7 enroll_ext_payment_plan_installment: [plan_installments_standard] ("The plan divides the open balance into plan_installments_standard equal installments ...") - unchanged.
Both directions are checked for all seven policies: no factor-only key is listed (R2-F1 class) and no key the baseline paragraph names is missing (C-F8 class). sweep.py is clean.

## REWORK round 7 claims
- C-F8: closed. P3 baseline.params = [offer_pct]; P6 baseline.params = [waiver_standard]. The two-way sweep over all seven policies leaves every list equal to the keys its baseline paragraph names.
- O-r6-1: closed. tuition_due_day (P2) and school_year_billing_months (P3) are no longer in baseline.params; both stay defined in their plain sentences.
- R2-F1: remains closed (P4 []).
- O-r5-1 and all other items (revision_5 CLEAN, render F1-F7): remain closed or carried. No rule, compute, factor, task world or scored figure changed.
REWORK round 7: gates 7/7 green

## REWORK round 8 — working notes (KB audit revision_1: S1, S2; seed only)
Read in full: audits/policy_kb/transfers_and_enrollment_changes/_difficulty.md, 0.md, 1.md. Published docs read: docs/care (due dates and late fees, late payment fee posting and amount, Workforce Solutions funding terms, subsidized credit base, monthly tuition posting and rate basis, registration and admission, registration fee, plan lineup) and the docs/enroll registration and residency pages. enroll.extended.yaml and task_tools.py were not touched (sha256 prefixes 0c3feb33baacf692 / f452cff1522de765 before and after).
- S1 verified. The care rule makes a month late when "the amounts applied by the due day leave any part of that month's tuition unpaid". Lucia's December charge posted 2026-12-09, before the day-10 due day (so the posted-after-due-day carve-out does not apply). No Workforce Solutions remittance had posted, and under the CCS terms the household owes the rest, "made late ... like any other balance". Fix: seeded one family ACH payment of the full 192.00 on the 2026-12-10 due day (reference 75631915). With no remittance posted yet the household owes the whole charge; paid by the due day, it owes no care late payment fee. The combined-program cap reads only the seat's tuition and remittance rows, so no scored read moves.
- S2 verified. Care admission needs "a student whose current district enrollment record is in status enrolled at a campus in the plan's offered campuses", and Mateo had none. Fix: seeded Mateo's 2026-27 Attendance Zone Enrollment at his zoned Alder Springs Elementary (which offers After-School 5 Days), grade 03, new_to_district, registered 2026-07-13 with residency verified 2026-07-20. It is therefore enrolled by his 2026-07-20 Creek Kids Club registration, and gold's find_enrollments(customer_id) returns it. Mateo is not part of any computation target (every compute targets Lucia's enrollment).
- Exhaustive other-category pass (both worlds, against the published owning docs as of each row's date):
  - Task 0 care rows. Registration fees: 40.00 each, household cap 100.00 not exceeded, each paid the same day so the seat is confirmed. Mateo's tuition: 248.00 After-School 5 Days standard rate (no meal account means no meal rate; household not an employee household), sibling position 1 because the CCS seat is left out. His August charge posted on seat confirmation 2026-07-20 and September-December on day 1, each paid by the 10th, so no late fees. Lucia's tuition: 384.00 x 50 % = 192.00, standard rate under CCS, posted on seat confirmation, now paid by its due day. No suspension or late fee owed at 2026-12-17.
  - Task 0 meals: Lucia's Paid account opened on her registration date.
  - Task 1 meals: both Reduced-Price accounts effective on the 2026-12-17 determination. The application was submitted 2026-12-08 and approved within 10 operating days, reaching all students of the household. Both approval letters are dated the same day, with balance_at_notice 0.00.
  - No further member found.
  - Accepted residue unchanged (no gold read): Mateo's meal account, Ivy's enrollment record, registration-document rows.
- Task 0 text updated (step 3 and step 6 objectives and the step 3 necessity, seed_consistency row for Mateo's enrollment, design_rationale seed card). The care payment row is not an enroll row, so its check lives in the rationale. Task 1 unchanged. All scored figures are unchanged (COMPUTE OK; evalc gives the same advance payment). crossfire.py shows 0.00 everywhere.
- K1 is a KB label the renderer fixes; no source change is needed (the source rules carry no Tuition-Based type scope, as the KB audit itself states).

## REWORK round 8 claims
- S1: closed. The family's full payment of Lucia's December care tuition is seeded on its due day; no care late payment fee is owed; no scored figure moves.
- S2: closed. Mateo's enrolled 2026-27 district enrollment record at Alder Springs Elementary is seeded, matching the care admission rule and the persona.
- Exhaustive other-category pass: done over every care and meals row of both worlds; no other member.
- K1: renderer's item; source unchanged (the source scopes match the KB audit's reading).
- O1-O5: KB observations, no source change. O5 (no type scope on the advance-payment rule) is outside both tasks' domain.
- Policy-audit items (revision_7 CLEAN), render items and baseline-params items: remain closed. The charter and tools are byte-identical.
REWORK round 8: gates 7/7 green
