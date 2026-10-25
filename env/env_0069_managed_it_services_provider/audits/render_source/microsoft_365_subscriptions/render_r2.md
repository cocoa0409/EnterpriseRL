# Renderer scan-first STOP — product licensing, render round 2 (agent afd16e23584b14c84)

Saved verbatim by the coordinator from the renderer's report (2026-10-18). Gate line read: `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN`. No documents written. All four round-1 findings (F1–F4) were confirmed fixed.

Clean: every `compute_basis` quote, `baseline.rule` sentence, `replaced_by` and prerequisite sentence verbatim in its own rule; every `superseded_clause` verbatim in its base rule; no factor reads another factor's binding, no plain binding reads a factor binding, no factor id is a substring of a tool name; docstrings have no example values.

**Findings** (all in `tasks/microsoft_365_subscriptions/licensing.extended.yaml`):

**R2-1: the cancellation refund's standard-method paragraph names two factors (XF A.3 / A.5)**
- Policy `licensing_ext_window_cancellation`, `baseline.rule`, last sentence: "The order reversal fee and the seat change charges are Stratton Bay's charges for license work outside a ClearPath agreement, so a client holding a ClearPath agreement whose status is active or notice_given and whose tier has m365_administration_included true pays neither, that work being covered."
- Compute: `result: RND(MN(refund_base, billed_cycle) + admin_return - (0 if covered_work else reversal_fee + change_rate * seat_changes) - deprov_rate * lic_held, 2)`. `covered_work` affects only the two factor quantities (factor `order_reversal_fee`, baseline `'0'`; factor `seat_change_reversals`, baseline `'0'`).
- Under the standard method neither charge exists. Rendering this sentence in the computation document would name both factors there. Leaving it out would drop the `covered_work` binding that document must cover. Moving it into the factor documents would be rendering around the defect.
- Compare `licensing_ext_seat_partial_charge`: its provisioning fee is a standard-method amount (6.00 USD), so its coverage sentence is fine.

**R2-2: "the past month" has no defined window in the front-loading sentence (XF B.12 / A.5)**
- Policy `licensing_ext_payment_arrangement`, factor `front_loading`. Rule: "when two or more late charges were posted on the subscription less than twenty-four whole months before the arrangement, not counting those of the past month, the first instalment carries one and a half of the equal shares; when exactly one was, one and a quarter shares; otherwise one share."
- Compute: `late_24m: COUNT('licensing_billing', within_months=24, date_field='posted_date', event_type='licensing_late_fee') - COUNT('licensing_billing', within_months=1, date_field='posted_date', event_type='licensing_late_fee')`
- Compute leaves out charges posted less than one whole month before the arrangement. The factor's own sentence never says that; that window is only defined in another factor's sentence (`month_late_treatment`). Read as the previous calendar month, it gives a different count.
- Example: late charges post on the 1st, and the arrangement is made mid-month. If the only late charge was posted on the 1st of the current month, compute counts 0 (one share). The calendar reading counts it as 1 (one and a quarter shares).
- Fix: "not counting those posted less than one whole month before the arrangement".

**R2-3: the deprovisioning charge assumes users are on Continuum backup, but compute never checks (XF B.8 / D.26)**
- Policy `licensing_ext_window_cancellation`, factor `backup_deprovisioning`. Rule: "Removing the cancelled users from Continuum Microsoft 365 backup deducts a deprovisioning charge per license cancelled from the cancellation refund: 0.50 USD under an active Continuum Backup Plus, Continuum BDR, Continuum DRaaS or Continuum DRaaS Premier plan, 1.00 USD under an active Continuum Backup Basic or Continuum Backup Standard plan, and nothing without an active Continuum plan."
- Compute: `cont_tier: CFIELD('backup', 'variant_name', status='active')` and `deprov_rate: K('deprov_low') if (cont_tier == 'Continuum Backup Plus' or ...) else (K('deprov_high') if (...) else 0)`, charged as `deprov_rate * lic_held`.
- The records do show which Microsoft 365 users each plan protects (`backup_device_changes`, `device_class='m365_user'`, which `licensing_ext_admin_fee` reads), but this charge never checks them.
- Example: an active Continuum BDR plan protecting only servers. Compute deducts 0.50 USD per license, while the rule's "removing the cancelled users from Continuum Microsoft 365 backup" suggests there is nothing to remove.
- Fix: either drop the framing clause or add the protection test to compute.

**Not a defect, for the next render:** in `licensing_ext_reduction_credit`, the plain binding `in_renewal_window` ("A reduction counts as made in a renewal window when …") is not in `baseline.rule`. Only factors `early_release_anchor` and `review_miss_goodwill` read it, which XF A.2 allows. The computation document would cover it in meta only, and the definition would be restated in both factor documents.
