# Renderer findings — product hecm, render round 1 (agent af7b474ee21d1f58c, 2026-10-15)
Saved verbatim by the coordinator. The renderer stopped before writing any document (both mismatches sit in computation documents).

Clean: every compute_basis quote verbatim; every superseded clause verbatim in its base rule and every replaced_by in its extended rule; all three prerequisite sentences in their blocked rules; task_tools docstrings state nothing the code doesn't do (fixed 20.00 fee = payment_plan_change_fee on every plan allowing changes); 12/1/2/36-month windows match "after the same day of the month N months before"; rule and compute agree on every branch of check_void, payment_release, reinstatement_restore and payment_designation; the draw request channel list has exactly three values.

**Mismatch 1 — draw ceiling, first-anniversary fallback (rule vs compute).**
- The rule says: "The first anniversary is the same day number in the month first_year_period_months calendar months after the closing date, falling back to the last day of that month when that day does not exist." The same sentence is in the base draw rule.
- The compute uses `before_anniv: MONTHS(F('closing_date'), NOW) < P('first_year_period_months')`. `MONTHS` subtracts one month when the current day number is lower than the closing day number.
- The two disagree on the fallback day. For a loan closed 2024-02-29 and handled 2025-02-28, the rule says the anniversary has arrived, so the drawable figure is the `available_line`. The compute returns `MONTHS = 11`, so it still treats the loan as in its first year and takes the lesser of the line and the first-year room.
- With `first_year_period_months` at 12 on every plan, only a Feb-29 closing can reach this. It is narrow but real: the rule states a branch the compute never takes.

**Mismatch 2 — payment reset, committed amount for a Tenure or Term target (base clause in force vs extended rule and compute).**
- These base clauses are not retired by any overwrite: "Processing happens in this order on the handling date: when the current plan pays scheduled payments, the present value of the payments not yet made returns to the available line as one hecm_line_release; then, when the target plan pays scheduled payments, the committed amount leaves the available line…" and "For a change into the Tenure or Term plan the whole available line after any release is committed".
- The extended reset rule's standard paragraph says the committed amount is "…the whole available_line for the HECM Tenure Payment Plan or HECM Term Payment Plan". The compute matches it: `committed: … (line if (req_plan == 'HECM Tenure Payment Plan' or req_plan == 'HECM Term Payment Plan') …)` with `line: F('available_line')`, so no release is added.
- `process_payout_plan_change_72a1f37c` can't book a release either; it books only a commitment and the fee.
- So when the loan's current plan already pays scheduled payments, the base requires a release first and commits the larger post-release line, while the compute commits the pre-release line. That changes the new scheduled payment. A Modified target also leaves the base's required release with no tool to book it.
- Fix needed: an overwrite on the "after any release" and processing-order clauses, or a rule scoped to a current plan without scheduled payments.

**Non-blocking issue (recipe point 6) — draw ceiling overwrite #1, "first-year draws".**
- The base clause used `hecm_msr_first_year_draws`: draw postings within the window, less reversals of those draws. The `replaced_by` swaps in "the first-year draws", which the extended rule defines as "every advance posting of type loc_draw on the loan less every return entry crediting a draw back to the line".
- After a stopped check is settled, its reversal is the settlement (draw amount plus interest, premium and compounding), but its return entry is only the draw amount. So the two definitions differ, and the general first-year limit for ordinary draws changes too, not only for a ceiling-sized request.
- The base `formula` (`first_year_headroom`, `max_draw_first_year`) still uses the measure, so the product would carry two definitions of the first-year room.
- This can actually come up in this difficulty's own chain: check void, then draw ceiling, on a loan still before its first anniversary.
