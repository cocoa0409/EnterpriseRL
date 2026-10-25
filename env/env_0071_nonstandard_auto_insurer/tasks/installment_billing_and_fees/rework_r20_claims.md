# Rework round 20 claims (bounded: CG-42)

- CG-42: the draft notice (in-scope notice and every base branch) and the direct-bill switch (first invoice and out-of-scope invoice) now honor the base clause "No installment fee is charged ... on an installment avoided by paying the whole balance before it was invoiced", in words and compute alike.
  - Record test: the plan's account_balance at the invoice is zero or less. The installment (or state) fee is then 0.00, and any certificate filing fee is still billed.
  - Probe (task 0's plan with its whole balance paid before installment 3 is invoiced):
    - the notice's fee drops to the certificate fee alone, 25.00, with the installment fee 0.00;
    - on a Four-Pay plan the base branch fee is likewise 0.00.
    - Scored worlds have a positive balance; values unchanged.
- Sweep fix: compute_basis quotes that had picked up a following sentence were reduced to their single verbatim sentence (all quotes verbatim again).

## Clause-by-clause sweep (every clause of every base sentence the five rules touch)
### billing_agg_returned_payments
- "Returned payments are counted across every billing plan of the customer" -- in force; no rule departs from it
- "not plan by plan" -- in force; no rule departs from it
- "over the rolling lookback measured by billing_msr_nsf_returns_lookback." -- in force; no rule departs from it
- "A plan is restricted to certified funds only when billing_msr_nsf_returns_lookback has reached nsf_returns_for_certified_funds." -- in force; no rule departs from it
- "When the threshold is reached" -- in force; no rule departs from it
- "every open plan of the customer is flagged certified_funds_only on the same day" -- in force; no rule departs from it
- "any recurring authorization on those plans is revoked" -- in force; no rule departs from it
- "and a Monthly EFT or Monthly Card Autopay plan becomes the Six-Pay Direct Bill Plan." -- in force; no rule departs from it
- "While a plan is restricted to certified funds" -- in force; no rule departs from it
- "a payment is accepted on it only by a method in certified_funds_methods." -- in force; no rule departs from it
- "Personal checks and bank ACH payments are refused while the restriction applies." -- in force; no rule departs from it
- "The restriction stays on the flagged plans for the rest of their terms" -- in force; no rule departs from it
- "a plan set up later for a renewal is enrolled without it only when the count is then below the threshold." -- in force; no rule departs from it

### billing_delinquency
- "A plan moves to past_due only when an installment invoice's minimum due is unpaid at the end of its due date." -- in force; no rule departs from it
- "A past_due plan returns to current only when payments cover every past-due amount" -- in force; no rule departs from it
- "including late and NSF fees" -- in force; no rule departs from it
- "a partial payment leaves it past_due." -- in force; no rule departs from it
- "A plan moves to paid_in_full when account_balance is 0.00 or less and no installment remains to be billed." -- in force; no rule departs from it
- "The policy's notice of cancellation for nonpayment follows its own rule." -- in force; no rule departs from it

### billing_down_payment
- "The down payment is the premium portion" -- in force; no rule departs from it
- "term_premium_billed multiplied by the plan's down_pct for a new-business term or renewal_down_pct for a renewal term and divided by 100" -- in force; no rule departs from it
- "rounded to the cent" -- in force; no rule departs from it
- "plus every fully earned fee charged with the term (policy fee and any SR-22 or FR-44 filing fee) in full." -- in force; no rule departs from it
- "An installment plan is available only when billing_msr_nsf_returns_lookback does not exceed the plan's entry gate max_nsf_returns_12_months." -- in force; no rule departs from it
- "A customer who exceeds it is offered only the Cardinal Point Paid-in-Full Plan." -- in force; no rule departs from it
- "A Monthly EFT or Monthly Card Autopay plan is set up only after the customer has signed a recurring payment authorization for it." -- in force; no rule departs from it
- "A new-business down payment is accepted only by a method in down_payment_methods." -- in force; no rule departs from it
- "When the down payment clears" -- in force; no rule departs from it
- "the plan becomes current" -- in force; no rule departs from it
- "or paid_in_full when the down payment was the whole premium." -- in force; no rule departs from it
- "When the down payment is returned dishonored" -- in force; no rule departs from it
- "the plan closes on that day" -- in force; no rule departs from it
- "the NSF fee is charged" -- in force; no rule departs from it
- "and the term is voided from inception under the policy's own rule." -- in force; no rule departs from it

### billing_fee_waivers
- "A waiver reverses one fee transaction for that fee's full amount and references it" -- in force; no rule departs from it
- "partial waivers are not given." -- in force; no rule departs from it
- "Each fee is waived at most once." -- in force; no rule departs from it
- "courtesy_late_fee applies only to a late fee." -- in force; no rule departs from it
- "A courtesy waiver is granted only while billing_msr_courtesy_waivers_in_term is below courtesy_waivers and billing_msr_nsf_returns_lookback is zero." -- in force; no rule departs from it
- "postmark_on_time reverses a late fee charged on a mailed payment whose postmark was within the grace period" -- in force; no rule departs from it
- "company_error reverses a fee charged contrary to these rules (for example a late fee on a payment posted within the grace period)" -- in force; no rule departs from it
- "duplicate_charge reverses a second charge of the same fee." -- in force; no rule departs from it
- "Installment fees" -- in force; no rule departs from it
- "NSF fees and agent-assisted payment fees are never waived as a courtesy." -- in force; no rule departs from it

### billing_installment_fee_rule
- "Each installment invoice carries the plan's installment_fee" -- retired by a scoped overwrite in billing_ext_direct_bill_switch, base restated for every other case
- "charged on the invoice date." -- retired by a scoped overwrite in billing_ext_direct_bill_switch, base restated for every other case
- "Only one installment fee is charged per installment invoice." -- in force; no rule departs from it
- "No installment fee is charged on the down payment" -- in force; no rule departs from it
- "on a final bill" -- in force; no rule departs from it
- "on a renewal bill" -- in force; no rule departs from it
- "on any plan without installments" -- in force; no rule departs from it
- "or on an installment avoided by paying the whole balance before it was invoiced." -- in force; no rule departs from it
- "After a mid-term plan switch" -- retired by a scoped overwrite in billing_ext_direct_bill_switch, base restated for every other case
- "invoices issued from the switch date carry the new plan's fee" -- retired by a scoped overwrite in billing_ext_direct_bill_switch, base restated for every other case
- "invoices already issued keep theirs." -- retired by a scoped overwrite in billing_ext_direct_bill_switch, base restated for every other case

### billing_installment_schedule
- "The premium remaining after the down payment premium is spread over installment_count equal installments rounded to the cent" -- in force; no rule departs from it
- "the final installment absorbing any rounding difference." -- in force; no rule departs from it
- "Installment 1 falls due first_installment_months_after_effective calendar months after the term effective date and each later installment installment_interval_months after the previous one" -- in force; no rule departs from it
- "always on installment_due_day" -- in force; no rule departs from it
- "in a month without that day the due date is the last calendar day of the month." -- in force; no rule departs from it
- "Each invoice is issued invoice_lead_days calendar days before its due date and bills the installment premium" -- retired by a scoped overwrite in billing_ext_direct_bill_switch, base restated for every other case
- "the plan's installment fee and every past-due amount still unpaid" -- retired by a scoped overwrite in billing_ext_direct_bill_switch, base restated for every other case
- "its minimum_due is their sum." -- retired by a scoped overwrite in billing_ext_direct_bill_switch, base restated for every other case
- "Only one installment invoice is issued per installment number of a plan." -- in force; no rule departs from it
- "Credits on the plan reduce the next installments nearest first" -- retired by a scoped overwrite in billing_ext_draft_notice, base restated for every other case
- "an installment fully covered by credit before its invoice date is not invoiced." -- retired by a scoped overwrite in billing_ext_draft_notice, base restated for every other case
- "No installments exist on the Cardinal Point Paid-in-Full Plan." -- in force; no rule departs from it

### billing_late_fee_rule
- "A late fee is assessed only later than late_fee_grace_days calendar days after the due date of the installment" -- in force; no rule departs from it
- "and only when that installment's minimum due is still not paid in full." -- in force; no rule departs from it
- "Calendar days are counted from the due date as day 0" -- in force; no rule departs from it
- "a payment posted on or before the due date plus the grace days is on time" -- in force; no rule departs from it
- "and the fee may be assessed from the following day." -- in force; no rule departs from it
- "No more than late_fee_max_per_installment late fee is charged for one installment invoice." -- in force; no rule departs from it
- "Payment timeliness is judged by posted_date" -- in force; no rule departs from it
- "except that a mailed payment whose postmark_date is on or before the due date plus the grace days counts as on time." -- in force; no rule departs from it
- "No late fee is charged on the Cardinal Point Paid-in-Full Plan" -- in force; no rule departs from it
- "on a final bill" -- in force; no rule departs from it
- "or on an automatic draft that cleared on its draft date." -- in force; no rule departs from it

### billing_payment_posting
- "The customer personally authorizes each one-time payment taken by a representative" -- retired by a scoped overwrite in billing_ext_switch_down_payment, base restated for every other case
- "stating the card or bank account to be charged and the amount." -- retired by a scoped overwrite in billing_ext_switch_down_payment, base restated for every other case
- "A single card or bank payment may not exceed max_single_payment." -- in force; no rule departs from it
- "Payments are applied in payment_application_order: past-due invoices oldest first (fees before premium)" -- retired by a scoped overwrite in billing_ext_draft_notice, base restated for every other case
- "then unpaid late and NSF fees" -- retired by a scoped overwrite in billing_ext_draft_notice, base restated for every other case
- "then the current invoice" -- retired by a scoped overwrite in billing_ext_draft_notice, base restated for every other case
- "then future installments nearest first" -- retired by a scoped overwrite in billing_ext_draft_notice, base restated for every other case
- "any excess is a credit." -- retired by a scoped overwrite in billing_ext_draft_notice, base restated for every other case
- "A payment posts on the day it is received" -- in force; no rule departs from it
- "a mailed payment also records its postmark date." -- in force; no rule departs from it
- "A partial payment is accepted and applied in the same order." -- in force; no rule departs from it
- "A personal check is refused on plans whose personal_check_accepted is false." -- in force; no rule departs from it
- "The agent-assisted payment fee is charged only on a one-time payment taken through the agent_phone channel." -- in force; no rule departs from it
- "The fee is the plan's agent_fee and is not charged on payments made online" -- in force; no rule departs from it
- "through the automated phone line" -- in force; no rule departs from it
- "by mail" -- in force; no rule departs from it
- "at an agent office or by automatic draft." -- in force; no rule departs from it

### billing_plan_switch
- "A plan is switched only to a plan listed in its plan_switch_targets." -- in force; no rule departs from it
- "plan_switches_used must be below max_switches." -- in force; no rule departs from it
- "A switch to a Monthly EFT or Monthly Card Autopay plan requires a recurring payment authorization signed by the customer at least authorization_lead_days calendar days before the next draft date." -- in force; no rule departs from it
- "The customer personally signs a recurring payment authorization" -- in force; no rule departs from it
- "stating the last four digits of the account or card." -- in force; no rule departs from it
- "A plan restricted to certified funds can never be switched to a Monthly EFT or Monthly Card Autopay plan." -- in force; no rule departs from it
- "A switch to the Cardinal Point Paid-in-Full Plan is made only when the whole account_balance is paid" -- in force; no rule departs from it
- "and future installment fees are then avoided." -- in force; no rule departs from it
- "Unbilled installments keep their amounts and due dates" -- retired by a scoped overwrite in billing_ext_direct_bill_switch, base restated for every other case
- "invoices issued after the switch carry the new plan's installment fee." -- retired by a scoped overwrite in billing_ext_direct_bill_switch, base restated for every other case

### billing_premium_posting
- "Every premium written and additional premium transaction of the billed term is posted as a charge" -- in force; no rule departs from it
- "and every return premium transaction as a credit" -- in force; no rule departs from it
- "for the same amount on the day the policy transaction is processed" -- in force; no rule departs from it
- "referencing it." -- in force; no rule departs from it
- "Each policy premium transaction is posted to the plan only once." -- in force; no rule departs from it
- "Fully earned fees are charged with the policy transaction that produced them." -- in force; no rule departs from it
- "Premium is never posted to a plan whose term it does not belong to." -- in force; no rule departs from it

### billing_returned_payments
- "A returned payment reverses the original payment for its full amount on the date the bank return posts" -- in force; no rule departs from it
- "and the charges it had paid become unpaid again." -- in force; no rule departs from it
- "An NSF fee is charged only for a returned payment whose return_reason is in nsf_fee_return_reasons." -- in force; no rule departs from it
- "Only one NSF fee is charged per returned payment." -- in force; no rule departs from it
- "The NSF fee is the plan's nsf_fee" -- in force; no rule departs from it
- "returns coded bank_error or unauthorized_debit carry no fee." -- in force; no rule departs from it
- "When billing_msr_returned_drafts_in_term reaches returned_drafts on a Monthly EFT or Monthly Card Autopay plan" -- in force; no rule departs from it
- "the recurring authorization is revoked and the plan becomes the Cardinal Point Six-Pay Direct Bill Plan." -- in force; no rule departs from it
- "A customer may also revoke a recurring authorization at any time" -- retired by a scoped overwrite in billing_ext_direct_bill_switch, base restated for every other case
- "the plan then becomes the Six-Pay Direct Bill Plan for its remaining installments." -- retired by a scoped overwrite in billing_ext_direct_bill_switch, base restated for every other case
- "A returned down payment closes the plan and voids the term." -- in force; no rule departs from it

Notes on in-force clauses the rules touch:
- The certificate-fee additions are billed under the filing charter, never as an installment fee.
- The agent-assisted fee is a separate charge (0.00 on the Monthly plans the deposit and switch down payment cover).
- Switch targets and the switch limit stay in force alongside the switch.
- Returned-draft and certified-funds moves are restated as base.
- The installment schedule's equal spreading governs the enrolled schedule; the respread after a requested move is under the retired billing_plan_switch clause.

Nothing else changed. Carried, not regressed: every item closed in rounds 1-19.
