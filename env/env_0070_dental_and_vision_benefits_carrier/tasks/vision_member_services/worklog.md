INSTANTIATE round 1: gates 7/7 green
REWORK round 2: gates 7/7 green
REWORK round 3 claims: D1,D2,D3,D4,D5,D6,D7,D8,D9,D10,F0-5,F0-6,F0-7,F1-5,F1-6
REWORK round 3: gates 7/7 green
REWORK round 4 claims: E1,E3
REWORK round 4: gates 7/7 green
REWORK round 5 claims: G1,G2,G3
REWORK round 5 claims: G1,G2,G3,E2,E4,E5,E6
REWORK round 5: gates 7/7 green
REWORK round 6 claims: H1,H2,H3,H4,H5,H6,H7,H8,H9,H10
REWORK round 6: gates 7/7 green
REWORK round 7 claims: J1,J2,J3,J4,J5,J6,J7,J8,J10
REWORK round 7: gates 7/7 green
REWORK round 8 claims: K1,K2,K3,K4,K6
REWORK round 8: gates 7/7 green
REWORK round 9 claims: L1,L2
REWORK round 9: gates 7/7 green
REWORK round 10 seed pass (every paid/reversed/denied/open vision row and every billing row, both worlds, each checked against the vision and billing charters on its own date):
- T0 vision V73-261204-4409 exam PAID 2026-12-05: FIXED, priced by the exam-visit rule (chain 95.00 x new patient 1.25 x pediatric 1.10, child copay 5.00): plan_paid 125.63, copay 5.00, member 5.00.
- T0 vision reversal of V73-261204-4409 2026-12-06: FIXED, mirrors the original plan_paid 125.63, REVERSED, eligibility reason.
- T0 vision V73-261204-4417 exam + standard fitting, denied 2026-12-08 (before the binder): OK, DENIED_NOT_ELIGIBLE, plan 0.00, member the retail charge, received in 3 days.
- T0 vision V73-261211-4502 five out-of-network lines, received 2027-01-26, no remark: OK, inside timely_filing_days_oon 365, member holds the receipts.
- T0 vision V73-270104-4620 lens + frame and V73-270108-4630 specialty fitting + contacts, denied 2027-01-07 / 2027-01-12: OK on the record as it stood (enrollment still applied, activation not posted; the tasks' premise), plan 0.00, member the retail charge.
- T0 billing: invoices 2026-12 (at opening 2026-11-12, lead date passed), 2027-01 (2026-12-12), 2027-02 (2027-01-12) at 29.44 = Select 150 member_children, one premium per plan unit: OK. Binder 29.44 by check 2026-12-28 (deadline 2026-12-31) and regular 29.44 by check 2026-12-28: OK. Account active, paid through 2027-01-31, balance 29.44: OK.
- T1 vision V73-260912-5233 four out-of-network lines, received 2026-10-24, no remark: OK, inside 365 days.
- T1 vision V73-261006-5310 specialty refit, denied 2026-10-09: OK on the record as it stood (enrollment applied), plan 0.00, member 225.00.
- T1 billing: invoices 2026-09 (at opening 2026-08-18), 2026-10 (2026-09-11), 2026-11 (2026-10-12) at 14.72 = Select 150 member_only: OK. Binder 14.72 by check on the deadline day 2026-10-01 and regular 14.72 by check 2026-10-01: OK. Account active, paid through 2026-10-31, balance 14.72: OK.
REWORK round 10 claims: M1
REWORK round 10: gates 7/7 green
REWORK round 11 claims: R1,R2,R3,R4,R5,R6,R7
REWORK round 11: gates 7/7 green
REWORK round 12 claims: R2-1,R2-2
REWORK round 12: gates 7/7 green
REWORK round 13 claims: KB-TRACE-1
REWORK round 13: gates 7/7 green
REWORK round 14 claims: S1,S2
REWORK round 14: gates 7/7 green
REWORK round 15 amount comparison (glasses claim rule vs contact-lens claim rule, every amount both price):
- routine exam: oon_exam_reimbursement after the exam frequency, both: SAME.
- fitting: specialty oon_fit_specialty_reimbursement / standard oon_fit_standard_reimbursement / no fitting line 0.00, nothing without a contacts benefit, follows its claim's contact-lens line, both: SAME.
- contact lenses: medically necessary oon_contacts_medically_necessary_reimbursement / elective oon_contacts_elective_reimbursement, nothing without a contacts benefit, left out when glasses count in the period (glasses rule: in-lieu tier; contact-lens rule: contact-lens basis), both: SAME outcome.
- spectacle lenses: by lens type (progressive / trifocal / bifocal / single vision), nothing without a lens benefit, both: SAME.
- frame: nothing without a frame benefit / oon_child_frame_reimbursement under child_age_limit_years / oon_frame_reimbursement otherwise: DIFFERED (contact-lens rule had no children's amount) -> FIXED, now SAME in rule, baseline and compute.
- lens options never reimbursed, copays never deducted: SAME (contact-lens rule now states the options clause too).
- side test, frequency, in-lieu period test, binder and filing limit, rounding: SAME.
REWORK round 15 claims: N1
REWORK round 15: gates 7/7 green
