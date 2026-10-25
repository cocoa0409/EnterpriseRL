# Render-surfaced source findings: continence (continence_supply_program_services)

Source: tasks/continence_supply_program_services/continence.extended.yaml (sha256 36723c68...) and task_tools.py (sha256 8cf6605b...).
In every case below the KB renders the source as it stands, in the rule's own wording. Nothing is rendered around.

## F-1 Rule and compute disagree: the waiver-cover fall-through (continence_ext_noncovered_catheter_charge)

- Rule (extended_policies[continence_ext_noncovered_catheter_charge].rule, "Waiver cover"): "Otherwise every unit concerned is charged."
- baseline.rule: "Every unit concerned is charged."
- Compute: `waiver_cap: 0 if (...) else (notice_units_on_file if notice_units_on_file < ship_units else ship_units)` and `charged_units: MN(units_concerned, waiver_cap)`.
- Ladder text, factors[waiver_cover_rule].ladder[2]: "value: the refill's units (no cap)". factor baseline: `waiver_cap: ship_units`.
- What goes wrong: on the CO-151 route, `units_concerned = ship_units + kits_counted * ship_days / 30 - limit_units`. When the kits counted per 30 days exceed the 150-unit limit, units concerned exceed the refill's units. The compute then charges only the refill's units, while the rule charges every unit concerned. The baseline has the same gap.
- KB carries the rule's sentence.

## F-2 Rule and compute disagree: the time anchor of a withdrawn CGM plan (continence_ext_payment_plan_installment)

- Rule ("First-installment form"): "When the customer withdrew from a payment plan on their Continuous Glucose Monitoring Supply Program within the last 24 calendar months, a quarter of the covered balance ... is set as the first installment"
- Compute: `cgm_withdrawn: XCOUNT('cgm', 'cgm_requests', within_months=24, date_field='received_at', request_type='payment_plan', request_status='withdrawn')`
- What goes wrong: the window is on the plan request's received date, which is when the plan was accepted. It is not on the date of the withdrawal, and cgm_requests has no withdrawal-date field. Take a CGM plan accepted more than 24 months ago and withdrawn within the last 24 months. The rule sets a first installment; the compute does not.
- KB carries the rule's wording ("withdrew from a payment plan ... within the last 24 calendar months").

## F-3 A factor's method wording uses another factor's quantity (continence_ext_noncovered_catheter_charge, continence_ext_returned_unit_credit)

- factors[denial_route_rule].ladder[0]: "method: the units concerned are the refill's units plus the kits counted, less the plan limit for its supply days". The rule's "Denial route" says the same. "The kits counted" is the quantity that factor kit_count_rule decides.
- factors[restocking_form_rule].ladder[0..1]: "the restocking share is withheld from the whole credit" / "from one box of 30 units only". The rule adds "that is from the credited units times the price" / "that is from 30 units times the price". "The price" is the quantity that factor credit_price_rule decides.
- In the compute, these combinations live in non-factor bindings (`units_concerned`, `restock_charge`), so the compute-level independence holds. The ladder wording, though, composes with the other factor's output. As a result, the rendered denial-route document has to say "the kits counted", and the restocking-form document has to say "the price". Neither document describes the other factor's tiers.
- Low severity.

## F-4 Possible effect in a docstring that the tool body lacks (task_tools.py, ship_catheter_refill_863073b5)

- Docstring: "One call records one package leaving the warehouse today by standard ground shipping, billed to the program's payer by claim, ..."
- Body: it creates only the continence_shipments row, with billing_route="payer_claim". It creates no continence_claim_submission row; the charter's event trigger for the claim is not executed by the tool.
- Plausible, low: "billed ... by claim" may be meant as the shipment's billing route rather than as a claim the tool records.
- The KB invocation section carries the docstring's wording.

## F-5 Rule and compute disagree: summing balances across Ostomy programs (continence_ext_hardship_waiver)

- Rule ("Hardship share"): "When the customer holds an active Ostomy Supply Program that carries a balance due above zero and no such approved application, the waiver share is three quarters."
- Compute: `ostomy_balance: XSUM('ostomy', 'ostomy_programs', 'patient_balance_due', status='active')` and the branch test `ostomy_active and ostomy_balance > 0`.
- What goes wrong: the blueprint allows a customer two Ostomy programs (one per stoma). Suppose one active program carries a positive balance and another active program carries a larger credit, so the sum is at or below zero. The rule gives three quarters; the compute gives one half.
- Low severity, edge case. KB carries the rule's wording.

## Gate note (not a source mismatch)

check_docs.py treats each base policy's `params.per_tier` mapping, whose values are all `=param` references, as a required literal key `<policy>.params.per_tier`. The base policy documents list those keys in meta.carries so the gate is satisfied. They render no extra figures.
