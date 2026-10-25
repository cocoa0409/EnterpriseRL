# Remaining source mismatches reported by the loan renderer (agent a98c70f1f4d9199a4), render round 2 — copied verbatim by the coordinator

Rendered source: loan.extended.yaml b7e75bb8…c20e, task_tools.py ec0bb1f1…dc4e. docs/loan/ republished (69 docs, DOCS OK).

**Remaining source mismatches (rendered as they stand):**
1. **First-match selection on files with several records (audit O-9).** In `loan_ext_closing_disclosure_lender_credit`, the rule says "where the closing on the file is a Larkspur Remote Online Notarization Closing…", "where the rate lock on the file is locked at a negative net price…" and "where the closing cost credit reserved against the file is verified…". The compute reads these with `CFIELD('funding', 'variant_name', loan_file_id=HID)`, `CFIELD('lock', …)` and `CFIELD('credit', …)` and no status filter. On a file with several closings, locks or credits, the stored order decides which one counts; the rule doesn't say which.
2. **Stale cross-category note (authoring field, not published).** In `loan_ext_application_fee_due.cross_category[funding].note`, it still reads "the returning-borrower discount is decided by the disbursement date of the customer's funded Larkspur closing." That note was not updated with the funding-wire tier.
3. **Base B-1, unchanged.** `loan_condition_management` suspends on "any prior-to-documents condition … past its due date", but `loan_msr_overdue_conditions` counts overdue conditions of every class. (coordinator: BLUEPRINT-KNOWN, no action)
