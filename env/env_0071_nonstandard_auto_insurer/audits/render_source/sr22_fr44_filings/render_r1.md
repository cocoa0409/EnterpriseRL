# Render round 1: fr (sr22_fr44_filings): source scan STOPPED

Gate: `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN` (present).
Scope: `tasks/sr22_fr44_filings/fr.extended.yaml` and `task_tools.py`, checked against `audits/render_source/XF_recipe.md`. Enum domains come from `blueprint/db_schema.json`.
No doc was written. Nothing was staged under `.doc_render_staging/fr/`.

RENDER r1 = STOPPED (findings S1–S3 block; S4 is a second-reading edge for the reworker to settle)

---

## S1. Bindings on the wrong side of the factor line (XF 1). Applies to all 5 extended policies

In every policy, the two state-group bindings are plain (non-factor) bindings. Nothing reads them except the out-of-state factor's output. The baseline therefore defines a quantity that only a factor uses. If rendered, the computation document's `covers` has to claim these bindings, so it would carry the company's state groups even though no part of the standard method uses them. That either signals that a factor exists, or leaves a covered atom unborne. Fix in the source: move `*_filed_group` and `*_home_group` into the out-of-state factor's `bindings`.

| policy id | non-factor bindings used only by factor | consuming factor |
|---|---|---|
| fr_ext_lapse_sr26_runoff | lapse_filed_group, lapse_home_group | lapse_out_of_state_notice |
| fr_ext_refiling_fee | refile_filed_group, refile_home_group | refile_out_of_state_charge |
| fr_ext_cancellation_sr26_runoff | cancel_filed_group, cancel_home_group | cancel_out_of_state_notice |
| fr_ext_unbilled_fee | recharge_filed_group, recharge_home_group | recharge_out_of_state_charge |
| fr_ext_moved_refiling_fee | transfer_filed_group, transfer_home_group | transfer_out_of_state_charge |

Verbatim (fr_ext_refiling_fee; the other four have the same shape):
- compute_basis of `refile_filed_group` / `refile_home_group`: "The adjustments below make up Cardinal Point's own filing-fee schedule for refilings; its state groups are Florida and Virginia, Texas and Georgia, and Arizona and Ohio."
- compute `refile_filed_group`: `'a' if ((F('filing_state')) == 'FL' or (F('filing_state')) == 'VA') else ('b' if ((F('filing_state')) == 'TX' or (F('filing_state')) == 'GA') else 'c')`
- compute `refile_out` (only reader): `K('refile_out_of_region_charge') if (refile_home_state and refile_filed_group != refile_home_group) else (K('refile_in_region_charge') if (refile_home_state and F('filing_state') != refile_home_state) else 0)`
- factor `refile_out_of_state_charge` bindings: `[refile_home_state, refile_out]`. The group bindings are absent.

## S2. Assembly sentences name factor quantities (XF 2). Applies to all 5 extended policies

Each `result` sentence fixes the order by naming the method factor's output and the parameter factors' outputs. The computation document is the single home of the assembly, and it must say nothing about any factor. It cannot carry these sentences without naming the factors, and it cannot drop them without losing the order. Fix in the source: use a generic order sentence such as "the adjustments below are applied to the standard amount: replacements of the standard method first, then additions". The factor-specific names belong in the factor sentences only.

- fr_ext_lapse_sr26_runoff, rule / compute_basis.result: "They are applied in this order: first the counting of the standard lapse run-off is settled, then the lapse notice days below are added to that result; the lapse run-off is never below zero days. Each dimension enters the schedule once." Compute `result`: `int(MX(0, lapse_counted + lapse_state + lapse_out + lapse_type + lapse_form))`
- fr_ext_refiling_fee: "They are applied in this order: first the refiling fee basis replaces the standard fee of this rule, then every refiling charge below is added to that fee basis; the total is never below zero and is rounded to the cent, half up, once at the end. Each dimension enters the schedule once." Compute `result`: `RND(MX(0, refile_basis + refile_restoration + refile_state + refile_out + refile_type + refile_form), 2)`
- fr_ext_cancellation_sr26_runoff: "They are applied in this order: first the counting of the standard cancellation run-off is settled, then the cancellation notice days below are added to that result; the cancellation run-off is never below zero days. Each dimension enters the schedule once." Compute `result`: `int(MX(0, cancel_counted + cancel_state + cancel_out + cancel_type))`
- fr_ext_unbilled_fee: "They are applied in this order: first the re-charge fee basis replaces the standard fee of this rule, then every re-charge charge below is added to that fee basis; that total is never below minimum_recharge, the fee charged again is then never more than the fees reversed on the filing less any fee still standing on it, and it is rounded to the cent, half up, once at the end. Each dimension enters the schedule once." Compute `recharge_floored`: `MX(K('minimum_recharge'), recharge_basis + recharge_ending + recharge_state + recharge_out + recharge_type + recharge_form)`; `result`: `RND(MN(recharge_cap, recharge_floored), 2)`
- fr_ext_moved_refiling_fee: "They are applied in this order: first the transfer fee basis replaces the standard fee of this rule, then every transfer charge below is added to that fee basis; the total is never below zero and is rounded to the cent, half up, once at the end. Each dimension enters the schedule once." Compute `result`: `RND(MX(0, transfer_basis + transfer_ending + transfer_state + transfer_out + transfer_type + transfer_form), 2)`

## S3. Ladder gap on the real domain: moved certificate ending charge (XF 9 / XF 11)

- fr_ext_moved_refiling_fee scope: "when the term backing it (an Owner Auto Policy term, or a Named Non-Owner term) was cancelled, for any cancellation_reason, and not reinstated"
- Tier sentences: "A backing term cancelled for nonpayment adds transfer_nonpayment_charge; a backing term cancelled at the insured_request adds transfer_insured_cancel_charge; a backing term cancelled for underwriting or down_payment_dishonored adds no transfer ending charge."
- Factor `transfer_ending_charge` ladder, last tier: "otherwise (cancelled for underwriting or down_payment_dishonored)"
- Compute `transfer_ending`: `K('transfer_nonpayment_charge') if transfer_end_reason == 'nonpayment' else (K('transfer_insured_cancel_charge') if transfer_end_reason == 'insured_request' else 0)`
- Domain: the Named Non-Owner `cancellation_reason` enum also includes `converted_to_owner_policy`. The scope admits it ("for any cancellation_reason"), the compute prices it at 0, and no rule sentence states it. A renderer may not complete the counter-case, so a replaced non-owner certificate whose term ended by conversion has no stated ending charge. Fix in the source: name `converted_to_owner_policy` in the no-charge tier, or exclude it from the scope.

## S4. Second reading on a reinstated term: re-charge ending charge (XF 8 / XF 19 edge; for the reworker to settle)

- fr_ext_unbilled_fee scope: "where the filing rests on an Owner Auto Policy term, or on a Named Non-Owner term whose status is not cancelled". Any Owner Auto Policy status is in scope, reinstated terms included.
- Tier sentences: "The re-charge ending charge follows how the backing term's coverage ended, read from its cancellation_reason. A backing term cancelled for nonpayment, underwriting or down_payment_dishonored adds recharge_company_cancel_charge; a backing term cancelled at the insured_request adds recharge_insured_cancel_charge; a backing term not cancelled adds no re-charge ending charge."
- Compute `recharge_ending`: `K('recharge_company_cancel_charge') if (recharge_end_reason == 'nonpayment' or recharge_end_reason == 'underwriting' or recharge_end_reason == 'down_payment_dishonored') else (K('recharge_insured_cancel_charge') if recharge_end_reason == 'insured_request' else 0)`
- Edge: the Owner Auto Policy `cancellation_reason` stays filled on a reinstated term ("empty unless the term is or was cancelled"). For a term cancelled for nonpayment and since reinstated (now in force), the compute charges recharge_company_cancel_charge. A reader can take "a backing term not cancelled" as the term's current state and price 0. Fix in the source: say outright that a term which was cancelled and has since been reinstated takes the tier of its recorded cancellation_reason (or 0), whichever the compute is meant to do.

---

Checked and clean: compute_basis quotes are verbatim in each rule; prerequisite sentences are verbatim in the blocked rules and in the state form; every replaced_by is verbatim in its rule; sibling overwrites of the shared base clauses exclude each other by name; every declared param is read by its compute; no factor reads another factor's binding; rounding sentences match the RND / int placement; task_tools docstrings carry no example values.
