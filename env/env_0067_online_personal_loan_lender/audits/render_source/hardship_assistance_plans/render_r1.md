# Renderer findings — product hardship (d=hardship_assistance_plans), render round 1 (saved verbatim by the coordinator)

Renderer agent a392bef3bd69af260 scanned the source first and STOPPED with 0 documents written. Its report, verbatim:

### 1. Rule says one thing, compute does another (blocking)
Policy `hardship_ext_settlement_installment_term`, factor `balance_term`, second tier of `starting_term`.
- Rule: "a charged-off balance of proportional_term_max_basis or more on a loan charged off at least aged_months whole calendar months earlier allows only **the whole calendar months left before the account's sale review**, which falls sale_review_months whole calendar months after the charge-off date, a month counting as complete only when the later date reaches the charge-off day of the month …"
- Compute: `starting_term: "… ((K('sale_review_months') - months_since_charge_off) if months_since_charge_off >= K('aged_months') else …)"`, where `months_since_charge_off = MONTHS(charged_off_date, NOW)`.
- The compute takes 24 minus the months elapsed. That is not the whole months left before the sale review, except when today falls on the charge-off day of the month. On any other day the compute is one higher than the rule.
- Hypothetical example: charged off 2024-03-10, term recorded 2025-09-20, balance 7,000.00. The rule gives 5 whole months to the 2026-03-10 sale review; the compute gives 6. The result is held between 2 and 6, so the difference changes the settlement term.

### 2. Quantities defined outside the factor that uses them (blocking)
Policy `hardship_ext_trr_offer_payment`.
- `scheduled_installment` and `current_rate_monthly` are not bindings of any factor, so they belong to the computation document. Yet only the repayment-shape method reads them, in the `shape_code == 2` branch of `result`.
- Their `compute_basis` quotes come from the "Repayment shape:" sentence ("the principal part of its scheduled installment, being that installment less one month's interest on the unpaid principal at the loan's current rate …").
- The calculation itself ("level installment … at the program's plan_rate_percent …") never uses them. The computation document would therefore have to describe quantities only one factor uses, or the `repayment_shape` factor document would have to claim bindings it does not own. Either way the computation document and that factor document stop being independent.

### 3. One look-back rule serves several factors (lower severity, same class)
- `hardship_ext_rpp_offer_payment`: "In every look-back of this policy a ledger row counts as inside the stated months when fewer than that many whole calendar months separate its date from the decision date, a row dated exactly that many months before it falling outside them." This is the only boundary rule for the `arrears_base` 12-month window and the `autopay_record` 6-month window, and it is the `compute_basis` of `autopay_returns_6m`.
- `hardship_ext_scra_closing_installment`: "In every twelve-month look-back of this policy a ledger row counts when fewer than twelve whole calendar months separate its date from the day the line is scheduled." This serves both `autopay_relief` and `prepayment_relief`.
- Each factor's own sentence should carry its window boundary, as `prehardship_record` and the rate-reduction AutoPay factor already do.

### 4. Tool docstring conflicts with the rule in an edge case (low)
- `report_military_service_end_1d04825e` describes `end_date` as "the last loan due date the benefit applies to".
- `hardship_ext_scra_service_end_months` says "A benefit with no plan installment line records no plan months at all, 0, … and records the end of military service as its end date." That release date need not be a loan due date.

### 5. Observation, not blocking
`hardship_ext_settlement_offer_amount` has a rule sentence right after its second state-form prerequisite: "Where that Reduced Payment Plan request cannot be offered under its program's rules, the wait is lifted only by the hardship desk declining it under the base decision rules, so the settlement request is handed to the hardship desk with it instead of being priced in that contact."
- It names the action that clears the waited-on state, and it adds a handoff.
- It can be carried verbatim because the source says it, but it weakens the state-only wording the skill wants around that prerequisite.
