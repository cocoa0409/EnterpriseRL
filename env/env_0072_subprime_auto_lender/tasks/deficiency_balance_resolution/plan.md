# plan — deficiency_balance_resolution (env_0072), M=2  (revised on relaunch, round 1)

## Draw (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1 (2 problems), factor_counts [5, 6]
- task 1: prerequisite_problems=2 (3 problems), factor_counts [5, 6, 5]

## Trees
### Task 0 (plan restart after a broken plan) — Renata Szabo (TX), Band 3, contract Tier 6 Fresh Start
- R `deficiency_ext_restart_down_payment` (owner=user, 5 factors) -> `pay_restart_down_payment_04892a83` (amount_usd)
  factors: hardship_relief(P), surrender_relief(P, X recovery, multi-source), broken_run_relief(P),
  contract_history_relief(P, X contract XCOUNT), make_good_addition(M)
- P `deficiency_ext_plan_installment` (agent, ROOT, 6) -> `record_payment_plan_offer_3f4fb3a9` (installment_amount_usd)
  factors: installment_basis_method(M), rebreak_surcharge(P), returned_surcharge(P), paydown_reduction(P),
  credit_tier_surcharge(P, X contract), recent_payer_reduction(P)
- Edge P <- R value_input (pi_balance, also pi_paid_share / pi_recent_count), state form, affirmative.

### Task 1 (installment settlement) — Marcus Thornbury (OH), Band 4, contract Tier 5 Rebuild
- L `deficiency_ext_lump_sum_settlement` (agent, 6) -> `record_lump_sum_settlement_offer_7c3d7537` (offer_amount_usd)
  factors: hardship_reduction_method(M), debt_age_points(P), sale_recovery_points(P, X recovery+contract),
  paydown_points(P), recovery_route_points(P, X recovery), lapsed_offer_points(P)
- S `deficiency_ext_installment_settlement` (user, 5) -> `accept_installment_settlement_d1722676` (settlement_amount_usd)
  factors: premium_method(M), returned_points(P), idle_points(P), contract_paid_points(P, X contract), credit_tier_points(P, X contract)
- I `deficiency_ext_settlement_installment` (agent, ROOT, 5) -> `start_installment_settlement_185f50ba` (installment_amount_usd)
  factors: count_method(M), returned_cut(P), tier_history_cut(P, X contract, multi-source), paydown_extension(P), recent_extension(P)
- Edges: S <- L value_input (lump-sum offer dated today; negated "not worked out until"); I <- S value_input (accepted
  installment settlement offer amount; affirmative "only after").

## Design rules adopted (XF recipe)
- Factor bindings never read another factor's binding; shared selections (balance, latest broken date, accepted amount)
  are plain bindings; assembly sentence fixes order (points summed -> applied once -> rounded -> amounts added -> floor/cap).
- No settlement figure below the base band minimum in any tier (only surcharges + base-sanctioned hardship), so L/S/I
  carry overwrite []; R and P declare scoped overwrites of the deficiency_payment_plan clauses they replace.
- No tier selects a rounding mode or the base a rate acts on; method tiers change formula shape (all-pairs tables in worklog).
- Factor ids avoid every tool-name substring (no 'plan', 'pay', 'start', 'settle', 'offer', 'sum', 'down', 'rest').
- Absent-record edges: no accepted installment settlement -> amount = whole balance (no 0.00 root); no lump offer today -> lump figure 0.

## Trigger rule (events my tools write, with base `triggers`)
- deficiency_payment_posted -> [deficiency:deficiency_account_update] (in category) — task 0 user tool
- deficiency_account_update -> [] — task 0 user tool (balance / last_payment_date refresh)
- deficiency_settlement_started -> [] — task 1 start tool
- deficiency_arrangement_offers rows: intake table, no event, no trigger — plan offer, lump-sum offer, acceptance tools
- NOT written: deficiency_opened (-> contract:contract_balance_transferred), credits, settled/waiver, any recovery/contract/dealer event.

## Seeds
- Contract seeded from origination: installment payments (simple interest actual/365, interest first), late charges on the
  missed installments (Tier late-charge rule), sale-proceeds payment by waterfall, balance transfer to the deficiency account.
- Recovery case: opened, assigned, recovered, expenses from the class schedule, NOI, sale, expenses settled from proceeds,
  post-sale explanation (UCC 9-616) before any offer. Dealer agreement + dealer profile for the FK only.
- Historical deficiency offers priced by this charter's own policies on snapshot worlds (plan installment by P, hardship
  lump-sum by L) — no historical row teaches a contrary algorithm.

## Files
- deficiency.extended.yaml, task_tools.py, tasks/0.json, tasks/1.json, worklog.md; scratch /tmp/deficiency_balance_resolution_0072/

## Round 2 (policy audit revision_1) — changes and adversarial probe table
- Whole-month convention stated inline in every whole-month sentence of R, P, L, S, I: "whole months counted as the difference in calendar months, less one when the later date's day of the month is below the earlier date's" (= MONTHS()).
- Tie-free reads: S lump-sum figure = MAX over lump_sum_settlement offers dated today (largest where several); I settlement amount = MAX over accepted installment_settlement offers. No LATEST over created_at remains. P, S, I state "No two arrangements of an account break on the same day ..." (R already did).
- Absent prerequisite records: S with no lump-sum offer dated today -> [round 3] no installment settlement is offered, amount nil; I with no accepted installment settlement -> nil, the base starts no settlement; edge I <- S re-declared state_gate (deficiency_settlement.settlement_offer_accepted).
- Edge wording: P and I recent-payment tiers cover any smaller (incl. negative) net count; L sale-recovery tier covers a missing figure.
- Probe table (scratch copies of each task world at the policy's handling time; every outcome matches the rule words):

| policy | probe | outcome |
|---|---|---|
| restart_down_payment | hardship doc on a declined offer dated today (date diff 0) | dp_hardship_pts=3.0 |
| restart_down_payment | hardship offer exactly 12 whole months back | dp_hardship_pts=0 |
| restart_down_payment | month-end: hardship offer 2025-10-31, today 2026-10-30 (11 whole months) | dp_hardship_pts=3.0 |
| restart_down_payment | voluntary surrender, keys false | dp_surrender_pts=1.0 |
| restart_down_payment | absent recovery case | dp_surrender_pts=0 |
| restart_down_payment | prior broken arrangement (older) present | dp_broken_date=2026-08-12, dp_run_months=8 |
| restart_down_payment | month-end run: accepted 2026-01-31, broken 2026-04-30 | dp_run_months=2, dp_run_pts=0 |
| restart_down_payment | run of 0 months (accepted and broken in the same month) | dp_run_months=0, dp_run_pts=0 |
| restart_down_payment | returned contract installment (reversal) | dp_contract_paid=22, dp_history_pts=0.5 |
| restart_down_payment | absent contract ledger | dp_contract_paid=0, dp_history_pts=0 |
| restart_down_payment | second return dated today (diff 0) | dp_returned_total=281.92, dp_make_good=281.92 |
| restart_down_payment | no return in window, break exactly 90 days back | dp_days_since_break=90, dp_make_good=140.96 |
| restart_down_payment | no return in window, break 91 days back | dp_days_since_break=91, dp_make_good=0 |
| plan_installment | no hardship doc: carry tier (broken plan 2 months ago, ran 8) | pi_basis=140.96, result=157.88 |
| plan_installment | broken settlement (not a plan) is the latest break | pi_since_break=1, pi_plan_broken=2026-08-12, pi_basis=140.96 |
| plan_installment | recent count negative (a return in window for an older payment) | pi_recent_count=0, pi_recent_pct=0 |
| plan_installment | credit applied counts toward paydown; waiver row does not | pi_paid_down=1623.06 |
| plan_installment | absent contract | pi_tier_pct=0 |
| plan_installment | no broken arrangement in 12 months (rebreak surcharge none) | pi_adjust_pct=2.0, pi_adjusted=111.47473749999999, result=111.48 |
| lump_sum_settlement | lasting doc beside the unemployment doc | ls_hardship_cut=816.71 |
| lump_sum_settlement | jobless cap bites (balance 12,000) | ls_hardship_cut=900.0 |
| lump_sum_settlement | open lump offer (offered) is not lapsed; declined installment settlement is | ls_lapsed=2, ls_lapsed_pts=4.0 |
| lump_sum_settlement | month-end debt age: opened 2025-01-31, today 2025-10-30 | ls_debt_age=8, ls_age_pts=5.0 |
| lump_sum_settlement | missing gross proceeds | ls_sale_ratio=0.0, ls_sale_pts=0 |
| lump_sum_settlement | tiny balance: floor above balance | result=600.0 |
| installment_settlement | second lump offer today recorded at the same clock | si_lump_count=2, si_lump_read=4000.0, result=5564.24 |
| installment_settlement | no lump offer today (only yesterday's) [round 3] | si_lump_count=0, result=0 (no installment settlement offered) |
| installment_settlement | absent last_payment_date | si_idle_days=397, si_idle_pts=3.0 |
| installment_settlement | no broken arrangement, account 11 months old | si_premium=1000.0 |
| settlement_installment | second acceptance at the same clock | ss_amount=5361.92, result=1340.48 |
| settlement_installment | no accepted installment settlement (opening world) | ss_amount=0.0, result=0.0 |
| settlement_installment | count when plan ran 0 months | ss_plan_ran=0, ss_count_basis=1, ss_count=1 |
| settlement_installment | no broken plan, small amount (600.00) | ss_count_basis=4 |
| settlement_installment | Tier 4 contract with 14 payments | ss_tierhist_cut=1 |
| settlement_installment | recent count negative | ss_recent_count=-1, ss_recent_ext=0 |

## Round 3 (policy audit revision_2: R-ABSENT P4 changed form, R-BASELINE)
- S: the no-offer state has one answer — no installment settlement is offered, amount nil (0.00), matching its prerequisite sentence; si_band_min removed; effect text updated.
- Tie fact moved out of the S and I baselines into the premium method / count method sentences (the only factor sentences there reading broken arrangements); R, P, L baselines already carried only the standard method.
- Class sweep: P (plan installment) carries a prerequisite sentence and no carve-out; I already answered its absent state with nil; R and L have no prerequisite. No other member.
- Touched-read probes: | S opening world | si_lump_count=0, result=0 | S lump offer yesterday only | result=0 | S second lump offer today | MAX picks the larger | S/I broken read with an older broken plan added | latest broken date unchanged | I no acceptance | result=0 |

## Round 6 (KB audit src S2, S3, S5) — re-priced worlds and probe table
- Cross-product rows re-priced by the published docs (as of each row date): T0 voluntary surrender fee (class fee less prompt-surrender credit); T0/T1 contract late charges (autopay + first-delinquency relief, cap after reduction); T1 second late charge removed (not bookable while the oldest unpaid installment carries one). Followed: expense settlement, net proceeds, sale-proceeds waterfall, fee settlement, balance transfer, NOI stated amounts, post-sale explanations, original deficiency.
- Confirmed unchanged against the published docs: installment interest/principal splits, transport / key replacement / reconditioning / auction / storage (posted at sale, 2 free days), agency fee (OH limit not binding, book value >= 12,000, weekday, key replacement posted), NOI mailing window and 15-day sale period (no late-mailing, servicemember, funds or reissue days), proceeds order, explanation timing.
- Lump-sum rule: records the document the borrower hands in; reduction reads only offers already recorded. Historical offers re-priced in date order.

| policy | probe | outcome |
|---|---|---|
| restart_down_payment | hardship doc on a declined offer dated today | dp_hardship_pts=3.0 |
| restart_down_payment | hardship offer exactly 12 whole months back | dp_hardship_pts=0 |
| restart_down_payment | month-end: hardship offer 2025-10-31, today 2026-10-30 | dp_hardship_pts=3.0 |
| restart_down_payment | voluntary surrender, keys false | dp_surrender_pts=1.0 |
| restart_down_payment | absent recovery case | dp_surrender_pts=0 |
| restart_down_payment | older broken arrangement present | dp_broken_date=2026-08-12, dp_run_months=8 |
| restart_down_payment | month-end run: accepted 2026-01-31, broken 2026-04-30 | dp_run_months=2, dp_run_pts=0 |
| restart_down_payment | returned contract installment | dp_contract_paid=22, dp_history_pts=0.5 |
| restart_down_payment | absent contract ledger | dp_contract_paid=0, dp_history_pts=0 |
| restart_down_payment | second return dated today | dp_returned_total=279.94, dp_make_good=279.94 |
| restart_down_payment | no return in window, break exactly 90 days back | dp_days_since_break=90, dp_make_good=139.97 |
| restart_down_payment | no return in window, break 91 days back | dp_days_since_break=91, dp_make_good=0 |
| plan_installment | no hardship doc: carry tier | pi_basis=139.97, result=156.77 |
| plan_installment | broken settlement (not a plan) is the latest break | pi_since_break=1, pi_plan_broken=2026-08-12, pi_basis=139.97 |
| plan_installment | net recent count pushed to zero by returns | pi_recent_count=0, pi_recent_pct=0 |
| plan_installment | credit counts toward paydown; waiver row does not | pi_paid_down=1613.75 |
| plan_installment | absent contract | pi_tier_pct=0 |
| plan_installment | no broken arrangement in 12 months | pi_adjust_pct=2.0, result=110.69 |
| lump_sum_settlement | lasting doc beside the unemployment doc | ls_hardship_cut=812.83 |
| lump_sum_settlement | jobless cap bites (balance 12,000.00) | ls_hardship_cut=900.0 |
| lump_sum_settlement | open lump offer is not lapsed; declined installment settlement is | ls_lapsed=2, ls_lapsed_pts=4.0 |
| lump_sum_settlement | month-end debt age: opened 2025-01-31, today 2025-10-30 | ls_debt_age=8, ls_age_pts=5.0 |
| lump_sum_settlement | missing gross proceeds | ls_sale_pts=0 |
| lump_sum_settlement | floor above balance (balance 600.00) | result=600.0 |
| lump_sum_settlement | first hardship document only on the offer being made (none earlier) | ls_hardship_cut=0 |
| installment_settlement | opening world (no lump-sum offer dated today) | si_lump_count=0, result=0 |
| installment_settlement | lump-sum offer dated yesterday only | si_lump_count=0, result=0 |
| installment_settlement | second lump-sum offer today at the same clock (4,000.00) | si_lump_read=4000.0, result=5557.37 |
| installment_settlement | absent last_payment_date | si_idle_days=397, si_idle_pts=3.0 |
| installment_settlement | no broken arrangement, account 11 months old | si_premium=1000.0 |
| installment_settlement | older broken plan added | si_broken_date=2026-06-30, si_premium=988.39 |
| settlement_installment | second acceptance at the same clock (5,000.00) | ss_amount=5337.02, result=1334.26 |
| settlement_installment | no accepted installment settlement | ss_amount=0.0, result=0.0 |
| settlement_installment | plan ran 0 months | ss_count_basis=1, ss_count=1 |
| settlement_installment | no broken plan, amount 600.00 | ss_count_basis=4 |
| settlement_installment | Tier 4 contract with 14 payments | ss_tierhist_cut=1 |
| settlement_installment | net recent count negative | ss_recent_count=-1, ss_recent_ext=0 |
| settlement_installment | older broken plan added | ss_plan_broken=2026-06-30, ss_count_basis=5 |
