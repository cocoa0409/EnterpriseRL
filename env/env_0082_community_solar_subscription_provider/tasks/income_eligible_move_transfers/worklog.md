# worklog — income_eligible_move_transfers (access), M=2

## Step 0 — draw (printed by draw_counts.py --tasks 2)
{"task": 0, "prerequisite_problems": 3, "problems": 4, "factor_counts": [6, 6, 6, 6]}
{"task": 1, "prerequisite_problems": 2, "problems": 3, "factor_counts": [6, 4, 6]}

## Step 0 — charter stock-take (base access.yaml, frozen)
- Numeric write fields in the claimed events: access_allocations.kw (reassigned / reduced lines), access_billing.amount
  (charges). access_transfer_requested / access_recertified / access_transfer_completed / _lapsed carry no number of their own.
- Variant parameters that differ across the six Access plans: savings_rate_pct, recert_interval_months,
  nonpayment_removal_days_past_due, billing_types_offered, eligible_programs; every other Access parameter is one value.
- BLUEPRINT-KNOWN (DSL, frozen): compute can read only this holding, its own event/intake tables and other categories'
  holdings / event tables. utility_accounts (usage, usage_as_of_month, status, designation, assistance flag, data
  authorization) and projects (yield, program, utility, capacity) are NOT readable by compute. They act only as
  agent-checked record tests (eligibility, prerequisites, scope), never as factor evidence.
- access_benefit_basis (account-wide, binding): a charge is priced only by its own plan's pricing; no other line,
  reservation or promotion changes it; billing credits are separate lines. => no cross-difficulty factor on a charge's
  price; cross-difficulty factors sit on kW sizing (another line's true-up as the household's consumption record) and on
  the estimate's credit-value basis (the converted residential plan's credit statements: raw utility-reported values,
  priced at the Access plan's own rate).
- The only by:user transition among the claimed events (access_transfer_requested) has no numeric field, so the
  customer-own computed writes are holder-completed payments through the secure payment portal (owner_ruling (b);
  base access_evt_payment_application: "Meadowlark representatives never take card or bank account numbers").
- Thin charter vs the draw (40 factors over 7 computations): the honest record-backed levers number far fewer than 40.
  Factors beyond the base-grounded ones are written as Meadowlark's own published schedules keyed on recorded fields,
  tagged R6 in the factor card below, each with an overwrite where it replaces a base sentence.

## Structural decision (scope claim for both tasks, Principle C)
- task 0 (out-of-territory move, subscription already closed as moved_out_of_territory; money tree, 4 problems):
  root = closing-balance payment (owner=user); prerequisites = estimated charge for the statement month the utility has
  not reported (cross: converted residential plan's credits), actual charge for the credit that posted after closing,
  reversal-correction credit for a credit the utility partly reversed after closing. Edges: payment <- each (value_input);
  actual charge <- estimate (state: statement order).
- task 1 (in-territory move under a nonpayment removal notice; 3 problems): root = reassignment filing with the move
  resize, kW kept (cross: converted residential plan's true-up as the consumption record); prerequisites = past-due
  payment that clears the removal notice (owner=user, state gate on the filing), billing-error correction of a charge
  billed at the wrong plan rate (value_input into the past-due payment).
- Disjointness: task 0 claims {closing payment, final-month estimate, post-closing charge, reversal correction};
  task 1 claims {move reassignment sizing, removal-notice payment, rate-error correction}. No policy, tool or
  (target_tool, computes) pair is shared.

## Step 0 — REVISION 1 of the scope claim (final for round 1)
Symptom: a past-due payment can only take value inputs from billing credits on past-due lines; a closing payment can
take them from new charges too; the kW filing can only take them from allocation or review writes. Root cause: value
edges must land on bindings the depended-on write actually changes. Change:
- task 0 = closing settlement of a share closed at an out-of-territory move (MD, Pepco -> BGE), 4 problems:
  P0 root  access_ext_move_closing_settlement   (owner=user payment)       <- E0, C0, R0 (value_input)
  E0       access_ext_move_closing_estimate     (estimated charge, cross: converted residential plan's statements)
  C0       access_ext_move_post_closing_charge  (actual charge for the statement posted after closing) <- E0 (state:
           statements are billed in statement order)
  R0       access_ext_move_partial_reversal_credit (correction credit for a partly reversed statement)
- task 1 = in-territory move under a nonpayment removal notice (NY, National Grid), 3 problems:
  A1 root  access_ext_move_reassignment_sizing  (kW kept at the new account, cross: converted residential plan's true-up)
           <- P1 (state: no outstanding removal notice)
  P1       access_ext_move_notice_payment       (owner=user payment of the whole past-due balance) <- B1 (value_input)
  B1       access_ext_move_rate_error_credit    (billing-error credit for a charge billed at the wrong plan rate)
Factor counts: P0 6, E0 6, C0 6, R0 6 | A1 6, P1 6, B1 4.

## Step 0 — REVISION 2 (final round-1 claim)
Symptom: the account-wide access_benefit_basis forbids any term but the plan's savings rate on a charge, so a charge
computation carries at most the base recertification rate and the priced-value rules; corrections inherit the same
limit. Root cause: thin charter (BLUEPRINT-KNOWN). Change: put the charge in the 4-factor slot and keep the
6-factor slots for computations whose method genuinely varies (estimate, sizing, settlement composition, correction
extent).
- task 0 (MD, Pepco, closed moved_out_of_territory; converted from a residential plan on the same account):
  P0 root access_ext_move_closing_settlement (owner=user, 6) <- E0, B0, R0 (value_input each)
  E0 access_ext_move_closing_estimate (6, cross home)  B0 access_ext_move_rate_error_credit (6)
  R0 access_ext_move_partial_reversal_credit (6)
- task 1 (NY, National Grid, transfer pending; converted from a residential plan with a completed residential true-up):
  A1 root access_ext_move_reassignment_sizing (6, cross home) <- P1 (state: no open dual balance)
  P1 access_ext_move_transfer_settlement (owner=user, 6) <- C1 (value_input)
  C1 access_ext_move_out_statement_charge (4)

## Step 0 — REVISION 3 (final round-1 claim; supersedes revisions 1-2)
Symptom: payments and corrections, like charges, carry almost no record-backed method variation; only the
estimate (Meadowlark's own estimation convention) and the move sizing (Meadowlark's own sizing practice within the
program cap) do. Change: give each task one estimate-type or sizing-type computation per cross-difficulty need and
keep the thin computations to the minimum the draw forces (payments x2, corrections x2).
- task 0 (NY, National Grid, in-territory move, transfer pending; household converted from a residential plan):
  A0 root access_ext_move_reassignment_sizing (6, cross home true-up) <- P0 (state: no open dual-billed balance)
  P0 access_ext_move_transfer_settlement (owner=user payment, 6) <- E0 (value_input), R0 (value_input)
  E0 access_ext_move_pending_estimate (6, cross home statements)
  R0 access_ext_move_partial_reversal_credit (6)
- task 1 (MD, Pepco -> BGE, closed moved_out_of_territory; household converted from a residential plan):
  P1 root access_ext_move_closing_settlement (owner=user payment, 6) <- E1 (value_input), B1 (value_input)
  E1 access_ext_move_closing_estimate (6, cross home statements)
  B1 access_ext_move_rate_error_credit (4)
Tools (uuid8 drawn one per tool): file_move_reassignment_5a7d54a1, pay_transfer_balance_0f5b0288 (user),
bill_pending_estimate_ff226895, credit_partial_reversal_7609dc6e | pay_closing_balance_ce594868 (user),
bill_closing_estimate_4dff6268, credit_rate_error_cc3dddf3.

## Step 0 — REVISION 4 (final for round 1; supersedes 3)
Symptom: a state gate "no open balance" forces the gating payment to equal the ledger balance, leaving it no rule of
its own. Root cause: the gate quantity and the payment's own computation coincide. Change: task 0's gate is the
base nonpayment-removal mechanism (access_nonpayment_removal: "Payment of the whole past-due balance before the
removal date clears the notice (removal_notice_date emptied)"); the share is reassigned only once the subscription
carries no outstanding removal notice. The payment clears the notice (its own same-category consequence) and its
amount is the clearing balance its own rule defines. Value inputs into that payment are billing credits on
past-due lines (reversal correction, rate-error correction). The estimate stays only in task 1.
- task 0 (NY, National Grid, transfer pending, removal notice outstanding; converted household):
  A0 root access_ext_move_reassignment_sizing (6, cross home) <- P0 (state_gate: removal_notice_date empty)
  P0 access_ext_move_notice_payment (owner=user, 6) <- R0 (value_input), B0 (value_input)
  R0 access_ext_move_partial_reversal_credit (6)   B0 access_ext_move_rate_error_credit (6)
- task 1 (MD, Pepco -> BGE, closed moved_out_of_territory; converted household):
  P1 root access_ext_move_closing_settlement (owner=user, 6) <- E1 (value_input), C1 (value_input)
  E1 access_ext_move_closing_estimate (6, cross home)   C1 access_ext_move_post_closing_charge (4)
  C1 <- E1 (state: statements are billed in statement order)

## Step 0 — REVISION 5 (round-1 final)
Symptom: a payment limited to the past-due balance can take value inputs only from billing credits on past-due
lines, which forces a second correction policy. Change: the household settles its whole old-address ledger; any
payment of at least the past-due balance clears the removal notice (base access_nonpayment_removal), so the gate
stays the notice and the settlement's scope is its own rule. Task 0 = A0 (root), P0 (user), E0, R0; task 1 = P1
(root, user), E1, C1. B0 dropped. Thin computations in 6-factor slots: P0, R0, P1 (R6-tagged schedules).

## Progress log
- access.extended.yaml assembled (base verbatim + 7 extended policies); check_extended structural FAILs left are only
  "no tasks yet" (cardinality/coverage). task_tools.py: 7 tools, TASK TOOL CONTRACT OK.
- Revision: A0 subject narrowed to [access_allocation_reassigned] (the kW it computes lands on the reassignment
  line; base gate within_transfer_window applies to access_transfer_requested/completed, which no tool here writes).
- Revision: estimate tools carry access_credit_id (passed empty) because base dedup gate one_charge_per_credit binds
  access_billing.access_credit_id on every access_charge_billed write.
- Revision: settlement payments net credits across the whole settlement (MX(0, past-due figure + added shares));
  the floor of the standard settlement alone dropped credit balances.
- Scratch harness (/tmp/income_eligible_move_transfers_0082/bin): world builders w0.py / w1.py, run0.py / run1.py.
  Task 0 handling-time values: E0 46.58 (baseline 63.50), R0 34.28 (28.90), P0 111.50 (0.00), A0 3.6 kW (5.0).
  Task 1 handling-time values: E1 42.64 (56.92), R1 22.45 (17.31), P1 95.08 (0.00). Every single-factor
  substitution moves the result; no value within 1e-4 cent of a half cent.

## Trigger list (XF F4) — every event a task tool writes, with its base `triggers`
- file_move_reassignment_5a7d54a1: access_allocation_reassigned (triggers []), access_allocation_reduced move_resize
  (triggers []); updates access_subscriptions.allocation_kw and the access_requests line (intake). No other category.
- pay_move_settlement_0f5b0288 / pay_closing_balance_ce594868: access_payment_received (triggers []).
- bill_pending_estimate_ff226895 / bill_closing_estimate_4dff6268: access_charge_billed (triggers []).
- credit_partial_reversal_7609dc6e / credit_closed_reversal_cc3dddf3: access_billing_credited (triggers []).

## What each factor reads (XF A1) — no factor reads another factor's binding
| policy | factor | reads (own bindings) | shared plain selections it uses |
|---|---|---|---|
| A0 sizing | record_source | home CFIELD closure/sub/contract_kw, home XCOUNT/XLATEST reviews, own access_reviews count, reassigned lines | own review fields (plain) |
| A0 | banking_cap | access_credits banked_value window 12 months | — |
| A0 | verification_age_allowance | income_verified_date | — |
| A0 | share_size_allowance | access_allocations initial kW | — |
| A0 | restatement_allowance | latest access_credit_reversed posted_date | — |
| A0 | conversion_allowance | home CFIELD closed_date | — |
| P0/P1 settlement | not_yet_due_share | actual charges due after today, move_out_date | — |
| P0/P1 | open_estimate_share | actual charges invoiced in two whole months | estimate_open (plain) |
| P0/P1 | unbilled_statement_share | request received_date | unbilled component (plain) |
| P0/P1 | unbilled_banked_value | latest posting value/banked | — |
| P0/P1 | final_month_prepay_share | latest payment bill_date | — |
| P0/P1 | final_month_prepay_basis | latest estimate, actual count, latest actual | estimate_open (plain) |
| E0 | basis_rate_restatement | posted values, latest posting priced?, billing-error credits | rate_now (plain) |
| E0 | reversal_deduction | reversal values, latest reversal month postings | rate_now (plain) |
| E0/E1 | young_share_pct | activation_date | — |
| E0 | request_wait_pct / E1 request_age_pct | request received_date | — |
| E0 | moved_out_pct | move_out_date | — |
| E1 | departure_pct | closed_date | — |
| E0/E1 | share_band_pct | access_allocations initial kW | — |
| E1 | residential_fill | home EXISTS converted, XCOUNT/XLATEST home_credits | basis count (plain) |
| E1 | reversal_restatement | reversal values, latest reversal month postings | — |
| R0/R1 | reversed_part_rate | reversed line posted_date, recert dates, offset charge vs plan price | line value, charge (plain) |
| R0/R1 | corrected_value_basis | reversal kWh/value, line kWh/value | — |
| R0/R1 | held_interest_rate | days since the offset charge's due_date | charge_due_date (plain) |
| R0/R1 | held_days_start | due-date vs payment-date day counts | pay_date, paid_after_bill (plain) |
| R0 | interest_year | latest payment method | — |
| R0 | restatement_lag_uplift | reversal posted vs line posted | — |

## Defining-sentence table (XF A4) — sentence -> owner
- "The rate in force on the estimate/settlement date is lapsed_savings_rate_pct when ..." -> plain (shared by every
  factor of that policy; base access_recertification restated).
- "The standard move sizing rests on ..." / "The standard ... estimate ..." / "The standard reversal correction ..." /
  "The standard move settlement / closing payment ..." -> baseline paragraph of each policy (computation document).
- Each "<Quantity> of the <act>: when ..." paragraph -> the one factor of that name; quantities are named after the act
  ("the awaiting-move estimate", "the estimate" of a closed share, "the move settlement", "the closing payment",
  "the move sizing", "the correction") so no ladder attaches to two baselines.

## Pairwise method-tier table (XF B1)
- record_source: residential review vs whole share (different input: home_reviews vs none); residential vs own review
  (different table); whole share vs own review (sizing operation absent vs present).
- basis_rate_restatement: billed-less-error-credits (input: billing-error credits) vs restated sum (input: posted
  credit values at the rate in force) vs billed sum (input: charges only).
- reversal_deduction / reversal_restatement: re-posting tier (count operation / nothing) vs single-posting tier
  (reversed value deducted) vs none.
- unbilled_banked_value: half-banked add-back (operation on banked) vs applied-only (credit less banked) vs whole.
- final_month_prepay_basis: latest estimate (input: estimated line) vs average of actuals (operation: mean) vs latest
  actual.
- corrected_value_basis: kWh x line rate (inputs kWh and line rate) vs line value x kWh share (operation: ratio) vs
  reversal value.
- held_days_start: from due date vs from payment date vs no interest (different anchors).

## Probe table (XF C1) — scratch copies of the task-0/1 worlds
| read | decoy / second record / absent | outcome |
|---|---|---|
| home plan (CFIELD converted on same account) | converted plan on another account; absent | filtered by utility_account_id; absent -> own record / whole share |
| home reviews (XLATEST by review_date) | second (later) review | latest review_date is used, as the rule states |
| access reviews | own true-up present | record_source tier (c) own record; >18 months old with a reassignment -> whole share |
| banked lines (COUNT with banked_value=0.0) | banked_value stored as 0.0 | exact-value filter: seeds write 0.0 floats (DSL-KNOWN: an int 0 would not match) |
| latest posting priced? (COUNT charges with its credit id) | latest posting already priced | nothing left out of the basis / no unbilled component |
| reversal (LATEST + SUM by reversed id) | second reversal of the same line | both summed into the reversed part (rule: every reversal naming the line) |
| payment (LATEST bill_date) | no payment | no interest; prepay share 0 |
| actual charges count | zero actual charges | out of scope (estimate scopes require at least one); P basis avoids division unless >= 2 |
| request (LATEST move_transfer) | no request | request-wait/age 100 percent; report shares 0 |
Same-day ties: credit postings and reversals carry at most one line per posted_date in these worlds; the rule states
"a subscription carries at most one reversal per posted_date" for the correction (C2).

## Manual values gates (round 1, both tasks)
- Problem trees: task 0 = 3 prerequisites (2 value_input, 1 state_gate), task 1 = 2 (both value_input); every
  prerequisite false at the opening with seed evidence in prerequisite_closure; each resolved by a synchronous task
  tool; the customer's own write is the portal payment in both tasks.
- Persona: no prerequisite named; payments only after hand-over; no ask outside the tree.
- Realism status: factors tagged R6 in each task's factor card are Meadowlark schedules keyed on recorded fields; the
  sizing allowances keep the kept share at or below the program cap (100 percent of the record usage). The thin
  charter (BLUEPRINT-KNOWN, see Step 0) forces more R6 schedules than "minimal"; flagged for the policy audit.

## Final gate block (round 1)
- EXTENDED OK
- TASK TOOL CONTRACT OK
- REPLAY OK
- SOLVABILITY OK
- COMPUTE OK
- GROUNDING OK
- SCOPE OK
ROUND 1: gates 7/7 green
