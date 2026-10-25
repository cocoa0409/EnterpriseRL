# Rework round 14 claims (bounded: CG-37 and the same-class billed-certificate read)

Closed:
- CG-37: the set-up-day filing-fee read is now tied to this plan's own term by an exact value. It reads the fee rows of the filing whose backing term id equals the term the plan bills, with no status filter: `CFIELD('fr','fr_filing_id', auto_policy_id=F('auto_policy_id'))`, or nonowner_policy_id for a non-owner plan, combined with `posted_date=F('enrolled_date')`.
- Same-class read (the draft notice's and the switch's billed certificate fee): the fee date, fee amount and waiver reads now look up the filing by the same backing-term tie, whatever the certificate's present status.
- Because the charter allows several filings on one backing term (fr_agg_backing_term), each certificate read is exact only for a term backing one certificate. That limit is now a stated and enforced record test, `XCOUNT('fr','fr_filings', auto_policy_id=F('auto_policy_id')) <= 1`, in every schedule's scope. Outside it:
  - the deposit, makeup and switch down payment figure 0.00;
  - the draft notice and the switch give their base figures;
  - the schedule's down payment premium falls back to the base down payment rule, as the words state.

Every place that reads certificates or filing fees:
1. draft notice: down payment premium, owner branch (set-up-day fees of the term's certificate);
2. draft notice: down payment premium, non-owner branch (same, keyed by nonowner_policy_id);
3. draft notice: billed certificate fee (filing_fee_date, filing_reversed, filing_fee_amount);
4. endorsement deposit: down payment premium;
5. returned-payment makeup: advance schedule down payment premium;
6. switch down payment: own down payment premium;
7. direct-bill switch: old schedule down payment premium;
8. direct-bill switch: first-invoice certificate fee (sw_cert_date, sw_cert_reversed, sw_cert_fee).
The certificate stamp reads (financial_responsibility_filing on the term) are term fields, not certificate reads, and are unchanged.

Probes (scratch copies of task 0's world):
- (a) A second owner policy of the customer with its own SR-22 fee assessed on the plan's set-up day: the down payment premium is unchanged in every read, so the other policy's fee is not subtracted.
- (b) Task 0's SR-22 moved to cancellation_filed with its fee unbilled: the notice still bills the recorded certificate fee, and the down payment premium is unchanged.
- (extra) Task 0's term backing a second certificate: outside every schedule, so the notice gives its base figure and the deposit figures 0.00.

Nothing else changed; scored values unchanged. Carried, not regressed: every item closed in rounds 1-13.
