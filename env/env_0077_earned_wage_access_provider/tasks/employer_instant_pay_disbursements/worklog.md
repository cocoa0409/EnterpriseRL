# worklog — employer_instant_pay_disbursements (instantiator)

## REWORK round 2 claims
- F-1 (closing-month rule restates the ETF dependency): removed "before the employer confirms the closure" from the closing-month rule and its overwrite replaced_by; the dependency is stated only by the early-closure prerequisite sentence; task 0 action_semantics re-cited.
- F-2 (ETF wait unsatisfiable on a zero-fee tier): prerequisite sentence now opens with the record test "For a service whose tier carries a monthly platform fee"; edge condition aligned; on every fee-carrying tier the closing-month fee is always above zero, so the resolver always books an entry.
- F-3 (platform fee tier vs base "tier held on the day they are incurred"): declared scoped overwrite of that base sentence in the completed-month platform fee rule; replaced_by restates the base sentence for every other fee, the closing-month fee named.
- F-4 (rd_new_service / rd_returns gated by the minimum floor): replenishment baseline is now the alert level less the ledger balance (never below the minimum); rd_size fall-through equals it; both multipliers now move the debit on their own (T2) — recorded in task 1 rationale.
- F-5 ("whole months left" undefined): rule now defines whole months left as minimum_term_months less the whole months from enrolled_date to the closing date (matches compute).
- F-6 (window / whole-month / day-count conventions): class closed in all six policies — every whole-month count states "calendar-month difference less one when the later day-number is smaller"; every month window states "dated fewer than N whole months before today/the closing date"; every day count states which end is counted (billed part, notice, setup).
- T0-F1 (no near-miss in the ETF computation): seeded a duplicate service-closure request submitted later and withdrawn; reading it as the latest request changes the notice tier and the fee.
- T1-F1 (no multi-source factor in task 1): rd_size's two non-fall-through tiers now combine the ledger balance against half the alert with the month's payout total against a multiple of the alert (distinct aggregates).
- T1-C1 (proof asserted a debit the rule forbids): skip-election load-bearing text and tracing now state the rule's world (no debit may be pulled; deposit recomputed), naming the ungated formula value as such.
- O-T1-1: persona no longer says "before anything else". O-T1-2: deposit prerequisite sentence names the single debit due. O-7: both bundle overwrite tails repeat the half-up rounding. O-6 (realism of weakest add-ons): rationale recorded for rd_ewa, af_groups, etf_setup; task 0 agreement headcount made consistent with the Growth expectation. O-1..O-5: unchanged (observations).
- World re-scan (task 1): duplicate-credit amount re-chosen so every factor and every edge still moves its rounded result and no figure sits near a half cent; all computations, sensitivities, traces, closures and rationales re-swept for stale figures.
REWORK round 2: gates 7/7 green

## REWORK round 3 claims
- T0-F1 (residual: no discriminating near-miss in the closing-month computation): seeded a second tips payout on the activity window's excluded boundary day (exactly one whole month before the closing date); counting that day lifts the count past the light-use threshold and changes the fee, the rule excludes it; propagated to the seed-consistency entries, factor traces, tracing and rationale (balances and payout counts swept). Charter, tools and task 1 unchanged.
REWORK round 3: gates 7/7 green

## REWORK round 4 claims
- F1 (round-up moves exact multiples): both next-multiple expressions (replenishment floor, replenishment debit) rewritten as the ceiling of (amount - 1e-9) to the multiple in the renderer's suggested form; the three rule sentences now state that an amount already at a multiple is kept, so words equal compute at exact multiples; no other policy rounds to a multiple (the rest round half up to the cent and their sentences already match). Every scored, baseline and sensitivity figure of both tasks recomputed against its rounding step: none changed and all are clear of the boundary except the floor's whole baseline, the tier default itself, an exact integer that the rule keeps.
- F2 (shared record selection inside a factor): ledger_balance removed from rd_size's bindings and left as a plain binding claimed by the computation document; the platform-fee edge's gate and rd_size's multi-source ladder unchanged; task-1 rationale tables updated.
- Sweep: task-1 traces and rationale re-worded from "next multiple" to the new wording; no stale figures (all values unchanged). Task 0 unchanged apart from reassembly.
REWORK round 4: gates 7/7 green
