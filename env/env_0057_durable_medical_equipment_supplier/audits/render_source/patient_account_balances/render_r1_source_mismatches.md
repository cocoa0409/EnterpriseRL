# Source mismatches reported by the coverage renderer (agent ab5a9e75454a73fb9), round 1 — verbatim

*A factor tier, or the computation document, depends on another factor's output:*
1. **Crossover fee factor reads the flow factor.** `crossover_fee_composition` has the tier "when: the flow multiplier raises the stationary fee…", and the flow multiplier is the output of `crossover_flow_multiplier` (`s_flow_mult`).
2. **Crossover pricing factor reads three other factors.** `crossover_pricing_method` uses "the Medicaid monthly rate", computed as `s_medicaid_rate: RND(s_fee * s_usage_pct / 100 * s_rate_pct / 100 …)` — the outputs of three other factors. That rate is a non-factor binding the baseline never uses, so I rendered its definition in the pricing-method document while the computation document lists it in its covers to satisfy the gate.
3. **Prompt-pay speed points read the speed-reckoning factor.** `prompt_speed_points` is based on `p_speed_days`, which is the output of `prompt_speed_start_day`.
4. **Hardship burden points read the window factor.** `hardship_medical_burden_points` sums charges with `within_months=h_window_months`, which is the output of `hardship_burden_window_convention`.
5. **Revision new-charge factor reads the core-term factor.** `revision_new_charge_months` uses `within_months=m_due_so_far`, a binding of `revision_core_term_convention`.
6. **Prompt-pay computation depends on factor bindings.** The non-factor binding `p_eligible` reads `p_paid_amount` (payment-size factor), `p_paid_on` (speed factor) and `p_statement_date` (start-day factor).

*An extended rule disagrees with its own compute:*
7. **Prompt-pay base amount.** The rule says "applied once to the amount the qualifying payment paid", but the compute is `result: … RND(p_charge_amount * p_rate / 100 …)`, i.e. the charge amount.
8. **Prompt-pay statement date.** The rule says "the latest statement issued on the account before the payment", but the compute uses `p_statement_date: LATEST(… coverage_statement)`, the latest statement overall, with `DAYS(p_statement_date, p_paid_on) >= 0`.
9. **Prompt-pay rental lines.** The rule says "a monthly rental line of a wheelchair, an oxygen system or a PAP device", but the compute is `p_charge_source == 'mobility' or 'oxygen' or 'pap'`, which takes any line from those categories.
10. **Hardship lookback charges (plausible).** The rule says "a charge already open on the approval date and posted no more than `hardship_lookback_days` … before it receives the discount on the approval date", but `h_charge_covered` requires `DAYS(F('hardship_approved_date'), h_charge_date) >= 0`.
11. **Crossover ceiling (plausible).** The rule says "never exceeds the open amount of the charge it settles", but the compute is `result: MN(s_cost_share, …)`, which caps at the cost share instead.

*An extended rule narrows a base sentence that its overwrite list does not name:*
12. **Hardship timing.** The base `coverage_hardship` says "While it is in force, each charge of responsibility_type deductible, coinsurance, copay or repair_patient_share receives a coverage_adjustment…". The extended rule says a post-approval charge "receives it while it is still the account's most recently posted patient charge, and a covered charge that passes that moment without the discount keeps its amount". Only the "equal to the tier's discount_pct…" fragment is in the overwrite list.
13. **Crossover refusals.** The base `coverage_agg_coordination` says "When a secondary record exists, the secondary pays on those charges … a secondary payment refused for late filing leaves the charge with the patient". The extended rule says "a coinsurance charge from an older line that carries no crossover was refused at its turn and stays with the patient". This is not in the overwrite list.

*A retired clause is wider than what replaces it:*
14. Each of these clauses is retired for every case, but its replacement covers only one policy's case:
    - **Stacking cap.** "Adjustments on one charge never stack beyond its open amount…" is retired, but both replacements (hardship and prompt-pay) cover only those two discounts. Small-balance, missing-notice, claim-reversal and retro-Medicaid adjustments lose the cap.
    - **QMB active requirement.** "The QMB protection applies only while the Medicaid record is active…" is replaced by "…governs only adjustments posted for QMB protection", which no longer states that the record must be active.
    - **Secondary coinsurance share.** The clause "and on the coinsurance charge the percentage `as_secondary_coinsurance_cover_pct` of that charge…" is retired for all secondary payers, but its replacement covers only Medicaid crossover on oxygen lines.
    - **Payment posting and allocation.** Four `coverage_evt_payment` / `coverage_agg_payment_allocation` clauses are retired for all payments (exact-amount posting, the no-reposting duplicate check, oldest-first allocation, and the overpayment credit), but every replacement covers arrangement deposits only.

*A tool docstring claims an effect the tool body does not have (minor):*
15. **Statement effects.** The hardship and prompt-pay tools claim "…and on the next statement", `set_payment_arrangement` claims "the patient's statements then show the installment due each month", and `revise_payment_arrangement` claims "the patient's next statements ask for the new installment". None of the tool bodies writes a statement. I carried these sentences as the docstrings state them.

*Base wording carried as written:* `coverage_evt_adjustments` says "three adjustments exist" but lists four, and the `prompt_pay_window_days` parameter description says "after the first statement showing the charge" while the extended rule says the latest statement. The latter is for your base-issues log.
