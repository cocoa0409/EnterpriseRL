# Rework round 10 — claims (audit revision_9)

- T0-R9-1: closed — the returned-payment-fee relief's size now reads whether the late fee of the same missed payment already carries a waiver entry, so its wait on the late-fee relief is a value-input edge that changes the returned-fee relief, and through it the payoff, on task 0's world; every edge of task 0's tree changes a scored value, the draw and factor floor are kept, task 1 is untouched, and the renderer D1–D6 closures stay intact.
