# render_r1 — billing (Installment Payment Plans) — STOPPED at source scan

Gate: `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN` (confirmed). Source scanned before any doc was written:
tasks/installment_billing_and_fees/billing.extended.yaml + task_tools.py. No doc and no staging were written.

## F1 (blocking) — billing_ext_draft_notice: rounding sentence vs RND placement of the three advances (XF 6, XF 3)

Rule sentence (verbatim):
> Only the shares, the advances and the minimum due are rounded, each half up to the cent.

The three advance schedules are separate sentences, each adding its own percentage ("the notice adds to its premium fr44_endorsement_advance_pct percent of the endorsement premium not yet billed", "... points_high_endorsement_advance_pct percent ...", "... package_min_endorsement_advance_pct percent ..."), so the rule rounds **each advance separately**. The compute sums the percentages and rounds **once**:

> `notice_endorsement: MN(MX(0, endorsement_balance), endorsement_share + RND(MX(0, endorsement_balance) * (adv_filer_pct + adv_points_pct + adv_package_pct) / 100, 2))`

Witness (exact half-up decimal): endorsement premium not yet billed 100.10, SR-22 (2.5), 4-7 points (1.5), Minimum Limits (2.5):
rule = 2.50 + 1.50 + 2.50 = 6.50; compute = round(100.10 x 6.5%) = 6.51. (140.20: rule 9.12, compute 9.11.)
The other four policies state their single final rounding explicitly ("rounded half up to the cent once, at the end"); this one does not, and the three factor documents would each have to say "rounded half up to the cent" for their own advance.

Same sentence, second defect: "Only ... are rounded" literally excludes the down payment premium and the scheduled installment premium, which the rule's earlier sentences and the compute (`down_premium: RND(...)`, `scheduled_premium: RND(...)`) round. Compare billing_ext_direct_bill_switch, which says "Apart from the old schedule's figures, only the shares, the advance and the minimum due are rounded".

Fix direction (source side): either state in the assembly sentence that the percentages of the advance schedules are added together and applied once to the endorsement premium not yet billed, rounded once, or move RND into each advance; and add the "Apart from the schedule's own figures" qualifier.

## F2 — billing_ext_returned_draft_makeup: absent-invoice case of the undraftable-account advance is unstated (XF 8, XF 9)

Rule sentence (verbatim):
> when the returned payment is coded account_closed or stop_payment_by_payer and an installment remains after the one its invoice billed but has not been invoiced, the makeup adds that next installment's scheduled premium (...); when it is so coded and the next installment has already been invoiced, the makeup adds that invoice's minimum due less the payments posted against it; when the return is coded otherwise, or no installment remains, the makeup adds no advance.

Compute:
> `advance_core: adv_next_sched if ((adv_reason == 'account_closed' or adv_reason == 'stop_payment_by_payer') and adv_inst != None and adv_inst < P('installment_count') and adv_next_invoice == None) else (... if (... and adv_inst != None and ...) else 0)`

When the returned payment is linked to no invoice (`adv_inst == None` — a case the same rule contemplates in the re-collection schedule: "when it had paid no installment invoice, the makeup re-collects nothing for it"; e.g. a returned one-time payment recorded toward no invoice) and is coded account_closed / stop_payment_by_payer while installments remain unbilled, the compute adds 0, but no rule tier covers it: "the one its invoice billed" is undefined, and the "otherwise" tier names only "coded otherwise, or no installment remains". A reader can as naturally take the next unbilled installment and add its scheduled premium.

## F3 — billing_ext_endorsement_deposit: "what its most recent installment invoice still owes" ignores returned payments (XF 8 decoy: reversed rows)

Rule sentence (verbatim, also in baseline.rule):
> and less any credit the plan holds beyond what its issued invoices carry (the amount by which its account_balance falls short of the premium not yet billed on any invoice plus what its most recent installment invoice still owes), never below zero.

Compute:
> `dep_latest_unpaid: MX(0, RND((LATEST('billing_invoices','minimum_due', ...) or 0) - SUM('billing_transactions','amount', event_type='billing_payment_received', related_invoice_id=LATEST(...billing_invoice_id...)), 2))`
> `dep_credit: MX(0, RND(dep_unbilled_scheduled + dep_ap_total - dep_endorsement_billed + dep_latest_unpaid - F('account_balance'), 2))`

Under the base rule "the charges it had paid become unpaid again" a returned payment makes the invoice owe again, but the compute counts the returned payment as still paying it. Witness: plan holds credit C (e.g. an earlier deposit) and the draft that paid the latest invoice (minimum due M) was returned and not made good: rule credit = C; compute credit = max(0, C - M). Endorsement balance (and every deposit figure) differs whenever C > 0.

## F4 — billing_ext_returned_draft_makeup: payment-plan advance tiers overlap on the Paid-in-Full Plan (XF 9)

Rule sentence (verbatim):
> when the plan is an installment plan billed directly (no recurring payment authorization in force and installment_count above zero), direct_bill_advance_pct percent of the returned amount is added to the makeup; when it bills by automatic draft (signed authorizations outnumbering revocations), autopay_advance_pct percent; on the Cardinal Point Paid-in-Full Plan nothing.

Compute:
> `plan_pct: K('direct_bill_advance_pct') if (not plan_auth and P('installment_count') > 0) else (K('autopay_advance_pct') if plan_auth else 0)`

A Paid-in-Full plan whose authorization rows still outnumber revocations (e.g. switched from a monthly draft plan without a revocation row) satisfies both the second and third tiers in words; compute gives autopay_advance_pct. The tiers need one ordering or an exclusive condition (installment_count above zero on the autopay tier, or "otherwise" wording).

## Note (non-blocking) — billing_ext_draft_notice: declared month convention nothing uses

> A whole calendar month is complete only when the later date's day number is at least the earlier date's day number (so a month that starts on a day the later month lacks is not complete until the next month).

No MONTHS()/within_months read exists in this policy's compute; the sentence would render as a definition with no rule using it.

## Scanned clean
billing_ext_switch_down_payment (90-day boundary, 12-month window, tiers, single rounding, cap), billing_ext_direct_bill_switch (prerequisite sentences state-form, credit/endorsement tiers, state fee, filing-fee window, single advance), endorsement-deposit tiers/age months/window days/same-date tie (XLATEST keeps first recorded, matching "the one recorded first"), makeup same-day tie and re-collection tiers, overwrite tails (scoped replaced_by restating in-force content; sibling overwrites of the payment-authorization clause each name the others), params all used.
