# Rework round 11 — claims (audit revision_10)

- R10-1: closed — the returned-payment-fee relief's tier for an already-relieved missed payment is the keep-back figure but never more than the cap, so for every reachable fee it gives no more than the unrelieved tier, which gives no more than the whole fee; the tiers keep different shapes and task 0's edge still changes a scored value.
- R10-1 class: closed — the late-fee relief size ladder carried the same inversion and now uses the same capped keep-back tier; every other ladder in the charter was checked and is monotone in the direction its rule states.
