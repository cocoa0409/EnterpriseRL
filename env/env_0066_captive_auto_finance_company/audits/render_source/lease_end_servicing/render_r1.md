# Renderer findings, lease render round 1 — STOPPED before writing any doc (saved verbatim by the coordinator from the renderer's final message)

RENDER round 1: STOPPED 4 source mismatches

## Source mismatches (all in `env/env_0066_captive_auto_finance_company/tasks/lease_end_servicing/`)

**1. Undefined tie for the qualifying account number** (`lease.extended.yaml`, `lease_ext_wear_forgiveness.rule`)
- The rule says: "where an active Kestrel new-vehicle retail or balloon contract set the wear forgiveness cap, carries that contract's account_number as the qualifying account number".
- It doesn't say whose account number to carry when both an active retail contract and an active balloon contract set the cap. That happens when both are inside `loyalty_window_days` with `days_past_due` of 0, or both are inside the window at the halfway cap.
- The sentence "Wherever this rule reads a contract of another Kestrel product in a stated status, it reads the first contract in that status that the customer's records for that product list" only settles the choice within one product, not between products.
- No compute binding covers this, so the rule is the only source, and the value is a verbatim tool parameter.

**2. Rule and tool docstring disagree at the halfway cap** (`lease_ext_wear_forgiveness.rule` vs `task_tools.py`, `post_wear_forgiveness_925a15e3`, argument `qualifying_account_number`)
- The rule carries the account number of a contract that "set the wear forgiveness cap". The halfway cap is a declared ladder tier: "halfway … when no contract meets both conditions but an active Kestrel new-vehicle retail or balloon contract has its contract_date within that window".
- The docstring says: "the account number of the Kestrel contract that qualified the forgiveness … or an empty string when no contract qualified (verbatim)".
- A contract inside the window but with days past due can be read as having "set" the cap, which means passing its number. It can equally be read as not having "qualified", which means passing an empty string.

**3. A retirement removes a condition that is still in force** (`lease_ext_wear_forgiveness.overwrite[1]`, base policy `lease_end_of_term_charges`)
- The retired clause is "When the loyalty condition is met, loyalty_wear_forgiveness_cap replaces wear_forgiveness_cap".
- Its opening words are the only condition on the in-force rest of the base sentence: "…, and where loyalty_disposition_waiver is true for the tier the disposition fee is waived as loyalty_disposition_waiver; the waiver records the qualifying account number."
- The `replaced_by` keeps that waiver ("the disposition fee and its loyalty waiver remain under the base rule"). Tiers 4, 3, 2, 1 and 1+ have `loyalty_disposition_waiver: true`.
- Rendered as declared, that waiver loses its loyalty condition. Narrowing the retired clause to "loyalty_wear_forgiveness_cap replaces wear_forgiveness_cap" would fix it.

**4. Replacement texts point back to the clause they retire** (low severity: the content is restated in full each time)
- `lease_ext_charge_off_hold.overwrite[0].replaced_by` (also in its rule): "every other end-of-term balance still unpaid end_of_term_charge_off_days after turn_in_date is charged off as the base rule states." This defers to the retired clause "a balance still unpaid end_of_term_charge_off_days after turn_in_date is charged off."
- `lease_ext_end_installment_plan.overwrite[0]` and `overwrite[1].replaced_by` (also in its rule): "…and a balance still unpaid end_of_term_charge_off_days after turn_in_date is charged off, as the base rule states." The second of these retires that same clause.
- `lease_ext_excess_mileage.overwrite[3].replaced_by` (also in its rule): "every other end-of-term charge is invoiced when billed as the base rule states." This defers to the retired clause "An end-of-term invoice is mailed when charges are billed".

## Not counted as mismatches (placement only)
- **Balance bindings sit in shape factors but are defined in the standard method.** `end_balance` belongs to the factor `hold_shape` and `plan_balance` to `first_shape`, but `baseline.rule` defines both balances and the standard method uses them. The calculation documents would define the balance without covering the binding.
