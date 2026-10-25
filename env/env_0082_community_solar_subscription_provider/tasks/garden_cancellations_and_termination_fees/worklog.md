# worklog — garden_cancellations_and_termination_fees (env_0082)

## Step 0 — inputs, draw, scope decisions
- Read: inst_common.md (binding), XF_recipe.md, realism_bar.md, owner_ruling.md, blueprint.yaml, products/garden.yaml,
  db_schema.json, share_tools.py (verify needs 2 credentials), skill references.
- Draw: task 0 prereq=3, factor_counts=[4,6,6,5]; task 1 prereq=3, factor_counts=[4,5,6,5].
- DECISION D1 (thin charter vs draw; recorded, pushed on): the claimed garden events carry numbers only in
  garden_billing.amount (charge, ETF) and garden_allocations.kw; every closing's removal line must equal
  allocation_kw (schema: allocation_kw = filed - reduced, 0.00 after removal), so no closing/removal write can carry
  a factor-bearing computation; the claimed owner=user events (notice, withdrawal, successor, preactivation) carry
  dates or that same forced kW only. Charges are pinned by the account-wide benefit rule (contract rate with
  escalator only) and carry at most two honest conventions. Route chosen: closings are already recorded by the
  system at the opening; each tree books the money lines a closing leaves owed and ends in the subscriber's own
  settlement payment (owner ruling (b)), using garden events no difficulty claims (garden_payment_received,
  garden_late_fee_assessed, garden_change_fee_assessed) — logged as a claim-list deviation, no other difficulty
  touches garden.
- Sibling split by plan family (business vs residential Garden plans) for every pair; task 0 = business plan
  world, task 1 = residential world. Every sibling tail names the other family.
- Tree (both tasks): root = settlement payment (owner=user) <- ETF, late fee, excess-decrease fee (value_input x3).
- Counts: task 0 payment 4, ETF 6, late fee 6, excess-decrease fee 5; task 1 payment 4, ETF 6, late fee 5,
  excess-decrease fee 5 (late-fee pair: business sibling carries one extra business-only factor).
- BLUEPRINT-THIN residue: the payment computation has no honest charter levers (a payoff is a sum of booked
  lines); its factors are R6 settlement schedules, flagged for the coordinator.

## Tool names (uuid8 generated one per tool)
- task 0: assess_closing_etf_d780691d, (late fee) _7f086ee4, (excess fee) _e48668a1, (payment, user) _c372b67a
- task 1: assess_closing_etf_e3af903e, (late fee) _3e91b283, (excess fee) _99d02cc8, (payment, user) _8237cc21

## Policy log
- garden_ext_business_etf written (6 factors: remaining_year_rule M, share_band_rate P, line_switch_credit M
  cross biz multi-source, notice_lead_rate P, market_rate_relief P, prior_decrease_addback M).

## Task 0 (business family) — closed
- Draw [4,6,6,5]: settlement 4, ETF 6, late fee 6, excess-decrease fee 5. Tree: root garden_ext_business_settlement_payment
  (owner=user) <- etf / returned_late_fee / excess_decrease_fee, three value_input state-form edges (gate lines_all).
- Policy revisions: (r1) factors without an evidence read inside their own bindings failed check_extended -> moved
  months_left into remaining_year_rule, added band reads (band_kw, band_amt, size_kw), status tier re-keyed on
  closed_date/scheduled_end_date/move_out_date with DAYS, channel ladders replaced (excess: advance_request_terms on
  the decrease request lead; settlement: agreement_form_share on signed_date vs form dates). (r2) multi-source: the
  line_switch_credit ladder rewritten as four status-specific parts, every fork an `A and B` (signed date AND plan term).
  (r3) history floor: ETF removal kW and excess-decrease kW now SUMs (removal lines; lines of the latest decrease
  request), so zeroing history moves both results. (r4) late-fee tool arg renamed garden_ref_bill_id (blueprint action
  binding of after_grace / one_fee_per_charge). (r5) seed: empty FK fields null; 7 read nodes added so the closure equals
  the seed (utility accounts, projects, garden reviews, biz allocations/credits/requests/reviews).
- Verification (scratch /tmp/garden_0082/run_t0.py, gate evaluator): ETF 4960.05 (baseline 6912.00), late fee 22.04
  (7.84), excess fee 37.40 (264.00), settlement 6139.41 (552.46); per-factor figures in tasks/0.json computations;
  edge skips: ETF 1427.36, late 6117.37, excess 6102.01. Half-cent distances all > 1e-6.
- Gates (per task): check_extended OK, check_task_tools OK, replay OK (closure 417 = seed 417), solvability OK,
  compute OK, grounding OK, cross_fire OK.

### What each factor reads (A1) — task 0
| policy | factor | reads |
|---|---|---|
| etf | remaining_year_rule | closed_date, term_end_date (MONTHS) |
| etf | share_band_rate | removal lines kW (SUM), plan etf rate |
| etf | line_switch_credit | home/biz CFIELD signed_date, contract_kw, CPARAM term_months by status; request date |
| etf | notice_lead_rate | request date, closed_date (DAYS) |
| etf | market_rate_relief | activation_date, closed_date, contract_rate, plan escalator, plan fixed_rate |
| etf | prior_decrease_addback | latest subscriber_decrease line date/kW, closed_date |
| late | lateness_accrual | re-opened charge due_date, NOW |
| late | repeat_lateness_points | count of garden late fee lines, 12 months |
| late | unpaid_band_share | re-opened charge amount (LATEST) |
| late | closing_status_load | closed_date / scheduled_end_date / move_out_date (DAYS) |
| late | returned_instrument_points | latest payment_returned payment_method |
| late | other_line_lateness_points | XCOUNT home/biz late fee lines, 12 months |
| excess | term_position_allowance | decrease effective date, term_end_date |
| excess | decrease_size_rate | kW of the latest decrease request's lines (SUM) |
| excess | advance_request_terms | decrease request received_date, effective date |
| excess | allowance_basis_rule | initial line kW, contract_kw, increase lines (SUM) |
| excess | closing_overlap_share | decrease effective date, closed_date |
| pay | closing_line_scope | line sums by bill_date/all, status |
| pay | prompt_settlement_share | closed_date, NOW |
| pay | agreement_form_share | signed_date vs form dates |
| pay | final_statement_reserve | latest posted statement_month, charges billed last 3 months |
No factor reads another factor's binding; assembly only in basis_kw / fee_raw / excess_kw / result.

### Defining-sentence table (A4)
- "Standard method: ..." (each policy) -> baseline; selection sentences ("The charge concerned is ...", "The decrease
  concerned is ...") -> plain shared bindings; each factor paragraph -> its factor only; assembly sentence -> plain.

### Probe table (C1)
- line_switch_credit: decoy closed biz Starter (status closed) -> excluded by status filter (seeded); absent home -> ''/0
  -> no deduction (seeded); second qualifying share in the same line and status -> first match only (residue: rule says
  one per line and status).
- prior_decrease_addback: absent decrease -> dec_months 9999 -> nothing; second decrease -> LATEST picks latest
  (yearly change limit 1 keeps one per contract year).
- returned late fee: absent returned payment -> policy out of scope (no re-opened charge); second returned payment ->
  the latest one's billing_month.
- excess: absent decrease request -> dec_kw 0 -> 0.00 (no line written); decoy increase lines -> tier (b).
- settlement reserve: no posted credit -> '1900-01' -> gap >= 3 -> two averages (closed only).

### Pairwise method-tier table (B1)
- remaining_year_rule: (a) months+1 over 12 (fraction) vs (b) floor years vs (c) floor+1 — (a) adds division by 12 of
  months, (b)/(c) differ by the +1 part year on m%12<6.
- line_switch_credit: full contract_kw vs half vs zero (distinct operations on a cross read).
- prior_decrease_addback: full kW vs half kW vs zero.
- lateness_accrual: pct x started 30-day periods (adds days input) vs pct x 1.5 vs pct.
- allowance_basis_rule: contract_kw vs held-before less increases vs held-before (distinct inputs).
- closing_line_scope: all lines vs lines billed by today vs lines due by today (distinct selections).
- final_statement_reserve: 2 x average vs 1 x average vs none.

### Trigger list (F4)
- garden_etf_assessed: triggers [] ; garden_late_fee_assessed: [] ; garden_change_fee_assessed: [] ;
  garden_payment_received: [] — nothing lands in another category.

### Capability contract cards
- assess_closing_etf_d780691d (agent, write): one garden_etf_assessed line (amount, bill_date=assessment_date,
  billing_month=YYYY-MM of it, due_date, dual); receipt names line id, sub, amount, month, due.
- assess_reopened_late_fee_7f086ee4 (agent, write): one garden_late_fee_assessed line referring to garden_ref_bill_id,
  billing_month of that charge.
- assess_decrease_fee_e48668a1 (agent, write): one garden_change_fee_assessed line, billing_month = filing_month of the
  decrease filing.
- pay_garden_settlement_c372b67a (user, write): one garden_payment_received line dated today, method enum.

## Task 1 (residential family) — closed
- Draw [4,5,6,5]: settlement 4, ETF 6, late fee 5, excess-decrease fee 5. Root garden_ext_residential_settlement_payment
  (owner=user) <- residential etf / returned_late_fee / excess_decrease_fee (three value_input state-form edges).
- World: Garden Fixed 10, move transfer requested 2026-04-28, no qualifying account within the 60-day window after the
  2026-06-30 move-out, move_removal effective 2026-10-01 (transfer_not_completed); returned ach payment of the 2026-07
  charge; 6.00 kW decrease effective 2026-04-01; Meadowlark Commit 5 (home, allocated) signed 2026-09-21; frozen
  2026-10-27 10:05 CDT.
- Revisions shared with task 0: sibling sentences family-tagged ("On a Garden Business plan," / "On a residential Garden
  plan,") so no sentence attaches to two policies; residential prerequisite sentences reworded (both directions);
  band_mid_usd lowered 250 -> 200 for both late-fee siblings (task 0 tier unchanged, traces updated).
- Verification (/tmp/garden_0082/run_t1.py): ETF 516.67 (baseline 600.00 capped), late fee 8.97 (3.42), excess fee
  15.78 (143.00), settlement 915.06 (764.37); edge skips 419.06 / 906.09 / 899.28; half-cent distances > 1e-6.
- Probe notes: request date falls back from notice_date to the move_transfer received_date (reading trap); Commit 5
  sits on another utility account and still counts (rule keys on status and signed date only).

## Difficulty-level closing
- Coverage: 8 extended policies, task 0 = business family 4, task 1 = residential family 4; scopes and tools disjoint.
- Trigger list: every tool writes garden_billing lines of events with triggers [] (etf, late fee, change fee, payment).
- Final gate block (no --task): check_extended OK, check_task_tools OK, replay OK, check_solvability OK,
  check_compute OK (suite branches mean 73, steps 23, history max 304, branches max 75), check_grounding OK,
  check_cross_fire OK. Traceability deferred until the KB is published.
- Open residues for the coordinator / audits (honest, not hidden):
  R-1 BLUEPRINT-THIN (D1): the claimed garden user events carry no factor-bearing number; the user write is the
      holder's portal payment and the tree uses three garden events no difficulty claims (payment, late fee,
      change fee).
  R-2 R6 load: settlement factors (line scope, prompt settlement, agreement form, final-statement reserve), ETF
      line_switch_credit / market_rate_relief / prior_decrease_addback, late-fee point schedules and band/status
      loads, excess-fee basis/overlap terms are company schedules tagged R6 in `factors[].realism`.
  R-3 Both worlds carry fee lines the system never booked (excess-decrease fee since the decrease's effective date,
      late fee since the grace end) — the opening state the trees resolve.
  R-4 CFIELD first match: a second open subscription in the same line and status would be read once (rule states one
      per line and status).
- Scratch kept outside the write domain: /tmp/garden_0082/ (builders, seeds, sims). No authoring script in the
  difficulty directory.
ROUND 1: gates 7/7 green

## REWORK round 2 (item ids and dispositions only; no scored, baseline or sensitivity figures)
- Inputs read in full: audits/policy_task/garden_cancellations_and_termination_fees/{_difficulty.md,0.md,1.md}; realism_bar.md
  incl. AMENDMENT 1; XF_recipe.md. Scratch: /tmp/garden_cancellations_and_termination_fees_0082/. Round-1 sections above are
  superseded wherever they disagree with this section.
- Changes by class (every member across both families):
  - C-SCOPE: closed by AMENDMENT 1.1 (own-category events booked by the base charter; triggers []).
  - C-APPLY: late-fee unpaid amount now defined by payment application (each payment recorded under the line it settles);
    both worlds re-seeded so the returned payment is the last payment and every later charge is inside its grace period.
  - C-ETFRED: settlement no longer deducts any part of the termination fee; prompt and agreement-form deductions removed.
  - C-RESERVE: reserve for unposted statements removed; replaced by reported_statement_prepay (a statement already posted,
    priced by the base charge rule, no estimate).
  - C-B1: line_switch_credit and prior_decrease_addback relabelled parameter; late-fee lateness_accrual redesigned (accrual
    anchor: return date vs due date, a genuine input change); settlement method = reported_statement_prepay; closing_line_scope
    relabelled parameter.
  - C-MARKET: market_rate_relief removed from both ETF policies; agreement_form_terms (R6) takes its slot.
  - C-R6COUNT: LEVER CATALOGUE below; every remaining R6 factor sits on a computation with no unused honest lever.
  - C-NONPAY: ETF counts nonpayment_removal lines, cites garden_nonpayment_removal, and has an absent-request tier.
  - C-C1: line_switch_credit and moved_share_deferral read other-line initial filings tied by the removal's filing_month
    (sum of kW, term of the latest such line, stated); reserve read removed; late-fee charge selection names the latest bill_date.
  - C-B5: late-fee rule states the zero floor and that a zero unpaid amount writes no fee; compute returns zero then.
  - C-C3: every policy states the MONTHS() convention (no last-day substitution).
  - C-G3: all eight tool bodies book nothing for a non-positive amount and say so; docstrings state it.
  - C-E4: settlement edge effects rewritten (no stale deduction names).
  - T0-4 / T1 steps: closure step numbers generated from the evaluation criteria.
  - O5: decrease request filtered to outcome completed. Seed observation (sizing cut): business world now has an equal
    initial line and contract_kw plus a subscriber increase; the allowance-basis tier taken is the increase tier.
- What each factor reads (A1): ETF remaining_year_rule (closed_date, term_end_date), share_band_rate (removal lines kW),
  line_switch_credit (other-line initial filings in the removal filing_month, their plan term), notice_lead_rate (request
  date, closed_date), agreement_form_terms (signed_date vs form dates), prior_decrease_addback (latest subscriber_decrease
  line). Late fee lateness_accrual (re-opened charge due_date, return date, NOW), repeat_lateness_points (own late fee lines,
  12 months), unpaid_band_share (re-opened charge amount), closing_status_load (closed/scheduled/move-out dates),
  returned_instrument_points (returned payment method), other_line_lateness_points (home/biz late fee lines). Excess fee
  term_position_allowance, decrease_size_rate, advance_request_terms, allowance_basis_rule, closing_overlap_share as before.
  Settlement closing_line_scope (status, line sums), reported_statement_prepay (latest posted statement, its charge count,
  contract rate, escalator, activation date, latest charge), dispute_holdback (open billing_dispute, disputed line, its late
  fees), moved_share_deferral (termination fee line and due date, other-line filings in the removal month, plan term). No
  factor reads another factor's binding.
- Defining sentences: each policy's standard method -> baseline; selection sentences (re-opened charge, decrease concerned,
  moved kW, request date, months convention) -> plain bindings; one paragraph per factor; one assembly sentence per policy.
- Probe table: moved kW — decoy closed small-business share filed in another month (excluded), absent other line (nothing),
  second filing in the same month (summed, term of the latest, stated). Re-opened charge — second actual charge of the month
  (latest bill_date, stated), absent return (out of scope). Decrease — declined later request (excluded by outcome). Prepay —
  statement already priced (nothing), absent statements (nothing). Dispute — none (nothing), overdue decision (line plus its
  late fees). Request date — nonpayment closing (none: lead tier full).
- Pairwise method-tier table: remaining_year_rule (fraction vs floor vs floor+1); lateness_accrual (periods from return vs
  periods from due date vs flat rate — distinct anchor input); allowance_basis_rule (contract_kw vs held less increases vs held);
  reported_statement_prepay (kWh x escalated contract rate vs kWh x latest charge per-kWh rate vs nothing — distinct inputs).
- Trigger list unchanged: garden_etf_assessed, garden_late_fee_assessed, garden_change_fee_assessed, garden_payment_received
  all carry triggers [].
- Open item for the coordinator: settlement factor floor (no honest R1–R5 lever for a payment amount; ruling requested).
### LEVER CATALOGUE (AMENDMENT 1.2) — garden parameter keys
- eligible_customer_types: unusable on these computations — varies by plan but enters only enrollment, sizing, true-up or filing rules no scored write here prices (sizing/yield/usage also outside the DSL, AMENDMENT 1.5)
- eligible_programs: unusable — constant across all six plans
- min_annual_usage_kwh: unusable on these computations — varies by plan but enters only enrollment, sizing, true-up or filing rules no scored write here prices (sizing/yield/usage also outside the DSL, AMENDMENT 1.5)
- min_allocation_kw: unusable on these computations — varies by plan but enters only enrollment, sizing, true-up or filing rules no scored write here prices (sizing/yield/usage also outside the DSL, AMENDMENT 1.5)
- max_allocation_kw: unusable on these computations — varies by plan but enters only enrollment, sizing, true-up or filing rules no scored write here prices (sizing/yield/usage also outside the DSL, AMENDMENT 1.5)
- allocation_increment_kw: unusable on these computations — varies by plan but enters only enrollment, sizing, true-up or filing rules no scored write here prices (sizing/yield/usage also outside the DSL, AMENDMENT 1.5)
- sizing_cap_pct: unusable on these computations — varies by plan but enters only enrollment, sizing, true-up or filing rules no scored write here prices (sizing/yield/usage also outside the DSL, AMENDMENT 1.5)
- usage_data_max_age_months: unusable — constant across all six plans
- credit_review_required: unusable — constant across all six plans
- income_verification_required: unusable — constant across all six plans
- utility_data_authorization_required: unusable — constant across all six plans
- pricing_method: unusable — constant across all six plans
- savings_rate_pct: unusable — constant across all six plans
- fixed_rate_per_kwh: used — unusable: equals contract_rate_per_kwh on every signing (C-MARKET)
- annual_escalator_pct: used — prepay pricing (reported_statement_prepay)
- charge_rounding: unusable — constant across all six plans
- invoice_issue_days_after_posting: unusable — constant across all six plans
- estimated_billing_allowed: unusable — constant across all six plans
- estimate_wait_days: unusable — constant across all six plans
- estimate_basis_months: used — unusable: estimates are off on every Garden plan
- max_consecutive_estimates: unusable — constant across all six plans
- billing_types_offered: unusable — constant across all six plans
- invoice_due_days: used — due dates (non-scored dates)
- late_fee_grace_days: used — late-fee eligibility gate only
- late_fee_pct: used — late-fee baseline; lateness_accrual
- late_fee_min_usd: used — late-fee bound (a binding bound hides the other factors)
- late_fee_max_usd: used — late-fee bound (same)
- returned_payment_fee_usd: used — seeded returned-payment fee (base trigger books it at once)
- payment_methods: unusable — constant across all six plans
- payment_application_order: unusable — constant across all six plans
- nonpayment_removal_days_past_due: unusable — constant across all six plans
- nonpayment_removal_min_balance_usd: unusable — constant across all six plans
- removal_notice_days: unusable — constant across all six plans
- security_deposit_months: unusable — constant across all six plans
- deposit_refund_on_time_months: unusable — constant across all six plans
- allocation_changes_per_contract_year: unusable — constant across all six plans
- max_decrease_pct_per_contract_year: used — excess-fee baseline; term_position_allowance
- excess_decrease_fee_per_kw_usd: used — excess-fee baseline; decrease_size_rate
- min_months_before_first_change: unusable — constant across all six plans
- increase_waitlist_when_full: unusable — constant across all six plans
- term_months: used — ETF eligibility; term_end_date drives remaining_year_rule
- post_term_renewal: unusable — constant across all six plans
- cancellation_notice_days: used — constant 90 on every Garden plan; eligibility of the closing only
- preactivation_cancel_fee_usd: unusable — constant across all six plans
- etf_per_kw_per_remaining_year_usd: used — ETF baseline rate; share_band_rate
- etf_cap_usd: used — ETF baseline cap (cannot be a factor: a binding cap hides every other ETF factor, A7)
- etf_waiver_out_of_territory_move: unusable — constant across all six plans
- etf_waiver_deceased: unusable on these computations — varies by plan but enters only enrollment, sizing, true-up or filing rules no scored write here prices (sizing/yield/usage also outside the DSL, AMENDMENT 1.5)
- etf_waiver_successor_transfer: unusable — constant across all six plans
- rescission_business_days: unusable — constant across all six plans
- transfer_window_days: unusable — constant across all six plans
- successor_transfer_allowed: unusable — constant across all six plans
- transfer_resize_to_new_usage: unusable — constant across all six plans
- production_guarantee_pct: unusable on these computations — varies by plan but enters only enrollment, sizing, true-up or filing rules no scored write here prices (sizing/yield/usage also outside the DSL, AMENDMENT 1.5)
- annual_review_enabled: unusable — constant across all six plans
- oversize_review_threshold_pct: unusable on these computations — varies by plan but enters only enrollment, sizing, true-up or filing rules no scored write here prices (sizing/yield/usage also outside the DSL, AMENDMENT 1.5)
- resize_target_pct: unusable on these computations — varies by plan but enters only enrollment, sizing, true-up or filing rules no scored write here prices (sizing/yield/usage also outside the DSL, AMENDMENT 1.5)
- recert_interval_months: unusable — constant across all six plans
- dispute_late_fee_hold: used — late-fee eligibility (no fee on a disputed line)
- dispute_resolution_days: used — dispute_holdback
### LEVER CATALOGUE — garden_subscriptions fields
- garden_sub_id: scope key
- customer_id: scope key
- variant_name: family split of the siblings
- status: closing_line_scope, reported_statement_prepay
- project_id: unusable — projects not readable (AMENDMENT 1.5)
- utility_account_id: unusable — utility_accounts not readable
- contract_kw: allowance_basis_rule (tier a)
- allocation_kw: 0.00 after every closing (schema identity); the removal lines carry the held kW
- billing_type: unusable — dual on every Garden plan
- sales_channel: unusable as a tier: the gate needs a record-derived evidence read and a channel ladder only restates a recorded label (R6 at best, not stronger than the form lever)
- signed_date: agreement_form_terms
- approved_date: unusable — no bearing on closing fees
- activation_date: prepay escalation
- term_end_date: remaining_year_rule, term_position_allowance
- notice_date: ETF request date
- scheduled_end_date: closing_status_load pending tier
- move_out_date: closing_status_load pending tier
- pending_utility_account_id: unusable — cleared at the lapse
- removal_notice_date: unusable — no nonpayment world
- closed_date: ETF, late fee, excess fee, settlement
- closure_reason: unusable on the business world (subscriber_cancellation is the base case); waivers are base rules
- contract_rate_per_kwh: prepay pricing
### LEVER CATALOGUE — garden event tables
- garden_allocations: kw, filing_month, effective_date, filing_reason, garden_request_id: used (removal kW and month, decrease, increase, add-back, moved-share tie)
- garden_credits: statement_month, credited_kwh, posted_date: used (prepay); credit_value, banked_value: unusable for charges or fees (benefit_basis: the charge ignores credit value)
- garden_billing: amount, due_date, bill_date, billing_month, payment_method, garden_ref_bill_id, event_type: used (late fee, settlement); credit_reason: no billing credit in these worlds
- garden_reviews: unusable — no scored write prices a true-up here; usage and guarantee need yield (outside the DSL)
- garden_requests: request_type, received_date, outcome, garden_disputed_bill_id: used (request date, decrease lead, dispute hold-back)
### LEVER CATALOGUE — other categories (readable through CFIELD/CPARAM/X*)
- home/biz *_allocations kw, filing_month, filing_reason, *_sub_id: used (moved-share tie; line_switch_credit, moved_share_deferral)
- home/biz plan param term_months: used (moved plan term)
- home/biz *_billing late fee lines: used (other_line_lateness_points, business family)
- home/biz savings_rate_pct, charges, credits: unusable — benefit_basis forbids another line changing a Garden price or fee by its pricing
- access: unusable — Access plans are not offered on MN_CSG, so a Garden customer's Access holding has no bearing on a Minnesota closing
- waitlist reservations/offers: unusable — no reservation rule bears on a Garden closing fee; using one would invent a mechanism
### Catalogue conclusion — computations whose drawn count exceeds the honest R1–R5 levers
- ETF: honest R1–R5 = remaining_year_rule (R3), share_band_rate (R1), notice_lead_rate (R2); the cap cannot be a factor; closure_reason bites only in lapse worlds. The rest (line_switch_credit for the cross-difficulty floor, agreement_form_terms, prior_decrease_addback) are R6 with no unused honest lever left.
- Late fee: honest = lateness_accrual (R2); bounds and grace unusable as factors; the rest R6, none of them an X kind.
- Excess-decrease fee: honest = term_position_allowance (R2), decrease_size_rate (R1), advance_request_terms (R2); allowance_basis_rule (the only method) and closing_overlap_share are R6.
- Settlement: no honest R1–R5 lever exists for a payment amount (benefit_basis, ETF tail, no-estimate plans, deposits 0); all four factors are R6; coordinator ruling requested.
REWORK round 2: gates 7/7 green
