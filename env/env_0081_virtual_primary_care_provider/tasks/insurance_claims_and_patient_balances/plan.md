# plan — insurance_claims_and_patient_balances (env_0081), M=2

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=2, factor_counts=[5,5,4]
- task 1: prerequisite_problems=1, factor_counts=[5,6]

Owner=user write: only (c) of owner_ruling.md is inside this difficulty's claimed events
(claim_patient_payment_posted): the patient reads out a card that is not on file (stored card expired /
HSA card not on file) after the agent quotes the amount. Payment-plan / hardship / appeal requests have no
claimed event type here.

Tree drafts (realism: trees on writes priced from raw records where the charter has them):
- task 0 (3 problems): root = patient pays the open balance of a visit whose claim was denied
  eligibility_terminated (user). Prereqs: price-path self-pay rebill posting (agent, value_input) and the
  booking-collection application (agent, value_input). Parallel prerequisites, commuting entries.
- task 1 (2 problems): root = patient pays the insured patient-responsibility balance of an adjudicated
  visit (user). Prereq: credit sitting on an older claim moved onto it first (agent, value_input).

Cross-difficulty evidence: visit (visit_appointments / visit_charges of the billed visit), membership
(membership_holdings / membership_charges on the service and booking dates).

Process: per task — Step 0 cards in worklog -> policies into claim.extended.yaml one at a time ->
tools into task_tools.py (check_task_tools) -> seed initial_state piecewise -> verification script in
/tmp/insurance_claims_and_patient_balances_0081/ -> computations/GT -> per-task gates -> worklog.
Traceability once before docs. Final 7 gates -> tail line.

Known risk recorded up front: the claim charter's numeric writes are mechanical (balance entries); the
drawn 4–6 factors per computation exceed the charter's genuine multi-tier rules. Factors are taken first
from charter rules (visit/membership price-path rules, denial handling, COB, measures), then from
Larkspur published schedules of R1/R2 shape overriding a named base sentence; each such factor is tagged
THIN in the worklog for the coordinator.
