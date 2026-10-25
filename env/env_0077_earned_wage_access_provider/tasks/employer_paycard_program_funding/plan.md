# plan — employer_paycard_program_funding (category paycard), M=2

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=1, factor_counts=[6, 4]
- task 1: prerequisite_problems=1, factor_counts=[4, 4]

Constraint found while designing: every tree needs one owner=user write carrying its own 4-6 factor
computation. In this charter the employer's own acts are its funding payment (b), a package change (a), a
termination notice (a) and a load-reversal request (b) (owner_ruling). Card balances and card loads belong to
worker customers and are unreadable from the program holding, so the reversal request carries no computable
figure, and a package change carries none either. So task 0 uses the employer's wire, task 1 the signed
termination notice with its early termination fee booked with the notice (declared overwrite).

## task 0 — live program short of its reserve after a short, late-funded batch (root = restoring wire, user)
- paycard_ext_late_funding_fee (agent, 4 factors, prerequisite): lateness method, cards affected, repeat
  lateness, Access bundle (cross program, multi-source) -> debit_program_fee_609ed260.
- paycard_ext_restoring_wire (user, 6 factors, root): returned-funding uplift, program-age basis (method),
  headcount growth, off-cycle allowance, funding-method weight (from receipts), late-history weight
  -> send_restoring_wire_ac37b9e9.
- edge (state form, affirmative): the restoring payment is worked out only after the ledger carries every owed
  late funding fee; value_input on w_late_net (and the balance).

## task 1 — suspended, already-cured program; the employer leaves (root = termination notice, user)
- paycard_ext_reinstatement_fee (agent, 4 factors, prerequisite): cure speed (method), repeat reinstatement,
  Access bundle (cross program, multi-source), cure channel -> reinstate_suspended_program_c7549ab9.
- paycard_ext_early_termination_fee (user, 4 factors, root): term anchor (method), funding standing (reads
  reinstatement fees), Access retention (cross program, multi-source), unissued kit recapture
  -> give_termination_notice_a65df371.
- edge (state form, negated): the notice is not recorded and its fee not fixed until the status is live;
  value_input on e_reinstatements.

Scratch: /tmp/employer_paycard_program_funding_0077/ (seed builders, verification code, probes).
Identifier band: phones 4155550100-199, tax 2xxx, numbers start with 2, surnames E-H, employer first word E-H.

## Status (end of round 1)
- task 0 closed: late funding fee 90.00 (step 6) -> restoring wire 22058.21 (step 8, owner=user); frozen 2026-10-13 09:40:00 EDT.
- task 1 closed: reinstatement fee 48.60 (step 8) -> termination notice with early termination fee 407.50 (step 10, owner=user); frozen 2026-10-20 10:05:00 EDT.
- Final gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK, CACHE-DIFF INFO;
  TRACEABILITY NOT OK only for the four unlock tool names (expected before the KB is rendered).
