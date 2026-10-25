# Rework round 17 claims (strictly bounded: CG-41)

- CG-41: the DSL residue is now stated in the rule words, matching the compute.
  - One identical sentence was added to the draft notice (after its standard notice sentence, governing the in-scope notice and every base branch, owner and non-owner) and to the direct-bill switch (after its standard first-invoice sentence, governing the first invoice and the out-of-scope invoice): "Where an invoice bills a certificate filing fee, it bills the unbilled filing fee of the certificate recorded first among the filings whose backing term is the term the plan bills (the earliest of those entries in the filing records, whatever its present status); when that term backs more than one certificate, the unbilled filing fee of any further certificate is not billed on that invoice and is referred to the filings desk."
  - The fee phrases that named "the certificate whose backing term is ..." now name "the certificate recorded first on ..." in the notice's standard and base sentences and in the switch's standard sentence.
  - "Recorded first" is exactly the compute's pick: `CFIELD('fr','fr_filing_id', auto_policy_id=...)`, or nonowner_policy_id for a non-owner plan, returns the first matching entry in the filing records' order. The entries are distinct rows, so there is no tie.

Probe (auditor's world: a second certificate on the term with its own unbilled 25.00, scratch copies):
- Draft notice base invoice on task 0's term: computed 158.01. The rule gives 247.01 + 6.00 + 25.00 (first certificate only) - 120.00 = 158.01, with the second fee referred. Agree.
- Switch base invoice on task 1's term: computed 483.36. The rule gives 205.18 + 9.00 + 25.00 (first certificate only) + 244.18 = 483.36, with the second fee referred. Agree.

Nothing else changed; scored values unchanged.
