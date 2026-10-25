# plan — project_engagements (env_0069), M=2

## Draws (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1, factor_counts=[5, 6]
- task 1: prerequisite_problems=3, factor_counts=[6, 6, 4, 5]

## Design constraints found in step 0 (DSL / schema)
- No business-day primitive; no list indexing (milestone_pcts usable only via min/max); no date-range filter
  (only within_months from NOW); cross_category may not name `project` itself -> no client-wide or
  cross-engagement reads. Late fees (per-invoice selection) and T&M monthly invoices (calendar-month window)
  are DSL-hostile and are not claimed.
- Only user-owned numeric write in this charter = a client e-signed change order carrying value_delta_usd
  (payment amounts are a ledger balance with no factor ladder). So each task's user problem is a change order
  whose value delta is priced from records: task 0 = close-out scope reduction, task 1 = restart re-pricing.

## Task 0 (root + 1) — REVISED: "deposit invoice for a T&M SOW the client has not e-signed yet"
- Root D0 = project_ext_signature_deposit (agent, 6 factors: client_standing [multi-source, managed], hardware_exposure
  [hardware], start_lead, clearpath_autopay [managed], open_balance [managed], planned_duration [method]).
- Prereq S0 = project_ext_sow_signature_rate_lock (USER: client e-signs the SOW; locks rate_discount_pct; 5 factors:
  managed_component, commitment_component, seat_scale_component, tenure_component [managed], prepaid_hours_component
  [method, timebank]). Edge D0 <- S0 value_input on est_fees (deposit on estimated fees at the locked discount), state form
  ("SOW signature before deposit" — the coordinator's own natural-order example).
- Reason for revision: the close-out de-scope / final-invoice pair had no realistic factor ladders.
- Tools: sign_statement_of_work_96bc6bf1 (user), post_deposit_invoice_06d795b1 (agent).
- World: Advanced Project T&M SOW-043715, NTE quoted 86,400.00 at list, provisional discount 7.5 at issue 2026-09-21,
  status proposed, scheduled start 2026-11-02, target 2027-03-26; frozen 2026-10-15. Client Merriwether & Pike
  Accounting, LLC (Dana Okonkwo). ClearPath Premier active 36 mo, 54 seats, go-live 2024-04-01; 1 managed late fee in
  12 m (+1 older decoy); 4 ACH payments in 6 m (+1 check decoy); Oct fee open; TimeBank grants 52 h in 12 m (+decoy
  13 m old); 1 hardware late fee in 12 m. Expected discount 12.9, deposit 14,110.20 (baseline 18,813.60).

## Task 1 (root + 3) — "restart charge after a long client pause"
- Root R1 = remobilization fee (agent, 6). R1 <- X1 = change-order administration fee on the restart
  re-pricing change order (agent, 5) [value_input: restart fee nets the CO fee]. X1 <- U1 = restart
  re-pricing change order (user, 6) [value_input: |delta| drives the fee]. U1 <- M1 = milestone invoice
  for a milestone completed before the hold and never invoiced (agent, 4) [value_input: remaining value].
- Engagement: Major Project, fixed fee, client_request hold > max_client_hold_days, PM recorded the
  resumption two days before frozen_time.

## Task 1 tools (reserved uuid8): post_milestone_invoice_79b8c922 (agent), sign_restart_change_order_602c3012 (user),
post_change_order_fee_93724a4c (agent), post_remobilization_fee_508d4151 (agent).
## Progress log
- S0, D0 policies written to project.extended.yaml.
- task 0 written and gated green
- task 1 written and gated green (M1 -> U1 [user] -> X1 -> R1); final full gate block green
