# render purchase (env_0075, D=vehicle_purchase_deals) — source scan findings, STOP before any document

Gate: `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN` (passed).
Scanned all 6 extended policies of tasks/vehicle_purchase_deals/purchase.extended.yaml + task_tools.py against XF_recipe.md and the skill's two-way correspondence. No document was written.

## F1 (STOP) — purchase_ext_fleet_unit_incentive: the assembly sentence names factor quantities (XF A3)

Location: `extended_policies[purchase_ext_fleet_unit_incentive].rule`, which is also `compute_basis.summed_incentive` and part of `compute_basis.result`. `summed_incentive` and `result` are non-factor bindings, so this sentence has to be carried by the policy's computation document:

> "Every bonus and program cash amount is added to the per-unit amount first, giving the summed incentive; any adjustment to the summed incentive comes next, and rounding to the cent comes last."

- "program cash" is the quantity of exactly one declared factor, `quarterly_program` (rule: "The manufacturer's quarterly fleet program adds program cash by the calendar quarter of the unit's delivery_date ...").
- "bonus" is the quantity of the factors `order_bank_lead` ("earns an order-bank bonus") and `registered_fleet_size` ("adds a fleet-size bonus").

If the computation document carries this sentence, it announces that program cash and bonuses exist. That breaks the fall-back silence: a reader who has only the computation document gets a signal that something is missing. Paraphrasing it into generic wording would mean rendering around the source. Every other policy in this charter states its assembly generically:
- delivery fee: "Where an amount is added to the delivery mileage charge and shares apply to the fee, ..."
- late balance fee: "Any add-on to the monthly rate is added to it first; ... each share then multiplies that product in turn; ..."
- order deposit: "Every add-on to the order deposit rate is added to it first; ..."
- extension deposit: "Every add-on to the extension deposit rate is added to it first; ... each share then multiplies ..."
- hold extension days: "Every added day is added to the deal type's hold_extension_days first, ..."

Suggested fix (on the source side): restate the sentence generically and keep its order, e.g. "Every amount added to the per-unit amount is added first, giving the summed incentive; any adjustment to the summed incentive comes next, and rounding to the cent comes last." Change the rule text and `compute_basis.summed_incentive` / `compute_basis.result` together so that the quotes stay verbatim. Compute is unchanged.

## Checked clean (no action)
- Every compute_basis quote, every baseline.rule sentence and every policy_source appears verbatim in its rule (mechanical sweep). No factor id is a substring of a tool name.
- Factor independence: no factor binding reads another factor's binding, in all 6 policies.
- Rounding sentences match where RND sits: delivery fee (fee rounded, then excess); incentive (round last); late fee (round, then minimum last); order deposit (subtract held, then round); extension deposit (subtract credit, then minimum, then round).
- Every tier boundary matches compute: >, >= and <= at every edge in all ladders. Month windows match the "whole month once the same day is reached" definition used by MONTHS/within_months. Weekday indices (2000-01-03 = Monday) and the quarter index are correct.
- Overwrites (home delivery fee, fleet incentive, late balance fee, the two hold-extension clauses): each replaced_by names its own scope and restates the content still in force. The two hold-extension overwrites retire different clauses.
- The refunded-deposit decoys in the extension deposit (card deposits net of refunds) and in the extension days (collected funds net of refunds) cannot arise on a reserved deal. Base purchase_deposit_refunded happens only after a cancellation, release or unwind.
- Tool docstrings state formats only, with no example values, and every claimed effect is in the tool body.
- Low note, not a stop: in purchase_ext_fleet_order_deposit the non-factor binding `order_account` has as its compute_basis the commercial-standing ladder sentence. That binding is shared by the factors `commercial_standing_rate` and `account_exposure_base`. Its home is the computation document's covers, with no prose needed, so it does not block the render.
