# plan — worker_early_wage_access (category access), M=2

Draws (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=2, factor_counts=[4,6,4]
- task 1: prerequisite_problems=1, factor_counts=[5,5]

## DSL constraint found at Step 0 (decision record)
Compute runs on the access plan (CUST = the worker). CFIELD/CPARAM/EXISTS/X* force customer_id=CUST,
so the employer's program agreement (configured_cap_percent, fee_model, program tier) is UNREADABLE by
compute. Routes chosen:
- transfer amount: extended transfer policies are scoped (self-naming overwrite) to a plan whose employer
  agreement's configured access percentage is not below the plan tier's access percentage; out of scope the
  base availability sentence stays in force verbatim. The agent checks the scope on the agreement record.
- fee: the employer fee model and the tier free-instant allowance only decide WHETHER a fee is owed (zero or
  pass-through); the extended fee policy prices an owed fee. World seeded worker_paid; position past allowance.
- cross-difficulty factor reads the worker's own card account / card_transactions (card = claimed difficulty).
- access_transfer writes only external_debit_card / bank_account (card:card_load trigger never fires).

## Trees (tentative)
- task 0: root = instant transfer fee (agent, 4 factors) <- instant external-debit transfer (owner=user, 6) <-
  write-off of an uncarried shortfall past its wait (agent, 4). Plan on a no-tolerance tier: the open shortfall
  withholds access until written off.
- task 1: root = next-business-day bank transfer (owner=user, 5) <- payday level review owed for the payday just
  passed (agent, 5); review upgrade changes the tier parameters the transfer reads.

## Files
- access.extended.yaml (base verbatim + extended_policies), task_tools.py, tasks/0.json, tasks/1.json
- scratch: /tmp/worker_early_wage_access_0077/ (builder scripts, probes)

## Progress (instantiator, round 1)
- Final tree choice (supersedes the tentative one): task 0 = bank transfer fee (root, 4) <- next-business-day bank transfer (owner=user, 6) <- payday tier review (4); task 1 = instant transfer fee (root, 5) <- instant external-debit transfer (owner=user, 5).
- Reason: write-offs, shortfalls and voluntary payments are fixed by the ledger (no factor can move them honestly); the review, the two transfer amounts and the two fees are the five computations with real levers.
- access.extended.yaml + task_tools.py written; task 0 written and green on all per-task gates (traceability: only the expected unlock tool-name misses before docs).
- Builders: /tmp/worker_early_wage_access_0077/{pol/*.py, t0_*.py, t1_*.py, eng.py}.
- Task 1 written; final suite green (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; CACHE-DIFF INFO); traceability pre-docs: only the 5 unlock tool-name misses.

## Rework round 2 (policy audit r1)
- Trees now: task 0 = bank transfer fee (root, 4) <- bank transfer (owner=user, 6) <- tier review of a payday without a shortfall (4); task 1 = instant transfer (root, owner=user, 5) <- missed-recovery review of a payday with a shortfall (5). The instant-fee policy and its tool are withdrawn; task 1's employer pays fees (employer_paid).
- See worklog.md "REWORK round 2 claims".
