# Rework claims, round 8 (store_card_billing_and_disputes)

| item | status | location changed |
|---|---|---|
| R7-1 | closed | card_ext_catch_up_payment: rule (own referral sentence for the catch-up payment only), compute_basis referral; card_ext_line_increase: rule (own referral sentence after the waiting sentence), prerequisite[0].policy_source (waiting sentence only), prerequisite[0].condition, compute_basis; tasks/0.json design_rationale |
| O-21 | closed | card_ext_line_increase: prerequisite[0].condition (route clause removed) |

Probe table and decisions are in tasks/store_card_billing_and_disputes/worklog.md under "REWORK round 8".
