# rework_claims_r9 — cpi_insurance_verification_and_force_placement (audit revision_7: R7-A; coordinator route)

- R7-A (only the latest accepted proof per channel is read, so a binder followed by a policy on the same channel loses the binder's days): both refund rules are now scoped, in their scope sentence and in the shared self-naming hand-off, to records on which no arrival channel holds more than one accepted proof. The test is an exact count of the record's accepted cpi_proof_verified entries per verification_source, stated in the rule and computed with COUNT per channel.
  - On any other record, the latest charge stays under the base refund rule. The base clauses are restated in the tail with full_no_lapse / pro_rata_from_proof_effective / pro_rata_from_closure, plus one reading note: the base rule reads the accepted proof with the latest policy_effective_date, whatever its channel. The compute applies that base computation (amount and refund basis) when the record test fails.
  - Within the scope each channel holds at most one accepted proof, so the earlier "later proof supersedes an earlier one" sentence is removed.
- Both worlds sit inside the scope after the re-reviews (checked). Task 0's original 2025 proof is re-seeded as confirmed by the borrower's insurance agent by phone (insurance_agent_call), so the feed channel holds only the re-reviewed policy. Task 1 needed no change. Seed text and traces were swept to match.
- Probes (plan.md "Round 9 probe table"):
  - binder and policy accepted through the same channel → base;
  - one proof per channel → extended, figures as in the tasks;
  - a proof moved to a channel that already holds one → base;
  - a proof moved to an empty channel → extended, unchanged.
- Kept: the R6-A closure (re-reviews on closed records only), the R6-B closure (hand-off conditioned on the receiving rule's own test, now including the per-channel count), channel-blind selection inside the scope, every factor draw, every scored figure, standard result and solo sensitivity. Gates 7/7.
