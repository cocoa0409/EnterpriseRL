# Renderer findings — product pos (d=practicepay_patient_financing), render round 1 (saved verbatim by the coordinator)

Renderer agent a15d98cac80cd91ef scanned the source first and STOPPED with 0 documents written. Its report, verbatim (line numbers refer to pos.extended.yaml at that time):

**D1. `pos_ext_returned_fee_relief` copies the whole late-fee relief computation into bindings that belong to no factor (most serious).**
- **Rule:** the rule (l.1967) states only *"and, where only one courtesy waiver remains within that number, no late-fee relief above 0.00 is owed on the plan's latest late fee under the late-fee relief schedule"*.
- **Compute:** that one phrase is quoted as the `compute_basis` of all 27 `lr_*` bindings (l.2087–2113). Those bindings (l.2026–2052) recompute late-fee relief in full, including its five factor ladders: `lr_relief_size`, `lr_timing_share`, `lr_autopay_share`, `lr_loan_share`, `lr_line_share`.
- **Params:** the policy also declares that schedule's constants as its own `params` (l.1940–1954): `relief_clearing_days` 3, `late_relief_cap_usd` 10.0, `late_relief_keep_usd` 5.0, quick/slow days 10/30, shares 0.9/0.75, AutoPay 5/1/0.95/0.9, loan 0.8/0.9, line 0.85/0.95. Its own rule states none of them.
- **Why it blocks:** the gate requires a returned-fee document to carry these constants, and its computation document owns the `lr_*` bindings. That document would have to restate all five of another policy's factor ladders, which breaks the separation between documents for `pos_ext_late_fee_relief`.

**D2. `pos_ext_late_fee_schedule`, factor `late_record_level`: the tiers leave a gap at exactly 6 months and overlap at exactly 12 months.**
- **Rule (l.2271–2274):** *"when the plan shows a late fee dated within the last 6 months, the late-fee level is repeat_late_fee_usd; when the plan shows no late fee dated within the last 12 months, the late-fee level is first_late_fee_usd; when the plan's most recent late fee is dated more than 6 but no more than 12 months back, the late-fee level is late_fee_usd."*
- **Window definition (l.2259):** "within the last N months" means fewer than N whole months.
- **Exactly 6 whole months back:** no tier matches by the text. The compute (l.2311–2313) gives 27.00.
- **Exactly 12 whole months back:** tier 2 and tier 3 both match. The compute gives 20.00.
- "Months back" is not defined anywhere.

**D3. A month-window convention sentence placed outside the factors that use it serves several factors (in all six policies).** Only 4 of the 6 sentences also serve non-factor quantities.
- **`pos_ext_payoff_quote`:** l.1373–1374, also in `baseline.rule` at l.1674: *"a window of the last N months covers entries dated fewer than N whole months before today, a month being whole once today's day of the month has reached the entry's day of the month."* No baseline binding uses a window. It serves only `return_record_hold`, `return_reason_hold`, `personal_loan_return_hold` and `flexline_return_hold`.
- **`pos_ext_late_fee_relief`:** l.1732–1734, *"In the late-fee relief schedule a window of the last N months … and a span of days is counted from the day after its start date through its end date."* It serves the courtesy-count gate plus `late_relief_size_rule`, `late_relief_loan_record` and `late_relief_flexline_record`. Its span half serves `late_relief_timing_band`.
- **`pos_ext_returned_fee_relief`:** l.1970–1972, the same sentence. It serves the gate plus `returned_relief_size_rule`, `returned_relief_loan_record` and `returned_relief_flexline_record`. Its span half serves `returned_relief_timing_band`.
- **`pos_ext_late_fee_schedule`:** l.2259–2261. It serves only `late_record_level`, `late_fee_loan_record` and `late_fee_flexline_record`.
- **`pos_ext_returned_item_fee`:** l.2496–2498, *"In this fee schedule a window of the last N months … and a span of days is counted …"*. The window half serves only `returned_item_level` and the two loan/FlexLine factors. The span half is used only by `one_penalty_limit_rule` (`within_grace`).
- **`pos_ext_payment_reset`:** l.2811–2812. It serves only `reset_loan_record`, `reset_flexline_record` and `reset_payment_record`.

**D4. `pos_ext_payment_reset`: the split-payment quantities are defined outside the factor that uses them.**
- **`di_part`:** a binding outside any factor whose `compute_basis` quotes the `reset_payment_method` factor's own sentence: *"the reset's deferred-interest part, which is the deferred interest billed on the plan but never more than the reset balance and bears no further interest"*.
- **`di_reset_payments`:** a binding outside any factor, defined by the sentence *"On a plan set to a split payment the reset payments are the due dates after the deferred-interest billing date through the final due date, …"* (l.2823–2825). That sentence names the factor's split tier and is used only by that tier.
- **`method_amount`:** a binding outside any factor that holds all three tier formulas. The factor's own bindings are only `di_billed_count` and `method_choice`.

**D5. `pos_ext_payment_reset`: the boundary on payments made "since the billing" is unstated.**
- **Rule (l.2821–2822):** *"only while no payment has posted on it since the billing"*.
- **Compute:** `last_pay_date > di_bill_date`, so a payment dated on the billing date does not bar a reset.
- **Fix:** the rule should say outright whether a same-day payment counts.

**D6. `pos_ext_returned_item_fee`: the definition of the grace period's last day sits only in a sentence outside the factor that uses it (lower severity).**
- **Sentence (l.2484–2486):** *"A returned-payment fee for a payment that was credited toward a monthly due date is decided once that due date's grace period has ended, the grace period's last day being the due date plus late_fee_grace_days calendar days, counted from the day after the due date."*
- **Use:** it is quoted as the `compute_basis` of `within_grace`, which belongs to `one_penalty_limit_rule`. No binding outside that factor uses it.

Points the renderer checked as fine: every `compute_basis` quote verbatim; no factor reads another factor's binding; return-code check matches the schema; tool docstrings agree with the rules; rounding statements match the compute.
