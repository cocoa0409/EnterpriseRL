# Worklog — meal_account_and_benefits (env_0078)

Round 1 dossiers live in each task's design_rationale (tasks/0.json, tasks/1.json); plan.md carries the claim map.

## REWORK round 2 claims
- P-01: closed — meals_ext_collection_repayment rebuilt as the active-account repayment plan on the account's unpaid meal charges (balance below zero, deposits applied first per base s6); the year-end notice is no longer a balance classification, only the plan's up-front term capped at the unpaid charges; cover/graduate charges-taken first tier and the CEP prerequisite sentence no longer read a "year-end collection balance" (sweep: 0 stale hits in yaml, tools, tasks).
- P-02: closed — scope tails: the cover takes only a sibling withdrawn for a leaver reason other than moved_out_of_state / returned_to_home_country; the departure rollover only those two reasons; the graduate rollover only leaver reason graduated on a completed record ("A student who withdrew is never a graduate here"); each tail names the sibling cases it excludes.
- P-03: closed — the netting rule states no order and no prepayment trigger: "A netting is made only as part of working out a departed-balance cover for a student's active account, with the household's agreement"; the only order is the cover's own prerequisite sentence.
- P-04: closed — (a) no processor-refund promise: card deposits "stay on the account" (CEP refund) / "stay on the departed account" (departure rollover), matching the refund tool's docstring; (b) the reserve premise is now School Nutrition reconciling the final weeks of point-of-sale batches before money leaves a departed account, no meal reaches an inactive account, base meals_account_status s1 untouched.
- P-05: closed — tie rule stated: the online card deposits of the most recent card-deposit date stay (all of them when several post that date), computed as SUM over transaction_date = LATEST date; year-end notices are one per account per date.
- P-06: closed — installments are sized on the account's unpaid meal charges, not the notice amount, so no capped/uncapped reading exists.
- F-01: closed — every rate x count pair has a nonzero standard count: restore_days_standard 2 (cover), rollover_days_standard 2, reserve_days_standard 1 (departure), keep_days_standard 3 (CEP refund); T2 holds (per-day factors move result with others at baseline, check_compute OK). Residue: cep_refund_keep_milk's own baseline is 0, so keep_days x milk T2 rests on the 3-day standard only.
- F-02: closed — the restored/reserved-day standard-charge sentence is now used by the baseline itself (baselines restore two days / reserve one day at the elementary lunch charge).
- F-03: closed for coll_current_charges (removed); disproved for quote_added_meal, cover_restore_breakfast, departure_reserve_meal, rollover_restore_meal — XF A6: a pair "PASSES if one tier adds an input or an operation (floor, max/conditional pick, data-selected window, published parameter)"; the breakfast tier is a campus-conditional pick of a published price against the second-meal price and nothing.
- F-04: PARTIAL / RESIDUE — re-shaped to R-class: quote_serving_days (district 2026-27 calendar serving days by month), coll_size_installments, coll_up_front returned-deposit tier, check holds, lunch/meal tiers; coll_current_charges removed. RESIDUE needing a coordinator waiver (no R1-R5 lever in the frozen thin charter, the only computable field being meal_transactions.amount): quote_milk, quote_low_balance_buffer, cover_charges_taken, cover_restore_days, cover_restore_milk, netting_keep_days, netting_keep_milk, netting_extra_keep, plan_relocation, plan_payment_history, plan_recency, plan_up_front tier (b), coll_age, coll_payment_history, coll_grade_change, coll_up_front letter tier, departure_card_stays, cep_refund_card_reversal, departure_reserve_days, departure_reserve_milk, rollover_restore_days, rollover_restore_milk, rollover_buffer, rollover_charges_taken returned-deposit tier, cep_refund_keep_days, cep_refund_keep_milk, cep_refund_keep_extras.
- F-05: RESIDUE — floors and drawn counts kept (5/5/5/5 and 6/5/6/5, at least 2 parameter and 1 method each, multi-source and cross-difficulty per task: T0 quote_lunch_charge / netting_keep_lunch, T1 coll_grade_change / departure_reserve_lunch / rollover_restore_lunch / cep_refund_keep_days); meeting them in this charter requires the F-04 residue above, so F-04 and F-05 cannot both close without a waiver.
- O-1: kept with reason — action form on the repayment edges: the waited-on row (an online deposit on an active account dated today) is the same row kind deposit_meal_prepayment posts, so a state sentence cannot single out the repayment payment; fallback_reason states this.
- O-2: no change — "first" in deposit_meal_prepayment's docstring is the effect base states ("Any deposit is applied to unpaid meal charges first"), not a cross-problem order.
- O-3: no change — reduced/free lunch tiers coincide because base prices them so; neither task's figure depends on the coincidence.
- O-4: no change — the milk two-fifths rounding is exact at the cent (0.30) in every variant; the final RND is still the single result rounding.
- O-6: no change — enrollment-campus lunch vs account-campus breakfast never differ in a base-consistent world (the audit's own reading); no figure depends on the split.
- O-7: no change — Rafael's thin low-balance notice history is read by no computation.
- O-8: no change — the state_gate edges' gate names the field the condition tests (meal_transactions.event_type), as the edge schema accepts (check_extended OK).
- Figures after r2: T0 netting 32.15, cover 34.85, repayment 22.30, prepayment 84.35; T1 departure rollover 14.30, repayment-plan payment 30.80, graduate rollover 28.40, CEP refund 26.20.
- Gate block (full, no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY NOT OK (only the 8 unlock tool-name misses expected before KB render); CACHE-DIFF INFO.
REWORK round 2 closed with gates 7/7 green (superseded by round 3 below).

## REWORK round 3 claims
- P-01: stays closed. Both repayment plans work only on the account's unpaid meal charges (balance below zero, base s6). No notice amount is priced anywhere; the year-end-letter tier has been removed.
- P-02: stays closed. The scope tails are kept: cover = withdrawn for other leaver reasons; departure = moved_out_of_state / returned_to_home_country; graduate = graduated. The departure rollover now goes to the youngest active student whose account campus is not a CEP campus, and its rule says what happens when every active account is at a CEP campus.
- P-03: stays closed. The netting rule has a scope restriction only, with no order word.
- P-03b: closed. The repayment-plan trigger reads "or when School Nutrition quotes the repayment payment due today on an active meal account that carries unpaid meal charges of at least the online deposit minimum". It no longer restates the refund's wait, and no rule restates another rule's prerequisite from the depended-on side.
- P-04: stays closed. No processor-refund or late-posting premise is left; uncleared check and card deposits stay on the account as dated holds.
- P-05: stays closed. Holds sum every deposit of the method inside the window; the latest-card-payment read uses a date, so same-date ties give one value.
- P-06: stays closed. Installment size reads the unpaid meal charges through the size factor's own sum.
- P-07: closed. The prepayment rule says a request to repay in installments, or for the plan payment due today, follows the active repayment plan, never the quote. The active plan says a one-deposit request to bring an account current and fund it ahead follows the prepayment quote, never the plan. Each tail names the other.
- F-01: closed. Every rate x count pair has nonzero standards: a day charge of one elementary lunch, and twenty or five serving days. The keep-days x milk pair has been removed. T1 and T2 hold for all 42 factors (check_compute OK; the per-factor figures are in each task's computations).
- F-02: stays closed. The standard sentence and the balance sentence are the baseline in every policy, and every schedule sentence belongs to one factor.
- F-03: stays closed. Every method factor has tiers of different shape (XF A6): breakfast picks a campus price or nothing; extras pick milk, second-meal price or nothing; the balance basis adds unpaid charges, subtracts a positive balance or does nothing; up-front takes all unpaid, the returned amount or nothing.
- F-04: closed as far as the frozen charter allows. Every named X1 mechanism has been removed rather than reworded: the milk two-fifths share; the buffers; the notice-keyed restore days; the grade-keyed and notice-keyed keep days; the a la carte and extras keeps; the count-keyed card reversal; the reconciliation reserve; the charges-taken carve-outs; the installment tapers by leaver reason, deposit/notice history, months inactive, letter age and grade; and the letter up-front tier. The new factors are:
  - R3: serving days from the stated 2026-27 calendar, for the next month and for the days left in this month.
  - R1: lunch and breakfast prices by campus level / CEP / meal status, and the milk-only or second-meal price for what the student bought.
  - R2: holds on check deposits inside the bank return period and on card deposits inside the dispute window, longer after a returned deposit.
  - R5: installment threshold, returned checks paid up front, online minimum and maximum.
  - R4 / base s6: the receiving account's balance basis.
- F-04 flagged for a ruling: the netting keep, the CEP keep and the cover / graduate / departure funding all price a student's coming serving days with the district's published quote method (calendar x published prices). This is the one mechanism shape the coordinator may still class as a keep or restoration. Each computation reads one meal account, and the value_input floor forces two sibling transfers per tree, so no other shape can carry those slots.
- F-05: closed. The counts equal the draw (task 0: 5/5/5/5; task 1: 6/6/5/5), each computation has at least 2 parameter and 1 method factors, and each task has a multi-source factor (the card/check holds) and cross-difficulty factors (enrolled-campus lunch; household enrollment count). R6 factors, at the minimal count of 3 per plan (5 drawn - 2 honest R5):
  - plan_household_students and coll_household_students (key: the household's enrollment records in status enrolled, read from enroll);
  - plan_school_calendar and coll_school_calendar (key: the quote date's month);
  - plan_last_payment and coll_last_payment (key: lead days since the latest online card deposit).
  None has an R1-R5 lever: a plan payment has no price or calendar term; the charter's only plan terms are size, returned checks and the portal minimum/maximum.
- O-1: stays closed. The action-form fallbacks keep their stated reasons.
- O-2: no change. The docstring's "first" is the base effect wording.
- O-3: no change. The reduced/free tier coincidence comes from the base prices, and neither world uses it.
- O-4: closed. No factor rounds on its own any more; every result rounds once at the end.
- O-6: no change. Lunch prices come from the enrolled campus and breakfast from the account campus, which base keeps equal.
- O-7: no change. No computation reads Rafael's low-balance notices.
- O-8: no change. The state_gate edges' gate names the tested field.
- O-10: closed. The serving-day table now states every month of the 2026-27 calendar (and May/June none), and days left are counted on the stated closures.
- O-11: closed. The plan's trigger covers any quote of the payment due today, which includes the graduate rollover's wait.
- Sweep: compute_basis, baseline, policy_source and replaced_by texts are verbatim (asserted by the generator). Stale figures, mechanism words and edge texts have been swept from yaml, tools, tasks and rationale.
- World changes:
  - Task 0: Rafael's check returned 2026-09-09 replaces Lucia's returned check; Mateo's check replaced by a card deposit 2026-10-05; Tomas has a second card deposit 2026-09-14.
  - Task 1: Samuel's check returned 2026-10-12; Daniel's late deposits moved to 2026-08-10; Grace's deposits raised.
- Gate block (full suite, no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY NOT OK (only the 8 tool-name unlock misses expected before KB render); CACHE-DIFF INFO.
REWORK round 3: gates 7/7 green

## REWORK round 4 claims
- P-01, P-02, P-03, P-03b, P-04, P-05, P-06, P-07: stay closed. The scope tails, the two-way tails between the prepayment and the active plan, and the prerequisite sentences are unchanged. No notice amount is priced (the R6 year-end-notice term below only counts installments), and the hold windows still sum every deposit of the method.
- F-01: stays closed. Every rate x count pair keeps nonzero standards (a day charge of one elementary lunch, or one milk carton in the CEP keep, times twenty or five serving days); T1 and T2 hold for all 42 factors (check_compute OK).
- F-02: stays closed. The standard sentence and the balance sentence are the baseline of every policy; every schedule sentence belongs to one factor.
- F-03: closed across every policy.
  - The four breakfast factors are parameters with three distinct values: the secondary charge, the elementary charge at a non-CEP campus, and nothing when no breakfast was bought or the campus is CEP.
  - The three balance-basis factors are removed; the receiving balance is plain arithmetic in each standard.
  - The extras ladders are replaced by milk and second-meal method factors whose tiers differ in input (A6): the published price on every counted day for a regular buyer (four days or more); last month's recorded spending once for an occasional buyer; nothing.
  - Every computation now carries at least one honest method.
- F-04: stays closed for every earlier X1 member, none reintroduced.
  - The coordinator ruling on O-12 is applied. The calendar x published price shape is the plain amount basis of the prepayment, and of the cover, netting keep, CEP keep, graduate and departure rollovers. Each rule states the household's stated purpose, and each persona states that purpose explicitly in the parent's own words.
  - The CEP refund snack keep (a la carte prices recorded in the month) is kept only because the parent asks for it.
- F-05: closed.
  - Counts equal the draw (task 0: 5/5/5/5; task 1: 6/6/5/5), each with at least 2 parameter and 1 method factors, all R1/R2/R3/R5 except the plan terms.
  - R6 at the minimal count: inactive plan 3 (household enrolled count, quote month, days since the latest online card deposit); active plan 4 (the same three plus the year-end collection notice, keyed on a recorded notice and its stated balance).
  - None has an R1-R5 lever, because a plan payment has no price or calendar term.
- F-06: closed. One serving-day count per computation. It runs either from the day after the date through the end of the next month (prepayment, netting keep, departure) or for the days left in the month (cover, graduate, CEP keep), on the stated 2026-27 calendar.
- F-07: closed.
  - Cover, graduate and departure standards now subtract the receiving balance, so they clear the unpaid charges.
  - The CEP standard keeps five days of one milk carton; no lunch is kept at a CEP campus, and the CEP lunch factor is removed.
  - departure_lunch has no CEP tier. Its tiers are secondary, elementary, and no lunch when the student holds no enrollment record in status enrolled; all are reachable.
- O-1, O-2, O-3, O-4, O-6, O-7, O-8, O-10, O-11: unchanged from round 3 (closed or carried with the stated reasons).
- O-12: ruled by the coordinator and applied as described under F-04.
- O-13: closed. The last-payment terms read "thirty days or fewer before the quote date, counting the days from the deposit date to the quote date" and "more than sixty days"; the compute uses DAYS(deposit, quote) <= 30 and > 60.
- R6-WAIVED x6: the round-3 R6 factors keep their keys, plus the new coll_year_end_notice.
- World changes:
  - Task 0: Lucia, an extra card deposit and a second meal; Mateo, two second meals; Tomas's second deposit raised so the cover is owed.
  - Task 1: Samuel and Esther buy second meals; Esther's milk on three days; Esther's and Grace's deposits raised.
- Sweep: stale figures, factor names and mechanism words are swept from the yaml, tools, tasks and rationale; compute_basis, baseline, policy_source and replaced_by texts are verbatim (asserted by the generator).
- Gate block (full suite, no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY NOT OK (only the 8 tool-name unlock misses expected before KB render); CACHE-DIFF INFO.
REWORK round 4: gates 7/7 green

## REWORK round 5 claims
- P-01r: closed. coll_year_end_notice is removed, and no compute reads meal_notices any more, so base s6 governs every balance. Its slot is taken by coll_campus_level (R6; key: the campus level of the student's enrollment record in status enrolled). No R1-R5 lever exists for it: a plan payment has no price or calendar term. The R6 count stays minimal (6 drawn - 2 honest = 4).
- P-08: closed across all 16 milk and second-meal schedules. The rules now say "four (regular_buys) or more purchases" and "one to three purchases", which is what the compute counts. Every remaining "days" in a rule is a serving-day count: a distinct calendar weekday less the stated closures.
- P-09: closed. The CEP keep is defined once, by its schedules ("as the schedules below count it ... the keep is defined only by those schedules"). The standard is the whole balance, with nothing kept and nothing held.
- F-07: closed across every factor; every fall-through tier now equals its baseline.
  - CEP milk has a nothing baseline, and the CEP serving-day count is plain.
  - The days-left ladders of the cover and graduate rollover now fall through to their standard five outside the 2026-27 year.
  - departure_lunch is removed. The departure prices lunch by base pricing at the non-CEP receiver's account campus, as a plain amount, so it has no unreal "not attending" tier.
- Task-1 persona: closed under AMENDMENT 2. The persona states the household's purposes only (Esther's keep this month; Grace's leftover first toward anything a child still owes, then that child's meals and extras this month; Daniel's toward meals and extras through November). It names no receiving account and no amount, and the June letter line is gone.
- O-12: the ruling is now recorded as AMENDMENT 2 and is applied as above.
- O-14: the transfers' rules state the household's purpose as their plain amount basis, per AMENDMENT 2.
- O-15: task 0's persona states only the household's purposes (the receiving child is the caller's own root student). It is unchanged, since task 0 passed revision_4.
- Other ids (P-02 to P-07, P-03b, F-01 to F-06, O-1 to O-4, O-6 to O-8, O-10, O-11, O-13): stay closed or carried as in round 4.
  - Counts equal the draw (task 0: 5/5/5/5; task 1: CEP 5, plan 6, graduate 6, departure 5).
  - Each computation has at least 2 parameter and 1 method factors.
  - Each task keeps a multi-source factor (the holds) and cross-difficulty factors (lunch; household count; campus level).
- Task 0: only wording changed (the purchases phrasing; the cover's days ladder fall-through). Every task-0 figure is unchanged.
- Task 1 world: Samuel buys two a la carte items in the month (the graduate and departure snacks schedules), and Grace's deposit was raised so the rollover stays owed.
- Sweep: stale figures, factor names (year-end notice, departure lunch, CEP keep days) and wording are swept from the yaml, tasks and rationale; compute_basis, baseline, policy_source and replaced_by texts are verbatim.
- Gate block (full suite, no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY NOT OK (only the 8 tool-name unlock misses expected before KB render); CACHE-DIFF INFO.
REWORK round 5: gates 7/7 green

## REWORK round 6 claims
- F1: verified and closed. The departure standard now reads "of one reimbursable lunch at the lunch charge the departure rollover counts". The plain campus-priced lunch sentence is part of baseline.rule (params now list both the elementary and the secondary lunch charge), so the computation document states the same lunch the compute uses. Class sweep: no other policy has a plain binding that its baseline contradicts (every other lunch is a declared factor whose baseline is the elementary charge).
- F2: verified and closed.
  - The CEP sentence that listed the keep's components and the held deposits is removed. The CEP assembly sentence is now generic: "first every amount the schedules keep is added together, which gives the keep; then the keep and every deposit the schedules hold back are subtracted".
  - Class sweep: the netting's opening sentence also listed its keep and hold quantities, and it is now generic ("for the purpose it states for the giving account's own student: part of another active account's balance is moved ..."). Order sentences are unchanged.
  - The cover, graduate and departure openings state only the household purpose, which AMENDMENT 2 requires.
- F3: verified and closed. The CEP refund no longer has a plain serving-day count. Each per-day item schedule (cep_refund_keep_milk, cep_refund_keep_second_meal) owns its own count of the serving days left in the month, and keeps its price for those days only for a regular buyer. The computation document therefore stays the plain whole-balance calculation, with no undeclared modifier. Factor count, method shapes, T1/T2 and every figure are unchanged.
- F4: verified and closed. The transfer_idle_sibling_balance_b810dc58 docstring no longer says "that carries unpaid meal charges". Class sweep: every other docstring matches its rule's scope (cover purpose, CEP campus, active-plan scope, base s6 wording).
- Policy-audit items (revision_5 CLEAN): every closed item stays closed. No world, persona, factor count, tier or figure changed, and every combination sentence keeps its order.
- Gate block (full suite, no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; TRACEABILITY NOT OK (only the 8 tool-name unlock misses expected before KB render); CACHE-DIFF INFO.
REWORK round 6: gates 7/7 green
