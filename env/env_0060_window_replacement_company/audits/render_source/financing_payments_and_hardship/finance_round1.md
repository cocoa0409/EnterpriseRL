# Render-source findings — finance (financing_payments_and_hardship), round 1

Source: `env/env_0060_window_replacement_company/tasks/financing_payments_and_hardship/finance.extended.yaml`
(sha256 1af42ceb…7399), `task_tools.py` (sha256 e9d0c111…6fc9).

Mechanical checks that came back clean: every `compute_basis` quote is a verbatim substring of its rule; every
`superseded_clause` is verbatim in its base rule; every `replaced_by`, `baseline.rule` and prerequisite
`policy_source` is verbatim in its extended rule; the `compute_basis` keys equal the compute bindings for all six
policies. The KB renders each item below exactly as the source states it. None of them was rendered around.

## F1 — undefined branch: the grant's monthly-interest gate on promotional plans (medium)

- `finance_ext_hardship_deferral_grant.prerequisite[1].policy_source` (also in its rule): "A deferral is not granted
  until the account carries a monthly-interest entry for every statement period whose due date has passed."
- The only writer of monthly-interest entries is `finance_ext_period_interest`, and its rule scopes it to
  no-promotion plans: "Monthly interest on an account whose plan carries no promotion is posted once for each
  statement period whose due date has passed, as a monthly-interest entry naming that period" … "every promotional
  plan account remains under the base interest rules".
- Base `finance_interest.rule`: "A zero-APR equal payment plan charges no interest unless its promotion is
  forfeited" and "A deferred-interest plan charges no monthly interest during its promotion." No sentence says
  whether a 0.00 monthly-interest entry is booked for such a period.
- Ridgeline Zero-Interest Equal Pay 24 offers deferral (`hardship_deferral_max_months: 2`,
  `hardship_lifetime_max_months: 2`). On that plan the grant gate is either never met or met by a write that no policy
  defines.
- The same definition drives "scheduled payments fallen due / behind" (one per statement period carrying a
  monthly-interest entry) in `finance_ext_late_fee_assessment` (periods_due, payments_behind),
  `finance_ext_catch_up_payment` (periods_due, payments_behind, schedule_reach) and `finance_ext_period_interest`
  (periods_posted). On a promotional-plan account with no monthly-interest entries, every such count is zero,
  however far behind the account really is.

## F2 — undefined branch: the hardship request asks for more months than the hardship offer (medium)

- `finance_ext_hardship_request_months.overwrite[0].replaced_by` retires the base caps ("the months requested may
  not exceed the plan's maximum per deferral, and the months already used … plus those requested must stay within
  the plan's lifetime maximum"). In their place, "the months the borrower may ask for are the hardship offer set
  out in this policy". It adds that "how many of those months are granted, and how a request that fails a
  condition is declined, remain with the hardship deferral rules".
- `finance_ext_hardship_deferral_grant.overwrite[0].replaced_by`: "a request that fails the seasoning, plan-offer
  or days-past-due condition is declined, and a request that meets them is granted for the months set out in this
  policy". The grant's result is `MX(0, MN(months_asked, months_asked + record_adj + returns_adj))`, with no cap
  at the hardship offer or the lifetime maximum.
- The submit tool accepts any non-negative `requested_months`. Neither policy says what happens to a submitted
  request that asks for more than the hardship offer: decline it, cap it, or grant it as asked. As written, the
  grant would allow more months than the plan's lifetime maximum.

## F3 — undefined branch: the record window can be zero or negative (low–medium)

- `finance_ext_hardship_deferral_grant.rule`: "an account granted an earlier deferral looks back the whole calendar
  months from the latest earlier deferral's grant date to the grant date less the months that deferral covered".
- compute `record_window_months: MONTHS(last_grant, NOW) - last_months if deferral_count >= 1 …` is used as
  `within_months=record_window_months`. Example: a 3-month deferral granted 2 whole months earlier gives a window of
  -1. No rule defines a window of zero or below, or what the measured record is in that case.

## F4 — the 360-day branch's day count vs the compute (low)

- `finance_ext_period_interest.rule`: "on an account funded before 1 January 2023 whose interest is posted within
  that count, it is figured day by day as the balance times the annual rate times the days since the previous
  monthly-interest entry over 360".
- compute `accrual_days: DAYS(previous_posting if previous_posting else F('funded_date'), NOW)` falls back to the
  funded date when there is no previous entry. The rule gives that fallback only for the late-posting comparison
  ("or after the funded date where there is none"), not for the 360-day figure.
- Rendered as the rule states, in the day-count factor document.

## F5 — the coverage sentence vs the adjusted months granted (low)

- `finance_ext_hardship_deferral_grant.rule` and `baseline.rule`: "A deferral covers the months asked on the
  request, starting with the first statement period whose due date has not yet passed."
- The same rule says "The months granted are the months asked, adjusted one month at a time for the account's
  record, and never more than the months asked nor below zero". The compute result can be below months_asked.
- Read literally, the coverage sentence says the deferral covers the months asked, even when fewer are granted.
  It is the policy's baseline sentence, and it is rendered verbatim only in the computation document.
