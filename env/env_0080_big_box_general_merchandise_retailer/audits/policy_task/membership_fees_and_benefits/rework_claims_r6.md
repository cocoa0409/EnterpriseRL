# Rework claims — membership_fees_and_benefits, round 6

| item | status | where changed |
| --- | --- | --- |
| PT-R18 hold-rate condition had two readings | closed | membership_ext_business_cash_earning rule: the payment-hold sentence is split into a definition ("an order is held when it was fulfilled on or after the membership's payment hold date, the billing period starting on that payment hold date carries a declined attempt, and the fee of that billing period settled after the fulfilled date or has not yet settled") and the rate sentence ("When the membership is not canceled on the fulfilled date and the order is held, …"); the compute_basis quotes of held_declines, held_period_settled and base_rate follow; factor payment_hold_rate ladder tier 1 mirrors the definition; tasks/1.json factor_sensitivity tier_taken text re-matched. Compute unchanged (it already implemented this single reading). Probes on scratch copies: unsettled held fee with fulfilment after the hold date → hold rate; unsettled held fee with fulfilment before the hold date → tier rate; fee settled on the fulfilled date → tier rate. |
| O-16 | kept as observation | unrounded cap remainder is within tolerance and the tool takes two decimals; no scored consequence |

No tool docstring or signature changed. Gold arguments and computations of both tasks unchanged; every gate re-run green.
