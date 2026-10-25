# microsoft_365_subscriptions — instantiation plan (M=2)

Draws (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=2, factor_counts=[4,6,4]
- task 1: prerequisite_problems=2, factor_counts=[4,6,5]

Task tools (uuid8 generated one per tool):
- post_reduction_credit_23f8ed2c (agent)      -> licensing_ext_reduction_credit      (task 0, 4 factors)
- assess_late_charge_e02563fc (agent)         -> licensing_ext_late_charge           (task 0, 6 factors)
- pay_arrangement_instalment_a0d5f2e9 (user)  -> licensing_ext_payment_arrangement   (task 0, 4 factors, root)
- post_admin_fee_5104ae31 (agent)             -> licensing_ext_admin_fee             (task 1, 6 factors)
- post_seat_addition_charge_bba679a2 (agent)  -> licensing_ext_seat_partial_charge   (task 1, 4 factors)
- cancel_subscription_in_window_d46a60fb (user)-> licensing_ext_window_cancellation  (task 1, 5 factors, root)

Task 0 (collections, frozen 2026-10-01): client asks to settle a past-due annual E3 invoice by a payment
arrangement and pay the first instalment by card. Tree: arrangement <- late charge <- reduction credit (chain,
both value_input). Cross-difficulty: ClearPath (managed) tier/ledger.
Task 1 (mistaken purchase, frozen 2026-10-01): client cancels an E5 P1M bought 3 days ago inside the window.
Tree: cancellation <- admin fee (value_input), cancellation <- seat-addition charge (value_input; refund cap).
Cross-difficulty: ClearPath (managed) tier + seat ledger; Sentinel (security), Continuum (backup), TimeBank.

Scratch: /tmp/microsoft_365_subscriptions_0069/ (builder scripts; removed at the end).
Progress log: worklog.md in this directory.

## Design (fixed before authoring; numbers recomputed by the builder through check_compute's engine)

### Task 0 — Fenwick Hale Wealth Partners, LLC (contact Renata Esquivel), frozen 2026-10-01 11:20:00 EDT
World: ClearPath Standard active (3rd term, balance 0, one ClearPath late fee 2026-04-01, near-miss 2025-09-01).
Sub A: Microsoft 365 E3 (no Teams) P1Y annual, renewal_count 2, term 2026-08-10..2027-08-09, renewal invoice
INV-024118 4,050.00 (10 lic), in-window reduction 2026-08-12 16:30 of 2 (no credit posted), ACH 400.00 2026-09-04.
History: 2024 purchase 12 lic + in-window reduction 2024-08-13 (credited, LATEST decoy), 2025 renewal 4,050.00
paid late with late charge 2025-10-01 (exactly 12 months back = near-miss for the 12-month window).
- RC licensing_ext_reduction_credit (4): early_release_anchor (method: whole cycle if renewal window and <=2 days
  after opening and no source / from source seat addition date / from reduction date), clearpath_change_fee (param,
  cross: 0 covered / 10 Monitor / 25), posting_delay_goodwill (param: >30 days 50 / 8-30 days 25 / 0),
  review_miss_goodwill (param, cross+window, multi: vCIO>=4 5% / vCIO>=1 2.5% / 0).
- LC licensing_ext_late_charge (6): courtesy_rate (param multi: no late charge 12m & renewal_count>=2 1.0 / no late
  charge & <2 1.25 / 1.5), relationship_minimum (param cross: Premier/Enterprise 50 / Standard/Professional 35 / 25),
  first_period_accrual (method: annual & <=30 days pro rata / monthly-billed & <=30 half month / full month),
  master_account_escalation (param cross history: 2+ ClearPath late fees 12m 1.5 / 1 1.25 / 1.0),
  good_faith_relief (param: paid >=25% 0.5 / paid >0 0.75 / 1.0), invoice_size_scale (param: >=10000 0.8 /
  >=2500 0.9 / 1.0). Prereq: RC (value_input past_due_balance).
- PY licensing_ext_payment_arrangement (4, user): instalment_count (param cross multi: ClearPath 3rd+ term & owes
  nothing 6 / other active ClearPath 4 / 3), down_payment_share (param: bal>=5000 25% / >=1000 10% / 0),
  month_late_treatment (method: month's late charge excluded when tier has a dedicated account manager / collected
  upfront otherwise / spread when none), arrangement_setup (param: late charges in prior 24 months 0 -> 0 / 1 -> 15 /
  2+ -> 25). Prereq: LC (value_input).

### Task 1 — Granger Hollis Engineering, LLC (contact Trevor Esposito), frozen 2026-10-01 10:05:00 EDT
World: ClearPath Monitor active; Sentinel MDR Advanced active (identity threat detection); Continuum Backup Standard
active protecting 22 M365 users; TimeBank 20-Hour Block active 14.5 h.
Sub M: Microsoft 365 E5 (no Teams) P1M bought 2026-09-28 14:05 (26 lic, cycle 1,708.20 INV-025611), seat addition
2026-09-30 17:40 +4 (no partial-cycle charge posted), September admin fee not posted.
- AF licensing_ext_admin_fee (6): coverage_share (param cross multi), commitment_term_adjust (param, term days),
  tenant_volume_rate (param, licence ledger), security_baseline_upkeep (param cross security),
  held_days_month_fraction (method: <30 days held days/30 / suspended half / full), backup_bundle_rate (param cross backup).
- SC licensing_ext_seat_partial_charge (4): order_window_convention (method), prepaid_hours_provisioning (param cross
  timebank), addition_volume_discount (param), onboarded_staff_discount (param cross managed seat ledger).
- CX licensing_ext_window_cancellation (5, user): prompt_cancel_anchor (method), admin_fee_return (method),
  order_reversal_fee (param), backup_deprovisioning (param cross backup), seat_change_reversals (param).
  Prereqs: AF (value_input admin_return), SC (value_input billed_cycle cap).
