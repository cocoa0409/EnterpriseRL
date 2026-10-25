# Rework round 14: claims per revision_3 cross-product re-judge (seed only: S-2)

- auto.extended.yaml sha256 prefix **657983bf**: unchanged (byte-identical).
- task_tools.py sha256 prefix **5a982b7f**: unchanged (byte-identical).
- No gold value moved.

## S-2 (task 0, auto x billing): the seeded plan balance would be written off at the nonpayment cancellation

**Closed.** Only task 0's billing seed changed: initial_state and db_closure.

**Seed change**
- The 2026-09-21 partial payment is now recorded as taken by a live representative by phone.
- A matching billing_agent_payment_fee row (uuid4, 5.00, 2026-09-21) references that payment. This is priced by the published billing docs: payment_posting_rule and plan_fee_schedule (Six-Pay agent-assisted fee).
- The plan's account_balance is re-summed from the ledger.

**What stays the same**
- Agent-assisted fees are neither past-due amounts nor late or NSF fees (delinquency_status_rule; the payment application order).
- So these are unchanged: invoice 5's past-due amount and minimum due, the plan's current status, the payments posted by the cancellation effective date, the latest payment date, and every auto reading.

**Why the premise now holds**
- After the nonpayment return is credited, the remaining debit is above the small-balance write-off limit (cancellation_settlement_rule; closing_refund_and_collection_terms).
- The plan is therefore final-billed rather than closed, and the reinstatement reactivates it (reactivation_after_reinstatement). The insured-request plan charge's premise, a plan closed again, now holds.

**Proof text swept:** seed_consistency[8] (with the new evidence row), evaluation_criteria[6] objective, and the design_rationale note.

## Checks

- Gate block 7/7 green.
- Replay closure matches the initial state.
