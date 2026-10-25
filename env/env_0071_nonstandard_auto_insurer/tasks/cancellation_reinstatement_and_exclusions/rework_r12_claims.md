# Rework round 12: claims per revision_1 audits (policy_kb + runtime_context)

No scored value moved. The changes are limited to the certificate reads (nonpayment return, reinstatement fee, insured-request return), the rating-date sentences (relisting, reported-resident exclusion, lift), and the proof text that quotes them.

## S-1 (task 0, cross-product auto x fr): figures depended on an fr SR-26 write made mid-conversation

**Closed.** The class sweep covered all six policies. Only these three read certificates; the other three and the six task tools read none.

- **Nonpayment return** (days returned, SR-26 transmission days) and **insured-request return** (the same two factors): every certificate is now read as it stood on the cancellation effective date.
  - A certificate stood filed on that date when either holds:
    - the first-entered certificate with status filed has its filed_date on or before that date;
    - the first-entered certificate with status cancellation_filed has its filed_date on or before that date and its sr26_date after it.
  - An SR-26 counts, and its certificate_end_date is read, only when its sr26_date is on or before that date.
  - The run-off and transmission figures are taken from the filed or the cancellation_filed certificate.
  - This is stated in the rule words and enforced in compute: the filed, run-off, SR-26 end, lag and lag-max reads.
- **Reinstatement fee**: every certificate is now read as it stood on the reinstatement effective date. This applies to the exposure charge and to the form, type and out-of-state charges, each of which has its own date binding for factor independence.
  - A certificate filed after that date does not change the reading, and neither does an SR-26 transmitted after it.
- Also updated: ladder whens, compute_basis quotes, the fr cross-category reads (filed_date, sr26_date) and notes, and the task 0 proof text (tier_taken, factor_trace, computation steps, probe list).
- **Probes** (scratch copy; check_compute against the gold):
  - SR-26 dated the processing day on the term's certificate, with and without a refiling filed that day: figures hold. The previous charter moved them (insured-request days and figures, reinstatement-fee components).
  - SR-26 dated before the cancellation effective date: the tiers still move, so the reads stay live.

## N-1 (task 1, advisory): "rating date" defined in general sentences, used only by the age factors

**Closed.** Each date is now defined only inside the age-class sentence that uses it:

- **Relisting:** "the change effective date of the resident's most recent driver-added entry, the date of that rating", and "the report date, the date the resident is rated again".
- **Exclusion:** "the report date of the claim report handled".
- **Lift:** "the processing date".

Also updated: one ladder when, one compute_basis quote, one cross-category note, and the task 1 proof text.

## P-1 (base law): no change

Base auto_cancellation_nonpayment / auto_notice_rescission wording. The base blueprint is frozen.

## P-2 (policy-side): no change

This is source wording rendered as required, not a rule-vs-compute error. The computation document stays silent.

## N-2, N-3, N-4 (advisory, not RED): no change

## X-1 (cross-product-pending, billing): no change

## Checks

- Verbatim sweep clean: compute_basis, replaced_by, baseline and policy_source sentences.
- Gate block 7/7 green; check_traceability OK.
