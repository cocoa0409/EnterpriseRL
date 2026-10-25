# plan — bed_hold_and_leave_reservations (env_0074), M=2

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=2 (3 problems), factor_counts [6,4,5]
- task 1: prerequisite_problems=1 (2 problems), factor_counts [5,6]

Constraint found at step 0: the only user-owned bedhold writes in the blueprint (elections: hold / decline /
private_extension / release) carry no numeric field (bedhold_elections has only enum+date fields), and every
problem needs a 4-6 factor numeric computation. Route-around (declared in worklog): the customer's own numeric
write is the representative's written acknowledgement / payment-side act — decided in worklog Step 0.

Files (write order, persist each immediately):
1. worklog.md (running), plan.md (this)
2. bedhold.extended.yaml — base copied verbatim by script, extended_policies appended per task
3. task_tools.py — tools appended per task, gate check_task_tools after each
4. tasks/0.json built by /tmp/bedhold_0074/build0.py (piecewise), gates --task 0
5. tasks/1.json likewise, gates --task 1, then full-suite gates
6. final line in worklog: ROUND 1: gates n/n green; remove /tmp/bedhold_0074 scripts
Identifier band: phones 717-555-0400..0499, ssn_last4 4000-4999, surnames N/O/P/Q/R, rooms 400-499.
