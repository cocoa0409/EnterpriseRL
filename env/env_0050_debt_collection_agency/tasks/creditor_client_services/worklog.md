# creditor_client_services — worklog

## Rework round 2 (audit: audits/policy_task/creditor_client_services/, revision r1)

The blueprint is unchanged. Every change is in `client.extended.yaml`, `task_tools.py` or `tasks/{0,1}.json`. Scratch work was done in `/tmp/env0050_rework_client/`.

### Charter-level items (_difficulty.md findings)

- **D1 (two payment policies overlap)**: the closing rule now states precedence: "Where a termination notice is on record, a payment of the fees owed on that agreement is a closing settlement payment even when the client names one of its invoices." The payoff rule's scope is now "on an agreement with no termination notice on record".
- **D2 (XCOUNT and CFIELD not scoped)**:
  - ETC: added `legal_agreement_ref` and `precollect_program_ref` (CFIELD filtered by agreement). Suits and conversions are counted only under that legal agreement or program.
  - Payoff: added `payoff_legal_ref`; suits are counted under that legal agreement.
  - Late charge: the flatfee `CFIELD`/`CPARAM` calls now filter by `agreement_id=HID`.
  - Factor bindings, compute_basis and the cross-difficulty bindings were updated to match.
- **D3 (renewal promise had no compute)**: added a rule and baseline sentence: "The agreement has renewed when its term end date lies the tier's initial_term_months or more whole months after its effective date, and a termination of a renewed agreement takes effect after the initial term and carries no charge." It is implemented as the binding `renewed`, and `result` is now 0 when `renewed` is true.
- **D4 (net_remit deviation not declared)**: the closing policy's `overwrite` now declares it against `client_evt_remittance` ("For a net_remit agreement the period's fees are first retained from trust and the rest is remitted" → "on a net_remit agreement, the available trust balance is set against the whole of the fees owed").
- **D5 ("full calendar month" ambiguous)**: the late-charge and payoff rules now define it: "A full calendar month after a late-charge start runs from that day to the same day of the next month, or to that month's last day where the same day does not exist."
- **D6 (invoice locator differs from the rule's object)**: no structural change. The DSL cannot receive the invoice the client names, so the locator (the invoice of the latest late charge) stays. It coincides with the target at both handling times in task 1, and D1 narrows the payoff scope. This is recorded in the task 1 rationale as an accepted limitation.
- **D7 (legal and flatfee belong to no difficulty)**: no change is possible. A creditor-client customer can only hold legal and flatfee products besides its contingency agreement, because the consumer products are scoped to consumers. Recorded.
- **D8 (rounding: docstrings said half-up)**:
  - The tool docstrings now say "rounded to the nearest cent (2 decimal places)" instead of "half-up".
  - Task 1's world was adjusted (see 1-O3) so that no gold or declared figure sits on a half-cent tie.
- **All rules**: added the window convention "A window of a number of months before a date covers the dates after the same day that number of months earlier, up to and including that date." It matches the DSL.

### Task 0 (0.md)

- **0-F1 (SOURCE-FACTOR RED)**:
  - The flatfee conversion for CHH-5120561 was re-dated from 2026-09-02 to 2026-09-14. That is after its 75-day series (submitted 2026-06-23, last letter by 2026-09-08) and inside the 45-day conversion window.
  - The single 547.50 legal reimbursement was replaced by two one-cost client reimbursements on KLG-5260522-04 (395.00 filing, 85.00 service).
  - The second matter was re-dated to KLG-5260710-05: authorized 2026-07-10, filed 2026-08-27, costs 2026-08-27 and 2026-09-03. Its 2026-08-19 collection now comes before its costs, so the costs_first recovery order is not engaged.
  - cost_advance_balance is now 480.00. The ETC stays 206.66. The closing payment changes from 356.24 to 423.74, with baseline 797.45 and the skipped-prerequisite figure 237.75. This was propagated everywhere.
- **0-O1 (seeded late charge used the base formula)**: re-figured under the extended rule at its own date: 5.00 → 3.04. fees_receivable 592.75 → 590.79. The scored payment is unaffected because the waiver moves with the charge.
- **0-O2 (day-count and window readings)**: both readings are now pinned in the rule text. The ETC day-count sentence says the first date is not counted and the last is. The window sentence is above.
- **0-O3 (open-invoice cap does not bind)**: kept. Making the cap bind would make both reserves decorative. The method still bears weight against its fall-through (773.74). Recorded.

### Task 1 (1.md)

- **1-O1 ("full calendar month" reading)**: closed by the D5 definition.
- **1-O2 (no tier-moving near-miss in the late charge)**: documented the tier-moving near-miss in the late-charge computation. Reading the invoice age from the due date (75 days) or from the late-charge start (65 days) instead of the invoice date (105 days) loses the +0.25 step.
- **1-O3 (half-cent ties)**:
  - The part payment changed from 1000.00 to 1010.00 (same tier). The 2026-09-16 late charge was re-figured to 15.19. fees_receivable 3336.15 → 3326.09.
  - New gold: late charge 18.17, payoff 1841.24. New baselines: 27.55 and 1870.06. Skipped-prerequisite figure: 1840.50.
  - No figure sits on a tie. The persona now says "a little over a thousand dollars".

### Gates (after rework)

All per-task gates are green for tasks 0 and 1. The full gate block was re-run at the difficulty level (see the final report).
