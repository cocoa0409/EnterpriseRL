# Render-source findings — window (round 1)

Source: `tasks/window_contract_deposits_and_cancellations/window.extended.yaml` (sha256 c05622d9…) and `task_tools.py` (sha256 c0b715a7…). The corpus renders the rule text as it stands; nothing below was rendered around.

## F1 — window_ext_late_balance_charge: periods already charged are counted as entries, but the rule allows one entry to cover several periods (rule vs compute)

- Rule / replaced_by (overwrite[0].replaced_by and rule sentence 1): "every full period that has ended without a late balance charge is charged in one late balance charge entry dated the day it is booked"
- Rule (last sentence): "the period amount is multiplied by the number of full periods not yet charged."
- baseline.rule: "... never less than the series minimum charge, less the periods already carrying a late balance charge."
- compute: `periods_charged: "COUNT('window_transactions', event_type='window_fee_assessed', fee_kind='late_balance_charge')"`, `periods_due: "MX(0, full_periods - periods_charged)"`, and `days_since_open_period_end: "... - K('period_days') * (periods_charged + 1)"`.
- Mismatch: the compute counts late balance charge *entries*, while the rule makes a single entry carry every ended, uncharged period. Once an entry that covered two or more periods is on the ledger, the entry count is smaller than the number of periods already charged, so `periods_due` re-charges periods the rule says are already charged, and the catch-up share is read from a period end that is too early. The two coincide only while every existing entry covers exactly one period. The KB carries the rule wording ("periods already carrying a late balance charge", "full periods not yet charged").

## F2 — window_ext_late_balance_charge: account-standing share reads financing records the "never read" sentence excludes (rule vs compute, scope ambiguity)

- Rule: "Throughout these terms the contract's financing account is its Ridgeline financing account in force (approved, active, delinquent or paid off), ... ; a cancelled, charged-off, voided, expired or transferred record is never read."
- Rule: "The account-standing share comes from the household's Ridgeline financing accounts: with no late fee and no returned payment posted in the last twelve months and at least one payment posted, it is the clean-paying share; ..."
- compute: `finance_late_fees_12m`, `finance_returns_12m`, `finance_payments_posted` use `XCOUNT('finance', 'finance_transactions', ...)` with no account filter, so late fees, returned payments and payments on a cancelled or charged-off household account are counted.
- Mismatch: "Throughout these terms ... a cancelled, charged-off ... record is never read" reads as applying to every financing read of the terms; the compute reads such accounts' transactions for the account-standing share. A household whose only late fee in the last twelve months sits on a charged-off account gets share 1 in the compute but, under the "never read" sentence, the clean-paying share. The KB carries both sentences as they stand (the factor document states "the household's Ridgeline Home Improvement Financing accounts").

## F3 — window_ext_change_order_fee: returning_household_share ladder gloss narrower than rule/compute (authoring field, low)

- factors[returning_household_share].ladder[2].when: "otherwise (no door contract closed before the change order date)"
- Rule: "a household whose most recently closed door contract was closed before the change order date but fewer whole months before it takes the recent-standing share; any other household, including one with no closed door contract, takes a share of one."
- compute: `last_door_closed: XLATEST(... 'closed_date' ... status='closed')`; tier 3 whenever `last_door_closed >= last_change_date`.
- A household with one door contract closed before the change order date and a later one closed on or after it takes share 1 (rule and compute agree), although a door contract closed before the date exists, contradicting the ladder's parenthesis. The KB follows the rule ("most recently closed").

## F4 — window_ext_door_bundle_credit: credit basis with more than one completed final measure is undefined in the rule (undefined branch, low)

- Rule (credit basis): "the series base price per opening times the openings the completed final measure confirmed (the contract's openings while it is not yet measured)".
- Rule (window-project step) states the tie-break explicitly: "(the largest count should more than one completed final measure be recorded)".
- compute: `measured_openings: "MAX('window_transactions', 'openings_affected', ... visit_kind='final_measure', visit_outcome='completed')"`.
- The basis sentence gives no rule for several completed final measures; the compute takes the largest. The KB states the largest-count clause only in the window-project step document, where the source states it.
