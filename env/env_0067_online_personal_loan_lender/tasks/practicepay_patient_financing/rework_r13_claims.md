# Rework round 13 — claims (seed-only, cross-product re-judge)

- X1: closed — the FlexLine returned-payment fee rows of both tasks are priced by the published FlexLine rules, the replacement payments are sized on them, and every FlexLine interest row, balance and minimum payment is re-derived from the published interest and minimum-payment rules.
- X2: closed — the personal-loan late fee rows of both tasks carry the published first-late share, and task 0's late installment payment and fee-payment line are sized on that fee.
- X3: closed — task 1's late installment payment pays the unpaid late fee under the published allocation order with its own fee-payment line, and the courtesy waiver of a fee already paid is removed.
- X4: closed — task 1's scheduled loan payment is the published level payment rounded to the cent, and every installment's interest and principal portions and the loan's principal balance are re-derived.
- Own PracticePay rows: checked — every seeded fee reproduces under the charter on its date; the charter and task tools are byte-identical and no scored value moved.
