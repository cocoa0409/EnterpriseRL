# Renderer source-scan findings — product credit, render round 1 (renderer agentId a4d7f10aa813c2839)
Saved verbatim by the coordinator from the renderer's final report (the renderer stopped before writing any document; gate line read `VERDICT revision_12: task0=PASS task1=PASS charter=CLEAN`).

The problem is the same in both findings. Records that a factor and a plain binding share are declared as that factor's bindings, so a plain binding reads them. The recipe says a shared record selection must be a plain binding stated once in the rule, and that no factor may be gated through another. Rendering it as it stands would force the computation document to name or restate a factor's quantity. That breaks the covers single-home rule and the "computation document never names a factor's quantity" rule, so it can't be rendered without working around the source.

**Finding 1: the scope binding reads a binding of `contract_share_of_rate`.**
- File: `env/env_0068_industrial_mro_distributor/tasks/d1_credit_account_billing_and_credits/credit.extended.yaml`
- Compute bindings:
  - `in_scope: "live_n == 1 and pa_in_force"` is plain.
  - `pa_in_force`, built from `inv_date`, `pa_eff` and `pa_end`, is listed in `factors[contract_share_of_rate].bindings`.
- Rule sentence (basis of `in_scope`, `pa_in_force`, `inv_date`, `pa_eff`, `pa_end`): "This rule covers only an invoice dated inside the current term, from its effective date through its expiration date, of the customer's live Contract Pricing Agreement, meaning its one agreement whose status is active or renewal pending; for every other invoice, including any invoice of a customer with no live agreement or with more than one, the catch-up line carries exactly the base cash-discount rule's figure: …"
- Effect: `result` uses `in_scope` to switch between the figure built from the factors and `base_figure`. So `payment_allocation_to_merchandise`, `payment_record_share_of_rate` and `discountable_merchandise_deduction` all apply only through the contract factor's binding. The computation document covers `in_scope`, so it would have to define "dated inside the current term", which the contract factor document also covers.

**Finding 2: `base_share` reads four bindings of `payment_allocation_to_merchandise`.**
- Compute binding: `base_share: "1 if left_open <= full_rate_disc else (pay_amt / inv_total if P('cash_discount_partial_payment') else 0)"` is plain and feeds `base_figure`, which is also plain.
- `left_open`, `full_rate_disc`, `pay_amt` and `inv_total` (and through `left_open`, `applied_out` and `returned_in`) are listed in that factor's bindings.
- Rule sentence `base_share` rests on: "… the tier's prompt-payment discount percentage of the invoice's merchandise subtotal when the payment leaves open no more than that discount, that figure in the proportion of the payment to the invoice total for a payment leaving more open on a tier allowing partial-payment discounts …"
- What "left open" means is stated only inside the factor's ladder sentence, joined to it by a colon: "What is left open on the invoice is the invoice total less every payment, credit memo, discount line and write-off applied to it, plus every returned payment reversed on it, compared without rounding: when more is left open than … the payment is taken to settle the invoice's freight and sales tax first …"
- Effect: the computation document can't state the out-of-scope figure precisely unless it restates a definition that the factor document covers.

**Suggested source fix** (renderer's suggestion):
- Move `inv_date`, `pa_eff`, `pa_end` and `pa_in_force` into the plain set. `contract_share_of_rate` keeps `pa_tier` and `contract_share`.
- Move `pay_amt`, `inv_total`, `applied_out`, `returned_in`, `left_open` and `full_rate_disc` into the plain set. `payment_allocation_to_merchandise` keeps `inv_freight_tax` (only that factor uses it) and `paid_merch`.
- Split the rule so the "left open" definition and the payment amount each stand as their own plain sentence. Point the `compute_basis` quotes for those bindings at the new sentences.

The other three extended policies scanned clean (compute_basis quotes verbatim, prerequisite sentences verbatim, overwrites found, no factor reads another factor, no other plain binding reads a factor's bindings, month conventions match, cross-product names match, docstrings match bodies).
