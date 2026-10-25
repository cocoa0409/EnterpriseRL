# Renderer findings — product builder (d=credit_builder_accounts), render round 2 (saved verbatim by the coordinator)

Renderer agent ac44317da4685f756 re-scanned (gate VERDICT revision_10 CLEAN), confirmed S1–S7 closed, and STOPPED with 0 documents written on one new defect:

**New defect N1: same-day tie not stated for "latest payment" lookups in `builder_ext_autopay_reenrollment`, factor `ad_return_buf`.**
- Rule sentence: "When the account's most recent AutoPay debit (the latest payment made through the AutoPay channel) was returned in the 12 whole calendar months before today (…) and the borrower's own payment made it good within the late-fee grace period after that debit's due date (the payment looked at is the latest payment posted toward that due date: it makes the debit good only when no return points at it, it is dated after the return and it is dated no more than the plan's late-fee grace days after the due date, counted as that payment's date less the due date; when a return points at that latest payment, the debit has not been made good), the buffer is those days plus one, …"
- Compute: `ad_good_id` is `LATEST('builder_transactions', 'builder_txn_id', date_field='txn_date', event_type='builder_payment_posted', installment_due_date=ad_ap_due)`, then `ad_good_ret` counts returns pointing at it. On equal dates, `LATEST` keeps the first booked row. The rule never says which of two same-day payments is "the latest". The other "most recent" lookups in this charter all state the tie ("when two … on the same day, the one booked first counts as the most recent"). This sentence's own policy states it only for the most recent returned payment.
- Example: an AutoPay debit for due date D is returned. On D plus 5 days the borrower posts two payments toward D: a debit-card payment booked first and later charged back, then an ACH payment that stands.
  - Compute: it picks the charged-back payment, so the debit is not made good and the buffer is a flat 3 days.
  - Rule read as "the later booking is the latest": the debit is made good with 5 days' lag, so the buffer is 6 days and the due day differs.
- The same gap, less likely in practice, applies to "the latest payment made through the AutoPay channel" in two places:
  - `ad_ap_id` in this policy.
  - `gw_ap_id` in `builder_ext_goodwill_late_fee_credit`, whose prerequisite sentence is "A goodwill credit for a borrower whose most recent AutoPay debit (the latest payment made through the AutoPay channel) was returned, …".
- Suggested fix: add the tie clause used elsewhere, "when two were posted on the same day, the one booked first counts as the latest", to both "latest payment" definitions. Changing the goodwill prerequisite sentence also means updating its `policy_source` verbatim.
