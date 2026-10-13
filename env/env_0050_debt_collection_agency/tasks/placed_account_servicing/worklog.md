# placed_account_servicing — instantiation worklog (erl-task-instantiate, M=2)

## Step 0 (difficulty pre-check)
- Draws (draw_counts.py --tasks 2):
  task 0: prerequisite_problems=2, factor_counts=[4,4,4]
  task 1: prerequisite_problems=2, factor_counts=[4,6,4]
- Base charter: account.yaml copied verbatim as the base section of account.extended.yaml.
- Numeric write fields in the account category exist only on account_transactions.amount
  (and placed_accounts.balance_due as the ledger view). Every consumer money event of the
  category (payment_posted, payment_returned, overpayment_refunded, direct_payment_reported)
  carries an unconditional trigger into the client category; the blueprint nevertheless claims
  payment_posted / payment_returned / overpayment_refunded for this difficulty and says "The
  agent posts payments the caller makes ... books returns and refunds". The task tools write only
  account tables (the client-side knock-on rows are not written by any task tool).
- DSL limits noted: history primitives are scoped to one placed account; windows are whole months.

## Design decision log (round 1, resumed)
- Tool suffixes generated one per tool with uuid.uuid4().hex[:8]:
  take_debit_card_payment_cc21c0ad (agent), take_credit_card_payment_bec5ec25 (agent),
  make_portal_bank_payment_436b09cd (user)  -> task 0
  take_phone_bank_payment_d463b192 (agent), make_portal_debit_card_payment_fc4d38a9 (user),
  make_portal_credit_card_payment_7a2662c6 (user) -> task 1
- Numeric scored writes available in this category are payment/refund amounts only. Refund and
  return amounts are fixed by base (excess / original payment) and cannot carry 4-6 load-bearing
  factors without breaking the ledger, so every problem is a payment whose amount is a policy
  ceiling (the consumer asks to pay "the most the account will take").
- Task 0 (draw 2 prereqs, factors 4/4/4): same-day maximum on a bank-card collection.
  chain: phone debit-card ceiling -> phone credit-card ceiling -> portal bank-debit ceiling (root, user).
- Task 1 (draw 2 prereqs, factors 4/6/4): medical account paid down under the credit-reporting floor.
  chain: portal debit-card ceiling (user) -> portal credit-card ceiling (user, 6 factors) -> phone
  bank-debit pay-down to the reporting floor (root, agent).
- Every edge is action form: both the phone desk and the portal post debit-card / credit-card /
  bank-debit payments, so "a payment of that instrument on the handling date" does not single out
  one write.
2026-10-09T04:28:40  NOTE task 0 closed: all per-task gates OK
2026-10-09T04:34:02  NOTE task 1 policies appended (portal debit, portal credit, reporting-floor pay-down)
2026-10-09T04:37:23  NOTE task 1 closed; rationale written
2026-10-09T04:38:22  FINAL gates (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (suite means branches=39.00 steps=13.00, history_rows_max=36, branches_max=39); GROUNDING OK; CACHE-DIFF INFO; SCOPE OK. check_traceability not run (KB not yet published).
2026-10-09T04:38:22  validate_scenario: only errors are the six required documents not yet rendered under env/<scenario>/docs (KB render stage); a temp copy with stub docs for the six policy ids validates VALID.
2026-10-09T04:38:22  Known deviation: payment tools write account_payment_posted rows whose blueprint trigger (client:client_collection_booked) is unconditional; no task tool writes the client ledger.

## Round 2 rework (audit: env/env_0050_debt_collection_agency/audits/policy_task/placed_account_servicing/{_difficulty.md,0.md,1.md})
- F5 (SOURCE-FACTOR RED; 0.md #1, 1.md #1, 1.md #2): the three window factors were parameters under a method label.
  - phone debit: debit_counting_window (look-back by stage) -> debit_exposure_basis (method: all card and bank debits / debit and credit cards / debit cards only, of the last month; decided by a credit-card payment in the last month and a bank debit in the last three months).
  - portal debit: portal_debit_window (look-back by debt type) -> portal_debit_exposure_basis (same channel-set method, its own sentences).
  - pay-down: paydown_provisional_addback now selects the channel set by return reason (unauthorized_debit/stop_payment -> bank and card debits of two months; nsf/account_closed -> bank debits only; none -> nothing).
  - Every computation now has >= 1 honest method factor. Recomputed: task 0 = 1050.00 / 1000.00 / 675.00 (was 1300.00 / 750.00 / 675.00); task 1 = 960.00 / 460.00 / 478.49 (was 860.00 / 560.00 / 438.49).
- F1 (SOURCE-POLICY RED): portal debit assistance ladder now ends in "standard_pct in every other case, including a Financial Assistance Review Hold that has not yet ended"; compute tests the ending date is present (no `or NOW` substitution).
- F2 (SOURCE-POLICY RED): every plan/hold read now quantifies over all of the account's rows: XLATEST over payment_plans.broken_date (phone debit), latest broken_not_reinstated closing via XLATEST with close_reason (phone credit), XCOUNT of broken_not_reinstated plans (portal bank), latest ending per tier via XLATEST over hardship_holds (phone credit cushion, portal debit assistance); rule sentences reworded to "any payment plan" / "the most recent ... ending". Worlds have one plan / one hold, so the reads coincide with the old ones there.
- F3 (SOURCE-POLICY RED): the pay-down's reporting floor is now the base reporting minimum by debt type with no age tier (non-factor binding); the rule says obsolescence is left to the base credit reporting rule. To keep the drawn 4 factors: added paydown_recoupment_reserve (insurance payment credit in 3 months x rebill in 6 months), and paydown_margin_rule now reads the recency of the denied decision instead of the return count.
- F4 (observation): all rules now say "rounded to the cent (half to even)" (29 occurrences), matching RND.
- O1 (observation, block vs two-return tiers): no change; the base block stays inherited, no world uses the two-return tier.
- O2 (observation, claim coverage): no change; the account category's only numeric writes are money events, and refunds/returns are fixed by base, so payment ceilings are the only factor-bearing problems (recorded in Step 0 of this worklog).
- O3 (observation, stage/debt-type window): removed with F5.
- O5 (observation, "afterwards" in docstrings): reworded to "The receipt gives the consumer the confirmation number".
- 0.md #2 / 1.md #4 (charter defects not reached): closed by F1-F3 above; worlds unchanged.
- 0.md #3 (debit card vs checking in persona): no change; the persona already separates the instruments.
- 0.md #4 / 1.md #5 (multi-source label on one-record fields): factor_trace no longer labels credit_card_on_card_limit / portal_credit_bill_limit multi-source.
- 1.md #3 (O-1, persona hints the root edge direction): persona now says "the part coming from your checking account they can take over the phone" (no "whatever is left").
- Gates after rework (full block, no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (suite means branches=39.50 steps=13.00; history_rows_max=36; branches_max=41); GROUNDING OK; CACHE-DIFF INFO; SCOPE OK. validate_scenario: only "required document not found" errors (KB not rendered); stub-doc copy of this difficulty validates VALID.
