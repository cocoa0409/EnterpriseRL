# plan: recovery_repossession_and_reinstatement (env_0072), M=2

## Draws (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=2, factor_counts=[4,4,5]
- task 1: prerequisite_problems=1, factor_counts=[4,4]

## Constraint analysis (why this shape)
- Writable trigger-free events in my claim: recovery_notice_sent, recovery_expense_posted, recovery_expense_waived,
  recovery_expense_settled, recovery_reinstatement_quoted, recovery_property_released. recovery_recalled has no number.
- FORBIDDEN (unconditional cross-category triggers): recovery_reinstated (-> contract:contract_reinstated),
  recovery_redeemed (-> contract:contract_paid_off), recovery_vehicle_recovered, recovery_vehicle_sold. Never written.
- The only borrower-own write with a number: recovery_expense_settled settlement_method paid_by_borrower (base rules:
  "the expense portion settles the case's expenses" in recovery_reinstatement and recovery_redemption). Base gate
  recovery_disposition.settlement_case_status ("settled only when the case is reinstated, redeemed or sold") is
  retired for these two borrower payments by self-naming scoped overwrites (sibling tails name each other).
- The variable part of a borrower expense payment is storage accrued and not yet posted (recovery_msr_expenses_outstanding),
  so both user policies carry the storage factors; no agent policy in the same tree posts storage.

## REVISED design (supersedes the tree list below where they differ)
T0 (redemption-only world; WI contract; Class 6 van recovered Sunday 2026-10-04, keyless; prior case reinstated 2025;
    first NOI stated only 8 days): recovery_ext_agency_fee (agent, 4) + recovery_ext_sale_notice_period (agent, 5)
    -> recovery_ext_redemption_expense_payment (USER, 4, ROOT). Both edges value_input, state form.
T1 (reinstatement world; GA contract; Class 2 minivan recovered Saturday 2026-10-10, keyless; valid NOI):
    recovery_ext_reinstatement_quote (agent, 4: storage factors; installments through earliest sale date)
    -> recovery_ext_reinstatement_expense_payment (USER, 4, ROOT; storage through the quote's good-through date).
Shared storage factor family (act-named in each policy): lot_day_rate (state), lot_grace_days (lot contract),
storage_clock_start (method: impound/weekend/standard), keyless_lot_handling (multi-source).
Tools: post_agency_recovery_fee_54cbecc0, mail_corrected_sale_notice_6ba1fcf2, pay_redemption_recovery_expenses_4986a691(user),
issue_reinstatement_quote_b6cf374c, pay_reinstatement_recovery_expenses_82a1a2b9(user).
DSL limits found: no date add (installments through GT not computable) -> installments counted through the latest NOI earliest sale date; no list literals (use K() lists).

## Policies (5) and trees (original draft)
T0 (reinstatement world, contract in a listed cure state, involuntary recovery):
  P_FEE  recovery_ext_recovery_fee_posting (agent, 4 factors) -> posts the agency recovery fee (recovery_expense_posted)
  P_RQ   recovery_ext_reinstatement_quote (agent, 5 factors) -> recovery_reinstatement_quoted.stated_amount_usd
         waits on P_FEE (state form: recovery fee stands posted) value_input expense component
  P_RXP  recovery_ext_reinstatement_expense_payment (USER, 4 factors, ROOT) -> recovery_expense_settled paid_by_borrower
         waits on P_RQ (state form: a reinstatement quote dated the payment date stands) value_input storage window end
T1 (redemption-only world: contract reinstated once before; first NOI stated a sale period shorter than the minimum):
  P_NOI  recovery_ext_corrected_sale_notice (agent, 4 factors) -> recovery_notice_sent NOI re-mailed, computes sale period days
  P_DXP  recovery_ext_redemption_expense_payment (USER, 4 factors, ROOT) -> recovery_expense_settled paid_by_borrower
         waits on P_NOI (state form: a notice meeting the minimum sale period stands) value_input storage cap tier

## Trigger rule (events my tools write -> base triggers)
- recovery_expense_posted -> triggers: []          (P_FEE)
- recovery_reinstatement_quoted -> triggers: []    (P_RQ)
- recovery_expense_settled -> triggers: []         (P_RXP, P_DXP)
- recovery_notice_sent -> triggers: []             (P_NOI)
None lands in another category.

## Status
- [x] extended yaml base copy  - [x] agency_fee - [x] sale_notice_period - [x] redemption_expense_payment - [x] tools T0 (contract gate OK) - [ ] task0.json - [ ] gates T0
- [ ] P_NOI - [ ] P_DXP - [ ] tools T1 - [ ] task1.json - [ ] gates T1 - [ ] final gates - [ ] worklog tail

## T1 revision (RQ dropped: DSL has no date-add, a quote's good-through window cannot be computed)
T1 (reinstatement world, voluntary surrender, GA, Class 3 SUV, surrendered Saturday 2026-10-10 at a drop-off lot, keyless):
  recovery_ext_surrender_fee (agent, 4: state ceiling, drop-off credit, prompt-surrender credit, value method)
  -> recovery_ext_reinstatement_expense_payment (USER, 4 storage factors, ROOT). Tools: post_surrender_fee_<new uuid>,
  pay_reinstatement_recovery_expenses_82a1a2b9 (b6cf374c unused).
## T0 seed (generated once by /tmp/recovery_repossession_and_reinstatement_0072/gen_t0.py -> t0_state.json; never re-run)
expected: agency fee 570.00; sale_notice_days 46 (stated 0.00); redemption expense payment 1133.00

## Rework round 2: adversarial self-probe table (charter compute evaluated with check_compute's DSL on scratch copies of each task world)
| policy | probe (decoy / absent / tie / edge) | result | rule tier that explains it |
|---|---|---|---|
| agency_fee | gold world | 604.0 |  |
| agency_fee | book None | error (unreachable) | impossible: every case points at a seeded contract (FK); the field is always present |
| agency_fee | book 1000.0 | 320.0 | low tier; agency_fee_minimum_usd floor binds (no 0.00 fee) |
| agency_fee | book 7999.99 | 550.0 | low tier |
| agency_fee | book 8000.0 | 550.0 | mid taper tier (boundary is "at least") |
| agency_fee | book 11999.99 | 670.0 | mid taper, near zero |
| agency_fee | book 12000.0 | 670.0 | no reduction (boundary "or more") |
| agency_fee | keys obtained | 509.0 | keyless fall-through |
| agency_fee | key cut posted (decoy) | 509.0 | a key_replacement_fee row ends the keyless tier |
| agency_fee | recovered 2026-10-03 | 579.0 | Saturday charge |
| agency_fee | recovered 2026-10-05 | 529.0 | weekday, no charge |
| agency_fee | state IL | 654.0 | limit_states_b |
| agency_fee | state TX | 704.0 | flat 15 |
| sale_notice_period | gold world | 45 |  |
| sale_notice_period | mailed 2026-10-17 | 43 | Saturday mailing: business-day conversion reads the weekday; lag 13 -> short late-mailing tier |
| sale_notice_period | mailed 2026-10-18 | 42 | Sunday mailing |
| sale_notice_period | mailed 2026-10-23 | 47 | Friday mailing, lag 19 |
| sale_notice_period | state MO | 50 | extended tier, count ends Sunday -> rolled to Monday |
| sale_notice_period | state TX | 44 | flat 15 |
| sale_notice_period | scra active (no ended row) | 50 | serving tier |
| sale_notice_period | no scra rows | 35 | no service days |
| sale_notice_period | no earlier notice | 38 | first notice, no reissue days |
| sale_notice_period | second short notice same day | 48 | two earlier notices -> multi reissue tier |
| sale_notice_period | certified false, returns 2026 | 43 | recent-return tier |
| sale_notice_period | certified false, no returns | 40 | no funds days |
| sale_notice_period | lag 7 | 38 | no late-mailing days (boundary "no more than") |
| sale_notice_period | lag 8 | 42 | short late-mailing tier |
| sale_notice_period | lag 14 | 42 | short tier (boundary) |
| redemption_expense_payment | gold handling world | 1897.0 | gold |
| redemption_expense_payment | no notice at all (absent) | 1897.0 | storage runs to the payment date (no stated date to cap it); the E2 wait is then unmet |
| redemption_expense_payment | same-day tie: extra short notice | 1897.0 | latest STATED date counts, so a same-day short row cannot win the tie |
| redemption_expense_payment | earlier partial settlement (decoy) | 1797.0 | settled rows are subtracted from posted open |
| redemption_expense_payment | key cut posted | 2089.0 | keyless per-day addition ends |
| redemption_expense_payment | payment on recovery day (diff 0) | 1609.0 | held 0, floored chargeable 0 |
| redemption_expense_payment | recovered Sunday day before (negative held) | 1609.0 | negative held floored at 0 |
| redemption_expense_payment | recovered 34 days ago (grace window lapsed) | 2633.0 | extended grace needs payment within 30 days -> class grace |
| redemption_expense_payment | recovered 60 days ago (45-day cap) | 3049.0 | storage_max_days_chargeable caps |
| redemption_expense_payment | impound, no impound row | 1929.0 | impound tier falls back to the day after recovery |
| redemption_expense_payment | impound, lot charges 2026-10-08 | 2011.0 | impound clock starts the day after the lot-charge posting |
| surrender_fee | gold world | 101.0 |  |
| surrender_fee | lag 3 | 86.0 | prompt tier |
| surrender_fee | lag 7 | 101.0 | no late-mailing days (boundary "no more than") |
| surrender_fee | lag 8 | 116.0 | short late-mailing tier |
| surrender_fee | lag 0 | 86.0 | prompt tier |
| surrender_fee | weekday drop (staffed) | 61.0 | staffed drop-off credit |
| surrender_fee | not a drop-off lot | 126.0 | no drop-off credit |
| surrender_fee | book 3000, prompt (min floor) | 25.0 | surrender_fee_minimum_usd floor binds (no 0.00 fee) |
| reinstatement_expense_payment | gold handling world | 297.0 | gold |
| reinstatement_expense_payment | recovered Sunday | 297.0 | Sunday shift 1 vs Saturday 2 gives same held here because end moves equally |
| reinstatement_expense_payment | fee removed (decoy) | 199.0 | a waived fee is subtracted |
| reinstatement_expense_payment | extended-grace lot within window | 157.0 | extended grace tier |

## Rework round 3: notice-sequence probes (earliest sale date = latest deadline among notices whose own deadline is >= 15 days after their own mailing; storage end = earlier of payment date and latest stated deadline; E2 = latest stated date carried by at least one compliant notice)
| read | sequence | outcome |
|---|---|---|
| redemption_expense_payment / sale-date clauses | compliant then later short re-mail: [('2026-10-06', '2026-10-22'), ('2026-10-12', '2026-10-24')] | payment 1897.0; earliest sale date 2026-10-22; E2 holds False |
| redemption_expense_payment / sale-date clauses | short then compliant: [('2026-10-06', '2026-10-14'), ('2026-10-19', '2026-12-03')] | payment 1897.0; earliest sale date 2026-12-03; E2 holds True |
| redemption_expense_payment / sale-date clauses | two same day, short and compliant (compliant later date): [('2026-10-19', '2026-10-25'), ('2026-10-19', '2026-12-03')] | payment 1897.0; earliest sale date 2026-12-03; E2 holds True |
| redemption_expense_payment / sale-date clauses | two same day stating the same date, one short: [('2026-10-06', '2026-10-21'), ('2026-10-01', '2026-10-21')] | payment 1897.0; earliest sale date 2026-10-21; E2 holds True |
| redemption_expense_payment / sale-date clauses | short only: [('2026-10-06', '2026-10-14')] | payment 1737.0; earliest sale date none running; E2 holds False |
| redemption_expense_payment / sale-date clauses | no notice: [] | payment 1897.0; earliest sale date none running; E2 holds False |
| sale-notice stated amount | task 1 seeded notice 2026-10-13, reinstatement available | 775.56 by the self-contained mailing-date formula |
| sale-notice stated amount | task 0 2025 notice 2025-07-01, reinstatement available | 1849.27 (3 installments + fees + expenses posted on or before the mailing date; storage within free days) |
| sale-notice stated amount | task 0 2026 corrected notice, reinstatement limit reached | 0.00 |

## Rework round 6 seed pass
Contract fee rows re-priced per published contract docs (late charges: 5% x installment less autopay + first-delinquency reductions; returned fees: tier + restriction + subsequent + state bank recovery - autopay offset, state cap); dependents rebuilt (payments, fee_paid, fees_due, cure and notice stated amounts).
