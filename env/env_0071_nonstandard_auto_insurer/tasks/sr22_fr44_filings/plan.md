# plan — sr22_fr44_filings (category fr), M=2

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=1, factor_counts=[6,5]
- task 1: prerequisite_problems=2, factor_counts=[4,6,6]

Constraint analysis (why this shape):
- fr numeric write fields: fr_filing_transactions.amount (fee assessed / waived) and SR-26
  certificate_end_date (derivable from an integer run-off day count passed in). DSL is HID-scoped
  for own category (no cross-filing reads), so every value_input edge must write on the dependent's
  own HID filing (or its fee/doc rows).
- Customer-owned numeric writes in fr: only a certificate request (the filer orders the certificate,
  gives license data verbatim, accepts the fee billed on the plan). A release request carries no number.
- Fee reversals are always "the fee's full amount" (no load-bearing factors possible) -> not used.

Problems (5 extended policies, 5 tools):
- T0 root  fr_ext_refiling_fee        user  order_refiled_certificate_<u8>   6 factors  HID = replaced certificate
- T0 prereq fr_ext_lapse_sr26_runoff  agent transmit_lapse_sr26_<u8>        5 factors  HID = same certificate (value_input)
- T1 root  fr_ext_household_fee       user  order_household_certificate_<u8> 6 factors  HID = term's existing certificate
- T1 prereq fr_ext_unbilled_fee       agent post_unbilled_filing_fee_<u8>   6 factors  HID = same (value_input)
- T1 prereq fr_ext_removal_sr26_runoff agent transmit_removal_sr26_<u8>     4 factors  HID = same (value_input)

T0 story: FL FR-44 Operator certificate on a Non-Owner 100/300/50 term cancelled for nonpayment and
reinstated WITH a lapse before the SR-26 went out. Overwrite (scoped) of fr_sr26_notice suppression
clause: a with-lapse reinstatement still gets its SR-26 for the lapse and a reinstatement_refiling.
T1 story: VA owner term backs the husband's SR-22 Owner certificate (fee never posted); husband
excluded from the term; named insured now needs her own VA FR-44 Owner-Operator.

Steps: write extended yaml base copy (script, never staged in context) -> T0 policies -> tools ->
seed -> persona -> verify -> GT -> gates; then T1 same; then final gates; worklog.md running.
Scratch: /tmp/sr22_fr44_filings_0071/ only.

## Round 2 re-tree (audit F-G1..F-G10)
- T0 unchanged tree, re-keyed: fr_ext_lapse_sr26_runoff (5) <- root fr_ext_refiling_fee (6); customer now a Georgia
  resident with a Florida FR-44 (out-of-state filing).
- T1 replaced: fr_ext_owner_sr26_runoff (4, transmit_owner_sr26_911d0783) <- fr_ext_unbilled_fee (6, fee charged
  again after full company_error reversals) <- root fr_ext_moved_refiling_fee (6, order_moved_certificate_231455f7,
  state_change refiling after a TX -> VA move). Removal SR-26 and household fee dropped (no 4-6 real keys).

## Round 3 note
Factors re-cut to real dimensions only (coverage end/restoration, certificate type and backing, out-of-state filing,
requirement period, transfer vs refiling after lapse); limits, plan and home-state charges struck; fee charged again
has a minimum; moved-certificate wait carved out by record test; lapse suppression replaced_by restates owner cases.

## Round 4 note
Re-split the SR-26 rules by restoration (lapse vs cancelled-not-reinstated, any backing); every factor keyed on
the publishable keys only; fees priced by the certificate's standing with the state; late SR-26 sent at once.
fr_ext_owner_sr26_runoff renamed fr_ext_cancellation_sr26_runoff (tool transmit_cancellation_sr26_eaec830f).

## Round 5 note
Type+backing one factor; only in-scope tiers; lapse-length counting; flat company fees so form is charged once;
moved fee waits on a standing fee by state gate; sibling timely overwrites name each other (day 0 per case).
