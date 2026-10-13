# mobile_wallet_transfers — instantiation worklog (difficulty-level notes; per-task dossiers live in tasks/N.json design_rationale)

## Step 0 — difficulty pre-check
- Category: wallet (Mobile Wallet). Base read: binding, 7 lifecycle states, 15 claimed event types, 10 base policies.
- Draw (scripts/draw_counts.py --tasks 2):
  {"task": 0, "key": "env_0030_money_transfer_service/mobile_wallet_transfers/0", "prerequisite_problems": 3, "problems": 4, "factor_counts": [6, 5, 5, 5]}
  {"task": 1, "key": "env_0030_money_transfer_service/mobile_wallet_transfers/1", "prerequisite_problems": 1, "problems": 2, "factor_counts": [5, 4]}
- Constraints found while scanning base gates (they shape which writes can be problems):
  * every wallet_fee_refunded write inherits wallet_evt_cancellation.full_refund_window (a cancellation time gate) and
    wallet_evt_on_time_promise.credited_late — no single fee refund can satisfy both, so no problem writes a fee refund;
  * wallet_redirect_requested inherits redirect_rules (authority mixed, caller binding on wallet_transfer_id) — not
    satisfiable from a persona without leaking an internal id, so no problem records a redirect;
  * the DSL cannot read fx_rate_sheet, so no problem re-quotes from the daily sheet;
  * customer-owned writes with a numeric parameter in this charter are the remedy choice (re-credit / refund) and booking;
    booking creates a new holding (compute cannot target it) — so the customer's own write in each task is a remedy choice.
- Space plan (M=2): task 0 = incorrect-amount shortfall (make-good + customer re-credit) gated by an earlier bounced
  transfer to the same wallet (resend charge + resend); task 1 = wrong-wallet finding (funding credit + customer re-credit).
- Bands (k=4): phones 555-0160..0179, id_document_last4 / ein_last4 start with 4, confirmation/order/pickup/doc/payout refs numeric part starts with 4.

## Task 0 — tools (uuid8 drawn one per tool with uuid.uuid4().hex[:8])
- charge_resend_fee_8300b1da (agent) — wallet_ext_resend_charge
- resend_failed_credit_8d2e2e1a (agent) — wallet_ext_resend_credit
- book_shortfall_makegood_2311834f (agent) — wallet_ext_shortfall_makegood
- choose_shortfall_recredit_f54302ef (user) — wallet_ext_shortfall_recredit

## Task 0 — closed
- Tree: root wallet_ext_shortfall_recredit (user) <- wallet_ext_shortfall_makegood (value_input, held_usd)
  <- wallet_ext_resend_credit (state_gate, earlier-booked transfer to same wallet no longer credit_failed)
  <- wallet_ext_resend_charge (value_input into resend, paid_charge). Factors 6/5/5/5.
- Gold: charge 1.27 -> resend 71825.41 (rate 56.1136) -> make-good 13.35 -> customer re-credit 763.71 (rate 57.2064).
- Revisions: helpers inlined in task_tools.py (gate treats every def as a tool); make-good reads delivered amount by SUM
  (history floor); closure trimmed (rate sheet, top-up ledger dropped; ledger read by customer; recipient/bank/cash reads).
- Per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

## Task 1 — snapshot before claiming
- Occupied by task 0: policies resend_charge / resend_credit / shortfall_makegood / shortfall_recredit; tools 8300b1da,
  8d2e2e1a, 2311834f, f54302ef; events retry_fee charge, customer resend, incorrect_amount make-good, recredit_shortfall.
- Free for task 1: wrong_wallet_credited remedy (error_recredit funding + remedy_choice recredit) on a different
  customer/transfer. Draw: 1 prerequisite problem, factor counts {5,4}.

## Task 1 — closed
- Tree: root wallet_ext_wrong_wallet_recredit (user, choose_wallet_recredit_d4ef146e) <- wallet_ext_wrong_wallet_funding
  (value_input, held_usd; fund_wallet_recredit_aebfda78). Factors 5/4.
- Gold: funding 621.50 -> customer re-credit 80803.70 KES (rate 130.0140).
- Revision: Cash Pickup dropped as a factor source (no KE-KES cash corridor); Top-Up and Paloma Business used instead.

## Difficulty close
- Coverage: 6 extended policies, each claimed by exactly one task; 6 task tools, pairwise disjoint scopes.
- Prerequisite sentences: 2 affirmative ("only after"), 2 negated ("not ... until"); all state form.
- Runnable recomputation entry point: .venv/bin/python skills/erl-task-instantiate/scripts/check_compute.py <difficulty> [--task N]
  (replays gold with the real tools and evaluates every compute on its handling-time world, per-factor and all-baseline).
- Temporary authoring scripts (_author_*.py) deleted.
- Final gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO (optional), SCOPE OK; check_traceability pending the published KB.

## Round 2 — audit audits/policy_task/mobile_wallet_transfers (0.md PASS, 1.md SOURCE-POLICY RED F-1)
- F-1 (RED): all 7 window sentences of the 6 policies (bank 6m, cash 6m, top-up 12m, cash payouts 12m, bank payouts 12m,
  bank 12m, top-up 6m) now state the rolling convention in rule + compute_basis ("fewer than N whole calendar months before
  today; whole months = calendar-month difference, less one when today's day of the month is lower than the entry's"),
  ladders marked "rolling". Compute unchanged (it already was within_months). Task 1's 2026-04-02 top-up is excluded by
  the rule's words; no scored value moved.
- O-2: funding rule conditions on the customer asking for the re-credit (stated choice). O-4: collection sentence names
  ACH debit and wire. O-8: fee_seq docstring = number of credits already sent. O-9: edge effects reworded.
- Task-0 observations: T2 date_available -> 2026-09-24 (retry day); account_standing_relief no longer labelled
  multi-source; resend stage_provenance cites the persona's "cause fixed" line. Task-1 observation: standing_goodwill /
  business_points no longer labelled multi-source. Traces, necessities and rationales updated for the window wording.
- Not acted on (no consequence, no fix within the frozen base / DSL): O-1, O-3, O-5, O-6, O-10, O-11, O-12, O-0 (replay
  row for 0.json is present in this run).
- Gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.

## Round 3 — scenario load check (erlbench validate_scenario: frozen_time must start with YYYY-MM-DD + word boundary)
- frozen_time: task 0 '2026-10-06T11:20:00' -> '2026-10-06 11:20:00 CDT'; task 1 '2026-10-08T15:05:00' -> '2026-10-08 15:05:00 CDT'.
- task_tools.py: resend_failed_credit_8d2e2e1a, choose_shortfall_recredit_f54302ef, choose_wallet_recredit_d4ef146e rebuild
  released_at as '<date>T<HH:MM:SS>' from the clock, so the stored timestamps keep the schema form and are unchanged
  (replay: 2026-10-06T11:20:00 / 2026-10-08T15:05:00). Date parts (ctx.now()[:10], NOW) unchanged. No scored value moved.
- design_rationale of both tasks: the quoted frozen_time updated; a round-3 note appended.
- Gates: all OK incl. TRACEABILITY OK; validate_scenario: no wallet errors.
