# Source mismatches reported by the loyalty renderer (agent a5e2b4185b40b3e2d), render round 1 — verbatim from its final report

1. **Factor reads another factor's output (missing-points credit).** Two factors, `event_multiplier` and `late_event_share`, both read `event_day`, which is the output of the `event_day_anchor` factor:
   - `event_entries: "COUNT('loyalty_points_ledger', ..., earn_source='bonus_event', entry_date=event_day)"`
   - `days_after_event: "DAYS(event_day, NOW) if event_day else 0"`
2. **Factor reads another factor's output (card floor).** The goodwill factor (`delay_goodwill`) reads the output of `delay_anchor`: `delay_days: "DAYS(delay_start, NOW)"`.
3. **Factor reads another factor's binding (return points deduction).** The `card_basis` factor reads `refund_dest`, a binding owned by `refund_basis`: `card_refunded: "card_credit - refund_tax if card_credit else (0 if refund_dest == 'merchandise_credit_card' else base_q)"`.
4. **Result assembled inside a factor binding (courtesy reissue).** The policy's result is just the courtesy-days binding, which the `return_share_rule` factor owns:
   - `result: "courtesy_days"`
   - `courtesy_days: "int(day_count / 2) if return_pct >= K('high_return_pct') else (day_count - K('mid_return_cut') if return_pct >= K('mid_return_pct') else day_count)"`
   The basis text for the result, "The courtesy validity days are the courtesy day count.", describes only the factor's default value.
5. **Rounding sentence vs rounding placement (return points deduction; plausible rather than certain).** The `replaced_by` text, which also sits in the rule, says the shares come after rounding: "each taken in proportion to the refunded amount that applies to it and rounded half up to whole points, and then adjusted by the return shares worked out below". But the compute applies the exchange share and event share before each part is rounded: `purchase_back: "int(base_pts * refund_share * exchange_share + 0.5)"` and `event_back: "int(event_pts * refund_share * event_claw + 0.5)"`. The rule's own later sentence agrees with the compute: "Before that rounding, the return purchase points are also multiplied by the return exchange share and the return bonus event points by the return event share."

Renderer note: four computation documents state factor-decided quantities at their default values as flat figures because those `baseline.rule` texts leave out how the factor quantities combine into the result.
