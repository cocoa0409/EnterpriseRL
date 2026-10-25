# Seed-row legality cross-check: Insurance Claim (Third-Party Billing) rows, env_0073 tasks 0 and 1

Criterion: the published docs in env/env_0073_regional_hospital_system/docs/claim/*.json (title + content). Each row was checked against the docs in force as of its posting date. Doc file names below drop the hash suffix and `.json`.

Frozen times: task 0 2025-10-21 10:20 CDT; task 1 2025-11-18 14:05 CST. `find_claim_appeal_authorizations` is empty in both tasks. Both appeals are UNDERPAYMENT_APPEAL. That is a provider-level appeal, because the docs list member-level appeals as "a member appeal with the patient's authorized-representative form, a Medicare Advantage reconsideration or a Medicaid HMO appeal filed for the patient". So no authorization is required, and the empty authorization lookup is consistent with the rows.

## 1. Every row

| Task | Claim | Row type | Date | Amount / key fields | Verdict | Docs relied on |
|---|---|---|---|---|---|---|
| T0 | C0 | claim header | 2024-09-22 | Commercial PPO Claim, Anthem Blue Cross Blue Shield, closed, PRIMARY; acct Outpatient Surgery Account (Grand Chute, MEDICALLY_NECESSARY); DOS 2024-09-17; submitted 2024-09-22 (final bill 2024-09-22); adjudicated 2024-10-15; denial - NONE; appeal_level 0; billed 9640.00 (gross 9640.00); payer_balance 0.00; closed 2024-10-15; prior_auth '' | OK | timely_filing_rule, payer_class_filing_and_submission_limits, contract_modeling_and_underpayment_thresholds (30-day clean claim; closes at zero balance), claims_per_encounter_and_coverage_order, claim_submission_acknowledgement_and_follow_up, claim_follow_up_and_coordination_settings |
| T0 | C1 | claim header | 2025-01-24 | Commercial PPO Claim, Anthem Blue Cross Blue Shield, closed, PRIMARY; acct Inpatient Admission Account (Appleton, EMERGENCY); DOS 2025-01-14; submitted 2025-01-24 (final bill 2025-01-24); adjudicated 2025-02-20; denial - NONE; appeal_level 0; billed 64250.00 (gross 64250.00); payer_balance 0.00; closed 2025-02-20; prior_auth '' | OK | timely_filing_rule, payer_class_filing_and_submission_limits, contract_modeling_and_underpayment_thresholds (30-day clean claim; closes at zero balance), claims_per_encounter_and_coverage_order, claim_submission_acknowledgement_and_follow_up, claim_follow_up_and_coordination_settings |
| T0 | C2 | claim header | 2025-03-08 | Commercial PPO Claim, Anthem Blue Cross Blue Shield, closed, PRIMARY; acct Outpatient Clinic Visit Account (Neenah, MEDICALLY_NECESSARY); DOS 2025-03-05; submitted 2025-03-08 (final bill 2025-03-08); adjudicated -; denial 2025-03-27 PR-27; appeal_level 0; billed 420.00 (gross 420.00); payer_balance 0.00; closed 2025-03-27; prior_auth '' | OK | timely_filing_rule, payer_class_filing_and_submission_limits, contract_modeling_and_underpayment_thresholds (30-day clean claim; closes at zero balance), claims_per_encounter_and_coverage_order, claim_submission_acknowledgement_and_follow_up, claim_follow_up_and_coordination_settings, denial_and_rejection_routing, denial_reason_routing_and_write_off_limits |
| T0 | C3 | claim header | 2025-07-27 | Marketplace Exchange Plan Claim, Common Ground Healthcare Cooperative, appealed, PRIMARY; acct Observation Stay Account (Appleton, EMERGENCY); DOS 2025-07-22; submitted 2025-07-27 (final bill 2025-07-27); adjudicated 2025-08-20; denial - NONE; appeal_level 1; billed 9840.00 (gross 9840.00); payer_balance 0.00; closed -; prior_auth '' | OK | timely_filing_rule, payer_class_filing_and_submission_limits, contract_modeling_and_underpayment_thresholds (30-day clean claim; closes at zero balance), claims_per_encounter_and_coverage_order, claim_submission_acknowledgement_and_follow_up, claim_follow_up_and_coordination_settings, appeal_levels_and_windows, payer_class_appeal_rights_schedule |
| T0 | C4 | claim header | 2025-08-16 | Marketplace Exchange Plan Claim, Common Ground Healthcare Cooperative, closed, PRIMARY; acct Outpatient Diagnostic Imaging & Lab Account (Grand Chute, MEDICALLY_NECESSARY); DOS 2025-08-12; submitted 2025-08-16 (final bill 2025-08-16); adjudicated 2025-09-10; denial - NONE; appeal_level 0; billed 3460.00 (gross 3460.00); payer_balance 0.00; closed 2025-09-10; prior_auth '' | OK | timely_filing_rule, payer_class_filing_and_submission_limits, contract_modeling_and_underpayment_thresholds (30-day clean claim; closes at zero balance), claims_per_encounter_and_coverage_order, claim_submission_acknowledgement_and_follow_up, claim_follow_up_and_coordination_settings |
| T0 | C5 | claim header | 2025-09-12 | Marketplace Exchange Plan Claim, Common Ground Healthcare Cooperative, closed, PRIMARY; acct Outpatient Clinic Visit Account (Neenah, MEDICALLY_NECESSARY); DOS 2025-09-09; submitted 2025-09-12 (final bill 2025-09-12); adjudicated 2025-09-24; denial - NONE; appeal_level 0; billed 285.00 (gross 285.00); payer_balance 0.00; closed 2025-09-24; prior_auth '' | OK | timely_filing_rule, payer_class_filing_and_submission_limits, contract_modeling_and_underpayment_thresholds (30-day clean claim; closes at zero balance), claims_per_encounter_and_coverage_order, claim_submission_acknowledgement_and_follow_up, claim_follow_up_and_coordination_settings |
| T0 | C6 | claim header | 2025-10-04 | Marketplace Exchange Plan Claim, Common Ground Healthcare Cooperative, accepted, PRIMARY; acct Outpatient Diagnostic Imaging & Lab Account (Appleton, MEDICALLY_NECESSARY); DOS 2025-09-30; submitted 2025-10-04 (final bill 2025-10-04); adjudicated -; denial - NONE; appeal_level 0; billed 2180.00 (gross 2180.00); payer_balance 2180.00; closed -; prior_auth '' | OK | timely_filing_rule, payer_class_filing_and_submission_limits, contract_modeling_and_underpayment_thresholds (30-day clean claim; closes at zero balance), claims_per_encounter_and_coverage_order, claim_submission_acknowledgement_and_follow_up, claim_follow_up_and_coordination_settings |
| T0 | C0 | claim_billed | 2024-09-22 | 9640.00 | OK | payer_class_filing_and_submission_limits, timely_filing_rule, claims_per_encounter_and_coverage_order |
| T0 | C0 | claim_payment_posted | 2024-10-15 | 2911.52 remit EFT44A1015887 2024-10-15 | OK | remittance_posting_and_underpayment_modeling, contract_modeling_and_underpayment_thresholds |
| T0 | C0 | claim_contractual_adjustment | 2024-10-15 | 4000.60 CO-45 remit EFT44A1015887 2024-10-15 | OK | remittance_posting_and_underpayment_modeling, denial_reason_routing_and_write_off_limits |
| T0 | C0 | claim_patient_resp_transferred | 2024-10-15 | 2000.00 PR-1 remit EFT44A1015887 2024-10-15 | OK | remittance_posting_and_underpayment_modeling, coordination_of_benefits_across_payers |
| T0 | C0 | claim_patient_resp_transferred | 2024-10-15 | 727.88 PR-2 remit EFT44A1015887 2024-10-15 | OK | remittance_posting_and_underpayment_modeling, coordination_of_benefits_across_payers |
| T0 | C1 | claim_billed | 2025-01-24 | 64250.00 | OK | payer_class_filing_and_submission_limits, timely_filing_rule, claims_per_encounter_and_coverage_order |
| T0 | C1 | claim_payment_posted | 2025-02-20 | 29586.25 remit EFT44A0220514 2025-02-20 | OK | remittance_posting_and_underpayment_modeling, contract_modeling_and_underpayment_thresholds |
| T0 | C1 | claim_contractual_adjustment | 2025-02-20 | 26663.75 CO-45 remit EFT44A0220514 2025-02-20 | OK | remittance_posting_and_underpayment_modeling, denial_reason_routing_and_write_off_limits |
| T0 | C1 | claim_patient_resp_transferred | 2025-02-20 | 3000.00 PR-1 remit EFT44A0220514 2025-02-20 | OK | remittance_posting_and_underpayment_modeling, coordination_of_benefits_across_payers |
| T0 | C1 | claim_patient_resp_transferred | 2025-02-20 | 5000.00 PR-2 remit EFT44A0220514 2025-02-20 | OK | remittance_posting_and_underpayment_modeling, coordination_of_benefits_across_payers |
| T0 | C2 | claim_billed | 2025-03-08 | 420.00 | OK | payer_class_filing_and_submission_limits, timely_filing_rule, claims_per_encounter_and_coverage_order |
| T0 | C2 | claim_patient_resp_transferred | 2025-03-27 | 420.00 PR-27 remit EFT44A0327110 2025-03-27 | OK | denial_and_rejection_routing, denial_reason_routing_and_write_off_limits, remittance_posting_and_underpayment_modeling |
| T0 | C3 | claim_billed | 2025-07-27 | 9840.00 | OK | payer_class_filing_and_submission_limits, timely_filing_rule, claims_per_encounter_and_coverage_order |
| T0 | C3 | claim_payment_posted | 2025-08-20 | 854.40 remit EFT44C0820406 2025-08-20 | OK | remittance_posting_and_underpayment_modeling, contract_modeling_and_underpayment_thresholds |
| T0 | C3 | claim_contractual_adjustment | 2025-08-20 | 5416.00 CO-45 remit EFT44C0820406 2025-08-20 | OK | remittance_posting_and_underpayment_modeling, denial_reason_routing_and_write_off_limits |
| T0 | C3 | claim_patient_resp_transferred | 2025-08-20 | 3000.00 PR-1 remit EFT44C0820406 2025-08-20 | OK | remittance_posting_and_underpayment_modeling, coordination_of_benefits_across_payers |
| T0 | C3 | claim_patient_resp_transferred | 2025-08-20 | 569.60 PR-2 remit EFT44C0820406 2025-08-20 | OK | remittance_posting_and_underpayment_modeling, coordination_of_benefits_across_payers |
| T0 | C3 | claim_appeal_filed | 2025-08-28 | 0.00 level 1 UNDERPAYMENT_APPEAL | OK | appeal_levels_and_windows, payer_class_appeal_rights_schedule, remittance_posting_and_underpayment_modeling, authorized_representative_for_member_appeals |
| T0 | C4 | claim_billed | 2025-08-16 | 3460.00 | OK | payer_class_filing_and_submission_limits, timely_filing_rule, claims_per_encounter_and_coverage_order |
| T0 | C4 | claim_payment_posted | 2025-09-10 | 114.80 remit EFT44C0910277 2025-09-10 | OK | remittance_posting_and_underpayment_modeling, contract_modeling_and_underpayment_thresholds |
| T0 | C4 | claim_contractual_adjustment | 2025-09-10 | 1816.50 CO-45 remit EFT44C0910277 2025-09-10 | OK | remittance_posting_and_underpayment_modeling, denial_reason_routing_and_write_off_limits |
| T0 | C4 | claim_patient_resp_transferred | 2025-09-10 | 1500.00 PR-1 remit EFT44C0910277 2025-09-10 | OK | remittance_posting_and_underpayment_modeling, coordination_of_benefits_across_payers |
| T0 | C4 | claim_patient_resp_transferred | 2025-09-10 | 28.70 PR-2 remit EFT44C0910277 2025-09-10 | OK | remittance_posting_and_underpayment_modeling, coordination_of_benefits_across_payers |
| T0 | C5 | claim_billed | 2025-09-12 | 285.00 | OK | payer_class_filing_and_submission_limits, timely_filing_rule, claims_per_encounter_and_coverage_order |
| T0 | C5 | claim_payment_posted | 2025-09-24 | 95.38 remit EFT44C0924019 2025-09-24 | OK | remittance_posting_and_underpayment_modeling, contract_modeling_and_underpayment_thresholds |
| T0 | C5 | claim_contractual_adjustment | 2025-09-24 | 149.62 CO-45 remit EFT44C0924019 2025-09-24 | OK | remittance_posting_and_underpayment_modeling, denial_reason_routing_and_write_off_limits |
| T0 | C5 | claim_patient_resp_transferred | 2025-09-24 | 40.00 PR-3 remit EFT44C0924019 2025-09-24 | OK | remittance_posting_and_underpayment_modeling, coordination_of_benefits_across_payers |
| T0 | C6 | claim_billed | 2025-10-04 | 2180.00 | OK | payer_class_filing_and_submission_limits, timely_filing_rule, claims_per_encounter_and_coverage_order |
| T0 | - | find_claim_appeal_authorizations | - | empty | OK (no member-level appeal on file) | authorized_representative_for_member_appeals, authorized_representative_form_requirements |
| T1 | C0 | claim header | 2025-01-13 | Commercial HMO Claim, Network Health Plan, closed, PRIMARY; acct Emergency Department Visit Account (Appleton, EMERGENCY); DOS 2025-01-09; submitted 2025-01-13 (final bill 2025-01-13); adjudicated 2025-02-05; denial - NONE; appeal_level 0; billed 4880.00 (gross 4880.00); payer_balance 0.00; closed 2025-02-05; prior_auth '' | OK | timely_filing_rule, payer_class_filing_and_submission_limits, contract_modeling_and_underpayment_thresholds (30-day clean claim; closes at zero balance), claims_per_encounter_and_coverage_order, claim_submission_acknowledgement_and_follow_up, claim_follow_up_and_coordination_settings |
| T1 | C1 | claim header | 2025-05-17 | Commercial HMO Claim, Network Health Plan, closed, PRIMARY; acct Outpatient Clinic Visit Account (Neenah, ELECTIVE_NON_COVERED); DOS 2025-05-14; submitted 2025-05-17 (final bill 2025-05-17); adjudicated -; denial 2025-06-13 PR-27; appeal_level 0; billed 1180.00 (gross 1180.00); payer_balance 0.00; closed 2025-06-13; prior_auth '' | OK | timely_filing_rule, payer_class_filing_and_submission_limits, contract_modeling_and_underpayment_thresholds (30-day clean claim; closes at zero balance), claims_per_encounter_and_coverage_order, claim_submission_acknowledgement_and_follow_up, claim_follow_up_and_coordination_settings, denial_and_rejection_routing, denial_reason_routing_and_write_off_limits |
| T1 | C2 | claim header | 2025-06-15 | Commercial HMO Claim, Quartz Health Solutions, appealed, PRIMARY; acct Outpatient Surgery Account (Appleton, MEDICALLY_NECESSARY); DOS 2025-06-10; submitted 2025-06-15 (final bill 2025-06-15); adjudicated 2025-07-08; denial - NONE; appeal_level 1; billed 14860.00 (gross 14860.00); payer_balance 0.00; closed -; prior_auth '' | OK | timely_filing_rule, payer_class_filing_and_submission_limits, contract_modeling_and_underpayment_thresholds (30-day clean claim; closes at zero balance), claims_per_encounter_and_coverage_order, claim_submission_acknowledgement_and_follow_up, claim_follow_up_and_coordination_settings, appeal_levels_and_windows, payer_class_appeal_rights_schedule |
| T1 | C3 | claim header | 2025-10-24 | Commercial HMO Claim, Quartz Health Solutions, closed, PRIMARY; acct Outpatient Diagnostic Imaging & Lab Account (Grand Chute, MEDICALLY_NECESSARY); DOS 2025-10-20; submitted 2025-10-24 (final bill 2025-10-24); adjudicated 2025-11-10; denial - NONE; appeal_level 0; billed 2960.00 (gross 2960.00); payer_balance 0.00; closed 2025-11-10; prior_auth '' | OK | timely_filing_rule, payer_class_filing_and_submission_limits, contract_modeling_and_underpayment_thresholds (30-day clean claim; closes at zero balance), claims_per_encounter_and_coverage_order, claim_submission_acknowledgement_and_follow_up, claim_follow_up_and_coordination_settings |
| T1 | C4 | claim header | 2025-11-13 | Commercial HMO Claim, Security Health Plan of Wisconsin, accepted, PRIMARY; acct Emergency Department Visit Account (Appleton, EMERGENCY); DOS 2025-11-09; submitted 2025-11-13 (final bill 2025-11-13); adjudicated -; denial - NONE; appeal_level 0; billed 1650.00 (gross 1650.00); payer_balance 1650.00; closed -; prior_auth '' | OK | timely_filing_rule, payer_class_filing_and_submission_limits, contract_modeling_and_underpayment_thresholds (30-day clean claim; closes at zero balance), claims_per_encounter_and_coverage_order, claim_submission_acknowledgement_and_follow_up, claim_follow_up_and_coordination_settings |
| T1 | C5 | claim header | 2025-10-31 | Commercial HMO Claim, Quartz Health Solutions, closed, PRIMARY; acct Outpatient Clinic Visit Account (Neenah, MEDICALLY_NECESSARY); DOS 2025-10-28; submitted 2025-10-31 (final bill 2025-10-31); adjudicated -; denial 2025-11-17 PR-27; appeal_level 0; billed 830.00 (gross 830.00); payer_balance 0.00; closed 2025-11-17; prior_auth '' | OK | timely_filing_rule, payer_class_filing_and_submission_limits, contract_modeling_and_underpayment_thresholds (30-day clean claim; closes at zero balance), claims_per_encounter_and_coverage_order, claim_submission_acknowledgement_and_follow_up, claim_follow_up_and_coordination_settings, denial_and_rejection_routing, denial_reason_routing_and_write_off_limits |
| T1 | C0 | claim_billed | 2025-01-13 | 4880.00 | OK | payer_class_filing_and_submission_limits, timely_filing_rule, claims_per_encounter_and_coverage_order |
| T1 | C0 | claim_payment_posted | 2025-02-05 | 849.60 remit EFT44N0205114 2025-02-05 | OK | remittance_posting_and_underpayment_modeling, contract_modeling_and_underpayment_thresholds |
| T1 | C0 | claim_contractual_adjustment | 2025-02-05 | 1818.00 CO-45 remit EFT44N0205114 2025-02-05 | OK | remittance_posting_and_underpayment_modeling, denial_reason_routing_and_write_off_limits |
| T1 | C0 | claim_patient_resp_transferred | 2025-02-05 | 2000.00 PR-1 remit EFT44N0205114 2025-02-05 | OK | remittance_posting_and_underpayment_modeling, coordination_of_benefits_across_payers |
| T1 | C0 | claim_patient_resp_transferred | 2025-02-05 | 212.40 PR-2 remit EFT44N0205114 2025-02-05 | OK | remittance_posting_and_underpayment_modeling, coordination_of_benefits_across_payers |
| T1 | C1 | claim_billed | 2025-05-17 | 1180.00 | OK | payer_class_filing_and_submission_limits, timely_filing_rule, claims_per_encounter_and_coverage_order |
| T1 | C1 | claim_patient_resp_transferred | 2025-06-13 | 1180.00 PR-27 remit EFT44N0613308 2025-06-13 | OK | denial_and_rejection_routing, denial_reason_routing_and_write_off_limits, remittance_posting_and_underpayment_modeling |
| T1 | C2 | claim_billed | 2025-06-15 | 14860.00 | OK | payer_class_filing_and_submission_limits, timely_filing_rule, claims_per_encounter_and_coverage_order |
| T1 | C2 | claim_payment_posted | 2025-07-08 | 2946.00 remit EFT44Q0708215 2025-07-08 | OK | remittance_posting_and_underpayment_modeling, contract_modeling_and_underpayment_thresholds |
| T1 | C2 | claim_contractual_adjustment | 2025-07-08 | 8677.50 CO-45 remit EFT44Q0708215 2025-07-08 | OK | remittance_posting_and_underpayment_modeling, denial_reason_routing_and_write_off_limits |
| T1 | C2 | claim_patient_resp_transferred | 2025-07-08 | 2500.00 PR-1 remit EFT44Q0708215 2025-07-08 | OK | remittance_posting_and_underpayment_modeling, coordination_of_benefits_across_payers |
| T1 | C2 | claim_patient_resp_transferred | 2025-07-08 | 736.50 PR-2 remit EFT44Q0708215 2025-07-08 | OK | remittance_posting_and_underpayment_modeling, coordination_of_benefits_across_payers |
| T1 | C2 | claim_appeal_filed | 2025-09-24 | 0.00 level 1 UNDERPAYMENT_APPEAL | OK | appeal_levels_and_windows, payer_class_appeal_rights_schedule, remittance_posting_and_underpayment_modeling, authorized_representative_for_member_appeals |
| T1 | C3 | claim_billed | 2025-10-24 | 2960.00 | OK | payer_class_filing_and_submission_limits, timely_filing_rule, claims_per_encounter_and_coverage_order |
| T1 | C3 | claim_payment_posted | 2025-11-10 | 1171.36 remit EFT44Q1110402 2025-11-10 | OK | remittance_posting_and_underpayment_modeling, contract_modeling_and_underpayment_thresholds |
| T1 | C3 | claim_contractual_adjustment | 2025-11-10 | 1420.80 CO-45 remit EFT44Q1110402 2025-11-10 | OK | remittance_posting_and_underpayment_modeling, denial_reason_routing_and_write_off_limits |
| T1 | C3 | claim_patient_resp_transferred | 2025-11-10 | 75.00 PR-3 remit EFT44Q1110402 2025-11-10 | OK | remittance_posting_and_underpayment_modeling, coordination_of_benefits_across_payers |
| T1 | C3 | claim_patient_resp_transferred | 2025-11-10 | 292.84 PR-2 remit EFT44Q1110402 2025-11-10 | OK | remittance_posting_and_underpayment_modeling, coordination_of_benefits_across_payers |
| T1 | C4 | claim_billed | 2025-11-13 | 1650.00 | OK | payer_class_filing_and_submission_limits, timely_filing_rule, claims_per_encounter_and_coverage_order |
| T1 | C5 | claim_billed | 2025-10-31 | 830.00 | OK | payer_class_filing_and_submission_limits, timely_filing_rule, claims_per_encounter_and_coverage_order |
| T1 | C5 | claim_patient_resp_transferred | 2025-11-17 | 830.00 PR-27 remit EFT44Q1117512 2025-11-17 | OK | denial_and_rejection_routing, denial_reason_routing_and_write_off_limits, remittance_posting_and_underpayment_modeling |
| T1 | - | find_claim_appeal_authorizations | - | empty | OK (no member-level appeal on file) | authorized_representative_for_member_appeals, authorized_representative_form_requirements |

## 1a. Per-claim arithmetic behind the OK verdicts

Remittance identity: billed = payment + CO-45 + PR lines. The allowed amount is payment + PR lines. Expected allowed is billed x the class percentage, from contract_modeling_and_underpayment_thresholds: PPO 58.5%, HMO 52%, Marketplace 47.5%. The variance floor is max(USD threshold, 2% of expected), per remittance_posting_and_underpayment_modeling.

| Task | Claim | Billed | Pay + CO-45 + PR = billed? | Allowed / expected | Shortfall vs floor | Submit−DOS (limit) | Adjudication or denial − submit (30-day clean claim) | Account liabilities posted from the claim |
|---|---|---|---|---|---|---|---|---|
| T0 | C0 | 9640.00 | 2911.52+4000.60+2000+727.88 = 9640.00 yes | 5639.40 / 5639.40 | 0.00 < 112.79, no appeal due | 5 (180) | 23 | DEDUCTIBLE 2000, COINSURANCE 727.88 on 2024-10-15 = PR-1/PR-2 |
| T0 | C1 | 64250.00 | 29586.25+26663.75+3000+5000 yes | 37586.25 / 37586.25 | 0.00 | 10 (180) | 27 | 3000 / 5000 on 2025-02-20 match |
| T0 | C2 | 420.00 | PR-27 420.00 = billed, yes | - | - | 3 (180) | 19 (denial) | COVERAGE_TERMINATED 420 on 2025-03-27; account financial class now SELF_PAY ("the encounter's financial class is corrected") |
| T0 | C3 | 9840.00 | 854.40+5416.00+3000+569.60 yes | 4424.00 / 4674.00 | 250.00 ≥ 93.48, underpayment appeal routed | 5 (180) | 24 | 3000 / 569.60 on 2025-08-20 match |
| T0 | C4 | 3460.00 | 114.80+1816.50+1500+28.70 yes | 1643.50 / 1643.50 | 0.00 | 4 (180) | 25 | 1500 / 28.70 on 2025-09-10 match |
| T0 | C5 | 285.00 | 95.38+149.62+40 yes | 135.38 / 135.38 | 0.00 | 3 (180) | 12 | COPAY 40 on 2025-09-24 matches PR-3 |
| T0 | C6 | 2180.00 | billed only; payer_balance 2180.00 | - | - | 4 (180) | pending 17 days at freeze (< 30; first follow-up at day 30) | none (correct, nothing remitted) |
| T1 | C0 | 4880.00 | 849.60+1818.00+2000+212.40 yes | 3062.00 / 2537.60 | overpaid vs model, no appeal due | 4 (120) | 23 | 2000 / 212.40 on 2025-02-05 match |
| T1 | C1 | 1180.00 | PR-27 1180.00 = billed, yes | - | - | 3 (120) | 27 (denial) | COVERAGE_TERMINATED 1180; account SELF_PAY |
| T1 | C2 | 14860.00 | 2946+8677.50+2500+736.50 yes | 6182.50 / 7727.20 | 1544.70 ≥ 154.54, underpayment appeal routed | 5 (120) | 23 | 2500 / 736.50 on 2025-07-08 match |
| T1 | C3 | 2960.00 | 1171.36+1420.80+75+292.84 yes | 1539.20 / 1539.20 | 0.00 | 4 (120) | 17 | COPAY 75, COINSURANCE 292.84 on 2025-11-10 match |
| T1 | C4 | 1650.00 | billed only; payer_balance 1650.00 | - | - | 4 (120) | pending 5 days at freeze (< 30) | none |
| T1 | C5 | 830.00 | PR-27 830.00 = billed, yes | - | - | 3 (120) | 17 (denial) | COVERAGE_TERMINATED 830 on 2025-11-17; account SELF_PAY |

Appeals:
- **T0 C3, Marketplace.** Level 1 UNDERPAYMENT_APPEAL was received 2025-08-28, 8 days after the 2025-08-20 remittance. The provider window is 180 days with 0 presumed-receipt days, and 2 levels are available, so level 1 is legal and filed once. The payer decides within 60 days, by 2025-10-27, which is after the 2025-10-21 freeze, so `appealed` is consistent. The contract variance condition holds (250.00 ≥ 93.48).
- **T1 C2, HMO.** Level 1 UNDERPAYMENT_APPEAL was received 2025-09-24, 78 days after the 2025-07-08 remittance. The HMO provider window is 90 days, so it was received in time. The decision is due by 2025-11-23, which is after the 2025-11-18 freeze, so `appealed` is consistent. The variance holds (1544.70 ≥ 154.54).
- **Neither appeal is member-level.** Neither needs an authorization row, so the empty `find_claim_appeal_authorizations` is consistent. Neither is at the last internal level (2), which member_decision_denial_close_out reserves for the member's own appeal.

Other checks with no issue:
- **Billing data.** Billed amounts equal the account gross charges, and submitted dates equal the account final-bill dates.
- **Coverage order.** Every claim is PRIMARY with one claim per encounter. No secondary claim exists, so releasing PR lines to the patient is correct ("only the patient-responsibility amounts reported by the last payer in the order are released").
- **Claim frequency.** Every claim has frequency code 1 and front-end reject NONE.
- **Payer timeline.** Coverage changes match the PR-27 dates:
  - T0: Anthem paid 2025-01 service, PR-27 on 2025-03-05 service, Marketplace from 2025-07.
  - T1: Network Health paid 2025-01, PR-27 2025-05-14; Quartz paid 2025-06-10 and 2025-10-20, PR-27 2025-10-28; Security Health 2025-11-09.
- **Program claims.** There is no Medicare or BadgerCare claim in either task.
- **PR-27 routing.** Each PR-27 was transferred to the patient on the denial date, inside the 10-day denial work period, and the claim was closed with balance 0 ("The claim closes once no route remains").

## 2. MISS list

None. No row in either task contradicts a quoted published claim rule.

## 3. Doubtful (not a miss)

1. **Appealed claims with payer_balance 0.00 (T0 C3, T1 C2).**
   - Rule: "A claim closes as soon as its payer balance reaches zero." (contract_modeling_and_underpayment_thresholds; also remittance_posting_and_underpayment_modeling: "The claim closes when its payer balance reaches zero.")
   - Both claims reached 0 at remittance yet show status `appealed`, not `closed`. The docs never say whether filing an underpayment appeal reopens a closed claim or keeps it in an appealed status, so this is not a clear contradiction.
   - Assistance impact if it were wrong: the most recent appeal's type (UNDERPAYMENT_APPEAL) and its claim's `appealed` status are read by the assistance computations, so it could matter.
2. **Appeal-window evidence for underpayment appeals (T0 C3, T1 C2).**
   - The window gate is counted from "the denial date on the claim". Both claims have an empty denial_date because they were paid, not denied.
   - Counting from the adjudication (remittance) date, both are within the window (8 of 180 days; 78 of 90 days). No reading makes them late.
3. **HMO cost-share form (T1 C0 Network Health, T1 C2 Quartz).**
   - contract_modeling_and_underpayment_thresholds says the Commercial HMO class expresses cost sharing as "copay primarily".
   - Both claims post only PR-1 deductible + PR-2 coinsurance and no copay. T1 C3 (Quartz) has a copay.
   - "Primarily" does not forbid deductible or coinsurance, so this is not a miss. It does touch deductible/coinsurance liabilities that assistance reads.
4. **Marketplace deductible accumulation (T0 C3 then C4, same member CGH44918236, same 2025 plan year).**
   - C3 took PR-1 3000.00 out of an allowed 4424.00, so the remaining deductible was met by that remittance. C4, adjudicated after it, takes another PR-1 1500.00.
   - Coinsurance is also 40% on C3 but 20% on C4.
   - The docs publish no deductible, coinsurance rate or accumulator, so nothing published is contradicted. The point bears on deductible/coinsurance liabilities that assistance reads.
5. **Prior authorization / admission notification.**
   - prior_authorization_and_admission_notification_schedule lists these patient classes as needing prior authorization:
     - PPO: outpatient surgery, T0 C0
     - Marketplace: outpatient diagnostic, T0 C4 and T0 C6
     - HMO: outpatient surgery, T1 C2
     - HMO: outpatient diagnostic, T1 C3
   - Every claim's prior_auth_number is empty, yet the payer paid (or accepted) with no CO-197.
   - Also, T0 C1 is an emergency inpatient admission on PPO (2-business-day notification) with no notification reference. Emergency is exempt from prior authorization, but not from notification.
   - The docs govern routing once a CO-197 arrives. They do not say a payer must deny, or that the reference field must be filled. The empty field appears on every claim, which suggests it is simply unpopulated.
   - Assistance impact only if these claims "should" have been CO-197 denials, which the docs do not entail.
6. **Line-level contract methods.**
   - Methods such as the HMO operating-room per-procedure fee or the anesthesia 720/unit HMO rate (operating_room_surgical_pricing_method, anesthesia_unit_rate_outpatient_surgery, etc.) are written for valuing refunds and close-outs ("valued for an Insurance Claim" inside the refund/close-out computations).
   - They are not stated as the payer's remittance amount. The only published payment model is the class-percentage expected allowed, and every claim matches it exactly except T0 C3 and T1 C2 (both appealed as underpaid) and T1 C0 (overpaid vs model). So payments were not tested against the line methods.
