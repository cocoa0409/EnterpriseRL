# Renderer findings — product plan (difficulty payment_plan_servicing), render round 2
Saved verbatim (condensed headings kept) by the coordinator from renderer agent a4b22367d6fd6741c (2026-10-21). Scan-first STOP; no document written. Gate read: `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN`. Round-1 finding confirmed fixed (term_booked agrees with the floor-case booking sentence).

## 1. `plan_ext_signing_down_payment`: order of two non-commuting adjustments fixed only by one factor naming another (XF A3/A4)
- General order sentence (line ~2675) does not order the hold against the credit: "the signing share of the signing balance is taken first, amounts taken away from it come next with the figure never falling below zero, and amounts added to it come last."
- The order is set only inside the `post_offer_payment_credit` rule sentence (line ~2687), which names the `screening_hold` factor's effect: "A patient payment made after the offer on an account enrolled on the offer is credited against the down payment left after any hold, never below zero".
- Compute applies hold first, credit second: `share_left: RND(share_due * (100 - hold_pct) / 100 + 0.000001, 2)`; `result: RND(MX(0, share_left - credit) + first_part + 0.000001, 2)`.
- A factor document can't say "after any hold" (no factor document may describe another factor); without it the order is ambiguous and the readings differ (hypothetical: share 400.00, hold 50%, credit 150.00 → compute 50.00; credit before hold → 125.00).
- Second problem in the same policy: `share_left` is a non-factor binding, so the computation document has to cover it, but its only source text is the hold sentence ("…the part left at signing rounded half-up to the cent") — the hold factor's own content in a baseline binding.
- Possible fix: state hold-before-credit order in general words in the order sentence, drop "left after any hold" from the credit sentence, move `share_left` content into the hold factor.

## 2. `plan_ext_reage_schedule`: a non-factor binding carries one factor's own rule (XF A4)
- Line ~1255: `deferred: MX(0, deferrals - F('skip_count'))` — not among the `reage_deferrals` factor's bindings (`df_fpl`, `deferrals`), so the computation document must cover it.
- Its compute_basis is the deferral sentence itself: "…each less the skips already used on the plan (skip_count) and only on tiers whose own skip_payments_per_plan is smaller…"
- In the standard calculation it is always 0; "less skips already used" is used only by this one factor. The computation document would have to describe a deferral (a variation) or claim a binding its text never states.

## 3. `plan_ext_assistance_pause`: rule words vs compute when a plan has no next due date (XF B6)
- Rule (line ~776, in baseline.rule and the start_idx compute_basis): "the installments a pause considers are those falling due after the receipt date and on or after the plan's next due date (every one after the receipt date when the plan has no next due date), a receipt date before the first due date counting as one month before it so that no installment is counted before the first due date".
- Compute (line ~830): `start_idx: MX(-1, MX(MONTHS(F('first_due_date'), receipt), MONTHS(F('first_due_date'), F('next_due_date')) - 1)) if F('next_due_date') else MONTHS(F('first_due_date'), receipt)` — the branch without a next due date has no `MX(-1, …)`.
- Effect: a receipt more than a month before the first due date gives -2 or lower, pausing extra installments (e.g. first due 15th of month 3, receipt 20th of month 1 → -2). The pause tool does not check plan status. Low impact (only paid-off/cancelled plans lack a next due date).

## Clean
compute_basis quotes verbatim; prerequisite sentences present; overwrites scoped and siblings name each other; rounding placement matches; same-day ties match; month counting matches; method tiers change shape; docstrings match bodies; no factor id inside a tool name.
