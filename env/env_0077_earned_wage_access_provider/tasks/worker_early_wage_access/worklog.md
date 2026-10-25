# worklog — worker_early_wage_access (instantiator)

## REWORK round 2 claims
- P1 → bank fee rule now says the fee is quoted with the transfer, priced for it as confirmed, and booked only after it stands ("the figure quoted is the figure booked"); the instant-fee policy carrying the same conflict is withdrawn.
- P2 → tier review returns the plan to Starter on any write-off booked after its level_effective_date (the next review after the write-off), matching both base write-off clauses; one-review-per-payday sentence added.
- P3 → bank deduction-ceiling room now uses the period's accrued net as the base accrual rule measures it (recorded nets less corrections), a separate plain binding.
- P4 → every assembly and overwrite sentence across all five policies is generic ("any adjustment that adds / multiplies / sets / decides / measures …"); no sentence names a factor's quantity.
- F1 → the instant fee and its mislabelled surcharge method are removed with the instant-fee policy; every remaining method factor changes the formula's shape (all-pairs table in the rationales).
- F2 → the binary open-shortfall allowance is gone: the open shortfall is a plain base gate and a six-month earnings allowance (six distinct tiers) is the review's fourth factor.
- F3 → no flat fee carries stacked percentage shares: the bank fee is a flat fee set by settlement timing, a flat amount-band surcharge, the free first bank transfer of a period (withheld from heavy users) and the pay-frequency-prorated cap; the blocked-card and payday-distance tiers no longer exist; task 1 carries no fee (employer_paid).
- F5 → the weekend share is replaced by a period-advance share (amounts already advanced against the next payday as a share of accrued net).
- T1-F4 → task 1's 2026-10-16 payday reseeded from the charters: transfers booked while scheduled shifts were synced, timecard corrections for sick days, net pay fully deducted, shortfall = due less net pay, no payroll card load; card ledger chronological, never negative, card_balance equals the ledger net; no garnishment claim remains.
- Observations closed: duplicate factor id removed; overtime flag honoured by the overtime share; the instant amount now waits on the missed-recovery review (scoped prerequisite); loan read equals the base sum (at most one open loan per worker); tier review states one review per payday.
REWORK round 2: gates 7/7 green

## REWORK round 3 claims
- P2r → the return to Starter on a write-off is stated once per schedule with an explicit window (booked on or after level_effective_date and before the day the review is recorded; a same-day write-off is taken at the next review), and both computes test exactly that window.
- N1 → the missed-recovery schedule now declares its own overwrite of the base effective-date clause (verbatim superseded_clause, replaced_by = its own sentence), matching the tier review schedule: the tier applies from the day the review is recorded, which is recorded as level_effective_date. ONCE, prerequisite and gate wording read "on or after" / "no earlier than", and every seeded history review is recorded on its payday in both worlds.
- N2 → the cure ladder (card-ledger / voluntary / none) now belongs only to cure_protection, which decides its own allowance with a Starter baseline; no other factor or the assembly restates it.
- T1-F4r → task 1's card spending is realistic: merchant shares sum to the period spend, the rent purchase is a named merchant under the card's daily purchase limit, and the card ledger stays chronological and never negative.
- D1 observations → tool docstrings restate only what the bodies and rules produce: the missed-recovery enum notes that Premier Plus is never a landing, and bank delivery is the following business day, with cutoff and non-business-day roll stated as the rule states it.
- Multi-source → velocity_share decides on today's instant count AND today's instant sum (two record sources), so the multi-source requirement no longer rests on the cure factor.
- Stale proof sweep → effective-date, gate and tier-history text in both tasks' grounding, request bindings, plan checks and rationales rewritten to the recording-day rule; scored values re-derived and unchanged.
REWORK round 3: gates 7/7 green

## REWORK round 4 claims
- R3 → the frozen schema has no review row and no review event type, so the exact-value record is level_effective_date itself. Both review schedules now record it as the day after the payday the review covers, whatever day the review is recorded (each schedule declares a scoped effective-date overwrite: transfers and fees booked before the review is recorded keep their booked terms; each tail names the sibling). A payday's review is due exactly while level_effective_date is on or before that payday, so a late review, even one recorded on or after the next payday and before or after that payday's close, never makes another payday's review lapse or fall due. When a later close is booked before an earlier review is recorded, the one review of the latest closed payday covers every payday since level_effective_date, declared as an overwrite of the base cadence sentence. The schedule scopes test whether any shortfall carries a pay_date on or after level_effective_date, so an uncovered shortfall payday is never dropped; the missed-recovery cure reads that shortfall payday. Both amount prerequisite sentences and conditions now say "falls after" with the same scope qualifiers.
- R3 / P2 class (same window, whole charter) → the write-off reset reads the latest write-off booked on or after level_effective_date and on or before the payday reviewed. A write-off booked after the payday reviewed counts at the next payday's review (declared overwrite of the base write-off timing in both schedules), so every write-off is taken exactly once. Absent-record, payday-tie and None probes agree between rule and compute.
- N2r → cure_protection now tiers the cured share (collected over the shortfall payday's shortfall). Its fall-through, nothing collected, gives a cured share of zero and only Paystride Access Starter. That equals its declared baseline and the baseline.rule sentence ("the plan returns to Paystride Access Starter"). Every other factor's fall-through was rechecked against its baseline in both tasks, and all match.
- Docstrings (D1) → both review tools state that the date applies to transfers booked on or after it and that already-booked transfers keep their terms.
- Stale proof sweep → level_effective_date history (each tier applies from the day after its payday), gold review dates, prerequisite and scope quotes, the cure necessity text, and the rationales were rewritten in both tasks. Scored values were re-derived and are unchanged.
REWORK round 4: gates 7/7 green

## REWORK round 5 claims
- R4a → a record-time rule makes the payday-day tie impossible: both schedules now say a payday's review is recorded no earlier than the day after that payday, once that payday's payroll settlement and any write-off booked on it are on the plan. This is part of each schedule's own overwrite of the base cadence sentence, with sibling tails. Each review's write-off window therefore runs from the day after the previous reviewed payday through this payday, the windows tile the calendar, and every write-off is taken exactly once. The write-off timing overwrite in both schedules states that a write-off booked on a payday always stands before that payday's review.
- R4a, engaged worlds rechecked: a write-off on a payday is taken at that payday's review; one on the day after is taken at the next payday's review; a review recorded late keeps the same window; a catch-up review covers every window since level_effective_date. Each was checked as rule against compute, with the absent and None write-off probes.
- R4a, edge satisfiability → on a payday itself the review cannot yet be recorded, so both amount prerequisite sentences and conditions now apply only once the latest closed payday is before today. No edge is engaged where its resolver cannot act. Neither task world is affected (each review is recorded days after its payday).
- Stale proof sweep → the prerequisite quotes in both rationales were updated and the round-5 notes added. Scored values were re-derived and are unchanged.
REWORK round 5: gates 7/7 green

## REWORK round 6 claims
- F1 → the missed-recovery tool's new_variant_name description now says Premier Plus is never a landing because the review never lands above the tier one below the tier held, and a plan already on Starter stays on it. That is true for every current tier, including Starter. The body now refuses Premier Plus with an explicit error, as the description states.
- F2 → the bank-fee tool body now refuses, with an explicit error and nothing booked, a related transfer that is not a next-business-day transfer to a bank account. The docstring summary and the related_entry_id description state this refusal, so the fee it books is always typed next_business_day_fee on a transfer of that kind.
- Class sweep (D1, every tool) →
  - Both transfer tools now reject a non-whole or boolean daily_sequence, as "an integer of 1 or more" claims.
  - Both review tools now validate level_effective_date as a real calendar date (month lengths, leap years), as "the calendar date" claims.
  - The instant transfer no longer claims a "debit card on file" check the body never made (now "the worker's external debit card").
  - The bank transfer states ACH delivery as "for delivery", since the body books the entry undelivered.
  - Tool names and signatures are unchanged; the gold calls are unaffected and replay unchanged.
REWORK round 6: gates 7/7 green

## REWORK round 7 claims
- S1 → the tier review's assembly sentence now states once, generically, that an allowance permits only Paystride Access Starter unless one of its own tiers names a higher tier for the plan, so the next tier is never within an allowance by default. That sentence is now part of baseline.rule, so the visible fall-back keeps the current tier and is definite. Every allowance's declared baseline and fall-through is Starter.
- S1, method allowance → the recovery-count method used to fall through to "zero when any shortfall stands, else the paydays". It now has an explicit branch for no shortfall (count the paydays) and a fall-through of a zero count, Starter only. Its declared baseline is now Starter, matching baseline.rule, and rule and compute agree on every branch.
- S1 class sweep → the missed-recovery assembly states the same default for protections (only Starter unless one of the protection's own tiers names a higher tier) and joins baseline.rule; every protection's baseline and fall-through is Starter. The amount and fee policies combine multiplicative shares, whose baselines are the neutral values each fall-through gives, so there is no vacuous reading. K1 is the renderer's and is not touched here.
- Stale proof sweep → the recovery-count method description in the task 0 rationale and the round-7 notes in both rationales are updated. Scored values were re-derived and are unchanged.
REWORK round 7: gates 7/7 green

## REWORK round 8 claims
- R7a → recovery_count_method's two tiers that both counted the window's paydays are merged into one tier: no shortfall in the window, or every shortfall in it a deduction the employer did not take. The ladder now has three distinct methods: the paydays; the paydays less the carried shortfalls; and a zero count, which is the Starter fall-through equal to the baseline. The rule sentence and rv_count were rewritten to match, and rv_count is numerically identical on every input. The S1 default sentence is kept unchanged.
- R7a class re-check → the all-pairs table was re-listed for all 24 ladders, and every ladder's tier values or methods are pairwise distinct. The method ladders are recovery_count_method, estimate_method, cap_period_method, cure_protection and shortfall_method; in cure_protection the card and voluntary methods read different collected sources.
- Stale proof sweep → the task 0 necessity text and rationale now name the merged tier and the Starter baseline. Scored values and factor sensitivities are unchanged.
REWORK round 8: gates 7/7 green
