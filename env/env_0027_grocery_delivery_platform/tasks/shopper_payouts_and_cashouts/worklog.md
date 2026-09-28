# Worklog — shopper_payouts_and_cashouts (category payout), M=2

## Step 0 — difficulty pre-check
- Read: references (product_extended.yaml, task.json, task_tools.py), blueprint.yaml, products/payout.yaml, db_schema.json, share_tools.py.
- Base policies of payout: payout_agg_multi_holding, payout_plan_eligibility, payout_evt_earnings_ledger,
  payout_evt_instant_cashout, payout_evt_weekly_deposit, payout_evt_fee_refund, payout_evt_freezes,
  payout_evt_cashback, payout_evt_closure.
- Claimed events: payout_instant_cashout, payout_cashout_fee_charged, payout_fee_refunded, payout_account_unfrozen,
  payout_destination_changed, payout_plan_changed, payout_account_closed, payout_cashback_paid.
- Verification share tool passes at >= 2 matched details (phone/email/dob/zip).
- extended yaml base section = verbatim copy of blueprint/products/payout.yaml (+ extended_policies).

## Draw (draw_counts.py --tasks 2)
{"task": 0, "prerequisite_problems": 3, "problems": 4, "factor_counts": [5, 6, 5, 6]}
{"task": 1, "prerequisite_problems": 3, "problems": 4, "factor_counts": [5, 5, 6, 4]}
=> 8 extended policies in total, 8 distinct task tools, each task >= 2 value_input edges, >= 1 owner=user tool.

## Design decision (difficulty-level) — why these 8 problems
Payout writes that carry a real computed number are money rows (amount_usd). Status-only acts (unfreeze,
destination change) carry no number, so they are not problems here; where a status change is part of the
world it is either done before the opening (by the review team / an earlier agent) or it carries money
the business books at that moment (card-tier move settles closed, unpaid cashback). Claimed policies:
 T0 (Everyday Pay Card Gold shopper, fraud_review freeze 2026-08-28..2026-09-30 lifted by review team; frozen_time 2026-10-02):
   root  payout_ext_card_cashout        (user)  instant cashout onto the card           factors 6
         payout_ext_sweep_catchup       (agent) one catch-up deposit for weekly sweeps missed while not active  factors 5
         payout_ext_statement_cashback  (agent) statement-month cashback whose payment day passed unpaid        factors 6
         payout_ext_card_tier_move      (agent) card plan moved to the tier matching the level, settling closed unpaid cashback  factors 5
   edges: card_cashout <- sweep_catchup (value_input), card_cashout <- card_tier_move (value_input),
          card_tier_move <- statement_cashback (value_input)
 T1 (Instant Cashout shopper closing; frozen_time later chosen):
   root  payout_ext_closure_disbursement (user) final disbursement on closure           factors 6
         payout_ext_debit_cashout        (user) instant cashout to external debit card   factors 5
         payout_ext_returned_resend      (agent) re-send of a returned transfer once a new destination is on file and the account is active  factors 5
         payout_ext_former_card_cashback (agent) cashback earned on a card plan, unpaid when the account left the card plans  factors 4
Cross-difficulty evidence: shopper (level, status), batch (finalized/unfinalized tips, completed batches), membership.

## Tool names (uuid8 generated one per tool, frozen)
move_off_card_plan_7a80b851, resend_returned_transfer_f902fe69, send_catchup_deposit_164755b4,
cash_out_to_debit_card_0246d821 (T0) ; close_payout_account_ca79a9a7, cash_out_to_card_075a5c73,
pay_statement_cashback_5d281cc6, settle_closing_cashback_4e373fbf (T1)

## Task 0 design (Delphine Whitacre, frozen_time 2026-10-02 14:20:00 EDT)
Surface goal: "cash out as much as I can to my new debit card right now".
Tree: debit_cashout(root,user,6f) <- card_plan_exit(agent,6f... see yaml) [value_input: fee binding reads plan fee]
      debit_cashout <- sweep_catchup(agent,5f) [value_input: balance]
      sweep_catchup <- returned_resend(agent,5f) [value_input: returned remainder kept]
Draw factor multiset {5,6,5,6}: debit_cashout 6, card_plan_exit 6, sweep_catchup 5, returned_resend 5.
World: Everyday Pay Card Blue account; destination replaced by external debit card ••8427 on 2026-09-24;
09-22 weekly card load (period ending 09-20) returned 09-23 -> frozen transfer_returned; lifted 09-30 by agent;
09-29 sweep missed; Sept cashback earned (rows dated 10-01) unpaid; one batch completed 10-02 not finalized.

## T0 Step 1-2 persisted
- payout.extended.yaml: payout_ext_returned_resend (5f), payout_ext_sweep_catchup (5f), payout_ext_card_plan_exit (6f),
  payout_ext_debit_cashout (6f) written.
- task_tools.py: 4 T0 tools written; check_task_tools -> TASK TOOL CONTRACT OK.
Capability cards (summarised in docstrings): resend = agent, books one re-send deposit (payout_weekly_deposit with
source_event_id = returned entry), balance down; catch-up = agent, one payout_weekly_deposit with period end, balance
down; move_off_card_plan = agent, plan change + one payout_cashback_paid settlement, cashback balance cleared;
cash_out_to_debit_card = USER, one payout_instant_cashout + one payout_cashout_fee_charged, balance down by both.
No tool validates any prerequisite or eligibility; none writes another category; no event with a cross-category trigger.

## T0 Step 3/5 — seed + verification run (scratchpad/shopper_payouts_and_cashouts/build_t0.py, evalc.py, run_t0.py)
Seed: 47 batches (07-06..10-02; one completed-not-finalized on 10-02, tip 11.00), 121 batch_events, 148 payout_events,
balance 620.00, cashback 37.30 (Sept earned 21.40/9.80/6.10 unpaid), returned 09-22 deposit 208.00 (returned 09-23).
Param revision: resend limits 100/150 (was 200/300) and catch-up limits 200/300 (was 400/600) so the new-destination
limits bite on this world's weekly scale (symptom: resend limit decorative at 250 > 208; fix: params + rule text).
Run (gold order exit -> resend -> catch-up -> cashout, handling-time):
 exit 35.78 (baseline 25.00; sens cap 30.62, scope 35.20, share 44.73, fuel 33.90, auto 34.71, tenure 32.53)
 resend 161.10 (baseline 208.00; sens limit 181.60, mult 123.60, setoff 167.50, clawback 171.10, conduct 171.10)
 catch-up 246.05 (baseline 413.30; sens hold 211.45, returned-part 269.50, limit 404.95, tipbuf 253.55, conduct 258.05)
 cashout 146.60 fee 0.25 (baseline 201.35; sens tips 141.10, fee 146.35, return 166.60, debit 154.10, conduct 154.60, newdest 171.60)
Edge skips: skip exit -> cashout 146.85; skip resend -> catch-up 165.50; skip catch-up -> cashout 392.65.

## T0 closed — per-task gates (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK,
GROUNDING OK, CACHE-DIFF INFO, SCOPE OK. Revisions logged in tasks/0.json design_rationale [Revisions].
Manual values gates (T0): prerequisite sentences pass the 4-point test (2 affirmative, 1 negated); each state is set by
exactly one write of the difficulty; persona names no prerequisite; tools block nothing; no real-world wait (freeze lifted
09-30, destination recorded 09-24, cooldown ended 09-27); exit commutes with resend->catch-up (terminal DB identical).

## Task 1 design (card-plan shopper closing), draw {prerequisite_problems: 3, factor_counts: [5,5,6,4]}
Root payout_ext_closure_disbursement (user, close_payout_account_ca79a9a7) 6f
  <- payout_ext_card_cashout (user, cash_out_to_card_075a5c73) 5f  [value_input: balance]
  <- payout_ext_closing_cashback (agent, settle_closing_cashback_4e373fbf) 4f [state/value]
       <- payout_ext_statement_cashback (agent, pay_statement_cashback_5d281cc6) 5f [value_input: unpaid residual]
T1 Step 1-2 persisted: payout_ext_statement_cashback (5f), payout_ext_closing_cashback (4f), payout_ext_card_cashout (5f),
payout_ext_closure_disbursement (6f) in yaml; 4 tools appended; TASK TOOL CONTRACT OK (8 tools).
Edges: closure <- card_cashout (value_input, ACTION form: a cashout entry records no destination/plan, so the state does
not single out a card cashout from a debit cashout); closure <- closing_cashback (state_gate, ACTION form: same
cashback-payment entry kind as a statement payment); closing_cashback <- statement_cashback (value_input, state form).

## T1 closed — per-task gates (--task 1) all OK after one fix (card cashout request binding cites user_scenario
"sent out to you", on_request trigger). Run: statement 82.75 (base 60.00), closing 66.00 (base 26.80), card cashout 97.85
(base 168.85), closure 29.75 (base 46.70); skips: statement -> closing 34.50; cashout -> closure 127.60; cashout commutes.

## Difficulty-level closing record
- Coverage: 8 extended policies, T0 {card_plan_exit, returned_resend, sweep_catchup, debit_cashout}, T1 {statement_cashback,
  closing_cashback, card_cashout, closure_disbursement}; pairwise disjoint policies and tools; no idle policy or tool.
- Each task: 3 prerequisite problems (= draw), value_input edges T0 3/3, T1 2/3; user tools T0 1, T1 2.
- Prerequisite sentence directions across the charter: affirmative (only after) x4, negated (not ... until) x2;
  forms: state x4, action x2 (both with fallback_reason).
- No handoff in any gold; check_traceability skipped (KB not yet published).
- Final gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (suite means
  branches 94.50 / steps 17.50; history_rows_max 35; branches_max 97), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
- Temporary authoring scripts lived in scratchpad/shopper_payouts_and_cashouts/ and were deleted; __pycache__ removed.

## Rework round 2 (audit env/env_0027_grocery_delivery_platform/audits/policy_task/shopper_payouts_and_cashouts/)
Plan per item: F-C1 relabel 8 scalar "method" factors as parameter and give each of the 6 affected computations one
genuine method factor (selection rule largest/latest, history-derived vs fixed, proportional vs flat); F-C2 catch-up
sentence -> latest returned entry; F-C3 closing sentence -> payments cover the earned cashback of every due month;
F-C4 exit/statement caps as multiples of the plan cap; F-C5 state intermediate roundings/fall-backs, add level-order
sentence (lvl_rank basis); F-C6 sentence/condition wording, closure gate field, generic effect text; F-C7 closure <-
card cashout to state form; F-C10 docstrings; T0 seed on Everyday Pay Card Platinum (level-following), batch clock
stamps before frozen_time in both tasks; unrecorded freeze dates removed from proofs; persona consent lines neutral.
- Charter edits persisted (payout.extended.yaml, re-serialised extended_policies only; base section byte-identical):
  F-C1 relabelled to parameter: resend_limit_standing_multiplier, unfinalized_batch_leave_behind, returned_part_sweep_treatment,
  unfinalized_tip_hold, closing_ev_counting, card_tip_release, closing_unfinalized_hold, closing_reserve_scaling.
  Genuine methods: resend_debit_setoff_choice (largest debit ever vs latest debit vs none), catchup_new_destination_limit
  (largest weekly deposit ever vs fixed 200.00 vs whole balance), cashout_new_destination_hold (10 % of balance vs fixed
  50.00 vs none), closing_thank_you (5 % of shared figure vs fixed 1.50 vs none), card_debit_buffer (largest debit ever vs
  fixed 10.00 vs none), closing_clawback_reserve (largest batch pay reversal vs fixed 20.00 vs none). Kept: exit_cap_category_scope,
  statement_late_make_good. Each of the 8 computations now carries >= 1 honest method.
  F-C2 catch-up sentence/condition -> "latest returned-transfer entry". F-C3 closing sentence -> "cashback payments ... cover
  all the cashback earned in statement months whose payment day has passed" (+condition). F-C4 exit/statement caps -> 1.5x /
  1.25x the plan cap (never equal to or below the fall-through). F-C5 intermediate roundings stated, final-figure wording,
  fall-backs stated (statement opening date, card-cashout opening date), level-order sentence added to all 8 rules and quoted
  as lvl_rank basis. F-C6 debit<-catch-up sentence "covering the weekly deposit days", condition "not active"; closure<-closing
  gate payout_accounts.cashback_balance_usd; debit<-exit effect made general. F-C7 closure<-card cashout now state form
  ("carries an instant cashout dated the day of closing"), fallback_reason removed. F-C10 docstrings of
  settle_closing_cashback_4e373fbf / close_payout_account_ca79a9a7 reworded. TASK TOOL CONTRACT OK, EXTENDED OK after edits.
- Per audit item (closing record, round 2):
  F-C1 (RED, both tasks): closed as planned above; honest method per computation: exit (category scope), resend (set-off
    choice), catch-up (limit = largest deposit vs fixed), debit cashout (10 % hold vs fixed), statement (make-good),
    closing (thank-you 5 % vs fixed), card cashout (buffer = largest debit vs fixed), closure (clawback = largest reversal vs
    fixed). All factors still bear weight (check_compute).
  F-C2 (RED): payout_ext_sweep_catchup rule + prerequisite[0].policy_source now "latest returned-transfer entry" = re-send rule.
  F-C3 (RED): payout_ext_closing_cashback sentence/condition now amount-based ("payments cover all the cashback earned in
    statement months whose payment day has passed"), which one statement payment satisfies for any number of due months.
  F-C4: exit/statement caps = 1.25x/1.5x the plan cap (params exit_cap_mult_*, statement_cap_mult_*); T0 seed also moved to
    the level-matching Everyday Pay Card Platinum (0.md obs 3).
  F-C5: roundings of held/kept/closing_hold/reserves/drawn stated in rules; final-figure wording; fall-backs stated
    (statement last payment -> opening date; card cashout level evaluation -> opening date); level-order sentence in all
    rules, quoted as lvl_rank basis.
  F-C6: debit<-catch-up sentence "covering the weekly deposit days", condition "not active"; closure<-closing gate
    payout_accounts.cashback_balance_usd; debit<-exit effect general.
  F-C7: closure<-card cashout state form, "cashable balance" phrase removed; T1 why_false reworded.
  F-C8: both gating states hold at the opening in T0 (destination 2026-09-24 after the 2026-09-23 return; status active);
    recorded in the T0 proofs; no charter change (no tool exists for those base acts, none is needed in either world).
  F-C9: kept (not demonstrated as unreal); the holds remain stated in full in each rule.
  F-C10: docstrings of settle_closing_cashback_4e373fbf / close_payout_account_ca79a9a7 reworded (no progressive
    "being closed", no lapse restatement).
  0.md obs 3 (Gold on Blue) -> Card Platinum since 2026-06-01; obs 4 / 1.md obs 4 (clock) -> unfinalized batches accepted
    10:05 / 07:05; obs 5 / 1.md freeze claim -> unrecorded dates removed from proofs; obs 6 / 1.md obs 6 (persona) ->
    neutral consent / hand-over lines; 1.md obs 3 -> F-C7; 1.md obs 5 -> F-C6.
  New gold: T0 71.56 / 161.10 / 172.15 / 216.82 (fee 0.25); T1 82.75 / 66.15 / 81.25 / 53.05.
  Final gates round 2: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
    CACHE-DIFF INFO, SCOPE OK (traceability skipped). Scratch folder and __pycache__ deleted.

## Rework round 3 (audit revision_2)
- F-R2-1 (RED): payout_ext_closing_cashback sentence/condition -> "the latest statement month whose payment day has
  passed carries a cashback payment"; payout_ext_statement_cashback rule + baseline.rule -> "it carries the latest such
  month; whatever the cap leaves unpaid of those months lapses with the payment". One statement payment always makes the
  state true whatever the cap (no second payment of a month needed, base C5 respected). T1 edge, tracing, order text,
  rationale synced; gold unchanged (82.75 carries 2026-08, the only and latest passed month).
- F-R2-2 (obs): catch-up limit now "largest single weekly sweep deposit ever booked, re-send deposits not counted"
  (compute filter source_event_id=None); T0 figure unchanged (226.10). The "ever booked" debit tiers state their scope.
- F-C6 (obs, gate field): kept payout_accounts.cashback_balance_usd - the skill's state_gate contract allows
  <table>.<field>; the closure policy declares no eligibility id; rationale records this. No value consequence.
- F-C8, F-C9 (obs): kept; F-C8 opening facts recorded in T0 rationale.
- 1.md new obs (5cbab988 finalization clock): batches completed the day before frozen_time (T0 3fd282c8, T1 5cbab988)
  now accepted 08:05 so the 24-hour finalization precedes the call.
- Round 3 gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; scratch and __pycache__ removed.

## Rework round 4 (audit revision_3)
- F-R3-1 (RED, latent): removed the statement lapse clause (it had no record behind it). The charter now defines the
  cashback still to be paid once: the card cashback balance shown on the account (raised by earnings, lowered by every
  cashback payment incl. bonuses, cleared when the card's cashback lapses, never below zero, never above earned - paid).
  Readers checked and aligned: payout_ext_statement_cashback (cash_bal = MX(0, MN(balance, earned - paid)); due =
  cash_bal - waiting month; new minimum-payment test `owed`, result 0 when not owed); payout_ext_card_plan_exit older part
  = cash_bal - unpaid latest month; closing reads only the latest waiting month (never paid by the statement);
  exit/closure tools clear the balance (lapses recorded); statement/closing tools lower it, clamped at 0.
  Consequence check: with carry-over, a capped payment can leave part due for the next payment day and a sub-minimum
  due owes no payment, so the round-3 state wording of closing <- statement ("latest passed month carries a payment")
  would be unreachable in those worlds -> changed to ACTION form with fallback_reason ("fixed only after the statement
  payment owed for the months whose payment day has passed, where one is owed, has been made"): one payment, or none when
  nothing is owed, always resolves it; no month is paid twice (base C5 kept).
  All gold figures unchanged (T0 71.56/161.10/172.15/216.82, T1 82.75/66.15/81.25/53.05); T0/T1 tracing, factor_trace,
  E3 edge, rationale synced.
- F-C6 (obs): kept; closure has no eligibility of its own and a value link would invent a cashback term in the final
  disbursement. F-C8, F-C9 (obs): kept.
- Round 4 gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; scratch and __pycache__ removed.
