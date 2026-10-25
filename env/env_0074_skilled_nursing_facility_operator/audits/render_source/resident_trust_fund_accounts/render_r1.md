# Renderer scan-first findings — trust (render round 1, renderer agent aa2c31067df37608c, 2026-10-23)

Saved verbatim by the coordinator from the renderer's final report. The renderer wrote no documents.

I stopped before writing any document: the source scan found real mismatches in `trust.extended.yaml`. Nothing was written to `docs/trust/` or `.doc_render_staging/trust/`, the gate was not run, and I did not append to `RENDER.log`.

The input gate passed: the last line of `_difficulty.md` is `VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN`.

The scan otherwise came up clean. Every `compute_basis` quote is word for word in its own rule, rounding is applied once to the final result in all six policies, all four prerequisite sentences are verbatim in their blocked policy's rule, and the enums and tier names the computes test exist in the ancillary, medicaid, bedhold and medicare charters.

## Finding 1: P3 and P6 define "available balance" against an in-force base clause, with no overwrite

**What the extended policies say.** `trust_ext_patient_pay_transfer` and `trust_ext_spare_withdrawal` (both `overwrite: []`) carry this rule sentence:

> "The available balance is the account balance, which is the deposits, interest credits and returns on the account's ledger less its withdrawals, bill transfers and conveyances, less the most recent deposit (of two posted the same day, the one recorded first) while its available date is after today."

Both computes match that sentence:
- `last_dep_avail: LATEST('trust_ledger','available_date', date_field='entry_date', event_type='trust_deposit')`
- `last_dep_amt: LATEST('trust_ledger','amount', date_field='entry_date', event_type='trust_deposit') or 0`
- `available: balance_now - (last_dep_amt if (last_dep_avail and last_dep_avail > NOW) else 0)`

In P3 the result is capped by it: `result: RND(MX(0, MN(available, open_named, month_pp - credit_reaching - paid_named)) + 0.000000001, 2)`. P6 starts from it: `result: RND(MX(0, available - allowance_kept - coming_pp_kept - anc_kept - services_kept - bh_kept) + 0.000000001, 2)`.

**What the base says, still in force:**
- `trust_evt_withdrawals`, eligibility `within_balance`: "A withdrawal never exceeds the available balance; a check deposit still on hold is not available."
- `trust_evt_bill_transfers`: "A transfer pays at most the open balance of the named charge and never exceeds the available balance."
- Measure `trust_msr_available_balance`: "account balance minus trust_deposit amounts whose available_date is after the payment date". This counts every held deposit, not only the latest.

**World where they disagree.** The check hold is 5 business days. A family check is deposited and is still on hold. A pension direct deposit, available the day it posts, comes in two days later. The extended definition subtracts nothing, because only the most recent deposit is tested and it is not held. The base excludes the held check. The same split happens with two family checks both on hold: the extended rule subtracts only the later one. So the P6 spare amount, or the P3 transfer, can exceed the base available balance.

## Finding 2: P3 tests zero patient pay as "absent" in two places the rule does not

A patient pay of 0.00 can happen: the medicaid charter's patient pay rule says "never below zero".

**(a) Factor `named_month_amount`, binding `month_amount`:**
`(MN(case_pp, pp_days * ma_rate) if (pp_basis == 'partial_month' and CFIELD('medicaid','patient_pay_amount', status='eligible')) else (case_pp if (CFIELD('medicaid','patient_pay_effective_date', status='eligible') and pp_first and DAYS(pp_effective, pp_first) >= 0) else pp_amt))`

The rule says: "where the charge was billed as a partial month, the lesser of the case's patient pay and the charge's days in the center times the case's Medicaid daily rate".

Take a partial-month charge where the case's patient pay is 0.00 and its effective date falls after the first day of the named month. The rule gives 0. The compute skips the partial-month tier because 0.00 counts as false, and returns the charge as billed.

**(b) Factor `credited_reconciliation_amount`, binding `recon_credit`:**
`(tu_other if tu_other > 0 else ((elig_lag * (est_max - case_pp)) if (case_eligible and est_same and case_pp and est_max > case_pp and elig_lag > 0) else 0))`

The rule says: "where the case is eligible, no trueup decrease is posted yet and every estimate billed while the case was pending is the same amount above the case's patient pay, that difference for each month from the eligibility start date's month up to the month before the named month".

Take an eligible case with patient pay 0.00 and equal positive pending estimates. The rule gives the estimate times the number of months. The `case_pp and` guard makes the compute give 0.

## Finding 3 (only if a payee-tier account can carry this authorization): P3 ignores the personal needs allowance rule for Medicaid payee accounts

`trust_evt_bill_transfers` says: "for a Medicaid payee account the personal needs allowance stays in the account". The parameter `medicaid_pna_retained` is defined as "Whether, for a Medicaid payee account, the personal needs allowance stays in the account after patient pay is transferred". It is true for the Medicaid Representative Payee tier.

P3's rule is not scoped away from that tier, and `standing_authorization_allowed_for` includes `medicaid_patient_pay` on every tier. P3's rule and `result` keep nothing back for the allowance. On a Medicaid Representative Payee account with a standing patient-pay authorization, P3's transfer can therefore take the balance below the allowance.

## Not blocking (I can render around these)

- **P2:** `p0` and `plan_effective` are not part of any factor, but they only matter when the coinsurance share is not the whole coinsurance. The baseline rule never describes them.
- **P4:** the non-factor binding `billed_rate` reads `charge_billed`, which belongs to `hold_night_schedule`. A charge billed before 2025-07-01 is priced at its own daily rate, which can be reached only by reading that case as "no room tier can be priced".
- **P2 and P6:** when no room tier is recorded, the compute prices the nights at 0. The bedhold open event always records the room tier, so this cannot occur in practice.

Source file: `/home/ubuntu/github/enterprise_rl/env/env_0074_skilled_nursing_facility_operator/tasks/resident_trust_fund_accounts/trust.extended.yaml`
