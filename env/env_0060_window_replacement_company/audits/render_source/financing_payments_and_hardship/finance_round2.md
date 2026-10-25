# Render-source findings — finance (financing_payments_and_hardship), round 2

Source: `finance.extended.yaml` sha256 2ae3afa9829b6127b0bf0b26a9d126fff400c8a39b5c3748fa728fd7478473c3,
`task_tools.py` sha256 e9d0c11114277c84afd3ed7b513dfa807060ca7c2c19f8fe7105214723126fc9 (unchanged).
Upstream gate: policy_task revision_4 verdicts — task 0 PASS, task 1 PASS.

Re-checked mechanically on the new source: every `compute_basis` quote, `replaced_by`, `superseded_clause`,
`baseline.rule` and prerequisite `policy_source` is verbatim in its rule / base rule; compute_basis keys equal the
compute bindings for all six policies.

## Round-1 items F1–F5 — closure as rendered

- F1 (promotional plans vs monthly-interest entries): closed at source; the non-promotional scope ("an account whose
  plan carries no promotion (a fixed-rate or low-payment plan)") is now carried in the hub and every fragment of the
  late fee, hardship request, hardship grant, monthly interest and catch-up policies; the base late fee and hardship
  documents now mark their retired clauses as no longer in force only for such accounts, and in force for
  promotional plans, as the scoped `replaced_by` sentences say. The "paid ahead … counts as no scheduled payments
  behind" sentence is carried in the three arrears documents.
- F2 (request above the offer): closed; the hardship offer is rendered as never more than the lifetime room and
  never below zero, and the filing sentence ("The months asked on a request filed under this policy never exceed
  the hardship offer: …") is carried in the request hub. Tenure ladder re-rendered as plus 2 / less 1 (short-tenure
  cut).
- F3 (zero-or-negative record window): closed; the zero-or-less sentence is carried in the look-back document.
- F4 (360-day day count): closed; the 360-day branch now carries the funded-date fallback.
- F5 (coverage sentence): closed; the computation document carries the new coverage sentence.

## New source note

### N1 — promotional-plan catch-up routed to base rules that state no catch-up figure (low; = audit observation R4-O1)

- `finance_ext_catch_up_payment.rule`: "This policy figures the catch-up payment on an account whose plan carries no
  promotion (a fixed-rate or low-payment plan); an account on a promotional plan is brought current under the base
  payment rules."
- Base `finance_payments.rule` states allocation, posting, channel fees, prepayment and payoff only; no base policy
  states a catch-up figure (base `finance_delinquency_and_closure` says only that an account "returns to active once
  every past-due payment is brought current"). For a promotional-plan account asking for a catch-up payment the
  amount is undefined. Rendered verbatim in the catch-up hub; not rendered around.
