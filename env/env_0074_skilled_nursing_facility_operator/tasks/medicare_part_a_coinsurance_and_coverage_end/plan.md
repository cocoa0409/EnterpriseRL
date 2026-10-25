# plan.md — medicare_part_a_coinsurance_and_coverage_end (M=2), env_0074

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=1, factor_counts=[5,5]
- task 1: prerequisite_problems=2, factor_counts=[5,6,4]

Identifier band: phones 717-555-0100..0199; ssn_last4 1000-1999; resident+representative surnames A-D; rooms 100-199.
Scratch: /tmp/medicare_0074/ only.

## Charter facts that constrain the design (read before changing anything)
- Only money writes can carry >=2 `parameter` factors: the only tier-varying VALUES in the charter are the
  daily coinsurance rate by calendar year of service (2026 217.00, 2025 209.50; 2024 204.00 is the real CMS
  figure) and the coinsurance shares by supplemental coverage (resident 100/100/50/25/0/0). Day-count writes
  (booking, reversal) have no parameter ladder -> cannot be a problem.
- Customer-owned writes in this charter: QIO request (no numeric field), SNF ABN (option + date; DSL has no
  date arithmetic), coinsurance payment (numeric). Only the payment can carry a computed number -> the user
  write in each task is a resident coinsurance payment taken during the call (card in one task, bank draft
  in the other: two tools split by payment rail, the card single-payment maximum applying to one of them).
- No runtime trigger engine: booking a days_21_100 block makes a coinsurance charge OWED (state_due).
- Cross-difficulty evidence that genuinely moves Medicare money: bed-hold leave days (bedhold ledger),
  QMB determination on the County Assistance Office notice (medicaid case decision date).

## Task skeletons (to be refined in worklog)
- task 0: prereq = post the resident coinsurance charge for a booked block (agent) -> root = resident pays
  that charge by card (user, value_input via the posted charge).
- task 1: two agent money problems (correction / carrier share) -> root = resident pays by bank draft (user).

## Order of work
1. extended.yaml base copy + task 0 policies; task_tools.py (task 0 tools); gates check_task_tools.
2. task 0 seed + verification script in /tmp/medicare_0074; task 0 json; per-task gates.
3. task 1 same.
4. final gates; worklog `ROUND 1: gates n/n green`; delete scratch scripts.
