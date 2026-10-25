# plan — account_credit_and_recovery (env_0076, M=2)

Scratch: /tmp/account_credit_and_recovery_0076/ . Write domain: this dir only.

## Draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=3, factor_counts=[4,6,5,5]
- task 1: prerequisite_problems=3, factor_counts=[5,4,5,6]

## Structural findings (account charter vs skill)
- Only ledger writes carry numbers. Claimed numeric events: deposit, apply, withdraw, refund, goodwill, balance_sync.
  apply / refund are mirror postings of product lines (amount fixed by the product line, "unchanged by any tier
  figure") -> no factors possible. unlock / tier_change / security_update / close / reopen carry no number.
- So every problem is a deposit, a withdrawal or a goodwill grant.
- Owner=user per task: a deposit (the customer's own card/PayPal/bank payment) and a withdrawal (the customer's own
  instruction to send their money back). Blueprint summary says the agent books both; lifecycle fixes no owner for
  ledger events -> permission doctrine (customer disposing of own funds) decides. Recorded as a deliberate choice.
- Owed (state_due) numeric problems that can sit in front of a deposit/withdrawal: goodwill for documented
  Harborline service failures (Harborline's published service-failure goodwill schedule) -> prerequisites.
- Value edges: goodwill -> deposit top-up (balance), goodwill -> withdrawal (base netting measure: unspent non-cash =
  refund+service+goodwill - purchases floored at 0; with purchases above non-cash, each posted goodwill raises the
  remaining deposited credit).

## Design (draft, refine per task)
Task 0 root: top-up deposit to fund the coming year's auto-renewals from credit (user, 6 factors).
  prereqs: goodwill for a hosting plan provisioned after its deadline (5), goodwill for a duplicate domain charge (5),
  goodwill for a recovery request decided after its review deadline (4).
Task 1 root: withdrawal of one deposit back to its payment method (user, 6 factors).
  prereqs: goodwill for OV/EV certificate issued after the issuance target (5), + two more (4,5).

## Status
- [ ] task 0 policies / tools / seed / persona / GT / gates
- [ ] task 1
- [ ] final gates + XF sweep + worklog tables

## FROZEN DESIGN (after structural analysis; do not re-deliberate)
Every problem is a ledger write. Roots are the customer's own money moves (owner=user); prerequisites are
Harborline's published service-failure goodwill credits (state_due), one policy per documented failure kind.
- T0 (frozen 2026-10-22 10:15:00 CDT), draws [4,6,5,5]
  root  account_ext_deposit_return       WD of the most recent deposit (user)          4 factors
  pre   account_ext_provisioning_goodwill hosting plan activated late (cross hosting)   6 factors
  pre   account_ext_recovery_review_goodwill recovery request decided late (account)   5 factors
  pre   account_ext_refund_posting_goodwill  product refund posted late (cross domain)  5 factors
  edges: root <- each goodwill, value_input on the remaining deposited credit (base netting measure:
  purchases exceed non-cash credit, so each posted goodwill raises the remaining deposited credit 1:1).
  WD factors: post-recovery share (param, multi-source), charge-back holdback (param, multi-source),
  hosting auto-renew holdback (method, cross hosting), domain auto-renew holdback (method, cross domain).
- T1 draws [5,4,5,6]
  root  top-up deposit (user, DEP reserve / shortfall)                                4 factors
  pre   ssl issuance late (6), duplicate domain charge (5), recovery reset applied late (5)
- Goodwill caps (per case / 12-month) never bind jointly -> goodwill writes commute (prove both orders).

## Progress
- T0 DONE on disk (account.extended.yaml 4 policies, task_tools.py 4 tools, tasks/0.json). Per-task gates all OK;
  traceability pre-docs: only the 4 unlock tool names missing (expected). Scratch generators in
  /tmp/account_credit_and_recovery_0076/ (t0_world.py, p_t0_*.yaml, t0_texts_[abcd].py, t0_task.py, calc.py, sweep.py).
  Values: provisioning 27.10, review 35.00, duplicate 32.64, return 53.68.
- T1 next: root top-up deposit (user) 4 factors; ssl issuance late 6; recovery reset late 5; refund posting late 5.
- T1 DONE (tasks/1.json; 4 more policies/tools). Values: certificate 23.24, reset 22.40, refund posting 19.00, top-up 72.32.
- FINAL gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK; TRACEABILITY NOT OK only for the 8 unlock tool names (expected before KB rendering).

## Rework round 2 (supersedes the FROZEN DESIGN above)
- T0 root is now account_ext_renewal_prefund (holder's prefund deposit, make_prefund_deposit_8453f2b2); the withdrawal policy and
  return_deposit_credit tool are gone (audit C1). T1 root re-priced (published renewal prices, reseller bands, competing draws).
- Goodwill schedules re-scoped and re-tiered; see worklog.md "REWORK round 2 claims".
