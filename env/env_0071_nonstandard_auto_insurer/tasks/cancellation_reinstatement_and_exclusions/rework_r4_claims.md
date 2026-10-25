# Rework round 4: claims per revision_3 audit item

No scored values are given here. NC/RE/IC = nonpayment return / lapse re-write / insured-request return (task 0).
AD/EX/AB = re-listing / reported-resident exclusion / exclusion lift (task 1).

## R3-01: factors whose tier a recorded figure already embeds (closed for the whole class, XF26)

**Term level (NC, RE, IC)**
- Removed every term-rating relativity on the premium: certificate form, certificate type, payment plan, plus the plain package, state and points relativities. The recorded full_term_premium already carried all of them.
- The standard figure is now the recorded current rate: full_term_premium plus or minus the shares recorded on change entries.
- Factors act only on what no record embeds:
  - **SR-26 run-off day count, NC and IC.** Built only from the keys points 24 and 25 accept: the company state schedule by filing state, certificate form, certificate type, and filing state against garaging state. In IC the filing-state-against-garaging-state component is plain.
  - **RE's own re-written days**, capped by the days the nonpayment return gave back.
  - **Changes at the re-write since the term was rated:**
    - nonpayment history;
    - prior-insurance lapse, a point 23 dimension;
    - the named insured's age class: the certificate certifies her date of birth, and her class at binding is the one embedded in the recorded premium.
  - **IC's own methods:** short-rate retention by request reason and days in force; minimum-earned acquisition.
- **IC's daily basis** reads the re-written entry (a recorded figure). For that reason no relativity re-applies in IC.
- **Task 0 world:** the SR-22 requirement now comes from a Texas order, so the certificate's filing state differs from the Georgia garaging state.

**Driver level (AD, EX, AB)**
- **AD** (Wendell, a resident rated earlier in the term) uses his recorded share as the standard. Its factors carry only what changed since that share was rated:
  - age class at the rating date versus the report date;
  - points tier on the rating entry versus his most recent entry;
  - accidents and platform use reported while he was unlisted, which the share rated while he was listed cannot carry.
- **EX and AB** rate drivers who were never rated on the term (Brianna and Marcus were excluded at binding with no share), so no recorded share embeds their rating.

**Change of EX's computation (within the exclusion event)**
- An exclusion return of a recorded share cannot carry factors under XF26, so EX was re-scoped under the new id `auto_ext_reported_resident_exclusion`, with a new tool.
- It covers a resident reported operating while unlisted and named on a signed exclusion form. In one endorsement she is listed from the report date and excluded from the form's effective date, and charged the listing period at her full driver rating.
- It overrides the base clause "unlisted -> no premium change" for this case only. Sibling overwrites in AD, EX and AB each name the others' cases.

**Draws kept:** NC 5, RE 4, IC 6; AD 5, EX 6, AB 6.

**Tree and edges:**
- AB depends on AD by value: AB's occasional-operator relativity reads the rated-driver count, which the re-listing raises.
- AB depends on EX through a state gate: every signed form must be endorsed.
- Task 0's edges are unchanged.

**Probes:** every changed read was probed on scratch copies.

## R3-02: rate plan vs driver shares

- The term rules no longer state a term rating plan. The current rate is the recorded premium, which carries the shares of drivers rated at binding, plus or minus recorded change shares. This is consistent with the base charter.
- The task 1 seed now has no binding-rated driver other than the named insured, so there is no longer a refund of a share the premium never carried.
- Wendell's added share and its removal return are booked and billed consistently, using the company's driver rating on his added date.

## Observation items corrected

- **Docstrings:** the return-premium and re-written-premium descriptions now say "0.00 or more, a 0.00 amount booking no premium transaction". This matches the tool bodies.
- **processing_lag_days:** now defined where it is used. The NC rule states that it is zero days.
- **Rescinded July notice:** still counted in the nonpayment history ("every notice of cancellation for nonpayment issued on the term"), as before.
