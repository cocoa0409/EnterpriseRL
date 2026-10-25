# rework_claims_r7 — cpi_insurance_verification_and_force_placement (render_source r1: R1-R7 + note; class sweeps)

- R1 (gap owned by one factor, read by all three allowances): cm_gap / cp_gap is now a plain binding defined once in the standard method (gapdef). The first allowance is now keyed on the contract's vehicle book value (cm/cp_value_grace) instead of the CPI plan, because a factor needs a record read for its tier. It uses the same bands and the same days in both worlds. Each grace factor now owns only its own key and allowance; result reads only the decided allowances.
- R2 (plain bindings used only by the covered-days factor): cm_a_n, cm_b_n, cm_ov and cp_a_n, cp_b_n, cp_ov now belong to cm_cover_rule / cp_cover_rule. The standard covered-days count reads only plain bindings (start, closed, latest reaching effective date).
- R3 (standard sentence deferring to a retired base clause): "counted as the base refund rule counts an accepted proof's days:" is removed from both refund rules; the explicit definition stays.
- R4 (open-record outcome undefined): the re-review overwrite now names its own scope. On every tracking record, closed or not, an accepted re-review under these rules is recorded as a new review entry only: no status change, no update to the policy details on file, no cancellation of placed coverage, no notice. This matches what the three re-review tools write. The base status-return clause is retired for these re-reviews, and the "outside this rule" sentence restates it in full for accepted first reviews: return to compliant, cancellation of placed coverage, refunds and the cancellation notice.
- R5 (+ class sweep, rule text naming another policy's or factor's quantities): the upload rule no longer mentions a loan-to-value allowance or an expiry buffer. Its binder sentence now says the reach test compares the expiration date with the reach date itself. No other rule sentence names a sibling's factor quantity.
- R6 (binder_accepted no longer carried): the "outside this rule" sentence now requires, for a binder, binder_accepted true and a period no longer than binder_max_days. Sweep: every clause the five rules retire has its remaining in-force part restated.
- R7 (unstated ordering key): both refund rules now pick "the capitalised premium charge ... with the latest billing_period_start". Sweep: every other pick names its key (review date, or latest policy_effective_date with the tie rule).
- Note (trigger vs customer-run tool): the closing-period refund trigger is now on_request, matching the borrower-run refund tool. Task 1's request binding now cites the borrower's own request.
- Class sweeps run over all five policies:
  - factor-owned bindings read by result or by other factors: none remain, apart from each factor's decided input;
  - plain bindings used by a single factor: only the latest reaching effective date remains, and the standard method reads it;
  - deferrals to retired clauses: none;
  - unstated ordering keys: none.
- Figures: every scored value, standard result and solo sensitivity is unchanged in both tasks; traces were regenerated from the replayed values. Gates 7/7.
