# Renderer scan-first STOP, card render round 1 (saved verbatim by the coordinator from renderer agent a2a2e8e53ff96d538's reply; no docs written)

STOPPED before rendering. The source has rule-vs-compute mismatches, so no card documents were written.

**Gate:** `audits/policy_task/store_card_billing_and_disputes/_difficulty.md` ends with `VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN`, so the gate passed. I then checked `tasks/store_card_billing_and_disputes/card.extended.yaml` and `task_tools.py` against every point of `audits/render_source/XF_recipe.md`. A sweep script found every `compute_basis` quote, prerequisite sentence, `replaced_by`, superseded clause and baseline rule verbatim where it should be. The tool docstrings match their bodies and the forbidden-import check is clean.

## Source mismatches (recipe B.10 / B.11): rule words differ from compute on some inputs

1. **`card_ext_catch_up_payment`, binding `window_fees` (factor `restoration_fee`)**
   - Rule: "it is every late fee recorded on the account in the last two months less the fee reversals posted in that time, a month counted back from today to the same calendar day".
   - Compute: `MX(0, RND(SUM(late fees, 2m) - SUM(card_reverse_fee, 2m), 2))`.
   - The rule never says "never less than zero". The reversal sum covers every fee reversal in the window, including a `billing_error` reversal of a returned-payment fee or of an older late fee. Example: a standing late fee of 32.00 in the window plus a 43.00 reversal in the window gives -11.00 by the rule and 0.00 by compute. The same sentence states the shortfall's floor explicitly, which pushes a careful reader towards the negative figure.

2. **`card_ext_credit_balance_refund`, binding `payment_hold` (factor `payment_clearing`), not-clean tier**
   - Rule: "where the payment record is not clean, every payment credited in the last month is held, less the returned payments posted in that month".
   - Compute: `MX(0, RND(pay_1 - ret_1, 2))`.
   - The floor isn't in the words. This is an ordinary world: a payment credited 35 days ago and returned 3 days ago, with no other payment in the month. The rule gives a negative hold, which raises the refund above the credit balance; compute gives 0.

3. **`card_ext_line_increase`, binding `use_add` (factor `usage_line_addition`), below-10-percent tier**
   - Rule: "it is 5 percent of the payments credited on the account over the last 12 months less the payments returned unpaid in that time".
   - Compute: `RND(... * MX(0, use_payments_12) ..., 2)`.
   - The floor isn't in the words. It differs when payments credited before the window are returned inside it.

4. **`card_ext_line_increase`, binding `use_add`, both tiers**
   - Rule: "it is 5 percent of the highest new balance shown on any statement of the account" and "it is 5 percent of the payments credited ...". Neither states any rounding.
   - Compute rounds half up to the cent: `RND(K('use_add_pct') / 100 * ... + 0.000000001, 2)`. The result is then rounded down to a whole hundred.
   - The two readings give different new limits when the exact sum lands within half a cent below a hundred-dollar boundary. Example: 5 percent of a 99.99 balance is 4.9995 exactly and 5.00 after cent rounding.

## Placement notes (not blocking; I would have rendered these as placement)

Recipe A.3: these are non-factor bindings that only one factor uses, so `meta.covers` would put them in the computation document while their sentences belong in the factor document.

- **`card_ext_duplicate_final_credit`:** `post_date` is used only by `carried_days`. `carried_interest` ("The finance charge carried by the error is the duplicate excess times ... times the carried-error days ...") is a plain binding whose sentence names the `carried_error_days` quantity. If rendered in the computation document, it would name a factor quantity there. Suggest moving both into the `carried_error_days` bindings.
- **`card_ext_first_late_fee_courtesy`:** `fee_due` is used only by the lateness points and `fee_paid` only by the coverage points.
- **`card_ext_credit_balance_refund`:** `latest_stmt` and `latest_paid` are used only by `residual_interest_hold`.

## State left
- Nothing was written under `env/env_0080_big_box_general_merchandise_retailer/docs/card/`, and no staging directory was created.
- The `RENDER round 1: DOCS OK` line was not appended to `env/env_0080_big_box_general_merchandise_retailer/audits/render_source/store_card_billing_and_disputes/RENDER.log`.
- The scratch directory `/tmp/render_card_0080/` has been removed.

check_docs: not run (stopped at the source scan, no documents written)
