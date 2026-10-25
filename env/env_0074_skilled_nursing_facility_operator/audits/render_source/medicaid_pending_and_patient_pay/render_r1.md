# Renderer scan-first findings — medicaid (render round 1, renderer agent af8ecfecc65472307, 2026-10-22)

Saved verbatim by the coordinator from the renderer's report. The renderer wrote no documents.

Gate passed (`VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN`). Source: tasks/medicaid_pending_and_patient_pay/medicaid.extended.yaml + task_tools.py (5 extended policies, 23 declared factors, 10 base policies, 5 tools). All compute_basis quotes are verbatim in their rules; prerequisite sentences are present in the blocked policies' rules. Half-up rounding as `RND(x + 0.000000001, 2)` is the DSL-KNOWN ruling and is not counted.

## Mismatches that block rendering

**M1 — `medicaid_ext_pending_advance_payment`, factor `pending_funds_applied`: the compute floors a figure at zero, but the rule and ladder do not.**
- Rule: "where the account is a non-Medicaid representative payee account and a Social Security benefit was received as payee within the last two months, the latest benefit received less the personal needs allowance, which the payee leaves for the resident's personal needs; otherwise nothing."
- Ladder tier 2 value: "the latest benefit received less P('personal_needs_allowance_monthly')"
- Assembly sentence (no floor on the figure itself): "figures entering the estimate change it before its floor at zero, and figures entering the advance are subtracted from or added to the estimate after that floor; the advance is never below zero and is rounded half up to the cent."
- Compute: `funds_applied = ... else (MX(0, latest_payee - P('personal_needs_allowance_monthly')) if (funds_tier == 'Resident Funds Account, Non-Medicaid Representative Payee' and payee_recent > 0) else 0)`
- Example: a non-Medicaid payee account whose latest benefit is 30.00, with a 45.00 personal needs allowance and a pending estimate of 500.00. Under the rule the funds figure is −15.00 and the advance is 515.00; the compute gives 500.00.
- Fix: either state "never below zero" for this figure in the rule and the ladder, or drop the `MX(0, …)`.

**M2 — `medicaid_ext_actual_month_cost_cap`, factor `actual_hospice_share_start`: the rule leaves out the tier condition on the inside-the-month branch.**
- Rule: "The first day of an actual-billed month priced at the hospice room-and-board share: where the case is on the Medical Assistance Hospice Room and Board tier and the hospice was elected before the month began, the month's first day; where the hospice election date falls inside the month, the election date; otherwise none (the first day of the next month)."
- Ladder tier 2: "the case is on that tier and the hospice election date falls inside the month"
- Compute: `hospice_share_start = ... else (hospice_election if (on_hospice_tier and hospice_election >= first_day and hospice_election < next_first_day) else next_first_day)`
- Example: a Standard Patient Pay case with a hospice election on day 11 of a reviewed 30-day month. Under the rule days 11–30 are priced at that tier's room-and-board share (0 percent); the compute prices all 30 days at the Medicaid daily rate.
- Caveat: the base case-maintenance rule moves a case with a hospice election onto the hospice tier, so this world needs the tier change to lag — unlikely, but a rule/ladder conflict that cannot be rendered both ways.
- Fix: add "the case is on that tier and" to the rule's second branch.

## Secondary items (fix in the same pass)
- **S1 — `medicaid_ext_pending_advance_payment`, ambiguous grouping.** Rule: "100 less the larger of 20 and the benefit days already used in the benefit period (the coverage's prior skilled nursing days in the period plus its covered days used) plus the days from the first day of the current month to the first day of the coming month, never below zero". Compute: `MX(0, 100 - MX(20, used + DAYS(current_first_day, coming_first_day)))`. The prose also reads as adding the days after the larger-of. Suggested: "the larger of 20 and the total of the benefit days already used … and the days from …".
- **S2 — no same-date tie sentence in `medicaid_ext_eligible_advance_payment` or `medicaid_ext_pending_advance_payment`** ("Where two records share the latest date…, the one posted first is read"), needed for their latest-by-date reads (latest payee benefit, pension and interest by posting date, latest actual-notice and estimate charge by service month).
- **S3 — a tie in `medicaid_ext_estimate_month_trueup` and `medicaid_ext_pending_estimate_cost_cap` is broken differently by rule and compute.** On equal end dates the compute picks the unpaid hold (`end_reason=('unpaid_private_hold' if unpaid_last_held >= maxed_last_held else 'private_hold_max_reached')` in `private_end_return`); the rule says "the one posted first is read".
- **S4 — `medicaid_ext_eligible_advance_payment` unstated edge branches for `coming_patient_pay`.** The compute gives 0 when the case carries neither an actual-notice nor an estimate charge and the notice takes effect after the coming month's first day; it treats a missing notice effective date as "after" (`or '9999-12-31'`). The rule states neither.

The task tool bodies are consistent with their docstrings.
