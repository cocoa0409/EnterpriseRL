# Render-surfaced source findings — pump (insulin_pump_program_services)

Source: `env/env_0063_diabetes_and_medical_supply_company/tasks/insulin_pump_program_services/pump.extended.yaml` (+ `task_tools.py`).
Rendered as the source stands; nothing below was rendered around.

## F1 (high) — factor tier reads other factors; points factors bear weight only on one tier of another factor
Location: `extended_policies[pump_ext_hardship_waiver_amount].factors[fx_hw_burden].ladder[1]` and `.rule`; compute `share_pct`, `result`.
- Ladder tier 2 of `fx_hw_burden`: "the waiver is the waiver base times the standard share percent plus all the points, never more than 100 percent" (rule: "where exactly one of them carries a balance above zero, the waiver is the waiver base times the standard share percent plus all the points below, never more than 100 percent, rounded half up to the cent").
- That tier reads the outputs of `fx_hw_effort`, `fx_hw_aged`, `fx_hw_history`, `fx_hw_balance`, `fx_hw_cost_share`.
- Each points ladder states its effect unconditionally ("the share rises by the full effort points", "the share rises by the full aged points", ...), but compute applies `share_pct` only when `burden_basis == 2`; on `burden_basis == 3` the result is `std_waiver` (50 percent flat) whatever points the program earns, and on `burden_basis == 1` the whole base.
- Effect: the five points documents read as always raising the share; whether they apply is decided by another factor's tier. The burden factor document has to mention "every point the program earns" to render tier 2 as it stands.

## F2 (medium) — undeclared departure: reversal treats every non-CO-151 non-covered charge as wholly unsupported
Location: `extended_policies[pump_ext_unsupported_charge_reversal].rule` / compute `x_denied`.
- Rule: "The reviewed line's denied units are, where a CO-151 denial answers the line's original claim, its units less the covered rate times its supply days divided by 30, never below zero, and none where no such denial is on file."
- The charge under review is "the program's non-covered item charge with the largest amount", of any denial code. Base `pump_liability_notice` permits a non-covered item charge for any denied item or quantity covered by a signed notice or an MA organization determination denial, and base `pump_evt_denials_and_appeals` routes PR-204 and un-appealable CO-197 lines to that rule ("PR-204 (not covered under the plan) becomes the customer's responsibility only under pump_liability_notice").
- So a base-legitimate PR-204 or CO-197 non-covered charge that happens to be the largest has a supported charge of 0.00 and is reversed in full. No `overwrite` entry retires the base permission for those lines; the only overwrite retires "charged at the Larkfield cash price of the units concerned".

## F3 (low) — rule says "a" qualifying notice; compute reads only the newest notice
Location: `pump_ext_non_covered_item_charge` (`nt_date`, `nt_units`, `liab_basis`) and `pump_ext_unsupported_charge_reversal` (`xn_date`, `xn_units`, `x_liab_basis`).
- Rule: "where the tier is any other tier and a liability notice signed against the line's grant on or before the line's ship date is on file, the liable units are the lesser of the denied units and that notice's units".
- Compute takes the latest notice against the grant (`LATEST ... date_field='notice_date'`) and tests only that notice against the ship date. If a notice dated after the ship date is newer than one dated on or before it, the rule makes units liable and the compute makes none. Rendered with the rule's wording.

## F4 (low) — past-due gate is undefined on a tier whose past-due age is 0
Location: `pump_ext_infusion_set_refill_quantity.prerequisite[0].policy_source` and `pump_ext_cartridge_refill_quantity.prerequisite[1].policy_source`.
- Sentences: "The infusion-set refill is not shipped until the program's past-due amount, after leaving out any balance an approved payment plan covers, is below the tier's past-due hold minimum." / "The cartridge refill is not shipped until the program's past-due amount the patient-balance postings show, after leaving out any balance an approved payment plan covers, is below the tier's past-due hold minimum."
- `parameter_schema.past_due_hold_days`: "0 = shipments are never held for a past-due balance on this tier" (Medicaid tier = 0). The edges' conditions count postings "more than the tier's past-due hold days before the ship date", so on Medicaid every posting older than today counts. Whether these gates apply on that tier is not stated.

## F5 (low) — household-extension tier undefined without an active CGM program
Location: `pump_ext_payment_plan_installment.factors[fx_pl_household]`; compute `cgm_balance = CFIELD('cgm', 'patient_balance_due', status='active') or 0`.
- Rule: "where the customer carries an approved payment plan on a CGM program and the active CGM program's balance is below that minimum, the extension is the short household extension months".
- An approved CGM payment plan with no CGM program in active status is not covered by any tier's wording. Compute treats the missing balance as 0, which gives the short extension.

## F6 (low) — overwrite retires a clause its replaced_by restates in full
Location: `pump_ext_cartridge_liability_notice.overwrite[0]`.
- superseded_clause: "the customer signs it personally, and no Larkfield representative can sign it for them"
- replaced_by: "... the customer signs it personally on the call, through the signing step the representative hands over to them, and no Larkfield representative can sign it for them; every other liability notice keeps the base signing rule."
- The base clause does not conflict with the replacement; the replacement only adds the hand-over channel. Rendered as retired for cartridge or reservoir notices only, as declared.

## F7 (low) — window boundaries stated only for 3/6-month dispensing windows
- The infusion-set and cartridge refill rules define "A dispensing counts as in the three or six months before the ship date when its ship date is later than the same day of the month three or six months before the ship date". They do not define the boundary for written orders "dated in the three months before the ship date": the cartridge ordered-rate tier and the dose-window tier of both refill policies.
- The cartridge-notice rule does define it for orders. The render applied the same same-day-of-month convention to those order windows, matching compute `within_months`.
- No boundary is stated for the 12-month windows (defect lookback, over-limit justification record, hardship waivers in 12 months) or for the 24-month plan-history lookback. The render states those windows without a boundary convention.

## Base text notes (carried as is)
- `pump_agg_multi_holding.rule` contains the parameter name in prose ("at most max_per_customer insulin pump program"); rendered as "at most 1".
- Base rules refer to other policies by id (e.g. "under pump_liability_notice"); rendered as business references ("under the advance-notice-of-liability rules").
