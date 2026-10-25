# render_r2 — billing (Installment Payment Plans) — STOPPED at source re-scan

Gate: `VERDICT revision_17: task0=PASS task1=PASS charter=CLEAN` (confirmed). Re-scanned billing.extended.yaml (rev 17) + task_tools.py. No doc and no staging were written.

## Round-1 items
- F1 (draft-notice advance rounding): CLOSED — "the percentages of the advance schedules are added together and applied once ... rounded half up to the cent once" now matches `RND(MX(0, endorsement_balance) * (adv_filer_pct + adv_points_pct + adv_package_pct) / 100, 2)`; "Apart from the schedule's own figures" qualifier added.
- F2 (makeup advance, no-invoice case): CLOSED — "when the returned payment had paid no installment invoice ... the makeup adds no advance" matches the `adv_inst != None` guard.
- F3 (deposit, latest invoice still owes): CLOSED — "plus every amount the bank returned against that payment" plus the at-most-one-payment scope matches `dep_latest_unpaid` and `dep_scope_ok`.
- F4 (makeup plan advance overlap): CLOSED — "installment_count above zero" on the autopay tier and "whatever its authorizations" on Paid-in-Full match `plan_pct`.
- Note (unused month convention in draft notice): CLOSED (sentence removed).

## R1 (blocking) — billing_ext_draft_notice and billing_ext_direct_bill_switch: the out-of-scope invoice adds a certificate filing fee that the same rules' own overwrite tails say it does not carry (XF 5a/5d, XF 11)

billing_ext_draft_notice rule, scope sentence (verbatim):
> a plan billing a Named Non-Owner Policy term, and any other plan it does not name, is outside it and its invoices follow the base installment schedule unchanged, each billing its scheduled installment premium, the plan's installment_fee together with the certificate filing fee this schedule bills (read, as for a draft notice, from the certificate recorded first on the term the plan bills, owner or non-owner), and the standing balance

Same rule, overwrite tail of billing_installment_fee_rule (verbatim, also its replaced_by):
> any other installment invoice, a later invoice of a moved plan included, carries the plan's installment_fee unadjusted, charged on the invoice date.

Same rule, overwrite tail of billing_installment_schedule (verbatim):
> any other invoice, a later invoice of a moved plan included, is issued invoice_lead_days calendar days before its due date and bills the installment premium, the plan's installment fee and every past-due amount still unpaid, its minimum_due being their sum.

Compute (fallback branch):
> `result: 0 if unbilled_count <= 0 else ((...) if notice_scope_ok else RND(MX(0, fb_premium + P('installment_fee') + filing_fee_billed + fb_standing), 2))`

billing_ext_direct_bill_switch has the same contradiction: its out-of-scope sentence says the next invoice bills "as the base installment schedule states ... the Six-Pay Direct Bill Plan's installment_fee (direct_bill_installment_fee) together with the certificate filing fee the standard first invoice bills", while its own fee overwrite tail says "any other installment invoice, a later invoice of a moved plan included, carries the plan's installment_fee unadjusted"; compute: `RND(MX(0, sw_base_sched + K('direct_bill_installment_fee') + sw_cert_fee + sw_standing), 2)`.

Witness: a Named Non-Owner plan (or a later invoice of a moved owner plan) whose certificate has an unbilled, unreversed filing fee F assessed after the latest invoice. Scope sentence and compute: minimum due includes F. Overwrite tails (the clauses that remain in force for that plan) and the base installment schedule: the fee is the installment fee unadjusted, no F. "follow the base installment schedule unchanged" also contradicts adding a fee the base schedule never bills. The renderer cannot carry both the replaced_by and the scope sentence; one side must change (either drop the filing fee from the fallback compute, or scope the overwrite tails and base-fallback wording so they name the filing fee for these plans).

## R2 (blocking) — billing_ext_switch_down_payment and billing_ext_direct_bill_switch: scope test "two or more payments posted against it" counts the makeup in words but not in compute (XF 11, XF 19)

billing_ext_switch_down_payment rule (verbatim; direct_bill_switch carries the same words twice):
> and, as the records stood when the move was asked, neither the installment invoice that the payment most recently returned on the plan had paid nor its next installment invoice, if already issued, has two or more payments posted against it, and the owner term backs at most one certificate

Compute:
> `dn_pay_ok: (dn_ret_invoice == None or COUNT('billing_transactions', event_type='billing_payment_received', related_invoice_id=dn_ret_invoice) - COUNT('billing_transactions', event_type='billing_payment_received', related_invoice_id=dn_ret_invoice, related_payment_txn_id=dn_ret_payment) <= 1) and (...)`
> `sw_pay_ok:` identical shape.

The compute excludes every makeup referencing the returned payment from the count on the returned invoice. The words do not: the carve-out "a payment recorded against an invoice counts as another payment unless it is the returned payment itself or a makeup referencing it" exists only in billing_ext_returned_draft_makeup's rule, not in these two. Witness: returned draft P on invoice I, makeup M (referencing P) posted against I — exactly the state direct_bill_switch's own prerequisite sentence requires ("A plan is moved off automatic draft only after the installment invoice that the payment most recently returned on it had paid is paid again in full."). I then has two payments posted against it: words put the plan outside both schedules (switch down payment 0.00; first invoice priced on the base fallback); compute (2 - 1 = 1 <= 1) keeps it in scope.

"as the records stood when the move was asked" does not close it: no record holds the moment the move was asked (the move and its switch down payment are written later in the same handling), so a reader cannot tell from the records whether the makeup came before or after that moment, and the compute reads the records as they stand when it is evaluated. Fix direction: put the same carve-out (returned payment itself and makeups referencing it do not count) in both rules and drop the unrecorded time reference, or key the test on a record.

## R3 — billing_ext_draft_notice and billing_ext_direct_bill_switch: multi-certificate fallback for a switched plan with no installment 1 invoice is unstated (XF 8 absent record)

Rule (verbatim, draft notice; direct_bill_switch has the same clause):
> the schedule's down payment premium being the one the base down payment rule sets (...) for a plan enrolled on its present plan, and, for a plan switched onto it from another, the scheduled installment premium being the premium recorded on its installment 1 invoice.

Compute:
> `... if (F('plan_switches_used') or 0) == 0 else ((RND(F('term_premium_billed') - LATEST('billing_invoices','premium_amount', ..., installment_number=1) * P('installment_count'), 2)) if LATEST(... installment_number=1) != None else RND(F('term_premium_billed') * (P('down_payment_pct_new_business') if ... else P('down_payment_pct_renewal')) / 100, 2))`

For a switched plan whose installment 1 has not been invoiced yet, the rule gives no figure (there is no installment 1 premium to read); the compute silently uses the present plan's base percentage. Needs one sentence stating that case.

## Note (non-blocking) — punctuation
"the filing fee recorded on the filing ledger for the certificate recorded first on the owner term billed, whatever its present status,, when that fee was assessed" (double comma) in draft_notice rule/baseline.rule and direct_bill_switch rule.

## Scanned clean (rev 17)
billing_ext_endorsement_deposit (scope gate, down payment premium from down_payment_amount less fees, latest-invoice owed with returns, tiers, single rounding, prerequisite sentence), billing_ext_returned_draft_makeup (scope carve-out, made-good test, waiver-net fees, re-collection and advance tiers, plan tiers), switch-down tiers/90-day/12-month/state/package/points, direct-bill credit/endorsement/state-fee/advance tiers and both prerequisite sentences.
