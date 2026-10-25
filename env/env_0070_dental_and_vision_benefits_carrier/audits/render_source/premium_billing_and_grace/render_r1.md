# Render pre-scan findings — product billing (difficulty premium_billing_and_grace), render round 1
Source: renderer agent aefc90b325ef09997, 2026-10-19; saved verbatim by the coordinator. The renderer STOPPED before writing any document.
Gate line read: `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN`. All locations are in `env/env_0070_dental_and_vision_benefits_carrier/tasks/premium_billing_and_grace/billing.extended.yaml`.

### Rule vs compute mismatches (the rule says one thing, the compute does another)

**1. `billing_ext_grace_cure_payment`, factor `g_fee` (`fees_grace`, `grace_window`).**
- Rule: "the returned-payment fees booked in the grace period are collected, being every fee booked on or after the grace-period start date, which is the due date of a month and so its first day, counted as every fee booked within the whole calendar months from that date to the payment date plus one".
- The claimed equivalence is false. The compute's month count `MONTHS(gstart,NOW)+1` also takes in fees booked late in the month *before* the grace start.
- Example: grace start 2026-08-01, payment date 2026-10-19, fee booked 2026-07-28. `MONTHS(07-28,10-19)` = 2 = `MONTHS(08-01,10-19)`, so the compute collects the fee, but "on or after the grace-period start date" excludes it.

**2. `billing_ext_grace_cure_payment`, factor `g_relief` (`rets_before`).**
- Rule: "for an account with no returned payment in the twenty-four months before its grace period, counted as no more returned payments within twenty-four months before the payment date than within the whole calendar months from the grace-period start date to the payment date plus one".
- The "before its grace period" wording and the counting test measure different windows.
- Example (a): return on 2024-09-30, grace start 2026-08-01, payment 2026-10-19. The return falls within 24 months before the grace start, so the wording gives no relief. But `MONTHS` gives 24, which is not under 24, so the compute does not count it and grants relief.
- Example (b): a return late in July, before an 08-01 grace start, is counted by the compute as inside the grace window rather than before it.

**3. `billing_ext_renewal_payment`, factor `r_relief` (`rets_lb`, `rets_inv`, `inv_window`).**
- Rule: "no returned payment in the renewal_relief_lookback_months months before its renewal invoice, counted as no more returned payments within renewal_relief_lookback_months months before the payment date than within the whole calendar months from the renewal invoice's date to the payment date plus one".
- Example: renewal invoice 2026-08-17, payment 2026-10-19, return on 2026-08-10. The compute counts it in both windows (each `MONTHS` = 2), so the net is 0 and relief applies. The wording gives no relief, because the return is 7 days before the invoice.
- The 24-month window shift from 2(a) also applies here.

**4. Policies `billing_ext_dental_tier_credit` (`d_act_r`), `billing_ext_rider_end_credit` (`q_act_r`) and `billing_ext_renewal_payment` (`act_r`).**
- Rule: "each orthodontic rider the account funds that is active or applied at its plan's monthly premium per covered person, riders applied for after the invoice's date being left out".
- The compute only leaves out *applied* riders that share the latest application date. An *active* rider whose application date is after the last invoice is still priced in.
- Example: an Annual Prepay renewal invoice dated 08-17 and a rider applied 08-25 that is active by the payment date. The compute prices the rider into the invoice reading, so the invoice no longer matches and the re-billing amount or saving is not taken. The rule leaves the rider out and takes it.

### Branches the rule never states, and weaker mismatches (latent)
- **5. Prepay branch with no paid-through date.** In `vtc_window`, `dtc_window` and `rc_months`, when the prepay condition holds but no paid-through date is on record, the compute falls through to the grace or standard branch. The rule says nothing about this case.
- **6. "The dependent" is not filtered.** In `dep_end`/`dep_tier`, `qd_tier` and `dd_end`/`dd_tier`, the rule says "the dependent whose dental enrollment … ended for loss of eligibility". The compute has no enrollee-relationship filter, so a subscriber's own loss-of-eligibility enrollment would be picked up.
- **7. Vision enrollment not tied to the account.** In the invoice reading of policies 3 and 4 (`dv_*`, `cv_*`), the vision enrollment lacks "funded by the account" in the rule, while the compute filters by the account.
- **8. Tie rule missing.** In policy 4, "the dental plan being priced at the subscriber's current tier" does not say which active enrollment is used or how ties break. The compute uses the latest coverage effective date.

### Checked and clean
- No factor reads another factor's binding (checked mechanically on all five policies).
- Every `compute_basis` quote appears verbatim in its rule.
- All three prerequisite sentences appear verbatim in their rules and are in state form.

### Placement-only notes (coordinator: not routed, per the stop rule)
Some plain bindings are used by only one factor, for example `int_base`, `lag_base`, `rint_base`, `plan_units`, `vt_tenure`, `fee_in_grace`, `c_old`, `c_rid` and `inv_window`. Policy 5's scope sentence also names both the "dental saving" and the "rider saving".
