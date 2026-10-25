# worklog — business_allocation_changes_and_trueups (biz), M=2

## Step 0 — difficulty pre-check
- Read: references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/biz.yaml, db_schema.json,
  share_tools.py (verify K=2), audits/render_source/{XF_recipe.md, realism_bar.md, owner_ruling.md}, inst_common.md.
- Draws: task0 prerequisite_problems=1 factor_counts=[6,5]; task1 prerequisite_problems=1 factor_counts=[6,6].
- DSL ceiling (decisive): compute reads only the biz holding (F), plan params (P), own params (K), biz event/intake
  rows (biz_allocations, biz_credits, biz_billing, biz_reviews, biz_requests), and other categories' holdings/events.
  projects.* (yield, unallocated_kw, program) and utility_accounts.* (annual_usage_kwh) are unreadable, so increase
  sizing and the base annual right-size cannot be machine recomputed. Writes are therefore priced from biz ledger
  rows and garden/waitlist rows of the same customer.
- User-own writes (owner_ruling): (a) accepting a contract amendment / submitting a change request with its
  same-category consequence; (b) holder-completed payment. The compute is evaluated before the write, so a user
  write must price from records that exist before the call (a request already received).
- Feeder analysis: the only agent write that a user computation can read and that carries a multi-factor
  computation is the annual true-up (it writes biz_reviews). Late fees / estimates / deposit releases are thin.
  Decision: task 0 = true-up (agent prerequisite) -> decrease amendment fee (user root). Task 1 decided after task 0.
- Realism: R6 tags are recorded per factor (realism_bar.md). The base charter is thin (each base quantity has 2-3
  real levers); the drawn 5-6 factors per computation need company schedules keyed on recorded fields.

## Base automatic clauses checked
- biz_credit_posted triggers biz_charge_billed (actual) -> every seeded posting carries its charge.
- biz_trueup_completed triggers biz_billing_credited (production_guarantee) when outcome guarantee_credit /
  resize_and_credit, and biz_allocation_reduced (annual_resize) on resize outcomes.
- Estimates: an estimated charge may be billed estimate_wait_days after a statement month without a credit.
- Deposit release after deposit_refund_on_time_months without late fee (only deposit_required subscriptions).

## Trigger list (events task tools write; none lands in another category)
- biz_trueup_completed (biz_reviews) — triggers only biz events (biz_billing_credited, biz_allocation_reduced).
- biz_billing_credited (biz_billing) — triggers [].
- biz_change_fee_assessed (biz_billing) — triggers [].
- biz_requests update (intake, no event triggers).

## Task 0 — Bluffside Brewing Co. (true-up -> decrease amendment fee)
- Draw: prerequisite_problems=1, factor_counts=[6,5] -> fee 6, true-up 5.
- Tools (uuid8 generated once each): complete_guarantee_trueup_bd5f1ac2 (agent, write: biz_reviews row +
  production_guarantee biz_billing_credited when credit > 0); accept_share_decrease_75e61509 (user, write: updates
  the pending request's effective_date + biz_change_fee_assessed when fee > 0). Neither checks a prerequisite.
- Capability cards: true-up — object: one contract year of one biz subscription; effect: review row (+ credit line);
  receipt {status, biz_review_id, contract_year, guarantee_credit, billing_credit_id, review_date}. Acceptance —
  object: the subscriber's own pending decrease request; effect: effective_date set, fee line billed (none at 0.00);
  receipt {status, biz_request_id, effective_date, fee_bill_id, excess_decrease_fee}.
- Overwrites: true-up — review period (posting window), guaranteed kWh (carried from the previous true-up with the
  degradation step and period share), guarantee credit formula, and the once-per-year sentence (BLUEPRINT-KNOWN:
  the one_review_per_year evidence contract can never bind a new contract year to a pre-action system value; the
  replaced_by restates the same once-per-year rule). Fee — the allowance/fee sentence of biz_allocation_change
  (assessed on acceptance; allowance on the share on file). Each replaced_by names its scope and restates the base
  text for everything outside it.

### What each factor reads (A1)
| policy | factor | reads (own bindings) | reads (plain) |
|---|---|---|---|
| true-up | degradation_schedule | activation_date, NOW | — |
| true-up | excused_statement_months | COUNT postings/reversals (window) | — |
| true-up | surplus_carryover | latest review credited_kwh_12m | prior_guaranteed_kwh |
| true-up | banked_credit_valuation | SUM banked, applied rate | posted/reversed value, measured kWh, average_rate |
| true-up | share_size_guarantee_schedule | SUM filing lines | — |
| fee | usage_decline_allowance | MAX review usage, CFIELD garden allocation_kw | latest_usage_kwh |
| fee | usage_matched_release | latest review guaranteed_kwh | latest_usage_kwh, share_kw, P(pct) |
| fee | term_position_rate | term_end_date, NOW, plan fee/ETF params | — |
| fee | change_depth_multiplier | SUM filing lines | decrease_kw |
| fee | contract_year_timing_multiplier | request received_date, activation_date | — |
| fee | share_size_multiplier | SUM filing lines | — |
No factor reads another factor's decides binding.

### Defining-sentence table (sentence -> owner)
- true-up: scope sentence, the four "For a guarantee-schedule year" sentences, "most recent true-up", "measured kWh",
  "shortfall", "valuation rate is the average credit rate", "savings percentage", "degradation step is 0",
  "period share is 1" -> baseline; "contract year reviewed" -> degradation_schedule; "credited months ... period
  share" -> excused_statement_months; carryover sentence -> surplus_carryover; banked share/applied rate ->
  banked_credit_valuation; share-size sentence -> share_size_guarantee_schedule; "Each adjustment acts ..." ->
  assembly (generic order: degradation before period share; carryover before the zero floor).
- fee: scope, overwrite sentence, amended request, requested kW, share on file, allowance %, fee-free allowance,
  chargeable kW, per-kW rate -> baseline; prerequisite sentence -> edge; "latest true-up" -> plain selection;
  usage-decline sentence -> usage_decline_allowance; usage-matched sentence -> usage_matched_release; term-position
  -> term_position_rate; change-depth -> change_depth_multiplier; months-into-year -> timing multiplier;
  share-size -> share_size_multiplier; "Each adjustment acts ..." -> assembly (replacement before multipliers,
  release before the zero floor).

### Probe table (scratch copies; rule == compute)
| read | decoy / second / absent | rule outcome | compute |
|---|---|---|---|
| credit window | posting dated exactly 12 months before review | excluded ("after the same calendar day") | MONTHS=12 -> excluded |
| credit window | reversal in window | netted from kWh, value and months | yes |
| previous true-up | absent | out of scope (base rule) | not priced |
| decrease request | two open requests | latest received_date | LATEST |
| decrease request | withdrawn/filed request | not amended (outcome received only) | filter |
| reviews | none | plan allowance, nothing released | guards (peak 0, guaranteed 0) |
| garden | closed share / other account / two active shares | only an active share on the same account counts | CFIELD status=active, utility_account_id |
| term | plan without term (term_months 0) | plan fee | short-circuit guard |
| term | after term_end_date | rate 0.00 -> fee 0.00 -> no fee line | tool 0.00 path |

### Pairwise method tiers (B1)
- excused_statement_months: none(share 0) vs prorate(m/12) differ for m>=9; prorate vs full coincide only at m=12,
  which is outside the prorate tier; distinguishing input: credited months.
- surplus_carryover: cap vs whole excess vs none; distinguishing input: excess vs the limit.
- usage_matched_release: all vs half vs none; distinguishing input: oversized kW vs 10% of the share.

### R-kind tags (realism_bar)
true-up: degradation R5/R6, excused months R3, carryover R5/R6, banked valuation R6, share-size R1/R6.
fee: usage-decline allowance R6, usage-matched release R4-grounded/R6, term position R5, depth R6, timing R2/R6,
share size R1/R6.

### Runs
- evalc.py (gate DSL): true-up 167.93 (all-baseline 332.80); fee 301.89 (all-baseline 1800.00); fee with the
  true-up skipped 1215.00. Factor baselines: true-up {174.35, 284.08, 237.97, 174.09, 149.27}; fee {1111.89,
  405.00, 452.84, 201.26, 402.52, 335.43}. All > 1e-6 from a half cent (closest: 332.7953 -> 332.80).
- Revision log: (1) share-size/depth factors read F('allocation_kw') -> gate "tier read off a field" -> switched
  to SUM of filing lines; (2) dangling FK on '' ids -> None; (3) closure mismatch (billing, garden project,
  garden filing) -> added find_biz_billing, find_projects() and dropped the untouched garden filing row.
- Task-0 per-task gates: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK.

## Task 1 — Ironwood Machining Inc. (late-statement estimate -> increase deposit)
- Draw: prerequisite_problems=1, factor_counts=[6,6]. Headroom check before claiming: task 0 occupies the true-up and
  the decrease fee; the only agent writes left that a user computation can read are biz charges (estimate), late
  fees and deposit lines; late fees cannot be machine-priced (the overdue charge cannot be selected in the DSL),
  deposit releases are a recorded amount (X3); the estimate is computable, so task 1 = estimate -> deposit.
- Tools: bill_statement_estimate_b08e308f (agent: one estimated biz_charge_billed row); pay_increase_deposit_a318506d
  (user: one biz_deposit_held row + deposit_held_usd running sum). Receipts {status, biz_bill_id, billing_month,
  amount, bill_date, due_date} / {status, deposit_line_id, amount, deposit_held_usd, bill_date}.
- Overwrites: estimate sentence of biz_evt_subscription_charge and its one-charge-per-credit sentence (BLUEPRINT-KNOWN:
  that dedup contract cannot bind an estimate), base deposit formula of biz_evt_security_deposit (increase deposits).
- Own-category history repriced (H2): task 0's seeded 2026-08 estimate (was 775.70 under the base average) is now
  682.49 under the estimate rule as of 2026-10-16; task 0 gold unchanged (no task-0 computation reads charges).
- Cross-category consistency: both garden shares were moved to activations less than 12 months before their task's
  frozen date (task 0: 2026-01-15, task 1: 2025-11-13) so no garden true-up is owed (garden annual_review_enabled).

### What each factor reads (A1)
| policy | factor | own reads | plain reads |
|---|---|---|---|
| estimate | thin_basis_widening | COUNT/SUM actual charges (2x window), LATEST actual | window count/average |
| estimate | outstanding_estimate_level | COUNT estimated charges (window) | — |
| estimate | reversal_history_level | COUNT reversals (12 months) | — |
| estimate | history_length_level | MONTHS(activation, NOW) | — |
| estimate | share_size_estimate_level | SUM filing lines | — |
| estimate | credit_rate_step_level | LATEST posting value/kWh, SUM postings 12-15 months back | — |
| deposit | payment_record_months | COUNT own late fees, XCOUNT garden late fees | billing_type |
| deposit | returned_payment_months | COUNT returned payments | — |
| deposit | enlarged_share_band | SUM filing lines | added_kw |
| deposit | increase_depth_level | SUM filing lines | added_kw |
| deposit | remaining_term_level | MONTHS(NOW, term_end_date) | — |
| deposit | held_deposit_adjustment | SUM deposit held/released | monthly_estimate, plan months |

### Probe table
| read | decoy / second / absent | rule | compute |
|---|---|---|---|
| basis window | charge invoiced exactly 3 months before | excluded ("after the same calendar day") | MONTHS=3 excluded |
| basis | estimated charges | excluded from the estimate basis, counted for the deposit window | charge_basis filter / none |
| basis | no actual charge in 6 months | latest actual charge | LATEST |
| reversals | reversal 13 months back | not counted | window 12 |
| late fees | 2025-08-27 fee (13 months) | not counted | window 12 |
| garden | late fee on a garden share of another account | counted (customer's garden shares) | XCOUNT by customer |
| deposit | no held deposit | shortfall = whole current requirement | SUM = 0 |
| increase request | two open requests | latest received_date | LATEST |
| term | plan without term | x1 | guard 9999 |

### Pairwise method tiers
- thin_basis_widening: widened average vs latest charge vs window average; distinguishing input: actual-charge counts.
- held_deposit_adjustment: add shortfall vs deduct half the excess vs nothing; distinguishing input: held vs requirement.

### R-kind tags
estimate: widening R6, outstanding level R6, reversal level R6, history length R2/R6, share band R1, rate step R6.
deposit: payment record (base-grounded on the release test) R1/R6, returned payments R6, enlarged band R1, depth R6,
remaining term R2, held adjustment R6.

### Runs
- estimate 315.33 (all-baseline 359.33; factor baselines 276.95, 370.98, 331.93, 331.93, 320.14, 309.15); deposit
  579.75 (all-baseline 367.12; 422.81, 501.28, 608.67, 488.20, 762.86, 549.31); deposit with the estimate skipped
  670.30; seeded 2026-07 estimate 426.71. prec.py: every figure > 1e-6 from a half cent (closest 579.754954).
- Task-1 per-task gates: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK.

## Final difficulty-level gate run (no --task)
- check_extended: EXTENDED OK; check_task_tools: TASK TOOL CONTRACT OK; replay_tasks: REPLAY OK; check_solvability:
  SOLVABILITY OK; check_compute: COMPUTE OK (history_rows_max 51, branches_max 31); check_grounding: GROUNDING OK;
  check_cross_fire: SCOPE OK.
- check_traceability (pre-render): only the four unlock tool_name values lack a source (they appear once the KB is
  published); every other non-numeric argument is traced.
- Coverage: task 0 = {biz_ext_guarantee_trueup, biz_ext_decrease_amendment_fee}; task 1 =
  {biz_ext_late_statement_estimate, biz_ext_increase_deposit}; disjoint, all four policies covered.
- Known realism risks for the audit (recorded, not hidden): several factors are company schedules tagged R6 (see
  the R-kind tags per task); two blueprint dedup contracts (one_review_per_year, one_charge_per_credit) cannot bind
  the records these writes create and are routed by declared self-scoped overwrites (BLUEPRINT-KNOWN); increase
  sizing and the annual right-size stay under the base rule because project yield and utility usage are not
  readable by compute.
ROUND 1: gates 7/7 green
