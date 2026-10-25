# Renderer findings, card render round 1 (renderer agent ac20976d745168353; saved verbatim by the coordinator — the harness blocked the renderer from writing its findings file). Renderer STOPPED before writing any document.
Source: tasks/worker_payroll_card_servicing/card.extended.yaml and task_tools.py. Policy indices: [0] card_ext_signed_loss_claim_credit, [1] reversal Premier/Elite, [2] final credit Premier/Elite, [3] card_ext_advantage_signed_claim_credit, [4] reversal Advantage, [5] final credit Advantage.

Checks that passed: every compute_basis quote verbatim in its rule (B5); no factor id a substring of a tool name (A8); every superseded_clause verbatim in its base rule; every prerequisite sentence verbatim in its own rule; no factor reads another factor's binding (A1); base policies and variants match the blueprint exactly.

## 1. B1 (blocking): the signed-claim credit floors at zero in compute, but no rule sentence says so — [0] and [3]
- Rule and baseline.rule [0]: "The signed claim credit is the claimed transfer less the amount withheld for the cardholder's liability, rounded half up to the cent once at the end: the claimed transfer is the disputed amount less any ATM owner surcharge rebate posted on the claimed transaction; the cardholder's liability is the lesser of the disputed amount and the liability limit less the liability already charged on the same loss, never below zero, ...". [3] says the same with "The claim form credit".
- Assembly sentence: "The adjustments below each either replace a figure of that method or add an amount to the credit; replacements apply first, additions after them, and the credit is rounded half up to the cent once at the end."
- Compute floors twice: `s_transfer = MX(0, s_disputed - s_rebate)`; `result = RND(MX(0, s_transfer - s_withheld + s_fee_back + s_allow) + 0.000000001, 2) if s_scope else 0` (the `t_` lines in [3] are the same).
- Gap: the rule floors only the liability, never the claimed transfer or the credit.
- Hypothetical witness (Advantage, in scope): a 40.00 out-of-network ATM withdrawal (a free one) with a 3.00 surcharge rebate; reported on time, nothing already charged, signed 3 business days after notice. Rule words: 37.00 − 40.00 + 1.95 = −1.05; compute: 0.
- Inner floor: a disputed amount is "at most the disputed transaction's amount", so it can be below the rebate. Example: disputed 2.00, rebate 3.00, withheld 2.00, fee 1.75, allowance 10.00 → compute 9.75; rule words 8.75.
- [1], [2], [4], [5] not affected ("never below zero" on transfer less liability covers the inner floor).
- Fix: state both floors in rule and baseline.rule, or remove the MX(0, …) calls from compute.

## 2. A4: plain bindings used by only one factor (should move into that factor's bindings)
| Policy | Binding | Only user | Rule text that defines it |
|---|---|---|---|
| [1] | v_report | vr_liability_limit | "and that order's date is the day the loss was reported, the report being late when it came more than timely_loss_report_business_days business days after the loss date" |
| [1] | v_prov_date | vr_service_allowance | "to the posting date of its provisional credit" |
| [1] | v_resolved | vr_investigation_allowance | "from the claim's notice date to its resolution date" |
| [1] | v_posted | vr_investigation_allowance | "A new-account transaction is one that posted no more than new_account_days calendar days after the account's first deposit date" |
| [2] | z_report | zc_liability_limit | same report/late sentence |
| [2] | z_posted | zc_investigation_allowance | same new-account sentence |
| [4] | w_report | wr_liability_limit | same report/late sentence |
| [4] | w_prov_date | wr_service_allowance | same posting-date phrase |
| [5] | y_report | yc_liability_limit | same report/late sentence |
| [5] | y_posted | yc_investigation_allowance | same new-account sentence |

## 3. B3/B1: report-day ladders have a gap and no tie rule — [1], [2] (replacement card fees, early pay cost), [4], [5] (early pay cost)
- Tiers cover: card replaced as "stolen", as "lost", and "for a claim with no report day, nothing" (early pay: "or no such transfer, nothing counts").
- Gap: a report day exists whenever "Paystride ordered a replacement card for the account that day" — any replacement order, including reason damaged or expiring; that case has no tier in the rule. Compute (v_repl, v_early, z_repl, z_early, w_early, y_early) gives 0; only the factor ladders say "otherwise".
- No tie rule: v_order (and z_, w_, y_) reads `LATEST('card_service_orders', 'service_order_id', date_field='order_date', event_type='card_replacement_order', order_date=v_notice)`; two replacement orders on the notice date tie, and the rule doesn't say which is read.
- Fix: add "otherwise nothing" and a tie rule, or restrict the report-day order to lost or stolen in both rule words and compute.

## 4. B6 (low): a framing clause reads as an untested condition — [1], [2], [4], [5]
"The early pay cost ... follows the Paystride Access ledger on the claim's report day, when the blocked card could not receive early pay: ..." — no binding reads card status or a block, so the "when" clause looks like a condition nothing tests.

## 5. Dead bindings (low)
s_posted [0], t_posted [3], w_posted [4] and w_resolved [4] are computed and quoted but used by nothing.

## 6. D1 (low): tool docstrings claim a scope the bodies don't enforce (bodies check only that the dispute exists, the amount is positive, and the plan)
- sign_card_loss_claim_statement / sign_card_theft_claim_form: docstrings say "a claim about a lost or stolen payroll card ..., a claim given by phone" and "the claim itself stays under investigation"; bodies don't check the dispute reason, the notice channel, or that the claim is under investigation. The theft tool's Args also say "the claim the statement confirms", though the tool signs a "written claim form".
- reverse_card_claim_credit / take_back_card_claim_excess: docstrings say "a resolved claim" and "pointing to that claim's provisional credit"; no status check, and a reversal posts with related_txn_id=None when no provisional credit exists.
- post_card_error_claim_credit / post_card_claim_settlement: docstrings say "resolved with an error found", but there is no status check.
