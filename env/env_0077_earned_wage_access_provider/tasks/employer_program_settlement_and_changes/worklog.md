# worklog employer_program_settlement_and_changes

## REWORK round 2 claims
- C-01: termination fee policy declares the program_paycard_bundle overwrite (sibling tail names the per-worker fee, the early termination fee and the latest-month SLA base, and restates the base sentence for every other case); Instant Pay suite tier removed; bundle tier now by paycard package.
- C-02: SLA policy overwrites the bundle sentence as the same sibling, so its covered lines and other-program fees no longer contradict an in-force sentence; the per-worker policy's tail rewritten to the shared sibling form.
- C-03: both late-charge replaced_by sentences restate base pricing for every overdue item except the one each selects; the two prerequisite sentences now wait on exactly the item their resolver prices (latest return's schedule, latest employer-liable notice).
- C-04: return late charge in scope only when its return is the only return booked that day (probe: a second same-day return on the same schedule puts it out of scope).
- C-05: per-worker credit inherits the unpaid cap and one billing-error memo per line (probes: partly paid line capped; line with a memo gets none).
- C-06: every assembly sentence rewritten generically (adjustment kinds, no factor quantities); orders unchanged.
- F-P2: product_footprint and enrolled_reach removed; affected_services (other Paystride programs' monthly fees on the platform) and consecutive_breach added; hypercare replaced by stabilization_window (credits reduced after go-live).
- F-P3: relationship, degressive bands and cure relief removed; shortfall late charge now culpability method, repeat liable shortfalls, days past due, overdue balance, whole remittance exposure, prior late charges.
- F-P4: relationship, channel, degressive bands and re-send relief removed; return late charge now returned-payments method (remittance plus Payroll Card funding returns), days past due, overdue balance, exposure, prior late charges, liable-shortfall history.
- F-P5: remittance_standing removed; the root's edge to the return late charge is now a state_gate (notice accepted only once that late charge stands).
- T1-D6: stale "billing holds late charges" claim removed; the seeded July late charge is now real and priced by the shortfall rule; all proof/rationale/necessity text and equations swept.
- O-1: month_start has a compute_basis entry. O-3: closed by the stabilization reduction.
- World/propagation: Payroll Card funding ledgers seeded (now read) in both tasks; historical SLA credits and the July late charge re-priced by the round-2 rules; evaluation steps renumbered for the added funding-ledger read; persona conditional lines no longer name the prerequisite's kind.
REWORK round 2: gates 7/7 green

## REWORK round 3 claims
- C-03 (residual): both state-form waits now carry their resolver's whole scope test (single item of its day; return schedule without a liable notice; liable notice alone on its schedule whose schedule has no return), so the waited-on record is exactly the record the resolver writes in every engaged world; a schedule carrying both a return and a liable notice engages no wait.
- E3 tests, edge termination fee -> return late charge: engaged and unmet at the opening (the only return of its day names a reinstated schedule past grace, open, with no late charge); satisfiable by its resolver in every engaged world (the return policy prices exactly that schedule; nothing owed waits on nothing).
- E3 tests, edge return late charge -> shortfall late charge: engaged and unmet at the opening (the only liable notice of its day, alone on its schedule, past grace, open, no late charge); satisfiable by its resolver in every engaged world (the shortfall policy prices exactly that notice).
- N-A1: method factors decide only a charge rule from their own records; rate, percentage charge and charge are plain bindings; no factor reads another factor's output.
- N-B1: every "most recently" selector (prerequisite sentences and the new cross-item reads) applies only when exactly one such item was booked on that day, stated as a plain record test; out of scope the policy books nothing and the base pricing restated in replaced_by applies.
- N-B6: the termination bundle sentence drops the "bundle the employer is billed under" framing.
- N-F1: affected_services removed; downtime_depth (a finer uptime step on the depth of the shortfall below the commitment) added; the Payroll Card ledger read and rows dropped from task 0.
- N-F2: both whole-receivable exposure factors removed; replaced by a concurrent-delinquency factor reading only the other overdue item's past-due open amount.
- T0-D6 / T1-D6b: both persona lines rewritten in the bytes of user_scenario (verified), rationale claims now quote the actual lines.
- O-7: the root's wait is phrased on billing the fee and recording the notice. O-10: Payroll Card reserve cushion raised so the balance holds the reserve after every batch.
- Propagation: history re-priced (task 0 SLA credits and payments; task 1 July late charge and SLA credits), evaluation steps renumbered in task 0, all proof/rationale/necessity text swept.
REWORK round 3: gates 7/7 green

## REWORK round 4 claims
- S-1: termination-fee rule and replaced_by now state that a fee that comes to zero is recorded with the notice and no early_termination_fee line is billed; the sign_termination_notice_c67c1163 body books no fee line when the fee is 0.00 (no floor added). Docstring changed: capability text and Returns now describe the zero-fee case and its receipt line; tool name and signature unchanged.
- S-2: the SLA credit rule settles a claimed month whose invoice carries no platform_fee line (zero-platform-fee tiers): no service level credit is given under these provisions, by a record test on the month's platform_fee lines.
- S-3: every whole-month count and whole-month look-back window in all five policies now states its month-end convention (a month becomes whole on the same day of the month, or on the first day of the next month where that month has no such day), matching the compute.
- No regression: gold writes, scored values and task worlds unchanged; rationales carry a round-4 note.
REWORK round 4: gates 7/7 green

## REWORK round 5 claims
- R4-E4: the shortfall late-charge rule now states a de minimis record test — a late charge is booked on a shortfall notice only where the notice has an open amount of at least the de minimis amount (deminimis_open_usd); a smaller notice carries no late charge and no line is booked (compute: result only when open_amt reaches the threshold). The threshold makes every in-scope notice price at least 0.01 under every rate tier (lowest tier rate plus non-negative points). The returned-remittance late charge's prerequisite sentence and condition carry the same test verbatim ("has an open amount of at least the de minimis amount"), so the wait never engages on such a notice.
- Zero-amount class sweep, every member and its carve-out:
  - per-worker billing-error credit: "no credit is booked when that amount is not above zero" plus one memo per line; the SLA wait carves out "or no amount was billed above that fee".
  - SLA credit: no credit when availability is not below target, when the month has no platform_fee line, and (added) when that line carries billing-error credits equal to its whole amount (record test); a billed platform line is credited only in full, so any remaining base prices above zero; nothing waits on this policy.
  - shortfall late charge: percentage-only tier covered by the de minimis record test above; other tiers include the minimum.
  - returned-remittance late charge: every tier includes the minimum, so it is never 0.00 in scope; its own wait on the shortfall charge carries the de minimis test.
  - termination fee: a fee of zero records the notice and books no line (round 4); its wait on the returned-remittance charge engages only on a schedule that is open and past grace, whose charge is never 0.00.
- No regression: task worlds, gold writes and all scored values unchanged; S-1..S-3 fixes kept; rationales carry a round-5 note and quote the new sentence.
REWORK round 5: gates 7/7 green

## REWORK round 6 claims
- S-4: task 1's 2026-08-21 regular batch (funds arrived with the 2026-08-24 wire, after the Advantage deadline) now carries its late_funding fee debit pointing to the batch, priced at the Advantage late funding fee; the Payroll Card funding balance follows and still holds the reserve after every batch.
- S-5: task 1's June and August 2025 monthly_program and active_card fee debits re-dated to the 5th business day of the following month (Independence Day and Labor Day 2025 skipped).
- S-6: task 1's August 2025 program invoice lines re-dated to the 3rd business day of September 2025 (Labor Day skipped); their due dates and payment dates follow.
- Root cause and exhaustive pass: the scratch Federal Reserve calendar lacked 2025 holidays; completed, then every business-day-dated row family of both worlds re-derived and checked by script — deduction schedule delivery and due dates, ACH remittances on due dates, shortfall notice dates and cure due dates, remittance return dates, invoice issue and due dates, late-charge and return-fee due dates, Payroll Card ACH receipts, batch posting days, monthly and active-card fee debits (task 0: invoice lines and due dates). No other row moved.
- No scored value moved; program.extended.yaml and task_tools.py byte-identical (8edfe41cb636a001 / 0afad5185ffe98ca); task 1 rationale updated where it cites the ledger row count and carries a round-6 note.
REWORK round 6: gates 7/7 green
