# plan — cancellation_reinstatement_and_exclusions (category auto), M=2

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems 2, factor_counts [4, 5, 6]
- task 1: prerequisite_problems 2, factor_counts [5, 6, 6]

## Constraint analysis (why these trees)
Every problem needs a 4-6 factor computation and every tree needs one owner=user problem.
Money quantities this category can compute: nonpayment-cancellation return premium (NC),
lapse-reinstatement re-written premium (RE), insured-request cancellation return (IC),
named-driver-exclusion return (EX), driver-add additional premium (ADD / exclusion lift).
The Statement of No Loss, the Named Driver Exclusion form and the cancellation-request record
carry no computable quantity (only dates fixed by the records or chosen by the insured), so
they are never problems here; when needed they are seeded as signed and on file.
The insured's signed cancellation request taking effect is a by:user lifecycle transition
(in_force -> cancelled) -> IC is the owner=user problem of one tree.

## Task 0 — root IC (user) <- RE (agent) <- NC (agent)
Customer cancels effective today (moving out of the company's states). Opening world: term still
pending_cancellation with its notice effective date passed (cancellation not yet processed), the
past-due paid after that date and a Statement of No Loss signed two days ago.
- NC (4 factors): process the nonpayment cancellation, book the pro rata return premium.
- RE (5 factors): reinstate with lapse; re-written premium = cancellation return x days / its
  premium_days (value_input from NC's return row).
- IC (6 factors, user): insured-request cancellation of the in_force term (state_gate from RE).

## Task 1 — root exclusion lift / driver schedule (user) — designed after task 0 closes
Headroom left: EX (exclusion endorsement on a signed form on file) + a driver-add problem keyed on
a record (claim on the term naming the driver). Root user problem: lifting a named driver
exclusion at the named insured's signed request (additional premium). To be fixed at task 1 Step 0.

## Order of work
1. extended yaml: base copy + NC, RE, IC policies (task 0) ; tools ; seed ; persona ; gold ; gates.
2. task 1 likewise.
Scratch: /tmp/cancellation_reinstatement_and_exclusions_0071/

## Task 1 (fixed at task-1 Step 0)
Root: lifting a named driver exclusion at the named insured's signed request (owner=user, 6 factors), keyed on the
claim of the term reported with the excluded driver operating. Prerequisites (both value_input through the
schedule-change load): endorsing the exclusion on the signed Named Driver Exclusion form on file (agent, 5 factors)
and re-listing the household resident reported operating while unlisted on a claim, back-charged from the date of
loss (agent, 6 factors). Rejected: a brand-new undisclosed driver (no pre-action points record for the driver_points
gate); re-rating the lift on the current full-term rate (not how driver rating works).

## REWORK round 2 — plan (audit CG-01..CG-17, task findings 0.1-0.7, 1.1-1.6, XF 1-22)
Constraint found: in this charter the three term-level money computations (nonpayment return, lapse re-write,
insured-request return) admit only a few dimensions a real carrier uses; the driver-schedule computations
(rating of a driver share) admit many. Plan:
- Task 1 tree rebuilt as a natural value chain: lift (user root) <- exclusion endorsement (state gate: every signed
  form endorsed) <- relisting of the resident found operating unlisted (value: the exclusion returns the share the
  relisting charged). Brianna is relisted from her claim report date (after the loss -> physdam standing test
  still reads her unlisted at the loss, CG-07) and excluded on the form she signed; Marcus is lifted.
  Rating factors (driver class by age x relationship = multi-source, violation-points tier, chargeable at-fault
  claims as operator, package base share, effective-date methods) replace every struck load.
- Task 0 tree kept (nc -> rw -> ic); struck factors removed; replacements only from real dimensions
  (certificate status/run-off, lapse type / postmark rule, re-write rate basis, short-rate vs pro rata vs fully
  earned by request reason and total loss, transaction-proration daily basis); stamp handled honestly (CG-14).
- Wording sweep: ties (CG-09), inclusive/exclusive and month-end (CG-15), assembly (CG-17), replaced_by
  content (CG-08), lag sentence (CG-05), rule==compute (CG-12), edge strength (CG-13), deadlock (CG-16).
