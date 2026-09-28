# Worklog — debit_card_disputes_and_card_servicing (M=2)

## Step 0 — difficulty pre-check
- Draws (draw_counts.py --tasks 2):
  - task 0: prerequisite_problems=1, factor_counts=[4, 4]
  - task 1: prerequisite_problems=1, factor_counts=[4, 6]
- Base card charter read: owner=user writes are activation, cancellation, filing a dispute, withdrawing a dispute.
  Only dispute filings carry a computable scored value (dispute_amount / customer_liability), so every task's
  user problem is a dispute filing, and each task's agent problem is an on-filing credit or refund on the same card.
- DSL constraint: history primitives are scoped to one card holding and windows are rolling months; a per-transaction
  quantity is therefore only honest on a card whose whole activity is the disputed object (a single-use virtual card,
  or a virtual card created during an account takeover). Both tasks are built on such single-object cards.

## Task 0 — closed (takeover card: unauthorized filing -> final credit)
- Claimed: card_ext_takeover_card_liability (file_unauthorized_card_dispute_b9450be9, user, 4 factors) and
  card_ext_takeover_card_final_credit (post_takeover_dispute_credit_edfadedb, agent, 4 factors); edge value_input, state form.
- Gold: customer_liability 12.00, credit_amount 410.89; baselines 50.00 / 377.00; skip-filing credit 23.89.
- Base-layer defect routed around: card_disputes_merchant.merchant_contacted_first is a caller_statement gate whose
  correlation key is card_transactions.card_txn_id, which a caller cannot state verbatim; it is retired for these
  filings through a declared overwrite of the merchant-contact clause (the clause never applied to unauthorized or
  incorrect-amount reasons anyway).
- Per-task gates (--task 0): check_task_tools OK, replay OK, solvability OK, compute OK, grounding OK, cross_fire OK;
  check_extended red only because the task-1 tools were not yet named by a policy (expected until task 1 lands).

## Task 1 — closed (single-use card: incorrect-amount filing -> credit on filing)
- Claimed: card_ext_single_use_incorrect_amount (file_incorrect_amount_card_dispute_a0bf950b, user, 4 factors) and
  card_ext_single_use_filing_credit (post_on_filing_dispute_credit_86bd6080, agent, 6 factors); edge value_input, state form,
  negated direction ("not ... until"), so the charter carries both prerequisite-sentence directions.
- Gold: dispute_amount 49.25, credit_amount 47.75; baselines 92.75 / 25.00; skip-filing credit 0.00.
- Per-task gates (--task 1): all seven green.

## Difficulty closure
- Coverage: 4 extended policies, each claimed by exactly one task; task tools pairwise disjoint; every task calls one
  owner=user tool; no handoff in gold.
- Final gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK
  (branches mean 28.50, steps mean 11.00, history_rows_max 9, branches_max 29), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
- check_traceability not run: it needs the published KB, which is not rendered yet.

## Rework round 2 (policy audit r1)
- F1 (SOURCE-POLICY RED, task 0): card_ext_takeover_card_liability and card_ext_takeover_card_final_credit now each
  declare base card_disputes_unauthorized's small-dispute auto-credit sentence superseded, with a new sentence in each
  rule stating the takeover-card rule applies whatever the amount. No compute change; task 0 gold unchanged.
- F2 (SOURCE-FACTOR RED, task 1): card_ext_single_use_filing_credit.tenure_multiplier_tier relabelled effect: parameter
  (tiers now carry value); tasks/1.json factor_trace[0] relabelled. The policy keeps 1 method factor (near_ceiling_release).
- Observations O1–O11 and P1 were recorded as not grounds for rework and are left as they are.
