# rework_claims_r8 — cpi_insurance_verification_and_force_placement (audit revision_6: R6-A, R6-B, R6-C; coordinator route)

- R6-A (record-only re-review on an open force-placed record contradicts the base lifecycle): the feed, upload and fax re-review rules and their overwrites now govern closed tracking records only. On a record that is not closed, each rule's outcome is not_applicable; this is stated in the rule and enforced in compute. The base review, the policy-on-file update, the return to compliant and the cancellation of placed coverage all stay in force there, as the "outside this rule" sentence restates. The status-return retirement added in round 7 is withdrawn.
  - The reach-date ladder is re-keyed on closed-record cases: contract paid off → first-review date; contract not paid off but repossessed → repossession date; otherwise → re-review date (standard). Every tier was probed on closed records.
  - Agent-call proofs and uploads longer than binder_max_days are not re-reviewed on closed records. The rule states the reason for agent calls: a call leaves no document to review again.
- R6-B (hand-off not conditioned on the receiving rule's test): both refund rules now carry one shared hand-off sentence, which replaces both retired base clauses:
  - the latest charge of a record closed while force_placed by payoff goes to the closing-month rule (period ends on the closed date) or the closing-period rule (period runs past it) only when an accepted proof counts for its period;
  - that charge in any other case, and every other charge, keep the base refund rule, with the closure basis restated as in force.
  - Both scopes use the same record test.
- R6-C (refund depended on the arrival channel): each refund reads, for every arrival channel alike (feed, fax, agent call, upload), the accepted proof with the latest effective date. Covered days are the union of all reaching spans, and replacement days are the uncovered days between the first and last reaching span. The channel decides only which re-review rule reviewed a proof. A later accepted proof from one channel supersedes an earlier one from the same channel; this is stated.
  - Probed: the task proofs arriving by another channel give the task figures unchanged.
- Class sweeps:
  - Re-review effects on open records: none remain.
  - Every retired base clause has its receiving rule covering exactly its scope, and the remaining cases are restated.
  - Refund outcomes no longer depend on the channel.
  - Residual, stated in the rules: which re-review rule applies, and which rejected proofs a refund waits on, follow the channel by design of the problem tree. Agent-call proofs and long uploads are not re-reviewable on closed records.
- Factor draws unchanged: feed 6, upload 4, closing-month refund 4, fax 6, closing-period refund 4. Every factor still moves the result on its own in both worlds, and no scored figure moved (plan.md "Round 8 probe table"). Gates 7/7.
