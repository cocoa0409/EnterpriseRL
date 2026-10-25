# plan — worker_payroll_card_servicing (category card), M=2 — rework round 2

Draws (draw_counts.py --tasks 2, unchanged):
- task 0: prerequisite_problems=2, factor_counts [6,4,6]
- task 1: prerequisite_problems=2, factor_counts [4,4,5]

Round-2 redesign (audit revision_1 RED on every factor class; trees passed):
- Struck ladder classes removed everywhere (day fees, lesser-of surcharge basis, fee-kind sums, retry, early-pay
  cost, carried remainder, Access hold-backs, card-in-hand straw liability).
- Each task is one lost/stolen-card file with two losses on the same account; the three problems are the Reg E
  credits of that file: final credit on the earlier loss's claim (agent), reversal of the excess provisional
  credit on the later loss's report-day claim (agent), provisional credit on a later-found claim of the later
  loss that the cardholder signs (user, root).
- Tree per task: signed claim credit <-(state gate: reversal on the other claim of the same loss)- reversal
  <-(value input: available balance; final credits owed on other lost/stolen claims post first)- final credit.
- Plan families (account-level, disjoint): task 0 = Premier and Elite plans, task 1 = Advantage plan.
- Factor dimensions (real Reg E / Visa / payroll-card dims; Paystride schedule where not regulatory):
  liability limit (Visa Zero Liability purchase / timely report / late report; multi-source), liability already
  charged on the same loss (posting order), Paystride fees on the claimed transaction or the free withdrawal it
  used (method), provisional-credit / final-credit lateness allowance, investigation-length allowance (10/20 BD,
  45/90 days for new-account, POS and foreign-initiated), replacement card fees on a lost or stolen card
  (Premier/Elite), early pay the worker had to send to an outside destination on the report day while the
  card was blocked (cross-difficulty: Access ledger + Access tier fee; method).
- Counts: task 0 final credit 6, reversal 6, signed claim 4; task 1 final credit 5, reversal 4, signed claim 4.
- Business days computed exactly in the DSL (weekday ordinal less Federal Reserve holidays 2025-2027).

Scratch: /tmp/worker_payroll_card_servicing_0077/r2/ (authoring scripts live there only).
